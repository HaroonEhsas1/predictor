#!/usr/bin/env python3
"""
PREMARKET MULTI-STOCK PREDICTION SYSTEM
Works like overnight multi_stock_predictor.py but for premarket (9:15 AM)

Auto-fetches premarket data and generates predictions for all 6 stocks:
AMD, NVDA, META, AVGO, SNOW, PLTR
"""

from free_advanced_indicators import get_free_indicators
from stock_specific_predictors import get_predictor
import sys
from pathlib import Path
from datetime import datetime
import pytz
import json
import math
import yfinance as yf
import logging
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
                    filename='premarket_predictions.log')

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))


def adjust_premarket_volume_threshold(avg_volume):
    """
    Daily average volume cannot be compared 1:1 with premarket prints.
    Scale the reference so predictors judge liquidity relative to typical
    premarket participation instead of full-session averages.
    """
    if not avg_volume or math.isnan(avg_volume):
        return 1_000_000
    # Premarket volume is typically 10-20% of the regular-session average.
    scaled = avg_volume * 0.18
    return max(500_000, scaled)


def interpret_indicator_signals(symbol, indicators):
    """
    Convert raw indicator dictionaries into normalized features consumed
    by the stock-specific predictors.
    """
    features = {
        'indicator_bias': 0.0,
        'trend_strength': 0.0,
        'sector_alignment': 0.0,
        'ma_distance': 0.0,
        'sentiment_score': 0.0,
        'trap_signals': False,
        'trap_risk_score': 0.0,
        'support_signals': [],
        'risk_signals': []
    }
    if not isinstance(indicators, dict) or not indicators:
        return features

    bias_components = []

    def coerce_bias(value):
        if isinstance(value, (int, float)) and not math.isnan(value):
            bias_components.append(value)

    negative_signals = {
        'OVERBOUGHT', 'EXTENDED_UP', 'EXTREME_GREED', 'RISK', 'CAUTION',
        'HEAVY_SELLING', 'MASSIVE_SELLING', 'WEAK_CLOUD', 'CLOUD_DOWN',
        'CLOUD_WEAK', 'TRAP', 'ALERT'
    }
    positive_signals = {
        'OVERSOLD', 'EXTENDED_DOWN', 'STRONG_OUTPERFORM', 'OUTPERFORM',
        'VERY_SAFE', 'SAFE', 'STRONG_BUYING', 'BUYING', 'TRACKING'
    }

    for name, payload in indicators.items():
        if not isinstance(payload, dict):
            continue
        coerce_bias(payload.get('bias'))
        signal = str(payload.get('signal', '')).upper()
        if signal in negative_signals:
            features['risk_signals'].append(f"{name}:{signal}")
        elif signal in positive_signals:
            features['support_signals'].append(f"{name}:{signal}")

    ma_distance = indicators.get('ma_distance', {})
    if ma_distance.get('success'):
        features['ma_distance'] = ma_distance.get('distance_pct', 0.0) / 100.0

    relative_strength = indicators.get('relative_strength', {})
    if relative_strength.get('success'):
        rel = relative_strength.get('relative_strength', 0.0)
        # Normalize to [-1, 1]
        features['trend_strength'] = max(-1.0, min(1.0, rel / 10.0))
        features['sector_alignment'] = relative_strength.get('bias', 0.0)

    # Stock-specific sentiment proxies
    sentiment_sources = [
        indicators.get('pc_extreme'),
        indicators.get('short_interest'),
        indicators.get('insider_activity'),
        indicators.get('insider_selling')
    ]
    sentiment_scores = [
        payload.get('bias', 0.0)
        for payload in sentiment_sources
        if isinstance(payload, dict) and payload.get('success')
    ]
    if sentiment_scores:
        features['sentiment_score'] = max(-0.3,
                                          min(0.3, sum(sentiment_scores)))

    total_bias = sum(bias_components)
    features['indicator_bias'] = max(-0.3, min(0.3, total_bias))

    # Calibrate trap risk instead of binary flagging everything
    risk_weight = len(features['risk_signals']) * 0.2
    support_weight = len(features['support_signals']) * 0.12
    bias_penalty = max(0.0, -features['indicator_bias'])
    trap_score = max(
        0.0,
        min(1.0, 0.15 + risk_weight + bias_penalty - support_weight)
    )
    features['trap_risk_score'] = round(trap_score, 3)
    features['trap_signals'] = trap_score >= 0.45

    return features


