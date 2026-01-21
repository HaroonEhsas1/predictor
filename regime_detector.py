"""
REGIME DETECTION - Identify current market regime

Detects:
- Trending Bull
- Trending Bear
- Range-bound
- High Volatility

Adjusts strategy per regime
Compatible with existing system
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def detect_market_regime(lookback_days=60):
    """
    Detect current market regime
    
    Args:
        lookback_days: Days of history to analyze
    
    Returns:
        dict: Regime info and trading adjustments
    """
    
    try:
        # Get S&P 500 and VIX data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=lookback_days + 20)  # Extra for indicators
        
        spy = yf.Ticker("SPY")
        vix = yf.Ticker("^VIX")
        
        spy_data = spy.history(start=start_date, end=end_date)
        vix_data = vix.history(start=start_date, end=end_date)
        
        if spy_data.empty or vix_data.empty:
            return get_default_regime()
        
        # Calculate indicators
        closes = spy_data['Close']
        
        # 1. Trend detection (20 and 50 day SMA)
        sma_20 = closes.rolling(20).mean()
        sma_50 = closes.rolling(50).mean()
        
        current_price = closes.iloc[-1]
        sma_20_current = sma_20.iloc[-1]
        sma_50_current = sma_50.iloc[-1]
        
        # 2. Volatility (20-day)
        returns = closes.pct_change()
        volatility = returns.rolling(20).std() * np.sqrt(252) * 100  # Annualized %
        current_vol = volatility.iloc[-1]
        
        # 3. VIX level
        current_vix = vix_data['Close'].iloc[-1]
        
        # 4. Recent performance (last 20 days)
        recent_return = (closes.iloc[-1] / closes.iloc[-20] - 1) * 100
        
        # 5. Range detection (20-day high/low)
        high_20 = closes.rolling(20).max().iloc[-1]
        low_20 = closes.rolling(20).min().iloc[-1]
        range_pct = ((high_20 - low_20) / low_20) * 100
        
        # REGIME DETECTION LOGIC
        
        # Trending Bull
        if (current_price > sma_20_current > sma_50_current and
            recent_return > 3 and
            current_vix < 20):
            
            regime = 'TRENDING_BULL'
            confidence = 'HIGH'
            
            adjustments = {
                'gap_trust': 1.1,  # Trust gaps more in bull trend
                'threshold_modifier': 0.9,  # Lower threshold slightly
                'position_size_modifier': 1.0,  # Full size OK
                'max_positions': 4
            }
            
            reasoning = (f"Bullish trend: Price > SMA20 > SMA50, "
                        f"+{recent_return:.1f}% in 20d, VIX {current_vix:.1f}")
            
            strategy = "Follow bullish gaps, full positions, trust momentum"
        
        # Trending Bear
        elif (current_price < sma_20_current < sma_50_current and
              recent_return < -3 and
              current_vix > 20):
            
            regime = 'TRENDING_BEAR'
            confidence = 'HIGH'
            
            adjustments = {
                'gap_trust': 0.8,  # Fade gaps in bear trend
                'threshold_modifier': 1.1,  # Higher threshold for safety
                'position_size_modifier': 0.75,  # Reduce size
                'max_positions': 3
            }
            
            reasoning = (f"Bearish trend: Price < SMA20 < SMA50, "
                        f"{recent_return:.1f}% in 20d, VIX {current_vix:.1f}")
            
            strategy = "Fade bullish gaps, reduced positions, higher selectivity"
        
        # High Volatility
        elif current_vix > 30 or current_vol > 30:
            
            regime = 'HIGH_VOLATILITY'
            confidence = 'HIGH'
            
            adjustments = {
                'gap_trust': 0.7,  # Don't trust gaps in chaos
                'threshold_modifier': 1.3,  # Much higher threshold
                'position_size_modifier': 0.5,  # Half size
                'max_positions': 2
            }
            
            reasoning = (f"High volatility: VIX {current_vix:.1f}, "
                        f"Realized vol {current_vol:.1f}%")
            
            strategy = "Very selective, small positions, high standards"
        
        # Range-bound
        elif range_pct < 8 and abs(recent_return) < 3:
            
            regime = 'RANGE_BOUND'
            confidence = 'MEDIUM'
            
            adjustments = {
                'gap_trust': 0.9,  # Slightly skeptical of gaps
                'threshold_modifier': 1.0,  # Standard threshold
                'position_size_modifier': 0.9,  # Slightly reduced
                'max_positions': 3
            }
            
            reasoning = (f"Range-bound: {range_pct:.1f}% range, "
                        f"{recent_return:+.1f}% in 20d")
            
            strategy = "Cautious on gaps, fade extremes, standard positions"
        
        # Transitioning (unclear)
        else:
            regime = 'TRANSITIONING'
            confidence = 'LOW'
            
            adjustments = {
                'gap_trust': 1.0,  # Neutral
                'threshold_modifier': 1.1,  # Slightly higher threshold
                'position_size_modifier': 0.85,  # Slightly reduced
                'max_positions': 3
            }
            
            reasoning = f"Transitioning market: Mixed signals"
            strategy = "Wait for clear regime, slightly defensive"
        
        return {
            'regime': regime,
            'confidence': confidence,
            'adjustments': adjustments,
            'reasoning': reasoning,
            'strategy': strategy,
            'metrics': {
                'spy_price': current_price,
                'sma_20': sma_20_current,
                'sma_50': sma_50_current,
                'vix': current_vix,
                'volatility': current_vol,
                'recent_return': recent_return,
                'range_pct': range_pct
            },
            'success': True
        }
        
    except Exception as e:
        return {
            **get_default_regime(),
            'reasoning': f"Regime detection failed: {str(e)} - Using neutral default",
            'success': False
        }

def get_default_regime():
    """Default regime if detection fails"""
    return {
        'regime': 'UNKNOWN',
        'confidence': 'LOW',
        'adjustments': {
            'gap_trust': 1.0,
            'threshold_modifier': 1.0,
            'position_size_modifier': 0.9,
            'max_positions': 3
        },
        'strategy': "Use standard rules, slightly defensive",
        'success': False
    }

def apply_regime_adjustments(predictions, regime_info):
    """
    Apply regime-based adjustments to predictions
    
    Args:
        predictions: Dict of {symbol: prediction_result}
        regime_info: Regime detection results
    
    Returns:
        dict: Adjusted predictions
    """
    
    adjustments = regime_info['adjustments']
    
    adjusted = {}
    for symbol, pred in predictions.items():
        if pred['direction'] == 'NEUTRAL':
            adjusted[symbol] = pred
            continue
        
        # Apply position size adjustment
        original_size = pred.get('position_size', 1.0)
        adjusted_size = original_size * adjustments['position_size_modifier']
        
        # Apply confidence adjustment based on regime
        original_conf = pred.get('confidence', 0.5)
        
        # In high volatility or bear markets, reduce confidence
        if regime_info['regime'] in ['HIGH_VOLATILITY', 'TRENDING_BEAR']:
            adjusted_conf = original_conf * 0.95  # Reduce by 5%
        elif regime_info['regime'] == 'TRENDING_BULL':
            adjusted_conf = min(original_conf * 1.05, 0.95)  # Increase by 5%
        else:
            adjusted_conf = original_conf
        
        adjusted[symbol] = {
            **pred,
            'position_size': adjusted_size,
            'confidence': adjusted_conf,
            'original_position_size': original_size,
            'original_confidence': original_conf,
            'regime_adjusted': True,
            'regime': regime_info['regime']
        }
    
    return adjusted

def print_regime_status():
    """Print current regime status"""
    
    print("\n" + "="*80)
    print("📈 MARKET REGIME DETECTION")
    print("="*80)
    
    regime_info = detect_market_regime()
    
    if regime_info['success']:
        print(f"\nRegime: {regime_info['regime']}")
        print(f"Confidence: {regime_info['confidence']}")
        
        print(f"\nMarket Metrics:")
        metrics = regime_info['metrics']
        print(f"  SPY: ${metrics['spy_price']:.2f}")
        print(f"  SMA 20: ${metrics['sma_20']:.2f}")
        print(f"  SMA 50: ${metrics['sma_50']:.2f}")
        print(f"  VIX: {metrics['vix']:.2f}")
        print(f"  20-day Return: {metrics['recent_return']:+.1f}%")
        print(f"  Volatility: {metrics['volatility']:.1f}%")
        
        print(f"\nReasoning: {regime_info['reasoning']}")
        print(f"\nStrategy: {regime_info['strategy']}")
        
        print(f"\nAdjustments:")
        adj = regime_info['adjustments']
        print(f"  Gap Trust: {adj['gap_trust']:.0%}")
        print(f"  Threshold: {adj['threshold_modifier']:.0%} of base")
        print(f"  Position Size: {adj['position_size_modifier']:.0%}")
        print(f"  Max Positions: {adj['max_positions']}")
    else:
        print(f"\n⚠️ {regime_info['reasoning']}")
        print(f"\nUsing Conservative Defaults:")
        adj = regime_info['adjustments']
        print(f"  Position Size: {adj['position_size_modifier']:.0%}")
        print(f"  Max Positions: {adj['max_positions']}")
    
    print("\n" + "="*80 + "\n")
    
    return regime_info


if __name__ == "__main__":
    # Test regime detection
    regime_info = print_regime_status()
    
    print("REGIME EXAMPLES:")
    print("  TRENDING_BULL:    Follow gaps, full size, 4 positions")
    print("  TRENDING_BEAR:    Fade gaps, 75% size, 3 positions")
    print("  HIGH_VOLATILITY:  Very selective, 50% size, 2 positions")
    print("  RANGE_BOUND:      Cautious, 90% size, 3 positions")
