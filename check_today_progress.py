import yfinance as yf
import json
from datetime import datetime
import pytz

print("\n" + "="*80)
print("🔍 OCT 21 PREDICTIONS FOR TODAY (OCT 22)")
print("="*80)

# Load Oct 21 predictions
with open(r"d:\StockSense2\data\multi_stock\predictions_20251021_1551.json", 'r') as f:
    predictions = json.load(f)

print(f"\n📅 Prediction Made: Oct 21, 2025 at 3:51 PM (yesterday)")
print(f"📊 Predictions For: Oct 22, 2025 (TODAY)")

# Check market status
et = pytz.timezone('US/Eastern')
now_et = datetime.now(et)
print(f"\n⏰ Current Time: {now_et.strftime('%I:%M %p ET')} on Oct 22")
print(f"📍 Market Status: {'OPEN' if 9 <= now_et.hour < 16 else 'CLOSED'}")

print("\n" + "="*80)

stocks = ['AMD', 'AVGO', 'ORCL']

for symbol in stocks:
    pred = predictions['predictions'][symbol]
    
    print(f"\n📊 {symbol}:")
    print("-" * 80)
    
    # What was predicted yesterday
    print(f"\n  PREDICTED YESTERDAY (Oct 21 close):")
    print(f"    Direction: {pred['direction']}")
    print(f"    Confidence: {pred['confidence']:.1f}%")
    print(f"    Oct 21 Close: ${pred['current_price']:.2f}")
    print(f"    Target for Today: ${pred['target_price']:.2f}")
    print(f"    Expected Move: {pred['expected_move_pct']:+.2f}%")
    
    # Get current status
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        hist = ticker.history(period='5d')
        
        # Get yesterday's close and today's current
        if len(hist) >= 1:
            yesterday_close = float(hist['Close'].iloc[-1])  # Most recent close (Oct 21)
            
            # Get current price
            current = info.get('regularMarketPrice') or info.get('currentPrice')
            if current:
                current = float(current)
                change = current - yesterday_close
                change_pct = (change / yesterday_close) * 100
                
                print(f"\n  CURRENT STATUS (as of {now_et.strftime('%I:%M %p')} ET):")
                print(f"    Yesterday Close: ${yesterday_close:.2f}")
                print(f"    Current Price: ${current:.2f}")
                print(f"    Current Move: ${change:+.2f} ({change_pct:+.2f}%)")
                
                # Determine current direction
                if change_pct > 0.3:
                    current_dir = "UP"
                elif change_pct < -0.3:
                    current_dir = "DOWN"
                else:
                    current_dir = "FLAT"
                
                print(f"    Current Direction: {current_dir}")
                
                # Check if tracking prediction
                print(f"\n  TRACKING:")
                if pred['direction'] == current_dir:
                    print(f"    ✅ SO FAR CORRECT - Going {current_dir} as predicted!")
                elif current_dir == "FLAT":
                    print(f"    ⚠️ FLAT - Prediction {pred['direction']}, currently neutral")
                else:
                    print(f"    ❌ OPPOSITE - Predicted {pred['direction']}, going {current_dir}!")
                
                # Distance to target
                target = pred['target_price']
                dist_to_target = abs(current - target)
                pct_to_target = (dist_to_target / yesterday_close) * 100
                
                if pred['direction'] == 'UP':
                    if current >= target:
                        print(f"    🎯 TARGET HIT! (${current:.2f} >= ${target:.2f})")
                    else:
                        print(f"    📊 Distance to target: ${dist_to_target:.2f} ({pct_to_target:.2f}%) to go")
                else:  # DOWN
                    if current <= target:
                        print(f"    🎯 TARGET HIT! (${current:.2f} <= ${target:.2f})")
                    else:
                        print(f"    📊 Distance to target: ${dist_to_target:.2f} ({pct_to_target:.2f}%) to go")
            else:
                print(f"\n  ⚠️ Current price not available")
                
    except Exception as e:
        print(f"\n  ❌ Error getting current data: {e}")

print("\n" + "="*80)
print("⏰ Market closes at 4:00 PM ET to get final results")
print("="*80)
