#!/usr/bin/env python3
"""
Deep Verification: Check if Forex Data is Live or Cached/Hardcoded
Analyzes each component to ensure real-time data
"""

import yfinance as yf
from datetime import datetime, timedelta
from forex_data_fetcher import ForexDataFetcher
from forex_daily_predictor import ForexDailyPredictor
import time

def verify_data_freshness():
    """Verify that data sources are live and not cached"""
    
    print("=" * 80)
    print("🔍 FOREX DATA VERIFICATION - DEEP ANALYSIS")
    print("=" * 80)
    print()
    
    fetcher = ForexDataFetcher()
    
    # Test 1: Check EUR/USD price freshness
    print("\n📊 TEST 1: Price Data Freshness")
    print("-" * 80)
    
    ticker = yf.Ticker('EURUSD=X')
    hist = ticker.history(period='2d')
    
    if not hist.empty:
        latest_timestamp = hist.index[-1]
        now = datetime.now()
        
        print(f"✅ Latest data timestamp: {latest_timestamp}")
        print(f"⏰ Current time: {now}")
        print(f"⏱️ Data age: {now - latest_timestamp.replace(tzinfo=None)}")
        
        # Check if data is stale (more than 24 hours old)
        if (now - latest_timestamp.replace(tzinfo=None)).total_seconds() > 86400:
            print(f"❌ WARNING: Data is more than 24 hours old!")
        else:
            print(f"✅ Data is fresh (within 24 hours)")
    else:
        print(f"❌ ERROR: No price data available")
    
    # Test 2: Check if prices change between calls
    print("\n📊 TEST 2: Data Changes Between Calls")
    print("-" * 80)
    
    price1 = float(hist['Close'].iloc[-1])
    print(f"First call: {price1:.4f}")
    
    print("Waiting 2 seconds...")
    time.sleep(2)
    
    hist2 = ticker.history(period='1d')
    price2 = float(hist2['Close'].iloc[-1])
    print(f"Second call: {price2:.4f}")
    
    if price1 == price2:
        print(f"⚠️ WARNING: Price unchanged (might be cached or market closed)")
    else:
        print(f"✅ Price changed: {price2 - price1:+.4f} ({((price2-price1)/price1)*100:+.2f}%)")
    
    # Test 3: Check interest rates
    print("\n📊 TEST 3: Interest Rates Source")
    print("-" * 80)
    
    rates = fetcher.fetch_interest_rates()
    print(f"\nFetched rates:")
    for currency, rate in rates.items():
        print(f"   {currency}: {rate:.2f}%")
    
    # Test 4: Check DXY (Dollar Index)
    print("\n📊 TEST 4: Dollar Index (DXY) Freshness")
    print("-" * 80)
    
    try:
        dxy = yf.Ticker('DX-Y.NYB')
        dxy_hist = dxy.history(period='5d')
        
        if not dxy_hist.empty:
            current_dxy = float(dxy_hist['Close'].iloc[-1])
            week_ago_dxy = float(dxy_hist['Close'].iloc[0])
            change = ((current_dxy - week_ago_dxy) / week_ago_dxy) * 100
            
            print(f"✅ DXY current: {current_dxy:.2f}")
            print(f"📈 5-day change: {change:+.2f}%")
            print(f"⏰ Last update: {dxy_hist.index[-1]}")
        else:
            print(f"❌ ERROR: No DXY data available")
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    # Test 5: Check VIX
    print("\n📊 TEST 5: VIX (Risk Sentiment) Freshness")
    print("-" * 80)
    
    try:
        vix = yf.Ticker('^VIX')
        vix_hist = vix.history(period='5d')
        
        if not vix_hist.empty:
            current_vix = float(vix_hist['Close'].iloc[-1])
            prev_vix = float(vix_hist['Close'].iloc[-2]) if len(vix_hist) >= 2 else current_vix
            change = current_vix - prev_vix
            
            print(f"✅ VIX current: {current_vix:.2f}")
            print(f"📈 Daily change: {change:+.2f}")
            print(f"⏰ Last update: {vix_hist.index[-1]}")
        else:
            print(f"❌ ERROR: No VIX data available")
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    # Test 6: Check Gold
    print("\n📊 TEST 6: Gold Price Freshness")
    print("-" * 80)
    
    try:
        gold_data = fetcher.fetch_gold_price()
        if gold_data:
            print(f"✅ Gold price: ${gold_data['price']:.2f}")
            print(f"📈 Change: {gold_data['change_pct']:+.2f}%")
            print(f"📊 RSI: {gold_data['rsi']:.1f}")
            print(f"🔄 Trend: {gold_data['trend']}")
        else:
            print(f"❌ ERROR: Gold data not available")
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    # Test 7: Run actual prediction and analyze score components
    print("\n📊 TEST 7: Prediction Score Analysis")
    print("-" * 80)
    
    predictor = ForexDailyPredictor('EUR/USD')
    
    # Temporarily capture the scores (we need to modify predictor to return them)
    print("Running prediction to analyze score components...")
    prediction = predictor.generate_prediction()
    
    if prediction:
        print(f"\n✅ Prediction generated:")
        print(f"   Direction: {prediction['direction']}")
        print(f"   Confidence: {prediction['confidence']:.1f}%")
        print(f"   Score: {prediction['score']:+.3f}")
        
        # Analyze confidence calculation
        score = abs(prediction['score'])
        confidence_calc = 65 + (score * 200)
        confidence_capped = min(confidence_calc, 90)
        
        print(f"\n🔍 Confidence Calculation Breakdown:")
        print(f"   Base formula: 65 + (score × 200)")
        print(f"   Score magnitude: {score:.3f}")
        print(f"   Calculated: 65 + ({score:.3f} × 200) = {confidence_calc:.1f}%")
        print(f"   After 90% cap: {confidence_capped:.1f}%")
        
        if confidence_calc > 90:
            print(f"\n⚠️ ISSUE FOUND: Score is {confidence_calc:.1f}%, hitting 90% cap!")
            print(f"   This means confidence will ALWAYS be 90% with strong signals")
            print(f"   Recommendation: Increase cap to 95% or adjust formula")
        else:
            print(f"\n✅ Confidence is below cap ({confidence_calc:.1f}% < 90%)")
    
    print("\n" + "=" * 80)
    print("🎯 VERIFICATION COMPLETE")
    print("=" * 80)

