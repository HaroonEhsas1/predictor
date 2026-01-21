"""
VERIFY FRIDAY'S PREDICTIONS
===========================
Check if Friday Oct 24 predictions hit targets on Monday Oct 27
"""

import yfinance as yf
from datetime import datetime, timedelta

# Friday's predictions (Oct 24, 3:53 PM)
FRIDAY_PREDICTIONS = {
    'AMD': {
        'direction': 'UP',
        'confidence': 93.0,
        'entry': 252.42,  # Friday's close
        'target': 260.38,
        'expected_move': 3.15
    },
    'AVGO': {
        'direction': 'UP',
        'confidence': 93.2,
        'entry': 355.43,  # Friday's close
        'target': 363.42,
        'expected_move': 2.25
    },
    'ORCL': {
        'direction': 'UP',
        'confidence': 88.1,
        'entry': 283.76,  # Friday's close
        'target': 289.39,
        'expected_move': 1.99
    }
}

def get_monday_data(symbol):
    """Get Monday's trading data"""
    try:
        ticker = yf.Ticker(symbol)
        # Get last 5 days to ensure we capture Monday
        hist = ticker.history(period='5d', interval='1d')
        
        if len(hist) > 0:
            # Get latest (Monday)
            monday = hist.iloc[-1]
            
            return {
                'open': monday['Open'],
                'high': monday['High'],
                'low': monday['Low'],
                'close': monday['Close'],
                'date': monday.name.strftime('%Y-%m-%d')
            }
        return None
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
        return None

def verify_predictions():
    print("="*80)
    print("📊 FRIDAY'S PREDICTION VERIFICATION (Oct 24 → Oct 27)")
    print("="*80)
    print("\nChecking if targets were reached on Monday...\n")
    
    results = {}
    
    for symbol, pred in FRIDAY_PREDICTIONS.items():
        print(f"\n{'='*80}")
        print(f"📊 {symbol}")
        print(f"{'='*80}")
        
        # Get Monday data
        monday_data = get_monday_data(symbol)
        
        if monday_data is None:
            print(f"⚠️ Unable to fetch Monday data for {symbol}")
            continue
        
        # Calculate results
        entry = pred['entry']
        target = pred['target']
        
        monday_open = monday_data['open']
        monday_high = monday_data['high']
        monday_low = monday_data['low']
        monday_close = monday_data['close']
        
        # P&L calculations
        pnl_at_open = ((monday_open - entry) / entry) * 100
        pnl_at_high = ((monday_high - entry) / entry) * 100
        pnl_at_close = ((monday_close - entry) / entry) * 100
        
        target_pct = ((target - entry) / entry) * 100
        
        # Check if target hit
        target_hit = monday_high >= target
        target_progress = ((monday_high - entry) / (target - entry)) * 100 if target > entry else 0
        
        # Display results
        print(f"\n📈 FRIDAY'S PREDICTION:")
        print(f"   Direction: {pred['direction']} @ {pred['confidence']:.1f}% confidence")
        print(f"   Entry (Fri Close): ${entry:.2f}")
        print(f"   Target: ${target:.2f} (+{target_pct:.2f}%)")
        
        print(f"\n💰 MONDAY'S ACTUAL PERFORMANCE:")
        print(f"   Date: {monday_data['date']}")
        print(f"   Open:  ${monday_open:.2f} ({pnl_at_open:+.2f}%)")
        print(f"   High:  ${monday_high:.2f} ({pnl_at_high:+.2f}%)")
        print(f"   Low:   ${monday_low:.2f}")
        print(f"   Close: ${monday_close:.2f} ({pnl_at_close:+.2f}%)")
        
        print(f"\n🎯 TARGET ANALYSIS:")
        print(f"   Target Price: ${target:.2f}")
        print(f"   Monday High:  ${monday_high:.2f}")
        
        if target_hit:
            print(f"   ✅ TARGET HIT! ({target_progress:.0f}% to target)")
            print(f"   💰 Maximum Gain: {pnl_at_high:+.2f}%")
            verdict = "CORRECT ✅"
        else:
            print(f"   ❌ TARGET MISSED (only {target_progress:.0f}% to target)")
            print(f"   📊 Best Gain: {pnl_at_high:+.2f}% (needed {target_pct:.2f}%)")
            verdict = "MISSED ❌"
        
        # Direction check
        if pred['direction'] == 'UP':
            direction_correct = monday_close > entry
        else:
            direction_correct = monday_close < entry
        
        if direction_correct:
            print(f"   ✅ DIRECTION: Correct ({pred['direction']})")
        else:
            print(f"   ❌ DIRECTION: Wrong (predicted {pred['direction']})")
        
        print(f"\n📊 FINAL VERDICT: {verdict}")
        
        # Store results
        results[symbol] = {
            'predicted': pred,
            'actual': monday_data,
            'target_hit': target_hit,
            'target_progress': target_progress,
            'pnl_at_high': pnl_at_high,
            'pnl_at_close': pnl_at_close,
            'direction_correct': direction_correct,
            'verdict': verdict
        }
    
    # Summary
    print(f"\n{'='*80}")
    print("📋 SUMMARY")
    print(f"{'='*80}")
    
    targets_hit = sum(1 for r in results.values() if r['target_hit'])
    directions_correct = sum(1 for r in results.values() if r['direction_correct'])
    total = len(results)
    
    print(f"\n📊 Performance Metrics:")
    print(f"{'Symbol':<10} {'Target Hit':<15} {'Direction':<15} {'Best P&L':<15} {'Close P&L':<15}")
    print("-"*80)
    
    for symbol, r in results.items():
        target_status = "✅ HIT" if r['target_hit'] else "❌ MISSED"
        dir_status = "✅ CORRECT" if r['direction_correct'] else "❌ WRONG"
        best_pnl = f"{r['pnl_at_high']:+.2f}%"
        close_pnl = f"{r['pnl_at_close']:+.2f}%"
        
        print(f"{symbol:<10} {target_status:<15} {dir_status:<15} {best_pnl:<15} {close_pnl:<15}")
    
    print(f"\n{'='*80}")
    print(f"🎯 TARGET HIT RATE: {targets_hit}/{total} ({targets_hit/total*100:.0f}%)")
    print(f"🎯 DIRECTION ACCURACY: {directions_correct}/{total} ({directions_correct/total*100:.0f}%)")
    
    avg_best_pnl = sum(r['pnl_at_high'] for r in results.values()) / total
    avg_close_pnl = sum(r['pnl_at_close'] for r in results.values()) / total
    
    print(f"💰 AVERAGE BEST P&L: {avg_best_pnl:+.2f}%")
    print(f"💰 AVERAGE CLOSE P&L: {avg_close_pnl:+.2f}%")
    print(f"{'='*80}")
    
    if targets_hit == total:
        print("\n🎉 PERFECT! ALL TARGETS HIT!")
    elif targets_hit > 0:
        print(f"\n✅ GOOD! {targets_hit}/{total} targets hit")
    else:
        print(f"\n⚠️ NO TARGETS HIT - Review predictions")
    
    return results

if __name__ == "__main__":
    verify_predictions()
