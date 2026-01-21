#!/usr/bin/env python3
"""Quick ORCL Analysis for Configuration"""
import yfinance as yf
import numpy as np

ticker = yf.Ticker("ORCL")
data = ticker.history(period="90d")

# Filter normal days (remove top 10% volatility)
data['range_pct'] = ((data['High'] - data['Low']) / data['Open']) * 100
data['gap_pct'] = abs((data['Open'] - data['Close'].shift(1)) / data['Close'].shift(1)) * 100
data['move_pct'] = abs((data['Close'] - data['Open']) / data['Open']) * 100

normal = data[data['range_pct'] <= data['range_pct'].quantile(0.90)]

print("ORCL ANALYSIS (90 days, normal trading):")
print(f"Average Price: ${data['Close'].mean():.2f}")
print(f"Intraday Range: {normal['range_pct'].mean():.2f}% (${normal['High'].mean() - normal['Low'].mean():.2f})")
print(f"Overnight Gap: {normal['gap_pct'].mean():.2f}%")
print(f"Regular Hours Move: {normal['move_pct'].mean():.2f}%")
print(f"\nRecommended Config:")
print(f"  typical_volatility: {normal['range_pct'].mean()/100:.4f}")
print(f"  historical_avg_gap: {(normal['gap_pct'].mean() + normal['move_pct'].mean())/2/100:.4f}")
print(f"\nStock Characteristics:")
print(f"  Sector: Enterprise Software")
print(f"  Type: Large-cap ($300B+)")
print(f"  Style: Value/Dividend")
print(f"  Volatility: {'Low' if normal['range_pct'].mean() < 2 else 'Medium' if normal['range_pct'].mean() < 3 else 'High'}")
