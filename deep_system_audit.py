#!/usr/bin/env python3
"""
COMPREHENSIVE DEEP SYSTEM AUDIT
Check for logic conflicts, mismatches, and potential prediction errors
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from comprehensive_nextday_predictor import ComprehensiveNextDayPredictor
from stock_config import get_stock_config, get_stock_weight_adjustments, ACTIVE_STOCKS
import yfinance as yf

def audit_weight_totals():
    """Audit 1: Check if weights sum to 1.0"""
    print("\n" + "="*80)
    print("AUDIT 1: Weight Totals Check")
    print("="*80)
    
    issues = []
    
    for symbol in ACTIVE_STOCKS:
        weights = get_stock_weight_adjustments(symbol)
        total = sum(weights.values())
        
        print(f"\n{symbol} Weight Total: {total:.3f}")
        for factor, weight in sorted(weights.items(), key=lambda x: x[1], reverse=True):
            print(f"   {factor:15s} {weight:.3f}")
        
        if abs(total - 1.0) > 0.001:
            issues.append(f"❌ {symbol}: Weights sum to {total:.3f}, not 1.0! This will bias predictions!")
        else:
            print(f"✅ {symbol}: Weights sum correctly to 1.0")
    
    return issues


def audit_score_calculation_logic():
    """Audit 2: Check score calculation for conflicts"""
    print("\n" + "="*80)
    print("AUDIT 2: Score Calculation Logic")
    print("="*80)
    
    issues = []
    
    print("\nChecking score calculation formulas:")
    
    # Test case: All positive signals
    print("\n📊 Test Case 1: All Positive Signals")
    test_data = {
        'news': {'overall_score': 0.5},  # 50% bullish
        'futures': {'overall_sentiment': 1.0},  # 1% positive
        'options': {'sentiment': 'bullish'},
        'technical': {'trend': 'uptrend', 'macd_signal': 'bullish'},
        'sector': {'sector_sentiment': 0.01},  # 1% positive
        'reddit': {'sentiment_score': 0.3},
        'institutional': {'signal_strength': 0.2}
    }
    
    weights = get_stock_weight_adjustments('AMD')
    
    # Calculate as system does
    news_score = test_data['news']['overall_score'] * weights['news']
    futures_score = (test_data['futures']['overall_sentiment'] / 100) * weights['futures']
    options_score = weights['options']  # bullish
    technical_score = weights['technical']  # uptrend
    technical_score += weights['technical'] * 0.3  # MACD bullish
    sector_score = test_data['sector']['sector_sentiment'] * weights['sector']
    reddit_score = test_data['reddit']['sentiment_score'] * weights['reddit']
    inst_score = test_data['institutional']['signal_strength'] * weights['institutional']
    
    total = news_score + futures_score + options_score + technical_score + sector_score + reddit_score + inst_score
    
    print(f"   Total Score: {total:+.3f}")
    
    if total < 0:
        issues.append(f"❌ All positive signals resulted in NEGATIVE score {total:.3f}!")
    elif total < 0.05:
        issues.append(f"⚠️ All positive signals only scored {total:.3f}, below UP threshold (0.05)")
    else:
        print(f"   ✅ Correctly scored positive: {total:+.3f}")
    
    # Test case: All negative signals
    print("\n📊 Test Case 2: All Negative Signals")
    test_data_neg = {
        'news': {'overall_score': -0.5},
        'futures': {'overall_sentiment': -1.0},
        'options': {'sentiment': 'bearish'},
        'technical': {'trend': 'downtrend', 'macd_signal': 'bearish'},
        'sector': {'sector_sentiment': -0.01},
        'reddit': {'sentiment_score': -0.3},
        'institutional': {'signal_strength': -0.2}
    }
    
    news_score = test_data_neg['news']['overall_score'] * weights['news']
    futures_score = (test_data_neg['futures']['overall_sentiment'] / 100) * weights['futures']
    options_score = -weights['options']  # bearish
    technical_score = -weights['technical']  # downtrend
    technical_score -= weights['technical'] * 0.3  # MACD bearish
    sector_score = test_data_neg['sector']['sector_sentiment'] * weights['sector']
    reddit_score = test_data_neg['reddit']['sentiment_score'] * weights['reddit']
    inst_score = test_data_neg['institutional']['signal_strength'] * weights['institutional']
    
    total = news_score + futures_score + options_score + technical_score + sector_score + reddit_score + inst_score
    
    print(f"   Total Score: {total:+.3f}")
    
    if total > 0:
        issues.append(f"❌ All negative signals resulted in POSITIVE score {total:.3f}!")
    elif total > -0.05:
        issues.append(f"⚠️ All negative signals only scored {total:.3f}, above DOWN threshold (-0.05)")
    else:
        print(f"   ✅ Correctly scored negative: {total:+.3f}")
    
    return issues


def audit_direction_thresholds():
    """Audit 3: Check direction determination thresholds"""
    print("\n" + "="*80)
    print("AUDIT 3: Direction Threshold Logic")
    print("="*80)
    
    issues = []
    
    print("\nDirection determination thresholds:")
    print("   score > +0.05  → UP")
    print("   score < -0.05  → DOWN")
    print("   else           → NEUTRAL")
    
    # Test edge cases
    test_scores = [
        (0.051, "UP", "Barely above threshold"),
        (0.049, "NEUTRAL", "Just below UP threshold"),
        (-0.051, "DOWN", "Barely below threshold"),
        (-0.049, "NEUTRAL", "Just above DOWN threshold"),
        (0.0, "NEUTRAL", "Exactly zero"),
        (0.05, "NEUTRAL", "Exactly at threshold (not >)"),
        (-0.05, "NEUTRAL", "Exactly at threshold (not <)"),
    ]
    
    for score, expected_dir, desc in test_scores:
        if score > 0.05:
            actual_dir = "UP"
        elif score < -0.05:
            actual_dir = "DOWN"
        else:
            actual_dir = "NEUTRAL"
        
        if actual_dir == expected_dir:
            print(f"   ✅ Score {score:+.3f} → {actual_dir} ({desc})")
        else:
            issues.append(f"❌ Score {score:+.3f} expected {expected_dir} but got {actual_dir}")
            print(f"   ❌ Score {score:+.3f} → {actual_dir} (expected {expected_dir})")
    
    return issues


def audit_confidence_calculation():
    """Audit 4: Check confidence calculation logic"""
    print("\n" + "="*80)
    print("AUDIT 4: Confidence Calculation")
    print("="*80)
    
    issues = []
    
    print("\nConfidence formula: min(60 + abs(total_score) * 120, 88)")
    
    test_cases = [
        (0.05, 66.0),   # Minimum for UP
        (0.10, 72.0),
        (0.20, 84.0),
        (0.30, 88.0),   # Hits max
        (0.50, 88.0),   # Still max
        (-0.05, 66.0),  # Minimum for DOWN
        (-0.20, 84.0),
        (0.0, 50.0),    # NEUTRAL gets 50
    ]
    
    for score, expected_conf in test_cases:
        if abs(score) > 0.05:  # UP or DOWN
            actual_conf = min(60 + abs(score) * 120, 88)
        else:  # NEUTRAL
            actual_conf = 50
        
        if abs(actual_conf - expected_conf) < 0.1:
            print(f"   ✅ Score {score:+.3f} → {actual_conf:.1f}% confidence")
        else:
            issues.append(f"❌ Score {score:+.3f} expected {expected_conf}% but got {actual_conf}%")
            print(f"   ❌ Score {score:+.3f} → {actual_conf:.1f}% (expected {expected_conf}%)")
    
    return issues


def audit_options_scoring():
    """Audit 5: Check options P/C ratio logic"""
    print("\n" + "="*80)
    print("AUDIT 5: Options P/C Ratio Logic")
    print("="*80)
    
    issues = []
    
    print("\nOptions sentiment thresholds:")
    print("   P/C < 0.7  → Bullish (call buying)")
    print("   P/C > 1.3  → Bearish (put buying)")
    print("   else       → Neutral")
    
    test_ratios = [
        (0.5, 'bullish', "Heavy call buying"),
        (0.69, 'bullish', "Just below 0.7"),
        (0.70, 'neutral', "Exactly at threshold"),
        (0.71, 'neutral', "Just above bullish"),
        (1.0, 'neutral', "Balanced"),
        (1.29, 'neutral', "Just below bearish"),
        (1.30, 'neutral', "Exactly at threshold"),
        (1.31, 'bearish', "Just above 1.3"),
        (2.0, 'bearish', "Heavy put buying"),
    ]
    
    for ratio, expected, desc in test_ratios:
        if ratio < 0.7:
            actual = 'bullish'
        elif ratio > 1.3:
            actual = 'bearish'
        else:
            actual = 'neutral'
        
        if actual == expected:
            print(f"   ✅ P/C {ratio:.2f} → {actual} ({desc})")
        else:
            issues.append(f"❌ P/C {ratio:.2f} expected {expected} but got {actual}")
            print(f"   ❌ P/C {ratio:.2f} → {actual} (expected {expected})")
    
    return issues


def audit_technical_scoring_conflict():
    """Audit 6: Check for technical indicator conflicts"""
    print("\n" + "="*80)
    print("AUDIT 6: Technical Indicator Conflicts")
    print("="*80)
    
    issues = []
    
    print("\nChecking for conflicting technical signals:")
    
    # Scenario: Uptrend but bearish MACD
    print("\n   Scenario 1: Uptrend + Bearish MACD")
    weights = get_stock_weight_adjustments('AMD')
    
    # Uptrend gives positive
    uptrend_score = weights['technical']
    # Bearish MACD subtracts
    macd_score = -weights['technical'] * 0.3
    total_tech = uptrend_score + macd_score
    
    print(f"      Uptrend: +{uptrend_score:.3f}")
    print(f"      Bearish MACD: {macd_score:.3f}")
    print(f"      Total: {total_tech:+.3f}")
    
    if total_tech > 0:
        print(f"      ✅ Net positive (uptrend dominates)")
    elif total_tech < 0:
        issues.append(f"❌ Uptrend + Bearish MACD = NEGATIVE score! Logic conflict!")
        print(f"      ❌ Net negative (MACD overrides uptrend - CONFLICT!)")
    
    # Scenario: Downtrend but bullish MACD
    print("\n   Scenario 2: Downtrend + Bullish MACD")
    downtrend_score = -weights['technical']
    macd_bullish = weights['technical'] * 0.3
    total_tech2 = downtrend_score + macd_bullish
    
    print(f"      Downtrend: {downtrend_score:.3f}")
    print(f"      Bullish MACD: +{macd_bullish:.3f}")
    print(f"      Total: {total_tech2:+.3f}")
    
    if total_tech2 < 0:
        print(f"      ✅ Net negative (downtrend dominates)")
    elif total_tech2 > 0:
        issues.append(f"❌ Downtrend + Bullish MACD = POSITIVE score! Logic conflict!")
        print(f"      ❌ Net positive (MACD overrides downtrend - CONFLICT!)")
    
    return issues


def audit_futures_division_error():
    """Audit 7: Check for division by 100 error in futures"""
    print("\n" + "="*80)
    print("AUDIT 7: Futures Scoring Scale")
    print("="*80)
    
    issues = []
    
    print("\nFutures sentiment is divided by 100:")
    print("   Formula: (overall_sentiment / 100) * weight")
    print("   This means futures move of 1% = score of 0.01")
    
    # Check if this makes sense
    weights = get_stock_weight_adjustments('AMD')
    futures_weight = weights['futures']
    
    print(f"\n   Futures weight: {futures_weight:.2f} ({futures_weight*100:.0f}%)")
    print(f"\n   Examples:")
    
    test_moves = [1.0, 2.0, 5.0, -1.0, -2.0]
    for move in test_moves:
        score = (move / 100) * futures_weight
        print(f"      Futures {move:+.1f}% → score {score:+.4f}")
    
    # Compare to other factors
    print(f"\n   Comparison:")
    print(f"      News 50% bullish → score {0.5 * weights['news']:+.4f}")
    print(f"      Futures +1% → score {(1.0/100) * futures_weight:+.4f}")
    
    if (1.0/100) * futures_weight < 0.5 * weights['news']:
        print(f"\n   ⚠️ WARNING: Futures +1% has MUCH less impact than 50% bullish news!")
        print(f"   This might under-weight futures (which are highly predictive)")
        issues.append("⚠️ Futures may be under-weighted compared to news")
    
    return issues


def audit_neutral_zone_trap():
    """Audit 8: Check if system gets stuck in NEUTRAL too often"""
    print("\n" + "="*80)
    print("AUDIT 8: Neutral Zone Analysis")
    print("="*80)
    
    issues = []
    
    print("\nNEUTRAL range: -0.05 to +0.05 (total range: 0.10)")
    print("This is 10% of typical scoring range")
    
    # Simulate mixed signals
    print("\n   Testing mixed signal scenarios:")
    
    scenarios = [
        {
            'name': 'Slight bullish tilt',
            'scores': {'news': 0.01, 'futures': 0.01, 'options': 0, 'technical': 0.02, 
                      'sector': 0, 'reddit': 0, 'institutional': 0},
        },
        {
            'name': 'Balanced conflict',
            'scores': {'news': 0.10, 'futures': 0.01, 'options': 0.15, 'technical': -0.15, 
                      'sector': -0.05, 'reddit': 0.05, 'institutional': -0.01},
        },
    ]
    
    for scenario in scenarios:
        total = sum(scenario['scores'].values())
        if total > 0.05:
            direction = "UP"
        elif total < -0.05:
            direction = "DOWN"
        else:
            direction = "NEUTRAL"
        
        print(f"\n   {scenario['name']}:")
        print(f"      Total: {total:+.3f} → {direction}")
        
        if direction == "NEUTRAL" and abs(total) > 0.03:
            issues.append(f"⚠️ Score {total:+.3f} is NEUTRAL but has clear lean")
    
    return issues


def audit_data_api_fallbacks():
    """Audit 9: Check data API fallback behavior"""
    print("\n" + "="*80)
    print("AUDIT 9: API Fallback Behavior")
    print("="*80)
    
    issues = []
    
    print("\nWhen APIs fail, system uses neutral defaults:")
    print("   News: 0.0 (neutral)")
    print("   Options: 'neutral'")
    print("   Technical: RSI 50, neutral")
    print("   Futures: 0.0%")
    
    print("\n   ⚠️ RISK: If multiple APIs fail, system defaults to NEUTRAL")
    print("   ⚠️ This could give false confidence in NEUTRAL predictions")
    
    # Test all-neutral scenario
    weights = get_stock_weight_adjustments('AMD')
    all_neutral_score = 0.0  # All factors at zero
    
    print(f"\n   All APIs fail → Total score: {all_neutral_score:.3f} → NEUTRAL")
    print(f"   Confidence: 50% (but based on NO DATA!)")
    
    issues.append("⚠️ WARNING: System cannot distinguish between:")
    issues.append("   - True market neutral (conflicting real signals)")
    issues.append("   - False neutral (API failures, no data)")
    issues.append("   RECOMMENDATION: Add data quality score to confidence calculation")
    
    return issues


def run_deep_audit():
    """Run complete deep audit"""
    print("\n" + "="*80)
    print("🔍 DEEP SYSTEM AUDIT")
    print("Checking for logic conflicts, mismatches, and prediction errors")
    print("="*80)
    
    all_issues = []
    
    audits = [
        ("Weight Totals", audit_weight_totals),
        ("Score Calculation Logic", audit_score_calculation_logic),
        ("Direction Thresholds", audit_direction_thresholds),
        ("Confidence Calculation", audit_confidence_calculation),
        ("Options P/C Logic", audit_options_scoring),
        ("Technical Conflicts", audit_technical_scoring_conflict),
        ("Futures Scaling", audit_futures_division_error),
        ("Neutral Zone", audit_neutral_zone_trap),
        ("API Fallbacks", audit_data_api_fallbacks),
    ]
    
    for name, audit_func in audits:
        try:
            issues = audit_func()
            if issues:
                all_issues.extend(issues)
        except Exception as e:
            print(f"\n❌ AUDIT FAILED: {name}")
            print(f"   Error: {e}")
            import traceback
            traceback.print_exc()
            all_issues.append(f"❌ Audit '{name}' crashed: {e}")
    
    # Summary
    print("\n" + "="*80)
    print("AUDIT SUMMARY")
    print("="*80)
    
    if all_issues:
        print(f"\n⚠️ FOUND {len(all_issues)} POTENTIAL ISSUES:\n")
        for i, issue in enumerate(all_issues, 1):
            print(f"{i}. {issue}")
        print("\n" + "="*80)
        print("⚠️ REVIEW AND FIX ISSUES BEFORE TRADING!")
        print("="*80)
        return False
    else:
        print("\n✅ NO CRITICAL ISSUES FOUND")
        print("System logic appears sound")
        print("="*80)
        return True


if __name__ == "__main__":
    success = run_deep_audit()
    sys.exit(0 if success else 1)
