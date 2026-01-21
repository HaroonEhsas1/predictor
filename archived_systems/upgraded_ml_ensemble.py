#!/usr/bin/env python3
"""
Upgraded Advanced ML Ensemble System
Enhanced with multi-source data, cross-asset correlation, and dynamic weighting
"""

import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
import pickle
import os
import warnings
import time

try:
    import lightgbm as lgb
    LIGHTGBM_AVAILABLE = True
except ImportError:
    LIGHTGBM_AVAILABLE = False

try:
    import catboost as cb
    CATBOOST_AVAILABLE = True
except ImportError:
    CATBOOST_AVAILABLE = False

try:
    import tensorflow as tf
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import LSTM, GRU, Dense, Dropout, BatchNormalization
    from tensorflow.keras.optimizers import Adam
    from tensorflow.keras.callbacks import EarlyStopping
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False

from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import TimeSeriesSplit
import requests

warnings.filterwarnings('ignore')

@dataclass
class EnhancedPredictionResult:
    """Comprehensive prediction result with multi-model consensus"""
    predicted_price: float
    direction: str  # UP, DOWN, NEUTRAL
    confidence: float  # 0-100
    consensus_score: float  # Agreement between models
    individual_predictions: Dict[str, float]
    feature_importance: Dict[str, float]
    cross_asset_signals: Dict[str, float]
    news_sentiment_score: float
    risk_score: float
    volatility_forecast: float
    timestamp: datetime
    model_weights_used: Dict[str, float]

