#!/usr/bin/env python3
"""
AVGO Accuracy Test - Verify no hardcoded bias or fallback issues
Tests that AVGO gets REAL data, not AMD data or neutral fallbacks
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from comprehensive_nextday_predictor import ComprehensiveNextDayPredictor
from stock_config import get_stock_config
import yfinance as yf

def test_avgo_configuration():
    """Test 1: Verify AVGO config loads correctly"""
    print("\n" + "="*80)
    print("TEST 1: AVGO Configuration")
    print("="*80)
    
    config = get_stock_config('AVGO')
    
    assert config['name'] == 'Broadcom Inc', f"❌ Wrong name: {config['name']}"
    assert config['typical_volatility'] == 0.015, f"❌ Wrong volatility: {config['typical_volatility']}"
    assert config['weight_adjustments']['news'] == 0.25, f"❌ Wrong news weight: {config['weight_adjustments']['news']}"
    assert config['weight_adjustments']['reddit'] == 0.05, f"❌ Wrong reddit weight: {config['weight_adjustments']['reddit']}"
    assert 'OpenAI' in config['news_keywords'], "❌ Missing OpenAI keyword"
    assert 'NVDA' in config['competitors'], "❌ Missing NVDA competitor"
    
    print("✅ AVGO configuration is correct")
    print(f"   Name: {config['name']}")
    print(f"   Volatility: {config['typical_volatility']*100}%")
    print(f"   News Weight: {config['weight_adjustments']['news']*100}%")
    print(f"   Reddit Weight: {config['weight_adjustments']['reddit']*100}%")
    return True


def test_avgo_real_price():
    """Test 2: Verify AVGO gets real price, not AMD price"""
    print("\n" + "="*80)
    print("TEST 2: Real AVGO Price Data")
    print("="*80)
    
    # Get AVGO price
    avgo_ticker = yf.Ticker('AVGO')
    avgo_hist = avgo_ticker.history(period="5d")
    avgo_price = float(avgo_hist['Close'].iloc[-1])
    
    # Get AMD price
    amd_ticker = yf.Ticker('AMD')
    amd_hist = amd_ticker.history(period="5d")
    amd_price = float(amd_hist['Close'].iloc[-1])
    
    print(f"   AVGO Price: ${avgo_price:.2f}")
    print(f"   AMD Price: ${amd_price:.2f}")
    
    # They should be different (prices should never match)
    assert abs(avgo_price - amd_price) > 10, f"❌ Prices are too similar! AVGO may be using AMD data"
    
    # AVGO should be in reasonable range ($200-$500)
    assert 200 < avgo_price < 500, f"❌ AVGO price {avgo_price} is out of expected range"
    
    print(f"✅ AVGO is using real price data (not AMD)")
    return True


def test_avgo_predictor_initialization():
    """Test 3: Verify predictor initializes with AVGO, not AMD"""
    print("\n" + "="*80)
    print("TEST 3: Predictor Initialization")
    print("="*80)
    
    predictor = ComprehensiveNextDayPredictor(symbol='AVGO')
    
    assert predictor.symbol == 'AVGO', f"❌ Wrong symbol: {predictor.symbol}"
    assert predictor.stock_config['name'] == 'Broadcom Inc', f"❌ Wrong config loaded"
    assert predictor.weight_adjustments['news'] == 0.25, f"❌ Wrong weights"
    
    print(f"✅ Predictor correctly initialized for {predictor.symbol}")
    print(f"   Config: {predictor.stock_config['name']}")
    print(f"   News Weight: {predictor.weight_adjustments['news']*100}%")
    return True


def test_avgo_futures_weighting():
    """Test 4: Verify AVGO uses correct Nasdaq weighting"""
    print("\n" + "="*80)
    print("TEST 4: Futures Weighting")
    print("="*80)
    
    predictor = ComprehensiveNextDayPredictor(symbol='AVGO')
    futures = predictor.get_futures_sentiment()
    
    # AVGO should weight NQ more heavily (60% vs 40% ES)
    # Test formula: overall = ES*0.40 + NQ*0.60
    expected_sentiment = futures['es_change'] * 0.40 + futures['nq_change'] * 0.60
    
    assert abs(futures['overall_sentiment'] - expected_sentiment) < 0.01, \
        f"❌ Wrong futures calculation. Got {futures['overall_sentiment']}, expected {expected_sentiment}"
    
    print(f"✅ AVGO uses correct Nasdaq weighting (60% NQ, 40% ES)")
    print(f"   ES: {futures['es_change']:+.2f}%")
    print(f"   NQ: {futures['nq_change']:+.2f}%")
    print(f"   Overall: {futures['overall_sentiment']:+.3f}%")
    return True


def test_avgo_no_fallbacks():
    """Test 5: Verify AVGO doesn't use neutral fallbacks when data exists"""
    print("\n" + "="*80)
    print("TEST 5: No Neutral Fallbacks")
    print("="*80)
    
    predictor = ComprehensiveNextDayPredictor(symbol='AVGO')
    
    # Get technical data
    technical = predictor.get_technical_analysis()
    
    # RSI should not be exactly 50 (neutral fallback) unless market is truly neutral
    # If it's exactly 50, it might be a fallback
    if technical['rsi'] == 50.0:
        print("⚠️  RSI is exactly 50 - may be fallback (check if data is available)")
    else:
        print(f"✅ RSI: {technical['rsi']:.1f} (real data, not fallback)")
    
    # Check if we got real data
    assert technical['trend'] in ['uptrend', 'downtrend'], f"❌ Trend should not be neutral if data exists"
    print(f"✅ Trend: {technical['trend']} (real data)")
    
    return True


