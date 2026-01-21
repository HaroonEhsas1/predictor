import yfinance as yf
from datetime import datetime
import pytz

# Check current time
et = pytz.timezone('US/Eastern')
now_et = datetime.now(et)

print("\n" + "="*70)
print("⏰ MARKET STATUS CHECK")
print("="*70)

print(f"\nCurrent ET Time: {now_et.strftime('%Y-%m-%d %I:%M %p ET')}")
print(f"Day: {now_et.strftime('%A')}")

# Check if market is open
if now_et.weekday() < 5 and 9 <= now_et.hour < 16:
    if now_et.hour == 9 and now_et.minute < 30:
        status = "PREMARKET"
    else:
        status = "OPEN 📈"
else:
    status = "CLOSED"

print(f"Market Status: {status}")

# Get AVGO data
print("\n" + "="*70)
print("📊 AVGO DATA CHECK")
print("="*70)

ticker = yf.Ticker('AVGO')
hist = ticker.history(period='5d')

print(f"\nLast 3 days of AVGO:")
for i in range(min(3, len(hist))):
    idx = -(3-i)
    date = hist.index[idx].strftime('%Y-%m-%d')
    close = hist['Close'].iloc[idx]
    print(f"  {date}: ${close:.2f}")

print(f"\nWhat iloc[-1] gives: ${hist['Close'].iloc[-1]:.2f}")
print(f"What iloc[-2] gives: ${hist['Close'].iloc[-2]:.2f}")

# Get current price
info = ticker.info
current = info.get('regularMarketPrice', 'N/A')
print(f"\nCurrent Market Price (live): ${current}")

print("\n" + "="*70)
