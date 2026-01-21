"""
ADAPTIVE THRESHOLDS - VIX-based dynamic threshold adjustment

Adjusts signal strength thresholds based on market volatility:
- Low VIX (calm market): Lower threshold = More trades
- Medium VIX (normal): Standard threshold
- High VIX (volatile): Higher threshold = Safer trades

Compatible with existing signal_strength_system.py
"""

import yfinance as yf
from datetime import datetime, timedelta

def get_current_vix():
    """Get current VIX value"""
    try:
        vix = yf.Ticker("^VIX")
        data = vix.history(period="1d")
        if not data.empty:
            current_vix = data['Close'].iloc[-1]
            return current_vix
        return None
    except:
        return None

def get_adaptive_threshold():
    """
    Get adaptive threshold based on VIX
    
    Returns:
        dict: {
            'threshold': float (dominance points needed),
            'vix': float (current VIX value),
            'regime': str (market volatility regime),
            'reasoning': str (explanation)
        }
    """
    
    vix = get_current_vix()
    
    # Default if VIX unavailable
    if vix is None:
        return {
            'threshold': 12,
            'vix': None,
            'regime': 'UNKNOWN',
            'reasoning': 'VIX unavailable - using standard 12-point threshold'
        }
    
    # Adaptive thresholds based on VIX
    if vix < 15:
        # CALM MARKET - Lower threshold for more opportunities
        threshold = 10
        regime = 'CALM'
        reasoning = f"VIX {vix:.1f} < 15: Calm market, using lower threshold (10 points) for more trades"
        
    elif vix < 20:
        # NORMAL MARKET - Standard threshold
        threshold = 12
        regime = 'NORMAL'
        reasoning = f"VIX {vix:.1f} in 15-20: Normal volatility, standard threshold (12 points)"
        
    elif vix < 30:
        # ELEVATED VOLATILITY - Higher threshold for safety
        threshold = 15
        regime = 'ELEVATED'
        reasoning = f"VIX {vix:.1f} in 20-30: Elevated volatility, higher threshold (15 points) for safety"
        
    else:
        # HIGH VOLATILITY - Much higher threshold, very selective
        threshold = 18
        regime = 'HIGH'
        reasoning = f"VIX {vix:.1f} > 30: High volatility, much higher threshold (18 points) - trade only best setups"
    
    return {
        'threshold': threshold,
        'vix': vix,
        'regime': regime,
        'reasoning': reasoning
    }

def print_threshold_status():
    """Print current threshold status"""
    info = get_adaptive_threshold()
    
    print("\n" + "="*80)
    print("📊 ADAPTIVE THRESHOLD STATUS")
    print("="*80)
    
    if info['vix'] is not None:
        print(f"\nVIX Level: {info['vix']:.2f}")
    else:
        print(f"\nVIX Level: Unavailable")
    
    print(f"Market Regime: {info['regime']}")
    print(f"Threshold: {info['threshold']} points")
    print(f"\nReasoning: {info['reasoning']}")
    
    print("\n" + "="*80 + "\n")
    
    return info


if __name__ == "__main__":
    # Test the adaptive threshold system
    info = print_threshold_status()
    
    print("THRESHOLD EXAMPLES:")
    print(f"  VIX 12 (calm):      10-point threshold → More trades")
    print(f"  VIX 18 (normal):    12-point threshold → Standard")
    print(f"  VIX 25 (elevated):  15-point threshold → Fewer trades")
    print(f"  VIX 35 (high):      18-point threshold → Very selective")
