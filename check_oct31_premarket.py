import yfinance as yf
from datetime import datetime

print("\n" + "="*80)
print("📊 CHECKING OCT 31 PREMARKET FOR ORCL")
print("="*80)

ticker = yf.Ticker('ORCL')

# Get the info which includes premarket data
info = ticker.info

print(f"\n📅 PREDICTION (Oct 30 @ 3:55 PM):")
print(f"   Direction: DOWN")
print(f"   Confidence: 84.8%")
print(f"   Oct 30 Close: $257.63")
print(f"   Target: $251.30 (-2.46%)")
print(f"\n" + "-"*80)

# Check premarket price
premarket_price = info.get('preMarketPrice', None)
regular_price = info.get('regularMarketPrice', None)
prev_close = info.get('regularMarketPreviousClose', None)

if premarket_price:
    pm_change = ((premarket_price - prev_close) / prev_close) * 100
    print(f"📊 OCT 31 PREMARKET DATA:")
    print(f"   Previous Close: ${prev_close:.2f}")
    print(f"   Premarket Price: ${premarket_price:.2f}")
    print(f"   Premarket Change: {pm_change:+.2f}%")
    print("-"*80)
    
    if pm_change < 0:
        print(f"\n✅ PREDICTION CORRECT IN PREMARKET!")
        print(f"   Stock moving DOWN as predicted")
        
        if premarket_price <= 251.30:
            print(f"   🎯 TARGET ALREADY HIT: ${premarket_price:.2f} <= $251.30")
            print(f"   🚀 Full target achieved!")
        else:
            distance = premarket_price - 251.30
            progress = ((prev_close - premarket_price) / (prev_close - 251.30)) * 100
            print(f"   📊 Progress to target: {progress:.1f}%")
            print(f"   💰 Remaining to target: ${distance:.2f}")
    else:
        print(f"\n❌ PREDICTION WRONG IN PREMARKET")
        print(f"   Predicted: DOWN")
        print(f"   Premarket: UP {pm_change:+.2f}%")
else:
    print(f"\n⚠️ Premarket data not available yet")
    print(f"   Current Regular Price: ${regular_price:.2f}")
    print(f"   Previous Close: ${prev_close:.2f}")
    
    if regular_price and prev_close:
        change = ((regular_price - prev_close) / prev_close) * 100
        print(f"   Current Change: {change:+.2f}%")
        
        if change < 0:
            print(f"\n✅ Moving DOWN as predicted")
        else:
            print(f"\n❌ Moving UP (wrong prediction)")

print("\n" + "="*80)
