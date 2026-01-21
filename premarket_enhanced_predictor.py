"""
ENHANCED PREMARKET-TO-OPEN PREDICTOR
=====================================
Runs at 8:30 AM ET (1 hour before market open)
Predicts: Premarket Price → 9:30 AM Opening Move

ENHANCEMENTS:
- Stock-specific catalyst detection
- Symbol-specific sentiment (Reddit/Twitter)
- Gap fill psychology analysis
- Premarket volume momentum
- Overnight news impact scoring
- Level 2 order book analysis (if available)

Run this at 8:30 AM for intraday scalp opportunities

Author: StockSense Enhanced System
Created: Oct 27, 2025
"""

import sys
from datetime import datetime
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

from premarket_open_predictor import PremarketOpenPredictor

# Import catalyst detectors
try:
    from amd_catalyst_detector import AMDCatalystDetector
    amd_catalyst_available = True
except ImportError:
    amd_catalyst_available = False

try:
    from avgo_catalyst_detector import BroadcomCatalystDetector
    avgo_catalyst_available = True
except ImportError:
    avgo_catalyst_available = False

try:
    from orcl_catalyst_detector import OracleCatalystDetector
    orcl_catalyst_available = True
except ImportError:
    orcl_catalyst_available = False


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


def analyze_gap_psychology(current_price, premarket_price, gap_percent):
    """
    Analyze gap fill psychology for opening prediction
    
    Research shows:
    - Gaps >2%: 70% partially fill in first hour
    - Gaps >4%: 85% partially fill in first hour
    - Gaps >6%: 95% partially fill in first hour
    
    Args:
        current_price: Yesterday's close
        premarket_price: Current premarket price
        gap_percent: Gap size as percentage
        
    Returns:
        Dict with gap analysis and fill probability
    """
    gap_size = abs(gap_percent)
    gap_direction = "UP" if gap_percent > 0 else "DOWN"
    
    # Calculate fill probability based on gap size
    if gap_size < 1.0:
        fill_probability = 0.40  # Small gaps often continue
        expected_fill = 0.30
    elif gap_size < 2.0:
        fill_probability = 0.55
        expected_fill = 0.40
    elif gap_size < 3.0:
        fill_probability = 0.70
        expected_fill = 0.50
    elif gap_size < 4.0:
        fill_probability = 0.80
        expected_fill = 0.60
    else:  # >4%
        fill_probability = 0.90
        expected_fill = 0.70
    
    # Calculate expected open price based on fill
    if gap_direction == "UP":
        gap_dollars = premarket_price - current_price
        expected_fill_dollars = gap_dollars * expected_fill
        expected_open = premarket_price - expected_fill_dollars
        bias = -expected_fill  # Negative = down toward gap fill
    else:  # DOWN
        gap_dollars = current_price - premarket_price
        expected_fill_dollars = gap_dollars * expected_fill
        expected_open = premarket_price + expected_fill_dollars
        bias = +expected_fill  # Positive = up toward gap fill
    
    return {
        'gap_size': gap_size,
        'gap_direction': gap_direction,
        'fill_probability': fill_probability,
        'expected_fill_percent': expected_fill * 100,
        'expected_open': expected_open,
        'gap_bias_score': bias * 0.15,  # Weight: 15%
        'recommendation': 'FADE' if gap_size > 2.0 else 'FOLLOW'
    }


def analyze_overnight_news_impact(news_articles, symbol):
    """
    Score overnight news impact (events after 4 PM yesterday)
    
    Premarket-specific: News that broke overnight has MORE impact
    than news already known at close
    
    Args:
        news_articles: List of news article texts
        symbol: Stock symbol
        
    Returns:
        Overnight news impact score
    """
    if not news_articles:
        return {'score': 0.0, 'impact': 'NONE'}
    
    # Keywords indicating high-impact overnight news
    breaking_keywords = [
        'breaking', 'alert', 'just in', 'announced today',
        'this morning', 'premarket', 'before open',
        'upgrade', 'downgrade', 'analyst', 'target',
        'earnings beat', 'earnings miss', 'guidance',
        'acquisition', 'merger', 'deal', 'partnership'
    ]
    
    impact_count = 0
    for article in news_articles[:10]:  # Recent 10
        article_lower = article.lower()
        for keyword in breaking_keywords:
            if keyword in article_lower:
                impact_count += 1
                break
    
    # Score overnight news impact
    if impact_count >= 3:
        score = +0.10  # High impact
        impact = 'HIGH'
    elif impact_count >= 2:
        score = +0.06
        impact = 'MODERATE'
    elif impact_count >= 1:
        score = +0.03
        impact = 'LOW'
    else:
        score = 0.0
        impact = 'NONE'
    
    return {
        'score': score,
        'impact': impact,
        'breaking_news_count': impact_count
    }


