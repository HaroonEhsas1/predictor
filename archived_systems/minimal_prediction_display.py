#!/usr/bin/env python3
"""
Minimal Prediction Display Function
"""


def display_minimal_next_day_prediction(direction, confidence, current_price, expected_open, key_factors=None, position_size=None):
    """Display clean, minimal next-day prediction"""
    print("\n" + "="*60)
    print("🎯 NEXT-DAY PREDICTION - AMD")
    print("="*60)
    
    print(f"Direction:      {direction}")
    print(f"Confidence:     {confidence:.0f}%")
    print(f"Current Price:  ${current_price:.2f}")
    print(f"Expected Open:  ${expected_open:.2f}")
    
    # Show price change
    if expected_open != current_price:
        change = expected_open - current_price
        change_pct = (change / current_price) * 100
        print(f"Expected Move:  ${change:+.2f} ({change_pct:+.1f}%)")
    
    # Key factors (only significant ones)
    if key_factors:
        print(f"Key Factors:    {key_factors}")
    
    # Position size
    if position_size:
        print(f"Position Size:  {position_size}")
    
    print("="*60)
