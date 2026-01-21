"""
Debug why AMD isn't triggering bounce detection
"""

# AMD actual values
gap = -1.82  # From the output
rsi = 71.3
news = 0.080
options = 0.110
analyst = 0.015

fundamentals = (news + options + analyst) / 3
print("="*80)
print("AMD BOUNCE DETECTION DEBUG")
print("="*80)

print(f"\nACTUAL VALUES:")
print(f"  Gap: {gap:.2f}%")
print(f"  RSI: {rsi:.1f}")
print(f"  News: {news:.3f}")
print(f"  Options: {options:.3f}")
print(f"  Analyst: {analyst:.3f}")
print(f"  Fundamentals Avg: {fundamentals:.3f}")

print(f"\n" + "="*80)
print("CHECKING ALL CONDITIONS:")
print("="*80)

# Check overbought override
print(f"\n1. OVERBOUGHT OVERRIDE CHECK:")
print(f"   rsi > 65: {rsi} > 65 = {rsi > 65}")
print(f"   gap < -1.0: {gap} < -1.0 = {gap < -1.0}")
print(f"   fundamentals < 0.06: {fundamentals:.3f} < 0.06 = {fundamentals < 0.06}")
print(f"   ALL TRUE (triggers override): {rsi > 65 and gap < -1.0 and fundamentals < 0.06}")

if rsi > 65 and gap < -1.0 and fundamentals < 0.06:
    print(f"   ❌ OVERBOUGHT OVERRIDE TRIGGERED - Bounce detection WON'T run!")
else:
    print(f"   ✅ Overbought override SKIPPED - Continue to bounce detection")

# Check bounce scenario 1
print(f"\n2. BOUNCE SCENARIO 1 (Oversold):")
print(f"   abs(gap) > 3.0: {abs(gap):.2f} > 3.0 = {abs(gap) > 3.0}")
print(f"   rsi < 40: {rsi:.1f} < 40 = {rsi < 40}")
print(f"   fundamentals > 0.03: {fundamentals:.3f} > 0.03 = {fundamentals > 0.03}")
triggers_1 = abs(gap) > 3.0 and rsi < 40 and fundamentals > 0.03
print(f"   TRIGGERS: {triggers_1}")

# Check bounce scenario 2
print(f"\n3. BOUNCE SCENARIO 2 (Strong Fundamentals):")
print(f"   abs(gap) > 1.0: {abs(gap):.2f} > 1.0 = {abs(gap) > 1.0}")
print(f"   fundamentals > 0.06: {fundamentals:.3f} > 0.06 = {fundamentals > 0.06}")
triggers_2 = abs(gap) > 1.0 and fundamentals > 0.06
print(f"   TRIGGERS: {triggers_2}")

# Check general gap down
print(f"\n4. GENERAL GAP DOWN (Moderate bounce):")
print(f"   gap < -1.5: {gap:.2f} < -1.5 = {gap < -1.5}")
triggers_general = gap < -1.5
print(f"   TRIGGERS: {triggers_general}")

print(f"\n" + "="*80)
print("FINAL DIAGNOSIS:")
print("="*80)

if triggers_1:
    print(f"\n✅ SHOULD trigger Scenario 1 (Oversold bounce)")
elif triggers_2:
    print(f"\n✅ SHOULD trigger Scenario 2 (Strong fundamentals bounce)")
elif triggers_general:
    print(f"\n⚠️ SHOULD enter general gap down logic (moderate bounce)")
else:
    print(f"\n❌ NO bounce detection should trigger")

print(f"\n💡 EXPECTED BEHAVIOR:")
if fundamentals > 0.06:
    print(f"   Fundamentals {fundamentals:.3f} > 0.06 = STRONG")
    print(f"   Gap {gap:.2f}% = Pullback")
    print(f"   RSI {rsi:.1f} = Doesn't matter (fundamentals override!)")
    print(f"   → Should predict: UP (bounce from strong fundamentals)")
else:
    print(f"   Fundamentals {fundamentals:.3f} <= 0.06 = Not strong enough")
    print(f"   → Overbought correction logic applies")

print("\n" + "="*80)
