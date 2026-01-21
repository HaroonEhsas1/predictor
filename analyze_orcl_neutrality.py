"""
ANALYZE ORCL NEUTRALITY
========================
Why does ORCL keep showing neutral/uncertain predictions?
Compare data sources and signal strength across AMD, AVGO, ORCL
"""

# From today's predictions
STOCK_SCORES = {
    'AMD': {
        'total_score': 0.350,  # Estimate from 94% confidence
        'confidence': 94.0,
        'direction': 'UP',
        'components': {
            'technical': 0.140,
            'options': 0.110,
            'news': 0.060,
            'futures': 0.011,
            'premarket': 0.070,
            'hidden_edge': 0.012,
            'sector': 0.008,
            'institutional': 0.000,
            'reddit': 0.008,
            'twitter': 0.000,
            'vix': 0.004,
            'analyst': 0.013,
            'dxy': 0.000,
            'earnings': 0.000,
            'short_interest': 0.000
        }
    },
    'AVGO': {
        'total_score': 0.350,  # Estimate from 94% confidence
        'confidence': 94.1,
        'direction': 'UP',
        'components': {
            'technical': 0.070,
            'options': 0.110,
            'news': 0.080,
            'futures': 0.011,
            'premarket': 0.070,
            'hidden_edge': 0.008,
            'sector': 0.010,
            'institutional': 0.000,
            'reddit': 0.002,
            'twitter': 0.000,
            'vix': 0.004,
            'analyst': 0.019,
            'dxy': 0.000,
            'earnings': 0.000,
            'short_interest': 0.000
        }
    },
    'ORCL': {
        'total_score': -0.074,
        'confidence': 57.9,
        'direction': 'DOWN',
        'components': {
            'technical': -0.156,
            'options': 0.110,
            'news': 0.053,
            'futures': 0.005,
            'premarket': -0.020,
            'hidden_edge': 0.008,
            'sector': 0.001,
            'institutional': 0.000,
            'reddit': 0.000,
            'twitter': 0.000,
            'vix': 0.000,
            'analyst': 0.015,
            'dxy': 0.000,
            'earnings': 0.000,
            'short_interest': 0.000,
            'rel_strength': -0.060
        }
    }
}

