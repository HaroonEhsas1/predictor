"""
Model training and ensemble logic for After Close Engine
Handles LightGBM and optional LSTM models with auto-fit capabilities
"""
import logging
import numpy as np
import pandas as pd
import os
import joblib
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime

# Core ML libraries
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.ensemble import GradientBoostingRegressor

# Try to import optional libraries (suppress warnings - system designed to use fallbacks)
try:
    import lightgbm as lgb
    LIGHTGBM_AVAILABLE = True
except ImportError:
    LIGHTGBM_AVAILABLE = False
    # Note: System uses GradientBoostingRegressor fallback by design

try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False
    # Note: LSTM component optional, system works with tabular model only

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config import CONFIG

logger = logging.getLogger(__name__)

class GradientBoostingModel:
    """Gradient Boosting model for tabular overnight prediction (fallback for LightGBM)"""
    
    def __init__(self):
        self.model = None
        self.model_path = os.path.join(CONFIG.model_path, 'gradient_boosting_model.joblib')
        self.feature_names = [
            'overnight_futures_pct',
            'net_options_flow',
            'news_sentiment_score', 
            'global_index_impact_score',
            'prior_close_return',
            'intraday_volatility'
        ]
    
    def train(self, X: np.ndarray, y: np.ndarray) -> Dict[str, float]:
        """Train Gradient Boosting model and return metrics"""
        
        try:
            logger.info("Training Gradient Boosting model...")
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Initialize model
            if LIGHTGBM_AVAILABLE:
                self.model = lgb.LGBMRegressor(**CONFIG.lightgbm_params)
                logger.info("Using LightGBM")
            else:
                # Fallback to sklearn GradientBoostingRegressor
                self.model = GradientBoostingRegressor(
                    n_estimators=100,
                    learning_rate=0.1,
                    max_depth=6,
                    random_state=42
                )
                logger.info("Using sklearn GradientBoostingRegressor (LightGBM fallback)")
            
            # Train model
            if LIGHTGBM_AVAILABLE:
                self.model.fit(
                    X_train, y_train,
                    eval_set=[(X_test, y_test)],
                    callbacks=[lgb.early_stopping(stopping_rounds=50)],
                    verbose=False
                )
            else:
                self.model.fit(X_train, y_train)
            
            # Calculate metrics
            y_pred = self.model.predict(X_test)
            metrics = {
                'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
                'mae': mean_absolute_error(y_test, y_pred),
                'train_samples': len(X_train),
                'test_samples': len(X_test)
            }
            
            model_name = "LightGBM" if LIGHTGBM_AVAILABLE else "GradientBoosting"
            logger.info(f"{model_name} training completed: RMSE={metrics['rmse']:.4f}, MAE={metrics['mae']:.4f}")
            return metrics
            
        except Exception as e:
            logger.error(f"Model training failed: {e}")
            raise e
    
    def save(self):
        """Save trained model to disk"""
        if self.model is not None:
            os.makedirs(CONFIG.model_path, exist_ok=True)
            joblib.dump(self.model, self.model_path)
            model_name = "LightGBM" if LIGHTGBM_AVAILABLE else "GradientBoosting"
            logger.info(f"{model_name} model saved to {self.model_path}")
    
    def load(self) -> bool:
        """Load trained model from disk"""
        try:
            if os.path.exists(self.model_path):
                self.model = joblib.load(self.model_path)
                model_name = "LightGBM" if LIGHTGBM_AVAILABLE else "GradientBoosting"
                logger.info(f"{model_name} model loaded from {self.model_path}")
                return True
            else:
                logger.warning(f"Model not found: {self.model_path}")
                return False
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False
    
    def predict(self, X: np.ndarray) -> float:
        """Make prediction with trained model"""
        if self.model is None:
            logger.error("Model not loaded")
            return 0.0
            
        try:
            prediction = self.model.predict(X.reshape(1, -1))[0]
            logger.debug(f"Model prediction: {prediction:.4f}")
            return float(prediction)
        except Exception as e:
            logger.error(f"Model prediction failed: {e}")
            return 0.0

