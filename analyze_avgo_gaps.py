#!/usr/bin/env python3
"""
Analyze AVGO overnight gap behavior
Check if AVGO flips direction overnight or continues momentum
"""

import yfinance as yf
import pandas as pd

def analyze_overnight_gaps(symbol='AVGO', period='6mo'):
    """Analyze overnight gap patterns"""
    
    print(f"\n{'='*80}")
    print(f"📊 {symbol} OVERNIGHT GAP & MOMENTUM ANALYSIS (Last {period})")
    print(f"{'='*80}\n")
    
    # Get historical data
    ticker = yf.Ticker(symbol)
    hist = ticker.history(period=period, interval='1d')
    
    if hist.empty:
        print("❌ No data available")
        return
    
    # Analyze gaps and momentum
    gaps = []
    
    for i in range(1, len(hist)):
        prev_close = hist['Close'].iloc[i-1]
        prev_open = hist['Open'].iloc[i-1]
        curr_open = hist['Open'].iloc[i]
        curr_close = hist['Close'].iloc[i]
        
        # Calculate overnight gap
        gap_pct = ((curr_open - prev_close) / prev_close) * 100
        
        # Previous day direction
        prev_intraday_move = ((prev_close - prev_open) / prev_open) * 100
        prev_direction = 'UP' if prev_intraday_move > 0 else 'DOWN'
        
        # Current day direction
        curr_intraday_move = ((curr_close - curr_open) / curr_open) * 100
        curr_direction = 'UP' if curr_intraday_move > 0 else 'DOWN'
        
        # Check if momentum continued or flipped
        momentum_pattern = 'CONTINUE' if prev_direction == curr_direction else 'FLIP'
        
        # Check if gap direction matches previous day
        gap_direction = 'UP' if gap_pct > 0 else 'DOWN'
        gap_alignment = 'ALIGNED' if gap_direction == prev_direction else 'REVERSED'
        
        gaps.append({
            'Date': hist.index[i].strftime('%Y-%m-%d'),
            'Gap_%': round(gap_pct, 2),
            'Gap_Dir': gap_direction,
            'Prev_Day': prev_direction,
            'Curr_Day': curr_direction,
            'Momentum': momentum_pattern,
            'Gap_vs_Prev': gap_alignment
        })
    
    df = pd.DataFrame(gaps)
    
    # Statistics
    print("📈 OVERNIGHT GAP STATISTICS:")
    print(f"   Total Trading Days: {len(df)}")
    print(f"   Average Gap Size: {df['Gap_%'].abs().mean():.2f}%")
    print(f"   Largest Gap Up: +{df['Gap_%'].max():.2f}%")
    print(f"   Largest Gap Down: {df['Gap_%'].min():.2f}%")
    print()
    
    print("📊 GAP DIRECTION:")
    gap_up = len(df[df['Gap_%'] > 0])
    gap_down = len(df[df['Gap_%'] < 0])
    print(f"   Gap UP: {gap_up} days ({gap_up/len(df)*100:.1f}%)")
    print(f"   Gap DOWN: {gap_down} days ({gap_down/len(df)*100:.1f}%)")
    print()
    
    print("🎯 MOMENTUM CONTINUATION vs REVERSAL:")
    continue_count = len(df[df['Momentum'] == 'CONTINUE'])
    flip_count = len(df[df['Momentum'] == 'FLIP'])
    print(f"   MOMENTUM CONTINUES: {continue_count} days ({continue_count/len(df)*100:.1f}%)")
    print(f"   MOMENTUM FLIPS: {flip_count} days ({flip_count/len(df)*100:.1f}%)")
    print()
    
    print("🔄 GAP ALIGNMENT WITH PREVIOUS DAY:")
    aligned = len(df[df['Gap_vs_Prev'] == 'ALIGNED'])
    reversed = len(df[df['Gap_vs_Prev'] == 'REVERSED'])
    print(f"   Gap ALIGNED (gap continues prev day): {aligned} days ({aligned/len(df)*100:.1f}%)")
    print(f"   Gap REVERSED (gap opposite prev day): {reversed} days ({reversed/len(df)*100:.1f}%)")
    print()
    
    # Key finding
    print("🎯 KEY FINDING FOR PREDICTION SYSTEM:")
    if aligned > reversed:
        print(f"   ✅ AVGO shows MOMENTUM CONTINUATION overnight")
        print(f"      If closes UP → likely gaps UP next morning ({aligned/len(df)*100:.1f}% of time)")
        print(f"      If closes DOWN → likely gaps DOWN next morning")
        print(f"      → EXCELLENT for close-to-open prediction!")
    else:
        print(f"   ⚠️ AVGO shows OVERNIGHT REVERSALS")
        print(f"      If closes UP → often gaps DOWN next morning ({reversed/len(df)*100:.1f}% of time)")
        print(f"      If closes DOWN → often gaps UP next morning")
        print(f"      → POOR for close-to-open prediction!")
    
    print()
    print("📅 RECENT OVERNIGHT GAPS (Last 15 Days):")
    print(df.tail(15).to_string(index=False))
    print()
    
    # Calculate significant gaps
    sig_gaps = df[df['Gap_%'].abs() > 1.0]
    print(f"\n💥 SIGNIFICANT GAPS (>1%):")
    print(f"   Count: {len(sig_gaps)} out of {len(df)} days ({len(sig_gaps)/len(df)*100:.1f}%)")
    if not sig_gaps.empty:
        print(sig_gaps.tail(10).to_string(index=False))

if __name__ == "__main__":
    analyze_overnight_gaps('AVGO', period='6mo')
    
    print(f"\n{'='*80}")
    print("💡 COMPARISON: Analyzing AMD for reference...")
    print(f"{'='*80}")
    
    analyze_overnight_gaps('AMD', period='6mo')
