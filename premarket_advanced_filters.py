"""
ADVANCED PREMARKET FILTERS
Professional-grade enhancements for premarket system

Tier 1 Enhancements:
1. Pre-Market Volatility Filter
2. Dynamic ATR-Based Stops
3. Enhanced Sector Correlation
4. VWAP Analysis
5. Options Flow Analysis
"""

import yfinance as yf
import pandas as pd
import numpy as np
from typing import Dict, Any, List
from datetime import datetime, timedelta

class AdvancedPremarketFilters:
    """
    Advanced filters to enhance premarket predictions
    """
    
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.stock = yf.Ticker(symbol)
    
    def calculate_premarket_volatility_filter(self, premarket_price: float, 
                                              prev_close: float,
                                              premarket_volume: int) -> Dict[str, Any]:
        """
        FILTER #8: Pre-Market Volatility Filter
        
        Skip trades if:
        - Spread is >2-3x normal
        - Volume is too low
        - Volatility is extreme
        
        Returns:
            - should_trade: bool
            - volatility_rating: normal/high/extreme
            - warnings: list
        """
        
        print(f"\n🔍 Volatility Filter Check...")
        
        warnings = []
        should_trade = True
        
        # Get historical volatility
        hist = self.stock.history(period='1mo')
        
        if len(hist) < 10:
            return {
                'should_trade': True,
                'volatility_rating': 'unknown',
                'warnings': ['Insufficient data for volatility check']
            }
        
        # Calculate normal daily volatility
        hist['daily_range'] = (hist['High'] - hist['Low']) / hist['Close']
        normal_volatility = hist['daily_range'].median()
        
        # Calculate premarket spread
        gap_pct = abs((premarket_price - prev_close) / prev_close)
        
        # Check if volatility is extreme
        volatility_multiplier = gap_pct / normal_volatility if normal_volatility > 0 else 1
        
        if volatility_multiplier > 3.0:
            warnings.append(f"Extreme volatility ({volatility_multiplier:.1f}x normal)")
            should_trade = False
            volatility_rating = 'EXTREME'
        elif volatility_multiplier > 2.0:
            warnings.append(f"High volatility ({volatility_multiplier:.1f}x normal)")
            volatility_rating = 'HIGH'
        else:
            volatility_rating = 'NORMAL'
        
        # Check premarket volume vs normal
        avg_volume = hist['Volume'].mean()
        volume_ratio = premarket_volume / (avg_volume * 0.05) if avg_volume > 0 else 0  # 5% of daily = typical premarket
        
        if volume_ratio < 0.3:
            warnings.append(f"Very low premarket volume ({volume_ratio:.1f}x normal)")
            should_trade = False
        elif volume_ratio < 0.5:
            warnings.append(f"Low premarket volume ({volume_ratio:.1f}x normal)")
        
        result = {
            'should_trade': should_trade,
            'volatility_rating': volatility_rating,
            'volatility_multiplier': volatility_multiplier,
            'volume_ratio': volume_ratio,
            'warnings': warnings
        }
        
        print(f"   Volatility: {volatility_rating} ({volatility_multiplier:.1f}x)")
        print(f"   Volume Ratio: {volume_ratio:.1f}x normal")
        print(f"   Trade: {'✅ YES' if should_trade else '❌ NO - FILTERED'}")
        
        if warnings:
            for warning in warnings:
                print(f"   ⚠️ {warning}")
        
        return result
    
    def calculate_dynamic_atr_stops(self, entry_price: float, 
                                    direction: str,
                                    confidence: float) -> Dict[str, Any]:
        """
        FILTER #4: Dynamic ATR-Based Stops
        
        Instead of static stops, use:
        - ATR of last 2 weeks
        - Adjusted for confidence
        - Adaptive to volatility
        
        Returns:
            - stop_loss: price
            - take_profit levels (conservative/moderate/aggressive)
            - risk_reward ratios
        """
        
        print(f"\n📊 Calculating Dynamic ATR Stops...")
        
        try:
            # Get 1 month of data
            hist = self.stock.history(period='1mo')
            
            if len(hist) < 14:
                # Fallback to simple percentage
                return self._simple_stops(entry_price, direction, confidence)
            
            # Calculate ATR (14-period)
            high_low = hist['High'] - hist['Low']
            high_close = abs(hist['High'] - hist['Close'].shift())
            low_close = abs(hist['Low'] - hist['Close'].shift())
            
            true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            atr = true_range.rolling(14).mean().iloc[-1]
            
            # ATR as percentage of price
            atr_pct = (atr / entry_price) * 100
            
            # Adjust ATR multiplier based on confidence
            if confidence >= 75:
                stop_multiplier = 1.5  # Tighter stop for high confidence
                profit_multiplier = 2.5
            elif confidence >= 65:
                stop_multiplier = 2.0  # Standard stop
                profit_multiplier = 3.0
            else:
                stop_multiplier = 2.5  # Wider stop for lower confidence
                profit_multiplier = 3.5
            
            # Calculate stops
            if direction == 'UP':
                stop_loss = entry_price - (atr * stop_multiplier)
                conservative_target = entry_price + (atr * profit_multiplier * 0.6)
                moderate_target = entry_price + (atr * profit_multiplier)
                aggressive_target = entry_price + (atr * profit_multiplier * 1.5)
            else:
                stop_loss = entry_price + (atr * stop_multiplier)
                conservative_target = entry_price - (atr * profit_multiplier * 0.6)
                moderate_target = entry_price - (atr * profit_multiplier)
                aggressive_target = entry_price - (atr * profit_multiplier * 1.5)
            
            # Calculate percentages and R:R
            stop_pct = ((stop_loss - entry_price) / entry_price) * 100
            cons_pct = ((conservative_target - entry_price) / entry_price) * 100
            mod_pct = ((moderate_target - entry_price) / entry_price) * 100
            agg_pct = ((aggressive_target - entry_price) / entry_price) * 100
            
            result = {
                'method': 'ATR',
                'atr': atr,
                'atr_pct': atr_pct,
                'stop_loss': stop_loss,
                'stop_pct': stop_pct,
                'conservative_target': conservative_target,
                'conservative_pct': cons_pct,
                'moderate_target': moderate_target,
                'moderate_pct': mod_pct,
                'aggressive_target': aggressive_target,
                'aggressive_pct': agg_pct,
                'risk_reward_conservative': abs(cons_pct / stop_pct) if stop_pct != 0 else 0,
                'risk_reward_moderate': abs(mod_pct / stop_pct) if stop_pct != 0 else 0,
                'risk_reward_aggressive': abs(agg_pct / stop_pct) if stop_pct != 0 else 0
            }
            
            print(f"   ATR: ${atr:.2f} ({atr_pct:.2f}%)")
            print(f"   Stop: ${stop_loss:.2f} ({stop_pct:+.2f}%)")
            print(f"   Moderate Target: ${moderate_target:.2f} ({mod_pct:+.2f}%)")
            print(f"   R:R Ratio: {result['risk_reward_moderate']:.2f}:1")
            
            return result
            
        except Exception as e:
            print(f"   ⚠️ ATR calculation failed: {e}")
            return self._simple_stops(entry_price, direction, confidence)
    
    def _simple_stops(self, entry_price: float, direction: str, confidence: float) -> Dict[str, Any]:
        """Fallback to simple percentage stops"""
        
        if confidence >= 75:
            stop_pct = 1.5
        elif confidence >= 65:
            stop_pct = 2.0
        else:
            stop_pct = 2.5
        
        if direction == 'UP':
            stop_loss = entry_price * (1 - stop_pct/100)
            moderate_target = entry_price * (1 + (stop_pct * 2)/100)
        else:
            stop_loss = entry_price * (1 + stop_pct/100)
            moderate_target = entry_price * (1 - (stop_pct * 2)/100)
        
        return {
            'method': 'PERCENTAGE',
            'stop_loss': stop_loss,
            'stop_pct': -stop_pct if direction == 'UP' else stop_pct,
            'moderate_target': moderate_target,
            'moderate_pct': stop_pct * 2 if direction == 'UP' else -stop_pct * 2
        }
    
    def analyze_sector_correlation(self, sector_etf: str, 
                                   stock_gap_pct: float,
                                   stock_gap_direction: str) -> Dict[str, Any]:
        """
        FILTER #7: Enhanced Sector Correlation
        
        Checks:
        - Sector ETF strength vs stock
        - Correlation score
        - Divergence warnings
        
        Returns confidence adjustment
        """
        
        print(f"\n🔄 Sector Correlation Analysis...")
        
        try:
            # Get sector ETF data
            sector = yf.Ticker(sector_etf)
            sector_hist = sector.history(period='3mo')
            
            if len(sector_hist) < 20:
                return {'confidence_adjustment': 0, 'correlation': 'unknown'}
            
            # Get stock data
            stock_hist = self.stock.history(period='3mo')
            
            if len(stock_hist) < 20:
                return {'confidence_adjustment': 0, 'correlation': 'unknown'}
            
            # Calculate correlation
            sector_returns = sector_hist['Close'].pct_change()
            stock_returns = stock_hist['Close'].pct_change()
            
            # Align dates
            common_dates = sector_returns.index.intersection(stock_returns.index)
            if len(common_dates) < 20:
                return {'confidence_adjustment': 0, 'correlation': 'unknown'}
            
            correlation = sector_returns[common_dates].corr(stock_returns[common_dates])
            
            # Get sector premarket movement
            sector_info = sector.info
            sector_prev = sector_hist['Close'].iloc[-1]
            sector_current = sector_info.get('regularMarketPrice', sector_prev)
            sector_gap_pct = ((sector_current - sector_prev) / sector_prev) * 100
            
            # Check divergence
            divergence = False
            confidence_adjustment = 0
            
            if stock_gap_direction == 'up' and sector_gap_pct < -0.5:
                divergence = True
                confidence_adjustment = -12  # Stock up, sector down = weak
            elif stock_gap_direction == 'down' and sector_gap_pct > 0.5:
                divergence = True
                confidence_adjustment = -12  # Stock down, sector up = weak
            elif stock_gap_direction == 'up' and sector_gap_pct > 0.5:
                confidence_adjustment = +8  # Both up = strong
            elif stock_gap_direction == 'down' and sector_gap_pct < -0.5:
                confidence_adjustment = +8  # Both down = strong
            
            # Adjust based on correlation strength
            if correlation > 0.7:  # High correlation
                confidence_adjustment *= 1.2  # Sector matters more
            elif correlation < 0.3:  # Low correlation
                confidence_adjustment *= 0.5  # Sector matters less
            
            result = {
                'correlation': correlation,
                'sector_gap': sector_gap_pct,
                'divergence': divergence,
                'confidence_adjustment': round(confidence_adjustment),
                'rating': 'STRONG' if abs(correlation) > 0.7 else 'MODERATE' if abs(correlation) > 0.4 else 'WEAK'
            }
            
            print(f"   Correlation: {correlation:.2f} ({result['rating']})")
            print(f"   Sector ({sector_etf}): {sector_gap_pct:+.2f}%")
            print(f"   Divergence: {'⚠️ YES' if divergence else '✅ NO'}")
            print(f"   Confidence Adjust: {confidence_adjustment:+.0f}%")
            
            return result
            
        except Exception as e:
            print(f"   ⚠️ Sector analysis failed: {e}")
            return {'confidence_adjustment': 0, 'correlation': 'error'}
    
    def calculate_vwap_levels(self) -> Dict[str, Any]:
        """
        FILTER #1 (Partial): VWAP Analysis
        
        Calculate VWAP from recent data to identify
        support/resistance levels
        """
        
        print(f"\n📊 VWAP Analysis...")
        
        try:
            # Get intraday data (1 day, 5-min intervals)
            hist = self.stock.history(period='5d', interval='5m')
            
            if len(hist) < 10:
                return {'has_vwap': False}
            
            # Calculate VWAP
            typical_price = (hist['High'] + hist['Low'] + hist['Close']) / 3
            vwap = (typical_price * hist['Volume']).cumsum() / hist['Volume'].cumsum()
            
            current_vwap = vwap.iloc[-1]
            current_price = hist['Close'].iloc[-1]
            
            # VWAP deviation
            vwap_deviation = ((current_price - current_vwap) / current_vwap) * 100
            
            # Determine position relative to VWAP
            if vwap_deviation > 1.0:
                position = 'ABOVE'
                implication = 'Bullish (price above VWAP)'
            elif vwap_deviation < -1.0:
                position = 'BELOW'
                implication = 'Bearish (price below VWAP)'
            else:
                position = 'NEAR'
                implication = 'Neutral (at VWAP)'
            
            result = {
                'has_vwap': True,
                'vwap': current_vwap,
                'current_price': current_price,
                'deviation': vwap_deviation,
                'position': position,
                'implication': implication
            }
            
            print(f"   VWAP: ${current_vwap:.2f}")
            print(f"   Current: ${current_price:.2f}")
            print(f"   Position: {position} ({vwap_deviation:+.2f}%)")
            print(f"   Implication: {implication}")
            
            return result
            
        except Exception as e:
            print(f"   ⚠️ VWAP calculation failed: {e}")
            return {'has_vwap': False}


