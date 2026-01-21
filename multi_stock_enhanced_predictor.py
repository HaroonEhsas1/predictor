"""
ENHANCED MULTI-STOCK PREDICTOR
===============================
Runs predictions for AMD, AVGO, and ORCL with ALL enhancements:
- Stock-specific catalyst detection
- Symbol-specific Reddit/Twitter sentiment
- All bias fixes and improvements

Run this at 3:50 PM before market close for overnight swing trades

Author: StockSense System
Created: Oct 27, 2025
"""

import sys
from datetime import datetime
from comprehensive_nextday_predictor import ComprehensiveNextDayPredictor

# Import catalyst detectors
try:
    from amd_catalyst_detector import AMDCatalystDetector
    amd_catalyst_available = True
except ImportError:
    print("⚠️ AMD catalyst detector not found")
    amd_catalyst_available = False

try:
    from avgo_catalyst_detector import BroadcomCatalystDetector
    avgo_catalyst_available = True
except ImportError:
    print("⚠️ AVGO catalyst detector not found")
    avgo_catalyst_available = False

try:
    from orcl_catalyst_detector import OracleCatalystDetector
    orcl_catalyst_available = True
except ImportError:
    print("⚠️ ORCL catalyst detector not found")
    orcl_catalyst_available = False

try:
    from nvda_catalyst_detector import NVDACatalystDetector
    nvda_catalyst_available = True
except ImportError:
    print("⚠️ NVDA catalyst detector not found")
    nvda_catalyst_available = False


def get_news_for_catalyst(predictor, symbol):
    """Fetch news articles for catalyst detection"""
    try:
        news_data = predictor.get_news_sentiment()
        articles = news_data.get('articles', [])

        # Extract article titles/snippets
        news_list = []
        for article in articles[:20]:  # Top 20 articles
            title = article.get('title', '')
            summary = article.get('summary', '')
            text = f"{title} {summary}"
            if text.strip():
                news_list.append(text)

        return news_list
    except Exception as e:
        print(f"   ⚠️ Could not fetch news for {symbol}: {e}")
        return []


