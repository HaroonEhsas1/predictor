import yfinance as yf
import json
from datetime import datetime

print("\n" + "="*80)
print("🔍 CHECKING OCT 21 PREDICTIONS vs OCT 22 ACTUAL RESULTS")
print("="*80)

# Load Oct 21 predictions
with open(r"d:\StockSense2\data\multi_stock\predictions_20251021_1551.json", 'r') as f:
    predictions = json.load(f)

print(f"\n📅 Prediction Date: Oct 21, 2025 at 3:51 PM ET")
print(f"📊 Predictions for: Oct 22, 2025")
print("\n" + "="*80)

stocks = ['AMD', 'AVGO', 'ORCL']

for symbol in stocks:
    pred = predictions['predictions'][symbol]
    
    print(f"\n📊 {symbol}:")
    print("-" * 80)
    
    # Predicted
    print(f"\n  PREDICTED (Oct 21 at close):")
    print(f"    Direction: {pred['direction']}")
    print(f"    Confidence: {pred['confidence']:.1f}%")
    print(f"    Close Price (Oct 21): ${pred['current_price']:.2f}")
    print(f"    Target (Oct 22): ${pred['target_price']:.2f}")
    print(f"    Expected Move: {pred['expected_move_pct']:+.2f}%")
    
    # Get actual Oct 22 data
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period='5d')
        
        if len(hist) >= 2:
            oct21_close = hist['Close'].iloc[-2]
            oct22_close = hist['Close'].iloc[-1]
            actual_change = oct22_close - oct21_close
            actual_change_pct = (actual_change / oct21_close) * 100
            
            print(f"\n  ACTUAL RESULT (Oct 22):")
            print(f"    Oct 21 Close: ${oct21_close:.2f}")
            print(f"    Oct 22 Close: ${oct22_close:.2f}")
            print(f"    Actual Move: ${actual_change:+.2f} ({actual_change_pct:+.2f}%)")
            
            # Determine actual direction
            if actual_change_pct > 0.5:
                actual_dir = "UP"
            elif actual_change_pct < -0.5:
                actual_dir = "DOWN"
            else:
                actual_dir = "FLAT"
            
            print(f"    Actual Direction: {actual_dir}")
            
            # Check if prediction was correct
            print(f"\n  RESULT:")
            if pred['direction'] == actual_dir:
                print(f"    ✅ CORRECT! Predicted {pred['direction']}, went {actual_dir}")
                accuracy = "WIN"
            else:
                print(f"    ❌ WRONG! Predicted {pred['direction']}, went {actual_dir}")
                accuracy = "LOSS"
            
            # Calculate error
            predicted_pct = pred['expected_move_pct']
            error = abs(actual_change_pct - predicted_pct)
            print(f"    Prediction Error: {error:.2f}% off")
            
    except Exception as e:
        print(f"    ❌ Error getting data: {e}")

print("\n" + "="*80)
print("📊 SUMMARY")
print("="*80)
print("\nPrediction Accuracy will be calculated...")
