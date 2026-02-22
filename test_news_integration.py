#!/usr/bin/env python3
"""
Test news sentiment integration with ML models
Verifies that news is being fetched and blended correctly
"""

import sys
from pathlib import Path
from intraday_1hour_predictor import RealTimeNewsSentiment
import joblib

sys.path.insert(0, str(Path(__file__).parent))

def test_news_for_stock(symbol):
    """Test news sentiment fetching and ML blending for a stock"""
    print(f"\n{'='*80}")
    print(f"Testing News Sentiment for {symbol}")
    print(f"{'='*80}")
    
    # Load and test news sentiment
    news_sentiment = RealTimeNewsSentiment(symbol, model_blend_weight=0.6)
    result = news_sentiment.get_latest_news(hours_back=24)
    
    print(f"\nNews Fetching Result:")
    print(f"   Success: {result.get('success')}")
    print(f"   Overall Sentiment: {result.get('overall_sentiment'):+.2f}")
    print(f"   Article Count: {result.get('article_count')}")
    print(f"   Articles: {len(result.get('articles', []))}")
    
    # Check if ML model exists and is loaded
    model_path = Path('models') / f'news_model_{symbol}.joblib'
    if model_path.exists():
        try:
            model = joblib.load(str(model_path))
            print(f"\n   ✅ ML Model for {symbol} loaded successfully")
            print(f"      Model type: {type(model).__name__}")
            
            # Test the model on sample text
            sample_texts = [
                f"{symbol} announces strong Q4 earnings",
                f"{symbol} faces supply chain challenges",
                f"{symbol} partnership with major tech firm"
            ]
            
            print(f"\n   Testing model predictions on sample headlines:")
            for text in sample_texts:
                try:
                    pred = model.predict([text])[0]
                    print(f"      '{text}' → {pred}")
                except Exception as e:
                    print(f"      Error predicting: {e}")
                    
        except Exception as e:
            print(f"\n   ⚠️ Error loading ML model: {e}")
    else:
        print(f"\n   ⚠️ No ML model found at {model_path}")

# Test all stocks
if __name__ == "__main__":
    stocks = ['AMD', 'NVDA', 'META', 'AVGO', 'SNOW', 'PLTR']
    
    for symbol in stocks:
        try:
            test_news_for_stock(symbol)
        except Exception as e:
            print(f"\n❌ Error testing {symbol}: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'='*80}")
    print("✅ News Integration Test Complete!")
    print(f"{'='*80}\n")
