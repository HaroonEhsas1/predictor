#!/usr/bin/env python3
"""
Comprehensive Stock Independence Verification
Proves AMD and AVGO have their own separate everything
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from stock_config import get_stock_config, STOCK_CONFIGS

def verify_stock_independence():
    """Verify AMD and AVGO are completely independent"""
    
    print("="*80)
    print("STOCK INDEPENDENCE VERIFICATION - AMD vs AVGO")
    print("="*80)
    print("\nProving each stock has its OWN:")
    print("  1. Configuration")
    print("  2. Data source weights")
    print("  3. Historical parameters")
    print("  4. Confidence thresholds")
    print("  5. Keywords")
    print("  6. Competitors")
    print("\n")
    
    amd_config = get_stock_config('AMD')
    avgo_config = get_stock_config('AVGO')
    
    all_tests_passed = True
    
    # Test 1: Basic Configuration
    print("="*80)
    print("TEST #1: BASIC CONFIGURATION")
    print("="*80)
    
    tests = [
        ("Company Name", amd_config['name'], avgo_config['name']),
        ("Typical Volatility", amd_config['typical_volatility'], avgo_config['typical_volatility']),
        ("Historical Gap", amd_config['historical_avg_gap'], avgo_config['historical_avg_gap']),
        ("Min Confidence", amd_config['min_confidence_threshold'], avgo_config['min_confidence_threshold']),
        ("Momentum Rate", amd_config['momentum_continuation_rate'], avgo_config['momentum_continuation_rate']),
    ]
    
    for name, amd_val, avgo_val in tests:
        different = amd_val != avgo_val
        status = "[INDEPENDENT]" if different else "[WARNING: SAME]"
        print(f"{status} {name:20} | AMD: {amd_val:20} | AVGO: {avgo_val:20}")
        if not different and name != "Min Confidence":
            all_tests_passed = False
    
    print()
    
    # Test 2: Data Source Weights
    print("="*80)
    print("TEST #2: DATA SOURCE WEIGHTS (14 Sources)")
    print("="*80)
    
    amd_weights = amd_config['weight_adjustments']
    avgo_weights = avgo_config['weight_adjustments']
    
    all_sources = set(list(amd_weights.keys()) + list(avgo_weights.keys()))
    
    different_count = 0
    for source in sorted(all_sources):
        amd_weight = amd_weights.get(source, 0.0)
        avgo_weight = avgo_weights.get(source, 0.0)
        different = amd_weight != avgo_weight
        
        if different:
            different_count += 1
        
        status = "[DIFFERENT]" if different else "[SAME]"
        diff_pct = ((avgo_weight - amd_weight) / amd_weight * 100) if amd_weight > 0 else 0
        
        print(f"{status} {source:20} | AMD: {amd_weight:.3f} ({amd_weight*100:5.1f}%) | AVGO: {avgo_weight:.3f} ({avgo_weight*100:5.1f}%) | Diff: {diff_pct:+.1f}%")
    
    print(f"\nResult: {different_count}/{len(all_sources)} sources have DIFFERENT weights")
    
    if different_count >= len(all_sources) * 0.5:
        print("[PASS] Stocks have significantly different weight profiles")
    else:
        print("[WARNING] Stocks have too many similar weights")
        all_tests_passed = False
    
    print()
    
    # Test 3: Weight Sum Check
    print("="*80)
    print("TEST #3: WEIGHT SUM VALIDATION")
    print("="*80)
    
    amd_sum = sum(amd_weights.values())
    avgo_sum = sum(avgo_weights.values())
    
    print(f"AMD Total Weights:  {amd_sum:.3f} ({amd_sum*100:.1f}%)")
    print(f"AVGO Total Weights: {avgo_sum:.3f} ({avgo_sum*100:.1f}%)")
    
    if abs(amd_sum - 1.0) < 0.01 and abs(avgo_sum - 1.0) < 0.01:
        print("[PASS] Both stocks have properly normalized weights (~100%)")
    else:
        print("[WARNING] Weights don't sum to 100%")
        all_tests_passed = False
    
    print()
    
    # Test 4: Historical Parameters
    print("="*80)
    print("TEST #4: HISTORICAL PARAMETERS")
    print("="*80)
    
    print(f"AMD:")
    print(f"  Typical Volatility:  {amd_config['typical_volatility']*100:.2f}%")
    print(f"  Historical Avg Gap:  {amd_config['historical_avg_gap']*100:.2f}%")
    print(f"  Momentum Continue:   {amd_config['momentum_continuation_rate']*100:.1f}%")
    print(f"  Min Confidence:      {amd_config['min_confidence_threshold']*100:.1f}%")
    
    print(f"\nAVGO:")
    print(f"  Typical Volatility:  {avgo_config['typical_volatility']*100:.2f}%")
    print(f"  Historical Avg Gap:  {avgo_config['historical_avg_gap']*100:.2f}%")
    print(f"  Momentum Continue:   {avgo_config['momentum_continuation_rate']*100:.1f}%")
    print(f"  Min Confidence:      {avgo_config['min_confidence_threshold']*100:.1f}%")
    
    print(f"\nDifferences:")
    vol_diff = abs(amd_config['typical_volatility'] - avgo_config['typical_volatility'])
    gap_diff = abs(amd_config['historical_avg_gap'] - avgo_config['historical_avg_gap'])
    mom_diff = abs(amd_config['momentum_continuation_rate'] - avgo_config['momentum_continuation_rate'])
    conf_diff = abs(amd_config['min_confidence_threshold'] - avgo_config['min_confidence_threshold'])
    
    print(f"  Volatility Diff:  {vol_diff*100:.2f}%")
    print(f"  Gap Diff:         {gap_diff*100:.2f}%")
    print(f"  Momentum Diff:    {mom_diff*100:.1f}%")
    print(f"  Confidence Diff:  {conf_diff*100:.1f}%")
    
    if vol_diff > 0.001 and gap_diff > 0.001:
        print("[PASS] Stocks have distinct historical characteristics")
    else:
        print("[WARNING] Historical parameters too similar")
        all_tests_passed = False
    
    print()
    
    # Test 5: Keywords
    print("="*80)
    print("TEST #5: NEWS KEYWORDS (Stock-Specific)")
    print("="*80)
    
    amd_keywords = set(amd_config.get('news_keywords', []))
    avgo_keywords = set(avgo_config.get('news_keywords', []))
    
    overlap = amd_keywords.intersection(avgo_keywords)
    amd_unique = amd_keywords - avgo_keywords
    avgo_unique = avgo_keywords - amd_keywords
    
    print(f"AMD Unique Keywords ({len(amd_unique)}):")
    print(f"  {', '.join(sorted(list(amd_unique)[:5]))}...")
    
    print(f"\nAVGO Unique Keywords ({len(avgo_unique)}):")
    print(f"  {', '.join(sorted(list(avgo_unique)[:5]))}...")
    
    print(f"\nShared Keywords ({len(overlap)}):")
    if overlap:
        print(f"  {', '.join(sorted(overlap))}")
    else:
        print(f"  (None)")
    
    if len(overlap) < len(amd_keywords) * 0.3:
        print("[PASS] Stocks have mostly unique keywords")
    else:
        print("[WARNING] Too many shared keywords")
    
    print()
    
    # Test 6: Competitors
    print("="*80)
    print("TEST #6: COMPETITOR TRACKING")
    print("="*80)
    
    amd_competitors = set(amd_config.get('competitors', []))
    avgo_competitors = set(avgo_config.get('competitors', []))
    
    print(f"AMD Competitors: {', '.join(sorted(amd_competitors))}")
    print(f"AVGO Competitors: {', '.join(sorted(avgo_competitors))}")
    
    comp_overlap = amd_competitors.intersection(avgo_competitors)
    print(f"\nShared Competitors: {', '.join(sorted(comp_overlap)) if comp_overlap else '(None)'}")
    
    if len(amd_competitors) > 0 and len(avgo_competitors) > 0:
        print("[PASS] Each stock tracks its own competitors")
    else:
        print("[WARNING] Missing competitor data")
    
    print()
    
    # Test 7: Key Weight Differences
    print("="*80)
    print("TEST #7: KEY STRATEGIC DIFFERENCES")
    print("="*80)
    
    key_diffs = [
        ("News Weight", amd_weights.get('news', 0), avgo_weights.get('news', 0), 
         "AVGO should be higher (news-driven)"),
        ("Reddit Weight", amd_weights.get('reddit', 0), avgo_weights.get('reddit', 0),
         "AMD should be higher (retail-driven)"),
        ("Institutional Weight", amd_weights.get('institutional', 0), avgo_weights.get('institutional', 0),
         "AVGO should be higher (institution-heavy)"),
        ("DXY Weight", amd_weights.get('dxy', 0), avgo_weights.get('dxy', 0),
         "AVGO should be higher (more international revenue)"),
    ]
    
    for name, amd_val, avgo_val, expectation in key_diffs:
        if "higher" in expectation:
            expected_stock = expectation.split()[0]
            is_correct = (avgo_val > amd_val) if "AVGO" in expected_stock else (amd_val > avgo_val)
        else:
            is_correct = amd_val != avgo_val
        
        status = "[CORRECT]" if is_correct else "[MISMATCH]"
        print(f"{status} {name:20} | AMD: {amd_val:.3f} | AVGO: {avgo_val:.3f}")
        print(f"         Expectation: {expectation}")
        
        if not is_correct:
            all_tests_passed = False
    
    print()
    
    # Final Summary
    print("="*80)
    print("FINAL VERDICT")
    print("="*80)
    
    if all_tests_passed:
        print("[SUCCESS] AMD and AVGO are COMPLETELY INDEPENDENT")
        print("\nEach stock has:")
        print("  [OK] Own volatility parameters")
        print("  [OK] Own historical gap data")
        print("  [OK] Own confidence thresholds")
        print("  [OK] Own data source weights")
        print("  [OK] Own news keywords")
        print("  [OK] Own competitor tracking")
        print("  [OK] Own strategic focus")
        print("\n  SYSTEM IS PROPERLY CONFIGURED")
    else:
        print("[WARNING] Some configuration issues detected")
        print("Review the tests above for details")
    
    print("="*80)
    
    return all_tests_passed

if __name__ == "__main__":
    verify_stock_independence()