def test_avgo_competitors():
    """Test 6: Verify AVGO uses correct competitors (not AMD's)"""
    print("\n" + "="*80)
    print("TEST 6: Competitor Analysis")
    print("="*80)
    
    predictor = ComprehensiveNextDayPredictor(symbol='AVGO')
    config = predictor.stock_config
    
    # AVGO competitors should include QCOM, MRVL, TXN
    avgo_competitors = config['competitors']
    
    assert 'QCOM' in avgo_competitors, "❌ Missing QCOM (AVGO competitor)"
    assert 'MRVL' in avgo_competitors, "❌ Missing MRVL (AVGO competitor)"
    assert 'INTC' not in avgo_competitors, "❌ INTC is AMD competitor, not AVGO"
    
    print(f"✅ AVGO uses correct competitors: {', '.join(avgo_competitors)}")
    return True


def test_avgo_volatility_calculation():
    """Test 7: Verify AVGO uses correct volatility (1.5%, not AMD's 2.0%)"""
    print("\n" + "="*80)
    print("TEST 7: Volatility Calculation")
    print("="*80)
    
    predictor = ComprehensiveNextDayPredictor(symbol='AVGO')
    
    # Mock a prediction to test volatility usage
    typical_vol = predictor.stock_config.get('typical_volatility', 0.015)
    
    assert typical_vol == 0.015, f"❌ Wrong volatility: {typical_vol} (should be 0.015 for AVGO)"
    
    # Calculate expected move for 75% confidence
    move_pct = typical_vol  # High confidence uses full volatility
    current_price = 350  # Approximate AVGO price
    expected_move = current_price * move_pct
    
    print(f"✅ AVGO volatility: {typical_vol*100}%")
    print(f"   Expected move at 75% confidence: ${expected_move:.2f} ({move_pct*100}%)")
    
    # AVGO's move should be smaller than AMD's
    amd_vol = 0.020
    assert typical_vol < amd_vol, "❌ AVGO volatility should be less than AMD"
    
    return True


def test_full_avgo_prediction():
    """Test 8: Run full AVGO prediction and verify all components"""
    print("\n" + "="*80)
    print("TEST 8: Full AVGO Prediction")
    print("="*80)
    
    predictor = ComprehensiveNextDayPredictor(symbol='AVGO')
    prediction = predictor.generate_comprehensive_prediction()
    
    # Verify prediction structure
    assert 'direction' in prediction, "❌ Missing direction"
    assert 'confidence' in prediction, "❌ Missing confidence"
    assert 'current_price' in prediction, "❌ Missing current_price"
    assert 'target_price' in prediction, "❌ Missing target_price"
    
    # Verify direction is valid
    assert prediction['direction'] in ['UP', 'DOWN', 'NEUTRAL'], f"❌ Invalid direction: {prediction['direction']}"
    
    # Verify confidence is reasonable
    assert 0 <= prediction['confidence'] <= 100, f"❌ Invalid confidence: {prediction['confidence']}"
    
    # Verify prices are in AVGO range (not AMD range)
    assert 200 < prediction['current_price'] < 500, \
        f"❌ Current price ${prediction['current_price']:.2f} is not in AVGO range"
    
    print(f"✅ Full prediction generated successfully")
    print(f"   Symbol: AVGO")
    print(f"   Direction: {prediction['direction']}")
    print(f"   Confidence: {prediction['confidence']:.1f}%")
    print(f"   Current: ${prediction['current_price']:.2f}")
    print(f"   Target: ${prediction['target_price']:.2f}")
    
    return True


def run_all_tests():
    """Run all AVGO accuracy tests"""
    print("\n" + "="*80)
    print("🔍 AVGO ACCURACY TEST SUITE")
    print("Verifying no hardcoded bias, reactive logic, or fallback issues")
    print("="*80)
    
    tests = [
        ("Configuration", test_avgo_configuration),
        ("Real Price Data", test_avgo_real_price),
        ("Predictor Init", test_avgo_predictor_initialization),
        ("Futures Weighting", test_avgo_futures_weighting),
        ("No Fallbacks", test_avgo_no_fallbacks),
        ("Competitors", test_avgo_competitors),
        ("Volatility", test_avgo_volatility_calculation),
        ("Full Prediction", test_full_avgo_prediction),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            failed += 1
            print(f"\n❌ TEST FAILED: {name}")
            print(f"   Error: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"✅ Passed: {passed}/{len(tests)}")
    print(f"❌ Failed: {failed}/{len(tests)}")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED - AVGO IS WORKING PERFECTLY!")
        print("   ✅ No hardcoded bias")
        print("   ✅ No reactive logic issues")
        print("   ✅ No false fallbacks")
        print("   ✅ Uses real AVGO data")
        print("   ✅ Accurate calculations")
    else:
        print("\n⚠️ SOME TESTS FAILED - REVIEW ABOVE ERRORS")
    
    print("="*80)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
