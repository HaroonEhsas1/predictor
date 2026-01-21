#!/usr/bin/env python3
"""
Ensemble Model Improvements
Implements automatic weight redistribution, model fallbacks, and enhanced training
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class ImprovedEnsemble:
    """Enhanced ensemble with automatic fallbacks and weight redistribution"""
    
    def __init__(self):
        self.model_status = {}
        self.fallback_weights = {}
        self.performance_history = {}
        self.last_update = datetime.now()
        
    def predict_with_fallbacks(self, models: Dict, features: np.ndarray, 
                             model_weights: Dict[str, float]) -> Tuple[float, Dict[str, Any]]:
        """Make predictions with automatic fallbacks for failed models"""
        
        predictions = {}
        valid_predictions = []
        failed_models = []
        
        # Attempt predictions from all models
        for model_name, model in models.items():
            if model_name in model_weights:
                try:
                    # Ensure model is properly fitted
                    if not self._check_model_fitted(model, model_name):
                        failed_models.append(model_name)
                        continue
                        
                    pred = model.predict(features)[0]
                    predictions[model_name] = pred
                    valid_predictions.append((pred, model_weights[model_name]))
                    
                except Exception as e:
                    print(f"⚠️ {model_name} prediction failed: {e}")
                    failed_models.append(model_name)
        
        # Redistribute weights from failed models
        if failed_models:
            model_weights = self._redistribute_weights(model_weights, failed_models)
        
        # Calculate ensemble prediction
        if valid_predictions:
            ensemble_pred = self._calculate_weighted_ensemble(valid_predictions)
            consensus_score = self._calculate_consensus(predictions)
        else:
            # Complete fallback
            ensemble_pred = features[0, 0] if features.size > 0 else 180.0  # Price fallback
            consensus_score = 0.0
            
        results = {
            'prediction': ensemble_pred,
            'individual_predictions': predictions,
            'failed_models': failed_models,
            'consensus_score': consensus_score,
            'valid_model_count': len(valid_predictions),
            'redistributed_weights': model_weights
        }
        
        return ensemble_pred, results
    
    def _check_model_fitted(self, model: Any, model_name: str) -> bool:
        """Check if model is properly fitted"""
        try:
            # Common sklearn check
            if hasattr(model, '_sklearn_fitted'):
                return model._sklearn_fitted
            elif hasattr(model, 'tree_') and model.tree_ is not None:
                return True  # Random Forest
            elif hasattr(model, 'coef_') and model.coef_ is not None:
                return True  # Linear models
            elif hasattr(model, 'booster_') and model.booster_ is not None:
                return True  # LightGBM
            elif hasattr(model, 'feature_importances_') and model.feature_importances_ is not None:
                return True  # Tree-based models
            elif hasattr(model, 'predict') and callable(model.predict):
                # For neural networks, try a small test prediction
                try:
                    test_features = np.random.random((1, 10))
                    _ = model.predict(test_features)
                    return True
                except:
                    return False
            else:
                return False
                
        except Exception as e:
            print(f"⚠️ Model {model_name} fitness check failed: {e}")
            return False
    
    def _redistribute_weights(self, original_weights: Dict[str, float], 
                            failed_models: List[str]) -> Dict[str, float]:
        """Redistribute weights from failed models to working ones"""
        try:
            new_weights = original_weights.copy()
            
            # Calculate weight to redistribute
            failed_weight = sum(original_weights.get(model, 0) for model in failed_models)
            active_models = [m for m in original_weights.keys() if m not in failed_models]
            
            if active_models and failed_weight > 0:
                # Distribute failed weight proportionally among active models
                active_weight_sum = sum(original_weights.get(model, 0) for model in active_models)
                
                if active_weight_sum > 0:
                    for model in active_models:
                        current_weight = original_weights.get(model, 0)
                        weight_ratio = current_weight / active_weight_sum
                        additional_weight = failed_weight * weight_ratio
                        new_weights[model] = current_weight + additional_weight
            
            # Remove failed models
            for model in failed_models:
                new_weights[model] = 0.0
                
            # Normalize weights
            total_weight = sum(new_weights.values())
            if total_weight > 0:
                new_weights = {k: v/total_weight for k, v in new_weights.items()}
                
            return new_weights
            
        except Exception as e:
            print(f"⚠️ Weight redistribution error: {e}")
            return original_weights
    
    def _calculate_weighted_ensemble(self, valid_predictions: List[Tuple[float, float]]) -> float:
        """Calculate weighted ensemble prediction"""
        try:
            total_weight = sum(weight for _, weight in valid_predictions)
            if total_weight == 0:
                return np.mean([pred for pred, _ in valid_predictions])
            else:
                return sum(pred * weight for pred, weight in valid_predictions) / total_weight
        except Exception:
            # Simple average fallback
            return np.mean([pred for pred, _ in valid_predictions])
    
    def _calculate_consensus(self, predictions: Dict[str, float]) -> float:
        """Calculate consensus score (0-1) based on prediction agreement"""
        if len(predictions) < 2:
            return 0.0
        
        try:
            values = list(predictions.values())
            mean_pred = np.mean(values)
            
            if mean_pred == 0:
                return 0.5
                
            # Calculate coefficient of variation
            std_pred = np.std(values)
            cv = std_pred / abs(mean_pred)
            
            # Convert to consensus score (lower CV = higher consensus)
            consensus = max(0.0, 1.0 - cv)
            return consensus
            
        except Exception:
            return 0.5

def create_enhanced_training_system():
    """Create enhanced training system with comprehensive data handling"""
    
    class EnhancedTrainingSystem:
        def __init__(self):
            self.min_samples = 100
            self.validation_split = 0.2
            self.early_stopping_patience = 10
            
        def train_with_enhanced_features(self, models: Dict, features: np.ndarray, 
                                       targets: np.ndarray, enhanced_features: Dict[str, float]) -> Dict:
            """Train models with enhanced feature set"""
            
            results = {}
            
            # Add enhanced features to base features
            enhanced_array = self._incorporate_enhanced_features(features, enhanced_features)
            
            for model_name, model in models.items():
                try:
                    print(f"🔧 Training {model_name} with enhanced features...")
                    
                    # Train with enhanced features
                    model.fit(enhanced_array, targets)
                    
                    # Validate performance
                    train_pred = model.predict(enhanced_array)
                    mae = np.mean(np.abs(targets - train_pred))
                    
                    results[model_name] = {
                        'mae': mae,
                        'trained': True,
                        'features_used': enhanced_array.shape[1],
                        'samples_used': len(targets)
                    }
                    
                    print(f"✅ {model_name} trained - MAE: {mae:.4f}, Features: {enhanced_array.shape[1]}")
                    
                except Exception as e:
                    print(f"❌ {model_name} training failed: {e}")
                    results[model_name] = {
                        'error': str(e),
                        'trained': False
                    }
                    
            return results
        
        def _incorporate_enhanced_features(self, base_features: np.ndarray, 
                                         enhanced_features: Dict[str, float]) -> np.ndarray:
            """Incorporate enhanced features into base feature matrix"""
            try:
                # Convert enhanced features to array
                enhanced_values = list(enhanced_features.values())
                enhanced_array = np.array(enhanced_values).reshape(1, -1)
                
                # Combine with base features
                if base_features.shape[0] == enhanced_array.shape[0]:
                    combined = np.concatenate([base_features, enhanced_array], axis=1)
                else:
                    # If dimensions don't match, repeat enhanced features
                    enhanced_repeated = np.repeat(enhanced_array, base_features.shape[0], axis=0)
                    combined = np.concatenate([base_features, enhanced_repeated], axis=1)
                    
                return combined
                
            except Exception as e:
                print(f"⚠️ Feature incorporation error: {e}")
                return base_features
    
    return EnhancedTrainingSystem()

def implement_confidence_scaling(base_confidence: float, ml_consensus: float, 
                               historical_accuracy: float, additional_factors: Dict[str, float]) -> Dict[str, float]:
    """Implement advanced confidence scaling system"""
    
    try:
        # Base confidence adjustment
        adjusted_confidence = base_confidence
        
        # ML consensus adjustment
        consensus_weight = 0.3
        adjusted_confidence = adjusted_confidence * (1 + (ml_consensus - 0.5) * consensus_weight)
        
        # Historical accuracy adjustment  
        accuracy_weight = 0.2
        if historical_accuracy > 0:
            accuracy_factor = (historical_accuracy - 0.5) * accuracy_weight
            adjusted_confidence = adjusted_confidence * (1 + accuracy_factor)
        
        # Additional factors
        for factor_name, factor_value in additional_factors.items():
            if factor_name == 'technical_confluence':
                adjusted_confidence += factor_value * 5  # Up to 5% boost
            elif factor_name == 'volume_confirmation':
                adjusted_confidence += factor_value * 3  # Up to 3% boost
            elif factor_name == 'news_sentiment':
                adjusted_confidence += abs(factor_value) * 2  # Up to 2% boost
        
        # Ensure confidence stays within reasonable bounds
        final_confidence = max(0, min(100, adjusted_confidence))
        
        # Calculate position scaling
        if final_confidence >= 80:
            position_scale = 1.0
            trade_recommendation = "FULL_POSITION"
        elif final_confidence >= 65:
            position_scale = 0.7
            trade_recommendation = "PARTIAL_POSITION"
        elif final_confidence >= 50:
            position_scale = 0.4
            trade_recommendation = "SMALL_POSITION"
        else:
            position_scale = 0.1
            trade_recommendation = "MINIMAL_POSITION"
        
        return {
            'original_confidence': base_confidence,
            'adjusted_confidence': final_confidence,
            'ml_consensus_factor': ml_consensus,
            'historical_accuracy_factor': historical_accuracy,
            'position_scale': position_scale,
            'trade_recommendation': trade_recommendation,
            'confidence_grade': 'A' if final_confidence >= 80 else 'B' if final_confidence >= 65 else 'C'
        }
        
    except Exception as e:
        print(f"⚠️ Confidence scaling error: {e}")
        return {
            'original_confidence': base_confidence,
            'adjusted_confidence': base_confidence,
            'ml_consensus_factor': ml_consensus,
            'historical_accuracy_factor': historical_accuracy,
            'position_scale': 0.1,
            'trade_recommendation': "MINIMAL_POSITION",
            'confidence_grade': 'D'
        }

def create_data_fallback_system():
    """Create comprehensive data fallback and market closed handling"""
    
    class DataFallbackSystem:
        def __init__(self):
            self.fallback_data_sources = ['yahoo', 'alpha_vantage', 'polygon']
            self.collect_only_mode = False
            
        def handle_market_closed_data_collection(self, symbol: str) -> Dict[str, Any]:
            """Handle data collection when market is closed"""
            
            print("📊 Market closed - entering collect-only mode")
            
            return {
                'mode': 'collect_only',
                'trading_enabled': False,
                'data_collection_active': True,
                'prediction_type': 'next_day_planning',
                'confidence_override': 0.0,
                'message': 'Market closed - analyzing data for next trading session'
            }
        
        def handle_missing_intraday_data(self, symbol: str) -> Dict[str, Any]:
            """Handle missing or delisted stock data"""
            
            fallback_strategies = [
                'use_daily_data_with_interpolation',
                'use_sector_proxy_data', 
                'use_historical_pattern_matching',
                'use_synthetic_data_generation'
            ]
            
            print(f"⚠️ {symbol} intraday data missing - implementing fallbacks")
            
            return {
                'data_available': False,
                'fallback_strategies': fallback_strategies,
                'use_sector_correlation': True,
                'prediction_reliability': 'LOW',
                'recommended_action': 'SKIP_TRADING'
            }
        
        def validate_data_quality(self, data: pd.DataFrame) -> Dict[str, Any]:
            """Validate data quality and completeness"""
            
            quality_scores = {}
            
            # Check data completeness
            if not data.empty:
                completeness = (len(data.dropna()) / len(data)) * 100
                quality_scores['completeness'] = completeness
                
                # Check data freshness (last update time)
                if 'timestamp' in data.columns:
                    last_update = pd.to_datetime(data['timestamp'].iloc[-1])
                    freshness_minutes = (datetime.now() - last_update).total_seconds() / 60
                    quality_scores['freshness_minutes'] = freshness_minutes
                
                # Check for price anomalies
                if 'Close' in data.columns:
                    price_changes = data['Close'].pct_change().abs()
                    max_change = price_changes.max()
                    quality_scores['max_price_change'] = max_change
                    
                    # Flag unusual price movements
                    if max_change > 0.1:  # 10% single-period change
                        quality_scores['price_anomaly'] = True
                    else:
                        quality_scores['price_anomaly'] = False
            
            overall_quality = 'HIGH' if quality_scores.get('completeness', 0) > 95 else 'MEDIUM' if quality_scores.get('completeness', 0) > 80 else 'LOW'
            
            return {
                'overall_quality': overall_quality,
                'quality_scores': quality_scores,
                'data_usable': overall_quality in ['HIGH', 'MEDIUM'],
                'recommendations': self._get_quality_recommendations(quality_scores)
            }
        
        def _get_quality_recommendations(self, quality_scores: Dict) -> List[str]:
            """Get recommendations based on data quality"""
            recommendations = []
            
            if quality_scores.get('completeness', 100) < 90:
                recommendations.append('Use data interpolation for missing values')
            
            if quality_scores.get('freshness_minutes', 0) > 10:
                recommendations.append('Data is stale - reduce prediction confidence')
            
            if quality_scores.get('price_anomaly', False):
                recommendations.append('Price anomaly detected - verify data source')
            
            if not recommendations:
                recommendations.append('Data quality is acceptable for trading')
                
            return recommendations
    
    return DataFallbackSystem()