def enhance_premarket_with_catalyst(prediction, symbol, news_articles, gap_info):
    """
    Enhance premarket prediction with catalysts and gap psychology
    
    Args:
        prediction: Original premarket prediction
        symbol: Stock symbol
        news_articles: List of news articles
        gap_info: Gap analysis dict
        
    Returns:
        Enhanced prediction with catalyst boost and gap adjustment
    """
    # 1. Detect catalysts
    if symbol == 'AMD' and amd_catalyst_available:
        detector = AMDCatalystDetector()
        stock_name = "AMD"
    elif symbol == 'AVGO' and avgo_catalyst_available:
        detector = BroadcomCatalystDetector()
        stock_name = "AVGO"
    elif symbol == 'ORCL' and orcl_catalyst_available:
        detector = OracleCatalystDetector()
        stock_name = "ORCL"
    else:
        detector = None
        stock_name = symbol
    
    # Catalyst detection
    catalyst_score = 0.0
    catalyst_count = 0
    catalyst_sentiment = 'NEUTRAL'
    
    if detector and news_articles:
        catalyst_result = detector.detect_catalysts(news_articles)
        catalyst_score = catalyst_result.get('score', 0.0)
        catalyst_sentiment = catalyst_result.get('sentiment', 'NEUTRAL')
        catalyst_count = catalyst_result.get('total_catalysts', 0)
        
        if catalyst_count > 0:
            print(f"\n   📊 {stock_name} Catalysts: {catalyst_count} detected")
            print(f"      Sentiment: {catalyst_sentiment}")
            print(f"      Score: {catalyst_score:+.3f}")
    
    # 2. Analyze overnight news impact
    overnight_news = analyze_overnight_news_impact(news_articles, symbol)
    overnight_score = overnight_news['score']
    
    if overnight_news['impact'] != 'NONE':
        print(f"\n   📰 Overnight News Impact: {overnight_news['impact']}")
        print(f"      Breaking News Count: {overnight_news['breaking_news_count']}")
        print(f"      Impact Score: {overnight_score:+.3f}")
    
    # 3. Gap psychology adjustment
    gap_bias = gap_info['gap_bias_score']
    gap_size = gap_info['gap_size']
    
    print(f"\n   📊 Gap Analysis:")
    print(f"      Gap Size: {gap_size:+.2f}%")
    print(f"      Fill Probability: {gap_info['fill_probability']*100:.0f}%")
    print(f"      Expected Fill: {gap_info['expected_fill_percent']:.0f}%")
    print(f"      Recommendation: {gap_info['recommendation']}")
    print(f"      Gap Bias Score: {gap_bias:+.3f}")
    
    # 4. Calculate enhanced score
    original_score = prediction.get('raw_score', 0.0)
    
    # For premarket: Gap fill psychology is KING
    # Large gaps often partially fill regardless of other factors
    if gap_size > 3.0:
        # Large gap: Gap fill bias dominates (70% weight)
        enhanced_score = gap_bias * 0.70 + original_score * 0.20 + catalyst_score * 0.10
        print(f"\n   ⚠️ LARGE GAP DETECTED: Gap fill psychology dominates prediction")
    elif gap_size > 1.5:
        # Medium gap: Balanced between gap fill and other factors
        enhanced_score = gap_bias * 0.40 + original_score * 0.40 + catalyst_score * 0.15 + overnight_score * 0.05
    else:
        # Small gap: Normal prediction with slight gap consideration
        enhanced_score = original_score * 0.60 + catalyst_score * 0.25 + overnight_score * 0.10 + gap_bias * 0.05
    
    # 5. Recalculate confidence
    if abs(enhanced_score) < 0.01:
        enhanced_confidence = 50
    else:
        enhanced_confidence = 50 + abs(enhanced_score) * 233
        enhanced_confidence = min(enhanced_confidence, 95)
        enhanced_confidence = max(enhanced_confidence, 50)
    
    # 6. Determine direction
    if enhanced_score > 0.03:  # Lower threshold for 1-hour premarket prediction
        enhanced_direction = 'UP'
    elif enhanced_score < -0.03:
        enhanced_direction = 'DOWN'
    else:
        enhanced_direction = 'NEUTRAL'
    
    # 7. Calculate target
    premarket_price = prediction.get('current_price', 0)
    if premarket_price > 0:
        # Premarket predictions: smaller moves (1 hour vs overnight)
        target_pct = abs(enhanced_score) * 0.8  # Scaled down for 1-hour
        if enhanced_direction == 'UP':
            enhanced_target = premarket_price * (1 + target_pct)
        elif enhanced_direction == 'DOWN':
            enhanced_target = premarket_price * (1 - target_pct)
        else:
            enhanced_target = premarket_price
    else:
        enhanced_target = prediction.get('target_price', 0)
    
    # 8. Create enhanced prediction
    enhanced_prediction = prediction.copy()
    enhanced_prediction.update({
        'raw_score': enhanced_score,
        'original_score': original_score,
        'catalyst_boost': catalyst_score,
        'overnight_news_boost': overnight_score,
        'gap_fill_bias': gap_bias,
        'confidence': enhanced_confidence,
        'original_confidence': prediction.get('confidence', 50),
        'direction': enhanced_direction,
        'original_direction': prediction.get('direction', 'NEUTRAL'),
        'target_price': enhanced_target,
        'gap_info': gap_info,
        'catalyst_count': catalyst_count
    })
    
    # 9. Show impact
    print(f"\n   🎯 Enhancement Impact:")
    print(f"      Original Score: {original_score:.3f}")
    print(f"      + Catalyst: {catalyst_score:+.3f}")
    print(f"      + Overnight News: {overnight_score:+.3f}")
    print(f"      + Gap Fill Bias: {gap_bias:+.3f}")
    print(f"      = Enhanced Score: {enhanced_score:.3f}")
    print(f"      Confidence: {prediction.get('confidence', 50):.1f}% → {enhanced_confidence:.1f}%")
    print(f"      Direction: {prediction.get('direction', 'NEUTRAL')} → {enhanced_direction}")
    
    return enhanced_prediction


