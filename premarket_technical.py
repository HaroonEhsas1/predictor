"""
PREMARKET TECHNICAL ANALYZER
Checks technical levels and indicators

Features:
- RSI calculation (overbought/oversold)
- Support/Resistance levels
- Recent trend
- Gap to key levels
"""

import yfinance as yf
import pandas as pd
import numpy as np
from typing import Dict, Any, List
from premarket_config import get_stock_config

class PremarketTechnical:
    """
    Analyzes technical levels for premarket
    """
    
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.config = get_stock_config(symbol)
        self.stock = yf.Ticker(symbol)
    
    def calculate_rsi(self, period: int = 14) -> float:
        """Calculate RSI"""
        
        try:
            hist = self.stock.history(period='3mo')
            
            if len(hist) < period + 1:
                return 50.0  # Neutral default
            
            # Calculate price changes
            delta = hist['Close'].diff()
            
            # Separate gains and losses
            gains = delta.where(delta > 0, 0)
            losses = -delta.where(delta < 0, 0)
            
            # Calculate average gains and losses
            avg_gains = gains.rolling(window=period).mean()
            avg_losses = losses.rolling(window=period).mean()
            
            # Calculate RS and RSI
            rs = avg_gains / avg_losses
            rsi = 100 - (100 / (1 + rs))
            
            return rsi.iloc[-1]
            
        except:
            return 50.0
    
    def get_support_resistance(self) -> Dict[str, Any]:
        """
        Calculate support and resistance levels
        """
        
        try:
            # Get 3 months of data
            hist = self.stock.history(period='3mo')
            
            if len(hist) < 20:
                return {'supports': [], 'resistances': []}
            
            # Find local minima (support) and maxima (resistance)
            window = 10
            
            supports = []
            resistances = []
            
            for i in range(window, len(hist) - window):
                # Check if local minimum
                if hist['Low'].iloc[i] == hist['Low'].iloc[i-window:i+window].min():
                    supports.append(hist['Low'].iloc[i])
                
                # Check if local maximum
                if hist['High'].iloc[i] == hist['High'].iloc[i-window:i+window].max():
                    resistances.append(hist['High'].iloc[i])
            
            # Cluster similar levels
            supports = self._cluster_levels(supports)
            resistances = self._cluster_levels(resistances)
            
            # Keep top 3 of each
            supports = sorted(supports, reverse=True)[:3]
            resistances = sorted(resistances)[:3]
            
            return {
                'supports': supports,
                'resistances': resistances
            }
            
        except:
            return {'supports': [], 'resistances': []}
    
    def _cluster_levels(self, levels: List[float], threshold: float = 0.02) -> List[float]:
        """Cluster similar price levels"""
        
        if not levels:
            return []
        
        levels = sorted(levels)
        clustered = []
        current_cluster = [levels[0]]
        
        for level in levels[1:]:
            if (level - current_cluster[0]) / current_cluster[0] < threshold:
                current_cluster.append(level)
            else:
                clustered.append(np.mean(current_cluster))
                current_cluster = [level]
        
        # Add last cluster
        if current_cluster:
            clustered.append(np.mean(current_cluster))
        
        return clustered
    
    def analyze_gap_to_levels(self, premarket_price: float, 
                              supports: List[float],
                              resistances: List[float]) -> Dict[str, Any]:
        """
        Check if gap is to a key technical level
        """
        
        # Check distance to nearest support/resistance
        nearest_support = None
        nearest_resistance = None
        
        if supports:
            nearest_support = max([s for s in supports if s < premarket_price], default=None)
        
        if resistances:
            nearest_resistance = min([r for r in resistances if r > premarket_price], default=None)
        
        gap_type = 'none'
        significance = 'low'
        
        # Check if gapping through support/resistance
        if nearest_support and abs(premarket_price - nearest_support) / nearest_support < 0.01:
            gap_type = 'to_support'
            significance = 'high'
        elif nearest_resistance and abs(premarket_price - nearest_resistance) / nearest_resistance < 0.01:
            gap_type = 'to_resistance'
            significance = 'high'
        elif nearest_support and premarket_price < nearest_support:
            gap_type = 'through_support'
            significance = 'very_high'
        elif nearest_resistance and premarket_price > nearest_resistance:
            gap_type = 'through_resistance'
            significance = 'very_high'
        
        return {
            'gap_type': gap_type,
            'significance': significance,
            'nearest_support': nearest_support,
            'nearest_resistance': nearest_resistance
        }
    
    def get_trend(self) -> str:
        """Get recent trend"""
        
        try:
            hist = self.stock.history(period='1mo')
            
            if len(hist) < 10:
                return 'neutral'
            
            # Calculate simple moving averages
            sma_10 = hist['Close'].rolling(10).mean().iloc[-1]
            sma_20 = hist['Close'].rolling(20).mean().iloc[-1] if len(hist) >= 20 else sma_10
            current = hist['Close'].iloc[-1]
            
            # Determine trend
            if current > sma_10 > sma_20:
                return 'uptrend'
            elif current < sma_10 < sma_20:
                return 'downtrend'
            else:
                return 'neutral'
                
        except:
            return 'neutral'
    
    def analyze_technical(self, premarket_price: float, prev_close: float) -> Dict[str, Any]:
        """
        Complete technical analysis
        """
        
        print(f"\n📐 Analyzing Technical Levels...")
        
        # Calculate RSI
        rsi = self.calculate_rsi()
        
        # Determine RSI state
        if rsi > 70:
            rsi_state = 'OVERBOUGHT'
            rsi_warning = True
        elif rsi < 30:
            rsi_state = 'OVERSOLD'
            rsi_warning = True
        elif rsi > 65:
            rsi_state = 'HIGH'
            rsi_warning = False
        elif rsi < 35:
            rsi_state = 'LOW'
            rsi_warning = False
        else:
            rsi_state = 'NEUTRAL'
            rsi_warning = False
        
        # Get support/resistance
        levels = self.get_support_resistance()
        
        # Analyze gap to levels
        gap_analysis = self.analyze_gap_to_levels(
            premarket_price,
            levels['supports'],
            levels['resistances']
        )
        
        # Get trend
        trend = self.get_trend()
        
        # Calculate technical score adjustment
        score_adjust = 0
        
        # RSI adjustment
        if rsi_state == 'OVERBOUGHT':
            score_adjust -= 10  # Reversal risk
        elif rsi_state == 'OVERSOLD':
            score_adjust += 10  # Bounce opportunity
        
        # Level significance
        if gap_analysis['significance'] == 'very_high':
            score_adjust += 8  # Breaking key level = strong
        elif gap_analysis['significance'] == 'high':
            score_adjust += 5
        
        # Trend alignment
        gap_direction = 'up' if premarket_price > prev_close else 'down'
        if gap_direction == 'up' and trend == 'uptrend':
            score_adjust += 5  # With trend
        elif gap_direction == 'down' and trend == 'downtrend':
            score_adjust += 5
        elif gap_direction == 'up' and trend == 'downtrend':
            score_adjust -= 5  # Against trend
        elif gap_direction == 'down' and trend == 'uptrend':
            score_adjust -= 5
        
        result = {
            'rsi': rsi,
            'rsi_state': rsi_state,
            'rsi_warning': rsi_warning,
            'supports': levels['supports'],
            'resistances': levels['resistances'],
            'gap_to_level': gap_analysis,
            'trend': trend,
            'score_adjustment': max(-15, min(15, score_adjust))
        }
        
        print(f"   RSI: {rsi:.1f} ({rsi_state})")
        print(f"   Trend: {trend.upper()}")
        print(f"   Gap Type: {gap_analysis['gap_type']}")
        print(f"   Score Adjustment: {result['score_adjustment']:+.0f}%")
        
        if rsi_warning:
            print(f"   ⚠️ RSI Warning: {rsi_state}")
        
        return result


if __name__ == "__main__":
    # Test
    print("\n" + "="*80)
    print("PREMARKET TECHNICAL ANALYZER - TEST")
    print("="*80)
    
    for symbol in ['NVDA', 'META']:
        analyzer = PremarketTechnical(symbol)
        
        # Get current price for simulation
        stock = yf.Ticker(symbol)
        info = stock.info
        current_price = info.get('regularMarketPrice', 100)
        
        # Simulate 2% gap up
        premarket_price = current_price * 1.02
        
        result = analyzer.analyze_technical(premarket_price, current_price)
        
        print(f"\n{symbol}:")
        print(f"   RSI: {result['rsi']:.1f} ({result['rsi_state']})")
        print(f"   Trend: {result['trend']}")
        print(f"   Supports: {[f'${s:.2f}' for s in result['supports'][:2]]}")
        print(f"   Resistances: {[f'${r:.2f}' for r in result['resistances'][:2]]}")
        
        print("\n")
