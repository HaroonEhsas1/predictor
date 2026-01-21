"""
Test Bounce Detection Logic
Verify that ORCL Oct 31 data triggers bounce detection
"""

# Simulate ORCL Oct 31 conditions
premarket_change = -4.79  # Gap down
rsi = 34.4  # Oversold
news_score = 0.140  # Strong
options_score = 0.110  # Strong (estimated from pattern)
analyst_score = 0.015  # Positive

print("="*80)
print("🧪 TESTING BOUNCE DETECTION - ORCL OCT 31")
print("="*80)

print(f"\n📊 INPUT CONDITIONS:")
print(f"   Premarket Gap: {premarket_change:+.2f}%")
print(f"   RSI: {rsi:.1f}")
print(f"   News Score: {news_score:+.3f}")
print(f"   Options Score: {options_score:+.3f}")
print(f"   Analyst Score: {analyst_score:+.3f}")

# Check if bounce detection should trigger
print(f"\n🔍 CHECKING CONDITIONS:")
print(f"   1. Gap > 3%: {abs(premarket_change)} > 3.0 = {abs(premarket_change) > 3.0}")
print(f"   2. RSI < 40: {rsi} < 40 = {rsi < 40}")

# Calculate fundamental average
fundamental_score = 0
fundamental_count = 0

if news_score != 0:
    fundamental_score += news_score
    fundamental_count += 1
if options_score != 0:
    fundamental_score += options_score
    fundamental_count += 1
if analyst_score != 0:
    fundamental_score += analyst_score
    fundamental_count += 1

if fundamental_count > 0:
    fundamental_avg = fundamental_score / fundamental_count
else:
    fundamental_avg = 0

print(f"   3. Fundamentals: ({news_score} + {options_score} + {analyst_score}) / 3 = {fundamental_avg:.3f}")
print(f"      Strong enough: {fundamental_avg:.3f} > 0.03 = {fundamental_avg > 0.03}")

# Check if ALL conditions met
if abs(premarket_change) > 3.0 and rsi < 40 and fundamental_avg > 0.03:
    print(f"\n✅ ALL CONDITIONS MET - BOUNCE DETECTION SHOULD TRIGGER!")
    
    # Calculate bounce signal
    bounce_signal = 0.15  # Base
    bounce_signal += abs(premarket_change) * 0.015  # Gap factor
    
    if rsi < 35:
        bounce_signal += 0.05  # Very oversold bonus
        
    if fundamental_avg > 0.08:
        bounce_signal += 0.03  # Strong fundamentals bonus
    
    print(f"\n🎯 BOUNCE SIGNAL CALCULATION:")
    print(f"   Base Signal: 0.150")
    print(f"   Gap Bonus: {abs(premarket_change)} × 0.015 = {abs(premarket_change) * 0.015:.3f}")
    if rsi < 35:
        print(f"   Very Oversold Bonus: 0.050")
    if fundamental_avg > 0.08:
        print(f"   Strong Fundamentals Bonus: 0.030")
    print(f"   -" * 40)
    print(f"   TOTAL BOUNCE SIGNAL: +{bounce_signal:.3f}")
    
    print(f"\n💡 PREDICTION:")
    print(f"   System should REVERSE from bearish to BULLISH")
    print(f"   Expected direction: UP (bounce from oversold)")
    print(f"   Expected confidence: 65-75%")
    
else:
    print(f"\n❌ CONDITIONS NOT MET")
    if not abs(premarket_change) > 3.0:
        print(f"   Gap too small: {abs(premarket_change):.2f}% <= 3.0%")
    if not rsi < 40:
        print(f"   Not oversold: RSI {rsi:.1f} >= 40")
    if not fundamental_avg > 0.03:
        print(f"   Fundamentals too weak: {fundamental_avg:.3f} <= 0.03")

print("\n" + "="*80)
print("📋 DIAGNOSIS:")
print("="*80)

if abs(premarket_change) > 3.0 and rsi < 40 and fundamental_avg > 0.03:
    print("\n✅ Bounce detection logic is CORRECT")
    print("   If system still predicted DOWN, check:")
    print("   1. Is bounce signal being calculated?")
    print("   2. Is technical conflict resolution OVERRIDING the bounce?")
    print("   3. Is the bounce happening BEFORE or AFTER conflict resolution?")
    print("\n💡 SOLUTION: Bounce detection must happen AFTER conflict resolution")
    print("   OR: Bounce signal must be strong enough to survive conflicts")
else:
    print("\n⚠️ One or more conditions not met - bounce detection won't trigger")

print("\n" + "="*80)
