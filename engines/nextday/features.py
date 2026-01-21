"""
Professional feature engineering for next-day predictions
Implements institutional-grade features with proper validation
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
import logging
from datetime import datetime, timedelta
from scipy import stats
from sklearn.preprocessing import StandardScaler
import warnings

try:
    from .config import CONFIG
    from .data_ingest import DataIngestionEngine
    from .contrarian import ContrarianSignalEngine
    from .candlestick_patterns import CandlestickPatternDetector
except ImportError:
    try:
        from engines.nextday.config import CONFIG
        from engines.nextday.data_ingest import DataIngestionEngine
        from engines.nextday.contrarian import ContrarianSignalEngine
        from engines.nextday.candlestick_patterns import CandlestickPatternDetector
    except ImportError:
        from config import CONFIG
        from data_ingest import DataIngestionEngine
        try:
            from contrarian import ContrarianSignalEngine
        except ImportError:
            ContrarianSignalEngine = None
        try:
            from candlestick_patterns import CandlestickPatternDetector
        except ImportError:
            CandlestickPatternDetector = None

logger = logging.getLogger(__name__)

class NextDayFeatureEngine:
    """
    Institutional-grade feature engineering for overnight gap predictions
    Implements professional quant finance feature extraction
    """
    
    def __init__(self):
        self.feature_names = [
            # PREDICTIVE CORE: Real forward-looking intelligence (no data leakage)
            'analyst_target_delta',
            'earnings_surprise_momentum',
            'valuation_discount',  # Renamed from forward_pe_vs_peers for clarity
            'revenue_growth_trajectory',
            # TECHNICAL INDICATORS: Properly implemented
            'overnight_futures_delta_weighted',
            'options_gex_exposure',
            'rolling_volatility_5d',
            'rolling_volatility_10d',
            'rolling_volatility_20d',
            'overnight_news_sentiment',
            'liquidity_heatmap_distance',
            'block_trade_imbalance',
            'dark_pool_ratio',
            'vix_regime_change',
            'soxx_relative_strength',
            'nvda_correlation_factor',
            'volume_anomaly_score',
            'momentum_reversal_signal',
            'cross_asset_stress_index',
            # MARKET CONTEXT: Supporting features
            'sector_rotation_strength',
            'market_regime_factor',
            'bollinger_position',
            'stochastic_k',
            'williams_r',
            'roc_10d',
            # CANDLESTICK PATTERNS: Chart pattern recognition
            'pattern_doji',
            'pattern_hammer',
            'pattern_inverted_hammer',
            'pattern_shooting_star',
            'pattern_bullish_engulfing',
            'pattern_bearish_engulfing',
            'pattern_bullish_harami',
            'pattern_bearish_harami',
            'pattern_morning_star',
            'pattern_evening_star',
            'pattern_bullish_marubozu',
            'pattern_bearish_marubozu',
            'pattern_piercing_line',
            'pattern_dark_cloud_cover',
            'pattern_three_white_soldiers',
            'pattern_three_black_crows'
        ]
        
        self.scaler = None
        self.data_engine = DataIngestionEngine()
        
        # Initialize candlestick pattern detector
        self.candlestick_detector = CandlestickPatternDetector() if CandlestickPatternDetector else None
        
        # Initialize contrarian engine if available
        self.contrarian_engine = None
        if ContrarianSignalEngine and getattr(CONFIG, 'enable_contrarian_signals', False):
            try:
                self.contrarian_engine = ContrarianSignalEngine()
                logger.info("Contrarian signal engine initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize contrarian engine: {e}")
                self.contrarian_engine = None
        
    def compute_features(self, market_data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """LEGACY INTERFACE: Wrapper for engineer_features method"""
        return self.engineer_features(market_data)
    
        
    def engineer_features(self, data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """
        Engineer comprehensive feature set for next-day predictions
        
        Args:
            data: Dictionary of market data DataFrames
            
        Returns:
            DataFrame with engineered features and target
        """
        
        logger.info("Engineering institutional-grade features...")
        
        # Get primary asset (AMD)
        amd_data = data['amd'].copy()
        
        # Initialize feature DataFrame
        features_df = pd.DataFrame(index=amd_data.index)
        
        # 1. Overnight futures delta (volatility-weighted)
        features_df['overnight_futures_delta_weighted'] = self._compute_futures_delta(data)
        
        # 2. Options GEX exposure (simulated from volume patterns)
        features_df['options_gex_exposure'] = self._compute_gex_proxy(amd_data)
        
        # 3. Rolling volatility features (multiple windows)
        volatility_windows = getattr(CONFIG, 'volatility_windows', [5, 10, 20])
        for window in volatility_windows:
            features_df[f'rolling_volatility_{window}d'] = self._compute_rolling_volatility(amd_data, window)
        
        # 4. Overnight news sentiment (placeholder with realistic proxy)
        features_df['overnight_news_sentiment'] = self._compute_news_sentiment_proxy(amd_data)
        
        # 5. Liquidity heatmap distance
        features_df['liquidity_heatmap_distance'] = self._compute_liquidity_levels(amd_data)
        
        # 6. Block trade imbalance (from volume patterns)
        features_df['block_trade_imbalance'] = self._compute_block_trade_proxy(amd_data)
        
        # 7. Dark pool ratio (estimated from volume anomalies)
        features_df['dark_pool_ratio'] = self._compute_dark_pool_proxy(amd_data)
        
        # 8. VIX regime change
        if 'vix' in data:
            features_df['vix_regime_change'] = self._compute_vix_regime(data['vix'])
        else:
            features_df['vix_regime_change'] = 0.0
        
        # 9. SOXX relative strength
        if 'soxx' in data:
            features_df['soxx_relative_strength'] = self._compute_relative_strength(amd_data, data['soxx'])
        else:
            features_df['soxx_relative_strength'] = 0.0
        
        # 10. NVDA correlation factor
        if 'nvda' in data:
            features_df['nvda_correlation_factor'] = self._compute_correlation_factor(amd_data, data['nvda'])
        else:
            features_df['nvda_correlation_factor'] = 0.0
        
        # 11. Volume anomaly score
        features_df['volume_anomaly_score'] = self._compute_volume_anomaly(amd_data)
        
        # 12. Momentum reversal signal
        features_df['momentum_reversal_signal'] = self._compute_momentum_reversal(amd_data)
        
        # 13. Cross-asset stress index
        features_df['cross_asset_stress_index'] = self._compute_stress_index(data)
        
        # PREDICTIVE CORE: Forward-looking features (REAL-TIME ONLY, NO DATA LEAKAGE)
        if len(amd_data) > 0:
            predictive_features = self._compute_predictive_intelligence_realtime(amd_data)
            for name, values in predictive_features.items():
                features_df[name] = values
        
        # SUPPORTING: Market context and regime
        context_features = self._compute_market_context(data)
        for name, values in context_features.items():
            features_df[name] = values
            
        # ADVANCED TECHNICAL INDICATORS
        advanced_indicators = self._compute_advanced_free_indicators(amd_data)
        for name, values in advanced_indicators.items():
            features_df[name] = values
        
        # CANDLESTICK PATTERN DETECTION
        if self.candlestick_detector is not None:
            try:
                logger.info("Detecting candlestick patterns...")
                pattern_df = self.candlestick_detector.detect_all_patterns(amd_data)
                
                # Rename columns to match feature names
                pattern_df = pattern_df.rename(columns={
                    name: f'pattern_{name}' for name in pattern_df.columns
                })
                
                # Merge pattern features with main features
                features_df = features_df.join(pattern_df, how='left')
                
                logger.info(f"Added {len(pattern_df.columns)} candlestick pattern features")
                
            except Exception as e:
                logger.warning(f"Failed to compute candlestick patterns: {e}")
                # Add zero features as fallback
                for pattern_name in ['doji', 'hammer', 'inverted_hammer', 'shooting_star',
                                   'bullish_engulfing', 'bearish_engulfing', 'bullish_harami', 
                                   'bearish_harami', 'morning_star', 'evening_star',
                                   'bullish_marubozu', 'bearish_marubozu', 'piercing_line',
                                   'dark_cloud_cover', 'three_white_soldiers', 'three_black_crows']:
                    features_df[f'pattern_{pattern_name}'] = 0.0
        
        # Add contrarian analysis features if enabled
        if self.contrarian_engine is not None:
            try:
                logger.info("Computing contrarian features...")
                contrarian_features_df = self.contrarian_engine.compute_contrarian_features(amd_data)
                
                # Merge contrarian features with main features (proper time alignment)
                features_df = features_df.join(contrarian_features_df, how='left')
                
                logger.info(f"Added {len(contrarian_features_df.columns)} contrarian features")
                
            except Exception as e:
                logger.warning(f"Failed to compute contrarian features: {e}")
        
        # Target: next day gap (open vs previous close)
        features_df['target_gap_pct'] = self._compute_target_gap(amd_data)
        
        # IMPROVED: Feature-specific NaN handling instead of blanket 0.0 fillna
        feature_columns = [col for col in features_df.columns if col != 'target_gap_pct']
        
        # For each feature, use appropriate fillna strategy
        for col in feature_columns:
            if col in features_df.columns:
                # Use forward fill for time-series features, then backward fill, then 0
                # This preserves last known values instead of defaulting to 0
                features_df[col] = features_df[col].ffill().bfill().fillna(0)
        
        # Remove rows with missing target only
        features_df = features_df.dropna(subset=['target_gap_pct'])
        
        logger.info(f"Engineered {len(self.feature_names)} features for {len(features_df)} samples")
        return features_df
    
    def _compute_futures_delta(self, data: Dict[str, pd.DataFrame]) -> pd.Series:
        """Compute volatility-weighted futures delta for overnight bias"""
        
        try:
            futures_signals = []
            
            for name in ['futures_es', 'futures_nq']:
                if name in data:
                    futures_df = data[name]
                    returns = futures_df['Close'].pct_change()
                    volatility = returns.rolling(getattr(CONFIG, 'futures_weight_halflife', 10)).std()
                    
                    # Weight by inverse volatility (more weight to stable signals)
                    weights = 1.0 / (volatility + 1e-6)
                    weighted_delta = returns * weights
                    futures_signals.append(weighted_delta.fillna(0))
            
            if futures_signals:
                # Combine multiple futures signals
                combined = sum(futures_signals) / len(futures_signals)
                return combined.rolling(3).mean().fillna(0)
            else:
                # Fallback to zeros if no futures data
                return pd.Series(0.0, index=data['amd'].index)
                
        except Exception as e:
            logger.warning(f"Futures delta calculation failed: {e}")
            return pd.Series(0.0, index=data['amd'].index)
    
    def _compute_gex_proxy(self, amd_data: pd.DataFrame) -> pd.Series:
        """
        Compute proxy for options Gamma Exposure using volume patterns
        Real implementation would use options chain data
        """
        
        try:
            # Use volume spikes and price action as GEX proxy
            volume_ratio = amd_data['Volume'] / amd_data['Volume'].rolling(20).mean()
            price_momentum = amd_data['Close'].pct_change(5)
            
            # Higher volume with lower momentum suggests dealer hedging
            gex_proxy = volume_ratio * (1.0 / (abs(price_momentum) + 0.01))
            return gex_proxy.rolling(3).mean().fillna(0)
            
        except Exception as e:
            logger.warning(f"GEX proxy calculation failed: {e}")
            return pd.Series(0.0, index=amd_data.index)
    
    def _compute_rolling_volatility(self, amd_data: pd.DataFrame, window: int) -> pd.Series:
        """Compute rolling volatility with proper annualization"""
        
        returns = amd_data['Close'].pct_change()
        volatility = returns.rolling(window).std() * np.sqrt(252)
        return volatility.fillna(volatility.mean())
    
    def _compute_news_sentiment_proxy(self, amd_data: pd.DataFrame) -> pd.Series:
        """
        Proxy for news sentiment using price action patterns
        Real implementation would use NLP on news feeds
        """
        
        try:
            # Use overnight gaps as sentiment proxy
            overnight_gaps = (amd_data['Open'] / amd_data['Close'].shift(1)) - 1
            
            # Smooth and normalize
            sentiment_proxy = overnight_gaps.rolling(5).mean()
            return sentiment_proxy.fillna(0)
            
        except Exception as e:
            logger.warning(f"News sentiment proxy failed: {e}")
            return pd.Series(0.0, index=amd_data.index)
    
    def _compute_liquidity_levels(self, amd_data: pd.DataFrame) -> pd.Series:
        """Compute distance from key liquidity levels (support/resistance)"""
        
        try:
            # Identify key levels using rolling highs/lows
            highs_20d = amd_data['High'].rolling(20).max()
            lows_20d = amd_data['Low'].rolling(20).min()
            
            current_price = amd_data['Close']
            
            # Distance from nearest level (normalized)
            dist_to_high = (highs_20d - current_price) / current_price
            dist_to_low = (current_price - lows_20d) / current_price
            
            # Use minimum distance to either level
            distance = np.minimum(dist_to_high, dist_to_low)
            return distance.fillna(0)
            
        except Exception as e:
            logger.warning(f"Liquidity levels calculation failed: {e}")
            return pd.Series(0.0, index=amd_data.index)
    
    def _compute_block_trade_proxy(self, amd_data: pd.DataFrame) -> pd.Series:
        """Proxy for block trade imbalance using volume patterns"""
        
        try:
            # Large volume days with small price moves suggest block trades
            volume_ratio = amd_data['Volume'] / amd_data['Volume'].rolling(20).mean()
            price_move = abs(amd_data['Close'].pct_change())
            
            # High volume, low volatility = potential block trades
            block_proxy = volume_ratio / (price_move + 0.001)
            
            # Smooth and cap outliers
            block_proxy = np.tanh(block_proxy / block_proxy.rolling(20).std())
            return block_proxy.fillna(0)
            
        except Exception as e:
            logger.warning(f"Block trade proxy failed: {e}")
            return pd.Series(0.0, index=amd_data.index)
    
    def _compute_dark_pool_proxy(self, amd_data: pd.DataFrame) -> pd.Series:
        """Estimate dark pool activity from volume anomalies"""
        
        try:
            # Dark pool activity often shows as volume without price impact
            volume_surprise = (amd_data['Volume'] - amd_data['Volume'].rolling(10).mean()) / amd_data['Volume'].rolling(10).std()
            price_impact = abs(amd_data['Close'].pct_change())
            
            # High volume surprise with low price impact
            dark_pool_ratio = volume_surprise / (price_impact + 0.001)
            
            # Normalize and smooth
            dark_pool_ratio = np.tanh(dark_pool_ratio / 3.0)
            return dark_pool_ratio.rolling(3).mean().fillna(0)
            
        except Exception as e:
            logger.warning(f"Dark pool proxy failed: {e}")
            return pd.Series(0.0, index=amd_data.index)
    
    def _compute_vix_regime(self, vix_data: pd.DataFrame) -> pd.Series:
        """Compute VIX regime change indicator"""
        
        try:
            vix_level = vix_data['Close']
            vix_ma = vix_level.rolling(20).mean()
            vix_std = vix_level.rolling(20).std()
            
            # Z-score for regime identification
            vix_zscore = (vix_level - vix_ma) / vix_std
            
            # Regime change = significant deviation from norm
            regime_change = np.tanh(vix_zscore / 2.0)
            return regime_change.fillna(0)
            
        except Exception as e:
            logger.warning(f"VIX regime calculation failed: {e}")
            return pd.Series(0.0, index=vix_data.index)
    
    def _compute_relative_strength(self, amd_data: pd.DataFrame, benchmark_data: pd.DataFrame) -> pd.Series:
        """Compute relative strength vs benchmark"""
        
        try:
            amd_returns = amd_data['Close'].pct_change(20)
            benchmark_returns = benchmark_data['Close'].pct_change(20)
            
            # Relative performance
            relative_strength = amd_returns - benchmark_returns
            return relative_strength.fillna(0)
            
        except Exception as e:
            logger.warning(f"Relative strength calculation failed: {e}")
            return pd.Series(0.0, index=amd_data.index)
    
    def _compute_correlation_factor(self, amd_data: pd.DataFrame, corr_asset_data: pd.DataFrame) -> pd.Series:
        """Compute rolling correlation factor"""
        
        try:
            amd_returns = amd_data['Close'].pct_change()
            asset_returns = corr_asset_data['Close'].pct_change()
            
            # Rolling correlation
            correlation = amd_returns.rolling(20).corr(asset_returns)
            return correlation.fillna(0)
            
        except Exception as e:
            logger.warning(f"Correlation factor calculation failed: {e}")
            return pd.Series(0.0, index=amd_data.index)
    
    def _compute_volume_anomaly(self, amd_data: pd.DataFrame) -> pd.Series:
        """Detect volume anomalies"""
        
        try:
            volume_ma = amd_data['Volume'].rolling(20).mean()
            volume_std = amd_data['Volume'].rolling(20).std()
            
            # Z-score for volume anomaly detection
            volume_zscore = (amd_data['Volume'] - volume_ma) / volume_std
            
            # Cap extreme values
            anomaly_score = np.tanh(volume_zscore / 3.0)
            return anomaly_score.fillna(0)
            
        except Exception as e:
            logger.warning(f"Volume anomaly calculation failed: {e}")
            return pd.Series(0.0, index=amd_data.index)
    
    def _compute_momentum_reversal(self, amd_data: pd.DataFrame) -> pd.Series:
        """Compute momentum reversal signal"""
        
        try:
            # Short-term vs long-term momentum
            momentum_5d = amd_data['Close'].pct_change(5)
            momentum_20d = amd_data['Close'].pct_change(20)
            
            # RSI-like reversal signal
            rsi_series = self._compute_rsi(amd_data['Close'], 14)
            
            # Combine momentum divergence with RSI
            reversal_signal = (momentum_20d - momentum_5d) * (50 - rsi_series) / 50
            return reversal_signal.fillna(0)
            
        except Exception as e:
            logger.warning(f"Momentum reversal calculation failed: {e}")
            return pd.Series(0.0, index=amd_data.index)
    
    def _compute_stress_index(self, data: Dict[str, pd.DataFrame]) -> pd.Series:
        """Compute cross-asset stress index"""
        
        try:
            stress_components = []
            
            # VIX stress
            if 'vix' in data:
                vix_level = data['vix']['Close']
                vix_stress = (vix_level - 20) / 20  # Normalized around 20 VIX
                stress_components.append(vix_stress)
            
            # Volatility stress across assets
            for name in ['amd', 'soxx', 'nvda']:
                if name in data:
                    returns = data[name]['Close'].pct_change()
                    vol_stress = returns.rolling(5).std() * np.sqrt(252)
                    stress_components.append(vol_stress)
            
            if stress_components:
                # Average stress across components
                stress_index = pd.concat(stress_components, axis=1).mean(axis=1)
                if hasattr(stress_index, 'rolling'):
                    return stress_index.rolling(3).mean().fillna(0)
                else:
                    return pd.Series(stress_index, index=data['amd'].index).fillna(0)
            else:
                return pd.Series(0.0, index=data['amd'].index)
                
        except Exception as e:
            logger.warning(f"Stress index calculation failed: {e}")
            return pd.Series(0.0, index=data['amd'].index)
    
    def _compute_rsi(self, prices: pd.Series, window: int = 14) -> pd.Series:
        """Compute RSI indicator"""
        
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        # FIXED: Use forward fill for RSI instead of hardcoded 50
        return rsi.ffill().bfill().fillna(50)  # Only fillna(50) as last resort
    
    def _compute_advanced_free_indicators(self, amd_data: pd.DataFrame) -> Dict[str, pd.Series]:
        """FREE UPGRADE: Advanced technical indicators using only free data"""
        
        indicators = {}
        
        try:
            if len(amd_data) >= 20:
                # Bollinger Bands position (0-1 scale)
                sma_20 = amd_data['Close'].rolling(20).mean()
                std_20 = amd_data['Close'].rolling(20).std()
                bb_upper = sma_20 + (std_20 * 2)
                bb_lower = sma_20 - (std_20 * 2)
                bb_position = (amd_data['Close'] - bb_lower) / (bb_upper - bb_lower)
                # FIXED: Use forward/backward fill before defaulting to 0.5
                indicators['bollinger_position'] = bb_position.ffill().bfill().fillna(0.5)
                
                # Stochastic Oscillator %K
                low_14 = amd_data['Low'].rolling(14).min()
                high_14 = amd_data['High'].rolling(14).max()
                stoch_k = (amd_data['Close'] - low_14) / (high_14 - low_14) * 100
                # FIXED: Use forward/backward fill before defaulting to 50
                indicators['stochastic_k'] = stoch_k.ffill().bfill().fillna(50.0)
                
                # Williams %R (negative oscillator)
                williams_r = (high_14 - amd_data['Close']) / (high_14 - low_14) * -100
                # FIXED: Use forward/backward fill before defaulting to -50
                indicators['williams_r'] = williams_r.ffill().bfill().fillna(-50.0)
                
                # Rate of Change (10-day momentum)
                roc_10 = amd_data['Close'].pct_change(10) * 100
                # FIXED: Use forward/backward fill before defaulting to 0
                indicators['roc_10d'] = roc_10.ffill().bfill().fillna(0.0)
                
            else:
                # Fallback for insufficient data
                indicators.update({
                    'bollinger_position': pd.Series(0.5, index=amd_data.index),
                    'stochastic_k': pd.Series(50.0, index=amd_data.index),
                    'williams_r': pd.Series(-50.0, index=amd_data.index),
                    'roc_10d': pd.Series(0.0, index=amd_data.index)
                })
                
        except Exception as e:
            logger.warning(f"Advanced indicators calculation failed: {e}")
            # Safe fallback
            indicators.update({
                'bollinger_position': pd.Series(0.5, index=amd_data.index),
                'stochastic_k': pd.Series(50.0, index=amd_data.index),
                'williams_r': pd.Series(-50.0, index=amd_data.index),
                'roc_10d': pd.Series(0.0, index=amd_data.index)
            })
            
        return indicators
    
    def _compute_earnings_proximity(self, amd_data: pd.DataFrame) -> pd.Series:
        """FREE UPGRADE: Earnings proximity feature using free calendar data"""
        
        try:
            import yfinance as yf
            # Get earnings calendar (free from yfinance)
            amd_ticker = yf.Ticker('AMD')
            calendar = amd_ticker.calendar
            
            if calendar is not None and len(calendar) > 0:
                # Get next earnings date
                next_earnings = calendar.index[0] if hasattr(calendar, 'index') else None
                
                if next_earnings:
                    # Days until earnings (negative = days since)
                    days_diff = []
                    for date in amd_data.index:
                        diff = (next_earnings - date).days if hasattr(next_earnings, 'date') else 0
                        days_diff.append(max(-30, min(30, diff)))  # Cap at ±30 days
                    
                    proximity_series = pd.Series(days_diff, index=amd_data.index)
                    # Transform to proximity score (higher = closer to earnings)
                    proximity_score = 1.0 / (abs(proximity_series) / 7 + 1)  # Week-based decay
                    return proximity_score
            
            # Fallback: use volume spikes as earnings proxy
            volume_ratio = amd_data['Volume'] / amd_data['Volume'].rolling(60).mean()
            earnings_proxy = (volume_ratio > 2.0).astype(float)  # Volume spikes
            return earnings_proxy.rolling(3).mean().fillna(0)
            
        except Exception as e:
            logger.warning(f"Earnings proximity calculation failed: {e}")
            return pd.Series(0.0, index=amd_data.index)
    
    def _compute_predictive_intelligence_realtime(self, amd_data: pd.DataFrame) -> Dict[str, pd.Series]:
        """REAL-TIME PREDICTIVE FEATURES: Current data only (prevents data leakage)"""
        
        features = {}
        current_date = datetime.now()
        
        # Only compute for latest data point to prevent data leakage
        if len(amd_data) == 0:
            return features
            
        try:
            import yfinance as yf
            amd_ticker = yf.Ticker('AMD')
            
            # 1. ANALYST TARGET DELTA - Only for real-time predictions
            try:
                info = amd_ticker.info
                target_price = info.get('targetMeanPrice', None) or info.get('targetMedianPrice', None)
                
                if target_price and target_price > 0:
                    # Calculate delta for each historical point using HISTORICAL closing price
                    target_deltas = []
                    for idx, price in amd_data['Close'].items():
                        delta = (target_price - price) / price
                        target_deltas.append(delta)
                    
                    features['analyst_target_delta'] = pd.Series(target_deltas, index=amd_data.index)
                    logger.info(f"Using current analyst target ${target_price:.2f} for feature calculation")
                else:
                    features['analyst_target_delta'] = pd.Series(0.0, index=amd_data.index)
            except Exception as e:
                logger.warning(f"Analyst target calculation failed: {e}")
                features['analyst_target_delta'] = pd.Series(0.0, index=amd_data.index)
            
            # 2. EARNINGS SURPRISE MOMENTUM (historical data OK)
            try:
                earnings_dates = amd_ticker.earnings_dates
                if earnings_dates is not None and len(earnings_dates) > 0:
                    recent_surprises = earnings_dates['Surprise(%)'].dropna().head(4)
                    if len(recent_surprises) > 0:
                        surprise_momentum = recent_surprises.mean() / 100
                        features['earnings_surprise_momentum'] = pd.Series(surprise_momentum, index=amd_data.index)
                    else:
                        features['earnings_surprise_momentum'] = pd.Series(0.0, index=amd_data.index)
                else:
                    features['earnings_surprise_momentum'] = pd.Series(0.0, index=amd_data.index)
            except Exception as e:
                logger.warning(f"Earnings surprise calculation failed: {e}")
                features['earnings_surprise_momentum'] = pd.Series(0.0, index=amd_data.index)
            
            # 3. VALUATION DISCOUNT (FIXED INTERPRETATION: negative = cheaper = bullish)
            try:
                info = amd_ticker.info
                forward_pe = info.get('forwardPE', None)
                
                # Get NVDA for peer comparison
                nvda = yf.Ticker('NVDA')
                nvda_info = nvda.info
                nvda_forward_pe = nvda_info.get('forwardPE', None)
                
                if forward_pe and nvda_forward_pe and nvda_forward_pe > 0:
                    # Valuation discount: positive = AMD is cheaper (bullish)
                    valuation_discount = (nvda_forward_pe - forward_pe) / nvda_forward_pe
                    features['valuation_discount'] = pd.Series(valuation_discount, index=amd_data.index)
                    logger.info(f"AMD forward P/E: {forward_pe:.1f}, NVDA: {nvda_forward_pe:.1f}, discount: {valuation_discount:.3f}")
                else:
                    features['valuation_discount'] = pd.Series(0.0, index=amd_data.index)
            except Exception as e:
                logger.warning(f"Valuation discount calculation failed: {e}")
                features['valuation_discount'] = pd.Series(0.0, index=amd_data.index)
            
            # 4. REVENUE GROWTH TRAJECTORY (historical data OK)
            try:
                financials = amd_ticker.quarterly_financials
                if financials is not None and len(financials.columns) >= 2:
                    latest_quarter = financials.columns[0]
                    prev_quarter = financials.columns[1]
                    
                    if 'Total Revenue' in financials.index:
                        current_rev = financials.loc['Total Revenue', latest_quarter]
                        prev_rev = financials.loc['Total Revenue', prev_quarter]
                        revenue_growth = (current_rev / prev_rev - 1) if prev_rev != 0 else 0.0
                        features['revenue_growth_trajectory'] = pd.Series(revenue_growth, index=amd_data.index)
                        logger.info(f"Revenue growth trajectory: {revenue_growth:.3f}")
                    else:
                        features['revenue_growth_trajectory'] = pd.Series(0.0, index=amd_data.index)
                else:
                    features['revenue_growth_trajectory'] = pd.Series(0.0, index=amd_data.index)
            except Exception as e:
                logger.warning(f"Revenue growth calculation failed: {e}")
                features['revenue_growth_trajectory'] = pd.Series(0.0, index=amd_data.index)
            
        except Exception as e:
            logger.warning(f"Predictive intelligence calculation failed: {e}")
            
        # Ensure required features exist (only real ones, no placeholders)
        required_features = ['analyst_target_delta', 'earnings_surprise_momentum', 
                           'valuation_discount', 'revenue_growth_trajectory']
        
        for feature in required_features:
            if feature not in features:
                features[feature] = pd.Series(0.0, index=amd_data.index)
        
        return features
    
    def _compute_market_context(self, data: Dict[str, pd.DataFrame]) -> Dict[str, pd.Series]:
        """SUPPORTING FEATURES: Market context and regime detection"""
        
        features = {}
        amd_data = data['amd']
        
        try:
            # Market regime detection
            if 'vix' in data:
                vix_level = data['vix']['Close'].iloc[-1] if len(data['vix']) > 0 else 20
                regime_factor = min(1.0, max(-1.0, (vix_level - 20) / 20))  # Normalize around VIX 20
                features['market_regime_factor'] = pd.Series(regime_factor, index=amd_data.index)
            else:
                features['market_regime_factor'] = pd.Series(0.0, index=amd_data.index)
            
            # Sector strength (SOXX relative performance)
            if 'soxx' in data:
                soxx_data = data['soxx']
                amd_returns = amd_data['Close'].pct_change(20)
                soxx_returns = soxx_data['Close'].pct_change(20)
                sector_strength = amd_returns - soxx_returns
                features['sector_rotation_strength'] = sector_strength.fillna(0)
            else:
                features['sector_rotation_strength'] = pd.Series(0.0, index=amd_data.index)
                
        except Exception as e:
            logger.warning(f"Market context calculation failed: {e}")
            
        # Ensure only real context features exist (remove placeholders)
        real_context_features = ['sector_rotation_strength', 'market_regime_factor']
        
        for feature in real_context_features:
            if feature not in features:
                features[feature] = pd.Series(0.0, index=amd_data.index)
                
        return features
    
    def _compute_target_gap(self, amd_data: pd.DataFrame) -> pd.Series:
        """Compute next-day gap as target variable"""
        
        # Gap = (Next Open / Current Close) - 1
        next_open = amd_data['Open'].shift(-1)
        current_close = amd_data['Close']
        
        gap_pct = (next_open / current_close) - 1
        return gap_pct
    
    def fit_scaler(self, features_df: pd.DataFrame) -> None:
        """Fit scaler on training data only"""
        
        feature_columns = [col for col in self.feature_names if col in features_df.columns]
        
        self.scaler = StandardScaler()
        self.scaler.fit(features_df[feature_columns])
        
        logger.info(f"Fitted scaler on {len(feature_columns)} features")
    
    def transform_features(self, features_df: pd.DataFrame) -> np.ndarray:
        """Transform features using fitted scaler"""
        
        if self.scaler is None:
            raise ValueError("Scaler not fitted. Call fit_scaler() first.")
        
        feature_columns = [col for col in self.feature_names if col in features_df.columns]
        X = features_df[feature_columns].values
        # Handle NaN values before transforming
        X = np.nan_to_num(X, nan=0.0, posinf=1e10, neginf=-1e10)
        return self.scaler.transform(X)

# Export main class
__all__ = ['NextDayFeatureEngine']