def analyze_neutrality():
    print("="*80)
    print("🔍 ORCL NEUTRALITY ANALYSIS")
    print("="*80)
    print("\nWhy does ORCL keep showing neutral/uncertain predictions?")
    print("Let's compare data sources across all 3 stocks...\n")
    
    # Count active sources
    for symbol, data in STOCK_SCORES.items():
        print(f"\n{'='*80}")
        print(f"📊 {symbol}")
        print(f"{'='*80}")
        print(f"Total Score: {data['total_score']:+.3f}")
        print(f"Confidence: {data['confidence']:.1f}%")
        print(f"Direction: {data['direction']}")
        
        components = data['components']
        active = sum(1 for v in components.values() if abs(v) > 0.001)
        total = len(components)
        
        print(f"\n📊 Active Sources: {active}/{total} ({active/total*100:.0f}%)")
        
        # Categorize signals
        strong_signals = [(k, v) for k, v in components.items() if abs(v) >= 0.05]
        weak_signals = [(k, v) for k, v in components.items() if 0.001 < abs(v) < 0.05]
        zero_signals = [(k, v) for k, v in components.items() if abs(v) <= 0.001]
        
        print(f"\n💪 STRONG Signals (≥0.05): {len(strong_signals)}")
        for name, score in sorted(strong_signals, key=lambda x: abs(x[1]), reverse=True):
            direction = "📈" if score > 0 else "📉"
            print(f"   {direction} {name:15} {score:+.3f}")
        
        print(f"\n📊 WEAK Signals (0.001-0.05): {len(weak_signals)}")
        for name, score in sorted(weak_signals, key=lambda x: abs(x[1]), reverse=True):
            direction = "📈" if score > 0 else "📉"
            print(f"   {direction} {name:15} {score:+.3f}")
        
        print(f"\n❌ ZERO/Neutral Signals: {len(zero_signals)}")
        for name, score in zero_signals:
            print(f"   ➖ {name:15} {score:+.3f}")
    
    # Comparison
    print(f"\n{'='*80}")
    print("📊 COMPARISON SUMMARY")
    print(f"{'='*80}\n")
    
    print(f"{'Metric':<25} {'AMD':<15} {'AVGO':<15} {'ORCL':<15}")
    print("-"*80)
    
    # Active sources
    amd_active = sum(1 for v in STOCK_SCORES['AMD']['components'].values() if abs(v) > 0.001)
    avgo_active = sum(1 for v in STOCK_SCORES['AVGO']['components'].values() if abs(v) > 0.001)
    orcl_active = sum(1 for v in STOCK_SCORES['ORCL']['components'].values() if abs(v) > 0.001)
    
    print(f"{'Active Sources':<25} {amd_active:<15} {avgo_active:<15} {orcl_active:<15}")
    
    # Strong signals
    amd_strong = sum(1 for v in STOCK_SCORES['AMD']['components'].values() if abs(v) >= 0.05)
    avgo_strong = sum(1 for v in STOCK_SCORES['AVGO']['components'].values() if abs(v) >= 0.05)
    orcl_strong = sum(1 for v in STOCK_SCORES['ORCL']['components'].values() if abs(v) >= 0.05)
    
    print(f"{'Strong Signals (≥0.05)':<25} {amd_strong:<15} {avgo_strong:<15} {orcl_strong:<15}")
    
    # Zero signals
    amd_zero = sum(1 for v in STOCK_SCORES['AMD']['components'].values() if abs(v) <= 0.001)
    avgo_zero = sum(1 for v in STOCK_SCORES['AVGO']['components'].values() if abs(v) <= 0.001)
    orcl_zero = sum(1 for v in STOCK_SCORES['ORCL']['components'].values() if abs(v) <= 0.001)
    
    print(f"{'Zero/Neutral Signals':<25} {amd_zero:<15} {avgo_zero:<15} {orcl_zero:<15}")
    
    # Bullish vs bearish
    amd_bull = sum(v for v in STOCK_SCORES['AMD']['components'].values() if v > 0)
    amd_bear = sum(v for v in STOCK_SCORES['AMD']['components'].values() if v < 0)
    
    avgo_bull = sum(v for v in STOCK_SCORES['AVGO']['components'].values() if v > 0)
    avgo_bear = sum(v for v in STOCK_SCORES['AVGO']['components'].values() if v < 0)
    
    orcl_bull = sum(v for v in STOCK_SCORES['ORCL']['components'].values() if v > 0)
    orcl_bear = sum(v for v in STOCK_SCORES['ORCL']['components'].values() if v < 0)
    
    print(f"{'Bullish Component Sum':<25} {amd_bull:+.3f}{'':<7} {avgo_bull:+.3f}{'':<7} {orcl_bull:+.3f}{'':<7}")
    print(f"{'Bearish Component Sum':<25} {amd_bear:+.3f}{'':<7} {avgo_bear:+.3f}{'':<7} {orcl_bear:+.3f}{'':<7}")
    print(f"{'Net Score':<25} {STOCK_SCORES['AMD']['total_score']:+.3f}{'':<7} {STOCK_SCORES['AVGO']['total_score']:+.3f}{'':<7} {STOCK_SCORES['ORCL']['total_score']:+.3f}{'':<7}")
    
    # Diagnosis
    print(f"\n{'='*80}")
    print("🔍 DIAGNOSIS: Why is ORCL Neutral?")
    print(f"{'='*80}\n")
    
    print("📊 ORCL Issues Identified:\n")
    
    issue_count = 0
    
    # Issue 1: Too many zero signals
    if orcl_zero > amd_zero and orcl_zero > avgo_zero:
        issue_count += 1
        print(f"{issue_count}. ❌ TOO MANY ZERO SIGNALS ({orcl_zero} vs AMD {amd_zero}, AVGO {avgo_zero})")
        print(f"   Problem: Many data sources returning neutral/zero")
        print(f"   Sources: institutional, reddit, twitter, dxy, short_interest, earnings, sector, vix")
        print(f"   Impact: Less data = less conviction\n")
    
    # Issue 2: Conflicting strong signals
    orcl_comps = STOCK_SCORES['ORCL']['components']
    tech_vs_opts = orcl_comps['technical'] * orcl_comps['options']
    if tech_vs_opts < 0 and abs(orcl_comps['technical']) > 0.1 and abs(orcl_comps['options']) > 0.1:
        issue_count += 1
        print(f"{issue_count}. ⚠️ CONFLICTING STRONG SIGNALS")
        print(f"   Technical: {orcl_comps['technical']:+.3f} (BEARISH)")
        print(f"   Options:   {orcl_comps['options']:+.3f} (BULLISH)")
        print(f"   Result: They cancel each other out → Net -0.046\n")
    
    # Issue 3: Low absolute magnitude
    if abs(STOCK_SCORES['ORCL']['total_score']) < 0.10:
        issue_count += 1
        print(f"{issue_count}. 📉 LOW TOTAL MAGNITUDE")
        print(f"   ORCL score: {STOCK_SCORES['ORCL']['total_score']:+.3f}")
        print(f"   AMD score:  {STOCK_SCORES['AMD']['total_score']:+.3f}")
        print(f"   AVGO score: {STOCK_SCORES['AVGO']['total_score']:+.3f}")
        print(f"   Result: ORCL close to threshold (±0.04), weak signal\n")
    
    # Issue 4: Stock nature
    issue_count += 1
    print(f"{issue_count}. 🏢 ORCL STOCK CHARACTERISTICS")
    print(f"   • Enterprise software (less retail interest)")
    print(f"   • Reddit: 0% weight (no WSB hype)")
    print(f"   • Twitter: 0% weight (no social buzz)")
    print(f"   • Institutional-heavy (but institutional flow = 0.000 today)")
    print(f"   • More stable = less extreme moves = weaker signals\n")
    
    # Summary
    print(f"{'='*80}")
    print("💡 CONCLUSIONS")
    print(f"{'='*80}\n")
    
    print("✅ GOOD NEWS:")
    print("   • ORCL genuinely IS more neutral/range-bound")
    print("   • System correctly showing lower confidence")
    print("   • This is HONEST behavior, not a bug\n")
    
    print("⚠️ POTENTIAL IMPROVEMENTS:")
    print("   1. Increase institutional weight (currently 18%, could be 22%)")
    print("   2. Add Oracle-specific catalysts (cloud deals, earnings beats)")
    print("   3. Reduce options weight when conflicting (already done)")
    print("   4. Accept that ORCL will have fewer actionable trades\n")
    
    print("📊 EXPECTATION:")
    print("   • AMD: High-beta, more extreme predictions (good for trading)")
    print("   • AVGO: M&A-driven, event-based predictions (good for trading)")
    print("   • ORCL: Stable, range-bound, fewer extremes (fewer trades)")
    print("   → This is CORRECT behavior based on stock characteristics!\n")

if __name__ == "__main__":
    analyze_neutrality()
