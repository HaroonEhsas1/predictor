"""
Professional Trader System - Bias Validation Test
Tests for random selection issues and signal strength problems
"""

import logging
from professional_trader_system import ProfessionalTraderSystem
from datetime import datetime
import time
from collections import Counter

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

def run_professional_trader_bias_test(num_runs: int = 15):
    """
    Run multiple predictions and check for:
    1. Random selection when signals are equal (the critical bug)
    2. UP vs DOWN bias
    3. Signal strength distribution
    4. Zero signal strength occurrences
    """
    print("=" * 80)
    print("🔍 PROFESSIONAL TRADER SYSTEM - BIAS & RANDOM SELECTION TEST")
    print(f"Running {num_runs} predictions to detect issues...")
    print("=" * 80 + "\n")
    
    system = ProfessionalTraderSystem(symbol="AMD")
    
    predictions = []
    random_selections = 0
    zero_strength_cases = 0
    
    print(f"Gathering {num_runs} predictions...\n")
    
    for i in range(num_runs):
        print(f"\n{'='*60}")
        print(f"Prediction {i+1}/{num_runs}")
        print('='*60)
        
        try:
            # Make prediction with real data
            prediction = system.predict_direction()
            
            # Store prediction details
            pred_data = {
                'direction': prediction['direction'],
                'confidence': prediction['confidence'],
                'reasoning': prediction.get('reasoning', [])
            }
            predictions.append(pred_data)
            
            # Check for random selection indicator
            reasoning_text = ' '.join(pred_data['reasoning'])
            if '[BALANCED] Equal signal strength - random selection' in reasoning_text:
                random_selections += 1
                print("⚠️  RANDOM SELECTION DETECTED!")
            
            # Check for zero signal strength
            if 'UP strength=0.0, DOWN strength=0.0' in reasoning_text:
                zero_strength_cases += 1
                print("⚠️  ZERO SIGNAL STRENGTH DETECTED!")
            
            print(f"✓ {prediction['direction']} (confidence: {prediction['confidence']:.1f}%)")
            
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
        
        # Small delay to avoid rate limits and allow data variation
        if i < num_runs - 1:
            time.sleep(3)
    
    # Analysis
    print("\n" + "=" * 80)
    print("📊 CRITICAL ISSUES ANALYSIS")
    print("=" * 80 + "\n")
    
    print("🎲 RANDOM SELECTION ISSUE:")
    print(f"   Random selections: {random_selections}/{num_runs} ({random_selections/num_runs*100:.1f}%)")
    if random_selections > 0:
        print("   ⚠️  CRITICAL: System is using coin flips instead of real analysis!")
        print("   ⚠️  This means signals are equal or both zero - not real prediction")
    else:
        print("   ✅ No random selections detected")
    
    print(f"\n📉 ZERO SIGNAL STRENGTH ISSUE:")
    print(f"   Zero strength cases: {zero_strength_cases}/{num_runs} ({zero_strength_cases/num_runs*100:.1f}%)")
    if zero_strength_cases > 0:
        print("   ⚠️  CRITICAL: Indicators are not detecting any signals!")
        print("   ⚠️  This suggests data collection or analysis problems")
    else:
        print("   ✅ All predictions have signal strength")
    
    # Direction distribution
    print("\n" + "=" * 80)
    print("📊 DIRECTION DISTRIBUTION")
    print("=" * 80 + "\n")
    
    directions = [p['direction'] for p in predictions]
    direction_counts = Counter(directions)
    
    total = len(predictions)
    up_count = direction_counts.get('UP', 0)
    down_count = direction_counts.get('DOWN', 0)
    hold_count = direction_counts.get('HOLD', 0)
    
    print(f"Total Predictions: {total}")
    print(f"  UP:   {up_count} ({up_count/total*100:.1f}%)")
    print(f"  DOWN: {down_count} ({down_count/total*100:.1f}%)")
    print(f"  HOLD: {hold_count} ({hold_count/total*100:.1f}%)")
    
    # Bias detection
    print("\n" + "-" * 80)
    
    bias_threshold = 0.70  # 70% threshold for bias
    
    if up_count / total > bias_threshold:
        print("⚠️  WARNING: System shows UP BIAS")
        print(f"   {up_count/total*100:.1f}% of predictions are UP")
        bias_detected = True
    elif down_count / total > bias_threshold:
        print("⚠️  WARNING: System shows DOWN BIAS")
        print(f"   {down_count/total*100:.1f}% of predictions are DOWN")
        bias_detected = True
    else:
        print("✅ Direction distribution is balanced")
        bias_detected = False
    
    # Confidence analysis
    print("\n" + "=" * 80)
    print("📊 CONFIDENCE ANALYSIS")
    print("=" * 80 + "\n")
    
    confidences = [p['confidence'] for p in predictions]
    avg_confidence = sum(confidences) / len(confidences)
    min_confidence = min(confidences)
    max_confidence = max(confidences)
    
    print(f"Average Confidence: {avg_confidence:.1f}%")
    print(f"Min Confidence: {min_confidence:.1f}%")
    print(f"Max Confidence: {max_confidence:.1f}%")
    
    low_confidence_count = sum(1 for c in confidences if c < 40)
    print(f"Low Confidence (<40%): {low_confidence_count}/{total} ({low_confidence_count/total*100:.1f}%)")
    
    # Final verdict
    print("\n" + "=" * 80)
    print("FINAL VERDICT")
    print("=" * 80 + "\n")
    
    critical_issues = []
    
    if random_selections > 0:
        critical_issues.append(f"Random selection used in {random_selections} predictions (COIN FLIP!)")
    
    if zero_strength_cases > 0:
        critical_issues.append(f"Zero signal strength in {zero_strength_cases} predictions (NO ANALYSIS!)")
    
    if bias_detected:
        critical_issues.append("Directional bias detected")
    
    if low_confidence_count / total > 0.5:
        critical_issues.append("Majority of predictions have low confidence (<40%)")
    
    if critical_issues:
        print("❌ CRITICAL ISSUES FOUND:\n")
        for i, issue in enumerate(critical_issues, 1):
            print(f"   {i}. {issue}")
        print("\n🔧 FIXES NEEDED:")
        print("   1. Fix data collection to ensure proper indicator values")
        print("   2. Require minimum signal strength threshold")
        print("   3. Return HOLD instead of random UP/DOWN when signals are weak")
        print("   4. Enhance DOWN-trend detection indicators")
        test_passed = False
    else:
        print("✅ ALL CHECKS PASSED")
        print("   System is working correctly with real signals")
        print("   No random selections or zero-strength issues")
        test_passed = True
    
    print("\n" + "=" * 80 + "\n")
    
    return test_passed


if __name__ == "__main__":
    try:
        print("\n🚀 Starting Professional Trader System Bias Test\n")
        passed = run_professional_trader_bias_test(num_runs=15)
        
        if passed:
            print("✅ Test PASSED - System is working correctly")
            exit(0)
        else:
            print("❌ Test FAILED - Critical issues detected")
            exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
