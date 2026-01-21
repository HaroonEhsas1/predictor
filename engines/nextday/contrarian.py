"""
Advanced Contrarian Analysis for Trading System
Implements sophisticated divergence detection and institutional flow analysis
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
import logging
from datetime import datetime, timedelta
from scipy import stats
from scipy.signal import argrelextrema
import warnings

# Try to import scipy, fall back to basic implementations if not available
try:
    from scipy import stats
    from scipy.signal import argrelextrema
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    # Use pandas/numpy only for pivot detection
    stats = None
    argrelextrema = None

logger = logging.getLogger(__name__)

class ContrarianSignalEngine:
    """
    Professional contrarian signal detection for institutional-grade trading
    Detects hidden market forces that contradict obvious price movements
    """
    
    def __init__(self):
        self.min_bars_for_divergence = 20
        self.pivot_window = 3
        self.volume_lookback = 20
        
    def compute_contrarian_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Main entry point for computing all contrarian features
        
        Args:
            df: OHLCV DataFrame with proper datetime index
            
        Returns:
            DataFrame with contrarian features as time series (no data leakage)
        """
        try:
            if len(df) < self.min_bars_for_divergence:
                return self._get_empty_features_df(df.index)
            
            # Initialize features DataFrame
            features_df = pd.DataFrame(index=df.index)
            
            # 1. RSI Divergence Analysis - compute as time series
            rsi_features = self._compute_rsi_divergence_series(df)
            for col, values in rsi_features.items():
                features_df[col] = values
            
            # 2. Price-Volume Divergence - compute as time series
            pv_features = self._compute_price_volume_divergence_series(df)
            for col, values in pv_features.items():
                features_df[col] = values
            
            # 3. Institutional Flow Proxies - compute as time series
            institutional_features = self._compute_institutional_flow_proxies_series(df)
            for col, values in institutional_features.items():
                features_df[col] = values
            
            # 4. Dark Pool Activity Proxies - compute as time series
            darkpool_features = self._compute_dark_pool_proxies_series(df)
            for col, values in darkpool_features.items():
                features_df[col] = values
            
            # 5. Composite Contrarian Score - compute as time series
            features_df['contrarian_composite_score'] = self._compute_composite_score_series(features_df)
            
            # Fill NaN values with zeros
            features_df = features_df.fillna(0.0)
            
            return features_df
            
        except Exception as e:
            logger.warning(f"Error computing contrarian features: {e}")
            return self._get_empty_features_df(df.index)
    
    def _compute_rsi_divergence_series(self, df: pd.DataFrame) -> Dict[str, pd.Series]:
        """Compute RSI divergence as time series to avoid data leakage"""
        try:
            close_series = df['Close'] if isinstance(df['Close'], pd.Series) else pd.Series(df['Close'])
            rsi = self._calculate_rsi(close_series, period=14)
            
            # Simple rolling divergence detection
            window = 10
            rsi_trend = rsi.rolling(window).apply(lambda x: np.polyfit(range(len(x)), x, 1)[0] if len(x) == window else 0, raw=False)
            price_trend = close_series.rolling(window).apply(lambda x: np.polyfit(range(len(x)), x, 1)[0] if len(x) == window else 0, raw=False)
            
            # Divergence when trends have opposite signs
            divergence_strength = np.where(
                (rsi_trend > 0) & (price_trend < 0), 1.0,  # Bullish divergence
                np.where((rsi_trend < 0) & (price_trend > 0), -1.0, 0.0)  # Bearish divergence
            )
            
            return {
                'rsi_div_bull': pd.Series(np.maximum(divergence_strength, 0), index=df.index),
                'rsi_div_bear': pd.Series(np.maximum(-divergence_strength, 0), index=df.index),
                'rsi_div_strength': pd.Series(np.abs(divergence_strength), index=df.index),
                'rsi_div_age': pd.Series(0.5, index=df.index)  # Simplified age metric
            }
        except Exception as e:
            logger.warning(f"RSI divergence series error: {e}")
            return {
                'rsi_div_bull': pd.Series(0.0, index=df.index),
                'rsi_div_bear': pd.Series(0.0, index=df.index),
                'rsi_div_strength': pd.Series(0.0, index=df.index),
                'rsi_div_age': pd.Series(0.0, index=df.index)
            }
    
    def _compute_price_volume_divergence_series(self, df: pd.DataFrame) -> Dict[str, pd.Series]:
        """Compute price-volume divergence as time series"""
        try:
            obv = self._calculate_obv(df)
            close_series = df['Close'] if isinstance(df['Close'], pd.Series) else pd.Series(df['Close'])
            
            window = 10
            obv_trend = obv.rolling(window).apply(lambda x: np.polyfit(range(len(x)), x, 1)[0] if len(x) == window else 0, raw=False)
            price_trend = close_series.rolling(window).apply(lambda x: np.polyfit(range(len(x)), x, 1)[0] if len(x) == window else 0, raw=False)
            
            # Normalize trends
            obv_trend_norm = obv_trend / (obv.rolling(window).std() + 1e-6)
            price_trend_norm = price_trend / (close_series.rolling(window).std() + 1e-6)
            
            # Divergence detection
            divergence = np.abs(obv_trend_norm - price_trend_norm)
            vol_confirm = close_series.pct_change().rolling(5).corr(df['Volume'].pct_change().rolling(5))
            
            return {
                'obv_price_div': divergence.fillna(0),
                'vpt_price_div': divergence.fillna(0) * 0.8,  # Similar pattern
                'mfi_div': divergence.fillna(0) * 0.6,  # Proxy
                'vol_confirm_score': vol_confirm.fillna(0),
                'dry_up_score': pd.Series(0.0, index=df.index)  # Simplified
            }
        except Exception as e:
            logger.warning(f"Price-volume divergence series error: {e}")
            return {
                'obv_price_div': pd.Series(0.0, index=df.index),
                'vpt_price_div': pd.Series(0.0, index=df.index),
                'mfi_div': pd.Series(0.0, index=df.index),
                'vol_confirm_score': pd.Series(0.0, index=df.index),
                'dry_up_score': pd.Series(0.0, index=df.index)
            }
    
    def _compute_institutional_flow_proxies_series(self, df: pd.DataFrame) -> Dict[str, pd.Series]:
        """Compute institutional flow proxies as time series"""
        try:
            adl = self._calculate_adl(df)
            close_series = df['Close'] if isinstance(df['Close'], pd.Series) else pd.Series(df['Close'])
            
            # ADL trend divergence
            window = 10
            adl_trend = adl.rolling(window).apply(lambda x: np.polyfit(range(len(x)), x, 1)[0] if len(x) == window else 0, raw=False)
            price_trend = close_series.rolling(window).apply(lambda x: np.polyfit(range(len(x)), x, 1)[0] if len(x) == window else 0, raw=False)
            
            adl_divergence = np.abs(adl_trend - price_trend)
            
            # Volume-based proxies
            vwap = (df['High'] + df['Low'] + df['Close']).div(3).multiply(df['Volume']).rolling(20).sum().div(df['Volume'].rolling(20).sum())
            vwap_distance = np.abs(close_series - vwap) / vwap
            
            return {
                'adl_trend_div': adl_divergence.fillna(0),
                'vwap_persist_score': (1 - vwap_distance).fillna(0.5),
                'close_range_volume_score': pd.Series(0.0, index=df.index),  # Simplified
                'absorption_score': pd.Series(0.0, index=df.index)  # Simplified
            }
        except Exception as e:
            logger.warning(f"Institutional flow series error: {e}")
            return {
                'adl_trend_div': pd.Series(0.0, index=df.index),
                'vwap_persist_score': pd.Series(0.0, index=df.index),
                'close_range_volume_score': pd.Series(0.0, index=df.index),
                'absorption_score': pd.Series(0.0, index=df.index)
            }
    
    def _compute_dark_pool_proxies_series(self, df: pd.DataFrame) -> Dict[str, pd.Series]:
        """Compute dark pool proxies as time series"""
        try:
            # Volume clustering
            volume_std = df['Volume'].rolling(10).std()
            volume_mean = df['Volume'].rolling(10).mean()
            clustering = volume_std / (volume_mean + 1e-6)
            
            # Volume during consolidation
            price_volatility = df['Close'].rolling(10).std() / df['Close'].rolling(10).mean()
            volume_anomaly = df['Volume'] / df['Volume'].rolling(20).mean()
            consolidation_anomaly = volume_anomaly / (price_volatility + 1e-6)
            
            return {
                'block_trade_proxy': clustering.fillna(0),
                'consolidation_volume_anomaly': consolidation_anomaly.fillna(0),
                'auction_imbalance_proxy': pd.Series(0.0, index=df.index),  # Simplified
                'dark_pool_proxy_score': (clustering + consolidation_anomaly).div(2).fillna(0)
            }
        except Exception as e:
            logger.warning(f"Dark pool series error: {e}")
            return {
                'block_trade_proxy': pd.Series(0.0, index=df.index),
                'consolidation_volume_anomaly': pd.Series(0.0, index=df.index),
                'auction_imbalance_proxy': pd.Series(0.0, index=df.index),
                'dark_pool_proxy_score': pd.Series(0.0, index=df.index)
            }
    
    def _compute_composite_score_series(self, features_df: pd.DataFrame) -> pd.Series:
        """Compute composite contrarian score as time series"""
        try:
            # Divergence signals
            div_cols = [col for col in features_df.columns if 'div' in col or 'divergence' in col]
            div_score = features_df[div_cols].mean(axis=1) if div_cols else pd.Series(0.0, index=features_df.index)
            
            # Institutional signals  
            inst_cols = [col for col in features_df.columns if 'adl' in col or 'vwap' in col or 'absorption' in col]
            inst_score = features_df[inst_cols].mean(axis=1) if inst_cols else pd.Series(0.0, index=features_df.index)
            
            # Dark pool signals
            dp_cols = [col for col in features_df.columns if 'block' in col or 'dark_pool' in col or 'consolidation' in col]
            dp_score = features_df[dp_cols].mean(axis=1) if dp_cols else pd.Series(0.0, index=features_df.index)
            
            # Weighted composite
            composite = div_score * 0.4 + inst_score * 0.35 + dp_score * 0.25
            return np.clip(composite, -1.0, 1.0)
            
        except Exception as e:
            logger.warning(f"Composite score series error: {e}")
            return pd.Series(0.0, index=features_df.index)
    
    def _get_empty_features_df(self, index: pd.Index) -> pd.DataFrame:
        """Return empty feature DataFrame when calculation fails"""
        empty_features = self._get_empty_features()
        return pd.DataFrame({k: pd.Series(v, index=index) for k, v in empty_features.items()})
    
    def _compute_rsi_divergence(self, df: pd.DataFrame) -> Dict[str, float]:
        """
        Detect TRUE RSI divergence - price vs RSI confirmation
        """
        try:
            # Calculate RSI
            close_series = df['Close'] if isinstance(df['Close'], pd.Series) else pd.Series(df['Close'])
            rsi = self._calculate_rsi(close_series, period=14)
            if len(rsi) < self.min_bars_for_divergence:
                return {'rsi_div_bull': 0.0, 'rsi_div_bear': 0.0, 'rsi_div_strength': 0.0, 'rsi_div_age': 0.0}
            
            # Find price and RSI pivots
            price_highs = self._find_pivots(close_series, pivot_type='high')
            price_lows = self._find_pivots(close_series, pivot_type='low')
            rsi_highs = self._find_pivots(rsi, pivot_type='high')
            rsi_lows = self._find_pivots(rsi, pivot_type='low')
            
            # Detect bullish divergence (price lower low, RSI higher low)
            bull_div_strength = self._detect_bullish_divergence(
                close_series, rsi, price_lows, rsi_lows
            )
            
            # Detect bearish divergence (price higher high, RSI lower high)
            bear_div_strength = self._detect_bearish_divergence(
                close_series, rsi, price_highs, rsi_highs
            )
            
            # Age of most recent divergence
            div_age = self._calculate_divergence_age(df, bull_div_strength, bear_div_strength)
            
            return {
                'rsi_div_bull': bull_div_strength,
                'rsi_div_bear': bear_div_strength,
                'rsi_div_strength': max(bull_div_strength, bear_div_strength),
                'rsi_div_age': div_age
            }
            
        except Exception as e:
            logger.warning(f"RSI divergence calculation error: {e}")
            return {'rsi_div_bull': 0.0, 'rsi_div_bear': 0.0, 'rsi_div_strength': 0.0, 'rsi_div_age': 0.0}
    
    def _compute_price_volume_divergence(self, df: pd.DataFrame) -> Dict[str, float]:
        """
        Detect price-volume divergence using multiple indicators
        """
        try:
            # On-Balance Volume divergence
            obv = self._calculate_obv(df)
            close_series = df['Close'] if isinstance(df['Close'], pd.Series) else pd.Series(df['Close'])
            obv_div = self._calculate_trend_divergence(close_series, obv)
            
            # Volume Price Trend divergence
            vpt = self._calculate_vpt(df)
            vpt_div = self._calculate_trend_divergence(close_series, vpt)
            
            # Money Flow Index divergence
            mfi = self._calculate_mfi(df)
            mfi_div = self._calculate_oscillator_divergence(close_series, mfi)
            
            # Volume confirmation score
            vol_confirm = self._calculate_volume_confirmation(df)
            
            # Volume dry-up detection
            dry_up_score = self._detect_volume_dryup(df)
            
            return {
                'obv_price_div': obv_div,
                'vpt_price_div': vpt_div,
                'mfi_div': mfi_div,
                'vol_confirm_score': vol_confirm,
                'dry_up_score': dry_up_score
            }
            
        except Exception as e:
            logger.warning(f"Price-volume divergence error: {e}")
            return {
                'obv_price_div': 0.0, 'vpt_price_div': 0.0, 'mfi_div': 0.0,
                'vol_confirm_score': 0.0, 'dry_up_score': 0.0
            }
    
    def _compute_institutional_flow_proxies(self, df: pd.DataFrame) -> Dict[str, float]:
        """
        Detect institutional money flow patterns
        """
        try:
            # Accumulation/Distribution Line trend
            adl = self._calculate_adl(df)
            close_series = df['Close'] if isinstance(df['Close'], pd.Series) else pd.Series(df['Close'])
            adl_trend_div = self._calculate_trend_divergence(close_series, adl)
            
            # VWAP persistence with high volume
            vwap_persist = self._calculate_vwap_persistence(df)
            
            # Closing range with volume (accumulation/distribution)
            close_range_vol = self._calculate_close_range_volume(df)
            
            # Large range with price absorption
            absorption_score = self._calculate_absorption_score(df)
            
            return {
                'adl_trend_div': adl_trend_div,
                'vwap_persist_score': vwap_persist,
                'close_range_volume_score': close_range_vol,
                'absorption_score': absorption_score
            }
            
        except Exception as e:
            logger.warning(f"Institutional flow proxy error: {e}")
            return {
                'adl_trend_div': 0.0, 'vwap_persist_score': 0.0,
                'close_range_volume_score': 0.0, 'absorption_score': 0.0
            }
    
    def _compute_dark_pool_proxies(self, df: pd.DataFrame) -> Dict[str, float]:
        """
        Detect dark pool activity through volume and price anomalies
        """
        try:
            # Block trade clustering (variance in volume patterns)
            block_trade_proxy = self._calculate_block_trade_clustering(df)
            
            # Volume anomaly during price consolidation
            consolidation_volume = self._calculate_consolidation_volume_anomaly(df)
            
            # Gap vs auction range analysis
            auction_imbalance = self._calculate_auction_imbalance(df)
            
            # Composite dark pool score
            dark_pool_composite = np.mean([
                block_trade_proxy, consolidation_volume, auction_imbalance
            ])
            
            return {
                'block_trade_proxy': block_trade_proxy,
                'consolidation_volume_anomaly': consolidation_volume,
                'auction_imbalance_proxy': auction_imbalance,
                'dark_pool_proxy_score': dark_pool_composite
            }
            
        except Exception as e:
            logger.warning(f"Dark pool proxy error: {e}")
            return {
                'block_trade_proxy': 0.0, 'consolidation_volume_anomaly': 0.0,
                'auction_imbalance_proxy': 0.0, 'dark_pool_proxy_score': 0.0
            }
    
    def _compute_composite_score(self, features: Dict[str, float]) -> float:
        """
        Compute composite contrarian signal strength
        """
        try:
            # Weight different signal types
            weights = {
                'divergence_signals': 0.4,  # RSI, Price-Volume divergence
                'institutional_signals': 0.35,  # ADL, VWAP persistence
                'dark_pool_signals': 0.25   # Block trades, volume anomalies
            }
            
            # Divergence component
            div_score = np.mean([
                features.get('rsi_div_strength', 0),
                features.get('obv_price_div', 0),
                features.get('mfi_div', 0)
            ])
            
            # Institutional component
            inst_score = np.mean([
                features.get('adl_trend_div', 0),
                features.get('vwap_persist_score', 0),
                features.get('absorption_score', 0)
            ])
            
            # Dark pool component
            dp_score = features.get('dark_pool_proxy_score', 0)
            
            # Weighted composite
            composite = (
                div_score * weights['divergence_signals'] +
                inst_score * weights['institutional_signals'] +
                dp_score * weights['dark_pool_signals']
            )
            
            # Normalize to [-1, 1] range
            return np.clip(composite, -1.0, 1.0)
            
        except Exception as e:
            logger.warning(f"Composite score error: {e}")
            return 0.0
    
    # Technical indicator calculations
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI with proper handling of edge cases"""
        try:
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            
            # Avoid division by zero
            loss_safe = loss.replace(0, np.nan) if hasattr(loss, 'replace') else pd.Series(loss).replace(0, np.nan)
            rs = gain / loss_safe
            rsi = 100 - (100 / (1 + rs))
            
            return rsi.fillna(50) if hasattr(rsi, 'fillna') else pd.Series(rsi).fillna(50)
            
        except Exception as e:
            logger.warning(f"RSI calculation error: {e}")
            return pd.Series([50] * len(prices), index=prices.index)
    
    def _calculate_obv(self, df: pd.DataFrame) -> pd.Series:
        """Calculate On-Balance Volume"""
        try:
            obv = pd.Series(index=df.index, dtype=float)
            obv.iloc[0] = df['Volume'].iloc[0]
            
            for i in range(1, len(df)):
                if df['Close'].iloc[i] > df['Close'].iloc[i-1]:
                    obv.iloc[i] = obv.iloc[i-1] + df['Volume'].iloc[i]
                elif df['Close'].iloc[i] < df['Close'].iloc[i-1]:
                    obv.iloc[i] = obv.iloc[i-1] - df['Volume'].iloc[i]
                else:
                    obv.iloc[i] = obv.iloc[i-1]
            
            return obv
            
        except Exception as e:
            logger.warning(f"OBV calculation error: {e}")
            return pd.Series([0] * len(df), index=df.index)
    
    def _calculate_vpt(self, df: pd.DataFrame) -> pd.Series:
        """Calculate Volume Price Trend"""
        try:
            vpt = pd.Series(index=df.index, dtype=float)
            vpt.iloc[0] = df['Volume'].iloc[0]
            
            for i in range(1, len(df)):
                price_change = (df['Close'].iloc[i] - df['Close'].iloc[i-1]) / df['Close'].iloc[i-1]
                vpt.iloc[i] = vpt.iloc[i-1] + (df['Volume'].iloc[i] * price_change)
            
            return vpt
            
        except Exception as e:
            logger.warning(f"VPT calculation error: {e}")
            return pd.Series([0] * len(df), index=df.index)
    
    def _calculate_mfi(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Money Flow Index"""
        try:
            typical_price = (df['High'] + df['Low'] + df['Close']) / 3
            money_flow = typical_price * df['Volume']
            
            positive_flow = pd.Series([0.0] * len(df), index=df.index)
            negative_flow = pd.Series([0.0] * len(df), index=df.index)
            
            for i in range(1, len(df)):
                if typical_price.iloc[i] > typical_price.iloc[i-1]:
                    positive_flow.iloc[i] = money_flow.iloc[i]
                elif typical_price.iloc[i] < typical_price.iloc[i-1]:
                    negative_flow.iloc[i] = money_flow.iloc[i]
            
            pos_mf = positive_flow.rolling(window=period).sum()
            neg_mf = negative_flow.rolling(window=period).sum()
            
            # Avoid division by zero
            neg_mf_safe = neg_mf.replace(0, np.nan) if hasattr(neg_mf, 'replace') else pd.Series(neg_mf).replace(0, np.nan)
            mfi = 100 - (100 / (1 + (pos_mf / neg_mf_safe)))
            
            return mfi.fillna(50) if hasattr(mfi, 'fillna') else pd.Series(mfi).fillna(50)
            
        except Exception as e:
            logger.warning(f"MFI calculation error: {e}")
            return pd.Series([50] * len(df), index=df.index)
    
    def _calculate_adl(self, df: pd.DataFrame) -> pd.Series:
        """Calculate Accumulation/Distribution Line"""
        try:
            clv = ((df['Close'] - df['Low']) - (df['High'] - df['Close'])) / (df['High'] - df['Low'])
            clv = clv.replace([np.inf, -np.inf], 0).fillna(0)
            
            money_flow_volume = clv * df['Volume']
            adl = money_flow_volume.cumsum()
            
            return adl
            
        except Exception as e:
            logger.warning(f"ADL calculation error: {e}")
            return pd.Series([0] * len(df), index=df.index)
    
    # Divergence detection helpers
    def _find_pivots(self, series: pd.Series, pivot_type: str = 'high') -> List[int]:
        """Find pivot highs or lows using scipy or fallback method"""
        try:
            if SCIPY_AVAILABLE and argrelextrema is not None:
                if pivot_type == 'high':
                    pivots = argrelextrema(series.values, np.greater, order=self.pivot_window)[0]
                else:
                    pivots = argrelextrema(series.values, np.less, order=self.pivot_window)[0]
                return pivots.tolist()
            else:
                # Fallback implementation using rolling windows
                return self._find_pivots_fallback(series, pivot_type)
            
        except Exception as e:
            logger.warning(f"Pivot detection error: {e}")
            return []
    
    def _find_pivots_fallback(self, series: pd.Series, pivot_type: str = 'high') -> List[int]:
        """Fallback pivot detection without scipy"""
        try:
            pivots = []
            window = self.pivot_window
            
            for i in range(window, len(series) - window):
                is_pivot = False
                
                if pivot_type == 'high':
                    # Check if current point is higher than neighbors
                    is_pivot = all(series.iloc[i] > series.iloc[j] for j in range(i-window, i+window+1) if j != i)
                else:
                    # Check if current point is lower than neighbors
                    is_pivot = all(series.iloc[i] < series.iloc[j] for j in range(i-window, i+window+1) if j != i)
                
                if is_pivot:
                    pivots.append(i)
            
            return pivots
            
        except Exception as e:
            logger.warning(f"Fallback pivot detection error: {e}")
            return []
    
    def _detect_bullish_divergence(self, prices: pd.Series, oscillator: pd.Series, 
                                  price_lows: List[int], osc_lows: List[int]) -> float:
        """Detect bullish divergence between price and oscillator"""
        try:
            if len(price_lows) < 2 or len(osc_lows) < 2:
                return 0.0
            
            # Get last two significant lows
            recent_price_lows = sorted(price_lows)[-2:]
            recent_osc_lows = sorted(osc_lows)[-2:]
            
            if len(recent_price_lows) < 2 or len(recent_osc_lows) < 2:
                return 0.0
            
            # Check for divergence: price lower low, oscillator higher low
            price_trend = prices.iloc[recent_price_lows[-1]] - prices.iloc[recent_price_lows[-2]]
            osc_trend = oscillator.iloc[recent_osc_lows[-1]] - oscillator.iloc[recent_osc_lows[-2]]
            
            if price_trend < 0 and osc_trend > 0:
                # Strength based on divergence magnitude
                strength = min(abs(osc_trend) / abs(price_trend), 1.0) if price_trend != 0 else 0
                return strength
            
            return 0.0
            
        except Exception as e:
            logger.warning(f"Bullish divergence detection error: {e}")
            return 0.0
    
    def _detect_bearish_divergence(self, prices: pd.Series, oscillator: pd.Series,
                                  price_highs: List[int], osc_highs: List[int]) -> float:
        """Detect bearish divergence between price and oscillator"""
        try:
            if len(price_highs) < 2 or len(osc_highs) < 2:
                return 0.0
            
            # Get last two significant highs
            recent_price_highs = sorted(price_highs)[-2:]
            recent_osc_highs = sorted(osc_highs)[-2:]
            
            if len(recent_price_highs) < 2 or len(recent_osc_highs) < 2:
                return 0.0
            
            # Check for divergence: price higher high, oscillator lower high
            price_trend = prices.iloc[recent_price_highs[-1]] - prices.iloc[recent_price_highs[-2]]
            osc_trend = oscillator.iloc[recent_osc_highs[-1]] - oscillator.iloc[recent_osc_highs[-2]]
            
            if price_trend > 0 and osc_trend < 0:
                # Strength based on divergence magnitude
                strength = min(abs(osc_trend) / abs(price_trend), 1.0) if price_trend != 0 else 0
                return strength
            
            return 0.0
            
        except Exception as e:
            logger.warning(f"Bearish divergence detection error: {e}")
            return 0.0
    
    def _calculate_trend_divergence(self, prices: pd.Series, indicator: pd.Series, 
                                   window: int = 10) -> float:
        """Calculate divergence between price and indicator trends"""
        try:
            if len(prices) < window:
                return 0.0
            
            # Calculate recent trends using proper indexing
            price_vals = prices.tail(window) if hasattr(prices, 'tail') else prices[-window:]
            ind_vals = indicator.tail(window) if hasattr(indicator, 'tail') else indicator[-window:]
            
            if SCIPY_AVAILABLE and stats is not None:
                price_trend = stats.linregress(range(window), price_vals)[0]
                ind_trend = stats.linregress(range(window), ind_vals)[0]
            else:
                # Simple linear trend using numpy
                x = np.arange(window)
                price_trend = np.polyfit(x, price_vals, 1)[0]
                ind_trend = np.polyfit(x, ind_vals, 1)[0]
            
            # Normalize and calculate divergence
            price_mean = price_vals.mean() if hasattr(price_vals, 'mean') else np.mean(price_vals)
            ind_mean = ind_vals.mean() if hasattr(ind_vals, 'mean') else np.mean(ind_vals)
            
            price_trend_norm = price_trend / price_mean if price_mean != 0 else 0
            ind_trend_norm = ind_trend / ind_mean if ind_mean != 0 else 0
            
            # Divergence when trends have opposite signs
            if (price_trend_norm > 0 and ind_trend_norm < 0) or (price_trend_norm < 0 and ind_trend_norm > 0):
                return abs(price_trend_norm - ind_trend_norm)
            
            return 0.0
            
        except Exception as e:
            logger.warning(f"Trend divergence error: {e}")
            return 0.0
    
    def _calculate_oscillator_divergence(self, prices: pd.Series, oscillator: pd.Series) -> float:
        """Calculate divergence for oscillator-type indicators"""
        try:
            # Find recent highs and lows for both price and oscillator
            price_highs = self._find_pivots(prices, 'high')
            price_lows = self._find_pivots(prices, 'low')
            osc_highs = self._find_pivots(oscillator, 'high')
            osc_lows = self._find_pivots(oscillator, 'low')
            
            # Check for bullish and bearish divergences
            bull_div = self._detect_bullish_divergence(prices, oscillator, price_lows, osc_lows)
            bear_div = self._detect_bearish_divergence(prices, oscillator, price_highs, osc_highs)
            
            # Return the stronger signal
            return max(bull_div, bear_div)
            
        except Exception as e:
            logger.warning(f"Oscillator divergence error: {e}")
            return 0.0
    
    # Volume analysis methods
    def _calculate_volume_confirmation(self, df: pd.DataFrame, window: int = 10) -> float:
        """Calculate how well volume confirms price moves"""
        try:
            recent_data = df.tail(window)
            
            # Price changes and volume changes
            price_changes = recent_data['Close'].pct_change().fillna(0)
            volume_changes = recent_data['Volume'].pct_change().fillna(0)
            
            # Calculate correlation
            if len(price_changes) > 1 and price_changes.std() > 0 and volume_changes.std() > 0:
                try:
                    correlation = price_changes.corr(volume_changes.abs())  # Volume should increase with price moves
                    return float(correlation) if not np.isnan(correlation) else 0.0
                except Exception:
                    return 0.0
            
            return 0.0
            
        except Exception as e:
            logger.warning(f"Volume confirmation error: {e}")
            return 0.0
    
    def _detect_volume_dryup(self, df: pd.DataFrame, window: int = 5) -> float:
        """Detect volume dry-up patterns near price extremes"""
        try:
            recent_data = df.tail(window)
            
            # Check if price is near recent high/low
            recent_high = recent_data['High'].max()
            recent_low = recent_data['Low'].min()
            current_price = recent_data['Close'].iloc[-1]
            
            price_range = recent_high - recent_low
            if price_range == 0:
                return 0.0
            
            # Distance from extremes
            dist_from_high = (recent_high - current_price) / price_range
            dist_from_low = (current_price - recent_low) / price_range
            
            near_extreme = min(dist_from_high, dist_from_low) < 0.1
            
            if near_extreme:
                # Check for declining volume
                volume_trend = stats.linregress(range(len(recent_data)), recent_data['Volume'])[0]
                avg_volume = recent_data['Volume'].mean()
                
                if avg_volume > 0:
                    volume_decline = -volume_trend / avg_volume
                    return max(0, min(volume_decline, 1.0))
            
            return 0.0
            
        except Exception as e:
            logger.warning(f"Volume dry-up detection error: {e}")
            return 0.0
    
    # Institutional flow methods
    def _calculate_vwap_persistence(self, df: pd.DataFrame, window: int = 10) -> float:
        """Calculate VWAP persistence score with high volume"""
        try:
            recent_data = df.tail(window)
            
            # Calculate VWAP
            vwap = (recent_data['Volume'] * (recent_data['High'] + recent_data['Low'] + recent_data['Close']) / 3).cumsum() / recent_data['Volume'].cumsum()
            
            # Price distance from VWAP
            vwap_distance = abs(recent_data['Close'] - vwap) / vwap
            
            # Volume above average
            avg_volume = df['Volume'].rolling(window=20).mean()
            high_volume_mask = recent_data['Volume'] > avg_volume.tail(window)
            
            # Persistence score: consistent VWAP relationship with high volume
            if high_volume_mask.sum() > 0:
                persistence = 1 - vwap_distance[high_volume_mask].mean()
                return max(0, min(persistence, 1.0))
            
            return 0.0
            
        except Exception as e:
            logger.warning(f"VWAP persistence error: {e}")
            return 0.0
    
    def _calculate_close_range_volume(self, df: pd.DataFrame, window: int = 10) -> float:
        """Calculate closing range weighted by volume (accumulation/distribution)"""
        try:
            recent_data = df.tail(window)
            
            # Closing range calculation
            daily_range = recent_data['High'] - recent_data['Low']
            close_position = (recent_data['Close'] - recent_data['Low']) / daily_range.replace(0, np.nan)
            close_position = close_position.fillna(0.5)  # Neutral when no range
            
            # Volume-weighted average
            volume_weights = recent_data['Volume'] / recent_data['Volume'].sum()
            weighted_close_position = (close_position * volume_weights).sum()
            
            # Convert to accumulation/distribution score
            return (weighted_close_position - 0.5) * 2  # Scale to [-1, 1]
            
        except Exception as e:
            logger.warning(f"Close range volume error: {e}")
            return 0.0
    
    def _calculate_absorption_score(self, df: pd.DataFrame, window: int = 5) -> float:
        """Detect large range with small net price change (absorption)"""
        try:
            recent_data = df.tail(window)
            
            # Average true range
            high_low = recent_data['High'] - recent_data['Low']
            avg_range = high_low.mean()
            
            # Net price change
            net_change = abs(recent_data['Close'].iloc[-1] - recent_data['Close'].iloc[0])
            
            # Volume above average
            avg_volume = df['Volume'].rolling(window=20).mean().tail(window).mean()
            current_volume = recent_data['Volume'].mean()
            
            # Absorption: high range, low net change, high volume
            if avg_range > 0 and current_volume > avg_volume * 1.2:
                absorption = 1 - (net_change / avg_range)
                return max(0, min(absorption, 1.0))
            
            return 0.0
            
        except Exception as e:
            logger.warning(f"Absorption score error: {e}")
            return 0.0
    
    # Dark pool proxy methods
    def _calculate_block_trade_clustering(self, df: pd.DataFrame, window: int = 10) -> float:
        """Detect clustering in volume patterns (block trades)"""
        try:
            recent_volumes = df['Volume'].tail(window)
            
            # Calculate volume variance relative to mean
            volume_mean = recent_volumes.mean()
            volume_std = recent_volumes.std()
            
            if volume_mean > 0 and volume_std > 0:
                coefficient_of_variation = volume_std / volume_mean
                
                # High CV suggests irregular block trades
                # Normalize to [0, 1] range
                clustering_score = min(coefficient_of_variation / 2.0, 1.0)
                return clustering_score
            
            return 0.0
            
        except Exception as e:
            logger.warning(f"Block trade clustering error: {e}")
            return 0.0
    
    def _calculate_consolidation_volume_anomaly(self, df: pd.DataFrame, window: int = 10) -> float:
        """Detect volume anomalies during price consolidation"""
        try:
            recent_data = df.tail(window)
            
            # Price consolidation: low volatility
            price_volatility = recent_data['Close'].std() / recent_data['Close'].mean()
            
            # Volume anomaly: high volume relative to average
            avg_volume = df['Volume'].rolling(window=20).mean().tail(window).mean()
            current_volume = recent_data['Volume'].mean()
            
            # Anomaly when low price volatility but high volume
            if price_volatility < 0.02 and current_volume > avg_volume * 1.5:
                anomaly_score = min((current_volume / avg_volume - 1.0) / 2.0, 1.0)
                return anomaly_score
            
            return 0.0
            
        except Exception as e:
            logger.warning(f"Consolidation volume anomaly error: {e}")
            return 0.0
    
    def _calculate_auction_imbalance(self, df: pd.DataFrame) -> float:
        """Detect imbalance in opening/closing auction patterns"""
        try:
            if len(df) < 2:
                return 0.0
            
            # Simple proxy: gap vs daily range
            yesterday_close = df['Close'].iloc[-2]
            today_open = df['Open'].iloc[-1]
            today_range = df['High'].iloc[-1] - df['Low'].iloc[-1]
            
            gap = abs(today_open - yesterday_close)
            
            if today_range > 0:
                gap_ratio = gap / today_range
                return min(gap_ratio, 1.0)
            
            return 0.0
            
        except Exception as e:
            logger.warning(f"Auction imbalance error: {e}")
            return 0.0
    
    # Helper methods
    def _calculate_divergence_age(self, df: pd.DataFrame, bull_strength: float, bear_strength: float) -> float:
        """Calculate age of most recent divergence signal"""
        try:
            max_strength = max(bull_strength, bear_strength)
            if max_strength > 0:
                # Simple proxy: return normalized age (0 = recent, 1 = old)
                return min(len(df) / 100.0, 1.0)  # Assume max 100 bars for full aging
            return 0.0
            
        except Exception as e:
            logger.warning(f"Divergence age error: {e}")
            return 0.0
    
    def _get_empty_features(self) -> Dict[str, float]:
        """Return empty feature set when calculation fails"""
        return {
            # RSI Divergence
            'rsi_div_bull': 0.0,
            'rsi_div_bear': 0.0,
            'rsi_div_strength': 0.0,
            'rsi_div_age': 0.0,
            # Price-Volume Divergence
            'obv_price_div': 0.0,
            'vpt_price_div': 0.0,
            'mfi_div': 0.0,
            'vol_confirm_score': 0.0,
            'dry_up_score': 0.0,
            # Institutional Flow
            'adl_trend_div': 0.0,
            'vwap_persist_score': 0.0,
            'close_range_volume_score': 0.0,
            'absorption_score': 0.0,
            # Dark Pool Proxies
            'block_trade_proxy': 0.0,
            'consolidation_volume_anomaly': 0.0,
            'auction_imbalance_proxy': 0.0,
            'dark_pool_proxy_score': 0.0,
            # Composite
            'contrarian_composite_score': 0.0
        }

# Convenience function for external use
def compute_contrarian_features(df: pd.DataFrame) -> Dict[str, float]:
    """
    Convenience function to compute contrarian features
    
    Args:
        df: OHLCV DataFrame with columns ['Open', 'High', 'Low', 'Close', 'Volume']
        
    Returns:
        Dictionary of contrarian features
    """
    engine = ContrarianSignalEngine()
    return engine.compute_contrarian_features(df)

def compute_contrarian_score(features: Dict[str, float]) -> float:
    """
    Convenience function to compute composite contrarian score
    
    Args:
        features: Dictionary of contrarian features
        
    Returns:
        Composite contrarian score [-1, 1]
    """
    engine = ContrarianSignalEngine()
    return engine._compute_composite_score(features)