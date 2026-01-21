"""
Professional ML models for next-day predictions with institutional validation
Implements proper cross-validation, calibration, and ensemble methods
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any, Union
import logging
import joblib
import os
from datetime import datetime
import warnings
from sklearn.model_selection import TimeSeriesSplit, GridSearchCV, RandomizedSearchCV
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor, VotingRegressor, BaggingRegressor, AdaBoostRegressor, StackingRegressor, ExtraTreesRegressor
from sklearn.linear_model import Ridge, ElasticNet, Lasso
from sklearn.metrics import mean_squared_error, mean_absolute_error, accuracy_score, r2_score
from sklearn.isotonic import IsotonicRegression
from sklearn.inspection import permutation_importance
import json

# TensorFlow/Keras for LSTM/GRU models
try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import LSTM, GRU, Dense, Dropout, Bidirectional
    from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
    from tensorflow.keras.optimizers import Adam
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("TensorFlow not available - LSTM/GRU models will be disabled")

# Import StackingMetaLearner for enhanced accuracy
try:
    from models.stacking_meta_learner import StackingMetaLearner
    STACKING_AVAILABLE = True
except ImportError:
    try:
        import sys
        sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        from models.stacking_meta_learner import StackingMetaLearner
        STACKING_AVAILABLE = True
    except ImportError:
        STACKING_AVAILABLE = False
        logger.warning("StackingMetaLearner not available - using basic ensemble")

try:
    from .config import CONFIG, get_model_version
    from .features import NextDayFeatureEngine
except ImportError:
    try:
        from engines.nextday.config import CONFIG, get_model_version
        from engines.nextday.features import NextDayFeatureEngine
    except ImportError:
        from config import CONFIG, get_model_version
        from features import NextDayFeatureEngine

logger = logging.getLogger(__name__)

class NextDayModelEngine:
    """
    Professional ML ensemble for next-day gap predictions
    Implements institutional best practices for model validation
    """
    
    def __init__(self, use_stacking: bool = True):
        self.models = {}
        self.calibrator = None
        self.feature_engine = NextDayFeatureEngine()
        self.performance_history = {}
        self.ensemble_weights = None
        self.use_stacking = use_stacking and STACKING_AVAILABLE
        
        # Initialize StackingMetaLearner for enhanced accuracy
        self.stacking_model = None
        if self.use_stacking:
            try:
                self.stacking_model = StackingMetaLearner(task='regression', n_splits=5)
                logger.info("StackingMetaLearner initialized - ENHANCED ACCURACY MODE")
            except Exception as e:
                logger.warning(f"Stacking initialization failed: {e}")
                self.use_stacking = False
        
        # Model configurations
        self.model_configs = {
            'gradient_boosting': {
                'class': GradientBoostingRegressor,
                'params': {
                    'n_estimators': 100,
                    'learning_rate': 0.1,
                    'max_depth': 4,
                    'random_state': 42,
                    'loss': 'huber'
                }
            },
            'random_forest': {
                'class': RandomForestRegressor,
                'params': {
                    'n_estimators': 100,
                    'max_depth': 6,
                    'random_state': 42,
                    'n_jobs': -1
                }
            },
            'ridge': {
                'class': Ridge,
                'params': {
                    'alpha': 1.0,
                    'random_state': 42
                }
            },
            # FREE UPGRADE: Advanced Ensemble Methods
            'elastic_net': {
                'class': ElasticNet,
                'params': {
                    'alpha': 1.0,
                    'l1_ratio': 0.5,  # Mix of L1 and L2
                    'random_state': 42
                }
            },
            'bagging_regressor': {
                'class': BaggingRegressor,
                'params': {
                    'n_estimators': 50,
                    'random_state': 42,
                    'n_jobs': -1
                }
            },
            'adaboost_regressor': {
                'class': AdaBoostRegressor,
                'params': {
                    'n_estimators': 50,
                    'learning_rate': 1.0,
                    'random_state': 42
                }
            },
            'extra_trees': {
                'class': ExtraTreesRegressor,
                'params': {
                    'n_estimators': 100,
                    'max_depth': 6,
                    'random_state': 42,
                    'n_jobs': -1
                }
            }
        }
        
        # Deep Learning model (LSTM/GRU)
        self.lstm_model = None
        self.use_deep_learning = TF_AVAILABLE
    
    def train_models(self, features_df: pd.DataFrame, save_artifacts: bool = True) -> Dict[str, Any]:
        """
        Train ensemble models with proper validation
        
        Args:
            features_df: DataFrame with features and target
            save_artifacts: Whether to save trained models
            
        Returns:
            Training results and validation metrics
        """
        
        logger.info("Training next-day prediction models...")
        
        # Prepare data
        X, y = self._prepare_training_data(features_df)
        
        if len(X) < 15:
            raise ValueError(f"Insufficient training data: {len(X)} samples < 15 minimum")
        
        # Time series cross-validation with purging
        cv_results = self._cross_validate_models(X, y)
        
        # Train final models on full dataset
        self._train_final_models(X, y)
        
        # Fit probability calibrator
        self._fit_calibrator(X, y)
        
        # Compute ensemble weights
        self._compute_ensemble_weights(cv_results)
        
        # Save artifacts if requested
        if save_artifacts:
            self._save_model_artifacts()
        
        training_results = {
            'cv_results': cv_results,
            'n_samples': len(X),
            'n_features': X.shape[1],
            'ensemble_weights': self.ensemble_weights,
            'model_version': get_model_version()
        }
        
        logger.info(f"Training completed: {len(self.models)} models trained on {len(X)} samples")
        return training_results
    
    def load_models(self, model_version: Optional[str] = None) -> bool:
        """
        Load pre-trained models from disk
        
        Args:
            model_version: Specific version to load (latest if None)
            
        Returns:
            Success status
        """
        
        try:
            if model_version is None:
                model_version = self._get_latest_model_version()
            
            if model_version is None:
                logger.warning("No trained models found")
                return False
            
            models_loaded = 0
            
            # Load individual models
            for model_name in self.model_configs.keys():
                model_path = os.path.join(CONFIG.models_path, f"{model_name}_v{model_version}.pkl")
                if os.path.exists(model_path):
                    self.models[model_name] = joblib.load(model_path)
                    models_loaded += 1
                    logger.info(f"Loaded {model_name} from {model_path}")
            
            # Load feature engine (scaler)
            scaler_path = os.path.join(CONFIG.models_path, f"scaler_v{model_version}.pkl")
            if os.path.exists(scaler_path):
                self.feature_engine.scaler = joblib.load(scaler_path)
                logger.info(f"Loaded scaler from {scaler_path}")
            
            # Load calibrator
            calibrator_path = os.path.join(CONFIG.models_path, f"calibrator_v{model_version}.pkl")
            if os.path.exists(calibrator_path):
                self.calibrator = joblib.load(calibrator_path)
                logger.info(f"Loaded calibrator from {calibrator_path}")
            
            # Load ensemble weights
            weights_path = os.path.join(CONFIG.models_path, f"ensemble_weights_v{model_version}.json")
            if os.path.exists(weights_path):
                with open(weights_path, 'r') as f:
                    self.ensemble_weights = json.load(f)
                logger.info(f"Loaded ensemble weights from {weights_path}")
            
            if models_loaded > 0:
                logger.info(f"Successfully loaded {models_loaded} models (version {model_version})")
                return True
            else:
                logger.warning("No models could be loaded")
                return False
                
        except Exception as e:
            logger.error(f"Failed to load models: {e}")
            return False
    
    def predict(self, features_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate ensemble prediction with calibrated probabilities
        
        Args:
            features_df: DataFrame with features for prediction
            
        Returns:
            Prediction results with confidence and direction
        """
        
        if not self.models:
            logger.error("No models loaded for prediction")
            return {'direction': 'SKIP', 'confidence': 0.0, 'reason': 'No trained models available'}
        
        try:
            # Transform features
            if self.feature_engine.scaler is None:
                logger.error("Feature scaler not available")
                return {'direction': 'SKIP', 'confidence': 0.0, 'reason': 'Feature scaler not fitted'}
            
            X = self.feature_engine.transform_features(features_df)
            
            if len(X) == 0:
                return {'direction': 'SKIP', 'confidence': 0.0, 'reason': 'No valid features'}
            
            # Get predictions from each model
            model_predictions = {}
            for model_name, model in self.models.items():
                try:
                    pred = model.predict(X[-1:])  # Predict on latest sample
                    model_predictions[model_name] = float(pred[0])
                except Exception as e:
                    logger.warning(f"Prediction failed for {model_name}: {e}")
                    model_predictions[model_name] = 0.0
            
            # Add LSTM/GRU prediction if available
            if self.lstm_model is not None:
                try:
                    X_seq = X[-1:].reshape(1, 1, X.shape[1])
                    lstm_pred = self.lstm_model.predict(X_seq, verbose=0)
                    model_predictions['lstm_gru'] = float(lstm_pred[0][0])
                except Exception as e:
                    logger.warning(f"LSTM prediction failed: {e}")
            
            # Ensemble prediction - use StackingMetaLearner if available
            if self.use_stacking and self.stacking_model is not None and hasattr(self.stacking_model, 'is_fitted') and self.stacking_model.is_fitted:
                try:
                    # Use stacking model for enhanced accuracy
                    stacking_pred = self.stacking_model.predict(X[-1:])[0]
                    
                    # Blend with traditional ensemble for robustness (70% stacking, 30% traditional)
                    traditional_ensemble = self._compute_ensemble_prediction(model_predictions)
                    ensemble_pred = 0.7 * stacking_pred + 0.3 * traditional_ensemble
                    
                    logger.info(f"🎯 Using StackingMetaLearner: {stacking_pred:.4f}")
                except Exception as e:
                    logger.warning(f"Stacking prediction failed: {e}")
                    ensemble_pred = self._compute_ensemble_prediction(model_predictions)
            else:
                ensemble_pred = self._compute_ensemble_prediction(model_predictions)
            
            # Convert to direction and confidence
            direction, confidence = self._convert_to_signal(ensemble_pred)
            
            # Get current price for expected open calculation - fix timestamp bug
            if 'price' in features_df.columns:
                current_price = float(features_df['price'].iloc[-1])
            elif 'amd_close' in features_df.columns:
                current_price = float(features_df['amd_close'].iloc[-1])
            else:
                logger.warning("No current price available in features")
                return {'direction': 'SKIP', 'confidence': 0.0, 'reason': 'No current price available'}
            
            expected_open = current_price * (1 + ensemble_pred)
            
            result = {
                'direction': direction,
                'confidence': confidence,
                'predicted_gap_pct': ensemble_pred,
                'expected_open': expected_open,
                'current_price': current_price,
                'model_predictions': model_predictions,
                'ensemble_weights': self.ensemble_weights,
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"Prediction: {direction} ({confidence:.1%} confidence, {ensemble_pred:+.3f} gap)")
            return result
            
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            return {'direction': 'SKIP', 'confidence': 0.0, 'reason': f'Prediction error: {str(e)}'}
    
    def _prepare_training_data(self, features_df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare features and target for training"""
        
        # Remove rows with missing target
        clean_df = features_df.dropna(subset=['target_gap_pct'])
        
        # Prepare features
        feature_columns = [col for col in self.feature_engine.feature_names if col in clean_df.columns]
        X = clean_df[feature_columns].values
        
        # Prepare target
        y = clean_df['target_gap_pct'].values
        
        # Fit scaler on training data
        self.feature_engine.fit_scaler(clean_df)
        
        # Transform features using feature engine method
        X = self.feature_engine.transform_features(clean_df)
        
        logger.info(f"Prepared training data: {X.shape[0]} samples, {X.shape[1]} features")
        return X, y
    
    def _cross_validate_models(self, X: np.ndarray, y: np.ndarray) -> Dict[str, Dict[str, float]]:
        """Perform time series cross-validation with purging"""
        
        # Time series split with gap (purging)
        tscv = TimeSeriesSplit(n_splits=CONFIG.cv_folds, gap=CONFIG.purge_days)
        
        cv_results = {}
        
        for model_name, model_config in self.model_configs.items():
            logger.info(f"Cross-validating {model_name}...")
            
            model_class = model_config['class']
            model_params = model_config['params']
            
            fold_results = []
            
            for fold, (train_idx, val_idx) in enumerate(tscv.split(X)):
                # Train model
                model = model_class(**model_params)
                model.fit(X[train_idx], y[train_idx])
                
                # Validate
                val_pred = model.predict(X[val_idx])
                
                # Compute metrics
                mse = mean_squared_error(y[val_idx], val_pred)
                mae = mean_absolute_error(y[val_idx], val_pred)
                
                # Direction accuracy
                actual_direction = np.sign(y[val_idx])
                pred_direction = np.sign(val_pred)
                direction_acc = accuracy_score(actual_direction, pred_direction)
                
                fold_results.append({
                    'mse': mse,
                    'mae': mae,
                    'direction_accuracy': direction_acc,
                    'n_samples': len(val_idx)
                })
            
            # Aggregate results
            cv_results[model_name] = {
                'mean_mse': np.mean([r['mse'] for r in fold_results]),
                'mean_mae': np.mean([r['mae'] for r in fold_results]),
                'mean_direction_accuracy': np.mean([r['direction_accuracy'] for r in fold_results]),
                'std_mse': np.std([r['mse'] for r in fold_results]),
                'fold_results': fold_results
            }
            
            logger.info(f"{model_name} CV: MAE={cv_results[model_name]['mean_mae']:.4f}, "
                       f"Direction Acc={cv_results[model_name]['mean_direction_accuracy']:.3f}")
        
        return cv_results
    
    def _train_final_models(self, X: np.ndarray, y: np.ndarray) -> None:
        """Train final models on full dataset"""
        
        for model_name, model_config in self.model_configs.items():
            logger.info(f"Training final {model_name} model...")
            
            model_class = model_config['class']
            model_params = model_config['params']
            
            model = model_class(**model_params)
            model.fit(X, y)
            
            self.models[model_name] = model
        
        # Train LSTM/GRU model if TensorFlow is available
        if self.use_deep_learning:
            self._train_lstm_model(X, y)
        
        # Train StackingMetaLearner for enhanced accuracy
        if self.use_stacking and self.stacking_model is not None and STACKING_AVAILABLE:
            try:
                logger.info("Training StackingMetaLearner...")
                stacking_metrics = self.stacking_model.fit(X, y)
                logger.info(f"StackingMetaLearner trained - Accuracy: {stacking_metrics.get('r2', 0):.3f}")
            except Exception as e:
                logger.warning(f"Stacking training failed: {e}")
                self.use_stacking = False
    
    def _build_lstm_model(self, input_shape: Tuple[int, int]) -> Any:
        """
        Build LSTM/GRU deep learning model for time series prediction
        
        Args:
            input_shape: (sequence_length, n_features)
            
        Returns:
            Compiled Keras model
        """
        
        if not TF_AVAILABLE:
            logger.warning("TensorFlow not available - cannot build LSTM model")
            return None
        
        model = Sequential([
            # Bidirectional LSTM layer for capturing patterns in both directions
            Bidirectional(LSTM(64, return_sequences=True, input_shape=input_shape)),
            Dropout(0.2),
            
            # GRU layer for faster training
            GRU(32, return_sequences=False),
            Dropout(0.2),
            
            # Dense layers for regression
            Dense(16, activation='relu'),
            Dropout(0.1),
            Dense(1, activation='linear')  # Regression output
        ])
        
        # Compile with Adam optimizer and mean squared error
        model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='mse',
            metrics=['mae']
        )
        
        return model
    
    def _train_lstm_model(self, X: np.ndarray, y: np.ndarray) -> None:
        """Train LSTM/GRU model with time series data"""
        
        if not TF_AVAILABLE:
            return
        
        try:
            # Reshape data for LSTM (samples, time_steps, features)
            # Use last 10 features as sequence
            sequence_length = min(10, X.shape[1])
            n_samples = X.shape[0]
            
            # Create sequences
            X_seq = X.reshape(n_samples, 1, X.shape[1])  # Simple reshape for now
            
            # Build model
            self.lstm_model = self._build_lstm_model((1, X.shape[1]))
            
            # Training callbacks
            early_stop = EarlyStopping(
                monitor='loss',
                patience=10,
                restore_best_weights=True,
                verbose=0
            )
            
            reduce_lr = ReduceLROnPlateau(
                monitor='loss',
                factor=0.5,
                patience=5,
                min_lr=1e-6,
                verbose=0
            )
            
            # Train model with validation split
            history = self.lstm_model.fit(
                X_seq, y,
                epochs=100,
                batch_size=16,
                validation_split=0.2,
                callbacks=[early_stop, reduce_lr],
                verbose=0
            )
            
            logger.info(f"LSTM model trained - final loss: {history.history['loss'][-1]:.4f}")
            
        except Exception as e:
            logger.warning(f"LSTM model training failed: {e}")
            self.lstm_model = None
    
    def _fit_calibrator(self, X: np.ndarray, y: np.ndarray) -> None:
        """Fit probability calibrator using ensemble predictions"""
        
        try:
            # Get ensemble predictions on training data
            ensemble_preds = []
            for i in range(len(X)):
                model_preds = {}
                for model_name, model in self.models.items():
                    pred = model.predict(X[i:i+1])
                    model_preds[model_name] = float(pred[0])
                
                ensemble_pred = np.mean(list(model_preds.values()))
                ensemble_preds.append(ensemble_pred)
            
            ensemble_preds = np.array(ensemble_preds)
            
            # Convert to binary classification (up/down)
            y_binary = (y > 0).astype(int)
            
            # Fit isotonic regression for calibration
            self.calibrator = IsotonicRegression(out_of_bounds='clip')
            self.calibrator.fit(ensemble_preds, y_binary)
            
            logger.info("Fitted probability calibrator")
            
        except Exception as e:
            logger.warning(f"Calibrator fitting failed: {e}")
            self.calibrator = None
    
    def _compute_ensemble_weights(self, cv_results: Dict[str, Dict[str, float]]) -> None:
        """Compute ensemble weights based on cross-validation performance"""
        
        # Use inverse of MAE as weights (better models get higher weight)
        weights = {}
        total_inv_mae = 0
        
        for model_name, results in cv_results.items():
            inv_mae = 1.0 / (results['mean_mae'] + 1e-6)
            weights[model_name] = inv_mae
            total_inv_mae += inv_mae
        
        # Normalize weights
        for model_name in weights:
            weights[model_name] /= total_inv_mae
        
        self.ensemble_weights = weights
        logger.info(f"Computed ensemble weights: {weights}")
    
    def _compute_ensemble_prediction(self, model_predictions: Dict[str, float]) -> float:
        """Compute weighted ensemble prediction"""
        
        if self.ensemble_weights is None:
            # Equal weights if no weights computed
            weights = {name: 1.0/len(model_predictions) for name in model_predictions}
        else:
            weights = self.ensemble_weights
        
        ensemble_pred = 0.0
        total_weight = 0.0
        
        for model_name, pred in model_predictions.items():
            weight = weights.get(model_name, 0.0)
            ensemble_pred += pred * weight
            total_weight += weight
        
        if total_weight > 0:
            ensemble_pred /= total_weight
        
        return ensemble_pred
    
    def _convert_to_signal(self, predicted_gap: float) -> Tuple[str, float]:
        """Convert regression output to trading signal with confidence"""
        
        # Determine direction
        if predicted_gap > 0:
            direction = 'UP'
        elif predicted_gap < 0:
            direction = 'DOWN'
        else:
            direction = 'SKIP'
        
        # Compute confidence using calibrator
        if self.calibrator is not None:
            try:
                calibrated_prob = self.calibrator.predict([abs(predicted_gap)])[0]
                confidence = float(calibrated_prob)
            except:
                # Fallback confidence based on magnitude
                confidence = min(abs(predicted_gap) * 10, 1.0)
        else:
            # Simple confidence based on magnitude
            confidence = min(abs(predicted_gap) * 10, 1.0)
        
        return direction, confidence
    
    def _save_model_artifacts(self) -> None:
        """Save all model artifacts with versioning"""
        
        version = get_model_version()
        
        try:
            # Save individual models
            for model_name, model in self.models.items():
                model_path = os.path.join(CONFIG.models_path, f"{model_name}_v{version}.pkl")
                joblib.dump(model, model_path)
                logger.info(f"Saved {model_name} to {model_path}")
            
            # Save scaler
            if self.feature_engine.scaler is not None:
                scaler_path = os.path.join(CONFIG.models_path, f"scaler_v{version}.pkl")
                joblib.dump(self.feature_engine.scaler, scaler_path)
                logger.info(f"Saved scaler to {scaler_path}")
            
            # Save calibrator
            if self.calibrator is not None:
                calibrator_path = os.path.join(CONFIG.models_path, f"calibrator_v{version}.pkl")
                joblib.dump(self.calibrator, calibrator_path)
                logger.info(f"Saved calibrator to {calibrator_path}")
            
            # Save ensemble weights
            if self.ensemble_weights is not None:
                weights_path = os.path.join(CONFIG.models_path, f"ensemble_weights_v{version}.json")
                with open(weights_path, 'w') as f:
                    json.dump(self.ensemble_weights, f, indent=2)
                logger.info(f"Saved ensemble weights to {weights_path}")
            
        except Exception as e:
            logger.error(f"Failed to save model artifacts: {e}")
    
    def _get_latest_model_version(self) -> Optional[str]:
        """Get the latest model version from saved files"""
        
        try:
            model_files = [f for f in os.listdir(CONFIG.models_path) if f.endswith('.pkl')]
            if not model_files:
                return None
            
            # Extract versions from filenames
            versions = set()
            for filename in model_files:
                if '_v' in filename:
                    version = filename.split('_v')[1].split('.')[0]
                    versions.add(version)
            
            if versions:
                return max(versions)  # Latest version (alphabetically)
            else:
                return None
                
        except Exception as e:
            logger.error(f"Failed to get latest model version: {e}")
            return None
    
    def optimize_hyperparameters(self, X: np.ndarray, y: np.ndarray, model_name: str, param_grid: Dict) -> Dict:
        """
        Optimize hyperparameters using GridSearchCV with time series validation
        
        Args:
            X: Feature matrix
            y: Target vector
            model_name: Name of model to optimize
            param_grid: Dictionary of parameters to search
            
        Returns:
            Best parameters and scores
        """
        
        if model_name not in self.model_configs:
            logger.error(f"Unknown model: {model_name}")
            return {}
        
        try:
            model_class = self.model_configs[model_name]['class']
            base_model = model_class()
            
            # Time series cross-validation
            tscv = TimeSeriesSplit(n_splits=5)
            
            # Grid search
            grid_search = GridSearchCV(
                base_model,
                param_grid,
                cv=tscv,
                scoring='neg_mean_squared_error',
                n_jobs=-1,
                verbose=1
            )
            
            grid_search.fit(X, y)
            
            logger.info(f"Best params for {model_name}: {grid_search.best_params_}")
            logger.info(f"Best CV score: {-grid_search.best_score_:.4f}")
            
            return {
                'best_params': grid_search.best_params_,
                'best_score': -grid_search.best_score_,
                'cv_results': grid_search.cv_results_
            }
            
        except Exception as e:
            logger.error(f"Hyperparameter optimization failed for {model_name}: {e}")
            return {}
    
    def compute_feature_importance(self, X: np.ndarray, y: np.ndarray, model_name: str = None) -> Dict[str, float]:
        """
        Compute permutation feature importance for interpretability
        
        Args:
            X: Feature matrix
            y: Target vector
            model_name: Specific model to use (uses ensemble if None)
            
        Returns:
            Dictionary of feature importances
        """
        
        if model_name and model_name not in self.models:
            logger.error(f"Model {model_name} not trained")
            return {}
        
        try:
            # Select model
            model = self.models[model_name] if model_name else self.models.get('gradient_boosting')
            
            if model is None:
                logger.error("No model available for feature importance")
                return {}
            
            # Compute permutation importance
            result = permutation_importance(
                model, X, y,
                n_repeats=10,
                random_state=42,
                n_jobs=-1
            )
            
            # Create importance dictionary
            feature_names = self.feature_engine.feature_names
            if len(feature_names) != X.shape[1]:
                feature_names = [f"feature_{i}" for i in range(X.shape[1])]
            
            importance_dict = {
                feature_names[i]: result.importances_mean[i]
                for i in range(len(feature_names))
            }
            
            # Sort by importance
            importance_dict = dict(sorted(importance_dict.items(), key=lambda x: x[1], reverse=True))
            
            # Log top features
            logger.info("Top 10 most important features:")
            for i, (feature, importance) in enumerate(list(importance_dict.items())[:10]):
                logger.info(f"{i+1}. {feature}: {importance:.4f}")
            
            return importance_dict
            
        except Exception as e:
            logger.error(f"Feature importance computation failed: {e}")
            return {}
    
    def get_model_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive summary of the ensemble system
        
        Returns:
            Dictionary with model counts, types, and status
        """
        
        summary = {
            'total_models': len(self.models),
            'sklearn_models': list(self.models.keys()),
            'deep_learning': self.lstm_model is not None,
            'calibrator_fitted': self.calibrator is not None,
            'ensemble_weights': self.ensemble_weights,
            'tensorflow_available': TF_AVAILABLE
        }
        
        return summary

# Export main class
__all__ = ['NextDayModelEngine']