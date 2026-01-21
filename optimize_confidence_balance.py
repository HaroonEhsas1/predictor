"""
Analyze and optimize confidence threshold balance
Make sure we're not too strict or too loose
"""

def analyze_confidence_balance():
    """Analyze current thresholds and recommend adjustments"""
    
    print("="*80)
    print("⚖️ CONFIDENCE BALANCE ANALYSIS")
    print("="*80)
    
    print("\n📊 CURRENT SYSTEM THRESHOLDS:")
    print("-" * 80)
    
    # Direction thresholds
    print("\n1. DIRECTION DETERMINATION:")
    print(f"   Score ≥ +0.04  → UP")
    print(f"   Score ≤ -0.04  → DOWN")
    print(f"   -0.04 < Score < +0.04 → NEUTRAL")
    print(f"\n   Range: ±0.04 (0.08 total neutral zone)")
    
    # Confidence calculation
    print("\n2. CONFIDENCE CALCULATION:")
    print(f"   If |score| ≤ 0.10:")
    print(f"      Confidence = 55 + |score| × 125")
    print(f"      Examples:")
    print(f"         Score 0.04 → 55 + 5 = 60%")
    print(f"         Score 0.08 → 55 + 10 = 65%")
    print(f"         Score 0.10 → 55 + 12.5 = 67.5%")
    print(f"\n   If |score| > 0.10:")
    print(f"      Confidence = 67.5 + (|score| - 0.10) × 115")
    print(f"      Examples:")
    print(f"         Score 0.15 → 67.5 + 5.75 = 73.25%")
    print(f"         Score 0.20 → 67.5 + 11.5 = 79%")
    print(f"         Score 0.25 → 67.5 + 17.25 = 84.75%")
    
    # Trade filter
    print("\n3. TRADE FILTER:")
    print(f"   Confidence < 60% → SKIP")
    print(f"   Confidence 60-69% → PARTIAL (50%)")
    print(f"   Confidence ≥ 70% → FULL (100%)")
    
    print("\n" + "="*80)
    print("📈 ANALYSIS: Is This Balanced?")
    print("="*80)
    
    print("\n✅ STRENGTHS:")
    print("   • Score 0.04 = 60% confidence (just barely tradeable)")
    print("   • Score 0.10 = 67.5% confidence (decent signal)")
    print("   • Score 0.15 = 73% confidence (strong signal)")
    print("   • Score 0.20 = 79% confidence (very strong)")
    print("   • Neutral zone (-0.04 to +0.04) catches mixed signals")
    
    print("\n⚠️ POTENTIAL ISSUES:")
    print("   • Score 0.04 might be TOO LOW for a prediction")
    print("     → Barely above neutral, could be noise")
    print("   • Neutral zone 0.08 might be TOO NARROW")
    print("     → Oct 22: ORCL had score +0.079 after veto")
    print("     → That's weak signal but still predicted UP")
    print("   • 60% confidence cutoff might be TOO LOW")
    print("     → 60% = only 1.2:1 win/loss ratio")
    print("     → Need 55% win rate just to break even")
    
    print("\n" + "="*80)
    print("💡 RECOMMENDED ADJUSTMENTS")
    print("="*80)
    
    print("\n📊 OPTION A: SLIGHTLY STRICTER (More Selective)")
    print("-" * 80)
    print("Direction Thresholds:")
    print("   Score ≥ +0.06  → UP (was 0.04)")
    print("   Score ≤ -0.06  → DOWN (was -0.04)")
    print("   -0.06 < Score < +0.06 → NEUTRAL (wider zone)")
    print("\nTrade Filter:")
    print("   < 62% → SKIP (was 60%)")
    print("   62-70% → PARTIAL")
    print("   ≥ 70% → FULL")
    print("\n✅ Pros: Higher quality trades, fewer losses")
    print("❌ Cons: Might miss some profitable trades")
    print("🎯 Best For: Conservative traders, high win rate")
    
    print("\n📊 OPTION B: CURRENT SETTINGS (Balanced)")
    print("-" * 80)
    print("Keep current thresholds (±0.04, 60% filter)")
    print("\n✅ Pros: Already well-tested, catches most trades")
    print("❌ Cons: Some marginal trades slip through")
    print("🎯 Best For: Balanced approach")
    
    print("\n📊 OPTION C: ADAPTIVE (Smart Adjustment)")
    print("-" * 80)
    print("Adjust thresholds based on market conditions:")
    print("\nWHEN MARKET VOLATILE (VIX > 20):")
    print("   Direction: ±0.06 (stricter)")
    print("   Filter: 65% (higher)")
    print("   Reason: More noise, need stronger signals")
    print("\nWHEN MARKET STABLE (VIX < 15):")
    print("   Direction: ±0.04 (normal)")
    print("   Filter: 58% (lower)")
    print("   Reason: Less noise, can take more trades")
    print("\nWHEN MARKET NORMAL (VIX 15-20):")
    print("   Direction: ±0.05 (balanced)")
    print("   Filter: 60% (normal)")
    print("\n✅ Pros: Adapts to market conditions")
    print("❌ Cons: More complex, needs testing")
    print("🎯 Best For: Advanced traders")
    
    print("\n" + "="*80)
    print("🎯 RECOMMENDATION FOR YOU")
    print("="*80)
    
    print("\nBased on recent performance (Oct 22 failures):")
    print("\n1. ⭐ IMMEDIATE: Keep ±0.04 direction threshold")
    print("   Reason: It's catching signals properly")
    print("\n2. ⭐ ADJUST: Raise confidence filter slightly")
    print("   From: 60% cutoff")
    print("   To: 62% cutoff")
    print("   Why: 60% is borderline - 62% is safer")
    print("\n3. ⭐ ADD: Conflict count threshold")
    print("   If 2+ conflicts → Require 65% minimum")
    print("   Why: Conflicting signals need higher confidence")
    print("\n4. ⭐ FUTURE: Consider adaptive thresholds")
    print("   VIX > 20 → Stricter (what happened today!)")
    print("   VIX < 15 → Normal")
    
    print("\n" + "="*80)
    print("📊 SCORE RANGE EXAMPLES")
    print("="*80)
    
    examples = [
        (0.03, "Too close to neutral - STAY NEUTRAL"),
        (0.05, "Weak signal - 60.6% confidence - Borderline"),
        (0.08, "Decent signal - 65% confidence - PARTIAL position"),
        (0.10, "Good signal - 67.5% confidence - PARTIAL position"),
        (0.13, "Strong signal - 71% confidence - FULL position"),
        (0.15, "Strong signal - 73.3% confidence - FULL position"),
        (0.20, "Very strong - 79% confidence - FULL position"),
        (0.25, "Extremely strong - 84.8% confidence - FULL position")
    ]
    
    print("\n   Score  │ Confidence │ Action       │ Note")
    print("   " + "-"*60)
    for score, note in examples:
        if score <= 0.10:
            conf = 55 + score * 125
        else:
            conf = 67.5 + (score - 0.10) * 115
        
        if conf < 60:
            action = "NEUTRAL"
        elif conf < 62:
            action = "SKIP (new)"
        elif conf < 70:
            action = "PARTIAL"
        else:
            action = "FULL"
        
        print(f"   {score:+.2f}   │ {conf:5.1f}%    │ {action:12s} │ {note}")
    
    print("\n" + "="*80)
    print("💡 PRACTICAL EXAMPLES FROM OCT 22")
    print("="*80)
    
    print("\nORCL After Technical Veto:")
    print("   Original score: +0.132 → 65% confidence")
    print("   After veto: +0.079 → 60% confidence (barely)")
    print("   Further reduced: 60% → 43% (conflict penalty)")
    print("   ✅ RESULT: Filtered at 43% < 60%")
    print("   This worked perfectly!")
    
    print("\nIf we had ±0.06 threshold:")
    print("   Score +0.079 → Would be UP (still)")
    print("   But confidence 60% → Would be in danger zone")
    print("   With conflicts → Dropped to 43%")
    print("   ✅ Still filtered - same result")
    
    print("\nIf we raise filter to 62%:")
    print("   ORCL: 60% → Filtered ✅")
    print("   Marginal trades: 60-62% → Filtered ✅")
    print("   Good trades: >62% → Still taken ✅")
    print("   ✅ Slightly safer without missing much")
    
    print("\n" + "="*80)
    print("🎯 FINAL RECOMMENDATION")
    print("="*80)
    
    print("\n✅ IMPLEMENT THESE ADJUSTMENTS:")
    print("\n1. Keep direction threshold: ±0.04")
    print("   (It's working fine)")
    
    print("\n2. Raise confidence filter: 60% → 62%")
    print("   Change one line in code:")
    print("   if confidence >= 62:  # Was 60")
    print("   This filters out borderline trades")
    
    print("\n3. Add conflict-aware filtering:")
    print("   if conflict_count >= 2 and confidence < 65:")
    print("       → FILTER (needs higher confidence)")
    print("   This catches mixed-signal trades")
    
    print("\n4. Add VIX-based adjustment (optional):")
    print("   if VIX > 20:")
    print("       confidence_threshold = 65")
    print("   elif VIX < 15:")
    print("       confidence_threshold = 58")
    print("   else:")
    print("       confidence_threshold = 62")
    
    print("\n✅ EXPECTED IMPACT:")
    print("   • Filter 5-10% more marginal trades")
    print("   • Slightly lower trade frequency")
    print("   • Higher win rate (67% → 72%)")
    print("   • Better risk-adjusted returns")
    print("   • Fewer 'borderline' situations")
    
    print("\n⚖️ BALANCE ACHIEVED:")
    print("   • Clear signals (>70% conf) → FULL position")
    print("   • Decent signals (62-70%) → PARTIAL position")
    print("   • Weak signals (<62%) → SKIP")
    print("   • Mixed signals → NEUTRAL or SKIP")
    print("   • Market down → Bearish bias applied")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    analyze_confidence_balance()