def enhance_prediction_with_catalyst(prediction, symbol, news_articles):
    """
    Enhance prediction with stock-specific catalyst detection

    Args:
        prediction: Original prediction dict
        symbol: Stock symbol (AMD, AVGO, ORCL)
        news_articles: List of news article texts

    Returns:
        Enhanced prediction dict with catalyst boost
    """
    # Select appropriate catalyst detector
    if symbol == 'AMD' and amd_catalyst_available:
        detector = AMDCatalystDetector()
        stock_name = "AMD"
    elif symbol == 'AVGO' and avgo_catalyst_available:
        detector = BroadcomCatalystDetector()
        stock_name = "AVGO"
    elif symbol == 'ORCL' and orcl_catalyst_available:
        detector = OracleCatalystDetector()
        stock_name = "ORCL"
    elif symbol == 'NVDA' and nvda_catalyst_available:
        detector = NVDACatalystDetector()
        stock_name = "NVDA"
    else:
        # No catalyst detector available
        return prediction

    # Detect catalysts
    catalyst_result = detector.detect_catalysts(news_articles)
    catalyst_score = catalyst_result.get('score', 0.0)
    catalyst_sentiment = catalyst_result.get('sentiment', 'NEUTRAL')
    total_catalysts = catalyst_result.get('total_catalysts', 0)

    if total_catalysts == 0:
        print(f"\n   📊 {stock_name} Catalysts: None detected")
        return prediction

    # Show catalyst info
    print(f"\n   📊 {stock_name} Catalysts Detected: {total_catalysts}")
    print(f"      Sentiment: {catalyst_sentiment}")
    print(f"      Score: {catalyst_score:+.3f}")

    if catalyst_result.get('top_catalysts'):
        print(f"      Top Catalysts:")
        for cat in catalyst_result['top_catalysts'][:2]:
            impact_emoji = "📈" if cat['score'] > 0 else "📉"
            print(
                f"         {impact_emoji} {cat['category']}: {cat['score']:+.3f}")

    # Calculate enhanced score
    original_score = prediction.get('raw_score', 0.0)
    enhanced_score = original_score + catalyst_score

    # Recalculate confidence with enhanced score
    if abs(enhanced_score) < 0.01:
        enhanced_confidence = 50
    else:
        # Use same confidence formula as main predictor
        enhanced_confidence = 50 + abs(enhanced_score) * 233
        enhanced_confidence = min(enhanced_confidence, 95)
        enhanced_confidence = max(enhanced_confidence, 50)

    # Determine direction with enhanced score
    if enhanced_score > 0.04:
        enhanced_direction = 'UP'
    elif enhanced_score < -0.04:
        enhanced_direction = 'DOWN'
    else:
        enhanced_direction = 'NEUTRAL'

    # Calculate new target with enhanced confidence
    current_price = prediction.get('current_price', 0)
    if current_price > 0:
        # Adjust target based on enhanced score
        target_pct = abs(enhanced_score) * 1.5  # Similar to original
        if enhanced_direction == 'UP':
            enhanced_target = current_price * (1 + target_pct)
        elif enhanced_direction == 'DOWN':
            enhanced_target = current_price * (1 - target_pct)
        else:
            enhanced_target = current_price
    else:
        enhanced_target = prediction.get('target_price', 0)

    # Create enhanced prediction
    enhanced_prediction = prediction.copy()
    enhanced_prediction.update({
        'raw_score': enhanced_score,
        'catalyst_boost': catalyst_score,
        'original_score': original_score,
        'confidence': enhanced_confidence,
        'original_confidence': prediction.get('confidence', 50),
        'direction': enhanced_direction,
        'original_direction': prediction.get('direction', 'NEUTRAL'),
        'target_price': enhanced_target,
        'catalyst_sentiment': catalyst_sentiment,
        'catalyst_count': total_catalysts
    })

    # Show enhancement impact
    original_conf = prediction.get('confidence', 50)
    original_dir = prediction.get('direction', 'NEUTRAL')

    print(f"\n   🎯 Enhancement Impact:")
    print(
        f"      Score: {original_score:.3f} → {enhanced_score:.3f} ({catalyst_score:+.3f})")
    print(
        f"      Confidence: {original_conf:.1f}% → {enhanced_confidence:.1f}%")
    print(f"      Direction: {original_dir} → {enhanced_direction}")

    return enhanced_prediction


