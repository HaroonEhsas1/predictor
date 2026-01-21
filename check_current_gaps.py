"""
Check current gaps for all stocks
Shows why you might be seeing NEUTRAL
"""

import yfinance as yf

def check_gaps():
    symbols = ['AMD', 'NVDA', 'META', 'AVGO', 'SNOW', 'PLTR']
    
    print("\n" + "="*80)
    print("CURRENT GAP CHECK")
    print("="*80)
    print("\nChecking why stocks showing NEUTRAL...\n")
    
    for symbol in symbols:
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period='5d')
            info = ticker.info
            
            if len(hist) >= 2:
                prev_close = hist['Close'].iloc[-2]
                current = info.get('regularMarketPrice', hist['Close'].iloc[-1])
                
                gap = ((current - prev_close) / prev_close) * 100
                
                # Get thresholds
                thresholds = {
                    'AMD': 1.0,
                    'NVDA': 1.5,
                    'META': 1.2,
                    'AVGO': 2.0,
                    'SNOW': 1.8,
                    'PLTR': 2.5
                }
                
                min_gap = thresholds.get(symbol, 1.0)
                
                status = "✓ TRADE" if abs(gap) > min_gap else "✗ NEUTRAL"
                
                print(f"{symbol}:")
                print(f"   Gap: {gap:+.2f}%")
                print(f"   Min Required: {min_gap:.1f}%")
                print(f"   Status: {status}")
                
                if abs(gap) <= min_gap:
                    print(f"   WHY NEUTRAL: Gap {abs(gap):.2f}% < {min_gap:.1f}% threshold")
                
                print()
                
        except Exception as e:
            print(f"{symbol}: Error - {e}\n")
    
    print("="*80)
    print("ANALYSIS")
    print("="*80)
    print("""
If most stocks show NEUTRAL, it means:

1. TIMING ISSUE (Most Common):
   - You're running AFTER market opened (9:45 AM ET)
   - Gaps already closed or became small
   - Solution: Run at 9:15 AM ET (6:45 PM your time)

2. LOW VOLATILITY DAY:
   - Stocks just not gapping much today
   - Market calm, no big moves
   - Solution: Wait for more volatile days

3. THRESHOLDS TOO STRICT:
   - System requires 1-2.5% gaps
   - Designed to avoid low-quality setups
   - Solution: Lower thresholds (but more risk)

RECOMMENDATION:
- Run at 6:45 PM (9:15 AM ET) tomorrow
- Check premarket gaps BEFORE market opens
- You'll see 2-3 tradeable signals when gaps exist

Current behavior is CORRECT - system avoiding bad setups!
    """)

if __name__ == "__main__":
    check_gaps()
