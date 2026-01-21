"""
Premarket Gap Confirmation Script
Run at 6:00 AM to check if gaps confirm yesterday's predictions
Helps decide: ADD position, HOLD, or EXIT
"""

import yfinance as yf
import json
from datetime import datetime, timedelta
import os

def check_premarket_gaps():
    """Check premarket gaps vs yesterday's predictions"""
    
    print("="*80)
    print("🌅 PREMARKET GAP CONFIRMATION CHECK")
    print("="*80)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %I:%M %p')}\n")
    
    # Find most recent prediction file
    data_dir = 'data/multi_stock'
    prediction_files = [f for f in os.listdir(data_dir) if f.startswith('predictions_') and f.endswith('.json')]
    
    if not prediction_files:
        print("❌ No prediction files found!")
        return
    
    # Get most recent file
    latest_file = sorted(prediction_files)[-1]
    filepath = os.path.join(data_dir, latest_file)
    
    print(f"📁 Loading predictions from: {latest_file}\n")
    
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    predictions = data.get('predictions', {})
    prediction_time = data.get('timestamp', 'Unknown')
    
    print(f"⏰ Predictions made: {prediction_time}")
    print("="*80)
    
    for symbol in predictions.keys():
        pred = predictions[symbol]
        
        print(f"\n{'='*80}")
        print(f"  {symbol}")
        print(f"{'='*80}")
        
        # Get prediction details
        pred_direction = pred['direction']
        pred_confidence = pred['confidence']
        pred_target = pred['target_price']
        pred_close = pred['current_price']
        
        print(f"\n📊 YESTERDAY'S PREDICTION:")
        print(f"   Direction: {pred_direction} {'⬆️' if pred_direction == 'UP' else '⬇️' if pred_direction == 'DOWN' else '➡️'}")
        print(f"   Confidence: {pred_confidence:.2f}%")
        print(f"   Entry Price (close): ${pred_close:.2f}")
        print(f"   Target: ${pred_target:.2f}")
        print(f"   Expected Move: {pred['expected_move_pct']:+.2f}%")
        
        # Get current premarket price
        try:
            stock = yf.Ticker(symbol)
            
            # Get premarket price (may not be available for all stocks)
            info = stock.info
            premarket_price = info.get('preMarketPrice')
            
            if premarket_price:
                premarket_price = float(premarket_price)
                gap_amount = premarket_price - pred_close
                gap_pct = (gap_amount / pred_close) * 100
                
                print(f"\n📈 PREMARKET STATUS:")
                print(f"   Premarket Price: ${premarket_price:.2f}")
                print(f"   Gap: ${gap_amount:+.2f} ({gap_pct:+.2f}%)")
                
                # Determine gap direction
                if abs(gap_pct) < 0.3:
                    gap_direction = 'NEUTRAL'
                    gap_emoji = '➡️'
                elif gap_pct > 0:
                    gap_direction = 'UP'
                    gap_emoji = '⬆️'
                else:
                    gap_direction = 'DOWN'
                    gap_emoji = '⬇️'
                
                print(f"   Gap Direction: {gap_direction} {gap_emoji}")
                
                # Check if prediction matches gap
                prediction_correct = (pred_direction == gap_direction) or (gap_direction == 'NEUTRAL')
                
                # Calculate progress toward target
                if pred_direction == 'UP':
                    progress_pct = (gap_pct / pred['expected_move_pct']) * 100 if pred['expected_move_pct'] > 0 else 0
                    target_hit = premarket_price >= pred_target
                elif pred_direction == 'DOWN':
                    progress_pct = (abs(gap_pct) / abs(pred['expected_move_pct'])) * 100 if pred['expected_move_pct'] < 0 else 0
                    target_hit = premarket_price <= pred_target
                else:
                    progress_pct = 0
                    target_hit = False
                
                print(f"   Progress to Target: {progress_pct:.1f}%")
                if target_hit:
                    print(f"   ✅ TARGET HIT!")
                
                # DECISION LOGIC
                print(f"\n🎯 RECOMMENDATION:")
                
                # Classify position based on original confidence
                if pred_confidence >= 70:
                    position_type = "FULL (100%)"
                elif pred_confidence >= 60:
                    position_type = "PARTIAL (50%)"
                else:
                    position_type = "NONE (Filtered)"
                
                print(f"   Position Type: {position_type}")
                
                # Decision for FULL positions
                if pred_confidence >= 70:
                    if target_hit:
                        print(f"   ✅ **EXIT NOW** - Target hit, take profit!")
                        print(f"      Profit: {gap_pct:+.2f}%")
                    elif prediction_correct and abs(gap_pct) > 0.5:
                        print(f"   ✅ **HOLD** - Gap confirms prediction, moving toward target")
                        print(f"      Current profit: {gap_pct:+.2f}%")
                    elif gap_direction != pred_direction and abs(gap_pct) > 0.5:
                        print(f"   ⚠️ **EXIT IMMEDIATELY** - Gap contradicts prediction!")
                        print(f"      Cut loss: {gap_pct:+.2f}%")
                    else:
                        print(f"   ⏸️ **HOLD & MONITOR** - Small gap, wait for market open")
                
                # Decision for PARTIAL positions (50%)
                elif pred_confidence >= 60:
                    if target_hit:
                        print(f"   ✅ **EXIT 50%** - Target hit on initial position")
                        print(f"      Profit on 50%: {gap_pct:+.2f}%")
                    elif prediction_correct and abs(gap_pct) > 0.5:
                        print(f"   ✅ **ADD 50% MORE** - Gap confirms prediction!")
                        print(f"      Gap: {gap_pct:+.2f}% in correct direction")
                        print(f"      Increase to 100% position")
                    elif gap_direction != pred_direction and abs(gap_pct) > 0.5:
                        print(f"   ❌ **EXIT 50%** - Gap contradicts prediction")
                        print(f"      Cut loss on 50%: {gap_pct:+.2f}%")
                    else:
                        print(f"   ⏸️ **HOLD 50%** - Neutral gap, don't add")
                        print(f"      Wait for market open momentum")
                
                # No position (filtered)
                else:
                    print(f"   ✅ **GOOD FILTER** - Trade was correctly skipped")
                    if abs(gap_pct) > 0.5:
                        if gap_direction == pred_direction:
                            print(f"      Note: Would have been profitable ({gap_pct:+.2f}%)")
                        else:
                            print(f"      Note: Filter saved from loss ({gap_pct:+.2f}%)")
                
            else:
                # No premarket price available
                print(f"\n📈 PREMARKET STATUS:")
                print(f"   ⚠️ Premarket price not available yet")
                print(f"   Check again at 7:00 AM or wait for market open")
                
                print(f"\n🎯 RECOMMENDATION:")
                if pred_confidence >= 70:
                    print(f"   ⏸️ **HOLD** - Full position, monitor at 7 AM")
                elif pred_confidence >= 60:
                    print(f"   ⏸️ **HOLD 50%** - Wait for premarket data before adding")
                else:
                    print(f"   ✅ Trade was filtered (low confidence)")
        
        except Exception as e:
            print(f"\n❌ Error getting premarket data: {e}")
            print(f"   Try again in a few minutes")
    
    print(f"\n{'='*80}")
    print("💡 GENERAL TIPS:")
    print("="*80)
    print("1. Exit ALL positions by 10:00 AM (hard stop)")
    print("2. If gap hits 80%+ of target, consider taking profit")
    print("3. If gap contradicts by >1%, exit immediately")
    print("4. Use limit orders in premarket (avoid market orders)")
    print("5. Premarket spreads are 0.10-0.20% - factor into decision")
    print("="*80)

if __name__ == "__main__":
    check_premarket_gaps()
