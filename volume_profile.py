"""
VOLUME PROFILE / VWAP ANALYSIS

Analyzes:
- Volume-Weighted Average Price (VWAP)
- Previous day volume profile
- Key support/resistance from volume

Compatible with existing system
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def calculate_vwap(symbol, days=1):
    """
    Calculate VWAP for a stock
    
    Args:
        symbol: Stock symbol
        days: Number of days to calculate (default 1 for today's VWAP)
    
    Returns:
        dict: VWAP info and trading signals
    """
    
    try:
        # Get intraday data if available, otherwise daily
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days+5)
        
        ticker = yf.Ticker(symbol)
        data = ticker.history(start=start_date, end=end_date, interval='1d')
        
        if data.empty:
            return get_default_vwap(symbol)
        
        # Calculate VWAP (using daily data as proxy)
        # True VWAP needs intraday data, but we can use daily average
        typical_price = (data['High'] + data['Low'] + data['Close']) / 3
        volume = data['Volume']
        
        vwap = (typical_price * volume).sum() / volume.sum()
        
        # Get current price
        current_price = data['Close'].iloc[-1]
        prev_close = data['Close'].iloc[-2] if len(data) > 1 else current_price
        
        # Calculate distance from VWAP
        vwap_distance_pct = ((current_price - vwap) / vwap) * 100
        
        # Calculate volume metrics
        avg_volume = volume.mean()
        recent_volume = volume.iloc[-1]
        volume_ratio = recent_volume / avg_volume
        
        # Determine signal
        if abs(vwap_distance_pct) < 0.5:
            position = 'AT_VWAP'
            signal_strength = 0
            signal = "Neutral - price at VWAP (equilibrium)"
            
        elif vwap_distance_pct > 2:
            position = 'ABOVE_VWAP'
            signal_strength = min(vwap_distance_pct / 2, 20)  # Max 20 points
            signal = f"Bullish - {vwap_distance_pct:.1f}% above VWAP (strong buyers)"
            
        elif vwap_distance_pct < -2:
            position = 'BELOW_VWAP'
            signal_strength = max(vwap_distance_pct / 2, -20)  # Max -20 points
            signal = f"Bearish - {abs(vwap_distance_pct):.1f}% below VWAP (strong sellers)"
            
        elif vwap_distance_pct > 0.5:
            position = 'SLIGHTLY_ABOVE'
            signal_strength = vwap_distance_pct * 5  # Weaker signal
            signal = f"Slightly bullish - {vwap_distance_pct:.1f}% above VWAP"
            
        else:  # vwap_distance_pct < -0.5
            position = 'SLIGHTLY_BELOW'
            signal_strength = vwap_distance_pct * 5  # Weaker signal
            signal = f"Slightly bearish - {abs(vwap_distance_pct):.1f}% below VWAP"
        
        # Volume confirmation
        if volume_ratio > 1.5:
            volume_signal = f"High volume ({volume_ratio:.1f}x avg) confirms move"
        elif volume_ratio < 0.7:
            volume_signal = f"Low volume ({volume_ratio:.1f}x avg) - weak move"
        else:
            volume_signal = f"Normal volume ({volume_ratio:.1f}x avg)"
        
        return {
            'symbol': symbol,
            'vwap': vwap,
            'current_price': current_price,
            'vwap_distance_pct': vwap_distance_pct,
            'position': position,
            'signal': signal,
            'signal_strength': signal_strength,
            'volume_ratio': volume_ratio,
            'volume_signal': volume_signal,
            'success': True
        }
        
    except Exception as e:
        return {
            **get_default_vwap(symbol),
            'error': str(e),
            'success': False
        }

def get_default_vwap(symbol):
    """Default VWAP info if calculation fails"""
    return {
        'symbol': symbol,
        'vwap': None,
        'current_price': None,
        'vwap_distance_pct': 0,
        'position': 'UNKNOWN',
        'signal': "VWAP unavailable - using neutral",
        'signal_strength': 0,
        'volume_ratio': 1.0,
        'volume_signal': "Volume data unavailable",
        'success': False
    }

def get_volume_profile_signal(symbol):
    """
    Get trading signal from volume profile analysis
    
    Args:
        symbol: Stock symbol
    
    Returns:
        dict: Signal strength for use in signal_strength_system
    """
    
    vwap_info = calculate_vwap(symbol)
    
    # Convert to signal strength format
    if not vwap_info['success']:
        return {
            'strength': 0,
            'direction': 'NEUTRAL',
            'reasoning': vwap_info['signal']
        }
    
    signal_strength = vwap_info['signal_strength']
    
    if signal_strength > 5:
        direction = 'BULLISH'
    elif signal_strength < -5:
        direction = 'BEARISH'
    else:
        direction = 'NEUTRAL'
    
    return {
        'strength': abs(signal_strength),
        'direction': direction,
        'reasoning': vwap_info['signal'],
        'volume_confirmation': vwap_info['volume_signal']
    }

def print_vwap_analysis(symbols):
    """Print VWAP analysis for multiple stocks"""
    
    print("\n" + "="*80)
    print("📊 VOLUME PROFILE / VWAP ANALYSIS")
    print("="*80)
    
    results = {}
    
    for symbol in symbols:
        print(f"\n{symbol}:")
        vwap_info = calculate_vwap(symbol)
        results[symbol] = vwap_info
        
        if vwap_info['success']:
            print(f"  Current Price: ${vwap_info['current_price']:.2f}")
            print(f"  VWAP: ${vwap_info['vwap']:.2f}")
            print(f"  Distance: {vwap_info['vwap_distance_pct']:+.2f}%")
            print(f"  Position: {vwap_info['position']}")
            print(f"  Signal: {vwap_info['signal']}")
            print(f"  {vwap_info['volume_signal']}")
        else:
            print(f"  ⚠️ {vwap_info['signal']}")
    
    print("\n" + "="*80 + "\n")
    
    return results


if __name__ == "__main__":
    # Test VWAP analysis
    symbols = ['AMD', 'NVDA', 'META', 'AVGO']
    
    results = print_vwap_analysis(symbols)
    
    print("VWAP TRADING SIGNALS:")
    print("  >2% above VWAP: Strong bullish (buyers in control)")
    print("  <2% below VWAP: Strong bearish (sellers in control)")
    print("  At VWAP (±0.5%): Equilibrium (no edge)")
