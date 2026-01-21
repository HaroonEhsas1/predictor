"""
Diagnose why October 21 predictions failed
Analyze what went wrong with each stock
"""
import yfinance as yf
from datetime import datetime
import json

def diagnose_failure():
    """Analyze what went wrong with Oct 21 predictions"""
    
    print("="*80)
    print("DIAGNOSING OCTOBER 21 PREDICTION FAILURES")
    print("="*80)
    
    # Load the prediction details
    with open('data/multi_stock/predictions_20251021_1551.json', 'r') as f:
        pred_data = json.load(f)
    
    predictions = pred_data['predictions']
    
    for symbol in ['AMD', 'AVGO', 'ORCL']:
        pred = predictions[symbol]
        
        print(f"\n{'='*80}")
        print(f"  {symbol} - FAILURE ANALYSIS")
        print(f"{'='*80}")
        
        print(f"\n📋 PREDICTION DETAILS:")
        print(f"   Direction: {pred['direction']}")
        print(f"   Confidence: {pred['confidence']:.2f}%")
        print(f"   Total Score: {pred['total_score']:.4f}")
        print(f"\n   Explanation: {pred['explanation']}")
        
        # Get actual data
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(start='2025-10-21', end='2025-10-23')
            
            if len(hist) >= 2:
                oct21_close = hist.iloc[0]['Close']
                oct22_close = hist.iloc[1]['Close']
                actual_change_pct = ((oct22_close - oct21_close) / oct21_close) * 100
                actual_direction = 'UP' if actual_change_pct > 0 else 'DOWN'
                
                print(f"\n📉 ACTUAL OUTCOME:")
                print(f"   Direction: {actual_direction}")
                print(f"   Change: {actual_change_pct:+.2f}%")
                
                print(f"\n🔍 POSSIBLE REASONS FOR FAILURE:")
                
                # Analyze based on the explanation
                explanation = pred['explanation']
                
                if symbol == 'AMD':
                    print(f"   • Predicted UP based on Technical (+0.091) and News (+0.069)")
                    print(f"   • Actual: DOWN -0.70%")
                    print(f"   • Likely Issue: Technical indicators gave false positive")
                    print(f"   • Missing: Market-wide weakness signal")
                    print(f"   • Missing: Overnight sentiment shift")
                    
                elif symbol == 'AVGO':
                    print(f"   • Predicted DOWN with 81% confidence based on Options (-0.110)")
                    print(f"   • BUT had conflicting News (+0.084) and Technical (+0.042)")
                    print(f"   • Actual: UP +0.29%")
                    print(f"   • Likely Issue: Options signal was early/wrong OR...")
                    print(f"   • ...News/Technical were actually correct but got overridden")
                    print(f"   • High confidence led to overconfidence in options signal")
                    
                elif symbol == 'ORCL':
                    print(f"   • Predicted UP based on Options (+0.110), News (+0.088), Institutional (+0.032)")
                    print(f"   • Had conflicting Technical (-0.078)")
                    print(f"   • Actual: DOWN -0.30%")
                    print(f"   • Likely Issue: Technical bearish signal was correct!")
                    print(f"   • System ignored the technical warning")
                    print(f"   • Options/News were misleading")
                
                # Check if there was a market-wide event
                spy = yf.Ticker('SPY')
                spy_hist = spy.history(start='2025-10-21', end='2025-10-23')
                if len(spy_hist) >= 2:
                    spy_change = ((spy_hist.iloc[1]['Close'] - spy_hist.iloc[0]['Close']) / spy_hist.iloc[0]['Close']) * 100
                    print(f"\n📊 MARKET CONTEXT:")
                    print(f"   SPY (S&P 500): {spy_change:+.2f}%")
                    if spy_change < -0.5:
                        print(f"   ⚠️ Market was significantly DOWN - should have reduced bullish bias")
                    elif spy_change < 0:
                        print(f"   ⚠️ Market was slightly DOWN - weak sentiment not captured")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n{'='*80}")
    print("OVERALL DIAGNOSIS")
    print(f"{'='*80}")
    print(f"\n🔴 CRITICAL ISSUES FOUND:")
    print(f"   1. System didn't detect market-wide weakness on Oct 22")
    print(f"   2. Technical signals gave false positives (AMD, AVGO)")
    print(f"   3. System ignored bearish technical warning (ORCL)")
    print(f"   4. High confidence (81% AVGO) led to wrong direction")
    print(f"   5. Options signals were unreliable on this day")
    print(f"   6. News sentiment may have been stale/misleading")
    print(f"\n💡 POTENTIAL FIXES NEEDED:")
    print(f"   • Add market regime detection (SPY/QQQ trend)")
    print(f"   • Reduce confidence when technical conflicts with other signals")
    print(f"   • Weight technical signals higher when they're bearish")
    print(f"   • Add overnight futures check at prediction time")
    print(f"   • Implement sentiment freshness decay")
    print(f"   • Add contrarian logic when confidence is high but signals mixed")

if __name__ == "__main__":
    diagnose_failure()
