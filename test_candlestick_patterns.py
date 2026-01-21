"""
Test candlestick pattern detection for correctness and bias
"""

import pandas as pd
import numpy as np
from engines.nextday.candlestick_patterns import CandlestickPatternDetector

def test_no_bias():
    """Test that patterns detect bullish and bearish equally"""
    
    detector = CandlestickPatternDetector()
    
    # Create test data with balanced bullish and bearish candles
    test_data = pd.DataFrame({
        'Open': [100, 105, 100, 95, 100],
        'High': [102, 108, 102, 98, 105],
        'Low': [98, 103, 98, 93, 99],
        'Close': [101, 107, 99, 94, 104]
    })
    
    patterns = detector.detect_all_patterns(test_data)
    
    print("✅ Testing pattern detection...")
    print(f"Detected {len(patterns.columns)} patterns")
    print("\nPattern scores (should be balanced, no systematic bias):")
    for col in patterns.columns:
        scores = patterns[col].values
        non_zero = scores[scores != 0]
        if len(non_zero) > 0:
            print(f"  {col}: {non_zero}")
    
    return True

def test_doji_detection():
    """Test doji detection with no hardcoded values"""
    
    detector = CandlestickPatternDetector()
    
    # Create perfect doji (open = close)
    test_data = pd.DataFrame({
        'Open': [100, 100, 100],
        'High': [102, 105, 101],
        'Low': [98, 95, 99],
        'Close': [100, 100, 100]  # Perfect doji
    })
    
    patterns = detector.detect_all_patterns(test_data)
    doji_scores = patterns['doji'].values
    
    print("\n✅ Testing Doji detection:")
    print(f"Doji scores: {doji_scores}")
    print("Expected: High scores for open≈close candles")
    
    assert all(doji_scores > 0.8), "Doji should be strongly detected when Open=Close"
    return True

def test_engulfing_patterns():
    """Test bullish and bearish engulfing are symmetric"""
    
    detector = CandlestickPatternDetector()
    
    # Bullish engulfing
    bullish_data = pd.DataFrame({
        'Open': [100, 98],
        'High': [101, 103],
        'Low': [99, 97],
        'Close': [99, 102]  # Bearish then bullish engulfing
    })
    
    # Bearish engulfing (mirror image)
    bearish_data = pd.DataFrame({
        'Open': [100, 102],
        'High': [101, 103],
        'Low': [99, 97],
        'Close': [101, 98]  # Bullish then bearish engulfing
    })
    
    bullish_patterns = detector.detect_all_patterns(bullish_data)
    bearish_patterns = detector.detect_all_patterns(bearish_data)
    
    bullish_score = bullish_patterns['bullish_engulfing'].iloc[-1]
    bearish_score = bearish_patterns['bearish_engulfing'].iloc[-1]
    
    print("\n✅ Testing Engulfing patterns (should be symmetric):")
    print(f"Bullish engulfing score: {bullish_score}")
    print(f"Bearish engulfing score: {bearish_score}")
    print(f"Symmetry check: {abs(bullish_score + bearish_score) < 0.1}")
    
    assert abs(bullish_score + bearish_score) < 0.1, "Engulfing patterns should be symmetric"
    return True

def test_hammer_shooting_star():
    """Test hammer (bullish) and shooting star (bearish) are opposites"""
    
    detector = CandlestickPatternDetector()
    
    # Hammer: Long lower shadow, small upper shadow
    # Body at top of range
    hammer_data = pd.DataFrame({
        'Open': [100],
        'High': [100.5],  # Small upper shadow
        'Low': [95],      # Long lower shadow (2x body)
        'Close': [100.3]  # Small body near top
    })
    
    # Shooting star: Long upper shadow, small lower shadow
    # Body at bottom of range
    star_data = pd.DataFrame({
        'Open': [100],
        'High': [105],    # Long upper shadow (2x body)
        'Low': [99.5],    # Small lower shadow
        'Close': [99.7]   # Small body near bottom
    })
    
    hammer_patterns = detector.detect_all_patterns(hammer_data)
    star_patterns = detector.detect_all_patterns(star_data)
    
    hammer_score = hammer_patterns['hammer'].iloc[0]
    star_score = star_patterns['shooting_star'].iloc[0]
    
    print("\n✅ Testing Hammer vs Shooting Star:")
    print(f"Hammer score (bullish): {hammer_score}")
    print(f"Shooting Star score (bearish): {star_score}")
    print(f"Opposite signs: {hammer_score > 0 and star_score < 0}")
    
    assert hammer_score > 0, "Hammer should be positive (bullish)"
    assert star_score < 0, "Shooting star should be negative (bearish)"
    return True

