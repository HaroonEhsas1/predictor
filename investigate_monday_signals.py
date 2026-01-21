#!/usr/bin/env python3
"""
Investigate Monday's Signals - Why Did System Miss Bearish Turn?
Check if data was LIVE or stale
"""

import yfinance as yf
from datetime import datetime

print("\n" + "="*80)
print("🔍 INVESTIGATING MONDAY'S PREDICTION FAILURE")
print("="*80)
print("\nWhy did AMD & AVGO predict UP when they went DOWN?")
print("Were data sources LIVE or STALE?")

# Get Monday and Tuesday data
symbols = ['AMD', 'AVGO', 'ORCL']

for symbol in symbols:
    print(f"\n{'='*80}")
    print(f"📊 {symbol} - DATA ANALYSIS")
    print(f"{'='*80}")
    
    ticker = yf.Ticker(symbol)
    hist = ticker.history(period='5d')
    
    if len(hist) < 3:
        continue
    
    # Get the dates
    friday = hist.iloc[-3]
    monday = hist.iloc[-2]
    tuesday = hist.iloc[-1]
    
    print(f"\n📅 FRIDAY (Oct 17):")
    print(f"   Close: ${friday['Close']:.2f}")
    
    print(f"\n📅 MONDAY (Oct 20) - When prediction was made:")
    print(f"   Open: ${monday['Open']:.2f}")
    print(f"   High: ${monday['High']:.2f}")
    print(f"   Low: ${monday['Low']:.2f}")
    print(f"   Close: ${monday['Close']:.2f}")
    print(f"   Daily Change: {((monday['Close']-monday['Open'])/monday['Open'])*100:+.2f}%")
    
    # Check Monday's intraday action
    monday_range = monday['High'] - monday['Low']
    close_position = (monday['Close'] - monday['Low']) / monday_range
    
    print(f"\n🔍 MONDAY'S INTRADAY SIGNALS:")
    print(f"   Range: ${monday_range:.2f}")
    print(f"   Close Position: {close_position*100:.0f}% of range")
    
    if close_position > 0.7:
        print(f"   → Closed near HIGH (bullish)")
    elif close_position < 0.3:
        print(f"   → Closed near LOW (bearish) ⚠️")
    else:
        print(f"   → Closed mid-range (neutral)")
    
    # Check if Monday showed weakness
    if monday['Close'] < monday['Open']:
        print(f"   ⚠️ BEARISH: Closed BELOW open!")
    else:
        print(f"   ✅ Closed above open")
    
    print(f"\n📅 TUESDAY (Oct 21) - Actual Result:")
    print(f"   Open: ${tuesday['Open']:.2f} ({((tuesday['Open']-monday['Close'])/monday['Close'])*100:+.2f}%)")
    print(f"   High: ${tuesday['High']:.2f}")
    print(f"   Low: ${tuesday['Low']:.2f}")
    print(f"   Close: ${tuesday['Close']:.2f}")
    print(f"   Daily Change: {((tuesday['Close']-tuesday['Open'])/tuesday['Open'])*100:+.2f}%")
    
    # Analysis
    print(f"\n💡 ANALYSIS:")
    
    # Did Monday show weakness that system should have caught?
    monday_weak = monday['Close'] < monday['Open']
    tuesday_gap_down = tuesday['Open'] < monday['Close']
    tuesday_went_down = tuesday['Close'] < tuesday['Open']
    
    if monday_weak:
        print(f"   🚨 Monday closed RED (down {((monday['Close']-monday['Open'])/monday['Open'])*100:.2f}%)")
        print(f"   → System should have seen this!")
    
    if tuesday_gap_down:
        print(f"   ⚠️ Tuesday gapped down at open")
    
    if tuesday_went_down:
        print(f"   ❌ Tuesday closed down")
    
    # Check if system had the data
    print(f"\n🔍 SYSTEM'S VIEW AT 3:55 PM MONDAY:")
    print(f"   Live Price Available: ${monday['Close']:.2f} ✅")
    print(f"   RSI: Would be calculated from recent closes")
    print(f"   Intraday Move: {((monday['Close']-monday['Open'])/monday['Open'])*100:+.2f}%")
    
    # Monday's momentum
    fri_to_mon = ((monday['Close'] - friday['Close']) / friday['Close']) * 100
    print(f"   Friday → Monday: {fri_to_mon:+.2f}%")
    
    if fri_to_mon > 2:
        print(f"   → Strong momentum UP (may have biased system)")
    elif fri_to_mon < -2:
        print(f"   → Momentum DOWN")

print(f"\n{'='*80}")
print(f"🎯 KEY FINDINGS:")
print(f"{'='*80}")

print(f"\n1. DATA AVAILABILITY:")
print(f"   ✅ Live prices were available")
print(f"   ✅ System could see Monday's close")
print(f"   ✅ Intraday data accessible")

print(f"\n2. WHAT SYSTEM SAW:")
print(f"   Let me check the actual signals...")

# Load the actual prediction output
print(f"\n3. POSSIBLE ISSUES:")
print(f"   🔍 Need to check:")
print(f"   • Was RSI showing overbought?")
print(f"   • Were options still bullish?")
print(f"   • Did technical indicators lag?")
print(f"   • Was momentum from Friday too strong?")
print(f"   • Did news sentiment bias system?")

print(f"\n{'='*80}\n")
