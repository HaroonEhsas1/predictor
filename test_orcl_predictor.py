#!/usr/bin/env python3
"""
ORCL Stock Prediction Test Engine
Simple test to predict if ORCL will go UP or DOWN tomorrow
Similar to AMD and AVGO predictions
"""

import sys
from pathlib import Path
from datetime import datetime
import pytz

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from comprehensive_nextday_predictor import ComprehensiveNextDayPredictor
from stock_config import get_stock_config

def test_orcl_prediction():
    """
    Test ORCL prediction and display results
    """
    print("="*80)
    print("🧪 ORACLE (ORCL) STOCK PREDICTION TEST ENGINE")
    print("="*80)
    
    # Get ORCL configuration
    print("\n📊 ORCL Configuration:")
    config = get_stock_config('ORCL')
    print(f"   Name: {config['name']}")
    print(f"   Sector: {config['sector_etf']} (Technology)")
    print(f"   Typical Volatility: {config['typical_volatility']*100:.2f}%")
    print(f"   Avg Gap Size: {config['historical_avg_gap']*100:.2f}%")
    print(f"   Min Confidence: {config['min_confidence_threshold']*100:.0f}%")
    print(f"   Momentum Continuation: {config['momentum_continuation_rate']*100:.0f}%")
    print(f"   Competitors: {', '.join(config['competitors'])}")
    
    # Show current time
    et_tz = pytz.timezone('US/Eastern')
    now_et = datetime.now(et_tz)
    print(f"\n🕐 Current Time: {now_et.strftime('%Y-%m-%d %I:%M:%S %p ET')}")
    print(f"   Day: {now_et.strftime('%A')}")
    
    # Run prediction
    print("\n" + "="*80)
    print("🎯 RUNNING ORCL PREDICTION...")
    print("="*80)
    print("\n⏳ Fetching data (this may take 15-30 seconds)...\n")
    
    try:
        # Initialize predictor for ORCL
        predictor = ComprehensiveNextDayPredictor(symbol='ORCL')
        
        # Generate prediction
        prediction = predictor.generate_comprehensive_prediction()
        
        if not prediction:
            print("\n❌ ERROR: Failed to generate ORCL prediction")
            print("   Check your API keys and internet connection")
            return False
        
        # Display results
        print("\n" + "="*80)
        print("📈 ORCL PREDICTION RESULTS")
        print("="*80)
        
        direction = prediction['direction']
        confidence = prediction['confidence']
        current_price = prediction['current_price']
        target_price = prediction['target_price']
        
        # Direction indicator
        if direction == 'UP':
            direction_emoji = "📈 🟢"
            arrow = "↗️"
        else:
            direction_emoji = "📉 🔴"
            arrow = "↘️"
        
        print(f"\n   {direction_emoji} PREDICTED DIRECTION: {direction} {arrow}")
        print(f"\n   💪 CONFIDENCE: {confidence:.1f}%")
        print(f"   💵 CURRENT PRICE: ${current_price:.2f}")
        print(f"   🎯 TARGET PRICE: ${target_price:.2f}")
        
        # Calculate expected move
        price_diff = target_price - current_price
        move_pct = (price_diff / current_price) * 100
        
        print(f"\n   📊 EXPECTED MOVE:")
        print(f"      Dollar Change: ${abs(price_diff):.2f}")
        print(f"      Percent Change: {abs(move_pct):.2f}%")
        
        # Confidence interpretation
        print(f"\n   🎓 INTERPRETATION:")
        if confidence >= 70:
            print(f"      ✅ HIGH confidence - Strong prediction")
        elif confidence >= config['min_confidence_threshold'] * 100:
            print(f"      ✅ MODERATE confidence - Acceptable prediction")
        else:
            print(f"      ⚠️ LOW confidence - Below threshold ({config['min_confidence_threshold']*100:.0f}%)")
        
        # Key factors
        print(f"\n   🔑 TOP CONTRIBUTING FACTORS:")
        if 'factors' in prediction and prediction['factors']:
            for i, (factor, score) in enumerate(prediction['factors'][:5], 1):
                print(f"      {i}. {factor}: {score:.1f}%")
        
        # Reasoning summary
        if 'reasoning' in prediction and prediction['reasoning']:
            print(f"\n   💡 KEY REASONING:")
            for i, reason in enumerate(prediction['reasoning'][:3], 1):
                print(f"      {i}. {reason}")
        
        print("\n" + "="*80)
        print("✅ ORCL PREDICTION TEST COMPLETED SUCCESSFULLY")
        print("="*80)
        
        # Summary
        print(f"\n📝 SUMMARY:")
        print(f"   If you buy ORCL now at ${current_price:.2f},")
        print(f"   the system predicts it will {direction} to ${target_price:.2f}")
        print(f"   by tomorrow with {confidence:.1f}% confidence.")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR during prediction: {e}")
        import traceback
        traceback.print_exc()
        return False


def compare_with_amd_avgo():
    """
    Quick comparison of ORCL vs AMD vs AVGO
    """
    print("\n\n" + "="*80)
    print("📊 MULTI-STOCK COMPARISON (Optional)")
    print("="*80)
    
    stocks = ['AMD', 'AVGO', 'ORCL']
    print("\nWould you like to compare ORCL with AMD and AVGO predictions?")
    print("This will take 1-2 minutes to run all three stocks.")
    
    response = input("\nRun comparison? (y/n): ").lower().strip()
    
    if response == 'y':
        print("\n⏳ Running predictions for AMD, AVGO, and ORCL...\n")
        
        from multi_stock_predictor import run_multi_stock_prediction
        
        results = run_multi_stock_prediction(stocks=stocks, apply_filters=False, apply_safeguard=False)
        
        if results and 'stocks' in results:
            print("\n" + "="*80)
            print("📊 MULTI-STOCK COMPARISON RESULTS")
            print("="*80)
            
            for symbol, pred in results['stocks'].items():
                if pred and not pred.get('error'):
                    direction = pred['direction']
                    confidence = pred['confidence']
                    
                    emoji = "📈 🟢" if direction == 'UP' else "📉 🔴"
                    print(f"\n   {symbol:5} {emoji} {direction:4} - Confidence: {confidence:.1f}%")
            
            print("\n" + "="*80)
    else:
        print("\n   Skipping comparison. You can run multi_stock_predictor.py later for comparisons.")


if __name__ == "__main__":
    print("\n")
    
    # Run ORCL prediction test
    success = test_orcl_prediction()
    
    if success:
        # Optional: Compare with other stocks
        # compare_with_amd_avgo()  # Uncomment this line to enable comparison prompt
        pass
    
    print("\n")
