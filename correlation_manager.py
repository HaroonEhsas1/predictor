"""
CORRELATION POSITION SIZING - Smart diversification

Reduces position sizes when stocks are highly correlated
Prevents overexposure to same market movements

Compatible with existing system
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def get_stock_correlation(symbols, period=60):
    """
    Calculate correlation matrix for stocks
    
    Args:
        symbols: List of stock symbols
        period: Days of history to analyze (default 60)
    
    Returns:
        dict: Correlation info and recommendations
    """
    
    try:
        # Download price data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period)
        
        data = yf.download(symbols, start=start_date, end=end_date, progress=False)
        
        if 'Close' in data.columns:
            closes = data['Close']
        else:
            closes = data['Adj Close']
        
        # Calculate daily returns
        returns = closes.pct_change().dropna()
        
        # Calculate correlation matrix
        corr_matrix = returns.corr()
        
        # Get average correlation (excluding diagonal)
        mask = np.ones_like(corr_matrix, dtype=bool)
        np.fill_diagonal(mask, False)
        avg_correlation = corr_matrix.where(mask).mean().mean()
        
        # Identify high correlation pairs
        high_corr_pairs = []
        for i in range(len(symbols)):
            for j in range(i+1, len(symbols)):
                corr_val = corr_matrix.iloc[i, j]
                if abs(corr_val) > 0.7:  # High correlation threshold
                    high_corr_pairs.append({
                        'pair': f"{symbols[i]}/{symbols[j]}",
                        'correlation': corr_val
                    })
        
        # Determine max positions based on correlation
        if avg_correlation > 0.8:
            max_positions = 2  # Very high correlation - limit exposure
            risk_level = 'HIGH'
            reasoning = f"Average correlation {avg_correlation:.2f} > 0.8: Stocks moving together - limit to 2 positions"
        elif avg_correlation > 0.6:
            max_positions = 3  # High correlation - moderate limit
            risk_level = 'MEDIUM'
            reasoning = f"Average correlation {avg_correlation:.2f} in 0.6-0.8: Some correlation - limit to 3 positions"
        else:
            max_positions = 4  # Low correlation - full exposure OK
            risk_level = 'LOW'
            reasoning = f"Average correlation {avg_correlation:.2f} < 0.6: Good diversification - all 4 positions OK"
        
        # Position size adjustment
        if avg_correlation > 0.8:
            size_multiplier = 0.75  # Reduce each position by 25%
        elif avg_correlation > 0.6:
            size_multiplier = 0.9   # Reduce each position by 10%
        else:
            size_multiplier = 1.0   # Full size OK
        
        return {
            'correlation_matrix': corr_matrix,
            'avg_correlation': avg_correlation,
            'high_corr_pairs': high_corr_pairs,
            'max_positions': max_positions,
            'size_multiplier': size_multiplier,
            'risk_level': risk_level,
            'reasoning': reasoning,
            'success': True
        }
        
    except Exception as e:
        # If correlation check fails, use conservative defaults
        return {
            'avg_correlation': None,
            'high_corr_pairs': [],
            'max_positions': 3,  # Conservative default
            'size_multiplier': 0.9,  # Slightly reduced
            'risk_level': 'UNKNOWN',
            'reasoning': f"Correlation check failed: {str(e)} - Using conservative 3-position limit",
            'success': False
        }

def apply_correlation_sizing(predictions, symbols):
    """
    Apply correlation-based position sizing to predictions
    
    Args:
        predictions: Dict of {symbol: prediction_result}
        symbols: List of symbols being traded
    
    Returns:
        dict: Adjusted predictions with correlation sizing
    """
    
    # Get correlation info
    corr_info = get_stock_correlation(symbols)
    
    # Rank predictions by confidence
    ranked = sorted(
        [(sym, pred) for sym, pred in predictions.items()],
        key=lambda x: x[1].get('confidence', 0),
        reverse=True
    )
    
    # Apply max positions limit
    max_positions = corr_info['max_positions']
    size_multiplier = corr_info['size_multiplier']
    
    adjusted = {}
    positions_taken = 0
    
    for symbol, pred in ranked:
        if pred['direction'] == 'NEUTRAL':
            adjusted[symbol] = pred
            continue
        
        # Check if we've hit max positions
        if positions_taken >= max_positions:
            # Skip this trade
            adjusted[symbol] = {
                **pred,
                'direction': 'NEUTRAL',
                'position_size': 0.0,
                'correlation_skip': True,
                'skip_reason': f"Correlation limit: Max {max_positions} positions"
            }
        else:
            # Adjust position size by correlation multiplier
            original_size = pred.get('position_size', 1.0)
            adjusted_size = original_size * size_multiplier
            
            adjusted[symbol] = {
                **pred,
                'position_size': adjusted_size,
                'original_position_size': original_size,
                'correlation_adjusted': True if size_multiplier < 1.0 else False,
                'correlation_multiplier': size_multiplier
            }
            positions_taken += 1
    
    return {
        'predictions': adjusted,
        'correlation_info': corr_info
    }

def print_correlation_status(symbols):
    """Print current correlation status"""
    
    print("\n" + "="*80)
    print("🔗 CORRELATION ANALYSIS")
    print("="*80)
    
    corr_info = get_stock_correlation(symbols)
    
    if corr_info['success']:
        print(f"\nAverage Correlation: {corr_info['avg_correlation']:.2f}")
        print(f"Risk Level: {corr_info['risk_level']}")
        print(f"Max Positions: {corr_info['max_positions']}")
        print(f"Size Multiplier: {corr_info['size_multiplier']:.0%}")
        
        print(f"\nReasoning: {corr_info['reasoning']}")
        
        if corr_info['high_corr_pairs']:
            print(f"\nHigh Correlation Pairs (>0.7):")
            for pair_info in corr_info['high_corr_pairs']:
                print(f"  {pair_info['pair']}: {pair_info['correlation']:.2f}")
        
        print("\nCorrelation Matrix:")
        print(corr_info['correlation_matrix'].round(2))
    else:
        print(f"\n⚠️ {corr_info['reasoning']}")
        print(f"Using Conservative Defaults:")
        print(f"  Max Positions: {corr_info['max_positions']}")
        print(f"  Size Multiplier: {corr_info['size_multiplier']:.0%}")
    
    print("\n" + "="*80 + "\n")
    
    return corr_info


if __name__ == "__main__":
    # Test correlation analysis
    symbols = ['AMD', 'NVDA', 'META', 'AVGO']
    
    corr_info = print_correlation_status(symbols)
    
    print("\nEXAMPLE SCENARIOS:")
    print("  Avg Corr 0.9: Max 2 positions, 75% size")
    print("  Avg Corr 0.7: Max 3 positions, 90% size")
    print("  Avg Corr 0.4: Max 4 positions, 100% size")
