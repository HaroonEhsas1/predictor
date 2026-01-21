"""
CHECK NVDA OVERNIGHT GAP DATA
Analyzes NVDA's actual overnight gap patterns and characteristics
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def analyze_nvda_overnight_patterns():
    """
    Analyze NVDA's real overnight gap patterns
    """
    
    print("\n" + "="*80)
    print("📊 NVDA OVERNIGHT GAP ANALYSIS")
    print("="*80)
    
    # Fetch NVDA data
    print("\n🔍 Fetching NVDA historical data (last 3 months)...")
    nvda = yf.Ticker("NVDA")
    hist = nvda.history(period="3mo", interval="1d")
    
    if len(hist) == 0:
        print("❌ Could not fetch data")
        return
    
    print(f"✅ Fetched {len(hist)} days of data")
    
    # Calculate overnight gaps
    print("\n📈 Calculating overnight gaps (close to open)...")
    gaps = []
    gap_directions = []
    
    for i in range(1, len(hist)):
        prev_close = hist['Close'].iloc[i-1]
        curr_open = hist['Open'].iloc[i]
        gap_pct = ((curr_open - prev_close) / prev_close) * 100
        gaps.append(abs(gap_pct))
        gap_directions.append('UP' if gap_pct > 0 else 'DOWN')
    
    # Statistics
    avg_gap = np.mean(gaps)
    median_gap = np.median(gaps)
    max_gap = np.max(gaps)
    std_gap = np.std(gaps)
    
    print(f"\n💰 NVDA GAP STATISTICS:")
    print(f"{'='*80}")
    print(f"   Average gap: {avg_gap:.2f}%")
    print(f"   Median gap: {median_gap:.2f}%")
    print(f"   Max gap: {max_gap:.2f}%")
    print(f"   Std deviation: {std_gap:.2f}%")
    
    # Gap size distribution
    small_gaps = sum(1 for g in gaps if g < 0.5)
    medium_gaps = sum(1 for g in gaps if 0.5 <= g < 2.0)
    large_gaps = sum(1 for g in gaps if 2.0 <= g < 4.0)
    huge_gaps = sum(1 for g in gaps if g >= 4.0)
    
    total = len(gaps)
    
    print(f"\n📊 GAP SIZE DISTRIBUTION:")
    print(f"{'='*80}")
    print(f"   Small (<0.5%): {small_gaps} ({small_gaps/total*100:.1f}%)")
    print(f"   Medium (0.5-2%): {medium_gaps} ({medium_gaps/total*100:.1f}%)")
    print(f"   Large (2-4%): {large_gaps} ({large_gaps/total*100:.1f}%)")
    print(f"   Huge (>4%): {huge_gaps} ({huge_gaps/total*100:.1f}%)")
    
    # Volatility
    print(f"\n🔥 VOLATILITY ANALYSIS:")
    print(f"{'='*80}")
    
    # Calculate ATR (14-day)
    high_low = hist['High'] - hist['Low']
    high_close = abs(hist['High'] - hist['Close'].shift())
    low_close = abs(hist['Low'] - hist['Close'].shift())
    
    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    atr_14 = true_range.rolling(window=14).mean().iloc[-1]
    atr_pct = (atr_14 / hist['Close'].iloc[-1]) * 100
    
    print(f"   Current price: ${hist['Close'].iloc[-1]:.2f}")
    print(f"   14-day ATR: ${atr_14:.2f} ({atr_pct:.2f}%)")
    print(f"   Daily range: {atr_pct:.2f}%")
    
    # Momentum continuation
    print(f"\n🎯 MOMENTUM CONTINUATION:")
    print(f"{'='*80}")
    
    # Check how often direction continues
    continuations = 0
    reversals = 0
    
    for i in range(1, len(hist)-1):
        # Check if previous day's close > open (bullish day)
        prev_day_bullish = hist['Close'].iloc[i] > hist['Open'].iloc[i]
        
        # Check if next day opens in same direction
        next_gap_up = hist['Open'].iloc[i+1] > hist['Close'].iloc[i]
        
        if prev_day_bullish and next_gap_up:
            continuations += 1
        elif not prev_day_bullish and not next_gap_up:
            continuations += 1
        else:
            reversals += 1
    
    total_checks = continuations + reversals
    continuation_rate = continuations / total_checks * 100 if total_checks > 0 else 0
    
    print(f"   Momentum continuations: {continuations}")
    print(f"   Momentum reversals: {reversals}")
    print(f"   Continuation rate: {continuation_rate:.1f}%")
    
    # Recent performance
    print(f"\n📅 RECENT PERFORMANCE (Last 30 days):")
    print(f"{'='*80}")
    
    recent_hist = hist.tail(30)
    returns_30d = ((recent_hist['Close'].iloc[-1] - recent_hist['Close'].iloc[0]) / recent_hist['Close'].iloc[0]) * 100
    
    print(f"   30-day return: {returns_30d:+.2f}%")
    print(f"   Trend: {'BULLISH ✅' if returns_30d > 5 else 'BEARISH ❌' if returns_30d < -5 else 'NEUTRAL ⚠️'}")
    
    # Volatility level
    if atr_pct > 4.0:
        vol_level = "EXTREME 🔥"
    elif atr_pct > 3.0:
        vol_level = "VERY HIGH 📈"
    elif atr_pct > 2.0:
        vol_level = "HIGH ⚡"
    else:
        vol_level = "MODERATE ✅"
    
    print(f"   Volatility: {vol_level}")
    
    # Summary for config
    print(f"\n{'='*80}")
    print(f"📋 RECOMMENDED CONFIG VALUES FOR NVDA:")
    print(f"{'='*80}")
    print(f"""
    'NVDA': {{
        'volatility': {atr_pct:.2f}%,  # Daily ATR
        'avg_gap': {avg_gap:.2f}%,  # Average overnight gap
        'momentum_continuation': {continuation_rate:.0f}%,  # How often stays in trend
        'min_confidence': 60%,  # Based on continuation rate
        'typical_gap_range': ({median_gap:.2f}%, {avg_gap + std_gap:.2f}%),
        'volatility_level': '{vol_level}',
    }}
    """)
    
    print(f"\n{'='*80}")
    print(f"✅ ANALYSIS COMPLETE")
    print(f"{'='*80}\n")
    
    return {
        'avg_gap': avg_gap,
        'atr_pct': atr_pct,
        'continuation_rate': continuation_rate,
        'current_price': hist['Close'].iloc[-1]
    }


if __name__ == "__main__":
    analyze_nvda_overnight_patterns()