class LSTMModel:
    """LSTM model for sequential overnight prediction"""
    
    def __init__(self):
        self.model: Optional[Any] = None
        self.model_path = os.path.join(CONFIG.model_path, 'lstm_model')
        self.sequence_length = CONFIG.lstm_sequence_length
        self.feature_count = 6  # Number of features
        
    def _build_model(self) -> Any:
        """Build LSTM architecture"""
        if not TF_AVAILABLE:
            return None
            
        try:
            model = keras.Sequential([
                layers.LSTM(32, return_sequences=True, 
                           input_shape=(self.sequence_length, self.feature_count)),
                layers.Dropout(0.2),
                layers.LSTM(16, return_sequences=False),
                layers.Dropout(0.2),
                layers.Dense(8, activation='relu'),
                layers.Dense(1, activation='linear')
            ])
            
            model.compile(
                optimizer='adam',
                loss='mse',
                metrics=['mae']
            )
            
            return model
            
        except Exception as e:
            logger.error(f"Failed to build LSTM model: {e}")
            return None
    
    def train(self, X: np.ndarray, y: np.ndarray) -> Dict[str, float]:
        """Train LSTM model and return metrics"""
        
        if not TF_AVAILABLE:
            logger.warning("TensorFlow not available, skipping LSTM training")
            return {'rmse': 0.0, 'mae': 0.0, 'train_samples': 0, 'test_samples': 0}
        
        try:
            logger.info("Training LSTM model...")
            
            # Ensure correct shape
            if len(X.shape) == 2:
                logger.warning("LSTM input should be 3D, skipping training")
                return {'rmse': 0.0, 'mae': 0.0, 'train_samples': 0, 'test_samples': 0}
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Build model
            self.model = self._build_model()
            if self.model is None:
                return {'rmse': 0.0, 'mae': 0.0, 'train_samples': 0, 'test_samples': 0}
            
            # Train model
            history = self.model.fit(
                X_train, y_train,
                validation_data=(X_test, y_test),
                epochs=50,
                batch_size=16,
                verbose=0,
                callbacks=[
                    keras.callbacks.EarlyStopping(patience=10, restore_best_weights=True)
                ]
            )
            
            # Calculate metrics
            y_pred = self.model.predict(X_test, verbose=0)
            metrics = {
                'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
                'mae': mean_absolute_error(y_test, y_pred),
                'train_samples': len(X_train),
                'test_samples': len(X_test)
            }
            
            logger.info(f"LSTM training completed: RMSE={metrics['rmse']:.4f}, MAE={metrics['mae']:.4f}")
            return metrics
            
        except Exception as e:
            logger.error(f"LSTM training failed: {e}")
            return {'rmse': 0.0, 'mae': 0.0, 'train_samples': 0, 'test_samples': 0}
    
    def save(self):
        """Save trained model to disk"""
        if self.model is not None and TF_AVAILABLE:
            try:
                os.makedirs(CONFIG.model_path, exist_ok=True)
                self.model.save(self.model_path)
                logger.info(f"LSTM model saved to {self.model_path}")
            except Exception as e:
                logger.error(f"Failed to save LSTM model: {e}")
    
    def load(self) -> bool:
        """Load trained model from disk"""
        if not TF_AVAILABLE:
            return False
            
        try:
            if os.path.exists(self.model_path):
                self.model = keras.models.load_model(self.model_path)
                logger.info(f"LSTM model loaded from {self.model_path}")
                return True
            else:
                logger.warning(f"LSTM model not found: {self.model_path}")
                return False
        except Exception as e:
            logger.error(f"Failed to load LSTM model: {e}")
            return False
    
    def predict(self, X: np.ndarray) -> float:
        """Make prediction with trained model"""
        if self.model is None or not TF_AVAILABLE:
            logger.debug("LSTM model not available")
            return 0.0
            
        try:
            # Ensure correct shape for LSTM
            if len(X.shape) == 2:
                X = X.reshape(1, X.shape[0], X.shape[1])
            
            prediction = self.model.predict(X, verbose=0)[0][0]
            logger.debug(f"LSTM prediction: {prediction:.4f}")
            return float(prediction)
        except Exception as e:
            logger.error(f"LSTM prediction failed: {e}")
            return 0.0