if __name__ == "__main__":
    # Test
    print("\n" + "="*80)
    print("ADVANCED PREMARKET FILTERS - TEST")
    print("="*80)
    
    for symbol in ['NVDA', 'META']:
        filters = AdvancedPremarketFilters(symbol)
        
        # Simulate premarket data
        stock = yf.Ticker(symbol)
        info = stock.info
        current_price = info.get('regularMarketPrice', 100)
        
        # Test volatility filter
        vol_filter = filters.calculate_premarket_volatility_filter(
            premarket_price=current_price * 1.02,
            prev_close=current_price,
            premarket_volume=500000
        )
        
        # Test ATR stops
        atr_stops = filters.calculate_dynamic_atr_stops(
            entry_price=current_price,
            direction='UP',
            confidence=75
        )
        
        # Test sector correlation
        sector_etf = 'SMH' if symbol == 'NVDA' else 'XLC'
        sector_corr = filters.analyze_sector_correlation(
            sector_etf=sector_etf,
            stock_gap_pct=2.0,
            stock_gap_direction='up'
        )
        
        # Test VWAP
        vwap = filters.calculate_vwap_levels()
        
        print(f"\n{symbol} Summary:")
        print(f"   Volatility Filter: {'✅ PASS' if vol_filter['should_trade'] else '❌ FAIL'}")
        print(f"   ATR Stop: ${atr_stops.get('stop_loss', 0):.2f}")
        print(f"   Sector Correlation: {sector_corr.get('correlation', 0):.2f}")
        print(f"   VWAP: ${vwap.get('vwap', 0):.2f}" if vwap.get('has_vwap') else "   VWAP: N/A")
        
        print("\n")