def check_market_hours():
    """Check if we're in premarket hours"""
    et_tz = pytz.timezone('US/Eastern')
    now_et = datetime.now(et_tz)
    current_time = now_et.time()

    premarket_start = datetime.strptime('04:00', '%H:%M').time()
    premarket_end = datetime.strptime('09:30', '%H:%M').time()
    market_close = datetime.strptime('16:00', '%H:%M').time()

    is_premarket = premarket_start <= current_time < premarket_end
    is_regular = premarket_end <= current_time < market_close

    return {
        'is_premarket': is_premarket,
        'is_regular': is_regular,
        'current_et': now_et,
        'status': 'PREMARKET' if is_premarket else ('REGULAR' if is_regular else 'CLOSED')
    }


def get_premarket_data(symbol):
    """Fetch current premarket gap and volume"""
    logging.info(f"Fetching premarket data for {symbol}")
    try:
        ticker = yf.Ticker(symbol)

        # Get historical data (last 2 days for comparison)
        hist = ticker.history(period='5d')
        logging.info(f"Historical data for {symbol}: {len(hist)} days fetched")

        if len(hist) < 2:
            logging.error(f"Insufficient historical data for {symbol}")
            return {
                'success': False,
                'symbol': symbol,
                'error': 'Insufficient historical data'
            }

        # Get previous close (last complete trading day)
        prev_close = hist['Close'].iloc[-2]  # Second to last day
        logging.info(f"Previous close for {symbol}: {prev_close}")

        # Try to get current/premarket price
        info = ticker.info
        logging.info(f"Ticker info for {symbol}: {info}")

        # Priority order for current price:
        # 1. preMarketPrice (if in premarket)
        # 2. regularMarketPrice (if market open)
        # 3. postMarketPrice (if after hours)
        # 4. currentPrice (fallback)
        # 5. Last close (if nothing else)

        market_status = check_market_hours()
        logging.info(f"Market status for {symbol}: {market_status}")

        if market_status['is_premarket']:
            current_price = info.get('preMarketPrice', info.get(
                'regularMarketPrice', info.get('currentPrice', hist['Close'].iloc[-1])))
            price_source = 'PREMARKET'
        elif market_status['is_regular']:
            current_price = info.get('regularMarketPrice', info.get(
                'currentPrice', hist['Close'].iloc[-1]))
            price_source = 'LIVE'
        else:
            # Market closed - use last available price
            current_price = info.get('postMarketPrice', info.get(
                'regularMarketPrice', hist['Close'].iloc[-1]))
            price_source = 'AFTER_HOURS'
        logging.info(
            f"Current price for {symbol}: {current_price} from {price_source}")

        # Calculate gap
        if prev_close > 0:
            gap_pct = ((current_price - prev_close) / prev_close) * 100
        else:
            gap_pct = 0
        logging.info(f"Gap percentage for {symbol}: {gap_pct}")

        # Get volume
        if market_status['is_premarket']:
            volume = info.get('preMarketVolume', info.get(
                'regularMarketVolume', 0))
        elif market_status['is_regular']:
            volume = info.get('regularMarketVolume', 0)
        else:
            volume = info.get('postMarketVolume',
                              info.get('regularMarketVolume', 0))
        logging.info(f"Volume for {symbol}: {volume}")

        avg_volume = info.get('averageVolume', 1000000)
        logging.info(f"Average volume for {symbol}: {avg_volume}")

        # Get earnings date proximity if available
        earnings_days_away = 999  # Default to far away
        try:
            earnings_dates = ticker.calendar
            if not earnings_dates.empty and 'Earnings Date' in earnings_dates.index:
                earnings_date = earnings_dates.loc['Earnings Date'][0] if isinstance(
                    earnings_dates.loc['Earnings Date'], pd.Series) else earnings_dates.loc['Earnings Date']
                if not pd.isna(earnings_date):
                    earnings_date = pd.to_datetime(earnings_date)
                    today = pd.Timestamp.now(tz='US/Eastern')
                    earnings_days_away = (earnings_date - today).days
                    if earnings_days_away < 0:
                        earnings_days_away = 999  # Past earnings, irrelevant
                    logging.info(
                        f"Earnings days away for {symbol}: {earnings_days_away}")
        except Exception as e:
            logging.error(
                f"Error fetching earnings date for {symbol}: {str(e)}")

        # Debug statement to confirm data freshness
        data_timestamp = pd.Timestamp.now(
            tz='US/Eastern').strftime('%Y-%m-%d %H:%M:%S %Z')
        logging.info(f"Data fetched for {symbol} at ET time: {data_timestamp}")
        print(f"   Data fetched at ET time: {data_timestamp}")

        return {
            'success': True,
            'symbol': symbol,
            'current_price': current_price,
            'prev_close': prev_close,
            'gap_pct': gap_pct,
            'volume': volume,
            'avg_volume': avg_volume,
            'volume_ratio': volume / avg_volume if avg_volume > 0 else 1.0,
            'price_source': price_source,
            'market_status': market_status['status'],
            'earnings_days_away': earnings_days_away
        }

    except Exception as e:
        logging.error(f"Error fetching premarket data for {symbol}: {str(e)}")
        return {
            'success': False,
            'symbol': symbol,
            'error': str(e)
        }


