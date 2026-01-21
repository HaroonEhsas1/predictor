import yfinance as yf
from datetime import datetime, timedelta

print("\n" + "="*70)
print("🔍 PREDICTION VERIFICATION - Oct 21 → Oct 22, 2025")
print("="*70)

stocks = ['AVGO', 'AMD', 'ORCL']

for symbol in stocks:
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period='5d')
        
        if len(hist) >= 2:
            oct21_close = hist['Close'].iloc[-2]
            oct22_current = hist['Close'].iloc[-1]
            change_pct = ((oct22_current - oct21_close) / oct21_close) * 100
            
            print(f"\n📊 {symbol}:")
            print(f"   Oct 21 Close: ${oct21_close:.2f}")
            print(f"   Oct 22 Current: ${oct22_current:.2f}")
            print(f"   Change: {change_pct:+.2f}%")
            
            if change_pct > 0:
                print(f"   Direction: ⬆️ UP")
            else:
                print(f"   Direction: ⬇️ DOWN")
    except Exception as e:
        print(f"\n❌ {symbol}: Error - {e}")

print("\n" + "="*70)
