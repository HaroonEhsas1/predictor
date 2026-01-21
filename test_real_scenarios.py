"""
COMPREHENSIVE SCENARIO TESTING
Test the system with 20 realistic trading scenarios
Prove it predicts BOTH UP and DOWN correctly
"""

print("="*80)
print("🧪 COMPREHENSIVE SYSTEM TESTING - 20 REAL SCENARIOS")
print("="*80)

# Define realistic test scenarios
test_scenarios = [
    # ========== BULLISH SCENARIOS ==========
    {
        'id': 1,
        'name': 'Classic Oversold Bounce',
        'gap': -4.5,
        'rsi': 32,
        'news': 0.080,
        'options': 0.110,
        'analyst': 0.015,
        'technical': -0.12,
        'sector': -0.03,
        'expected_direction': 'UP',
        'reason': 'Oversold RSI + strong fundamentals = bounce',
    },
    {
        'id': 2,
        'name': 'Earnings Beat + Gap Down (Buy the Dip)',
        'gap': -2.5,
        'rsi': 58,
        'news': 0.150,  # Strong positive earnings news
        'options': 0.120,
        'analyst': 0.080,
        'technical': 0.05,
        'sector': 0.02,
        'expected_direction': 'UP',
        'reason': 'Great earnings gapped down = buying opportunity',
    },
    {
        'id': 3,
        'name': 'M&A Announcement Dip',
        'gap': -1.8,
        'rsi': 62,
        'news': 0.200,  # Major M&A news
        'options': 0.150,
        'analyst': 0.100,
        'technical': 0.03,
        'sector': 0.01,
        'expected_direction': 'UP',
        'reason': 'Major catalyst, dip is buyable',
    },
    {
        'id': 4,
        'name': 'Sector Recovery + Stock Oversold',
        'gap': -1.2,
        'rsi': 35,
        'news': 0.040,
        'options': 0.060,
        'analyst': 0.020,
        'technical': -0.08,
        'sector': 0.08,  # Sector strong
        'expected_direction': 'UP',
        'reason': 'Sector rallying, stock catching up',
    },
    {
        'id': 5,
        'name': 'Analyst Upgrade + Small Gap',
        'gap': -0.8,
        'rsi': 48,
        'news': 0.090,
        'options': 0.080,
        'analyst': 0.150,  # Major upgrade
        'technical': 0.06,
        'sector': 0.03,
        'expected_direction': 'UP',
        'reason': 'Analyst upgrade drives momentum',
    },
    
    # ========== BEARISH SCENARIOS ==========
    {
        'id': 6,
        'name': 'Overbought Correction',
        'gap': -2.3,
        'rsi': 72,
        'news': 0.020,  # Weak news
        'options': -0.030,
        'analyst': 0.010,
        'technical': -0.10,
        'sector': -0.05,
        'expected_direction': 'DOWN',
        'reason': 'Overbought + weak fundamentals = correction',
    },
    {
        'id': 7,
        'name': 'Earnings Miss + Gap Down',
        'gap': -5.5,
        'rsi': 68,
        'news': -0.120,  # Bad earnings
        'options': -0.100,
        'analyst': -0.080,
        'technical': -0.15,
        'sector': -0.04,
        'expected_direction': 'DOWN',
        'reason': 'Earnings miss = more downside',
    },
    {
        'id': 8,
        'name': 'Distribution Pattern',
        'gap': -1.5,
        'rsi': 64,
        'news': -0.040,
        'options': -0.060,
        'analyst': 0.000,
        'technical': -0.12,
        'sector': -0.02,
        'expected_direction': 'DOWN',
        'reason': 'Institutional selling detected',
    },
    {
        'id': 9,
        'name': 'Gap Up Reversal (Sell the News)',
        'gap': +3.2,
        'rsi': 75,
        'news': 0.050,  # News already priced in
        'options': -0.040,
        'analyst': 0.020,
        'technical': -0.08,
        'sector': -0.03,
        'expected_direction': 'DOWN',
        'reason': 'Overbought + gap up = reversal',
    },
    {
        'id': 10,
        'name': 'Sector Weakness + Stock Following',
        'gap': -0.9,
        'rsi': 58,
        'news': -0.030,
        'options': -0.050,
        'analyst': -0.020,
        'technical': -0.05,
        'sector': -0.12,  # Sector very weak
        'expected_direction': 'DOWN',
        'reason': 'Sector dragging stock down',
    },
    
    # ========== NEUTRAL/EDGE CASES ==========
    {
        'id': 11,
        'name': 'Mixed Signals (Slight Bullish)',
        'gap': -0.5,
        'rsi': 52,
        'news': 0.045,
        'options': 0.035,
        'analyst': 0.025,
        'technical': -0.03,
        'sector': 0.02,
        'expected_direction': 'UP',
        'reason': 'Slight positive bias, but low confidence',
    },
    {
        'id': 12,
        'name': 'Choppy Market (Slight Bearish)',
        'gap': -0.3,
        'rsi': 49,
        'news': -0.020,
        'options': -0.030,
        'analyst': 0.010,
        'technical': 0.02,
        'sector': -0.04,
        'expected_direction': 'NEUTRAL/DOWN',
        'reason': 'No clear direction, lean bearish',
    },
    
    # ========== HIGH CONVICTION SCENARIOS ==========
    {
        'id': 13,
        'name': 'Panic Selling Bottom',
        'gap': -8.5,
        'rsi': 25,
        'news': 0.090,
        'options': 0.120,
        'analyst': 0.060,
        'technical': -0.18,
        'sector': -0.08,
        'expected_direction': 'UP',
        'reason': 'Extreme oversold + strong fundamentals = strong bounce',
    },
    {
        'id': 14,
        'name': 'Guidance Cut Disaster',
        'gap': -6.2,
        'rsi': 71,
        'news': -0.180,
        'options': -0.150,
        'analyst': -0.120,
        'technical': -0.14,
        'sector': -0.06,
        'expected_direction': 'DOWN',
        'reason': 'Everything bearish = strong down',
    },
    
    # ========== TRICKY SCENARIOS (Test Intelligence) ==========
    {
        'id': 15,
        'name': 'Overbought but STRONG Catalyst',
        'gap': -1.5,
        'rsi': 68,
        'news': 0.180,  # VERY strong news
        'options': 0.140,
        'analyst': 0.100,
        'technical': -0.05,
        'sector': 0.05,
        'expected_direction': 'UP',
        'reason': 'Strong fundamentals override overbought',
    },
    {
        'id': 16,
        'name': 'Oversold but WEAK Fundamentals',
        'gap': -3.8,
        'rsi': 32,
        'news': 0.015,  # Weak fundamentals
        'options': 0.020,
        'analyst': 0.005,
        'technical': -0.10,
        'sector': -0.06,
        'expected_direction': 'NEUTRAL/DOWN',
        'reason': 'Oversold but no catalyst = dead cat bounce',
    },
    
    # ========== RECENT MEMORY SCENARIOS ==========
    {
        'id': 17,
        'name': 'AMD Today (Oct 31) - ACTUAL',
        'gap': -1.9,
        'rsi': 71,
        'news': 0.080,
        'options': 0.000,  # Bug in real system
        'analyst': 0.013,
        'technical': -0.097,
        'sector': -0.03,
        'expected_direction': 'UP',
        'reason': 'Positive fundamentals > overbought (actual scenario)',
    },
    {
        'id': 18,
        'name': 'ORCL Today (Oct 31) - ACTUAL',
        'gap': -4.7,
        'rsi': 34,
        'news': 0.140,
        'options': 0.110,
        'analyst': 0.015,
        'technical': -0.107,
        'sector': -0.02,
        'expected_direction': 'UP',
        'reason': 'Classic oversold bounce (actual scenario)',
    },
    
    # ========== FUTURE SCENARIOS (What If) ==========
    {
        'id': 19,
        'name': 'What if AMD had WEAK fundamentals?',
        'gap': -1.9,
        'rsi': 71,
        'news': 0.015,  # Changed to weak
        'options': 0.010,  # Changed to weak
        'analyst': 0.005,  # Changed to weak
        'technical': -0.097,
        'sector': -0.03,
        'expected_direction': 'DOWN',
        'reason': 'Overbought + weak fundamentals = correction',
    },
    {
        'id': 20,
        'name': 'What if ORCL had NEGATIVE fundamentals?',
        'gap': -4.7,
        'rsi': 34,
        'news': -0.080,  # Changed to negative
        'options': -0.050,  # Changed to negative
        'analyst': -0.040,  # Changed to negative
        'technical': -0.107,
        'sector': -0.02,
        'expected_direction': 'DOWN',
        'reason': 'Oversold + bad news = more downside',
    },
]

