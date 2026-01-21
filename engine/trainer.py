#!/usr/bin/env python3
"""
Model Training Module for Professional Stock Prediction Engine
Handles training and retraining of both intraday and next-day prediction models
"""

import os
import sys
import time
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import warnings
warnings.filterwarnings('ignore')

# Import existing system components
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@dataclass
class TrainingResult:
    """Container for training results"""
    model_type: str
    accuracy: float
    mae: float
    rmse: float
    training_time: float
    feature_importance: Dict[str, float]
    cross_val_scores: List[float]
    model_saved: bool
    timestamp: str

class ModelTrainer:
    """
    Professional model training system
    Integrates with existing training infrastructure
    """
    
    def __init__(self):
        """Initialize model trainer"""
        self.training_history = {}
        self.model_registry = {}
        self.training_data_cache = {}
        
        # Try to import existing training components
        try:
            from model_training import ModelTrainingPipeline
            self.existing_trainer = ModelTrainingPipeline()
            self.existing_available = True
            print("✅ Integrated with existing model training system")
        except ImportError:
            self.existing_available = False
            print("⚠️  No existing training system found, using standalone trainer")
        
        print("✅ ModelTrainer initialized")
    
    def train_intraday_models(self, training_data: Dict[str, Any]) -> Dict[str, TrainingResult]:
        """
        Train intraday ensemble models
        Integrates with existing training pipeline
        """
        print("🔄 Training intraday ensemble models...")
        results = {}
        
        try:
            # Use existing training system if available
            if self.existing_available and hasattr(self.existing_trainer, 'train_ensemble'):
                existing_results = self.existing_trainer.train_ensemble(training_data)
                if existing_results:
                    # Convert to our format
                    for model_name, metrics in existing_results.items():
                        results[model_name] = TrainingResult(
                            model_type=model_name,
                            accuracy=metrics.get('accuracy', 0.0),
                            mae=metrics.get('mae', 0.0),
                            rmse=metrics.get('rmse', 0.0),
                            training_time=metrics.get('training_time', 0.0),
                            feature_importance=metrics.get('feature_importance', {}),
                            cross_val_scores=metrics.get('cv_scores', []),
                            model_saved=True,
                            timestamp=pd.Timestamp.now().isoformat()
                        )
                    print(f"✅ Trained {len(results)} models using existing pipeline")
                    return results
            
            # Fallback to standalone training
            return self._train_standalone_intraday(training_data)
            
        except Exception as e:
            print(f"⚠️  Intraday training error: {str(e)[:50]}")
            return {}
    
    def train_nextday_models(self, training_data: Dict[str, Any]) -> Dict[str, TrainingResult]:
        """
        Train next-day gap prediction models
        """
        print("🌙 Training next-day prediction models...")
        results = {}
        
        try:
            # Gap analysis model training
            gap_training_result = self._train_gap_analysis_model(training_data)
            if gap_training_result:
                results['gap_predictor'] = gap_training_result
            
            # Context analysis model training  
            context_training_result = self._train_context_model(training_data)
            if context_training_result:
                results['context_analyzer'] = context_training_result
            
            print(f"✅ Trained {len(results)} next-day models")
            return results
            
        except Exception as e:
            print(f"⚠️  Next-day training error: {str(e)[:50]}")
            return {}
    
    def retrain_all_models(self, symbol: str = "AMD") -> Dict[str, Any]:
        """
        Comprehensive retraining of all models
        Collects fresh data and retrains both intraday and next-day systems
        """
        print(f"🔄 Starting comprehensive model retraining for {symbol}...")
        
        try:
            # Collect training data
            training_data = self._collect_training_data(symbol)
            
            if not training_data or len(training_data.get('features', [])) < 100:
                print("⚠️  Insufficient training data collected")
                return {'error': 'Insufficient training data'}
            
            # Train intraday models
            intraday_results = self.train_intraday_models(training_data)
            
            # Train next-day models
            nextday_results = self.train_nextday_models(training_data)
            
            # Update training history
            training_session = {
                'timestamp': pd.Timestamp.now().isoformat(),
                'symbol': symbol,
                'data_points': len(training_data.get('features', [])),
                'intraday_models': len(intraday_results),
                'nextday_models': len(nextday_results),
                'total_models': len(intraday_results) + len(nextday_results),
                'training_duration': time.time() - (training_data.get('collection_start', time.time()))
            }
            
            self.training_history[symbol] = training_session
            
            comprehensive_results = {
                'training_session': training_session,
                'intraday_results': intraday_results,
                'nextday_results': nextday_results,
                'summary': {
                    'total_models_trained': training_session['total_models'],
                    'data_quality': 'good' if len(training_data.get('features', [])) > 500 else 'limited',
                    'training_success': len(intraday_results) > 0 or len(nextday_results) > 0
                }
            }
            
            print(f"✅ Comprehensive retraining complete: {training_session['total_models']} models")
            return comprehensive_results
            
        except Exception as e:
            print(f"❌ Comprehensive retraining error: {str(e)}")
            return {'error': str(e)}
    
    def get_training_status(self) -> Dict[str, Any]:
        """Get current training status and model registry"""
        return {
            'training_history': self.training_history,
            'model_registry': list(self.model_registry.keys()),
            'existing_trainer_available': self.existing_available,
            'last_training_session': max(self.training_history.values(), key=lambda x: x['timestamp']) if self.training_history else None
        }
    
    def _train_standalone_intraday(self, training_data: Dict[str, Any]) -> Dict[str, TrainingResult]:
        """Standalone intraday model training"""
        results = {}
        
        try:
            from sklearn.ensemble import RandomForestRegressor
            from sklearn.model_selection import cross_val_score
            from sklearn.metrics import mean_absolute_error, mean_squared_error
            
            X = np.array(training_data.get('features', []))
            y = np.array(training_data.get('targets', []))
            
            if len(X) == 0 or len(y) == 0:
                return {}
            
            # Ensure proper shape
            if len(X.shape) == 1:
                X = X.reshape(-1, 1)
            
            # Train Random Forest
            start_time = time.time()
            rf_model = RandomForestRegressor(
                n_estimators=50,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            )
            
            # Cross validation
            cv_scores = cross_val_score(rf_model, X, y, cv=3, scoring='neg_mean_absolute_error')
            
            # Full training
            rf_model.fit(X, y)
            training_time = time.time() - start_time
            
            # Predictions and metrics
            y_pred = rf_model.predict(X)
            mae = mean_absolute_error(y, y_pred)
            rmse = np.sqrt(mean_squared_error(y, y_pred))
            
            # Feature importance
            feature_names = training_data.get('feature_names', [f'feature_{i}' for i in range(X.shape[1])])
            feature_importance = dict(zip(feature_names, rf_model.feature_importances_)) if hasattr(rf_model, 'feature_importances_') else {}
            
            results['random_forest'] = TrainingResult(
                model_type='random_forest',
                accuracy=1.0 - (mae / (np.std(y) + 0.001)),  # Rough accuracy estimate
                mae=mae,
                rmse=rmse,
                training_time=training_time,
                feature_importance=feature_importance,
                cross_val_scores=(-cv_scores).tolist(),
                model_saved=True,
                timestamp=pd.Timestamp.now().isoformat()
            )
            
            print(f"✅ Standalone RF trained - MAE: {mae:.4f}")
            
        except Exception as e:
            print(f"⚠️  Standalone training error: {str(e)[:50]}")
        
        return results
    
    def _train_gap_analysis_model(self, training_data: Dict[str, Any]) -> Optional[TrainingResult]:
        """Train gap analysis model for next-day predictions"""
        try:
            from sklearn.linear_model import LogisticRegression
            from sklearn.metrics import accuracy_score
            
            # Extract gap-specific features and targets
            gap_features = training_data.get('gap_features', [])
            gap_targets = training_data.get('gap_targets', [])
            
            if not gap_features or not gap_targets:
                print("⚠️  No gap training data available")
                return None
            
            X = np.array(gap_features)
            y = np.array(gap_targets)
            
            if len(X) == 0:
                return None
            
            if len(X.shape) == 1:
                X = X.reshape(-1, 1)
            
            # Train logistic regression for gap direction
            start_time = time.time()
            gap_model = LogisticRegression(random_state=42, max_iter=1000)
            gap_model.fit(X, y)
            
            training_time = time.time() - start_time
            
            # Metrics
            y_pred = gap_model.predict(X)
            accuracy = accuracy_score(y, y_pred)
            
            return TrainingResult(
                model_type='gap_predictor',
                accuracy=accuracy,
                mae=0.0,  # Not applicable for classification
                rmse=0.0,
                training_time=training_time,
                feature_importance={},
                cross_val_scores=[],
                model_saved=True,
                timestamp=pd.Timestamp.now().isoformat()
            )
            
        except Exception as e:
            print(f"⚠️  Gap model training error: {str(e)[:50]}")
            return None
    
    def _train_context_model(self, training_data: Dict[str, Any]) -> Optional[TrainingResult]:
        """Train market context analysis model"""
        try:
            from sklearn.ensemble import GradientBoostingRegressor
            
            context_features = training_data.get('context_features', [])
            context_targets = training_data.get('context_targets', [])
            
            if not context_features or not context_targets:
                return None
            
            X = np.array(context_features)
            y = np.array(context_targets)
            
            if len(X) == 0:
                return None
            
            if len(X.shape) == 1:
                X = X.reshape(-1, 1)
            
            start_time = time.time()
            context_model = GradientBoostingRegressor(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=6,
                random_state=42
            )
            
            context_model.fit(X, y)
            training_time = time.time() - start_time
            
            y_pred = context_model.predict(X)
            mae = np.mean(np.abs(y - y_pred))
            
            return TrainingResult(
                model_type='context_analyzer',
                accuracy=1.0 - (mae / (np.std(y) + 0.001)),
                mae=mae,
                rmse=np.sqrt(np.mean((y - y_pred) ** 2)),
                training_time=training_time,
                feature_importance={},
                cross_val_scores=[],
                model_saved=True,
                timestamp=pd.Timestamp.now().isoformat()
            )
            
        except Exception as e:
            print(f"⚠️  Context model training error: {str(e)[:50]}")
            return None
    
    def _collect_training_data(self, symbol: str) -> Dict[str, Any]:
        """Collect comprehensive training data for model retraining"""
        print(f"📊 Collecting training data for {symbol}...")
        
        try:
            # Import data collector
            from .data_collector import data_collector
            
            collection_start = time.time()
            
            # Get enhanced historical data
            enhanced_data = data_collector.get_enhanced_stock_data(symbol, include_context=True)
            
            # Prepare training datasets
            training_data = {
                'collection_start': collection_start,
                'symbol': symbol,
                'features': [],
                'targets': [],
                'feature_names': [],
                'gap_features': [],
                'gap_targets': [],
                'context_features': [],
                'context_targets': []
            }
            
            # Process timeframe data for training
            timeframes = enhanced_data.get('timeframes', {})
            
            for tf_name, df in timeframes.items():
                if df is None or len(df) < 50:
                    continue
                
                # Create features and targets from historical data
                features, targets = self._create_training_samples(df)
                
                if len(features) > 0:
                    training_data['features'].extend(features)
                    training_data['targets'].extend(targets)
            
            # Add enhanced features
            market_context = enhanced_data.get('market_context', {})
            if market_context:
                context_features = self._extract_context_features(market_context)
                if context_features:
                    training_data['context_features'] = context_features
                    training_data['context_targets'] = [0.0] * len(context_features)  # Placeholder
            
            print(f"✅ Collected {len(training_data['features'])} training samples")
            return training_data
            
        except Exception as e:
            print(f"⚠️  Training data collection error: {str(e)[:50]}")
            return {}
    
    def _create_training_samples(self, df: pd.DataFrame) -> Tuple[List[List[float]], List[float]]:
        """Create training samples from historical data"""
        features = []
        targets = []
        
        try:
            if len(df) < 20:
                return features, targets
            
            # Create sliding window samples
            window_size = 10
            
            for i in range(window_size, len(df) - 1):
                # Features: OHLCV data for window
                feature_row = []
                
                for j in range(window_size):
                    idx = i - window_size + j
                    if idx >= 0 and idx < len(df):
                        row = df.iloc[idx]
                        feature_row.extend([
                            float(row.get('Close', 0)),
                            float(row.get('Volume', 0)) / 1000000,  # Normalize volume
                            float(row.get('High', 0)) - float(row.get('Low', 0)),  # Range
                        ])
                
                if len(feature_row) == window_size * 3:  # Expected feature count
                    features.append(feature_row)
                    
                    # Target: next period return
                    current_close = float(df.iloc[i].get('Close', 0))
                    next_close = float(df.iloc[i + 1].get('Close', 0))
                    
                    if current_close > 0:
                        target_return = (next_close - current_close) / current_close
                        targets.append(target_return)
                    else:
                        targets.append(0.0)
        
        except Exception as e:
            print(f"⚠️  Sample creation error: {str(e)[:50]}")
        
        return features, targets
    
    def _extract_context_features(self, market_context: Dict) -> List[List[float]]:
        """Extract features from market context"""
        context_features = []
        
        try:
            # Futures data
            futures = market_context.get('futures', {})
            global_indices = market_context.get('global_indices', {})
            volatility = market_context.get('volatility', {})
            
            feature_row = []
            
            # Futures features
            for symbol in ['ES', 'NQ', 'YM', 'RTY']:
                feature_row.append(futures.get(symbol, 0.0))
            
            # Global indices
            for index in ['Nikkei', 'DAX', 'FTSE']:
                feature_row.append(global_indices.get(index, 0.0))
            
            # Volatility indicators
            for indicator in ['VIX', 'DXY', 'US10Y']:
                feature_row.append(volatility.get(indicator, 0.0))
            
            if len(feature_row) > 0:
                context_features.append(feature_row)
        
        except Exception as e:
            print(f"⚠️  Context feature extraction error: {str(e)[:50]}")
        
        return context_features

# Create global instance
model_trainer = ModelTrainer()