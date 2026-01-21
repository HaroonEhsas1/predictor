#!/usr/bin/env python3
"""
Check Tuesday October 21, 2025 Results
Compare to Monday's overnight predictions
"""

import yfinance as yf
from datetime import datetime

def check_tuesday_results():
    """Check actual results vs Monday's predictions"""
    
    print("\n" + "="*80)
    print("📊 TUESDAY, OCTOBER 21, 2025 - PREDICTION RESULTS")
    print("="*80)
    print("⏰ Checking results vs Monday evening predictions...")
    
    # Monday's predictions (from enhanced_multi_stock_predictor.py output)
    predictions = {
        'AMD': {
            'direction': 'UP',
            'confidence': 88.0,
            'entry': 240.99,
            'target': 247.39,
            'expected_move': 6.40,
            'expected_pct': 2.66
        },
        'AVGO': {
            'direction': 'UP',
            'confidence': 88.0,
            'entry': 349.69,
            'target': 357.55,
            'expected_move': 7.86,
            'expected_pct': 2.25
        },
        'ORCL': {
            'direction': 'DOWN',
            'confidence': 71.6,
            'entry': 277.35,
            'target': 272.00,
            'expected_move': -5.35,
            'expected_pct': -1.93
        }
    }
    
    results = {}
    
    for symbol, pred in predictions.items():
        print(f"\n{'='*80}")
        print(f"📈 {symbol}")
        print(f"{'='*80}")
        
        # Fetch today's data
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="2d")
        
        if len(hist) < 2:
            print(f"⚠️ Not enough data for {symbol}")
            continue
        
        # Get Monday's close (entry price)
        monday_close = float(hist['Close'].iloc[-2])
        
        # Get Tuesday's data
        tuesday_open = float(hist['Open'].iloc[-1])
        tuesday_high = float(hist['High'].iloc[-1])
        tuesday_low = float(hist['Low'].iloc[-1])
        tuesday_close = float(hist['Close'].iloc[-1])
        
        # Get current price
        info = ticker.info
        current_price = info.get('currentPrice') or info.get('regularMarketPrice') or tuesday_close
        current_price = float(current_price)
        
        # Calculate actual moves
        actual_move = current_price - monday_close
        actual_pct = (actual_move / monday_close) * 100
        high_move = tuesday_high - monday_close
        high_pct = (high_move / monday_close) * 100
        low_move = tuesday_low - monday_close
        low_pct = (low_move / monday_close) * 100
        
        # Print prediction
        print(f"\n📋 PREDICTION (Monday 3:55 PM):")
        print(f"   Direction: {pred['direction']}")
        print(f"   Confidence: {pred['confidence']}%")
        print(f"   Entry: ${pred['entry']:.2f}")
        print(f"   Target: ${pred['target']:.2f}")
        print(f"   Expected: {pred['expected_move']:+.2f} ({pred['expected_pct']:+.2f}%)")
        
        # Print actual results
        print(f"\n📊 ACTUAL RESULTS (Tuesday):")
        print(f"   Monday Close: ${monday_close:.2f}")
        print(f"   Tuesday Open: ${tuesday_open:.2f} ({((tuesday_open-monday_close)/monday_close)*100:+.2f}%)")
        print(f"   Today's High: ${tuesday_high:.2f} ({high_pct:+.2f}%)")
        print(f"   Today's Low:  ${tuesday_low:.2f} ({low_pct:+.2f}%)")
        print(f"   Current:      ${current_price:.2f} ({actual_pct:+.2f}%)")
        
        # Check if target hit
        if pred['direction'] == 'UP':
            target_hit = tuesday_high >= pred['target']
            direction_correct = actual_move > 0
        else:  # DOWN
            target_hit = tuesday_low <= pred['target']
            direction_correct = actual_move < 0
        
        # Verdict
        print(f"\n✅ VERDICT:")
        print(f"   Direction Predicted: {pred['direction']}")
        print(f"   Direction Actual: {'UP' if actual_move > 0 else 'DOWN' if actual_move < 0 else 'FLAT'}")
        print(f"   Direction Correct? {'✅ YES' if direction_correct else '❌ NO'}")
        print(f"   Target: ${pred['target']:.2f}")
        print(f"   Target Hit? {'✅ YES' if target_hit else '❌ NO'}")
        
        if target_hit:
            if pred['direction'] == 'UP':
                print(f"   🎯 TARGET HIT! High: ${tuesday_high:.2f} vs Target: ${pred['target']:.2f}")
            else:
                print(f"   🎯 TARGET HIT! Low: ${tuesday_low:.2f} vs Target: ${pred['target']:.2f}")
        else:
            if pred['direction'] == 'UP':
                distance = pred['target'] - tuesday_high
                print(f"   📊 Missed by: ${abs(distance):.2f} (High: ${tuesday_high:.2f})")
            else:
                distance = tuesday_low - pred['target']
                print(f"   📊 Missed by: ${abs(distance):.2f} (Low: ${tuesday_low:.2f})")
        
        # Calculate profit/loss (using adjusted position sizes)
        if symbol == 'AMD':
            shares = 43  # Adjusted from 40
        elif symbol == 'AVGO':
            shares = 16  # Adjusted from 15
        else:  # ORCL
            shares = 19  # Adjusted from 20 (SHORT)
        
        if target_hit:
            profit = pred['expected_move'] * shares
        else:
            if pred['direction'] == 'DOWN':
                profit = -actual_move * shares  # SHORT position
            else:
                profit = actual_move * shares
        
        print(f"\n💰 P/L (if traded {shares} shares):")
        print(f"   Expected P/L: ${pred['expected_move'] * shares:+.2f}")
        print(f"   Actual P/L: ${profit:+.2f}")
        
        results[symbol] = {
            'direction_correct': direction_correct,
            'target_hit': target_hit,
            'profit': profit,
            'actual_pct': actual_pct
        }
    
    # Summary
    print(f"\n{'='*80}")
    print(f"📊 OVERALL SUMMARY")
    print(f"{'='*80}")
    
    total_correct = sum(1 for r in results.values() if r['direction_correct'])
    total_targets = sum(1 for r in results.values() if r['target_hit'])
    total_profit = sum(r['profit'] for r in results.values())
    
    print(f"\n✅ ACCURACY:")
    print(f"   Direction Correct: {total_correct}/3 ({total_correct/3*100:.0f}%)")
    print(f"   Targets Hit: {total_targets}/3 ({total_targets/3*100:.0f}%)")
    
    print(f"\n💰 PROFITABILITY:")
    print(f"   Total P/L: ${total_profit:+.2f}")
    if total_profit > 0:
        print(f"   Result: 🎉 PROFITABLE!")
    else:
        print(f"   Result: ⚠️ Loss")
    
    print(f"\n🎯 SYSTEM PERFORMANCE:")
    if total_correct >= 2:
        print(f"   ✅ GOOD - System predicted correctly")
    else:
        print(f"   ⚠️ NEEDS REVIEW - Less than 67% accuracy")
    
    if total_targets >= 2:
        print(f"   ✅ EXCELLENT - Targets were realistic")
    elif total_targets == 1:
        print(f"   ⚠️ MODERATE - Some targets too aggressive")
    else:
        print(f"   ❌ POOR - Targets need adjustment")
    
    # Two-day performance
    print(f"\n📈 TWO-DAY PERFORMANCE:")
    print(f"   Monday: 3/3 targets hit (100%)")
    print(f"   Tuesday: {total_targets}/3 targets hit ({total_targets/3*100:.0f}%)")
    print(f"   Combined: {3+total_targets}/6 ({(3+total_targets)/6*100:.0f}%)")
    
    print(f"\n{'='*80}\n")
    
    return results

if __name__ == "__main__":
    check_tuesday_results()