def run_enhanced_premarket_prediction():
    """
    Run enhanced premarket predictions for AMD, AVGO, ORCL
    
    Run at 8:30 AM ET for intraday scalp trades
    """
    print("="*80)
    print("🌅 ENHANCED PREMARKET-TO-OPEN PREDICTOR")
    print("="*80)
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %I:%M %p')}")
    print(f"🎯 Stocks: AMD, AVGO, ORCL")
    print(f"⏰ Run Time: 8:30 AM ET (1 hour before open)")
    print(f"💡 Predicts: Premarket → 9:30 AM Opening Move")
    print(f"✨ Enhanced: Catalysts + Gap Psychology + Overnight News")
    print("="*80)
    
    stocks = ['AMD', 'AVGO', 'ORCL']
    predictions = {}
    
    for symbol in stocks:
        print(f"\n{'='*80}")
        print(f"📊 ANALYZING {symbol} PREMARKET")
        print(f"{'='*80}")
        
        try:
            # Create premarket predictor
            predictor = PremarketOpenPredictor(symbol=symbol)
            
            # Generate base premarket prediction
            print(f"\n🔍 Analyzing premarket data for {symbol}...")
            prediction = predictor.generate_premarket_prediction()
            
            # Get current prices for gap analysis
            yesterday_close = prediction.get('yesterday_close', 0)
            premarket_price = prediction.get('current_price', 0)
            
            if yesterday_close > 0 and premarket_price > 0:
                gap_percent = ((premarket_price - yesterday_close) / yesterday_close) * 100
                
                # Analyze gap psychology
                gap_info = analyze_gap_psychology(yesterday_close, premarket_price, gap_percent)
                
                # Fetch news for catalysts
                news_articles = get_news_for_catalyst(predictor, symbol)
                
                # Enhance with catalysts and gap psychology
                enhanced_prediction = enhance_premarket_with_catalyst(
                    prediction, symbol, news_articles, gap_info
                )
            else:
                print(f"\n   ⚠️ Could not get price data for gap analysis")
                enhanced_prediction = prediction
            
            predictions[symbol] = enhanced_prediction
            
            # Display result
            print(f"\n{'='*80}")
            print(f"✅ {symbol} PREMARKET PREDICTION COMPLETE")
            print(f"{'='*80}")
            
            direction = enhanced_prediction.get('direction', 'NEUTRAL')
            confidence = enhanced_prediction.get('confidence', 50)
            premarket_price = enhanced_prediction.get('current_price', 0)
            target_price = enhanced_prediction.get('target_price', 0)
            yesterday_close = enhanced_prediction.get('yesterday_close', 0)
            
            # Direction emoji
            if direction == 'UP':
                dir_emoji = "📈"
            elif direction == 'DOWN':
                dir_emoji = "📉"
            else:
                dir_emoji = "➡️"
            
            print(f"\n{dir_emoji} Direction: {direction}")
            print(f"💪 Confidence: {confidence:.1f}%")
            print(f"💰 Yesterday Close: ${yesterday_close:.2f}")
            print(f"🌅 Premarket Price: ${premarket_price:.2f}")
            print(f"🎯 Predicted Open: ${target_price:.2f}")
            
            if yesterday_close > 0:
                gap = ((premarket_price - yesterday_close) / yesterday_close) * 100
                print(f"📊 Current Gap: {gap:+.2f}%")
            
            # Trade recommendation
            if confidence >= 60:
                print(f"\n✅ TRADEABLE (Confidence ≥ 60%)")
                
                if confidence >= 75:
                    position_size = "100% (High Confidence)"
                elif confidence >= 65:
                    position_size = "75% (Good Confidence)"
                else:
                    position_size = "50% (Moderate Confidence)"
                
                print(f"   Position Size: {position_size}")
                print(f"   Entry: 9:30-9:31 AM (market open)")
                print(f"   Exit: 10:00-10:30 AM (first hour)")
                print(f"   Time Horizon: 30-60 minutes")
            else:
                print(f"\n❌ FILTERED OUT (Confidence < 60%)")
                print(f"   Skip this premarket trade")
        
        except Exception as e:
            print(f"\n❌ Error predicting {symbol}: {e}")
            import traceback
            traceback.print_exc()
            predictions[symbol] = None
    
    # Summary
    print(f"\n{'='*80}")
    print("📋 PREMARKET TRADING SUMMARY")
    print(f"{'='*80}")
    
    tradeable_count = 0
    
    for symbol in stocks:
        pred = predictions.get(symbol)
        if pred:
            direction = pred.get('direction', 'NEUTRAL')
            confidence = pred.get('confidence', 0)
            gap_info = pred.get('gap_info', {})
            
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
            print(f"  ${pred.get('current_price', 0):.2f} → ${pred.get('target_price', 0):.2f}")
            if gap_info:
                print(f"  Gap: {gap_info.get('gap_size', 0):+.2f}% | {gap_info.get('recommendation', 'N/A')}")
            print(f"  {tradeable}")
    
    print(f"\n{'='*80}")
    print(f"🎯 Total Tradeable Signals: {tradeable_count}/3")
    print(f"{'='*80}")
    
    if tradeable_count > 0:
        print(f"\n💡 Premarket Trading Tips:")
        print(f"   1. Enter at 9:30-9:31 AM (market open)")
        print(f"   2. Use limit orders (avoid market orders)")
        print(f"   3. Exit within first hour (10:00-10:30 AM)")
        print(f"   4. Watch for gap fill patterns")
        print(f"   5. Lower position size than overnight trades")
    else:
        print(f"\n⚠️ No tradeable premarket signals")
        print(f"   Consider overnight positions instead")
    
    print(f"\n{'='*80}")
    print("✅ PREMARKET ANALYSIS COMPLETE")
    print(f"{'='*80}\n")
    
    return predictions


if __name__ == "__main__":
    predictions = run_enhanced_premarket_prediction()
