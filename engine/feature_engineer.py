#!/usr/bin/env python3
"""
Feature Engineering Module for Professional Stock Prediction Engine
Advanced feature creation for both intraday and next-day predictions
"""

import os
import sys
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import warnings
warnings.filterwarnings('ignore')

# Import existing system components
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from feature_engineering import (
        create_advanced_features,
        engineer_features_safe,
        add_institutional_indicators
    )
    ENHANCED_FEATURES_AVAILABLE = True
except ImportError:
    ENHANCED_FEATURES_AVAILABLE = False

# Import advanced free indicators
try:
    from indicators.advanced_free_indicators import AdvancedFreeIndicators, calculate_all_advanced_indicators
    ADVANCED_INDICATORS_AVAILABLE = True
except ImportError:
    ADVANCED_INDICATORS_AVAILABLE = False
    print("⚠️  Advanced free indicators not available")

@dataclass
class FeatureSet:
    """Container for engineered features"""
    basic_features: Dict[str, float]
    technical_indicators: Dict[str, float] 
    market_structure: Dict[str, float]
    cross_asset: Dict[str, float]
    time_series: np.ndarray
    feature_names: List[str]
    timestamp: str

class FeatureEngineer:
    """
    Professional feature engineering for stock predictions
    Combines existing feature engineering with new engine-specific features
    """
    
    def __init__(self):
        """Initialize feature engineer"""
        self.feature_cache = {}
        self.cache_duration = 60  # 1 minute cache for intraday
        
        # Feature configuration
        self.intraday_features = [
            'price_momentum_1m', 'price_momentum_3m', 'price_momentum_5m',
            'volume_ratio_current', 'volume_momentum_5m',
            'volatility_short_term', 'volatility_medium_term', 
            'rsi_fast', 'rsi_slow', 'macd_signal',
            'bollinger_position', 'price_range_position',
            'trend_strength', 'support_resistance_level'
        ]
        
        self.nextday_features = [
            'gap_probability', 'overnight_risk_score', 'sector_correlation',
            'futures_influence', 'global_market_influence', 'vix_impact',
            'earnings_proximity', 'technical_exhaustion', 'volume_climax',
            'institutional_flow', 'options_flow', 'news_sentiment_score'
        ]
        
        print("✅ FeatureEngineer initialized")
    
    def engineer_intraday_features(self, data: Dict[str, Any], symbol: str) -> FeatureSet:
        """
        Create optimized features for 1-minute ML ensemble predictions  
        Fast computation for low-latency inference
        """
        features = data.get('features', {})
        raw_data = data.get('raw_data', pd.DataFrame())
        
        # Basic features from data collector
        basic_features = {
            'price_current': features.get('price_current', 0.0),
            'price_change_1m': features.get('price_change_1m', 0.0),
            'price_change_5m': features.get('price_change_5m', 0.0),
            'volume_ratio': features.get('volume_ratio', 1.0),
            'data_quality_score': self._encode_data_quality(features.get('data_quality', 'stale'))
        }
        
        # Fast technical indicators
        technical_indicators = {}
        if len(raw_data) > 0:
            technical_indicators = self._calculate_fast_indicators(raw_data)
        
        # Market microstructure features
        market_structure = self._calculate_microstructure_features(raw_data, features)
        
        # Cross-asset features (minimal for speed)
        cross_asset = {
            'market_open_flag': 1.0 if features.get('market_open', False) else 0.0,
            'session_time': self._encode_session_time()
        }
        
        # Prepare time series array for models
        time_series_data = self._prepare_time_series(raw_data, 20)  # Last 20 points
        
        # Combine all features
        all_features = {**basic_features, **technical_indicators, **market_structure, **cross_asset}
        feature_names = list(all_features.keys())
        
        return FeatureSet(
            basic_features=basic_features,
            technical_indicators=technical_indicators,
            market_structure=market_structure,
            cross_asset=cross_asset,
            time_series=time_series_data,
            feature_names=feature_names,
            timestamp=pd.Timestamp.now().isoformat()
        )
    
    def engineer_nextday_features(self, dataset: Dict[str, Any], symbol: str) -> FeatureSet:
        """
        Create comprehensive features for next-day gap predictions
        Detailed analysis incorporating all available data
        """
        base_data = dataset.get('base_data', {})
        market_context = dataset.get('market_context', {})
        gap_features = dataset.get('gap_features', {})
        
        # Enhanced basic features
        basic_features = {
            'current_close': gap_features.get('current_close', 0.0),
            'daily_change_pct': gap_features.get('daily_change_pct', 0.0),
            'overnight_risk_score': gap_features.get('overnight_risk_score', 0.0),
            'gap_probability': gap_features.get('gap_probability', 0.5),
            'expected_gap_size': gap_features.get('expected_gap_size', 2.0)
        }
        
        # Comprehensive technical analysis
        technical_indicators = {}
        if base_data.get('timeframes', {}).get('1d') is not None:
            daily_data = base_data['timeframes']['1d']
            technical_indicators = self._calculate_comprehensive_indicators(daily_data)
            
            # Add existing enhanced features if available
            if ENHANCED_FEATURES_AVAILABLE:
                try:
                    enhanced_features = create_advanced_features(daily_data)
                    if isinstance(enhanced_features, dict):
                        technical_indicators.update(enhanced_features)
                except Exception as e:
                    print(f"⚠️  Enhanced features error: {str(e)[:50]}")
        
        # Market structure analysis
        market_structure = self._analyze_market_structure(base_data, market_context)
        
        # Cross-asset correlation features
        cross_asset = self._calculate_cross_asset_features(market_context)
        
        # Prepare time series for LSTM models
        time_series_data = self._prepare_comprehensive_time_series(base_data)
        
        # Combine all features
        all_features = {**basic_features, **technical_indicators, **market_structure, **cross_asset}
        feature_names = list(all_features.keys())
        
        return FeatureSet(
            basic_features=basic_features,
            technical_indicators=technical_indicators,
            market_structure=market_structure,
            cross_asset=cross_asset,
            time_series=time_series_data,
            feature_names=feature_names,
            timestamp=pd.Timestamp.now().isoformat()
        )
    
    def create_model_inputs(self, feature_set: FeatureSet, model_type: str) -> Tuple[np.ndarray, List[str]]:
        """
        Convert feature set to model-ready inputs
        """
        if model_type == 'ensemble':
            # For tree-based models (RF, XGBoost, LightGBM)
            features = {**feature_set.basic_features, **feature_set.technical_indicators, 
                       **feature_set.market_structure, **feature_set.cross_asset}
            
            # Convert to numpy array
            feature_values = []
            feature_names = []
            
            for name, value in features.items():
                if isinstance(value, (int, float)) and not np.isnan(value):
                    feature_values.append(float(value))
                    feature_names.append(name)
                else:
                    feature_values.append(0.0)
                    feature_names.append(name)
            
            return np.array(feature_values).reshape(1, -1), feature_names
            
        elif model_type == 'lstm':
            # For LSTM models - use time series data
            if len(feature_set.time_series.shape) == 2:
                return feature_set.time_series.reshape(1, *feature_set.time_series.shape), ['time_series']
            else:
                # Fallback to basic features
                basic_values = list(feature_set.basic_features.values())
                return np.array(basic_values).reshape(1, -1), list(feature_set.basic_features.keys())
                
        else:
            # Default - all numerical features
            all_features = {**feature_set.basic_features, **feature_set.technical_indicators,
                           **feature_set.market_structure, **feature_set.cross_asset}
            values = [float(v) if isinstance(v, (int, float)) and not np.isnan(v) else 0.0 
                     for v in all_features.values()]
            return np.array(values).reshape(1, -1), list(all_features.keys())
    
    def _calculate_fast_indicators(self, df: pd.DataFrame) -> Dict[str, float]:
        """Fast technical indicators for intraday predictions"""
        indicators = {}
        
        try:
            if len(df) < 5:
                return {name: 0.0 for name in ['rsi_9', 'momentum_3', 'volatility_10', 'volume_sma_ratio']}
            
            close = df['Close']
            volume = df.get('Volume', pd.Series([1] * len(df)))
            
            # Fast RSI (9 period)
            indicators['rsi_9'] = self._fast_rsi(close, 9)
            
            # Momentum (3 period)
            if len(close) > 3:
                indicators['momentum_3'] = ((close.iloc[-1] - close.iloc[-4]) / close.iloc[-4]) * 100
            else:
                indicators['momentum_3'] = 0.0
            
            # Short-term volatility
            if len(close) >= 10:
                returns = close.pct_change().dropna()
                indicators['volatility_10'] = returns.tail(10).std() * 100
            else:
                indicators['volatility_10'] = 0.0
                
            # Volume momentum
            if len(volume) >= 5:
                current_vol = volume.iloc[-1]
                avg_vol = volume.tail(5).mean()
                indicators['volume_sma_ratio'] = current_vol / avg_vol if avg_vol > 0 else 1.0
            else:
                indicators['volume_sma_ratio'] = 1.0
                
        except Exception as e:
            print(f"⚠️  Fast indicators error: {str(e)[:30]}")
            indicators = {name: 0.0 for name in ['rsi_9', 'momentum_3', 'volatility_10', 'volume_sma_ratio']}
        
        return indicators
    
    def _calculate_comprehensive_indicators(self, df: pd.DataFrame) -> Dict[str, float]:
        """Comprehensive technical indicators for next-day predictions"""
        indicators = {}
        
        try:
            if len(df) < 20:
                return {}
            
            close = df['Close']
            high = df['High']
            low = df['Low'] 
            volume = df.get('Volume', pd.Series([1] * len(df)))
            
            # RSI family
            indicators['rsi_14'] = self._fast_rsi(close, 14)
            indicators['rsi_21'] = self._fast_rsi(close, 21)
            
            # MACD
            macd_line, signal_line = self._calculate_macd(close)
            indicators['macd'] = macd_line
            indicators['macd_signal'] = signal_line
            indicators['macd_histogram'] = macd_line - signal_line
            
            # Bollinger Bands
            bb_upper, bb_middle, bb_lower = self._calculate_bollinger_bands(close, 20, 2)
            indicators['bb_position'] = (close.iloc[-1] - bb_lower) / (bb_upper - bb_lower) if bb_upper != bb_lower else 0.5
            indicators['bb_width'] = (bb_upper - bb_lower) / bb_middle if bb_middle > 0 else 0.0
            
            # ATR 
            indicators['atr_14'] = self._calculate_atr(high, low, close, 14)
            
            # Volume indicators
            indicators['volume_sma_20'] = volume.rolling(20).mean().iloc[-1] if len(volume) >= 20 else volume.mean()
            indicators['volume_ratio_20'] = volume.iloc[-1] / indicators['volume_sma_20'] if indicators['volume_sma_20'] > 0 else 1.0
            
            # Price patterns
            indicators['price_vs_sma_20'] = (close.iloc[-1] / close.rolling(20).mean().iloc[-1] - 1) * 100 if len(close) >= 20 else 0.0
            indicators['price_vs_sma_50'] = (close.iloc[-1] / close.rolling(50).mean().iloc[-1] - 1) * 100 if len(close) >= 50 else 0.0
            
            # Volatility
            returns = close.pct_change().dropna()
            indicators['volatility_20'] = returns.tail(20).std() * 100 if len(returns) >= 20 else 0.0
            indicators['volatility_5'] = returns.tail(5).std() * 100 if len(returns) >= 5 else 0.0
            
            # Add ADVANCED FREE INDICATORS for 10/10 accuracy
            if ADVANCED_INDICATORS_AVAILABLE:
                try:
                    # Prepare DataFrame with lowercase columns for advanced indicators
                    df_lowercase = df.copy()
                    df_lowercase.columns = [col.lower() for col in df_lowercase.columns]
                    
                    # Calculate all advanced indicators
                    advanced_indicators = calculate_all_advanced_indicators(df_lowercase)
                    
                    # Add key advanced indicators to the feature set
                    indicators.update(advanced_indicators)
                    
                except Exception as e:
                    print(f"⚠️  Advanced indicators error: {str(e)[:50]}")
            
        except Exception as e:
            print(f"⚠️  Comprehensive indicators error: {str(e)[:50]}")
            
        return indicators
    
    def _calculate_microstructure_features(self, df: pd.DataFrame, base_features: Dict) -> Dict[str, float]:
        """Calculate market microstructure features for intraday trading"""
        structure = {}
        
        try:
            if len(df) == 0:
                return {'bid_ask_spread': 0.0, 'price_impact': 0.0, 'order_flow': 0.0}
            
            # Price momentum cascade
            if len(df) >= 3:
                close = df['Close']
                structure['momentum_1min'] = base_features.get('price_change_1m', 0.0)
                structure['momentum_consistency'] = self._calculate_momentum_consistency(close)
                
            # Volume-price relationship
            if 'Volume' in df.columns and len(df) >= 5:
                structure['volume_price_trend'] = self._calculate_volume_price_trend(df)
            else:
                structure['volume_price_trend'] = 0.0
                
            # Price range analysis  
            if len(df) > 0:
                last_row = df.iloc[-1]
                if 'High' in last_row and 'Low' in last_row:
                    high = last_row['High']
                    low = last_row['Low']
                    close = last_row['Close']
                    structure['range_position'] = (close - low) / (high - low) if high != low else 0.5
                else:
                    structure['range_position'] = 0.5
                    
        except Exception as e:
            print(f"⚠️  Microstructure error: {str(e)[:30]}")
            structure = {'momentum_consistency': 0.0, 'volume_price_trend': 0.0, 'range_position': 0.5}
        
        return structure
    
    def _analyze_market_structure(self, base_data: Dict, market_context: Dict) -> Dict[str, float]:
        """Analyze overall market structure for next-day predictions"""
        structure = {}
        
        try:
            # Market regime detection
            if base_data.get('timeframes', {}).get('1d') is not None:
                daily_data = base_data['timeframes']['1d'] 
                structure['trend_regime'] = self._detect_trend_regime(daily_data)
                structure['volatility_regime'] = self._detect_volatility_regime(daily_data)
                
            # Institutional flow proxy
            structure['institutional_pressure'] = self._estimate_institutional_flow(base_data)
            
            # Market stress indicators
            vix_data = market_context.get('volatility', {})
            structure['market_stress'] = abs(vix_data.get('VIX', 0.0)) / 10.0  # Normalize VIX change
            
        except Exception as e:
            print(f"⚠️  Market structure error: {str(e)[:50]}")
            structure = {'trend_regime': 0.0, 'volatility_regime': 0.0, 'institutional_pressure': 0.0, 'market_stress': 0.0}
        
        return structure
    
    def _calculate_cross_asset_features(self, market_context: Dict) -> Dict[str, float]:
        """Calculate cross-asset correlation features"""
        cross_asset = {}
        
        try:
            # Futures correlation
            futures = market_context.get('futures', {})
            if futures:
                # Tech heavy futures (NQ) correlation
                cross_asset['nq_correlation'] = futures.get('NQ', 0.0) * 0.8  # AMD is tech-heavy
                cross_asset['es_correlation'] = futures.get('ES', 0.0) * 0.6  # General market
                cross_asset['futures_momentum'] = np.mean(list(futures.values()))
            else:
                cross_asset.update({'nq_correlation': 0.0, 'es_correlation': 0.0, 'futures_momentum': 0.0})
            
            # Global market influence
            global_indices = market_context.get('global_indices', {})
            if global_indices:
                cross_asset['global_sentiment'] = np.mean(list(global_indices.values()))
                cross_asset['asia_influence'] = global_indices.get('Nikkei', 0.0) * 0.3
                cross_asset['europe_influence'] = global_indices.get('DAX', 0.0) * 0.5
            else:
                cross_asset.update({'global_sentiment': 0.0, 'asia_influence': 0.0, 'europe_influence': 0.0})
            
            # Dollar and volatility impact
            vol_indicators = market_context.get('volatility', {})
            if vol_indicators:
                cross_asset['dollar_impact'] = vol_indicators.get('DXY', 0.0) * -0.3  # Inverse correlation
                cross_asset['vix_fear'] = vol_indicators.get('VIX', 0.0) * -0.5  # Risk-off sentiment
                cross_asset['bond_impact'] = vol_indicators.get('US10Y', 0.0) * -0.2  # Interest rate impact
            else:
                cross_asset.update({'dollar_impact': 0.0, 'vix_fear': 0.0, 'bond_impact': 0.0})
                
        except Exception as e:
            print(f"⚠️  Cross-asset features error: {str(e)[:50]}")
            cross_asset = {f'{name}': 0.0 for name in ['nq_correlation', 'es_correlation', 'global_sentiment', 'dollar_impact', 'vix_fear']}
        
        return cross_asset
    
    def _prepare_time_series(self, df: pd.DataFrame, length: int = 20) -> np.ndarray:
        """Prepare time series data for LSTM models"""
        try:
            if len(df) == 0:
                return np.zeros((length, 4))  # OHLC
            
            # Get OHLC data
            ohlc_data = []
            for col in ['Open', 'High', 'Low', 'Close']:
                if col in df.columns:
                    series = df[col].fillna(method='ffill').fillna(0)
                    ohlc_data.append(series.tail(length).values)
                else:
                    # Use Close as fallback
                    close_data = df['Close'].fillna(method='ffill').fillna(0) if 'Close' in df.columns else pd.Series([0] * len(df))
                    ohlc_data.append(close_data.tail(length).values)
            
            # Pad or truncate to exact length
            time_series = np.column_stack(ohlc_data)
            if len(time_series) < length:
                padding = np.tile(time_series[-1:], (length - len(time_series), 1))
                time_series = np.vstack([padding, time_series])
            elif len(time_series) > length:
                time_series = time_series[-length:]
                
            return time_series
            
        except Exception as e:
            print(f"⚠️  Time series preparation error: {str(e)[:50]}")
            return np.zeros((length, 4))
    
    def _prepare_comprehensive_time_series(self, base_data: Dict, length: int = 60) -> np.ndarray:
        """Prepare comprehensive time series for next-day LSTM models"""
        try:
            # Try to get hourly data first, then daily
            for timeframe in ['1h', '1d']:
                if base_data.get('timeframes', {}).get(timeframe) is not None:
                    df = base_data['timeframes'][timeframe]
                    return self._prepare_time_series(df, length)
            
            # Fallback
            return np.zeros((length, 4))
            
        except:
            return np.zeros((length, 4))
    
    # Helper functions
    def _encode_data_quality(self, quality: str) -> float:
        """Encode data quality as numerical feature"""
        quality_map = {'live': 1.0, 'fallback': 0.5, 'stale': 0.0}
        return quality_map.get(quality, 0.0)
    
    def _encode_session_time(self) -> float:
        """Encode current session time as feature"""
        try:
            from datetime import datetime
            import pytz
            
            et_tz = pytz.timezone('US/Eastern')
            current_et = datetime.now(et_tz)
            
            # Market hours: 9:30 AM to 4:00 PM ET
            market_start = 9.5  # 9:30 AM
            market_end = 16.0   # 4:00 PM
            
            current_hour = current_et.hour + current_et.minute / 60.0
            
            if market_start <= current_hour <= market_end:
                # During market hours: 0.0 to 1.0
                return (current_hour - market_start) / (market_end - market_start)
            else:
                # Outside market hours
                return -1.0
                
        except:
            return 0.0
    
    def _fast_rsi(self, prices: pd.Series, window: int) -> float:
        """Fast RSI calculation"""
        try:
            if len(prices) < window + 1:
                return 50.0
                
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
            
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            result = rsi.iloc[-1]
            return float(result) if not np.isnan(result) else 50.0
            
        except:
            return 50.0
    
    def _calculate_macd(self, prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[float, float]:
        """Calculate MACD"""
        try:
            if len(prices) < max(fast, slow, signal):
                return 0.0, 0.0
            
            ema_fast = prices.ewm(span=fast).mean()
            ema_slow = prices.ewm(span=slow).mean()
            
            macd_line = ema_fast - ema_slow
            signal_line = macd_line.ewm(span=signal).mean()
            
            return float(macd_line.iloc[-1]), float(signal_line.iloc[-1])
            
        except:
            return 0.0, 0.0
    
    def _calculate_bollinger_bands(self, prices: pd.Series, window: int, std_dev: float) -> Tuple[float, float, float]:
        """Calculate Bollinger Bands"""
        try:
            if len(prices) < window:
                current_price = prices.iloc[-1] if len(prices) > 0 else 0.0
                return current_price, current_price, current_price
            
            rolling_mean = prices.rolling(window).mean()
            rolling_std = prices.rolling(window).std()
            
            upper_band = rolling_mean + (rolling_std * std_dev)
            lower_band = rolling_mean - (rolling_std * std_dev)
            
            return float(upper_band.iloc[-1]), float(rolling_mean.iloc[-1]), float(lower_band.iloc[-1])
            
        except:
            return 0.0, 0.0, 0.0
    
    def _calculate_atr(self, high: pd.Series, low: pd.Series, close: pd.Series, window: int) -> float:
        """Calculate Average True Range"""
        try:
            if len(high) < 2:
                return 0.0
            
            tr1 = high - low
            tr2 = abs(high - close.shift())
            tr3 = abs(low - close.shift())
            
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            atr = tr.rolling(window).mean()
            
            return float(atr.iloc[-1])
            
        except:
            return 0.0
    
    def _calculate_momentum_consistency(self, prices: pd.Series) -> float:
        """Calculate momentum consistency score"""
        try:
            if len(prices) < 3:
                return 0.0
            
            returns = prices.pct_change().dropna()
            if len(returns) < 2:
                return 0.0
            
            # Count consistent direction
            positive_returns = (returns > 0).sum()
            total_returns = len(returns)
            
            consistency = abs((positive_returns / total_returns) - 0.5) * 2  # 0 to 1 scale
            return float(consistency)
            
        except:
            return 0.0
    
    def _calculate_volume_price_trend(self, df: pd.DataFrame) -> float:
        """Calculate volume-price trend correlation"""
        try:
            if len(df) < 5 or 'Volume' not in df.columns:
                return 0.0
            
            price_changes = df['Close'].pct_change().dropna()
            volume_changes = df['Volume'].pct_change().dropna()
            
            if len(price_changes) >= 3 and len(volume_changes) >= 3:
                correlation = price_changes.corr(volume_changes)
                return float(correlation) if not np.isnan(correlation) else 0.0
            return 0.0
            
        except:
            return 0.0
    
    def _detect_trend_regime(self, df: pd.DataFrame) -> float:
        """Detect trend regime (-1 to 1, bearish to bullish)"""
        try:
            if len(df) < 20:
                return 0.0
            
            close = df['Close']
            sma_20 = close.rolling(20).mean()
            sma_50 = close.rolling(50).mean() if len(df) >= 50 else sma_20
            
            # Current price vs moving averages
            price_vs_sma20 = (close.iloc[-1] / sma_20.iloc[-1] - 1) if sma_20.iloc[-1] > 0 else 0.0
            sma20_vs_sma50 = (sma_20.iloc[-1] / sma_50.iloc[-1] - 1) if sma_50.iloc[-1] > 0 else 0.0
            
            # Combine signals
            trend_score = (price_vs_sma20 + sma20_vs_sma50) * 5  # Scale to roughly -1 to 1
            return float(np.clip(trend_score, -1, 1))
            
        except:
            return 0.0
    
    def _detect_volatility_regime(self, df: pd.DataFrame) -> float:
        """Detect volatility regime (0 to 1, low to high vol)"""
        try:
            if len(df) < 20:
                return 0.5
            
            returns = df['Close'].pct_change().dropna()
            current_vol = returns.tail(5).std() * np.sqrt(252)  # Annualized
            historical_vol = returns.tail(20).std() * np.sqrt(252)
            
            if historical_vol > 0:
                vol_ratio = current_vol / historical_vol
                vol_regime = min(vol_ratio, 2.0) / 2.0  # Cap at 2x, scale to 0-1
                return float(vol_regime)
            return 0.5
            
        except:
            return 0.5
    
    def _estimate_institutional_flow(self, base_data: Dict) -> float:
        """Estimate institutional flow pressure"""
        try:
            # Use volume and price action as proxy
            if base_data.get('timeframes', {}).get('1d') is not None:
                daily_data = base_data['timeframes']['1d']
                
                if len(daily_data) >= 5:
                    # Volume-weighted price momentum
                    close = daily_data['Close']
                    volume = daily_data.get('Volume', pd.Series([1] * len(daily_data)))
                    
                    price_change = close.pct_change().fillna(0)
                    volume_weighted_momentum = (price_change * volume).sum() / volume.sum()
                    
                    return float(volume_weighted_momentum * 100)  # Scale up
            return 0.0
            
        except:
            return 0.0

# Create global instance
feature_engineer = FeatureEngineer()