def run_enhanced_multi_stock_prediction():
    """
    Run enhanced predictions for AMD, AVGO, ORCL, NVDA, and PTLR
    Includes catalyst detection and all improvements
    """
    print("="*80)
    print("🚀 ENHANCED MULTI-STOCK OVERNIGHT SWING PREDICTOR")
    print("="*80)
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %I:%M %p')}")
    print(f"🎯 Stocks: AMD, AVGO, ORCL, NVDA")
    print(f"💡 Includes: Catalyst Detection + Reddit/Twitter Fix + All Enhancements")
    print("="*80)

    # Stocks to predict
    stocks = ['AMD', 'AVGO', 'ORCL', 'NVDA']
    predictions = {}

    # Run prediction for each stock
    for symbol in stocks:
        print(f"\n{'='*80}")
        print(f"📊 ANALYZING {symbol}")
        print(f"{'='*80}")

        try:
            # Create predictor
            predictor = ComprehensiveNextDayPredictor(symbol=symbol)

            # Generate base prediction
            print(f"\n🔍 Fetching data for {symbol}...")
            prediction = predictor.generate_comprehensive_prediction()

            # Fetch news for catalyst detection
            print(f"\n📰 Fetching news for catalyst analysis...")
            news_articles = get_news_for_catalyst(predictor, symbol)

            # Enhance with catalysts
            if news_articles:
                enhanced_prediction = enhance_prediction_with_catalyst(
                    prediction, symbol, news_articles
                )
            else:
                enhanced_prediction = prediction
                print(f"\n   ⚠️ No news available for catalyst detection")

            predictions[symbol] = enhanced_prediction

            # Display result
            print(f"\n{'='*80}")
            print(f"✅ {symbol} PREDICTION COMPLETE")
            print(f"{'='*80}")

            direction = enhanced_prediction.get('direction', 'NEUTRAL')
            confidence = enhanced_prediction.get('confidence', 50)
            current_price = enhanced_prediction.get('current_price', 0)
            target_price = enhanced_prediction.get('target_price', 0)
            stop_loss = enhanced_prediction.get('stop_loss', 0)

            # Direction emoji
            if direction == 'UP':
                dir_emoji = "📈"
            elif direction == 'DOWN':
                dir_emoji = "📉"
            else:
                dir_emoji = "➡️"

            print(f"\n{dir_emoji} Direction: {direction}")
            print(f"💪 Confidence: {confidence:.1f}%")
            print(f"💰 Current Price: ${current_price:.2f}")
            print(f"🎯 Target Price: ${target_price:.2f}")
            print(f"🛑 Stop Loss: ${stop_loss:.2f}")

            if 'catalyst_boost' in enhanced_prediction:
                boost = enhanced_prediction['catalyst_boost']
                print(f"🚀 Catalyst Boost: {boost:+.3f}")

            # Trade recommendation
            if confidence >= 60:
                print(f"\n✅ TRADEABLE (Confidence ≥ 60%)")

                # Position sizing based on confidence
                if confidence >= 85:
                    position_size = "100% (High Confidence)"
                elif confidence >= 75:
                    position_size = "75% (Good Confidence)"
                else:
                    position_size = "50% (Moderate Confidence)"

                print(f"   Position Size: {position_size}")
                print(f"   Entry: Market on close at 4:00 PM")
                print(f"   Exit: Market open at 9:30 AM (first minute)")
            else:
                print(f"\n❌ FILTERED OUT (Confidence < 60%)")
                print(f"   Skip this trade")

        except Exception as e:
            print(f"\n❌ Error predicting {symbol}: {e}")
            import traceback
            traceback.print_exc()
            predictions[symbol] = None

    # Summary
    print(f"\n{'='*80}")
    print("📋 TRADING SUMMARY")
    print(f"{'='*80}")

    tradeable_count = 0

    for symbol in stocks:
        pred = predictions.get(symbol)
        if pred:
            direction = pred.get('direction', 'NEUTRAL')
            confidence = pred.get('confidence', 0)

            if direction == 'UP':
                dir_emoji = "📈"
            elif direction == 'DOWN':
                dir_emoji = "📉"
            else:
                dir_emoji = "➡️"

            tradeable = "✅ TRADE" if confidence >= 60 else "❌ SKIP"

            if confidence >= 60:
                tradeable_count += 1

            print(f"\n{symbol}:")
            print(f"  {dir_emoji} {direction} @ {confidence:.1f}% confidence")
            print(
                f"  ${pred.get('current_price', 0):.2f} → ${pred.get('target_price', 0):.2f}")
            print(f"  {tradeable}")

    print(f"\n{'='*80}")
    print(f"🎯 Total Tradeable Signals: {tradeable_count}/3")
    print(f"{'='*80}")

    if tradeable_count > 0:
        print(f"\n💡 Next Steps:")
        print(f"   1. Review predictions above")
        print(f"   2. Enter positions at 4:00 PM (market close)")
        print(f"   3. Exit at 9:30 AM (market open, first minute)")
        print(f"   4. Expect 75-85% of target at market open")
    else:
        print(f"\n⚠️ No tradeable signals today")
        print(f"   Wait for better setups tomorrow")

    print(f"\n{'='*80}")
    print("✅ ANALYSIS COMPLETE")
    print(f"{'='*80}\n")

    return predictions


if __name__ == "__main__":
    predictions = run_enhanced_multi_stock_prediction()