def get_market_context():
    """Get overall market context (futures, VIX, sectors)"""
    try:
        # Get VIX
        vix = yf.Ticker('^VIX')
        vix_data = vix.history(period='1d')
        current_vix = vix_data['Close'].iloc[-1] if len(vix_data) > 0 else 20

        # Get SPY
        spy = yf.Ticker('SPY')
        spy_data = spy.history(period='2d')
        if len(spy_data) >= 2:
            spy_change = ((spy_data['Close'].iloc[-1] /
                          spy_data['Close'].iloc[-2]) - 1) * 100
        else:
            spy_change = 0

        # Get NASDAQ (for tech stocks)
        qqq = yf.Ticker('QQQ')
        qqq_data = qqq.history(period='2d')
        if len(qqq_data) >= 2:
            nasdaq_change = (
                (qqq_data['Close'].iloc[-1] / qqq_data['Close'].iloc[-2]) - 1) * 100
        else:
            nasdaq_change = 0

        # Determine market regime
        if current_vix < 15:
            regime = 'LOW_VOL'
            sentiment = 'CALM'
        elif current_vix < 20:
            regime = 'NORMAL'
            sentiment = 'BALANCED'
        elif current_vix < 30:
            regime = 'ELEVATED'
            sentiment = 'CAUTIOUS'
        else:
            regime = 'HIGH_VOL'
            sentiment = 'FEARFUL'

        return {
            'vix': current_vix,
            'regime': regime,
            'sentiment': sentiment,
            'spy_change': spy_change,
            'nasdaq_change': nasdaq_change
        }

    except Exception as e:
        return {
            'vix': 20,
            'regime': 'NORMAL',
            'sentiment': 'UNKNOWN',
            'spy_change': 0,
            'nasdaq_change': 0,
            'error': str(e)
        }


