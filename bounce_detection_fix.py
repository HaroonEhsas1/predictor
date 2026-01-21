"""
BOUNCE DETECTION LOGIC FIX
===========================

PROBLEM: System is REACTIVE (sees drop, predicts more drop)
SOLUTION: System should be PREDICTIVE (sees extreme drop = bounce opportunity)

TRADING PSYCHOLOGY:
- Large gap down + oversold = PANIC SELLING = Buying opportunity
- Not "stock is weak, will drop more"

IMPLEMENTATION:
1. Detect extreme drops (>3% gap, >5% total drop)
2. Check if oversold (RSI <40)
3. Check if fundamentals still strong (news, options, analyst ratings)
4. If all 3 = BOUNCE signal (BULLISH not bearish!)

EXAMPLES:
- ORCL: -$15, RSI 34, Strong fundamentals → BOUNCE expected (not more drop)
- Any stock: -6% gap, RSI 35, Positive news → BUY signal
"""

def detect_bounce_opportunity(
    gap_percent,
    total_drop_percent,
    rsi,
    news_score,
    options_score,
    analyst_score,
    technical_score
):
    """
    Detects if extreme drop creates bounce opportunity
    
    Returns:
        bounce_signal: Float (-1.0 to +1.0)
        bounce_confidence: Float (0 to 100)
        reason: String explanation
    """
    
    # Step 1: Is this an EXTREME drop?
    is_extreme_gap = abs(gap_percent) > 3.0  # >3% gap
    is_big_drop = total_drop_percent < -3.0  # >3% total drop
    
    # Step 2: Is it OVERSOLD?
    is_oversold = rsi < 40
    is_very_oversold = rsi < 35
    
    # Step 3: Are fundamentals STRONG? (conflict between price and fundamentals)
    fundamental_score = (news_score + options_score + analyst_score) / 3
    fundamentals_strong = fundamental_score > 0.05
    
    # Step 4: BOUNCE DETECTION
    if is_extreme_gap and is_oversold and fundamentals_strong:
        # CLASSIC BOUNCE SETUP
        bounce_signal = 0.15  # Strong bullish bounce signal
        
        if is_very_oversold:
            bounce_signal = 0.20  # Even stronger if RSI < 35
            
        if abs(gap_percent) > 5:
            bounce_signal += 0.05  # Bigger gap = bigger bounce
            
        confidence = 75.0
        reason = f"🎯 BOUNCE OPPORTUNITY: {gap_percent:.1f}% gap, RSI {rsi:.0f}, Strong fundamentals → Classic oversold bounce setup"
        
        return bounce_signal, confidence, reason
    
    elif is_big_drop and is_oversold:
        # Moderate bounce potential
        bounce_signal = 0.08
        confidence = 65.0
        reason = f"📊 Potential bounce: Drop {total_drop_percent:.1f}%, RSI {rsi:.0f} → Oversold bounce likely"
        
        return bounce_signal, confidence, reason
    
    elif is_extreme_gap and not is_oversold:
        # Gap but not oversold - gap fill potential but weaker
        bounce_signal = 0.03
        confidence = 55.0
        reason = f"📈 Gap fill potential: {gap_percent:.1f}% gap, RSI {rsi:.0f} → Partial recovery likely"
        
        return bounce_signal, confidence, reason
    
    else:
        # No bounce setup
        return 0.0, 0.0, "No bounce setup detected"


def reverse_gap_penalty(
    gap_percent,
    rsi,
    fundamental_score,
    current_gap_penalty
):
    """
    REVERSES gap penalty when it's actually a bounce opportunity
    
    OLD LOGIC: Big gap down → Apply penalty (more bearish)
    NEW LOGIC: Big gap down + oversold + strong fundamentals → REVERSE to bullish
    """
    
    # Is this a panic sell setup?
    is_panic_sell = abs(gap_percent) > 4.0 and rsi < 38 and fundamental_score > 0.05
    
    if is_panic_sell:
        # REVERSE THE PENALTY
        # If penalty was -0.279, reverse to +0.150 (bounce signal)
        reversed_signal = abs(current_gap_penalty) * 0.5  # Take half the penalty magnitude
        
        return reversed_signal, "🔄 GAP PENALTY REVERSED: Panic sell → Bounce opportunity"
    
    # Moderate oversold with decent fundamentals
    elif abs(gap_percent) > 3.0 and rsi < 40 and fundamental_score > 0.0:
        # Reduce the penalty significantly
        reduced_penalty = current_gap_penalty * 0.3  # Only apply 30% of penalty
        
        return reduced_penalty, "📉 Gap penalty reduced: Oversold conditions"
    
    else:
        # Keep original penalty
        return current_gap_penalty, "Gap penalty applied as normal"


# TEST CASES
if __name__ == "__main__":
    print("\n" + "="*80)
    print("🧪 TESTING BOUNCE DETECTION LOGIC")
    print("="*80)
    
    # Test Case 1: ORCL Oct 30 (Yesterday - WRONG prediction)
    print("\n📊 TEST 1: ORCL Oct 30 (Actual scenario that failed)")
    gap = -6.45
    total_drop = -6.45
    rsi = 34.6
    news = 0.140
    options = 0.110
    analyst = 0.015
    tech = -0.107
    
    bounce_signal, confidence, reason = detect_bounce_opportunity(
        gap, total_drop, rsi, news, options, analyst, tech
    )
    
    print(f"   Gap: {gap}%, RSI: {rsi}, News: {news:+.3f}")
    print(f"   Bounce Signal: {bounce_signal:+.3f}")
    print(f"   Confidence: {confidence:.1f}%")
    print(f"   {reason}")
    print(f"   ✅ Should have predicted: UP/BOUNCE (not DOWN)")
    
    # Test Case 2: ORCL Oct 31 (Today - Same pattern)
    print("\n📊 TEST 2: ORCL Oct 31 (Today's prediction)")
    gap = -4.70
    rsi = 34.4
    
    bounce_signal, confidence, reason = detect_bounce_opportunity(
        gap, total_drop, rsi, news, options, analyst, tech
    )
    
    print(f"   Gap: {gap}%, RSI: {rsi}")
    print(f"   Bounce Signal: {bounce_signal:+.3f}")
    print(f"   {reason}")
    
    # Test Case 3: Normal drop (no bounce)
    print("\n📊 TEST 3: Normal drop (no special setup)")
    gap = -1.5
    rsi = 52
    news = 0.02
    
    bounce_signal, confidence, reason = detect_bounce_opportunity(
        gap, -1.5, rsi, news, 0.05, 0.01, -0.03
    )
    
    print(f"   Gap: {gap}%, RSI: {rsi}")
    print(f"   Bounce Signal: {bounce_signal:+.3f}")
    print(f"   {reason}")
    
    print("\n" + "="*80)
    print("✅ BOUNCE DETECTION LOGIC READY TO IMPLEMENT")
    print("="*80)
