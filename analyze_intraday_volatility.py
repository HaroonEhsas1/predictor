#!/usr/bin/env python3
"""
Analyze ACTUAL intraday volatility for AMD and AVGO
Not just overnight gaps, but HIGH-LOW range during regular trading hours
This shows realistic move expectations for next-day predictions
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def analyze_intraday_volatility(symbol: str, days: int = 90):
    """
    Analyze typical intraday moves (high-low range)
    This is what actually happens during trading hours
    """
    print(f"\n{'='*80}")
    print(f"INTRADAY VOLATILITY ANALYSIS: {symbol}")
    print(f"{'='*80}")
    
    # Get historical data
    ticker = yf.Ticker(symbol)
    data = ticker.history(period=f"{days}d")
    
    if len(data) < 20:
        print(f"Not enough data for {symbol}")
        return None
    
    # Calculate intraday range (high - low)
    data['intraday_range'] = data['High'] - data['Low']
    data['intraday_range_pct'] = (data['intraday_range'] / data['Open']) * 100
    
    # Calculate move from open to close (regular hours move)
    data['open_to_close'] = abs(data['Close'] - data['Open'])
    data['open_to_close_pct'] = (data['open_to_close'] / data['Open']) * 100
    
    # Calculate overnight gap (previous close to today's open)
    data['overnight_gap'] = data['Open'] - data['Close'].shift(1)
    data['overnight_gap_pct'] = (data['overnight_gap'] / data['Close'].shift(1)) * 100
    
    # Filter out extreme outliers (earnings, news events)
    # Remove top 10% (special events) to get NORMAL trading days
    normal_days = data[data['intraday_range_pct'] <= data['intraday_range_pct'].quantile(0.90)]
    
    # Statistics
    results = {
        'symbol': symbol,
        'avg_price': data['Close'].mean(),
        
        # Intraday Range (High - Low) - FULL potential
        'intraday_range_avg': normal_days['intraday_range'].mean(),
        'intraday_range_pct_avg': normal_days['intraday_range_pct'].mean(),
        'intraday_range_median': normal_days['intraday_range'].median(),
        'intraday_range_pct_median': normal_days['intraday_range_pct'].median(),
        
        # Open to Close - ACTUAL directional move in regular hours
        'open_to_close_avg': normal_days['open_to_close'].mean(),
        'open_to_close_pct_avg': normal_days['open_to_close_pct'].mean(),
        'open_to_close_median': normal_days['open_to_close'].median(),
        'open_to_close_pct_median': normal_days['open_to_close_pct'].median(),
        
        # Overnight Gap - WHAT WE'RE PREDICTING
        'overnight_gap_avg': abs(normal_days['overnight_gap']).mean(),
        'overnight_gap_pct_avg': abs(normal_days['overnight_gap_pct']).mean(),
        'overnight_gap_median': abs(normal_days['overnight_gap']).median(),
        'overnight_gap_pct_median': abs(normal_days['overnight_gap_pct']).median(),
    }
    
    return results, data, normal_days

def print_analysis(results):
    """Print detailed analysis"""
    if not results:
        return
    
    print(f"\n📊 AVERAGE PRICE: ${results['avg_price']:.2f}")
    print(f"\n" + "="*80)
    print("1️⃣ INTRADAY RANGE (High - Low) - Total Daily Volatility")
    print("="*80)
    print(f"   Average: ${results['intraday_range_avg']:.2f} ({results['intraday_range_pct_avg']:.2f}%)")
    print(f"   Median:  ${results['intraday_range_median']:.2f} ({results['intraday_range_pct_median']:.2f}%)")
    print(f"   → This is HIGH to LOW range (max daily volatility)")
    
    print(f"\n" + "="*80)
    print("2️⃣ OPEN TO CLOSE (Regular Hours Directional Move)")
    print("="*80)
    print(f"   Average: ${results['open_to_close_avg']:.2f} ({results['open_to_close_pct_avg']:.2f}%)")
    print(f"   Median:  ${results['open_to_close_median']:.2f} ({results['open_to_close_pct_median']:.2f}%)")
    print(f"   → This is typical ACTUAL move during 9:30-4pm")
    
    print(f"\n" + "="*80)
    print("3️⃣ OVERNIGHT GAP (What We Predict)")
    print("="*80)
    print(f"   Average: ${results['overnight_gap_avg']:.2f} ({results['overnight_gap_pct_avg']:.2f}%)")
    print(f"   Median:  ${results['overnight_gap_median']:.2f} ({results['overnight_gap_pct_median']:.2f}%)")
    print(f"   → This is CLOSE to OPEN gap (what we're predicting)")

def recommend_targets(amd_results, avgo_results):
    """Recommend realistic targets based on analysis"""
    print(f"\n\n" + "="*80)
    print("🎯 RECOMMENDED TARGET ADJUSTMENTS")
    print("="*80)
    
    print(f"\n📊 AMD:")
    print(f"   Current Target Logic: 1.83% (overnight gap average)")
    print(f"   ")
    print(f"   ACTUAL DATA:")
    print(f"   - Overnight Gap Avg: ${amd_results['overnight_gap_avg']:.2f} ({amd_results['overnight_gap_pct_avg']:.2f}%)")
    print(f"   - Open→Close Avg: ${amd_results['open_to_close_avg']:.2f} ({amd_results['open_to_close_pct_avg']:.2f}%)")
    print(f"   - Intraday Range: ${amd_results['intraday_range_avg']:.2f} ({amd_results['intraday_range_pct_avg']:.2f}%)")
    print(f"   ")
    print(f"   RECOMMENDATION:")
    if amd_results['open_to_close_pct_avg'] < amd_results['overnight_gap_pct_avg']:
        print(f"   ⚠️ Regular hours moves ({amd_results['open_to_close_pct_avg']:.2f}%) are LESS than overnight gaps!")
        print(f"   → For NEXT-DAY predictions, target should be:")
        print(f"      Conservative: ${amd_results['open_to_close_avg']:.2f} ({amd_results['open_to_close_pct_avg']:.2f}%)")
        print(f"      Normal: ${amd_results['overnight_gap_avg']:.2f} ({amd_results['overnight_gap_pct_avg']:.2f}%)")
        print(f"      Aggressive: ${amd_results['intraday_range_avg']:.2f} ({amd_results['intraday_range_pct_avg']:.2f}%)")
    
    print(f"\n📊 AVGO:")
    print(f"   Current Target Logic: 1.22% (overnight gap average)")
    print(f"   ")
    print(f"   ACTUAL DATA:")
    print(f"   - Overnight Gap Avg: ${avgo_results['overnight_gap_avg']:.2f} ({avgo_results['overnight_gap_pct_avg']:.2f}%)")
    print(f"   - Open→Close Avg: ${avgo_results['open_to_close_avg']:.2f} ({avgo_results['open_to_close_pct_avg']:.2f}%)")
    print(f"   - Intraday Range: ${avgo_results['intraday_range_avg']:.2f} ({avgo_results['intraday_range_pct_avg']:.2f}%)")
    print(f"   ")
    print(f"   RECOMMENDATION:")
    if avgo_results['open_to_close_pct_avg'] < avgo_results['overnight_gap_pct_avg']:
        print(f"   ⚠️ Regular hours moves ({avgo_results['open_to_close_pct_avg']:.2f}%) are LESS than overnight gaps!")
        print(f"   → For NEXT-DAY predictions, target should be:")
        print(f"      Conservative: ${avgo_results['open_to_close_avg']:.2f} ({avgo_results['open_to_close_pct_avg']:.2f}%)")
        print(f"      Normal: ${avgo_results['overnight_gap_avg']:.2f} ({avgo_results['overnight_gap_pct_avg']:.2f}%)")
        print(f"      Aggressive: ${avgo_results['intraday_range_avg']:.2f} ({avgo_results['intraday_range_pct_avg']:.2f}%)")
    
    print(f"\n" + "="*80)
    print("💡 KEY INSIGHT:")
    print("="*80)
    
    amd_ratio = amd_results['intraday_range_avg'] / avgo_results['intraday_range_avg']
    print(f"\nAMD intraday range: ${amd_results['intraday_range_avg']:.2f}")
    print(f"AVGO intraday range: ${avgo_results['intraday_range_avg']:.2f}")
    print(f"Ratio: {amd_ratio:.2f}x")
    
    if amd_ratio < 1.2:
        print(f"\n⚠️ WARNING: AMD and AVGO have similar DOLLAR ranges!")
        print(f"   But AMD price is ${amd_results['avg_price']:.2f} vs AVGO ${avgo_results['avg_price']:.2f}")
        print(f"   AMD is actually MORE volatile in PERCENTAGE terms")
        print(f"   Current system correctly uses PERCENTAGE targets, not dollar targets!")
    else:
        print(f"\n✅ AMD moves {amd_ratio:.2f}x more than AVGO in absolute dollars")
        print(f"   This is appropriate given the price difference")

if __name__ == "__main__":
    print("\n" + "="*80)
    print("ANALYZING REAL INTRADAY VOLATILITY")
    print("Checking: Regular market hours moves (not just overnight gaps)")
    print("Period: Last 90 days (normal trading only)")
    print("="*80)
    
    # Analyze both stocks
    amd_results, amd_data, amd_normal = analyze_intraday_volatility('AMD', days=90)
    avgo_results, avgo_data, avgo_normal = analyze_intraday_volatility('AVGO', days=90)
    
    # Print analysis
    if amd_results:
        print_analysis(amd_results)
    
    if avgo_results:
        print_analysis(avgo_results)
    
    # Recommendations
    if amd_results and avgo_results:
        recommend_targets(amd_results, avgo_results)
    
    print(f"\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)
