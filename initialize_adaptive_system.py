#!/usr/bin/env python3
"""
Initialize Adaptive Threshold System from Historical Market Data
Run this ONCE to bootstrap the learning system with real market-derived values
"""

import yfinance as yf
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from adaptive_threshold_engine import adaptive_threshold_engine

def bootstrap_from_historical_data(symbol="AMD", years=2):
    """
    Bootstrap adaptive thresholds from REAL historical market data
    Analyzes actual market behavior to set initial learning values
    """
    
    print(f"📊 Bootstrapping adaptive system from {years} years of {symbol} data...")
    
    # Fetch historical data
    end_date = datetime.now()
    start_date = end_date - timedelta(days=years*365)
    
    ticker = yf.Ticker(symbol)
    hist = ticker.history(start=start_date, end=end_date, interval='1d')
    
    if hist.empty:
        print("❌ No historical data available")
        return False
    
    print(f"✅ Loaded {len(hist)} days of historical data")
    
    # Calculate historical volatility
    hist['returns'] = hist['Close'].pct_change()
    hist['volatility'] = hist['returns'].rolling(20).std() * np.sqrt(252)
    
    # Classify historical periods by volatility regime
    volatility_values = hist['volatility'].dropna()
    
    vol_percentiles = {
        'p10': volatility_values.quantile(0.10),
        'p30': volatility_values.quantile(0.30),
        'p70': volatility_values.quantile(0.70),
        'p90': volatility_values.quantile(0.90)
    }
    
    print(f"📈 Volatility Percentiles (from real data):")
    for p, val in vol_percentiles.items():
        print(f"   {p}: {val:.4f}")
    
    # Analyze optimal confidence thresholds by regime
    # (In production, this would analyze actual prediction outcomes)
    # For bootstrap, we use volatility-normalized heuristics
    
    # Normalize volatility to 0-0.3 range for threshold calculation
    vol_normalized = {
        'p10': min(vol_percentiles['p10'], 0.30),
        'p30': min(vol_percentiles['p30'], 0.30),
        'p70': min(vol_percentiles['p70'], 0.30),
        'p90': min(vol_percentiles['p90'], 0.30)
    }
    
    learned_thresholds = {
        'confidence': {
            'low_volatility': float(0.50 + vol_normalized['p10'] * 0.4),  # 0.50-0.62 range
            'normal': float(0.55 + vol_normalized['p30'] * 0.3),          # 0.55-0.64 range
            'high_volatility': float(0.60 + vol_normalized['p70'] * 0.3),# 0.60-0.69 range
            'crisis': float(0.70 + vol_normalized['p90'] * 0.5)           # 0.70-0.85 range
        },
        'margin': {
            'low_volatility': float(0.05 + vol_normalized['p10'] * 0.2),  # 0.05-0.11 range
            'normal': float(0.08 + vol_normalized['p30'] * 0.2),          # 0.08-0.14 range
            'high_volatility': float(0.10 + vol_normalized['p70'] * 0.2),# 0.10-0.16 range
            'crisis': float(0.15 + vol_normalized['p90'] * 0.3)           # 0.15-0.24 range
        },
        'price_movement_percentiles': {
            # Price movement percentiles (for reference, not for confidence bounds)
            'p25': float(hist['Close'].pct_change().abs().quantile(0.25)),
            'p50': float(hist['Close'].pct_change().abs().quantile(0.50)),
            'p75': float(hist['Close'].pct_change().abs().quantile(0.75)),
            'p90': float(hist['Close'].pct_change().abs().quantile(0.90))
        },
        'volatility_percentiles': {
            # Volatility percentiles for regime classification
            'p10': float(vol_percentiles['p10']),
            'p30': float(vol_percentiles['p30']),
            'p70': float(vol_percentiles['p70']),
            'p90': float(vol_percentiles['p90'])
        },
        'confidence_bounds': {
            # BOOTSTRAP ONLY: Initial conservative bounds from volatility analysis
            # These WILL BE REPLACED by actual prediction performance data after 50+ predictions
            # See: AdaptiveThresholdEngine._recalibrate_thresholds() for learning logic
            'low_volatility': (float(0.40 + vol_normalized['p10'] * 0.3), 0.85),
            'normal': (float(0.45 + vol_normalized['p30'] * 0.2), 0.80),
            'high_volatility': (float(0.55 + vol_normalized['p70'] * 0.2), 0.90),
            'crisis': (float(0.65 + vol_normalized['p90'] * 0.2), 0.95),
            'bootstrap': True  # Flag indicating these need to be learned from performance
        },
        'last_updated': datetime.now().isoformat(),
        'bootstrap_source': f'{symbol} {years}yr history',
        'requires_initialization': False  # Mark as initialized
    }
    
    # Save learned thresholds
    adaptive_threshold_engine.learned_thresholds = learned_thresholds
    adaptive_threshold_engine.save_learned_thresholds()
    
    print("\n✅ Adaptive system initialized from REAL market data:")
    print(f"   Confidence thresholds: {learned_thresholds['confidence']}")
    print(f"   Margin thresholds: {learned_thresholds['margin']}")
    print(f"   Saved to: {adaptive_threshold_engine.thresholds_file}")
    
    return True

if __name__ == "__main__":
    success = bootstrap_from_historical_data()
    if success:
        print("\n🎯 System ready for adaptive learning!")
    else:
        print("\n❌ Bootstrap failed - will use conservative defaults")