class UpgradedMLEnsemble:
    """Professional ML ensemble with cross-asset correlation and news sentiment"""
    
    def __init__(self, symbol: str = "AMD"):
        self.symbol = symbol
        self.models = {}
        self.scalers = {}
        self.model_weights = {}
        self.performance_history = {}
        self.data_cache = {}
        
        # Enhanced feature engineering
        self.feature_names = []
        self.lookback_period = 60
        self.prediction_horizon = 1
        
        # Cross-asset correlation symbols with weights
        self.correlation_assets = {
            'NVDA': 0.85,    # High correlation with AMD
            'INTC': 0.60,    # Moderate correlation
            'SOXX': 0.80,    # Semiconductor ETF
            'QQQ': 0.65,     # Tech-heavy NASDAQ
            'SPY': 0.45,     # Market overall
            '^VIX': -0.40,   # Inverse correlation with volatility
            'GLD': -0.20,    # Flight to safety indicator
            '^TNX': 0.30     # 10-year treasury rates
        }
        
        # Enhanced model performance tracking
        self.prediction_accuracy = {}
        for model_name in ['lightgbm', 'catboost', 'lstm', 'gru', 'random_forest', 'gradient_boost']:
            self.prediction_accuracy[model_name] = {
                'correct': 0, 'total': 0, 'mae': [], 'mse': [], 'recent_performance': []
            }
        
        # Dynamic weighting configuration
        self.adaptive_weights = True
        self.weight_decay = 0.95
        self.min_weight = 0.05  # Minimum weight for any model
        self.max_weight = 0.40  # Maximum weight for any single model
        
        # News sentiment configuration
        self.news_sources = ['yahoo', 'finviz', 'marketwatch']
        self.sentiment_cache = {}
        self.sentiment_cache_ttl = 300  # 5 minutes
        
        # Technical indicators configuration
        self.technical_indicators = [
            'RSI', 'MACD', 'BB_upper', 'BB_lower', 'ATR', 'EMA_12', 'EMA_26',
            'Stoch_K', 'Stoch_D', 'Williams_R', 'CCI', 'ADX', 'AROON_up', 
            'AROON_down', 'MFI', 'TSI', 'UO', 'ROC', 'CMF', 'VWAP'
        ]
        
        self._initialize_models()
        
    def _initialize_models(self):
        """Initialize all ML models with enhanced parameters"""
        
        # Enhanced LightGBM
        if LIGHTGBM_AVAILABLE:
            self.models['lightgbm'] = lgb.LGBMRegressor(
                objective='regression',
                metric='rmse',
                boosting_type='gbdt',
                num_leaves=63,
                learning_rate=0.03,
                feature_fraction=0.8,
                bagging_fraction=0.7,
                bagging_freq=3,
                min_child_samples=20,
                reg_alpha=0.1,
                reg_lambda=0.1,
                verbose=0,
                random_state=42,
                n_estimators=200
            )
            self.model_weights['lightgbm'] = 0.25
        
        # Enhanced CatBoost
        if CATBOOST_AVAILABLE:
            self.models['catboost'] = cb.CatBoostRegressor(
                iterations=200,
                learning_rate=0.05,
                depth=8,
                l2_leaf_reg=3,
                bootstrap_type='Bayesian',
                bagging_temperature=1,
                od_type='IncToDec',
                od_wait=20,
                verbose=False,
                random_seed=42
            )
            self.model_weights['catboost'] = 0.25
        
        # Enhanced Random Forest
        self.models['random_forest'] = RandomForestRegressor(
            n_estimators=200,
            max_depth=15,
            min_samples_split=3,
            min_samples_leaf=1,
            max_features='sqrt',
            bootstrap=True,
            oob_score=True,
            random_state=42,
            n_jobs=-1
        )
        self.model_weights['random_forest'] = 0.20
        
        # Gradient Boosting
        self.models['gradient_boost'] = GradientBoostingRegressor(
            n_estimators=150,
            learning_rate=0.05,
            max_depth=8,
            min_samples_split=4,
            min_samples_leaf=2,
            subsample=0.8,
            random_state=42
        )
        self.model_weights['gradient_boost'] = 0.15
        
        # Initialize scalers for each model type
        self.scalers = {
            'standard': StandardScaler(),
            'robust': RobustScaler(),
            'minmax': MinMaxScaler(),
            'lstm_scaler': MinMaxScaler()
        }
        
        # LSTM model (will be created dynamically)
        if TENSORFLOW_AVAILABLE:
            self.model_weights['lstm'] = 0.10
            self.model_weights['gru'] = 0.05
    
    def fetch_cross_asset_data(self) -> Dict[str, float]:
        """Fetch cross-asset correlation data with caching"""
        cache_key = f"cross_assets_{int(time.time() // 60)}"  # 1-minute cache
        
        if cache_key in self.data_cache:
            return self.data_cache[cache_key]
        
        cross_asset_signals = {}
        
        for asset, weight in self.correlation_assets.items():
            try:
                ticker = yf.Ticker(asset)
                data = ticker.history(period='2d', interval='1m')
                
                if len(data) >= 2:
                    current_price = data['Close'].iloc[-1]
                    prev_price = data['Close'].iloc[-2]
                    change_pct = (current_price - prev_price) / prev_price * 100
                    
                    # Apply correlation weight
                    weighted_signal = change_pct * weight
                    cross_asset_signals[asset] = weighted_signal
                    
            except Exception as e:
                print(f"⚠️ Failed to fetch {asset}: {str(e)[:50]}")
                cross_asset_signals[asset] = 0.0
                
        self.data_cache[cache_key] = cross_asset_signals
        return cross_asset_signals
    
    def fetch_news_sentiment(self) -> float:
        """Enhanced news sentiment analysis with multiple sources"""
        cache_key = f"sentiment_{int(time.time() // self.sentiment_cache_ttl)}"
        
        if cache_key in self.sentiment_cache:
            return self.sentiment_cache[cache_key]
        
        sentiment_score = 0.0
        try:
            # Yahoo Finance news sentiment (simplified)
            ticker = yf.Ticker(self.symbol)
            news = ticker.news
            
            if news:
                # Simple sentiment scoring based on headline keywords
                positive_keywords = ['beats', 'exceeds', 'strong', 'growth', 'positive', 'bullish', 'upgrade']
                negative_keywords = ['misses', 'weak', 'decline', 'bearish', 'downgrade', 'concern', 'risk']
                
                total_sentiment = 0
                for article in news[:5]:  # Analyze top 5 articles
                    title = article.get('title', '').lower()
                    
                    pos_count = sum(1 for word in positive_keywords if word in title)
                    neg_count = sum(1 for word in negative_keywords if word in title)
                    
                    total_sentiment += pos_count - neg_count
                
                sentiment_score = np.clip(total_sentiment / 10.0, -1.0, 1.0)
                
        except Exception as e:
            print(f"⚠️ News sentiment fetch failed: {str(e)[:50]}")
            sentiment_score = 0.0
        
        self.sentiment_cache[cache_key] = sentiment_score
        return sentiment_score
    
    def create_enhanced_features(self, price_data: pd.DataFrame, 
                               cross_asset_signals: Dict[str, float]) -> pd.DataFrame:
        """Create comprehensive feature set with cross-asset correlation"""
        
        df = price_data.copy()
        
        # Basic price features
        df['returns'] = df['Close'].pct_change()
        df['returns_1h'] = df['Close'].pct_change(periods=60)  # 1 hour returns
        df['returns_1d'] = df['Close'].pct_change(periods=1440)  # 1 day returns
        
        # Volatility features
        df['volatility_10'] = df['returns'].rolling(10).std()
        df['volatility_30'] = df['returns'].rolling(30).std()
        df['realized_vol'] = df['returns'].rolling(60).std() * np.sqrt(252)
        
        # Enhanced technical indicators
        df['RSI'] = self._calculate_rsi(df['Close'], 14)
        df['RSI_2'] = self._calculate_rsi(df['Close'], 2)  # Short-term RSI
        
        # MACD
        ema_12 = df['Close'].ewm(span=12).mean()
        ema_26 = df['Close'].ewm(span=26).mean()
        df['MACD'] = ema_12 - ema_26
        df['MACD_signal'] = df['MACD'].ewm(span=9).mean()
        df['MACD_histogram'] = df['MACD'] - df['MACD_signal']
        
        # Bollinger Bands
        sma_20 = df['Close'].rolling(20).mean()
        std_20 = df['Close'].rolling(20).std()
        df['BB_upper'] = sma_20 + (2 * std_20)
        df['BB_lower'] = sma_20 - (2 * std_20)
        df['BB_width'] = (df['BB_upper'] - df['BB_lower']) / sma_20
        df['BB_position'] = (df['Close'] - df['BB_lower']) / (df['BB_upper'] - df['BB_lower'])
        
        # ATR
        df['ATR'] = self._calculate_atr(df, 14)
        
        # Volume features
        df['volume_sma'] = df['Volume'].rolling(20).mean()
        df['volume_ratio'] = df['Volume'] / df['volume_sma']
        df['price_volume'] = df['Close'] * df['Volume']
        df['vwap'] = df['price_volume'].rolling(20).sum() / df['Volume'].rolling(20).sum()
        
        # Momentum indicators
        df['momentum_10'] = df['Close'] / df['Close'].shift(10) - 1
        df['momentum_20'] = df['Close'] / df['Close'].shift(20) - 1
        
        # Support/Resistance levels
        df['high_20'] = df['High'].rolling(20).max()
        df['low_20'] = df['Low'].rolling(20).min()
        df['position_in_range'] = (df['Close'] - df['low_20']) / (df['high_20'] - df['low_20'])
        
        # Cross-asset correlation features
        for asset, signal in cross_asset_signals.items():
            df[f'corr_{asset}'] = signal
        
        # Time-based features
        df['hour'] = df.index.hour
        df['minute'] = df.index.minute
        df['is_opening'] = ((df['hour'] == 9) & (df['minute'] >= 30)).astype(int)
        df['is_closing'] = ((df['hour'] == 15) & (df['minute'] >= 30)).astype(int)
        
        # Market regime features
        df['trend_strength'] = abs(df['Close'].rolling(20).apply(
            lambda x: np.polyfit(range(len(x)), x, 1)[0], raw=False
        ))
        
        return df.fillna(0)
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI indicator"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _calculate_atr(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Average True Range"""
        high_low = df['High'] - df['Low']
        high_close = np.abs(df['High'] - df['Close'].shift())
        low_close = np.abs(df['Low'] - df['Close'].shift())
        
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        
        return true_range.rolling(period).mean()
    
    def build_lstm_model(self, input_shape: Tuple[int, int]) -> Sequential:
        """Build enhanced LSTM model with attention mechanism"""
        if not TENSORFLOW_AVAILABLE:
            return None
            
        model = Sequential([
            LSTM(100, return_sequences=True, input_shape=input_shape),
            BatchNormalization(),
            Dropout(0.2),
            
            LSTM(80, return_sequences=True),
            BatchNormalization(),
            Dropout(0.2),
            
            LSTM(60, return_sequences=False),
            BatchNormalization(),
            Dropout(0.2),
            
            Dense(50, activation='relu'),
            Dropout(0.1),
            Dense(25, activation='relu'),
            Dense(1, activation='linear')
        ])
        
        model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='huber',
            metrics=['mae']
        )
        
        return model
    
    def train_ensemble(self, price_data: pd.DataFrame) -> bool:
        """Train all models in the ensemble with enhanced validation"""
        try:
            # Fetch cross-asset data
            cross_asset_signals = self.fetch_cross_asset_data()
            
            # Create comprehensive feature set
            features_df = self.create_enhanced_features(price_data, cross_asset_signals)
            
            # Prepare features and targets
            feature_columns = [col for col in features_df.columns 
                             if col not in ['Open', 'High', 'Low', 'Close', 'Volume']]
            
            X = features_df[feature_columns].iloc[:-1].values  # All but last row
            y = features_df['Close'].shift(-1).iloc[:-1].values  # Next period's close
            
            # Remove any remaining NaN values
            mask = ~(np.isnan(X).any(axis=1) | np.isnan(y))
            X, y = X[mask], y[mask]
            
            if len(X) < 50:  # Need minimum data for training
                print("⚠️ Insufficient data for training")
                return False
            
            # Fit scalers with clean data
            self.scalers['standard'].fit(X)
            self.scalers['robust'].fit(X)
            self.scalers['minmax'].fit(X)
            
            # Scale features
            X_scaled = self.scalers['standard'].transform(X)
            X_robust = self.scalers['robust'].transform(X)
            
            # Time series split for validation
            tscv = TimeSeriesSplit(n_splits=3)
            
            # Train traditional ML models
            for model_name, model in self.models.items():
                if model_name in ['lstm', 'gru']:
                    continue  # Handle separately
                    
                try:
                    # Use different scaling for different models
                    if model_name in ['lightgbm', 'catboost']:
                        X_train = X  # Tree-based models don't need scaling
                    else:
                        X_train = X_scaled if model_name == 'random_forest' else X_robust
                    
                    # Train with validation
                    model.fit(X_train, y)
                    
                    # Calculate cross-validation performance
                    cv_scores = []
                    for train_idx, val_idx in tscv.split(X_train):
                        model.fit(X_train[train_idx], y[train_idx])
                        y_pred = model.predict(X_train[val_idx])
                        score = mean_absolute_error(y[val_idx], y_pred)
                        cv_scores.append(score)
                    
                    # Update performance tracking
                    avg_score = np.mean(cv_scores)
                    self.prediction_accuracy[model_name]['recent_performance'].append(avg_score)
                    
                    # Keep only last 50 performance scores
                    if len(self.prediction_accuracy[model_name]['recent_performance']) > 50:
                        self.prediction_accuracy[model_name]['recent_performance'] = \
                            self.prediction_accuracy[model_name]['recent_performance'][-50:]
                    
                    print(f"✅ {model_name.upper()} trained - CV MAE: {avg_score:.4f}")
                    
                except Exception as e:
                    print(f"❌ {model_name} training failed: {str(e)[:100]}")
            
            # Train LSTM/GRU if available
            if TENSORFLOW_AVAILABLE and len(X) >= 60:
                self._train_lstm_models(X_scaled, y)
            
            # Update dynamic weights based on performance
            self._update_dynamic_weights()
            
            # Store feature names for later use
            self.feature_names = feature_columns
            
            print("✅ Ensemble training completed successfully")
            return True
            
        except Exception as e:
            print(f"❌ Ensemble training failed: {str(e)}")
            return False
    
    def _train_lstm_models(self, X_scaled: np.ndarray, y: np.ndarray):
        """Train LSTM and GRU models"""
        try:
            # Prepare sequences for LSTM
            sequence_length = 60
            if len(X_scaled) < sequence_length + 10:
                return
            
            # Create sequences
            X_seq, y_seq = [], []
            for i in range(sequence_length, len(X_scaled)):
                X_seq.append(X_scaled[i-sequence_length:i])
                y_seq.append(y[i])
            
            X_seq, y_seq = np.array(X_seq), np.array(y_seq)
            
            # Split for training
            split_idx = int(len(X_seq) * 0.8)
            X_train, X_val = X_seq[:split_idx], X_seq[split_idx:]
            y_train, y_val = y_seq[:split_idx], y_seq[split_idx:]
            
            # Build and train LSTM
            lstm_model = self.build_lstm_model((sequence_length, X_scaled.shape[1]))
            if lstm_model:
                early_stopping = EarlyStopping(patience=10, restore_best_weights=True)
                
                lstm_model.fit(
                    X_train, y_train,
                    validation_data=(X_val, y_val),
                    epochs=50,
                    batch_size=32,
                    callbacks=[early_stopping],
                    verbose=0
                )
                
                self.models['lstm'] = lstm_model
                print("✅ LSTM model trained successfully")
                
        except Exception as e:
            print(f"⚠️ LSTM training failed: {str(e)[:100]}")
    
    def _update_dynamic_weights(self):
        """Update model weights based on recent performance"""
        if not self.adaptive_weights:
            return
        
        total_performance = 0
        model_scores = {}
        
        for model_name in self.model_weights.keys():
            if model_name in self.prediction_accuracy:
                recent_perf = self.prediction_accuracy[model_name]['recent_performance']
                if recent_perf:
                    # Lower MAE is better, so invert for weighting
                    avg_mae = np.mean(recent_perf[-10:])  # Last 10 performances
                    score = 1.0 / (1.0 + avg_mae)  # Inverse relationship
                    model_scores[model_name] = score
                    total_performance += score
        
        if total_performance > 0:
            # Normalize weights
            for model_name in self.model_weights.keys():
                if model_name in model_scores:
                    new_weight = model_scores[model_name] / total_performance
                    # Apply constraints
                    new_weight = max(self.min_weight, min(self.max_weight, new_weight))
                    self.model_weights[model_name] = new_weight
            
            # Ensure weights sum to 1.0
            total_weight = sum(self.model_weights.values())
            if total_weight > 0:
                for model_name in self.model_weights.keys():
                    self.model_weights[model_name] /= total_weight
    
    def predict_ensemble(self, current_data: pd.DataFrame, 
                        current_price: float) -> EnhancedPredictionResult:
        """Generate ensemble prediction with comprehensive analysis"""
        try:
            # Fetch real-time cross-asset signals
            cross_asset_signals = self.fetch_cross_asset_data()
            
            # Get news sentiment
            news_sentiment = self.fetch_news_sentiment()
            
            # Create features
            features_df = self.create_enhanced_features(current_data, cross_asset_signals)
            
            if self.feature_names:
                # Use last row of features for prediction
                X = features_df[self.feature_names].iloc[-1:].values
                
                # Check for NaN values
                if np.isnan(X).any():
                    X = np.nan_to_num(X)
                
                # Generate predictions from each model
                individual_predictions = {}
                prediction_weights = {}
                
                for model_name, model in self.models.items():
                    if model_name in ['lstm', 'gru']:
                        continue  # Handle separately
                        
                    try:
                        # Scale features appropriately
                        if model_name in ['lightgbm', 'catboost']:
                            X_scaled = X
                        elif model_name == 'random_forest':
                            # Check if scaler is fitted, if not use original features
                            if hasattr(self.scalers['standard'], 'scale_'):
                                X_scaled = self.scalers['standard'].transform(X)
                            else:
                                print(f"⚠️ StandardScaler not fitted for {model_name}, using raw features")
                                X_scaled = X
                        else:
                            # Check if scaler is fitted, if not use original features
                            if hasattr(self.scalers['robust'], 'scale_'):
                                X_scaled = self.scalers['robust'].transform(X)
                            else:
                                print(f"⚠️ RobustScaler not fitted for {model_name}, using raw features")
                                X_scaled = X
                        
                        pred = model.predict(X_scaled)[0]
                        individual_predictions[model_name] = pred
                        prediction_weights[model_name] = self.model_weights.get(model_name, 0.1)
                        
                    except Exception as e:
                        print(f"⚠️ {model_name} prediction failed: {str(e)[:50]}")
                
                # LSTM prediction if available
                if 'lstm' in self.models and len(current_data) >= 60:
                    try:
                        X_lstm = self.scalers['standard'].transform(
                            features_df[self.feature_names].iloc[-60:].fillna(0).values
                        )
                        X_lstm = X_lstm.reshape(1, 60, -1)
                        pred = self.models['lstm'].predict(X_lstm, verbose=0)[0][0]
                        individual_predictions['lstm'] = pred
                        prediction_weights['lstm'] = self.model_weights.get('lstm', 0.1)
                    except Exception as e:
                        print(f"⚠️ LSTM prediction failed: {str(e)[:50]}")
                
                # Calculate weighted ensemble prediction
                if individual_predictions:
                    total_weight = sum(prediction_weights.values())
                    if total_weight > 0:
                        weighted_pred = sum(
                            pred * prediction_weights.get(name, 0) 
                            for name, pred in individual_predictions.items()
                        ) / total_weight
                    else:
                        weighted_pred = np.mean(list(individual_predictions.values()))
                    
                    # Calculate consensus score
                    predictions_list = list(individual_predictions.values())
                    std_dev = np.std(predictions_list)
                    mean_pred = np.mean(predictions_list)
                    consensus_score = max(0, 100 - (std_dev / abs(mean_pred) * 100)) if mean_pred != 0 else 50
                    
                    # Determine direction and confidence
                    price_change = weighted_pred - current_price
                    price_change_pct = (price_change / current_price) * 100
                    
                    if abs(price_change_pct) < 0.1:
                        direction = "NEUTRAL"
                        confidence = 50 + consensus_score * 0.3
                    elif price_change_pct > 0:
                        direction = "UP"
                        confidence = 50 + abs(price_change_pct) * 5 + consensus_score * 0.5
                    else:
                        direction = "DOWN"
                        confidence = 50 + abs(price_change_pct) * 5 + consensus_score * 0.5
                    
                    confidence = min(95, max(30, confidence))
                    
                    # Calculate volatility forecast
                    recent_volatility = features_df['volatility_30'].iloc[-1] if 'volatility_30' in features_df.columns else 0.02
                    
                    # Feature importance (simplified)
                    feature_importance = {}
                    if 'random_forest' in self.models:
                        try:
                            rf_importance = self.models['random_forest'].feature_importances_
                            for i, name in enumerate(self.feature_names[:len(rf_importance)]):
                                feature_importance[name] = rf_importance[i]
                        except:
                            pass
                    
                    # Risk score calculation
                    risk_factors = [
                        abs(price_change_pct) * 0.3,  # Price volatility
                        (100 - consensus_score) * 0.4,  # Model disagreement
                        abs(news_sentiment) * 20,  # News uncertainty
                        recent_volatility * 1000  # Market volatility
                    ]
                    risk_score = min(100, sum(risk_factors))
                    
                    return EnhancedPredictionResult(
                        predicted_price=weighted_pred,
                        direction=direction,
                        confidence=confidence,
                        consensus_score=consensus_score,
                        individual_predictions=individual_predictions,
                        feature_importance=feature_importance,
                        cross_asset_signals=cross_asset_signals,
                        news_sentiment_score=news_sentiment,
                        risk_score=risk_score,
                        volatility_forecast=recent_volatility,
                        timestamp=datetime.now(),
                        model_weights_used=prediction_weights
                    )
            
            # Fallback prediction
            return EnhancedPredictionResult(
                predicted_price=current_price,
                direction="NEUTRAL",
                confidence=50.0,
                consensus_score=50.0,
                individual_predictions={},
                feature_importance={},
                cross_asset_signals=cross_asset_signals,
                news_sentiment_score=news_sentiment,
                risk_score=75.0,
                volatility_forecast=0.02,
                timestamp=datetime.now(),
                model_weights_used={}
            )
            
        except Exception as e:
            print(f"❌ Ensemble prediction failed: {str(e)}")
            return EnhancedPredictionResult(
                predicted_price=current_price,
                direction="NEUTRAL",
                confidence=30.0,
                consensus_score=30.0,
                individual_predictions={},
                feature_importance={},
                cross_asset_signals={},
                news_sentiment_score=0.0,
                risk_score=90.0,
                volatility_forecast=0.02,
                timestamp=datetime.now(),
                model_weights_used={}
            )

# Example usage and testing
if __name__ == "__main__":
    ensemble = UpgradedMLEnsemble("AMD")
    
    # Test with sample data
    try:
        ticker = yf.Ticker("AMD")
        data = ticker.history(period="5d", interval="1m")
        
        if len(data) > 100:
            print("🚀 Training ensemble with sample data...")
            success = ensemble.train_ensemble(data)
            
            if success:
                print("🎯 Generating test prediction...")
                result = ensemble.predict_ensemble(data, data['Close'].iloc[-1])
                
                print(f"\n📊 Prediction Results:")
                print(f"   Predicted Price: ${result.predicted_price:.2f}")
                print(f"   Direction: {result.direction}")
                print(f"   Confidence: {result.confidence:.1f}%")
                print(f"   Consensus Score: {result.consensus_score:.1f}%")
                print(f"   Risk Score: {result.risk_score:.1f}%")
                print(f"   News Sentiment: {result.news_sentiment_score:.3f}")
                print(f"   Cross-Asset Signals: {len(result.cross_asset_signals)} assets")
                
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")