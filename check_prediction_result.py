import yfinance as yf
from datetime import datetime

print("\n" + "="*80)
print("📊 CHECKING YESTERDAY'S ORCL PREDICTION")
print("="*80)

ticker = yf.Ticker('ORCL')
data = ticker.history(period='5d')

if len(data) >= 2:
    prev_close = data.iloc[-2]['Close']
    today_open = data.iloc[-1]['Open']
    current_price = data.iloc[-1]['Close']
    
    # Calculate changes
    overnight_change = ((today_open - prev_close) / prev_close) * 100
    total_change = ((current_price - prev_close) / prev_close) * 100
    
    print(f"\n📅 PREDICTION DATE: Oct 30, 2025 @ 3:55 PM")
    print(f"🎯 PREDICTION: DOWN with 84.8% confidence")
    print(f"💰 Target: $251.30 (-2.46%)")
    print(f"\n" + "-"*80)
    print(f"📊 ACTUAL RESULTS:")
    print(f"   Oct 30 Close:     ${prev_close:.2f}")
    print(f"   Oct 31 Open:      ${today_open:.2f} ({overnight_change:+.2f}%)")
    print(f"   Oct 31 Current:   ${current_price:.2f} ({total_change:+.2f}%)")
    print("-"*80)
    
    # Check if prediction was correct
    if total_change < 0:
        print(f"\n✅ PREDICTION: CORRECT!")
        print(f"   Direction: DOWN as predicted")
        
        if current_price <= 251.30:
            print(f"   🎯 TARGET HIT: ${current_price:.2f} <= $251.30")
        else:
            target_progress = (prev_close - current_price) / (prev_close - 251.30) * 100
            print(f"   📊 Target Progress: {target_progress:.1f}%")
            print(f"   💰 Still needs: ${current_price - 251.30:.2f} to hit target")
    else:
        print(f"\n❌ PREDICTION: WRONG!")
        print(f"   Predicted: DOWN")
        print(f"   Actual: UP {total_change:+.2f}%")
    
    print("\n" + "="*80)
    
    # Get premarket data if available
    print(f"\n💡 Checking premarket data...")
    try:
        premarket = ticker.info.get('preMarketPrice', 'N/A')
        if premarket != 'N/A':
            pm_change = ((premarket - prev_close) / prev_close) * 100
            print(f"   Premarket: ${premarket:.2f} ({pm_change:+.2f}%)")
    except:
        print(f"   Premarket data not available")
    
else:
    print("❌ Error: Not enough data to compare")