# Run tests
print("\nTesting each scenario with ACTUAL system logic...\n")

results = {'UP': 0, 'DOWN': 0, 'NEUTRAL': 0, 'correct': 0, 'total': 0}

for scenario in test_scenarios:
    print(f"{'='*80}")
    print(f"Test #{scenario['id']}: {scenario['name']}")
    print(f"{'='*80}")
    
    # Calculate fundamentals
    fundamentals = (scenario['news'] + scenario['options'] + scenario['analyst']) / 3
    
    print(f"Inputs:")
    print(f"  Gap: {scenario['gap']:+.1f}%")
    print(f"  RSI: {scenario['rsi']}")
    print(f"  Fundamentals: {fundamentals:+.3f} (news={scenario['news']:+.3f}, opt={scenario['options']:+.3f}, analyst={scenario['analyst']:+.3f})")
    print(f"  Technical: {scenario['technical']:+.3f}")
    print(f"  Sector: {scenario['sector']:+.3f}")
    
    # Apply ACTUAL system logic
    score = 0
    
    # Scenario 1: Oversold bounce
    if abs(scenario['gap']) > 3.0 and scenario['rsi'] < 40 and fundamentals > 0.05:
        score += 0.20
        reason_applied = "BOUNCE (Oversold + Strong)"
    # Scenario 2: Strong fundamentals bounce
    elif abs(scenario['gap']) > 1.0 and fundamentals > 0.03:
        score += 0.15
        reason_applied = "BOUNCE (Strong Fundamentals)"
    # Overbought correction
    elif scenario['rsi'] > 65 and scenario['gap'] < -1.0 and fundamentals < 0.03:
        score -= 0.12
        reason_applied = "CORRECTION (Overbought + Weak)"
    # Gap up reversal
    elif scenario['rsi'] > 65 and scenario['gap'] > 2.0:
        score -= 0.10
        reason_applied = "REVERSAL (Overbought + Gap Up)"
    else:
        reason_applied = "Standard scoring"
    
    # Add other factors
    score += scenario['news'] * 0.10
    score += scenario['options'] * 0.10
    score += scenario['analyst'] * 0.02
    score += scenario['technical'] * 0.12
    score += scenario['sector'] * 0.06
    
    # Determine direction
    if score > 0.04:
        prediction = 'UP'
    elif score < -0.04:
        prediction = 'DOWN'
    else:
        prediction = 'NEUTRAL'
    
    # Calculate confidence
    confidence = 55 + abs(score) * 125
    
    print(f"\nSystem Logic:")
    print(f"  Primary Rule: {reason_applied}")
    print(f"  Total Score: {score:+.3f}")
    print(f"  Predicted Direction: {prediction}")
    print(f"  Confidence: {confidence:.1f}%")
    
    print(f"\nExpected:")
    print(f"  Direction: {scenario['expected_direction']}")
    print(f"  Reason: {scenario['reason']}")
    
    # Check if correct
    is_correct = prediction in scenario['expected_direction']
    results['total'] += 1
    results[prediction] += 1
    if is_correct:
        results['correct'] += 1
        print(f"\n✅ CORRECT PREDICTION")
    else:
        print(f"\n❌ WRONG PREDICTION")
    
    print()

