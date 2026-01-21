"""
Feature Importance Analysis (FREE)
Alternative to SHAP using scikit-learn built-in methods
No hardcoded values - calculates from real model data
"""

import numpy as np
import logging
from typing import Dict, List, Optional, Tuple, Any
from sklearn.inspection import permutation_importance
import pandas as pd

logger = logging.getLogger(__name__)

class FeatureImportanceAnalyzer:
    """
    Model-agnostic feature importance analysis
    Uses sklearn's permutation importance and model-specific methods
    """
    
    def __init__(self):
        self.feature_importance_history = []
        logger.info("✅ Feature importance analyzer initialized")
    
    def get_tree_feature_importance(self, model, feature_names: List[str]) -> Dict[str, float]:
        """
        Get feature importance from tree-based models
        Works with: RandomForest, GradientBoosting, XGBoost, LightGBM, CatBoost
        """
        try:
            # Check if model has feature_importances_ attribute
            if hasattr(model, 'feature_importances_'):
                importances = model.feature_importances_
                
                # Create importance dict
                importance_dict = {}
                for name, importance in zip(feature_names, importances):
                    importance_dict[name] = float(importance)
                
                return importance_dict
            else:
                logger.warning(f"Model {type(model).__name__} doesn't have feature_importances_")
                return {}
                
        except Exception as e:
            logger.error(f"Failed to extract tree feature importance: {e}")
            return {}
    
    def get_linear_feature_importance(self, model, feature_names: List[str]) -> Dict[str, float]:
        """
        Get feature importance from linear models
        Uses absolute coefficient values
        Works with: Ridge, Lasso, ElasticNet, LogisticRegression
        """
        try:
            # Check if model has coef_ attribute
            if hasattr(model, 'coef_'):
                coefficients = model.coef_
                
                # Handle multi-output
                if len(coefficients.shape) > 1:
                    coefficients = coefficients[0]
                
                # Use absolute values for importance
                importances = np.abs(coefficients)
                
                # Normalize to sum to 1
                total = np.sum(importances)
                if total > 0:
                    importances = importances / total
                
                # Create importance dict
                importance_dict = {}
                for name, importance in zip(feature_names, importances):
                    importance_dict[name] = float(importance)
                
                return importance_dict
            else:
                logger.warning(f"Model {type(model).__name__} doesn't have coef_")
                return {}
                
        except Exception as e:
            logger.error(f"Failed to extract linear feature importance: {e}")
            return {}
    
    def get_permutation_importance(
        self, 
        model, 
        X: np.ndarray, 
        y: np.ndarray,
        feature_names: List[str],
        n_repeats: int = 10,
        random_state: int = 42
    ) -> Dict[str, float]:
        """
        Calculate permutation importance (model-agnostic)
        More reliable than built-in importances for some models
        """
        try:
            # Calculate permutation importance
            result = permutation_importance(
                model, X, y,
                n_repeats=n_repeats,
                random_state=random_state,
                n_jobs=-1
            )
            
            # Get mean importances
            importances = result.importances_mean
            
            # Create importance dict
            importance_dict = {}
            for name, importance in zip(feature_names, importances):
                importance_dict[name] = float(importance)
            
            return importance_dict
            
        except Exception as e:
            logger.error(f"Failed to calculate permutation importance: {e}")
            return {}
    
    def get_ensemble_feature_importance(
        self,
        models: Dict[str, Any],
        feature_names: List[str],
        X: Optional[np.ndarray] = None,
        y: Optional[np.ndarray] = None
    ) -> Dict[str, Dict[str, float]]:
        """
        Get feature importance from ensemble of models
        Aggregates importance across all models
        """
        all_importances = {}
        
        for model_name, model in models.items():
            # Try tree-based importance first
            importance = self.get_tree_feature_importance(model, feature_names)
            
            # If that fails, try linear
            if not importance:
                importance = self.get_linear_feature_importance(model, feature_names)
            
            # If that fails and we have data, use permutation
            if not importance and X is not None and y is not None:
                try:
                    importance = self.get_permutation_importance(
                        model, X, y, feature_names, n_repeats=5
                    )
                except:
                    pass
            
            if importance:
                all_importances[model_name] = importance
        
        return all_importances
    
    def aggregate_importance(self, importance_dict: Dict[str, Dict[str, float]]) -> Dict[str, float]:
        """
        Aggregate feature importance across multiple models
        Returns average importance for each feature
        """
        if not importance_dict:
            return {}
        
        # Collect all feature importances
        feature_values = {}
        
        for model_importances in importance_dict.values():
            for feature, importance in model_importances.items():
                if feature not in feature_values:
                    feature_values[feature] = []
                feature_values[feature].append(importance)
        
        # Calculate average for each feature
        avg_importance = {}
        for feature, values in feature_values.items():
            avg_importance[feature] = float(np.mean(values))
        
        return avg_importance
    
    def get_top_features(
        self,
        importance_dict: Dict[str, float],
        top_n: int = 20
    ) -> List[Tuple[str, float]]:
        """
        Get top N most important features
        Returns sorted list of (feature_name, importance) tuples
        """
        sorted_features = sorted(
            importance_dict.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return sorted_features[:top_n]
    
    def detect_feature_bias(
        self,
        importance_dict: Dict[str, float],
        directional_keywords: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Detect if features have directional bias
        Check if importance is concentrated in bullish or bearish features
        """
        if directional_keywords is None:
            directional_keywords = ['bull', 'bear', 'buy', 'sell', 'up', 'down']
        
        # Separate features by potential directional bias
        potentially_biased = []
        
        for feature, importance in importance_dict.items():
            feature_lower = feature.lower()
            for keyword in directional_keywords:
                if keyword in feature_lower:
                    potentially_biased.append({
                        'feature': feature,
                        'importance': importance,
                        'keyword': keyword
                    })
                    break
        
        # Calculate bias score
        if not potentially_biased:
            bias_score = 0.0
        else:
            total_biased_importance = sum(f['importance'] for f in potentially_biased)
            total_importance = sum(importance_dict.values())
            bias_score = total_biased_importance / total_importance if total_importance > 0 else 0.0
        
        return {
            'bias_score': bias_score,  # 0 to 1
            'potentially_biased_features': potentially_biased,
            'interpretation': 'HIGH_BIAS' if bias_score > 0.3 else 'MODERATE_BIAS' if bias_score > 0.15 else 'LOW_BIAS'
        }
    
    def analyze_feature_stability(
        self,
        current_importance: Dict[str, float],
        historical_importance: List[Dict[str, float]]
    ) -> Dict[str, Any]:
        """
        Analyze if feature importance is stable over time
        Unstable features may indicate overfitting or data issues
        """
        if not historical_importance:
            return {
                'stability_score': 1.0,
                'unstable_features': [],
                'interpretation': 'NO_HISTORY'
            }
        
        # Calculate variance for each feature
        feature_variances = {}
        
        for feature in current_importance.keys():
            historical_values = []
            for hist_imp in historical_importance:
                if feature in hist_imp:
                    historical_values.append(hist_imp[feature])
            
            if len(historical_values) > 1:
                variance = float(np.var(historical_values))
                feature_variances[feature] = variance
        
        # Identify unstable features (high variance)
        if feature_variances:
            mean_variance = np.mean(list(feature_variances.values()))
            std_variance = np.std(list(feature_variances.values()))
            
            unstable_features = []
            for feature, variance in feature_variances.items():
                if variance > mean_variance + 2 * std_variance:
                    unstable_features.append({
                        'feature': feature,
                        'variance': variance,
                        'current_importance': current_importance.get(feature, 0)
                    })
            
            # Overall stability score
            stability_score = 1.0 - min(mean_variance, 1.0)
        else:
            stability_score = 1.0
            unstable_features = []
        
        return {
            'stability_score': stability_score,  # 0 to 1
            'unstable_features': unstable_features,
            'interpretation': 'STABLE' if stability_score > 0.8 else 'MODERATE' if stability_score > 0.6 else 'UNSTABLE'
        }
    
    def generate_importance_report(
        self,
        models: Dict[str, Any],
        feature_names: List[str],
        X: Optional[np.ndarray] = None,
        y: Optional[np.ndarray] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive feature importance report
        """
        # Get importance from all models
        model_importances = self.get_ensemble_feature_importance(
            models, feature_names, X, y
        )
        
        # Aggregate across models
        avg_importance = self.aggregate_importance(model_importances)
        
        # Get top features
        top_features = self.get_top_features(avg_importance, top_n=20)
        
        # Check for bias
        bias_analysis = self.detect_feature_bias(avg_importance)
        
        # Check stability
        stability_analysis = self.analyze_feature_stability(
            avg_importance, 
            self.feature_importance_history[-10:]  # Last 10 runs
        )
        
        # Store in history
        self.feature_importance_history.append(avg_importance)
        
        # Keep only last 50 runs
        if len(self.feature_importance_history) > 50:
            self.feature_importance_history = self.feature_importance_history[-50:]
        
        return {
            'top_features': top_features,
            'all_importances': avg_importance,
            'model_specific_importances': model_importances,
            'bias_analysis': bias_analysis,
            'stability_analysis': stability_analysis,
            'total_features': len(feature_names),
            'timestamp': pd.Timestamp.now().isoformat()
        }


# Export
__all__ = ['FeatureImportanceAnalyzer']
