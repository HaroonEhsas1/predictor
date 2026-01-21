#!/usr/bin/env python3
"""
Enhanced Data Collector for Professional Stock Prediction Engine
Integrates with existing data sources while providing enhanced features
"""

import os
import sys
import time
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import concurrent.futures
import threading
from dataclasses import dataclass
import warnings
warnings.filterwarnings('ignore')

# Import existing system components
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sources.feeds import DataFeedManager, data_manager
from manager.scheduler import scheduler
from config import DATA_QUALITY, TIMEFRAMES, API_KEYS

@dataclass
class MarketContext:
    """Market context information for enhanced analysis"""
    futures_data: Dict[str, float]
    global_indices: Dict[str, float] 
    volatility_indicators: Dict[str, float]
    news_sentiment: float
    sector_performance: Dict[str, float]
    
class DataCollector:
    """
    Professional-grade data collector extending existing feeds system
    Provides enhanced features for intraday and next-day predictions
    """
    
    def __init__(self):
        """Initialize enhanced data collector"""
        # Use existing data manager as base
        self.base_manager = data_manager
        self.scheduler = scheduler
        
        # Enhanced data sources
        self.market_context_cache = {}
        self.news_cache = {}
        self.cache_duration = 300  # 5 minutes
        
        # Threading for concurrent data collection
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)
        self.collection_lock = threading.Lock()
        
        print("✅ Enhanced DataCollector initialized")
        
    def get_enhanced_stock_data(self, symbol: str, include_context: bool = True) -> Dict[str, Any]:
        """
        Get enhanced stock data with market context
        Extends existing data fetching with additional features
        """
        # Get base stock data using existing system with appropriate timeframes
        market_state = self.scheduler.get_market_state()
        if market_state['is_trading_day'] and market_state['market_open']:
            timeframes = ['1d', '1h', '15m', '5m', '1m']
        elif market_state['is_trading_day']:
            timeframes = ['1d', '1h', '15m']  # No 1m/5m when market closed
        else:
            timeframes = ['1d']  # Only daily on weekends/holidays
            
        base_data = self.base_manager.fetch_stock_data(symbol, timeframes)
        
        # Add enhanced features
        enhanced_data = {
            **base_data,
            'enhanced_features': {},
            'market_context': {},
            'technical_indicators': {},
            'timestamp': datetime.now().isoformat()
        }
        
        if include_context:
            # Add market context data concurrently
            futures = []
            
            with self.executor:
                # Futures data
                futures.append(
                    self.executor.submit(self._get_futures_data)
                )
                
                # Global indices
                futures.append(
                    self.executor.submit(self._get_global_indices)
                )
                
                # Volatility indicators
                futures.append(
                    self.executor.submit(self._get_volatility_indicators)
                )
                
                # News sentiment
                futures.append(
                    self.executor.submit(self._get_news_sentiment, symbol)
                )
                
            # Collect results
            try:
                futures_data = futures[0].result(timeout=10)
                global_data = futures[1].result(timeout=10) 
                volatility_data = futures[2].result(timeout=10)
                news_data = futures[3].result(timeout=10)
                
                enhanced_data['market_context'] = {
                    'futures': futures_data,
                    'global_indices': global_data,
                    'volatility': volatility_data,
                    'news_sentiment': news_data,
                    'context_timestamp': datetime.now().isoformat()
                }
                
            except concurrent.futures.TimeoutError:
                print("⚠️  Market context collection timeout - using cached data")
                enhanced_data['market_context'] = self.market_context_cache.get('last_good', {})
        
        # Add technical indicators using existing data
        if base_data.get('timeframes', {}).get('1m') is not None:
            enhanced_data['technical_indicators'] = self._calculate_enhanced_indicators(
                base_data['timeframes']
            )
        
        return enhanced_data
    
    def get_intraday_features(self, symbol: str, timeframe: str = '1m') -> Dict[str, Any]:
        """
        Get optimized intraday features for ML ensemble
        Fast, lightweight data for 1-minute predictions
        """
        # Get minimal required data for speed - check market state first
        market_state = self.scheduler.get_market_state()
        if not market_state['market_open']:
            return {
                'error': 'Market closed - no intraday predictions',
                'features': None,
                'market_state': market_state['session_phase']
            }
        
        base_data = self.base_manager.fetch_stock_data(symbol, [timeframe, '5m'])
        
        if not base_data.get('timeframes', {}).get(timeframe):
            return {'error': 'No intraday data available', 'features': None}
        
        df = base_data['timeframes'][timeframe]
        
        # Fast feature calculation for low-latency inference
        features = {
            'price_current': float(df['Close'].iloc[-1]) if len(df) > 0 else 0.0,
            'price_change_1m': self._safe_pct_change(df['Close'], 1),
            'price_change_5m': self._safe_pct_change(df['Close'], 5), 
            'volume_ratio': self._safe_volume_ratio(df),
            'volatility_short': self._safe_volatility(df['Close'], 10),
            'rsi_fast': self._safe_rsi(df['Close'], 9),
            'momentum_1m': self._safe_momentum(df['Close'], 3),
            'data_quality': base_data.get('data_quality', 'stale'),
            'timestamp': datetime.now().isoformat(),
            'market_open': self.scheduler.get_market_state()['market_open']
        }
        
        return {
            'symbol': symbol,
            'timeframe': timeframe, 
            'features': features,
            'raw_data': df.tail(20) if len(df) > 0 else pd.DataFrame()  # Last 20 points for context
        }
    
    def get_nextday_dataset(self, symbol: str) -> Dict[str, Any]:
        """
        Get comprehensive dataset for next-day gap predictions
        Detailed analysis for pre-close and pre-open predictions
        """
        # Get comprehensive historical data
        base_data = self.base_manager.fetch_stock_data(
            symbol, 
            ['1d', '1h', '15m', '5m']
        )
        
        # Get market context
        market_context = self._get_comprehensive_market_context()
        
        # Calculate gap analysis features
        gap_features = self._calculate_gap_features(base_data, market_context)
        
        return {
            'symbol': symbol,
            'base_data': base_data,
            'market_context': market_context,
            'gap_features': gap_features,
            'timestamp': datetime.now().isoformat(),
            'session_phase': self.scheduler.get_market_state()['session_phase']
        }
    
    def _get_futures_data(self) -> Dict[str, float]:
        """Get futures data (ES, NQ, YM, RTY)"""
        futures_symbols = ['ES=F', 'NQ=F', 'YM=F', 'RTY=F']
        futures_data = {}
        
        try:
            for symbol in futures_symbols:
                # Use existing yahoo data fetching
                data = self.base_manager._fetch_yahoo_data(symbol, ['1d'])
                if data and '1d' in data and len(data['1d']) > 0:
                    current_price = float(data['1d']['Close'].iloc[-1])
                    prev_close = float(data['1d']['Close'].iloc[-2]) if len(data['1d']) > 1 else current_price
                    change_pct = ((current_price - prev_close) / prev_close) * 100 if prev_close != 0 else 0.0
                    
                    futures_data[symbol.replace('=F', '')] = change_pct
                else:
                    futures_data[symbol.replace('=F', '')] = 0.0
                    
        except Exception as e:
            print(f"⚠️  Futures data error: {str(e)[:50]}")
            return {'ES': 0.0, 'NQ': 0.0, 'YM': 0.0, 'RTY': 0.0}
        
        return futures_data
    
    def _get_global_indices(self) -> Dict[str, float]:
        """Get global indices data"""
        indices = {
            'FTSE': '^FTSE',
            'Nikkei': '^N225', 
            'DAX': '^GDAXI',
            'EWU': 'EWU',
            'EWJ': 'EWJ'
        }
        
        indices_data = {}
        
        for name, symbol in indices.items():
            try:
                data = self.base_manager._fetch_yahoo_data(symbol, ['1d'])
                if data and '1d' in data and len(data['1d']) > 0:
                    current = float(data['1d']['Close'].iloc[-1])
                    prev = float(data['1d']['Close'].iloc[-2]) if len(data['1d']) > 1 else current
                    change_pct = ((current - prev) / prev) * 100 if prev != 0 else 0.0
                    indices_data[name] = change_pct
                else:
                    indices_data[name] = 0.0
            except:
                indices_data[name] = 0.0
        
        return indices_data
    
    def _get_volatility_indicators(self) -> Dict[str, float]:
        """Get DXY, VIX, and US10Y data"""
        volatility_symbols = {
            'DXY': 'DX=F',
            'VIX': '^VIX', 
            'US10Y': '^TNX'
        }
        
        vol_data = {}
        
        for name, symbol in volatility_symbols.items():
            try:
                data = self.base_manager._fetch_yahoo_data(symbol, ['1d'])
                if data and '1d' in data and len(data['1d']) > 0:
                    current = float(data['1d']['Close'].iloc[-1])
                    prev = float(data['1d']['Close'].iloc[-2]) if len(data['1d']) > 1 else current
                    change_pct = ((current - prev) / prev) * 100 if prev != 0 else 0.0
                    vol_data[name] = change_pct
                else:
                    vol_data[name] = 0.0
            except:
                vol_data[name] = 0.0
        
        return vol_data
    
    def _get_news_sentiment(self, symbol: str) -> float:
        """Get news sentiment (simplified implementation)"""
        # Cache check
        cache_key = f"news_{symbol}"
        if cache_key in self.news_cache:
            cache_time, sentiment = self.news_cache[cache_key]
            if time.time() - cache_time < self.cache_duration:
                return sentiment
        
        # For now, return neutral sentiment
        # In production, integrate with news APIs
        sentiment = 0.0
        
        self.news_cache[cache_key] = (time.time(), sentiment)
        return sentiment
    
    def _get_comprehensive_market_context(self) -> MarketContext:
        """Get comprehensive market context for next-day analysis"""
        return MarketContext(
            futures_data=self._get_futures_data(),
            global_indices=self._get_global_indices(),
            volatility_indicators=self._get_volatility_indicators(),
            news_sentiment=0.0,  # Placeholder
            sector_performance={'semiconductors': 0.0}  # Placeholder
        )
    
    def _calculate_enhanced_indicators(self, timeframe_data: Dict) -> Dict[str, float]:
        """Calculate enhanced technical indicators"""
        indicators = {}
        
        try:
            if '1m' in timeframe_data and len(timeframe_data['1m']) > 0:
                df = timeframe_data['1m']
                
                # Basic indicators
                indicators['rsi_14'] = self._safe_rsi(df['Close'], 14)
                indicators['rsi_9'] = self._safe_rsi(df['Close'], 9)
                indicators['volatility_20'] = self._safe_volatility(df['Close'], 20)
                indicators['volume_sma_ratio'] = self._safe_volume_sma_ratio(df)
                
                # Momentum indicators
                indicators['momentum_3'] = self._safe_momentum(df['Close'], 3)
                indicators['momentum_5'] = self._safe_momentum(df['Close'], 5)
                
                # Price action
                indicators['price_position'] = self._safe_price_position(df)
                
        except Exception as e:
            print(f"⚠️  Indicator calculation error: {str(e)[:50]}")
        
        return indicators
    
    def _calculate_gap_features(self, base_data: Dict, market_context: MarketContext) -> Dict[str, Any]:
        """Calculate features specific to gap predictions"""
        gap_features = {}
        
        try:
            if base_data.get('timeframes', {}).get('1d') is not None:
                daily_data = base_data['timeframes']['1d']
                
                if len(daily_data) > 1:
                    # Gap analysis
                    current_close = float(daily_data['Close'].iloc[-1])
                    prev_close = float(daily_data['Close'].iloc[-2])
                    
                    gap_features.update({
                        'current_close': current_close,
                        'prev_close': prev_close,
                        'daily_change_pct': ((current_close - prev_close) / prev_close) * 100,
                        'overnight_risk_score': self._calculate_overnight_risk(market_context),
                        'gap_probability': self._estimate_gap_probability(daily_data),
                        'expected_gap_size': self._estimate_gap_size(daily_data, market_context)
                    })
                    
        except Exception as e:
            print(f"⚠️  Gap feature calculation error: {str(e)[:50]}")
            
        return gap_features
    
    def _calculate_overnight_risk(self, context: MarketContext) -> float:
        """Calculate overnight risk score from market context"""
        risk_score = 0.0
        
        try:
            # Futures impact
            futures_avg = np.mean(list(context.futures_data.values()))
            risk_score += abs(futures_avg) * 0.3
            
            # Global markets impact
            global_avg = np.mean(list(context.global_indices.values()))
            risk_score += abs(global_avg) * 0.2
            
            # Volatility impact  
            vix_change = context.volatility_indicators.get('VIX', 0.0)
            risk_score += abs(vix_change) * 0.5
            
        except:
            pass
            
        return min(risk_score, 100.0)  # Cap at 100
    
    def _estimate_gap_probability(self, daily_data: pd.DataFrame) -> float:
        """Estimate probability of significant gap"""
        if len(daily_data) < 20:
            return 0.5
        
        try:
            # Calculate historical gap frequency
            gaps = []
            for i in range(1, min(len(daily_data), 20)):
                prev_close = daily_data['Close'].iloc[-(i+1)]
                curr_open = daily_data['Open'].iloc[-i]
                gap_pct = abs(((curr_open - prev_close) / prev_close) * 100)
                gaps.append(gap_pct > 1.0)  # Significant gap threshold
            
            return np.mean(gaps) if gaps else 0.5
            
        except:
            return 0.5
    
    def _estimate_gap_size(self, daily_data: pd.DataFrame, context: MarketContext) -> float:
        """Estimate expected gap size"""
        try:
            # Historical volatility
            if len(daily_data) >= 20:
                returns = daily_data['Close'].pct_change().dropna()
                hist_vol = returns.std() * 100
            else:
                hist_vol = 2.0
            
            # Market context adjustment
            context_multiplier = 1.0
            if context.volatility_indicators.get('VIX', 0) > 5.0:
                context_multiplier += 0.2
                
            return hist_vol * context_multiplier
            
        except:
            return 2.0
    
    # Helper functions for safe calculations
    def _safe_pct_change(self, series: pd.Series, periods: int) -> float:
        """Safe percentage change calculation"""
        try:
            if len(series) > periods:
                return float(series.pct_change(periods).iloc[-1] * 100)
            return 0.0
        except:
            return 0.0
    
    def _safe_volume_ratio(self, df: pd.DataFrame) -> float:
        """Safe volume ratio calculation"""
        try:
            if len(df) > 1 and 'Volume' in df.columns:
                current_vol = float(df['Volume'].iloc[-1])
                avg_vol = float(df['Volume'].tail(20).mean())
                return current_vol / avg_vol if avg_vol > 0 else 1.0
            return 1.0
        except:
            return 1.0
    
    def _safe_volatility(self, series: pd.Series, window: int) -> float:
        """Safe volatility calculation"""
        try:
            if len(series) >= window:
                returns = series.pct_change().dropna()
                return float(returns.tail(window).std() * 100)
            return 0.0
        except:
            return 0.0
    
    def _safe_rsi(self, series: pd.Series, window: int) -> float:
        """Safe RSI calculation"""
        try:
            if len(series) < window + 1:
                return 50.0
            
            delta = series.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
            
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return float(rsi.iloc[-1]) if not np.isnan(rsi.iloc[-1]) else 50.0
        except:
            return 50.0
    
    def _safe_momentum(self, series: pd.Series, window: int) -> float:
        """Safe momentum calculation"""
        try:
            if len(series) > window:
                return float((series.iloc[-1] - series.iloc[-(window+1)]) / series.iloc[-(window+1)] * 100)
            return 0.0
        except:
            return 0.0
    
    def _safe_volume_sma_ratio(self, df: pd.DataFrame) -> float:
        """Safe volume SMA ratio"""
        try:
            if len(df) > 20 and 'Volume' in df.columns:
                current_vol = float(df['Volume'].iloc[-1])
                sma_vol = float(df['Volume'].tail(20).mean())
                return current_vol / sma_vol if sma_vol > 0 else 1.0
            return 1.0
        except:
            return 1.0
    
    def _safe_price_position(self, df: pd.DataFrame) -> float:
        """Safe price position in daily range"""
        try:
            if len(df) > 0:
                last_row = df.iloc[-1]
                high = float(last_row['High'])
                low = float(last_row['Low'])
                close = float(last_row['Close'])
                
                if high != low:
                    return (close - low) / (high - low)
                return 0.5
            return 0.5
        except:
            return 0.5

# Create global instance for backward compatibility
data_collector = DataCollector()