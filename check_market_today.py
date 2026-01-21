"""
Check what happened in the market today
"""
import yfinance as yf
from datetime import datetime, timedelta

def check_market_today():
    """Check today's market performance"""
    
    print("="*80)
    print("📊 MARKET PERFORMANCE CHECK - October 22, 2025")
    print("="*80)
    
    # Get SPY (S&P 500)
    spy = yf.Ticker('SPY')
    spy_hist = spy.history(period='5d')
    
    if len(spy_hist) >= 2:
        today_idx = -1
        yesterday_idx = -2
        
        spy_yesterday_close = spy_hist['Close'].iloc[yesterday_idx]
        spy_today_open = spy_hist['Open'].iloc[today_idx]
        spy_today_high = spy_hist['High'].iloc[today_idx]
        spy_today_low = spy_hist['Low'].iloc[today_idx]
        spy_today_close = spy_hist['Close'].iloc[today_idx]
        
        spy_change = spy_today_close - spy_yesterday_close
        spy_change_pct = (spy_change / spy_yesterday_close) * 100
        intraday_range = ((spy_today_high - spy_today_low) / spy_yesterday_close) * 100
        
        print(f"\n📊 SPY (S&P 500):")
        print(f"   Yesterday Close: ${spy_yesterday_close:.2f}")
        print(f"   Today Open:  ${spy_today_open:.2f}")
        print(f"   Today High:  ${spy_today_high:.2f}")
        print(f"   Today Low:   ${spy_today_low:.2f}")
        print(f"   Today Close: ${spy_today_close:.2f}")
        print(f"   Change: ${spy_change:+.2f} ({spy_change_pct:+.2f}%)")
        print(f"   Intraday Range: {intraday_range:.2f}%")
        
        if spy_change_pct < -1:
            print(f"   🔴 SIGNIFICANT DECLINE - Market was weak!")
        elif spy_change_pct < -0.3:
            print(f"   ⚠️ MODERATE DECLINE - Market was down")
        elif spy_change_pct < 0:
            print(f"   📉 SLIGHT DECLINE - Market slightly down")
        elif spy_change_pct < 0.3:
            print(f"   📈 SLIGHT GAIN - Market slightly up")
        else:
            print(f"   🟢 STRONG GAIN - Market was strong")
    
    # Get QQQ (Nasdaq)
    qqq = yf.Ticker('QQQ')
    qqq_hist = qqq.history(period='5d')
    
    if len(qqq_hist) >= 2:
        qqq_yesterday_close = qqq_hist['Close'].iloc[-2]
        qqq_today_close = qqq_hist['Close'].iloc[-1]
        qqq_change = qqq_today_close - qqq_yesterday_close
        qqq_change_pct = (qqq_change / qqq_yesterday_close) * 100
        
        print(f"\n📊 QQQ (Nasdaq):")
        print(f"   Yesterday Close: ${qqq_yesterday_close:.2f}")
        print(f"   Today Close: ${qqq_today_close:.2f}")
        print(f"   Change: ${qqq_change:+.2f} ({qqq_change_pct:+.2f}%)")
        
        if qqq_change_pct < -1:
            print(f"   🔴 SIGNIFICANT DECLINE - Tech was weak!")
        elif qqq_change_pct < -0.3:
            print(f"   ⚠️ MODERATE DECLINE - Tech was down")
    
    # Check VIX
    vix = yf.Ticker('^VIX')
    vix_hist = vix.history(period='5d')
    
    if len(vix_hist) >= 2:
        vix_yesterday = vix_hist['Close'].iloc[-2]
        vix_today = vix_hist['Close'].iloc[-1]
        vix_change = vix_today - vix_yesterday
        vix_change_pct = (vix_change / vix_yesterday) * 100
        
        print(f"\n📊 VIX (Fear Gauge):")
        print(f"   Yesterday: {vix_yesterday:.2f}")
        print(f"   Today: {vix_today:.2f}")
        print(f"   Change: {vix_change:+.2f} ({vix_change_pct:+.2f}%)")
        
        if vix_today > 25:
            print(f"   🔴 HIGH FEAR - Market very volatile")
        elif vix_today > 20:
            print(f"   ⚠️ ELEVATED FEAR - Market concerned")
        elif vix_today > 15:
            print(f"   ⚖️ NORMAL FEAR - Market stable")
        else:
            print(f"   🟢 LOW FEAR - Market calm")
    
    # Check our stocks
    print(f"\n{'='*80}")
    print("📊 OUR STOCKS TODAY:")
    print(f"{'='*80}")
    
    for symbol in ['AMD', 'AVGO', 'ORCL']:
        stock = yf.Ticker(symbol)
        hist = stock.history(period='5d')
        
        if len(hist) >= 2:
            yesterday_close = hist['Close'].iloc[-2]
            today_close = hist['Close'].iloc[-1]
            change = today_close - yesterday_close
            change_pct = (change / yesterday_close) * 100
            
            print(f"\n{symbol}:")
            print(f"   Yesterday: ${yesterday_close:.2f}")
            print(f"   Today: ${today_close:.2f}")
            print(f"   Change: ${change:+.2f} ({change_pct:+.2f}%)")
            
            if abs(change_pct) > 2:
                print(f"   {'🔴' if change_pct < 0 else '🟢'} BIG MOVE!")
    
    print(f"\n{'='*80}")
    print("💡 SYSTEM ANALYSIS:")
    print(f"{'='*80}")
    
    # Would our market regime detection have caught this?
    market_avg = (spy_change_pct + qqq_change_pct) / 2
    
    print(f"\nMarket Average: {market_avg:+.2f}%")
    
    if market_avg < -0.5:
        print(f"✅ Our Market Regime Detection WOULD trigger:")
        print(f"   Status: BEARISH")
        print(f"   Bias: -0.05 (reduce bullish predictions)")
        print(f"   This should have helped!")
    elif market_avg > 0.5:
        print(f"✅ Our Market Regime Detection WOULD trigger:")
        print(f"   Status: BULLISH")
        print(f"   Bias: +0.05 (boost bullish predictions)")
    else:
        print(f"⚠️ Our Market Regime Detection would NOT trigger:")
        print(f"   Market change {market_avg:+.2f}% is within neutral zone (-0.5% to +0.5%)")
        print(f"   Need to lower threshold if market often moves 0.3-0.5%")

if __name__ == "__main__":
    check_market_today()
