#!/usr/bin/env python3
"""
Prediction Bias Diagnostic Tool
Identifies why the system always predicts UP
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from comprehensive_nextday_predictor import ComprehensiveNextDayPredictor
from stock_config import get_active_stocks
import yfinance as yf
from datetime import datetime, timedelta

def analyze_recent_predictions():
    """
    Analyze if predictions were correct for recent days
    """
    print("="*80)
    print("🔍 PREDICTION BIAS DIAGNOSTIC TOOL")
    print("="*80)
    
    stocks = get_active_stocks()
    print(f"\n📊 Analyzing: {', '.join(stocks)}")
    
    for symbol in stocks:
        print(f"\n{'='*80}")
        print(f"📈 {symbol} - ACTUAL PERFORMANCE")
        print(f"{'='*80}")
        
        try:
            # Get last 5 days of actual data
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="5d")
            
            if len(hist) < 2:
                print(f"   ⚠️ Not enough data for {symbol}")
                continue
            
            print(f"\n   Last 5 Days Actual Performance:")
            print(f"   {'Date':<12} {'Open':<10} {'Close':<10} {'Change':<10} {'Direction':<10}")
            print(f"   {'-'*60}")
            
            up_days = 0
            down_days = 0
            
            for i in range(len(hist)):
                date = hist.index[i].strftime('%Y-%m-%d')
                open_price = hist['Open'].iloc[i]
                close_price = hist['Close'].iloc[i]
                change = ((close_price - open_price) / open_price) * 100
                direction = "📈 UP" if change > 0 else "📉 DOWN"
                
                if change > 0:
                    up_days += 1
                else:
                    down_days += 1
                
                print(f"   {date:<12} ${open_price:<9.2f} ${close_price:<9.2f} {change:>+6.2f}%   {direction}")
            
            print(f"\n   Summary: {up_days} UP days, {down_days} DOWN days")
            print(f"   UP Rate: {(up_days/(up_days+down_days))*100:.1f}%")
            
            # Check today's prediction
            print(f"\n   🎯 Running prediction for tomorrow...")
            predictor = ComprehensiveNextDayPredictor(symbol=symbol)
            prediction = predictor.generate_comprehensive_prediction()
            
            if prediction:
                print(f"\n   System Predicts: {prediction['direction']}")
                print(f"   Confidence: {prediction['confidence']:.1f}%")
                print(f"   Total Score: {prediction.get('total_score', 'N/A')}")
            
        except Exception as e:
            print(f"   ❌ Error analyzing {symbol}: {e}")


def check_factor_bias():
    """
    Check if individual factors have a bias
    """
    print(f"\n\n{'='*80}")
    print(f"🔬 FACTOR BIAS ANALYSIS")
    print(f"{'='*80}")
    
    print("""
    Checking for systematic biases in scoring logic:
    
    1. NEWS BIAS:
       - Are we counting more bullish keywords than bearish?
       - Are API sentiment scores naturally positive?
    
    2. OPTIONS BIAS:
       - P/C ratio thresholds: < 0.7 = bullish, > 1.3 = bearish
       - Is this range too wide? (0.7-1.3 is 'neutral')
       - Market is often slightly bullish (P/C ~0.8), so we classify as neutral
    
    3. TECHNICAL BIAS:
       - RSI overbought threshold: 70 (should be 65?)
       - If stock is in uptrend with RSI 65-70, we give bullish score
       - But RSI 65-70 often precedes reversals!
    
    4. FUTURES BIAS:
       - Are we overweighting small positive futures moves?
       - ES +0.1% shouldn't translate to strong bullish signal
    
    5. ANALYST BIAS:
       - Analysts are notoriously bullish (80% buy ratings typical)
       - This creates systematic upward bias!
    
    6. MOMENTUM TRAP:
       - We're REACTIVE not PREDICTIVE
       - Stock rallies → News positive → Options bullish → Technical uptrend
       - We predict more UP → But rallies eventually reverse!
    """)
    
    print(f"\n{'='*80}")
    print(f"🚨 IDENTIFIED ISSUES:")
    print(f"{'='*80}")
    
    print("""
    ISSUE #1: ANALYST RATINGS BIAS
       - Analysts give 70-80% buy ratings even in bear markets
       - This creates +0.04 to +0.06 constant bullish bias
       - FIX: Reduce weight or require upgrades/downgrades, not absolute ratings
    
    ISSUE #2: RSI THRESHOLD TOO HIGH
       - Current: RSI > 70 = overbought penalty
       - Problem: RSI 60-70 is still overbought territory
       - ORCL had RSI 68.6 → got bullish score, then dropped $8
       - FIX: Lower threshold to RSI > 65 for penalty
    
    ISSUE #3: OPTIONS NEUTRAL ZONE TOO WIDE
       - P/C 0.7-1.3 is 'neutral' (score = 0)
       - P/C 0.7-1.0 is actually bullish positioning
       - Market naturally sits at P/C ~0.8-1.0
       - FIX: Adjust thresholds: <0.8 bullish, >1.2 bearish
    
    ISSUE #4: NEWS RECENCY BIAS
       - Recent news is about recent moves (lagging)
       - Stock rallies → news positive → but rally is over
       - FIX: Weight news less, or focus on forward-looking news
    
    ISSUE #5: MOMENTUM CONTINUATION ASSUMPTION
       - We assume UP today → UP tomorrow
       - But markets mean-revert, especially after strong moves
       - FIX: Add reversal detection for overextended moves
    
    ISSUE #6: LACK OF CONTRARIAN SIGNALS
       - When everything is bullish, it's often a top
       - When RSI high + options bullish + news positive = REVERSAL RISK
       - FIX: Add contrarian logic for extreme bullish readings
    """)


def suggest_fixes():
    """
    Suggest specific fixes
    """
    print(f"\n\n{'='*80}")
    print(f"🔧 RECOMMENDED FIXES:")
    print(f"{'='*80}")
    
    print("""
    FIX #1: LOWER RSI OVERBOUGHT THRESHOLD
       Change line 1115: if rsi > 70:  →  if rsi > 65:
       
    FIX #2: TIGHTEN OPTIONS THRESHOLDS
       Change line 207: if options_data['put_call_ratio'] < 0.7:  →  < 0.8:
       Change line 210: elif options_data['put_call_ratio'] > 1.3:  →  > 1.2:
       
    FIX #3: ADD REVERSAL DETECTION
       If RSI > 65 AND options bullish AND news very positive:
          → High probability of reversal (contrarian signal)
          → Reduce confidence or flip to DOWN
       
    FIX #4: REDUCE ANALYST WEIGHT
       Analysts are systematically bullish
       Current analyst_ratings weight: 0.04-0.06
       Reduce to: 0.02 or require recent upgrades only
       
    FIX #5: ADD MEAN REVERSION LOGIC
       If stock up 2+ days in a row with RSI > 60:
          → Increase probability of DOWN prediction
          → Markets don't go straight up forever
       
    FIX #6: EXTREME READING PENALTY
       If total_score > 0.30 (very bullish):
          → Apply penalty: total_score = 0.30 + (total_score - 0.30) * 0.5
          → Extreme bullish readings often precede reversals
    """)
    
    print(f"\n{'='*80}")
    print(f"⚠️ CRITICAL INSIGHT:")
    print(f"{'='*80}")
    print("""
    The system is REACTIVE (following momentum) not PREDICTIVE (anticipating reversals).
    
    Your memory says: "Close UP → Predict UP overnight" (no flips)
    But this is the problem! Markets don't work that way.
    
    Real pattern:
    - Close UP → Often gaps DOWN next day (profit taking)
    - Close DOWN → Often gaps UP next day (bargain hunting)
    - Strong rally + overbought RSI → Reversal coming
    - Heavy selloff + oversold RSI → Bounce coming
    
    The system needs to be MORE CONTRARIAN, not LESS!
    """)


if __name__ == "__main__":
    # Run diagnostics
    analyze_recent_predictions()
    check_factor_bias()
    suggest_fixes()
    
    print(f"\n\n{'='*80}")
    print(f"✅ DIAGNOSTIC COMPLETE")
    print(f"{'='*80}")
    print(f"\nNext steps:")
    print(f"1. Review the identified biases")
    print(f"2. Apply the recommended fixes")
    print(f"3. Re-test predictions")
    print(f"4. Validate against actual market moves\n")
