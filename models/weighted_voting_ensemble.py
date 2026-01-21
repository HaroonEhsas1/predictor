#!/usr/bin/env python3
"""
Dynamic Weighted Voting Ensemble - 100% FREE
Adjusts model weights based on recent performance automatically
Better than static ensembles - adapts to market regime changes
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from collections import deque
import json

class DynamicWeightedEnsemble:
    """
    Weighted voting ensemble with dynamic weight adjustment
    
    Features:
    - Tracks recent performance of each model
    - Adjusts weights based on rolling accuracy/error
    - Handles both classification and regression
    - Automatic weight decay for older predictions
    - Saves/loads weight history for persistence
    """
    
    def __init__(self, models: Dict[str, Any], task: str = 'classification',
                 performance_window: int = 50, decay_factor: float = 0.95):
        """
        Args:
            models: Dictionary of {name: model} pairs
            task: 'classification' or 'regression'
            performance_window: Number of recent predictions to track
            decay_factor: Weight decay for historical performance (0-1)
        """
        self.models = models
        self.task = task
        self.performance_window = performance_window
        self.decay_factor = decay_factor
        
        # Initialize weights (equal at start)
        self.weights = {name: 1.0 / len(models) for name in models.keys()}
        
        # Performance tracking
        self.performance_history = {name: deque(maxlen=performance_window) 
                                    for name in models.keys()}
        self.prediction_count = 0
    
    def predict(self, X: np.ndarray, update_weights: bool = True,
                y_true: Optional[np.ndarray] = None) -> np.ndarray:
        """
        Make weighted ensemble prediction
        
        Args:
            X: Input features
            update_weights: Whether to update weights based on this prediction
            y_true: True labels (if available, for weight updating)
        """
        predictions = {}
        
        # Get predictions from all models
        for name, model in self.models.items():
            if self.task == 'classification':
                if hasattr(model, 'predict_proba'):
                    pred = model.predict_proba(X)
                    if pred.shape[1] == 2:
                        pred = pred[:, 1]  # Binary classification
                    else:
                        pred = pred  # Multi-class (use full proba matrix)
                else:
                    pred = model.predict(X)
            else:
                pred = model.predict(X)
            
            predictions[name] = pred
        
        # Weighted voting
        if self.task == 'classification':
            weighted_pred = np.zeros_like(list(predictions.values())[0])
            for name, pred in predictions.items():
                weighted_pred += self.weights[name] * pred
            
            # For binary classification, threshold at 0.5
            if weighted_pred.ndim == 1 or weighted_pred.shape[1] == 1:
                final_pred = (weighted_pred > 0.5).astype(int).flatten()
            else:
                final_pred = np.argmax(weighted_pred, axis=1)
        else:
            weighted_pred = np.zeros(X.shape[0])
            for name, pred in predictions.items():
                weighted_pred += self.weights[name] * pred
            final_pred = weighted_pred
        
        # Update weights if true labels provided
        if update_weights and y_true is not None:
            self._update_weights(predictions, y_true)
        
        self.prediction_count += 1
        
        return final_pred
    
    def _update_weights(self, predictions: Dict[str, np.ndarray], 
                       y_true: np.ndarray):
        """Update model weights based on recent performance"""
        
        for name, pred in predictions.items():
            if self.task == 'classification':
                # Calculate accuracy for this prediction
                if pred.ndim == 1:
                    pred_class = (pred > 0.5).astype(int)
                else:
                    pred_class = np.argmax(pred, axis=1)
                
                accuracy = np.mean(pred_class == y_true)
                self.performance_history[name].append(accuracy)
            else:
                # Calculate error for regression
                error = np.mean(np.abs(pred - y_true))
                # Convert to "performance" (lower error = higher performance)
                performance = 1.0 / (1.0 + error)
                self.performance_history[name].append(performance)
        
        # Recalculate weights based on recent performance
        self._recalculate_weights()
    
    def _recalculate_weights(self):
        """Recalculate weights based on performance history"""
        
        # Calculate weighted average performance for each model
        avg_performance = {}
        
        for name, history in self.performance_history.items():
            if len(history) == 0:
                avg_performance[name] = 1.0 / len(self.models)  # Default
                continue
            
            # Apply exponential decay to older predictions
            weights_array = np.array([self.decay_factor ** i 
                                     for i in range(len(history)-1, -1, -1)])
            weights_array /= weights_array.sum()  # Normalize
            
            performance = np.average(history, weights=weights_array)
            avg_performance[name] = performance
        
        # Normalize to sum to 1
        total_performance = sum(avg_performance.values())
        
        if total_performance > 0:
            self.weights = {name: perf / total_performance 
                          for name, perf in avg_performance.items()}
        else:
            # Fallback to equal weights
            self.weights = {name: 1.0 / len(self.models) 
                          for name in self.models.keys()}
    
    def get_weights(self) -> Dict[str, float]:
        """Get current model weights"""
        return self.weights.copy()
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary for all models"""
        summary = {}
        
        for name, history in self.performance_history.items():
            if len(history) > 0:
                summary[name] = {
                    'current_weight': self.weights[name],
                    'recent_performance': np.mean(list(history)[-10:]) if len(history) >= 10 else np.mean(history),
                    'avg_performance': np.mean(history),
                    'std_performance': np.std(history),
                    'num_predictions': len(history)
                }
            else:
                summary[name] = {
                    'current_weight': self.weights[name],
                    'recent_performance': None,
                    'avg_performance': None,
                    'std_performance': None,
                    'num_predictions': 0
                }
        
        return summary
    
    def save_weights(self, filepath: str):
        """Save weight history to file"""
        data = {
            'weights': self.weights,
            'performance_history': {
                name: list(history) 
                for name, history in self.performance_history.items()
            },
            'prediction_count': self.prediction_count
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_weights(self, filepath: str):
        """Load weight history from file"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        self.weights = data['weights']
        self.performance_history = {
            name: deque(history, maxlen=self.performance_window)
            for name, history in data['performance_history'].items()
        }
        self.prediction_count = data['prediction_count']


class AdaptiveModelSelector:
    """
    Automatically selects best model based on current conditions
    
    Uses market regime, volatility, and recent performance to pick optimal model
    """
    
    def __init__(self, models: Dict[str, Any], task: str = 'classification'):
        self.models = models
        self.task = task
        self.selection_history = []
        
    def select_best_model(self, X: np.ndarray, 
                         market_regime: str = 'normal',
                         volatility: float = 0.02) -> Tuple[str, Any]:
        """
        Select best model based on conditions
        
        Args:
            X: Features for prediction
            market_regime: 'high_vol', 'low_vol', 'trending', 'mean_reverting'
            volatility: Current market volatility
        
        Returns:
            (model_name, model_object)
        """
        # Strategy: Different models work better in different conditions
        
        if market_regime == 'high_vol' or volatility > 0.03:
            # High volatility: Use ensemble models (more robust)
            preferred = ['random_forest', 'gradient_boosting', 'xgboost']
        elif market_regime == 'trending':
            # Trending: Use momentum-sensitive models
            preferred = ['xgboost', 'lightgbm', 'lstm']
        elif market_regime == 'mean_reverting':
            # Mean reverting: Use regression models
            preferred = ['ridge', 'random_forest', 'svm']
        else:
            # Default: Use best general performers
            preferred = ['xgboost', 'random_forest', 'gradient_boosting']
        
        # Select first available preferred model
        for model_name in preferred:
            if model_name in self.models:
                self.selection_history.append({
                    'regime': market_regime,
                    'volatility': volatility,
                    'selected': model_name
                })
                return model_name, self.models[model_name]
        
        # Fallback: Return first available model
        first_name = list(self.models.keys())[0]
        return first_name, self.models[first_name]


if __name__ == "__main__":
    print("Testing Dynamic Weighted Voting Ensemble (100% FREE)...")
    
    # Create sample models
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.datasets import make_classification
    
    X, y = make_classification(n_samples=1000, n_features=20, random_state=42)
    
    models = {
        'rf': RandomForestClassifier(n_estimators=50, random_state=42),
        'gb': GradientBoostingClassifier(n_estimators=50, random_state=42)
    }
    
    # Train models
    for name, model in models.items():
        model.fit(X[:800], y[:800])
    
    # Create ensemble
    ensemble = DynamicWeightedEnsemble(models, task='classification')
    
    # Make predictions with weight updates
    X_test = X[800:]
    y_test = y[800:]
    
    predictions = ensemble.predict(X_test, update_weights=True, y_true=y_test)
    accuracy = np.mean(predictions == y_test)
    
    print(f"\n📊 Ensemble Accuracy: {accuracy:.3f}")
    print(f"\n⚖️ Current Weights:")
    for name, weight in ensemble.get_weights().items():
        print(f"   {name}: {weight:.3f}")
    
    print(f"\n📈 Performance Summary:")
    summary = ensemble.get_performance_summary()
    for name, stats in summary.items():
        print(f"   {name}: {stats}")
    
    print("\n✅ Dynamic Weighted Ensemble adapts to changing conditions!")
