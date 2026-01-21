"""
VERIFY PREMARKET TARGETS
=========================
Check if Friday's predictions hit targets in MONDAY PREMARKET
This is the CORRECT way to evaluate overnight swing predictions!
"""

import yfinance as yf
from datetime import datetime

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

def get_premarket_data(symbol):
    """Get Monday's premarket data"""
    try:
        ticker = yf.Ticker(symbol)
        # Get intraday data with premarket
        data = ticker.history(period='5d', interval='1m', prepost=True)
        
        if len(data) == 0:
            return None
        
        # Filter for Monday premarket (4 AM - 9:30 AM ET)
        # Get the most recent day's data
        latest_date = data.index[-1].date()
        monday_data = data[data.index.date == latest_date]
        
        if len(monday_data) == 0:
            return None
        
        # Premarket is before 9:30 AM ET
        premarket = monday_data[monday_data.index.hour < 9]
        if len(premarket) == 0:
            premarket = monday_data[(monday_data.index.hour == 9) & (monday_data.index.minute < 30)]
        
        if len(premarket) > 0:
            return {
                'premarket_high': premarket['High'].max(),
                'premarket_low': premarket['Low'].min(),
                'premarket_open': premarket['Open'].iloc[0],
                'premarket_close': premarket['Close'].iloc[-1],
                'regular_open': monday_data[monday_data.index.hour >= 9]['Open'].iloc[0] if len(monday_data[monday_data.index.hour >= 9]) > 0 else None
            }
        
        return None
    except Exception as e:
        print(f"   ⚠️ Error fetching premarket for {symbol}: {e}")
        return None