class EnsembleModel:
    """Ensemble model combining LightGBM and LSTM"""
    
    def __init__(self):
        self.gradient_boosting = GradientBoostingModel()
        self.lstm = LSTMModel()
        self.weights = CONFIG.ensemble_weights
        self.metadata_path = os.path.join(CONFIG.model_path, 'ensemble_metadata.json')
    
    def train(self, tabular_data: Tuple[np.ndarray, np.ndarray], 
              sequence_data: Optional[Tuple[np.ndarray, np.ndarray]] = None) -> Dict[str, Any]:
        """Train ensemble models"""
        
        results = {
            'gradient_boosting': {},
            'lstm': {},
            'training_timestamp': datetime.now().isoformat()
        }
        
        # Train Gradient Boosting model
        try:
            X_tab, y_tab = tabular_data
            results['gradient_boosting'] = self.gradient_boosting.train(X_tab, y_tab)
            self.gradient_boosting.save()
        except Exception as e:
            logger.error(f"Gradient Boosting training failed: {e}")
            results['gradient_boosting'] = {'error': str(e)}
        
        # Train LSTM if sequence data available
        if sequence_data is not None:
            try:
                X_seq, y_seq = sequence_data
                results['lstm'] = self.lstm.train(X_seq, y_seq)
                self.lstm.save()
            except Exception as e:
                logger.error(f"LSTM training failed: {e}")
                results['lstm'] = {'error': str(e)}
        else:
            results['lstm'] = {'message': 'No sequence data available'}
        
        # Save metadata
        self._save_metadata(results)
        
        return results
    
    def load(self) -> bool:
        """Load all ensemble models"""
        gb_loaded = self.gradient_boosting.load()
        lstm_loaded = self.lstm.load()
        
        logger.info(f"Ensemble loading: GradientBoosting={gb_loaded}, LSTM={lstm_loaded}")
        return gb_loaded  # At minimum we need the gradient boosting model
    
    def predict(self, tabular_features: np.ndarray, 
                sequence_features: Optional[np.ndarray] = None) -> Tuple[float, Dict[str, float]]:
        """Make ensemble prediction"""
        
        predictions = {}
        
        # Gradient Boosting prediction
        gb_pred = self.gradient_boosting.predict(tabular_features)
        predictions['lightgbm'] = gb_pred  # Keep same key for API compatibility
        
        # LSTM prediction if available
        lstm_pred = 0.0
        if sequence_features is not None:
            lstm_pred = self.lstm.predict(sequence_features)
            predictions['lstm'] = lstm_pred
        else:
            predictions['lstm'] = 0.0
        
        # Ensemble prediction
        if predictions['lstm'] != 0.0:
            # Use both models
            ensemble_pred = (self.weights['lightgbm'] * gb_pred + 
                           self.weights['lstm'] * lstm_pred)
            logger.debug(f"Ensemble prediction using both models: {ensemble_pred:.4f}")
        else:
            # Use only Gradient Boosting
            ensemble_pred = gb_pred
            logger.debug(f"Ensemble prediction using Gradient Boosting only: {ensemble_pred:.4f}")
        
        return ensemble_pred, predictions
    
    def _save_metadata(self, results: Dict[str, Any]):
        """Save training metadata"""
        try:
            import json
            os.makedirs(CONFIG.model_path, exist_ok=True)
            with open(self.metadata_path, 'w') as f:
                json.dump(results, f, indent=2)
            logger.info(f"Ensemble metadata saved to {self.metadata_path}")
        except Exception as e:
            logger.error(f"Failed to save metadata: {e}")

def auto_fit_models(force_retrain: bool = False) -> Dict[str, Any]:
    """
    Auto-fit models if they don't exist or force retrain requested
    Returns: Training results and status
    """
    
    ensemble = EnsembleModel()
    
    # Check if models exist
    models_exist = ensemble.load()
    
    if models_exist and not force_retrain:
        logger.info("Models already exist and force retrain not requested")
        return {'status': 'models_exist', 'action': 'no_training'}
    
    # Load historical data for training
    historical_path = os.path.join(CONFIG.sample_data_path, 'historical_features.csv')
    
    if not os.path.exists(historical_path):
        logger.error(f"Historical training data not found: {historical_path}")
        return {'status': 'error', 'message': 'No historical data for training'}
    
    try:
        logger.info(f"Auto-fitting models from {historical_path}")
        
        # Load data
        df = pd.read_csv(historical_path)
        
        # Separate features and target
        feature_columns = [
            'overnight_futures_pct',
            'net_options_flow',
            'news_sentiment_score',
            'global_index_impact_score', 
            'prior_close_return',
            'intraday_volatility'
        ]
        
        target_column = 'next_day_return'  # Expected target column
        
        if target_column not in df.columns:
            logger.error(f"Target column '{target_column}' not found in historical data")
            return {'status': 'error', 'message': f"Missing target column: {target_column}"}
        
        # Prepare tabular data
        X_tabular = df[feature_columns].values
        y = df[target_column].values
        
        # Prepare sequence data (if enough data)
        X_sequence = None
        if len(df) >= CONFIG.lstm_sequence_length * 2:  # Minimum for meaningful sequence
            sequences = []
            sequence_targets = []
            
            for i in range(CONFIG.lstm_sequence_length, len(df)):
                seq = X_tabular[i-CONFIG.lstm_sequence_length:i]
                sequences.append(seq)
                sequence_targets.append(y[i])
            
            if sequences:
                X_sequence = np.array(sequences)
                y_sequence = np.array(sequence_targets)
                logger.info(f"Created {len(sequences)} sequences for LSTM training")
        
        # Train ensemble
        tabular_data = (X_tabular, y)
        sequence_data = (X_sequence, y_sequence) if X_sequence is not None else None
        
        results = ensemble.train(tabular_data, sequence_data)
        results['status'] = 'training_completed'
        
        logger.info("Auto-fit completed successfully")
        return results
        
    except Exception as e:
        logger.error(f"Auto-fit failed: {e}")
        return {'status': 'error', 'message': str(e)}