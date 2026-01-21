"""
PREMARKET EXIT CHECK
====================
Check if yesterday's predictions are still valid or if we should exit now
Run this during premarket (6-9:30 AM ET) to make exit decisions
"""

import yfinance as yf
from datetime import datetime
import pytz

# Yesterday's predictions (from Oct 23 3:50 PM)
PREDICTIONS = {
    'AMD': {
        'direction': 'UP',
        'confidence': 92,
        'entry': 234.99,  # Yesterday's close
        'target': 241.23,
        'stop': 232.00,   # Estimated 2% stop
        'expected_move': 2.66
    },
    'AVGO': {
        'direction': 'UP',
        'confidence': 92,
        'entry': 344.29,
        'target': 352.03,
        'stop': 337.00,   # Estimated 2% stop
        'expected_move': 2.25
    },
    'ORCL': {
        'direction': 'UP',
        'confidence': 69,
        'entry': 280.23,
        'target': 287.02,
        'stop': 276.00,   # Estimated 1.5% stop
        'expected_move': 2.45
    }
}

def get_premarket_price(symbol):
    """Get current premarket price"""
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period='1d', interval='1m', prepost=True)
        
        if len(data) > 0:
            current_price = data['Close'].iloc[-1]
            return current_price
        return None
    except Exception as e:
        print(f"   ⚠️ Error fetching {symbol}: {str(e)[:50]}")
        return None

def check_exit_decision():
    """Check if we should exit or hold"""
    
    # Get current ET time
    et_tz = pytz.timezone('US/Eastern')
    now_et = datetime.now(et_tz)
    
    print("="*80)
    print("🌅 PREMARKET EXIT CHECK")
    print("="*80)
    print(f"⏰ Current Time: {now_et.strftime('%I:%M %p ET')}")
    print(f"📅 {now_et.strftime('%A, %B %d, %Y')}")
    print("="*80)
    
    print("\n💼 CHECKING POSITIONS:")
    print("-"*80)
    
    decisions = {}
    
    for symbol, pred in PREDICTIONS.items():
        print(f"\n📊 {symbol}:")
        print(f"   Yesterday's Prediction: {pred['direction']} {pred['confidence']}% confidence")
        print(f"   Entry: ${pred['entry']:.2f}")
        print(f"   Target: ${pred['target']:.2f} (+{pred['expected_move']:.2f}%)")
        print(f"   Stop: ${pred['stop']:.2f}")
        
        # Get current price
        current = get_premarket_price(symbol)
        
        if current is None:
            print(f"   ⚠️ Cannot fetch premarket price - check manually")
            decisions[symbol] = 'CHECK_MANUALLY'
            continue
        
        # Calculate P&L
        pnl_pct = ((current - pred['entry']) / pred['entry']) * 100
        pnl_vs_target = ((current - pred['entry']) / (pred['target'] - pred['entry'])) * 100
        
        print(f"\n   💰 CURRENT PRICE: ${current:.2f}")
        print(f"   📈 P&L: {pnl_pct:+.2f}% (${current - pred['entry']:+.2f})")
        print(f"   🎯 Target Progress: {pnl_vs_target:.0f}%")
        
        # Decision logic
        decision = None
        reason = None
        
        # Check if target hit (90%+)
        if pnl_vs_target >= 90:
            decision = '✅ EXIT NOW'
            reason = 'Target reached! Lock in profits'
        
        # Check if stop hit
        elif current <= pred['stop']:
            decision = '🛑 EXIT NOW'
            reason = 'Stop loss hit - cut losses'
        
        # Check if losing significant amount
        elif pnl_pct < -1.5:
            decision = '⚠️ EXIT NOW'
            reason = f'Losing {pnl_pct:.2f}% - prediction may be wrong'
        
        # Check if gaining but reversing
        elif pnl_pct > 1.0 and pnl_vs_target < 50:
            decision = '⚠️ CONSIDER EXIT'
            reason = f'Up {pnl_pct:.2f}% but not reaching target - take profits?'
        
        # Check if moving toward target
        elif pnl_pct > 0 and pnl_vs_target >= 50:
            decision = '🟢 HOLD'
            reason = f'{pnl_vs_target:.0f}% to target - looking good!'
        
        # Check if slightly positive
        elif 0 < pnl_pct < 1.0:
            decision = '🟡 HOLD (MONITOR)'
            reason = f'Small gain {pnl_pct:.2f}% - wait for 9:30 AM open'
        
        # Check if slightly negative but above stop
        elif -1.0 < pnl_pct < 0:
            decision = '🟡 HOLD (MONITOR)'
            reason = f'Small loss {pnl_pct:.2f}% - above stop, wait for open'
        
        else:
            decision = '🟡 HOLD'
            reason = 'Within acceptable range'
        
        print(f"\n   {decision}")
        print(f"   💡 Reason: {reason}")
        
        decisions[symbol] = {
            'decision': decision,
            'reason': reason,
            'current': current,
            'pnl_pct': pnl_pct,
            'target_progress': pnl_vs_target
        }
    
    # Summary
    print("\n" + "="*80)
    print("📋 SUMMARY & RECOMMENDATIONS")
    print("="*80)
    
    exit_now = []
    hold = []
    monitor = []
    
    for symbol, data in decisions.items():
        if isinstance(data, str):
            continue
            
        decision = data['decision']
        
        if 'EXIT NOW' in decision:
            exit_now.append(symbol)
        elif 'HOLD (MONITOR)' in decision:
            monitor.append(symbol)
        elif 'HOLD' in decision:
            hold.append(symbol)
    
    if exit_now:
        print(f"\n🚨 EXIT IMMEDIATELY:")
        for symbol in exit_now:
            data = decisions[symbol]
            print(f"   • {symbol}: {data['reason']}")
    
    if monitor:
        print(f"\n⚠️ MONITOR CLOSELY (Exit if reverses):")
        for symbol in monitor:
            data = decisions[symbol]
            print(f"   • {symbol}: {data['pnl_pct']:+.2f}% - {data['reason']}")
    
    if hold:
        print(f"\n✅ HOLD UNTIL 9:30 AM OPEN:")
        for symbol in hold:
            data = decisions[symbol]
            print(f"   • {symbol}: {data['pnl_pct']:+.2f}% - {data['reason']}")
    
    print("\n" + "="*80)
    print("💡 GENERAL RULES:")
    print("="*80)
    print("✅ EXIT if target 90%+ reached (lock profits)")
    print("🛑 EXIT if stop loss hit (cut losses)")
    print("⚠️ EXIT if losing >1.5% (prediction likely wrong)")
    print("🟢 HOLD if moving toward target")
    print("🟡 MONITOR if small gain/loss (decide at 9:30 AM)")
    print("="*80)
    
    return decisions

if __name__ == "__main__":
    check_exit_decision()
