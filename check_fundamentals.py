"""
Check fundamental strength for AMD, AVGO, ORCL
To understand why bounce setup triggers or not
"""

stocks = {
    'ORCL': {
        'news': 0.140,
        'options': 0.110,
        'analyst': 0.015,
        'gap': -4.68,
        'rsi': 34.4
    },
    'AMD': {
        'news': 0.080,
        'options': 0.110,
        'analyst': 0.015,
        'gap': -2.13,
        'rsi': 71.3
    },
    'AVGO': {
        'news': 0.110,
        'options': 0.110,
        'analyst': 0.011,
        'gap': -2.49,
        'rsi': 71.0
    }
}

print("="*80)
print("FUNDAMENTAL STRENGTH ANALYSIS")
print("="*80)

for stock, data in stocks.items():
    fundamental_strength = data['news'] + data['options'] + data['analyst']
    fundamental_count = 3
    fundamental_avg = fundamental_strength / fundamental_count
    
    print(f"\n{stock}:")
    print(f"  News:     {data['news']:+.3f}")
    print(f"  Options:  {data['options']:+.3f}")
    print(f"  Analyst:  {data['analyst']:+.3f}")
    print(f"  ───────────────────")
    print(f"  Total:    {fundamental_strength:+.3f}")
    print(f"  Average:  {fundamental_avg:.3f}")
    print(f"  Gap:      {data['gap']:.2f}%")
    print(f"  RSI:      {data['rsi']:.1f}")
    
    # Check BOUNCE_SETUP conditions
    print(f"\n  BOUNCE_SETUP Scenarios:")
    
    # Scenario 1: Oversold bounce
    scenario1 = data['gap'] < -3.0 and data['rsi'] < 40 and fundamental_avg > 0.05
    print(f"    Scenario 1 (Oversold): {scenario1}")
    if scenario1:
        print(f"      ✅ Gap {data['gap']:.2f}% < -3.0")
        print(f"      ✅ RSI {data['rsi']:.1f} < 40")
        print(f"      ✅ Fundamentals {fundamental_avg:.3f} > 0.05")
    else:
        if not data['gap'] < -3.0:
            print(f"      ❌ Gap {data['gap']:.2f}% >= -3.0")
        if not data['rsi'] < 40:
            print(f"      ❌ RSI {data['rsi']:.1f} >= 40 (OVERBOUGHT)")
        if not fundamental_avg > 0.05:
            print(f"      ❌ Fundamentals {fundamental_avg:.3f} <= 0.05")
    
    # Scenario 2: Strong fundamentals (regardless of RSI)
    scenario2 = data['gap'] < -2.0 and fundamental_avg > 0.10
    print(f"    Scenario 2 (Strong Fund): {scenario2}")
    if scenario2:
        print(f"      ✅ Gap {data['gap']:.2f}% < -2.0")
        print(f"      ✅ Fundamentals {fundamental_avg:.3f} > 0.10")
    else:
        if not data['gap'] < -2.0:
            print(f"      ❌ Gap {data['gap']:.2f}% >= -2.0")
        if not fundamental_avg > 0.10:
            print(f"      ❌ Fundamentals {fundamental_avg:.3f} <= 0.10")
    
    triggers = scenario1 or scenario2
    print(f"\n  🎯 TRIGGERS BOUNCE_SETUP: {triggers}")

print("\n" + "="*80)
print("CONCLUSION:")
print("="*80)

print("\nBOUNCE_SETUP Rule:")
print("  Scenario 1: Gap < -3% AND RSI < 40 AND Fundamentals > 0.05")
print("  Scenario 2: Gap < -2% AND Fundamentals > 0.10")

print("\nIf fundamentals < 0.10, need to:")
print("  1. Lower threshold to 0.08, OR")
print("  2. Boost fundamentals calculation, OR")
print("  3. Accept that not all stocks trigger bounce logic")
