"""
Check October 22 actual market performance vs October 21 predictions
"""
import yfinance as yf
from datetime import datetime, timedelta

def get_actual_performance():
    """Get actual performance for Oct 22"""
    
    # October 21 predictions (made at 3:51 PM)
    predictions = {
        'AMD': {
            'direction': 'UP',
            'confidence': 71.54,
            'oct21_close': 239.12,
            'target': 243.98,
            'expected_change_pct': 2.03
        },
        'AVGO': {
            'direction': 'DOWN',
            'confidence': 81.10,
            'oct21_close': 342.335,
            'target': 335.78,
            'expected_change_pct': -1.91
        },
        'ORCL': {
            'direction': 'UP',
            'confidence': 71.31,
            'oct21_close': 275.23,
            'target': 280.38,
            'expected_change_pct': 1.87
        }
    }
    
    print("="*80)
    print("OCTOBER 21 PREDICTIONS vs OCTOBER 22 ACTUAL PERFORMANCE")
    print("="*80)
    print(f"\nChecking actual market data for October 22, 2025...\n")
    
    for symbol, pred in predictions.items():
        print(f"\n{'='*80}")
        print(f"  {symbol}")
        print(f"{'='*80}")
        
        try:
            # Get stock data
            stock = yf.Ticker(symbol)
            
            # Get historical data for Oct 21-22
            hist = stock.history(start='2025-10-21', end='2025-10-23')
            
            if len(hist) >= 2:
                oct21_close = hist.iloc[0]['Close']
                oct22_close = hist.iloc[1]['Close']
                
                # Get intraday high/low for Oct 22
                oct22_high = hist.iloc[1]['High']
                oct22_low = hist.iloc[1]['Low']
                oct22_open = hist.iloc[1]['Open']
                
                # Calculate actual change
                actual_change = oct22_close - oct21_close
                actual_change_pct = (actual_change / oct21_close) * 100
                
                # Check if prediction was correct
                predicted_direction = pred['direction']
                actual_direction = 'UP' if actual_change > 0 else 'DOWN'
                
                is_correct = predicted_direction == actual_direction
                
                print(f"\n📊 PREDICTION (Oct 21 @ 3:51 PM):")
                print(f"   Direction: {pred['direction']} ⬆️" if pred['direction'] == 'UP' else f"   Direction: {pred['direction']} ⬇️")
                print(f"   Confidence: {pred['confidence']:.2f}%")
                print(f"   Expected Move: {pred['expected_change_pct']:+.2f}%")
                print(f"   Target Price: ${pred['target']:.2f}")
                
                print(f"\n📈 ACTUAL PERFORMANCE (Oct 22):")
                print(f"   Oct 21 Close: ${oct21_close:.2f}")
                print(f"   Oct 22 Open:  ${oct22_open:.2f}")
                print(f"   Oct 22 High:  ${oct22_high:.2f}")
                print(f"   Oct 22 Low:   ${oct22_low:.2f}")
                print(f"   Oct 22 Close: ${oct22_close:.2f}")
                print(f"   Actual Change: ${actual_change:+.2f} ({actual_change_pct:+.2f}%)")
                
                print(f"\n🎯 RESULT:")
                if is_correct:
                    print(f"   ✅ CORRECT - Predicted {predicted_direction}, moved {actual_direction}")
                    
                    # Check if target was hit
                    if predicted_direction == 'UP':
                        target_hit = oct22_high >= pred['target']
                        print(f"   Target ${pred['target']:.2f}: {'✅ HIT' if target_hit else '❌ NOT HIT'}")
                    else:
                        target_hit = oct22_low <= pred['target']
                        print(f"   Target ${pred['target']:.2f}: {'✅ HIT' if target_hit else '❌ NOT HIT'}")
                    
                    # Compare predicted vs actual magnitude
                    magnitude_diff = abs(actual_change_pct) - abs(pred['expected_change_pct'])
                    if magnitude_diff > 0:
                        print(f"   📊 Actual move was LARGER by {magnitude_diff:.2f}%")
                    else:
                        print(f"   📊 Actual move was smaller by {abs(magnitude_diff):.2f}%")
                        
                else:
                    print(f"   ❌ INCORRECT - Predicted {predicted_direction}, but moved {actual_direction}")
                    print(f"   Loss: {abs(actual_change_pct):.2f}%")
                
            else:
                print(f"   ⚠️ Insufficient data available")
                
        except Exception as e:
            print(f"   ❌ Error fetching data: {e}")
    
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}\n")

if __name__ == "__main__":
    get_actual_performance()
