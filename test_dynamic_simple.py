#!/usr/bin/env python3
"""Test Dynamic Target - Windows Compatible"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from comprehensive_nextday_predictor import ComprehensiveNextDayPredictor

print("\n" + "="*80)
print("DYNAMIC TARGET CALCULATION TEST")
print("="*80)

for symbol in ['AMD', 'AVGO']:
    print(f"\n{symbol}:")
    print("-" * 40)
    
    predictor = ComprehensiveNextDayPredictor(symbol)
    pred = predictor.generate_comprehensive_prediction()
    
    current = pred['current_price']
    target = pred['target_price']
    move = target - current
    move_pct = (move / current) * 100
    
    print(f"\nRESULT:")
    print(f"  Direction: {pred['direction']}")
    print(f"  Confidence: {pred['confidence']:.1f}%")
    print(f"  Current: ${current:.2f}")
    print(f"  Target: ${target:.2f}")
    print(f"  Gap: ${move:+.2f} ({move_pct:+.2f}%)")
    print(f"\n  The target gap of ${abs(move):.2f} was calculated dynamically")
    print(f"  based on market conditions (see Dynamic Target Calculation above)")

print("\n" + "="*80)
print("COMPLETE!")
print("="*80)
