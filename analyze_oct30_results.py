"""
Analyze Oct 30, 2025 Results vs Predictions
Check what happened today and why stocks went down
"""

import yfinance as yf
from datetime import datetime, timedelta

def analyze_today_results():
    """Analyze today's market results"""
    
    print("="*80)
    print("📊 OCT 30, 2025 - MARKET ANALYSIS")
    print("="*80)
    print(f"Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
    
    stocks = ['AMD', 'AVGO', 'ORCL']
    
    # Get data for yesterday and today
    for symbol in stocks:
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period='5d')
            
            if len(hist) >= 2:
                # Get yesterday's close and today's performance
                yesterday_close = hist['Close'].iloc[-2]
                today_open = hist['Open'].iloc[-1]
                today_high = hist['High'].iloc[-1]
                today_low = hist['Low'].iloc[-1]
                today_close = hist['Close'].iloc[-1]
                
                # Calculate changes
                gap = ((today_open - yesterday_close) / yesterday_close) * 100
                intraday = ((today_close - today_open) / today_open) * 100
                total = ((today_close - yesterday_close) / yesterday_close) * 100
                
                print(f"\n{symbol}:")
                print(f"  Yesterday Close: ${yesterday_close:.2f}")
                print(f"  Today Open:      ${today_open:.2f} ({gap:+.2f}% gap)")
                print(f"  Today High:      ${today_high:.2f}")
                print(f"  Today Low:       ${today_low:.2f}")
                print(f"  Today Close:     ${today_close:.2f}")
                print(f"  Intraday Move:   {intraday:+.2f}%")
                print(f"  Total Change:    {total:+.2f}%")
                
                if total < -1.0:
                    print(f"  ⚠️ DOWN significantly")
                elif total < 0:
                    print(f"  📉 Slightly down")
                elif total > 1.0:
                    print(f"  ✅ UP significantly")
                else:
                    print(f"  📈 Slightly up")
                    
        except Exception as e:
            print(f"\n{symbol}: Error fetching data - {e}")
    
    # Check market indices
    print(f"\n{'='*80}")
    print("📊 MARKET INDICES:")
    print(f"{'='*80}")
    
    indices = ['^GSPC', '^IXIC', '^DJI']
    index_names = ['S&P 500', 'NASDAQ', 'DOW']
    
    for idx, name in zip(indices, index_names):
        try:
            ticker = yf.Ticker(idx)
            hist = ticker.history(period='5d')
            
            if len(hist) >= 2:
                yesterday = hist['Close'].iloc[-2]
                today = hist['Close'].iloc[-1]
                change = ((today - yesterday) / yesterday) * 100
                
                print(f"\n{name}:")
                print(f"  Yesterday: {yesterday:.2f}")
                print(f"  Today:     {today:.2f}")
                print(f"  Change:    {change:+.2f}%")
                
        except Exception as e:
            print(f"\n{name}: Error - {e}")
    
    # Check VIX (fear index)
    print(f"\n{'='*80}")
    print("📊 FEAR INDEX (VIX):")
    print(f"{'='*80}")
    
    try:
        vix = yf.Ticker('^VIX')
        hist = vix.history(period='5d')
        
        if len(hist) >= 2:
            yesterday_vix = hist['Close'].iloc[-2]
            today_vix = hist['Close'].iloc[-1]
            vix_change = today_vix - yesterday_vix
            
            print(f"\nVIX:")
            print(f"  Yesterday: {yesterday_vix:.2f}")
            print(f"  Today:     {today_vix:.2f}")
            print(f"  Change:    {vix_change:+.2f}")
            
            if today_vix > 20:
                print(f"  ⚠️ HIGH FEAR (VIX > 20)")
            elif today_vix > 15:
                print(f"  📊 MODERATE FEAR")
            else:
                print(f"  ✅ LOW FEAR (Bullish)")
                
    except Exception as e:
        print(f"\nVIX: Error - {e}")
    
    print(f"\n{'='*80}")
    print("🔍 POSSIBLE REASONS FOR DOWN MOVE:")
    print(f"{'='*80}")
    print("""
    Common reasons stocks go down:
    
    1. 📰 Negative News:
       - Earnings miss or guidance cut
       - Negative analyst downgrade
       - Sector-wide negative news
       - Macro economic data (GDP, inflation, etc.)
    
    2. 📊 Market Factors:
       - Overall market sell-off (S&P/NASDAQ down)
       - VIX spike (fear increase)
       - Profit taking after rally
       - End of month rebalancing
    
    3. 🌍 External Events:
       - Fed news or interest rate concerns
       - Geopolitical tensions
       - Bond yields rising
       - Dollar strength
    
    4. 📉 Technical Factors:
       - Resistance levels hit
       - Overbought conditions
       - Support level breaks
       - Momentum shift
    
    5. ⚠️ Stock-Specific:
       - Insider selling
       - Negative catalyst
       - Competitive threat
       - Regulatory issues
    """)
    
    print(f"\n{'='*80}")
    print("💡 SYSTEM LEARNING:")
    print(f"{'='*80}")
    print("""
    If prediction was WRONG (predicted UP, went DOWN):
    
    ✅ This is NORMAL - 60-70% win rate means 30-40% losses
    ✅ Check if stop loss was hit correctly
    ✅ Verify if any major news broke overnight
    ✅ Confirm market regime was properly detected
    ✅ Review bidirectional logic (should predict DOWN when bearish)
    
    Key Questions:
    1. Was the prediction confidence appropriate? (Lower = more uncertain)
    2. Were there conflicting signals that reduced confidence?
    3. Did major news break that system couldn't anticipate?
    4. Was overall market down (hard to fight trend)?
    5. Did technical levels hold or break?
    
    Remember: 
    - 100% accuracy is impossible
    - Risk management protects capital
    - Learn from both wins AND losses
    - System improves with data
    """)
    
    print(f"\n{'='*80}")
    print("✅ ANALYSIS COMPLETE")
    print(f"{'='*80}\n")

if __name__ == "__main__":
    analyze_today_results()
