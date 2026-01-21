"""
ORACLE ENHANCED PREDICTOR
=========================
Wraps the comprehensive predictor with ORCL-specific catalyst detection
Adds 10-15% boost to ORCL predictions when catalysts detected

Usage:
    from orcl_enhanced_predictor import generate_orcl_prediction
    prediction = generate_orcl_prediction()
"""

from comprehensive_nextday_predictor import ComprehensiveNextDayPredictor
from orcl_catalyst_detector import OracleCatalystDetector
import requests
import os
from dotenv import load_dotenv

load_dotenv()

def get_orcl_news_for_catalyst():
    """Fetch Oracle news for catalyst detection"""
    news_articles = []
    
    # Finnhub News
    try:
        finnhub_key = os.getenv('FINNHUB_API_KEY')
        if finnhub_key:
            url = f"https://finnhub.io/api/v1/company-news?symbol=ORCL&from=2025-10-26&to=2025-10-27&token={finnhub_key}"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                articles = response.json()
                for article in articles[:20]:  # Analyze up to 20 articles
                    if 'headline' in article:
                        news_articles.append(article['headline'])
                    if 'summary' in article:
                        news_articles.append(article['summary'])
    except Exception as e:
        print(f"   ⚠️ Error fetching Finnhub news: {e}")
    
    # Alpha Vantage News
    try:
        av_key = os.getenv('ALPHA_VANTAGE_API_KEY')
        if av_key:
            url = f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers=ORCL&apikey={av_key}"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if 'feed' in data:
                    for item in data['feed'][:10]:  # Top 10
                        if 'title' in item:
                            news_articles.append(item['title'])
                        if 'summary' in item:
                            news_articles.append(item['summary'])
    except Exception as e:
        print(f"   ⚠️ Error fetching Alpha Vantage news: {e}")
    
    return news_articles

def generate_orcl_prediction():
    """
    Generate ORCL prediction with catalyst enhancement
    
    Returns:
        Enhanced prediction dict with catalyst details
    """
    print("\n" + "="*80)
    print("🔮 ORACLE ENHANCED PREDICTION (with Catalyst Detection)")
    print("="*80)
    
    # Get standard prediction
    predictor = ComprehensiveNextDayPredictor(symbol='ORCL')
    standard_prediction = predictor.generate_comprehensive_prediction()
    
    # Detect ORCL-specific catalysts
    print("\n" + "="*80)
    print("🔍 DETECTING ORCL-SPECIFIC CATALYSTS")
    print("="*80)
    
    catalyst_detector = OracleCatalystDetector()
    news_articles = get_orcl_news_for_catalyst()
    
    if news_articles:
        print(f"\n📰 Analyzing {len(news_articles)} news items for catalysts...")
        catalyst_result = catalyst_detector.detect_catalysts(news_articles)
        
        # Print catalyst details
        explanation = catalyst_detector.get_catalyst_explanation(catalyst_result)
        print(f"\n{explanation}")
        
        # Apply catalyst boost to score
        catalyst_score = catalyst_result['score']
        original_score = standard_prediction.get('score', 0.0)
        
        # Catalyst can add/subtract up to 15% to the score
        # Cap the boost to prevent over-influence
        catalyst_boost = min(max(catalyst_score, -0.15), 0.15)
        
        enhanced_score = original_score + catalyst_boost
        
        # Recalculate confidence based on enhanced score
        if abs(enhanced_score) < 0.01:
            enhanced_confidence = 50.0
        elif abs(enhanced_score) < 0.04:
            enhanced_confidence = 50.0
        elif abs(enhanced_score) < 0.10:
            enhanced_confidence = 55 + (abs(enhanced_score) - 0.04) * 208.33
        else:
            enhanced_confidence = 67.5 + (abs(enhanced_score) - 0.10) * 115
        
        # Cap confidence
        enhanced_confidence = min(enhanced_confidence, 95.0)
        
        # Update prediction
        original_confidence = standard_prediction.get('confidence', 0.0)
        original_direction = standard_prediction.get('direction', 'NEUTRAL')
        
        # Determine new direction
        if enhanced_score > 0.04:
            enhanced_direction = 'UP'
        elif enhanced_score < -0.04:
            enhanced_direction = 'DOWN'
        else:
            enhanced_direction = 'NEUTRAL'
        
        # Show enhancement details
        print("\n" + "="*80)
        print("📊 CATALYST IMPACT ON PREDICTION")
        print("="*80)
        print(f"\n📊 ORIGINAL PREDICTION:")
        print(f"   Direction: {original_direction}")
        print(f"   Confidence: {original_confidence:.1f}%")
        print(f"   Score: {original_score:+.3f}")
        
        print(f"\n🔍 CATALYST ADJUSTMENT:")
        print(f"   Catalyst Score: {catalyst_score:+.3f}")
        print(f"   Applied Boost: {catalyst_boost:+.3f}")
        
        print(f"\n✨ ENHANCED PREDICTION:")
        print(f"   Direction: {enhanced_direction}")
        print(f"   Confidence: {enhanced_confidence:.1f}%")
        print(f"   Score: {enhanced_score:+.3f}")
        
        if catalyst_score > 0.05:
            print(f"\n   📈 CATALYST BOOST: Strong positive catalysts detected!")
            print(f"   💡 Oracle business drivers are bullish")
        elif catalyst_score < -0.05:
            print(f"\n   📉 CATALYST DRAG: Negative catalysts detected!")
            print(f"   ⚠️ Oracle facing headwinds")
        elif abs(catalyst_boost) > 0.02:
            print(f"\n   ➡️ CATALYST NUDGE: Minor catalyst impact")
        else:
            print(f"\n   ➡️ NO CATALYST IMPACT: Standard prediction stands")
        
        # Create enhanced prediction dict
        enhanced_prediction = standard_prediction.copy()
        enhanced_prediction['original_score'] = original_score
        enhanced_prediction['original_confidence'] = original_confidence
        enhanced_prediction['original_direction'] = original_direction
        enhanced_prediction['catalyst_score'] = catalyst_score
        enhanced_prediction['catalyst_boost'] = catalyst_boost
        enhanced_prediction['catalyst_details'] = catalyst_result
        enhanced_prediction['score'] = enhanced_score
        enhanced_prediction['confidence'] = enhanced_confidence
        enhanced_prediction['direction'] = enhanced_direction
        enhanced_prediction['enhanced'] = True
        
        return enhanced_prediction
    else:
        print("\n⚠️ No news articles found - using standard prediction")
        standard_prediction['enhanced'] = False
        return standard_prediction

if __name__ == "__main__":
    # Test the enhanced predictor
    result = generate_orcl_prediction()
    
    print("\n" + "="*80)
    print("🎯 FINAL RECOMMENDATION")
    print("="*80)
    
    if result.get('enhanced'):
        print(f"\n✅ Enhanced Prediction Active")
        print(f"   Catalyst Impact: {result.get('catalyst_boost', 0):+.3f}")
        
    print(f"\n📊 Direction: {result.get('direction')}")
    print(f"🎲 Confidence: {result.get('confidence', 0):.1f}%")
    print(f"📈 Score: {result.get('score', 0):+.3f}")
    
    if result.get('confidence', 0) >= 60:
        print(f"\n✅ TRADE RECOMMENDATION: Execute trade")
        print(f"   Position Size: Based on {result.get('confidence'):.0f}% confidence")
    else:
        print(f"\n❌ SKIP RECOMMENDATION: Confidence too low")
        print(f"   Wait for better setup")