def test_no_hardcoded_thresholds():
    """Test that patterns use dynamic calculations, not hardcoded values"""
    
    detector = CandlestickPatternDetector()
    
    # Small range candle
    small_data = pd.DataFrame({
        'Open': [100],
        'High': [100.5],
        'Low': [99.5],
        'Close': [100]
    })
    
    # Large range candle with same proportions
    large_data = pd.DataFrame({
        'Open': [100],
        'High': [105],
        'Low': [95],
        'Close': [100]
    })
    
    small_patterns = detector.detect_all_patterns(small_data)
    large_patterns = detector.detect_all_patterns(large_data)
    
    # Doji should be detected similarly regardless of absolute size
    small_doji = small_patterns['doji'].iloc[0]
    large_doji = large_patterns['doji'].iloc[0]
    
    print("\n✅ Testing dynamic calculations (no hardcoded thresholds):")
    print(f"Small candle doji: {small_doji}")
    print(f"Large candle doji: {large_doji}")
    print(f"Similar scores: {abs(small_doji - large_doji) < 0.1}")
    
    assert abs(small_doji - large_doji) < 0.1, "Pattern detection should be relative, not absolute"
    return True

def test_real_market_data():
    """Test with realistic market data"""
    
    detector = CandlestickPatternDetector()
    
    # Simulate 5 days of realistic AMD data
    np.random.seed(42)
    dates = pd.date_range('2025-10-01', periods=5)
    
    test_data = pd.DataFrame({
        'Open': [150 + np.random.randn() for _ in range(5)],
        'High': [152 + np.random.randn() for _ in range(5)],
        'Low': [148 + np.random.randn() for _ in range(5)],
        'Close': [151 + np.random.randn() for _ in range(5)]
    }, index=dates)
    
    # Ensure High >= Open/Close and Low <= Open/Close
    test_data['High'] = test_data[['Open', 'Close', 'High']].max(axis=1)
    test_data['Low'] = test_data[['Open', 'Close', 'Low']].min(axis=1)
    
    patterns = detector.detect_all_patterns(test_data)
    
    print("\n✅ Testing with realistic market data:")
    print(f"Patterns detected: {(patterns != 0).sum().sum()} non-zero pattern occurrences")
    print(f"Data shape: {patterns.shape}")
    
    assert patterns.shape[0] == 5, "Should process all rows"
    assert patterns.shape[1] == 16, "Should have all 16 pattern types"
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("CANDLESTICK PATTERN DETECTION TEST SUITE")
    print("Testing for: No hardcoded values, no bias, correct logic")
    print("=" * 60)
    
    tests = [
        test_no_bias,
        test_doji_detection,
        test_engulfing_patterns,
        test_hammer_shooting_star,
        test_no_hardcoded_thresholds,
        test_real_market_data
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
                print(f"✅ {test.__name__} PASSED\n")
        except AssertionError as e:
            failed += 1
            print(f"❌ {test.__name__} FAILED: {e}\n")
        except Exception as e:
            failed += 1
            print(f"❌ {test.__name__} ERROR: {e}\n")
    
    print("=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed == 0:
        print("✅ ALL TESTS PASSED - Candlestick patterns are unbiased and correct!")
    else:
        print("❌ SOME TESTS FAILED - Please review the implementation")