def run_premarket_prediction(symbol, premarket_data, market_context, advanced_indicators, mode='standard'):
    """Run prediction for one stock"""

    logging.info(f"Starting premarket prediction for {symbol}")
    print(f"\n{'='*80}")
    print(f" {symbol} PREMARKET ANALYSIS")
    print(f"{'='*80}")

    if not premarket_data['success']:
        logging.error(
            f"Failed to fetch data for {symbol}: {premarket_data.get('error')}")
        print(f"⚠️ Data unavailable: {premarket_data.get('error')}")
        return {
            'symbol': symbol,
            'direction': 'NEUTRAL',
            'confidence': 0.0,
            'reason': 'Data unavailable'
        }

    print(f"\n Market Data ({premarket_data['market_status']}):")
    print(f"   Data Source: {premarket_data['price_source']}")
    print(f"   Gap: {premarket_data['gap_pct']:+.2f}%")
    print(f"   Current: ${premarket_data['current_price']:.2f}")
    print(f"   Previous Close: ${premarket_data['prev_close']:.2f}")
    print(
        f"   Volume: {premarket_data['volume']:,} ({premarket_data['volume_ratio']:.1f}x avg)")

    print(f"\n Advanced Indicators:")
    if advanced_indicators:
        for key, value in advanced_indicators.items():
            if isinstance(value, dict):
                summary = value.get('reasoning') or value.get(
                    'signal') or value
                print(f"   {key}: {summary}")
            elif isinstance(value, (int, float)):
                print(f"   {key}: {value:.3f}")
            else:
                print(f"   {key}: {value}")
    else:
        print("   (no advanced indicators available)")

    indicator_features = interpret_indicator_signals(
        symbol, advanced_indicators)

    if indicator_features.get('risk_signals') or indicator_features.get('support_signals'):
        print("\n Indicator Balance:")
        if indicator_features['risk_signals']:
            print(f"   Risk flags: {', '.join(indicator_features['risk_signals'])}")
        if indicator_features['support_signals']:
            print(f"   Support flags: {', '.join(indicator_features['support_signals'])}")
        print(f"   Trap risk score: {indicator_features['trap_risk_score']:.2f}")
    # Prepare data for predictor

    predictor_data = {
        'gap_pct': premarket_data['gap_pct'] / 100.0,  # Convert to decimal
        'volume': premarket_data['volume'],
        'min_volume': adjust_premarket_volume_threshold(premarket_data['avg_volume']),
        'volume_ratio': premarket_data['volume_ratio'],
        'nasdaq_pct': market_context.get('nasdaq_change', 0) / 100.0,
        'spy_pct': market_context.get('spy_change', 0) / 100.0,
        'vix': market_context.get('vix', 20),
        'market_regime': market_context.get('regime', 'NORMAL'),
        'market_sentiment': market_context.get('sentiment', 'UNKNOWN'),
        'earnings_days_away': premarket_data.get('earnings_days_away', 999),
        # Social/sentiment proxies derived from free indicators
        'social_sentiment': indicator_features.get('sentiment_score', 0.0),
        # Trap signals inferred from indicator set
        'trap_signals': indicator_features.get('trap_signals', False),
        'trap_risk_score': indicator_features.get('trap_risk_score', 0.0),
        'indicator_bias': indicator_features.get('indicator_bias', 0.0),
        'trend_strength': indicator_features.get('trend_strength', 0.0),
        'sector_alignment': indicator_features.get('sector_alignment', 0.0),
        'ma_distance': indicator_features.get('ma_distance', 0.0),
        # Placeholder for specific news flags (to be enhanced with real data)
        'gov_contract_news': False,  # For PLTR
        'ai_news': False,  # For NVDA
        'ma_news': False,  # For AVGO
        'cloud_news': False  # For SNOW
    }

    rel = advanced_indicators.get('relative_strength') if isinstance(advanced_indicators, dict) else None
    if isinstance(rel, dict) and rel.get('success'):
        sector_return = rel.get('sector_return', 0.0)
        if symbol in ('AMD', 'NVDA', 'AVGO'):
            predictor_data['smh_pct'] = sector_return
            predictor_data['sector_pct'] = sector_return
        elif symbol in ('META', 'SNOW', 'PLTR'):
            predictor_data['sector_pct'] = sector_return

    if symbol == 'SNOW':
        cloud = advanced_indicators.get('cloud_strength') if isinstance(advanced_indicators, dict) else None
        if isinstance(cloud, dict) and cloud.get('success'):
            predictor_data['cloud_sector_pct'] = cloud.get('cloud_avg', 0.0)

    print(f"\n DEBUG: Passing to predictor:")
    print(f"   gap_pct = {predictor_data['gap_pct']*100:.2f}%")
    print(f"   volume = {predictor_data['volume']:,}")
    print(f"   min_volume = {predictor_data['min_volume']:,}")

    # Get stock-specific predictor
    predictor = get_predictor(symbol)

    # Run prediction
    prediction = predictor.predict(predictor_data)

    logging.info(f"Prediction for {symbol}: {prediction}")

    print(f"\n PREDICTION:")
    print(f"   Direction: {prediction['direction']}")
    print(f"   Confidence: {prediction['confidence']*100:.1f}%")
    print(
        f"   Reason: {prediction.get('reason', 'No specific reason provided')}")
    if 'warning' in prediction:
        print(f"   {prediction['warning']}")
    if prediction.get('confidence_breakdown'):
        print("\n Confidence Drivers:")
        for note in prediction['confidence_breakdown']:
            print(f"   - {note}")

    # Determine recommendation based on confidence
    confidence = prediction['confidence']
    direction = prediction['direction']
    if direction == 'NEUTRAL':
        recommendation = 'SKIP'
        position_size = 0.0
    else:
        if mode == 'decisive':
            if confidence >= 0.70:
                recommendation = 'STRONG_TRADE'
                position_size = 1.0
            elif confidence >= 0.60:
                recommendation = 'TRADE'
                position_size = 0.75
            elif confidence >= 0.50:
                recommendation = 'CAUTIOUS'
                position_size = 0.5
            elif confidence >= 0.45:
                recommendation = 'CAUTIOUS'
                position_size = 0.25
            else:
                recommendation = 'SKIP'
                position_size = 0.0
        else:
            if confidence >= 0.75:
                recommendation = 'STRONG_TRADE'
                position_size = 1.0
            elif confidence >= 0.65:
                recommendation = 'TRADE'
                position_size = 0.75
            elif confidence >= 0.53:
                recommendation = 'CAUTIOUS'
                position_size = 0.5
            else:
                recommendation = 'SKIP'
                position_size = 0.0

    print(
        f"\n📋 RECOMMENDATION: {'🟢' if recommendation in ['STRONG_TRADE', 'TRADE'] else '🟡' if recommendation == 'CAUTIOUS' else '⚪'} {recommendation}")
    print(f"   Position Size: {position_size*100:.0f}%")

    if recommendation != 'SKIP':
        # Calculate targets based on direction and typical volatility
        entry_price = premarket_data['current_price']
        if prediction['direction'] == 'UP':
            target_price = entry_price * 1.015  # +1.5%
            stop_price = entry_price * 0.99    # -1.0%
        elif prediction['direction'] == 'DOWN':
            target_price = entry_price * 0.985  # -1.5%
            stop_price = entry_price * 1.01    # +1.0%
        else:
            target_price = entry_price
            stop_price = entry_price

        print(f"\n Trade Plan:")
        print(f"   Entry: ${entry_price:.2f}")
        print(
            f"   Target: ${target_price:.2f} ({(target_price/entry_price-1)*100:+.1f}%)")
        print(
            f"   Stop: ${stop_price:.2f} ({(stop_price/entry_price-1)*100:+.1f}%)")
        print(f"   R:R Ratio: 1.5:1")

    return {
        'symbol': symbol,
        'direction': prediction['direction'],
        'confidence': confidence,
        'reason': prediction.get('reason', 'No specific reason provided'),
        'recommendation': recommendation,
        'position_size': position_size,
        'entry': premarket_data['current_price'],
        'target': target_price if recommendation != 'SKIP' else None,
        'stop': stop_price if recommendation != 'SKIP' else None,
        'warning': prediction.get('warning', ''),
        'prediction_data': predictor_data
    }


