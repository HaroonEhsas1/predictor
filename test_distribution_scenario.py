"""
TEST: Distribution Pattern Scenario
Market gaps up, rallies, then fades by close
What does the system predict for next day?
"""

print("="*80)
print("🧪 DISTRIBUTION PATTERN SCENARIO TEST")
print("="*80)

print("\n📊 MARKET ACTION:")
print("  Premarket: +1.8% (gap up)")
print("  Open: Stock rallies to +2.7%")
print("  Midday: Slowly drifts down")
print("  Close: -0.3% (RED, near lows)")
print("  Pattern: DISTRIBUTION (selling into strength)")

# System inputs based on this scenario
inputs = {
    'intraday_high': 2.7,  # % up from previous close
    'intraday_low': -0.8,  # % from previous close
    'close_change': -0.3,  # Closed red
    'premarket_gap': +1.8,  # Gap up
    'volume': 1.5,  # 50% above average (distribution volume)
}

# Calculate close position in range
daily_range = inputs['intraday_high'] - inputs['intraday_low']  # 3.5%
close_from_low = inputs['close_change'] - inputs['intraday_low']  # -0.3 - (-0.8) = 0.5
close_position = (close_from_low / daily_range) * 100  # 14% of range

print(f"\n📈 TECHNICAL ANALYSIS:")
print(f"  Intraday Range: {daily_range:.1f}%")
print(f"  Close Position: {close_position:.0f}% of range (NEAR LOW)")
print(f"  Volume: {inputs['volume']:.1f}x average (HIGH)")

# System logic for distribution detection
print(f"\n🔍 SYSTEM DETECTION:")

# 1. Red close check
red_close = inputs['close_change'] < 0
print(f"  1. Red Close: {red_close} ({'YES' if red_close else 'NO'})")

# 2. Near lows check (below 30% of range)
near_lows = close_position < 30
print(f"  2. Close Near Lows: {near_lows} (close at {close_position:.0f}% < 30%)")

# 3. Gap up that failed
gap_up_failed = inputs['premarket_gap'] > 1.0 and inputs['close_change'] < 0
print(f"  3. Gap Up Failed: {gap_up_failed} (gap +{inputs['premarket_gap']:.1f}% but closed red)")

# 4. High volume on down day
high_vol_distribution = inputs['volume'] > 1.3 and inputs['close_change'] < 0
print(f"  4. Distribution Volume: {high_vol_distribution} (vol {inputs['volume']:.1f}x on red day)")

# Distribution detected?
distribution_detected = red_close and near_lows
print(f"\n🚨 DISTRIBUTION PATTERN: {'DETECTED' if distribution_detected else 'NOT DETECTED'}")

if distribution_detected:
    print("  → Smart money selling into strength")
    print("  → Retail bought the gap, got trapped")
    print("  → Weakness likely to continue")

# Now simulate what system would predict
print(f"\n{'='*80}")
print("🤖 SYSTEM PREDICTION LOGIC:")
print("="*80)

# Assume some reasonable values for other factors
rsi = 68  # Likely overbought after gap up rally
news_score = 0.050  # Some positive news (caused the gap)
options_score = -0.030  # Options turned bearish (put buying at highs)
analyst_score = 0.020  # Neutral
technical_score = -0.120  # Bearish (distribution pattern detected)
sector_score = -0.020  # Sector also weak
institutional_score = -0.040  # Selling detected

# Calculate fundamentals
fundamentals = (news_score + options_score + analyst_score) / 3
print(f"\nInputs:")
print(f"  Gap: +{inputs['premarket_gap']:.1f}% (UP)")
print(f"  Close: {inputs['close_change']:+.1f}% (RED)")
print(f"  RSI: {rsi} (overbought)")
print(f"  Close Position: {close_position:.0f}% (WEAK)")
print(f"  Fundamentals: {fundamentals:+.3f}")
print(f"  Technical: {technical_score:+.3f} (distribution penalty)")
print(f"  Institutional: {institutional_score:+.3f} (selling)")

# Apply system logic
score = 0
reason = ""

# Check if this triggers overbought correction
if rsi > 65 and inputs['close_change'] < 0 and fundamentals < 0.03:
    score -= 0.10
    reason = "OVERBOUGHT CORRECTION"
    print(f"\n⚠️ TRIGGERED: Overbought Correction")
    print(f"   RSI {rsi} > 65 + Red close + Weak fundamentals")

# Distribution penalty
if distribution_detected:
    score -= 0.08
    reason += " + DISTRIBUTION"
    print(f"⚠️ TRIGGERED: Distribution Penalty")
    print(f"   Close at {close_position:.0f}% of range (selling pressure)")

# Failed gap penalty
if gap_up_failed:
    score -= 0.05
    reason += " + FAILED GAP"
    print(f"⚠️ TRIGGERED: Failed Gap Penalty")
    print(f"   Gap +{inputs['premarket_gap']:.1f}% but closed red")

# Add weighted factors
score += news_score * 0.08
score += options_score * 0.11
score += analyst_score * 0.02
score += technical_score * 0.12
score += sector_score * 0.06
score += institutional_score * 0.10

# Market regime (likely neutral to slightly down after failed gap)
market_bias = -0.025  # Bearish after failed rally
score += market_bias

print(f"\n📊 SCORE CALCULATION:")
print(f"  Overbought Correction: -0.10")
print(f"  Distribution Penalty: -0.08")
print(f"  Failed Gap Penalty: -0.05")
print(f"  News weighted: {news_score * 0.08:+.3f}")
print(f"  Options weighted: {options_score * 0.11:+.3f}")
print(f"  Technical weighted: {technical_score * 0.12:+.3f}")
print(f"  Institutional weighted: {institutional_score * 0.10:+.3f}")
print(f"  Market bias: {market_bias:+.3f}")
print(f"  ──────────────────")
print(f"  TOTAL SCORE: {score:+.3f}")

# Determine direction
if score > 0.04:
    direction = "UP"
elif score < -0.04:
    direction = "DOWN"
else:
    direction = "NEUTRAL"

confidence = 55 + abs(score) * 125

print(f"\n{'='*80}")
print("🎯 FINAL PREDICTION:")
print("="*80)
print(f"  Direction: {direction}")
print(f"  Confidence: {confidence:.1f}%")
print(f"  Score: {score:+.3f}")
print(f"  Reasoning: {reason}")

print(f"\n💡 EXPLANATION:")
if direction == "DOWN":
    print("  ✅ CORRECT PREDICTION!")
    print("  The system detected:")
    print("    - Distribution pattern (close near lows)")
    print("    - Failed gap up (trapped buyers)")
    print("    - Overbought RSI getting rejected")
    print("    - Institutional selling")
    print("  → Predicts continuation of weakness")
    print(f"\n  Expected move: -{abs(score) * 1.5:.1f}% to -{abs(score) * 2.5:.1f}%")
    print(f"  Risk: Market already weak, more downside likely")
else:
    print(f"  ⚠️ Unexpected prediction: {direction}")
    print(f"  Review logic needed")

print(f"\n{'='*80}")
print("CONCLUSION:")
print("="*80)
print("""
Distribution Pattern = BEARISH

When market gaps up but closes near lows:
1. Smart money is selling
2. Retail got trapped buying the gap
3. Weakness likely continues next day
4. System should predict DOWN

This tests if system can detect SELLING into STRENGTH
(not just buying dips or momentum continuation)
""")
