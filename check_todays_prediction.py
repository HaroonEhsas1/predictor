import yfinance as yf
from datetime import datetime

print("\n" + "="*80)
print("🔍 CHECKING TODAY'S PREDICTIONS (Oct 22 → Oct 23)")
print("="*80)

stocks = {
    'AVGO': {'predicted': 'DOWN', 'confidence': 66.1, 'target': 336.77, 'close': 342.66},
    'ORCL': {'predicted': 'UP', 'confidence': 70.6, 'target': 280.30, 'close': 275.15}
}

print("\n📊 TODAY'S PREDICTIONS (Made at close Oct 22):")
print("-" * 80)

for symbol, pred in stocks.items():
    print(f"\n{symbol}:")
    print(f"  Predicted: {pred['predicted']} at {pred['confidence']:.1f}% confidence")
    print(f"  Oct 22 Close: ${pred['close']:.2f}")
    print(f"  Target (Oct 23): ${pred['target']:.2f}")
    
    # Get current price (after-hours or premarket)
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        # Try to get after-hours or premarket price
        current_price = None
        price_source = "Unknown"
        
        if 'postMarketPrice' in info and info['postMarketPrice']:
            current_price = info['postMarketPrice']
            price_source = "After-Hours"
        elif 'preMarketPrice' in info and info['preMarketPrice']:
            current_price = info['preMarketPrice']
            price_source = "Premarket"
        elif 'regularMarketPrice' in info:
            current_price = info['regularMarketPrice']
            price_source = "Last Close"
        
        if current_price:
            change = current_price - pred['close']
            change_pct = (change / pred['close']) * 100
            
            print(f"  Current ({price_source}): ${current_price:.2f}")
            print(f"  Change from close: ${change:+.2f} ({change_pct:+.2f}%)")
            
            # Check if prediction is correct SO FAR
            if pred['predicted'] == 'DOWN' and change < 0:
                print(f"  Status: ✅ TRENDING CORRECTLY (going down as predicted)")
            elif pred['predicted'] == 'DOWN' and change > 0:
                print(f"  Status: ⚠️ TRENDING OPPOSITE (going UP, predicted DOWN!)")
            elif pred['predicted'] == 'UP' and change > 0:
                print(f"  Status: ✅ TRENDING CORRECTLY (going up as predicted)")
            elif pred['predicted'] == 'UP' and change < 0:
                print(f"  Status: ⚠️ TRENDING OPPOSITE (going DOWN, predicted UP!)")
            else:
                print(f"  Status: ➖ FLAT")
                
    except Exception as e:
        print(f"  ❌ Error getting current price: {e}")

print("\n" + "="*80)
print("⚠️ NOTE: Market may not be open yet. Check again during market hours!")
print("="*80)
