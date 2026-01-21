#!/usr/bin/env python3
"""
Check Prediction Results for Monday, October 20, 2025
Compare predicted targets vs actual stock performance
"""

import yfinance as yf
from datetime import datetime
import pytz

def check_results():
    """Check actual results vs predictions"""
    
    print("\n" + "="*80)
    print("📊 MONDAY, OCTOBER 20, 2025 - PREDICTION RESULTS")
    print("="*80)
    
    et_tz = pytz.timezone('US/Eastern')
    now_et = datetime.now(et_tz)
    print(f"⏰ Current Time: {now_et.strftime('%I:%M %p ET')}")
    
    # Our predictions from Sunday
    predictions = {
        'AMD': {
            'direction': 'UP',
            'confidence': 84.3,
            'entry': 233.08,
            'target': 238.60,
            'expected_move': 5.52,
            'expected_pct': 2.37
        },
        'AVGO': {
            'direction': 'UP',
            'confidence': 83.3,
            'entry': 349.33,
            'target': 356.34,
            'expected_move': 7.01,
            'expected_pct': 2.01
        },
        'ORCL': {
            'direction': 'DOWN',
            'confidence': 79.7,
            'entry': 291.31,
            'target': 285.27,
            'expected_move': -6.04,
            'expected_pct': -2.07
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
        
        # Get Friday's close (yesterday for our prediction)
        friday_close = float(hist['Close'].iloc[-2])
        
        # Get today's data
        today_open = float(hist['Open'].iloc[-1])
        today_high = float(hist['High'].iloc[-1])
        today_low = float(hist['Low'].iloc[-1])
        today_close = float(hist['Close'].iloc[-1])
        
        # Get current price
        info = ticker.info
        current_price = info.get('currentPrice') or info.get('regularMarketPrice') or today_close
        current_price = float(current_price)
        
        # Calculate actual moves
        actual_move = current_price - friday_close
        actual_pct = (actual_move / friday_close) * 100
        high_move = today_high - friday_close
        high_pct = (high_move / friday_close) * 100
        
        # Print prediction
        print(f"\n📋 PREDICTION (Sunday 3:24 PM):")
        print(f"   Direction: {pred['direction']}")
        print(f"   Confidence: {pred['confidence']}%")
        print(f"   Entry: ${pred['entry']:.2f}")
        print(f"   Target: ${pred['target']:.2f}")
        print(f"   Expected: {pred['expected_move']:+.2f} ({pred['expected_pct']:+.2f}%)")
        
        # Print actual results
        print(f"\n📊 ACTUAL RESULTS (Monday):")
        print(f"   Friday Close: ${friday_close:.2f}")
        print(f"   Monday Open:  ${today_open:.2f} ({((today_open-friday_close)/friday_close)*100:+.2f}%)")
        print(f"   Today's High: ${today_high:.2f} ({high_pct:+.2f}%)")
        print(f"   Today's Low:  ${today_low:.2f} ({((today_low-friday_close)/friday_close)*100:+.2f}%)")
        print(f"   Current:      ${current_price:.2f} ({actual_pct:+.2f}%)")
        
        # Check if target hit
        if pred['direction'] == 'UP':
            target_hit = today_high >= pred['target']
            direction_correct = actual_move > 0
        else:  # DOWN
            target_hit = today_low <= pred['target']
            direction_correct = actual_move < 0
        
        # Verdict
        print(f"\n✅ VERDICT:")
        print(f"   Direction Predicted: {pred['direction']}")
        print(f"   Direction Actual: {'UP' if actual_move > 0 else 'DOWN' if actual_move < 0 else 'FLAT'}")
        print(f"   Direction Correct? {'✅ YES' if direction_correct else '❌ NO'}")
        print(f"   Target: ${pred['target']:.2f}")
        print(f"   Target Hit? {'✅ YES' if target_hit else '❌ NO'}")
        
        if target_hit:
            print(f"   🎯 TARGET HIT! High: ${today_high:.2f} vs Target: ${pred['target']:.2f}")
        else:
            distance = pred['target'] - today_high if pred['direction'] == 'UP' else today_low - pred['target']
            print(f"   📊 Missed by: ${abs(distance):.2f}")
        
        # Calculate profit/loss (assuming position sizing from earlier)
        if symbol == 'AMD':
            shares = 40
        elif symbol == 'AVGO':
            shares = 15
        else:  # ORCL
            shares = 20
        
        if target_hit:
            profit = pred['expected_move'] * shares
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
    
    print(f"\n{'='*80}\n")

if __name__ == "__main__":
    check_results()
