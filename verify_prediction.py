import yfinance as yf

print("\n" + "="*80)
print("📊 VERIFYING OCT 30 PREDICTION FOR ORCL")
print("="*80)

ticker = yf.Ticker('ORCL')
hist = ticker.history(period='5d')

# Get Oct 30 close (last day in history)
oct30_close = hist['Close'].iloc[-1]

# Get current/premarket info
info = ticker.info
premarket = info.get('preMarketPrice', None)
current = info.get('regularMarketPrice', None)

print(f"\n📅 PREDICTION DETAILS (Oct 30 @ 3:55 PM):")
print(f"   Direction: DOWN")
print(f"   Confidence: 84.8%")
print(f"   Reference Close: $257.63 (from prediction)")
print(f"   Actual Oct 30 Close: ${oct30_close:.2f}")
print(f"   Target: $251.30 (-2.46%)")

print(f"\n" + "-"*80)
print(f"📊 OCT 31 RESULTS:")

if premarket:
    change_from_close = ((premarket - oct30_close) / oct30_close) * 100
    print(f"   Oct 30 Close: ${oct30_close:.2f}")
    print(f"   Oct 31 Premarket: ${premarket:.2f}")
    print(f"   Change: {change_from_close:+.2f}%")
    print("-"*80)
    
    if change_from_close < 0:
        print(f"\n✅ PREDICTION: CORRECT!")
        print(f"   Stock moved DOWN as predicted")
        
        if premarket <= 251.30:
            print(f"   🎯 TARGET HIT!")
        else:
            progress = ((oct30_close - premarket) / (oct30_close - 251.30)) * 100
            print(f"   📊 Progress: {progress:.1f}% to target")
    else:
        print(f"\n❌ PREDICTION: WRONG!")
        print(f"   Predicted: DOWN")
        print(f"   Actual: UP {change_from_close:+.2f}%")
else:
    if current:
        change_from_close = ((current - oct30_close) / oct30_close) * 100
        print(f"   Oct 30 Close: ${oct30_close:.2f}")
        print(f"   Current Price: ${current:.2f}")
        print(f"   Change: {change_from_close:+.2f}%")
        print("-"*80)
        
        if change_from_close < 0:
            print(f"\n✅ PREDICTION: CORRECT!")
        else:
            print(f"\n❌ PREDICTION: WRONG!")

print("\n" + "="*80)