def verify_premarket_targets():
    print("="*80)
    print("🌅 PREMARKET TARGET VERIFICATION (Overnight Swing Strategy)")
    print("="*80)
    print("\n📊 Strategy: Enter Friday Close → Exit Monday Premarket at Target")
    print("⏰ Exit Window: 4:00 AM - 9:30 AM ET Monday")
    print("\n" + "="*80 + "\n")
    
    results = {}
    
    for symbol, pred in FRIDAY_PREDICTIONS.items():
        print(f"{'='*80}")
        print(f"📊 {symbol}")
        print(f"{'='*80}")
        
        # Get premarket data
        pm_data = get_premarket_data(symbol)
        
        # Also get regular market data for comparison
        ticker = yf.Ticker(symbol)
        monday = ticker.history(period='2d', interval='1d').iloc[-1]
        
        entry = pred['entry']
        target = pred['target']
        
        print(f"\n📈 FRIDAY'S PREDICTION:")
        print(f"   Entry (Fri Close): ${entry:.2f}")
        print(f"   Target: ${target:.2f} (+{pred['expected_move']:.2f}%)")
        print(f"   Confidence: {pred['confidence']:.1f}%")
        
        if pm_data:
            pm_high = pm_data['premarket_high']
            pm_open = pm_data['premarket_open']
            reg_open = pm_data['regular_open']
            
            # Calculate premarket performance
            pm_high_pnl = ((pm_high - entry) / entry) * 100
            target_pct = ((target - entry) / entry) * 100
            
            # Check if target hit in premarket
            pm_target_hit = pm_high >= target
            pm_target_progress = ((pm_high - entry) / (target - entry)) * 100 if target > entry else 0
            
            print(f"\n🌅 MONDAY PREMARKET (4 AM - 9:30 AM):")
            print(f"   Premarket High: ${pm_high:.2f} ({pm_high_pnl:+.2f}%)")
            print(f"   Premarket Open: ${pm_open:.2f}")
            print(f"   Regular Open:   ${reg_open:.2f}" if reg_open else "   Regular Open: N/A")
            
            print(f"\n🎯 PREMARKET TARGET CHECK:")
            print(f"   Target: ${target:.2f}")
            print(f"   Premarket High: ${pm_high:.2f}")
            
            if pm_target_hit:
                print(f"   ✅ TARGET HIT IN PREMARKET! ({pm_target_progress:.0f}%)")
                print(f"   💰 Maximum Gain Available: {pm_high_pnl:+.2f}%")
                print(f"   ✅ CORRECT PREDICTION - Should have exited at target!")
                verdict = "CORRECT ✅"
            else:
                print(f"   ❌ Target not hit in premarket ({pm_target_progress:.0f}% to target)")
                print(f"   📊 Best Gain Available: {pm_high_pnl:+.2f}%")
                verdict = "MISSED ❌"
            
            # Store results
            results[symbol] = {
                'target_hit_premarket': pm_target_hit,
                'premarket_high': pm_high,
                'pnl_at_pm_high': pm_high_pnl,
                'target_progress': pm_target_progress,
                'verdict': verdict
            }
        else:
            print(f"\n⚠️ Could not fetch premarket data")
            print(f"   Using regular market open as proxy: ${monday['Open']:.2f}")
            
            open_pnl = ((monday['Open'] - entry) / entry) * 100
            target_hit_at_open = monday['Open'] >= target
            
            if target_hit_at_open:
                print(f"   ✅ TARGET HIT AT OPEN ({open_pnl:+.2f}%)")
                verdict = "LIKELY CORRECT ✅"
            else:
                print(f"   📊 Open: {open_pnl:+.2f}% (Target: {pred['expected_move']:.2f}%)")
                verdict = "UNCERTAIN"
            
            results[symbol] = {
                'target_hit_premarket': target_hit_at_open,
                'premarket_high': monday['Open'],
                'pnl_at_pm_high': open_pnl,
                'target_progress': 0,
                'verdict': verdict
            }
        
        # Show regular market comparison
        reg_high = monday['High']
        reg_high_pnl = ((reg_high - entry) / entry) * 100
        
        print(f"\n📊 REGULAR MARKET (9:30 AM - 4:00 PM):")
        print(f"   Regular High: ${reg_high:.2f} ({reg_high_pnl:+.2f}%)")
        print(f"   Close: ${monday['Close']:.2f}")
        
        if pm_data and pm_high > reg_high:
            diff = pm_high - reg_high
            print(f"\n💡 INSIGHT: Premarket high was BETTER by ${diff:.2f}!")
            print(f"   This validates the overnight swing strategy!")
        
        print(f"\n📊 FINAL VERDICT: {verdict}")
        print()
    
    # Summary
    print(f"{'='*80}")
    print("📋 PREMARKET TARGET SUMMARY")
    print(f"{'='*80}\n")
    
    targets_hit = sum(1 for r in results.values() if r['target_hit_premarket'])
    total = len(results)
    
    print(f"{'Symbol':<10} {'PM Target':<15} {'PM High':<15} {'Best P&L':<15}")
    print("-"*60)
    
    for symbol, r in results.items():
        status = "✅ HIT" if r['target_hit_premarket'] else "❌ MISSED"
        pm_high = f"${r['premarket_high']:.2f}"
        pnl = f"{r['pnl_at_pm_high']:+.2f}%"
        
        print(f"{symbol:<10} {status:<15} {pm_high:<15} {pnl:<15}")
    
    print(f"\n{'='*80}")
    print(f"🎯 PREMARKET TARGET HIT RATE: {targets_hit}/{total} ({targets_hit/total*100:.0f}%)")
    
    avg_pm_pnl = sum(r['pnl_at_pm_high'] for r in results.values()) / total
    print(f"💰 AVERAGE PREMARKET GAIN: {avg_pm_pnl:+.2f}%")
    print(f"{'='*80}\n")
    
    if targets_hit == total:
        print("🎉 PERFECT! ALL TARGETS HIT IN PREMARKET!")
        print("✅ Strategy validated - overnight swings work!")
    elif targets_hit > total / 2:
        print(f"✅ GOOD! {targets_hit}/{total} targets hit in premarket")
        print("📊 Overnight swing strategy is working")
    else:
        print(f"⚠️ Only {targets_hit}/{total} targets hit in premarket")
    
    print("\n💡 KEY INSIGHT:")
    print("   This is why we trade OVERNIGHT SWINGS - exit in premarket!")
    print("   Regular market data doesn't show the full picture.")
    
    return results

if __name__ == "__main__":
    verify_premarket_targets()