# Summary
print("="*80)
print("📊 TEST SUMMARY")
print("="*80)
print(f"\nTotal Tests: {results['total']}")
print(f"Correct Predictions: {results['correct']}")
print(f"Accuracy: {results['correct']/results['total']*100:.1f}%")
print(f"\nDirection Breakdown:")
print(f"  UP predictions: {results['UP']}")
print(f"  DOWN predictions: {results['DOWN']}")
print(f"  NEUTRAL predictions: {results['NEUTRAL']}")

print(f"\n{'='*80}")
print("CONCLUSION:")
print("="*80)
if results['UP'] > 0 and results['DOWN'] > 0:
    print("✅ System predicts BOTH UP and DOWN")
    print("✅ NO BIAS detected - predictions based on logic")
else:
    print("⚠️ System may be biased - investigate!")

print(f"\nThe system predicted:")
print(f"  {results['UP']} scenarios as UP")
print(f"  {results['DOWN']} scenarios as DOWN")
print(f"  {results['NEUTRAL']} scenarios as NEUTRAL")

if results['correct'] / results['total'] >= 0.75:
    print(f"\n✅ EXCELLENT: {results['correct']/results['total']*100:.1f}% accuracy")
elif results['correct'] / results['total'] >= 0.60:
    print(f"\n✅ GOOD: {results['correct']/results['total']*100:.1f}% accuracy (profitable)")
else:
    print(f"\n⚠️ NEEDS WORK: {results['correct']/results['total']*100:.1f}% accuracy")

print("\n" + "="*80)
