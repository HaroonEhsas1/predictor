#!/usr/bin/env python3
"""Test Twitter Integration"""

from comprehensive_nextday_predictor import ComprehensiveNextDayPredictor

print("\n" + "="*80)
print("TESTING TWITTER INTEGRATION - FULL PREDICTION")
print("="*80)

for symbol in ['AMD', 'AVGO']:
    print(f"\n\n{'='*80}")
    print(f"Testing {symbol} with Twitter")
    print(f"{'='*80}")
    
    predictor = ComprehensiveNextDayPredictor(symbol)
    prediction = predictor.generate_comprehensive_prediction()
    
    print(f"\n{'='*80}")
    print(f"{symbol} FINAL RESULT")
    print(f"{'='*80}")
    print(f"Direction: {prediction['direction']}")
    print(f"Confidence: {prediction['confidence']:.1f}%")
    print(f"Total Score: {prediction['total_score']:+.3f}")
    print(f"Target: ${prediction['target_price']:.2f}")
    print(f"{'='*80}")

print("\n\n✅ TWITTER INTEGRATION TEST COMPLETE!")
