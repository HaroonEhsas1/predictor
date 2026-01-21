#!/usr/bin/env python3
"""Test the earnings proximity fix"""

from comprehensive_nextday_predictor import ComprehensiveNextDayPredictor

print("\n" + "="*80)
print("Testing Earnings Proximity Fix")
print("="*80)

for symbol in ['AMD', 'AVGO']:
    print(f"\n{'='*80}")
    print(f"Testing {symbol}")
    print(f"{'='*80}")
    
    predictor = ComprehensiveNextDayPredictor(symbol)
    
    # Test just the earnings proximity method
    earnings = predictor.get_earnings_proximity()
    
    print(f"\n✅ Earnings Data Retrieved:")
    print(f"   Has Data: {earnings['has_data']}")
    print(f"   Days to Earnings: {earnings['days_to_earnings']}")
    print(f"   Volatility Multiplier: {earnings['volatility_multiplier']}x")
    print(f"   Is Earnings Week: {earnings['is_earnings_week']}")
    print(f"   Sentiment Score: {earnings['sentiment_score']:+.3f}")

print("\n" + "="*80)
print("✅ Earnings Proximity Fix Test Complete!")
print("="*80)