def check_score_variability():
    """Check if scores vary over different times/conditions"""
    
    print("\n" + "=" * 80)
    print("📊 SCORE VARIABILITY TEST")
    print("=" * 80)
    
    print("\nRunning 3 predictions 10 seconds apart to check variability...")
    
    scores = []
    confidences = []
    
    for i in range(3):
        if i > 0:
            print(f"\nWaiting 10 seconds...")
            time.sleep(10)
        
        print(f"\n🔄 Run {i+1}:")
        predictor = ForexDailyPredictor('EUR/USD')
        prediction = predictor.generate_prediction()
        
        if prediction:
            scores.append(prediction['score'])
            confidences.append(prediction['confidence'])
            print(f"   Score: {prediction['score']:+.3f}, Confidence: {prediction['confidence']:.1f}%")
    
    print("\n" + "=" * 80)
    print("📊 VARIABILITY RESULTS")
    print("=" * 80)
    
    if len(scores) == 3:
        score_variance = max(scores) - min(scores)
        conf_variance = max(confidences) - min(confidences)
        
        print(f"\nScore range: {min(scores):+.3f} to {max(scores):+.3f} (variance: {score_variance:.3f})")
        print(f"Confidence range: {min(confidences):.1f}% to {max(confidences):.1f}% (variance: {conf_variance:.1f}%)")
        
        if score_variance == 0:
            print(f"\n❌ CRITICAL: Scores are identical! Data might be cached/hardcoded")
        elif score_variance < 0.001:
            print(f"\n⚠️ WARNING: Very low score variability. Check data sources")
        else:
            print(f"\n✅ Scores vary (good - data is live)")
        
        if conf_variance == 0:
            print(f"❌ CRITICAL: Confidence is identical! Might be hardcoded")
        elif all(c == 90.0 for c in confidences):
            print(f"⚠️ WARNING: All confidences are 90% (hitting cap)")
        else:
            print(f"✅ Confidence varies (good)")

if __name__ == "__main__":
    verify_data_freshness()
    check_score_variability()
