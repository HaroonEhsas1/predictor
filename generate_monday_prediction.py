#!/usr/bin/env python3
"""
Generate Monday prediction using collected weekend data
"""
import sys
import os
from datetime import datetime, timedelta
import pytz

# Add paths
sys.path.append(os.path.dirname(__file__))

# Import weekend collector
from weekend_collector import weekend_collector

# Import database for data retrieval
try:
    from database.replit_database_bridge import prediction_db
    DB_AVAILABLE = True
except ImportError:
    prediction_db = None
    DB_AVAILABLE = False

def get_next_monday():
    """Get next Monday's date"""
    et_tz = pytz.timezone('US/Eastern')
    now = datetime.now(et_tz)
    
    # Find next Monday (weekday 0 = Monday)
    days_ahead = 0 - now.weekday()  # Monday is 0
    if days_ahead <= 0:  # If today is Monday or later in the week
        days_ahead += 7
    
    next_monday = now + timedelta(days=days_ahead)
    return next_monday.date()

def generate_monday_signal():
    """Generate trading signal for Monday using weekend data"""
    print("🚀 GENERATING MONDAY TRADING SIGNAL")
    print("=" * 80)
    
    # Get target date (next Monday)
    target_date = get_next_monday()
    print(f"📅 Target Date: {target_date} (Monday)")
    
    # Get weekend data
    weekend_data = weekend_collector.get_weekend_data(target_date)
    
    if not weekend_data:
        print("❌ No weekend data available!")
        print("🔄 Collecting fresh weekend data...")
        weekend_data = weekend_collector.run_cycle(target_date, force_refresh=True)
    
    if not weekend_data:
        print("❌ Failed to collect weekend data")
        return None
    
    # Extract sentiment scores
    news_sentiment = weekend_data.get('news_sentiment', {})
    futures_data = weekend_data.get('futures_data', {})
    crypto_sentiment = weekend_data.get('crypto_sentiment', {})
    sector_analysis = weekend_data.get('sector_analysis', {})
    
    news_score = news_sentiment.get('overall_score', 0.0)
    futures_score = futures_data.get('overall_sentiment', 0.0)
    crypto_score = crypto_sentiment.get('overall_sentiment', 0.0)
    sector_score = sector_analysis.get('overall_score', 0.0)
    
    current_price = weekend_data.get('current_amd_price', 0.0)
    
    print(f"\n📊 WEEKEND DATA ANALYSIS:")
    print(f"   News Sentiment:     {news_score:+.3f} (Weight: 50%)")
    print(f"   Futures Sentiment:  {futures_score:+.3f} (Weight: 35%)")
    print(f"   Crypto Sentiment:   {crypto_score:+.3f} (Weight: 10%)")
    print(f"   Sector Sentiment:   {sector_score:+.3f} (Weight: 5%)")
    print(f"   Current AMD Price:  ${current_price:.2f}")
    
    # Calculate overall sentiment (matching the system's algorithm)
    overall_sentiment = (news_score * 0.50) + (futures_score * 0.35) + (crypto_score * 0.10) + (sector_score * 0.05)
    
    # Calculate data quality
    data_quality_count = len([x for x in [news_score, futures_score, crypto_score] if x != 0])
    quality_factor = min(data_quality_count / 3.0, 1.0)
    
    # Dynamic threshold
    directional_threshold = 0.08 + (0.04 * (1.0 - quality_factor))
    
    print(f"\n📈 SIGNAL CALCULATION:")
    print(f"   Overall Sentiment:  {overall_sentiment:+.3f}")
    print(f"   Data Quality:       {data_quality_count}/3 sources ({quality_factor*100:.0f}%)")
    print(f"   Directional Threshold: ±{directional_threshold:.3f}")
    
    # Determine direction and confidence
    if overall_sentiment > directional_threshold:
        direction = 'UP'
        signal = 'BUY'
        base_conf = 58
        sentiment_boost = min(overall_sentiment * 30, 30)
        quality_boost = quality_factor * 5
        confidence = min(base_conf + sentiment_boost + quality_boost, 88.0)
        target_price = current_price * (1 + (confidence / 100 * 0.02))
    elif overall_sentiment < -directional_threshold:
        direction = 'DOWN'
        signal = 'SELL'
        base_conf = 58
        sentiment_boost = min(abs(overall_sentiment) * 30, 30)
        quality_boost = quality_factor * 5
        confidence = min(base_conf + sentiment_boost + quality_boost, 88.0)
        target_price = current_price * (1 - (confidence / 100 * 0.02))
    else:
        direction = 'NEUTRAL'
        signal = 'HOLD'
        neutrality_strength = 1.0 - (abs(overall_sentiment) / directional_threshold)
        base_neutral = 40 + (data_quality_count * 3)
        confidence = min(base_neutral + (neutrality_strength * 10), 52)
        target_price = current_price
    
    # Calculate expected move
    expected_move = target_price - current_price
    expected_move_pct = (expected_move / current_price) * 100 if current_price > 0 else 0
    
    print(f"\n" + "=" * 80)
    print(f"🎯 MONDAY PRE-MARKET TRADING SIGNAL")
    print(f"=" * 80)
    print(f"📅 For: {target_date} (Monday Opening)")
    print(f"🎯 Signal: {signal} ({direction})")
    print(f"📊 Confidence: {confidence:.1f}%")
    print(f"💰 Current Price: ${current_price:.2f}")
    print(f"🎯 Target Price: ${target_price:.2f}")
    print(f"📈 Expected Move: ${expected_move:+.2f} ({expected_move_pct:+.2f}%)")
    print(f"=" * 80)
    
    # Provide trading recommendation
    print(f"\n💡 PRE-MARKET ORDER RECOMMENDATION:")
    if signal == 'BUY':
        print(f"   ✅ BULLISH - Place BUY order for Monday pre-market")
        print(f"   📍 Entry: Around ${current_price:.2f}")
        print(f"   🎯 Target: ${target_price:.2f}")
        print(f"   ⚠️ Stop Loss: Consider ${current_price * 0.98:.2f} (2% below entry)")
    elif signal == 'SELL':
        print(f"   ⚠️ BEARISH - Consider SELL or avoid buying Monday pre-market")
        print(f"   📍 Current: ${current_price:.2f}")
        print(f"   🎯 Target: ${target_price:.2f}")
        print(f"   ⚠️ Risk: Market may open lower")
    else:
        print(f"   ⏸️ NEUTRAL - Wait for clearer signals")
        print(f"   📍 Price Range: ${current_price * 0.99:.2f} - ${current_price * 1.01:.2f}")
        print(f"   ⚠️ Recommendation: Stay on sidelines or small positions only")
    
    # Signal strength breakdown
    print(f"\n📊 SIGNAL STRENGTH BREAKDOWN:")
    if news_score != 0:
        news_direction = "BULLISH" if news_score > 0 else "BEARISH"
        print(f"   📰 News: {news_direction} ({news_score:+.3f})")
    if futures_score != 0:
        futures_direction = "BULLISH" if futures_score > 0 else "BEARISH"
        print(f"   📈 Futures: {futures_direction} ({futures_score:+.3f})")
    if crypto_score != 0:
        crypto_direction = "RISK-ON" if crypto_score > 0 else "RISK-OFF"
        print(f"   ₿ Crypto: {crypto_direction} ({crypto_score:+.3f})")
    if sector_score != 0:
        sector_direction = "BULLISH" if sector_score > 0 else "BEARISH"
        print(f"   🏭 Sector: {sector_direction} ({sector_score:+.3f})")
    
    print(f"\n" + "=" * 80)
    
    return {
        'direction': direction,
        'signal': signal,
        'confidence': confidence,
        'current_price': current_price,
        'target_price': target_price,
        'expected_move': expected_move,
        'overall_sentiment': overall_sentiment,
        'target_date': str(target_date)
    }

if __name__ == "__main__":
    prediction = generate_monday_signal()
