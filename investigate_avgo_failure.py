import yfinance as yf
from datetime import datetime, timedelta

print("\n" + "="*80)
print("🔍 INVESTIGATING AVGO PREDICTION FAILURE")
print("="*80)

# Check actual price movement
ticker = yf.Ticker('AVGO')
hist = ticker.history(period='5d')

print("\n📊 ACTUAL AVGO PRICE MOVEMENT:")
print("-" * 80)

if len(hist) >= 2:
    yesterday_close = hist['Close'].iloc[-2]
    today_current = hist['Close'].iloc[-1]
    change = today_current - yesterday_close
    change_pct = (change / yesterday_close) * 100
    
    print(f"Yesterday (Oct 21) Close: ${yesterday_close:.2f}")
    print(f"Today (Oct 22) Current:   ${today_current:.2f}")
    print(f"Change: ${change:+.2f} ({change_pct:+.2f}%)")
    
    if change > 0:
        print(f"\n✅ ACTUAL DIRECTION: UP (Stock went UP!)")
    else:
        print(f"\n❌ ACTUAL DIRECTION: DOWN")
    
    # Get yesterday's data
    print(f"\n📈 YESTERDAY'S DATA (When prediction was made):")
    print("-" * 80)
    yesterday_data = hist.iloc[-2]
    print(f"Open: ${yesterday_data['Open']:.2f}")
    print(f"High: ${yesterday_data['High']:.2f}")
    print(f"Low: ${yesterday_data['Low']:.2f}")
    print(f"Close: ${yesterday_data['Close']:.2f}")
    print(f"Volume: {yesterday_data['Volume']:,.0f}")
    
    intraday_change = ((yesterday_data['Close'] - yesterday_data['Open']) / yesterday_data['Open']) * 100
    print(f"Intraday Change: {intraday_change:+.2f}%")
    
    # Today's data
    print(f"\n📊 TODAY'S MOVEMENT:")
    print("-" * 80)
    today_data = hist.iloc[-1]
    print(f"Open: ${today_data['Open']:.2f}")
    print(f"High: ${today_data['High']:.2f}")
    print(f"Low: ${today_data['Low']:.2f}")
    print(f"Current: ${today_data['Close']:.2f}")
    print(f"Volume: {today_data['Volume']:,.0f}")

print("\n" + "="*80)
print("🔍 CHECKING FOR PREDICTION BIAS")
print("="*80)

# Check recent AVGO predictions
import os
import json
import glob

pred_dir = "D:\\StockSense2\\data\\multi_stock"
if os.path.exists(pred_dir):
    pred_files = sorted(glob.glob(os.path.join(pred_dir, "predictions_*.json")))[-5:]
    
    print(f"\n📁 Last 5 Predictions:")
    print("-" * 80)
    
    down_count = 0
    up_count = 0
    
    for f in pred_files:
        try:
            with open(f, 'r') as file:
                data = json.load(file)
                if 'AVGO' in data:
                    direction = data['AVGO'].get('direction', 'N/A')
                    confidence = data['AVGO'].get('confidence', 0)
                    score = data['AVGO'].get('score', 0)
                    
                    filename = os.path.basename(f)
                    print(f"{filename}: {direction} ({confidence:.1f}% conf, score: {score:+.3f})")
                    
                    if direction == 'DOWN':
                        down_count += 1
                    elif direction == 'UP':
                        up_count += 1
        except:
            pass
    
    print(f"\n📊 Recent AVGO Prediction Stats:")
    print(f"   DOWN predictions: {down_count}")
    print(f"   UP predictions: {up_count}")
    
    if down_count > up_count * 2:
        print(f"\n⚠️ WARNING: Possible BEARISH BIAS detected!")
        print(f"   System predicting DOWN {down_count}x more than UP")

print("\n" + "="*80)