def run_premarket_multi_stock(stocks=None, mode='standard'):
    """Run premarket predictions for all stocks"""

    # Get both local and ET time
    et_tz = pytz.timezone('US/Eastern')
    now_et = datetime.now(et_tz)
    now_local = datetime.now()

    print(f"\n{'='*80}")
    print(f"🚀 PREMARKET MULTI-STOCK PREDICTION SYSTEM")
    print(f"{'='*80}")
    print(f"⏰ ET Time: {now_et.strftime('%Y-%m-%d %I:%M %p ET')}")
    print(f"🌍 Your Local Time: {now_local.strftime('%Y-%m-%d %I:%M %p')}")
    print(f"{'='*80}")
    print("\n Best Time to Run: 9:15 AM ET (US Market Premarket)")

    # Show market schedule in ET
    print("\n US Market Schedule (ET):")
    print("   Premarket: 4:00 AM - 9:30 AM ET")
    print("   Regular: 9:30 AM - 4:00 PM ET")
    print("   After Hours: 4:00 PM - 8:00 PM ET")

    # Check market hours
    market_status = check_market_hours()
    print(f"\n Current Market Status: {market_status['status']}")

    if not market_status['is_premarket']:
        print(f"\n{'!'*80}")
        print(" WARNING: NOT IN PREMARKET HOURS")
        print(f"{'!'*80}")
        print(f"\n You are running this at {now_et.strftime('%I:%M %p ET')}")
        print(f" For REAL premarket data, run between 4:00 AM - 9:30 AM ET")
        print(f" Best time: 9:15 AM ET (6:45 PM your local time)")
        print(f"\n System will use last available prices (gaps may be small/zero)")
        print(f" Predictions shown are DEMO only until premarket hours")
        print(f"{'!'*80}\n")
    else:
        print(f"\n PREMARKET HOURS: System will fetch LIVE premarket data!\n")

    # Default stocks
    if stocks is None:
        stocks = ['AMD', 'NVDA', 'META', 'AVGO', 'SNOW', 'PLTR']

    print(f"\n Analyzing {len(stocks)} stocks: {', '.join(stocks)}")

    # Get market context
    print(f"\n{'='*80}")
    print(f"🌐 MARKET CONTEXT")
    print(f"{'='*80}")

    market_context = get_market_context()

    print(f"\n📊 Market Overview:")
    print(f"   VIX: {market_context['vix']:.2f} ({market_context['regime']})")
    print(f"   Sentiment: {market_context['sentiment']}")
    print(f"   SPY: {market_context['spy_change']:+.2f}%")
    print(f"   NASDAQ: {market_context['nasdaq_change']:+.2f}%")

    # Run predictions for each stock
    results = {}

    for symbol in stocks:
        # Get premarket data
        premarket_data = get_premarket_data(symbol)

        # Get advanced indicators
        try:
            advanced_indicators = get_free_indicators(symbol)
        except:
            advanced_indicators = {}

        # Run prediction
        prediction = run_premarket_prediction(
            symbol, premarket_data, market_context, advanced_indicators, mode=mode)

        if prediction:
            results[symbol] = prediction

    # Summary
    print(f"\n{'='*80}")
    print(f"📊 TRADING SUMMARY")
    print(f"{'='*80}")

    trades = [r for r in results.values() if r['position_size'] > 0]

    if trades:
        print(f"\n🎯 {len(trades)} TRADING OPPORTUNITIES:\n")

        for trade in trades:
            print(f"{trade['symbol']}:")
            print(f"   Direction: {trade['direction']}")
            print(f"   Confidence: {trade['confidence']*100:.1f}%")
            if trade['target']:
                print(f"   Entry: ${trade['entry']:.2f}")
                print(f"   Target: ${trade['target']:.2f}")
                print(f"   Stop: ${trade['stop']:.2f}")
            print(f"   Position: {trade['position_size']*100:.0f}%")
            if trade['warning']:
                print(f"   ⚠️ {trade['warning']}")
            print()
    else:
        print(f"\n⚪ NO TRADES RECOMMENDED")
        print(f"   All signals below minimum confidence threshold")
        print(f"   Wait for better setups")

    # Check for correlation (all agreeing)
    if len(results) >= 3:
        directions = [r['direction'] for r in results.values()]
        confidences = [r['confidence'] for r in results.values()]

        all_same = len(set(directions)) == 1 and directions[0] != 'NEUTRAL'
        all_high = all(c > 0.75 for c in confidences)

        if all_same and all_high:
            print(f"\n{'!'*80}")
            print(f"⚠️ CORRELATION ALERT: ALL STOCKS AGREEING")
            print(f"{'!'*80}")
            print(
                f"\n⚠️ All stocks predicting {directions[0]} with high confidence")
            print(f"   Average: {sum(confidences)/len(confidences):.0f}%")
            print(f"\n💡 Possible causes:")
            print(f"   • Strong market trend (SPY/NASDAQ)")
            print(f"   • Universal factors overwhelming individual signals")
            print(f"   • Genuine market-wide move")
            print(f"   Be cautious - reduce position sizes if unsure")
            print(f"{'!'*80}\n")
        elif all_same:
            print(f"\nℹ️ Note: All stocks predicting {directions[0]}")
            print(f"   May indicate strong market trend")

    # Save results
    output_dir = Path(__file__).parent / "data" / "premarket"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / \
        f"predictions_{now_et.strftime('%Y%m%d_%H%M')}.json"

    with open(output_file, 'w') as f:
        json.dump({
            'timestamp': now_et.isoformat(),
            'market_context': market_context,
            'predictions': results
        }, f, indent=2)

    print(f"\n💾 Saved to: {output_file}")
    print(f"\n{'='*80}")
    print(f"✅ PREMARKET ANALYSIS COMPLETE!")
    print(f"{'='*80}")
    print(f"\n🎯 Next Steps:")
    print(f"   1. Review recommendations above")
    print(f"   2. Enter positions at 9:25-9:30 AM")
    print(f"   3. Set stops and targets immediately")
    print(f"   4. Monitor for special rules (AMD 9:35 exit!)")
    print(f"\nGood luck trading! 🚀\n")

    return results


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description='Premarket Multi-Stock Predictions')
    parser.add_argument('--stocks', nargs='+',
                        help='Specific stocks to analyze', default=None)
    parser.add_argument('--mode', choices=['standard', 'decisive'], default='standard',
                        help='Trading mode: standard (stricter) or decisive (more trades, smaller size)')

    args = parser.parse_args()

    # Run predictions
    run_premarket_multi_stock(stocks=args.stocks, mode=args.mode)
