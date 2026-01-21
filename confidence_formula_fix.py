#!/usr/bin/env python3
"""
Confidence Formula Fix - Corrects zero-score confidence issue

Issue: Score +0.00 gives 65% confidence (should be ~50%)
Fix: Adjust base confidence to scale from 50% for neutral signals

Created: October 23, 2025
"""

def old_confidence_formula(score):
    """
    OLD FORMULA (Has bias issue)
    """
    if abs(score) < 0.15:
        confidence = 65 + abs(score) * 285
    else:
        confidence = 88 + (abs(score) - 0.15) * 70
    
    return min(confidence, 95)


def new_confidence_formula(score):
    """
    NEW FORMULA (Fixed)
    
    Changes:
    - Zero score → 50% confidence (coin flip, not 65%)
    - Small scores → 50-65% (appropriately cautious)
    - Medium scores → 65-85% (reasonable confidence)
    - Large scores → 85-95% (high confidence)
    """
    
    # Handle truly neutral case
    if abs(score) < 0.01:
        return 50.0  # Pure neutral = coin flip
    
    # Piecewise formula starting from 50% base
    if abs(score) < 0.15:
        # Scale from 50% to 85% for scores 0.01 to 0.15
        confidence = 50 + abs(score) * 233  # (85-50)/0.15 = 233
    else:
        # Scale from 85% to 95% for scores 0.15+
        confidence = 85 + (abs(score) - 0.15) * 67  # (95-85)/0.15 = 67
    
    return min(confidence, 95)


def compare_formulas():
    """
    Compare old vs new formulas
    """
    
    print("\n" + "="*80)
    print("🔧 CONFIDENCE FORMULA COMPARISON")
    print("="*80)
    
    test_scores = [0.00, 0.01, 0.02, 0.03, 0.05, 0.08, 0.10, 0.15, 0.20, 0.30]
    
    print(f"\n{'Score':>8} {'Old Formula':>15} {'New Formula':>15} {'Change':>10}")
    print("─"*80)
    
    for score in test_scores:
        old_conf = old_confidence_formula(score)
        new_conf = new_confidence_formula(score)
        change = new_conf - old_conf
        
        print(f"{score:>8.2f} {old_conf:>14.1f}% {new_conf:>14.1f}% {change:>9.1f}%")
    
    print("\n✅ KEY IMPROVEMENTS:")
    print("   • Zero score: 65% → 50% (honest neutral)")
    print("   • Small scores: Reduced to appropriate levels")
    print("   • Large scores: Still reach 85-95% (maintains edge)")
    
    print("\n📊 RESULT:")
    print("   Formula is now HONEST for neutral signals")
    print("   No artificial confidence for zero scores")


def generate_fixed_code():
    """
    Generate the fixed code snippet to use
    """
    
    print("\n" + "="*80)
    print("📝 FIXED CODE TO IMPLEMENT")
    print("="*80)
    
    code = '''
def calculate_confidence(score, direction):
    """
    Calculate confidence with FIXED formula (no zero-score bias)
    
    Args:
        score: Total prediction score
        direction: UP, DOWN, or NEUTRAL
    
    Returns:
        float: Confidence percentage (50-95%)
    """
    
    # CRITICAL FIX: Handle truly neutral case
    if abs(score) < 0.01:
        # Pure neutral = coin flip confidence
        return 50.0
    
    # For directional signals, use piecewise formula
    if direction in ['UP', 'DOWN']:
        if abs(score) < 0.15:
            # Scale from 50% to 85% for scores 0.01-0.15
            confidence_base = 50 + abs(score) * 233
        else:
            # Scale from 85% to 95% for scores 0.15+
            confidence_base = 85 + (abs(score) - 0.15) * 67
    else:
        # NEUTRAL direction (score near zero but not directional)
        confidence_base = 45 + abs(score) * 200
    
    # Cap at 95% (admit uncertainty)
    confidence = min(confidence_base, 95)
    
    return confidence


# USAGE EXAMPLE:
score = 0.087
direction = "UP"
confidence = calculate_confidence(score, direction)
print(f"Score: {score:+.3f}, Direction: {direction}, Confidence: {confidence:.1f}%")
# Output: Score: +0.087, Direction: UP, Confidence: 70.3%
'''
    
    print(code)
    print("\n✅ Copy this code to replace old confidence calculation")


if __name__ == "__main__":
    compare_formulas()
    generate_fixed_code()
    
    print("\n" + "="*80)
    print("✅ FIX COMPLETE")
    print("="*80)
    print("\nThe confidence formula has been corrected:")
    print("• Zero score now gives 50% confidence (honest neutral)")
    print("• Formula maintains high confidence for strong signals")
    print("• No artificial inflation for weak/neutral signals")
    print("\nImplement the fixed code above in your predictor!")
    print("="*80 + "\n")
