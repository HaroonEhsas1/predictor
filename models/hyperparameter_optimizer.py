#!/usr/bin/env python3
"""
Advanced Hyperparameter Optimization - 100% FREE
Uses GridSearchCV, RandomizedSearchCV, and Optuna (all free libraries)
Optimizes ML models for maximum accuracy without manual tuning
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV, TimeSeriesSplit
from sklearn.metrics import make_scorer, accuracy_score, mean_squared_error
import warnings
warnings.filterwarnings('ignore')

# Try to import optuna (free but optional)
try:
    import optuna
    optuna.logging.set_verbosity(optuna.logging.WARNING)
    OPTUNA_AVAILABLE = True
except ImportError:
    OPTUNA_AVAILABLE = False


class HyperparameterOptimizer:
    """
    FREE hyperparameter optimization using multiple methods
    
    Methods:
    1. GridSearchCV - Exhaustive search (small parameter spaces)
    2. RandomizedSearchCV - Random sampling (large spaces, faster)
    3. Optuna - Bayesian optimization (most efficient, requires optuna)
    """
    
    def __init__(self, task: str = 'classification', cv_splits: int = 5):
        """
        Args:
            task: 'classification' or 'regression'
            cv_splits: Number of cross-validation splits
        """
        self.task = task
        self.cv_splits = cv_splits
        self.best_params = {}
        self.best_score = None
        
    def optimize_random_forest(self, X: np.ndarray, y: np.ndarray, 
                               method: str = 'grid') -> Dict[str, Any]:
        """
        Optimize Random Forest hyperparameters - FREE
        
        Args:
            method: 'grid', 'random', or 'optuna'
        """
        from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
        
        print(f"🔍 Optimizing Random Forest with {method.upper()} search...")
        
        # Parameter grid
        param_grid = {
            'n_estimators': [50, 100, 200, 300],
            'max_depth': [5, 10, 15, 20, None],
            'min_samples_split': [2, 5, 10, 20],
            'min_samples_leaf': [1, 2, 4, 8],
            'max_features': ['sqrt', 'log2', 0.5, 0.7]
        }
        
        # Create model
        if self.task == 'classification':
            model = RandomForestClassifier(random_state=42, n_jobs=-1)
            scoring = 'accuracy'
        else:
            model = RandomForestRegressor(random_state=42, n_jobs=-1)
            scoring = 'neg_mean_squared_error'
        
        # Cross-validation
        cv = TimeSeriesSplit(n_splits=self.cv_splits)
        
        if method == 'grid':
            search = GridSearchCV(
                model, param_grid, cv=cv, scoring=scoring,
                n_jobs=-1, verbose=0
            )
        elif method == 'random':
            search = RandomizedSearchCV(
                model, param_grid, cv=cv, scoring=scoring,
                n_iter=50, random_state=42, n_jobs=-1, verbose=0
            )
        elif method == 'optuna' and OPTUNA_AVAILABLE:
            return self._optuna_optimize_rf(X, y)
        else:
            print("⚠️ Optuna not available, falling back to RandomizedSearchCV")
            search = RandomizedSearchCV(
                model, param_grid, cv=cv, scoring=scoring,
                n_iter=50, random_state=42, n_jobs=-1, verbose=0
            )
        
        # Fit
        search.fit(X, y)
        
        self.best_params = search.best_params_
        self.best_score = search.best_score_
        
        print(f"✅ Best score: {self.best_score:.4f}")
        print(f"   Best params: {self.best_params}")
        
        return {
            'best_model': search.best_estimator_,
            'best_params': self.best_params,
            'best_score': self.best_score,
            'cv_results': search.cv_results_
        }
    
    def optimize_xgboost(self, X: np.ndarray, y: np.ndarray,
                        method: str = 'random') -> Dict[str, Any]:
        """Optimize XGBoost hyperparameters - FREE"""
        try:
            import xgboost as xgb
        except ImportError:
            print("⚠️ XGBoost not installed. Install with: pip install xgboost")
            return {}
        
        print(f"🔍 Optimizing XGBoost with {method.upper()} search...")
        
        param_grid = {
            'n_estimators': [50, 100, 200, 300],
            'learning_rate': [0.01, 0.05, 0.1, 0.2],
            'max_depth': [3, 5, 7, 9],
            'min_child_weight': [1, 3, 5, 7],
            'subsample': [0.6, 0.7, 0.8, 0.9, 1.0],
            'colsample_bytree': [0.6, 0.7, 0.8, 0.9, 1.0]
        }
        
        if self.task == 'classification':
            model = xgb.XGBClassifier(random_state=42, eval_metric='logloss')
            scoring = 'accuracy'
        else:
            model = xgb.XGBRegressor(random_state=42)
            scoring = 'neg_mean_squared_error'
        
        cv = TimeSeriesSplit(n_splits=self.cv_splits)
        
        if method == 'optuna' and OPTUNA_AVAILABLE:
            return self._optuna_optimize_xgb(X, y)
        
        # Use RandomizedSearch (faster for XGBoost)
        search = RandomizedSearchCV(
            model, param_grid, cv=cv, scoring=scoring,
            n_iter=100, random_state=42, n_jobs=-1, verbose=0
        )
        
        search.fit(X, y)
        
        self.best_params = search.best_params_
        self.best_score = search.best_score_
        
        print(f"✅ Best score: {self.best_score:.4f}")
        print(f"   Best params: {self.best_params}")
        
        return {
            'best_model': search.best_estimator_,
            'best_params': self.best_params,
            'best_score': self.best_score
        }
    
    def _optuna_optimize_rf(self, X: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
        """Optimize Random Forest with Optuna (Bayesian optimization) - FREE"""
        from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
        from sklearn.model_selection import cross_val_score
        
        def objective(trial):
            params = {
                'n_estimators': trial.suggest_int('n_estimators', 50, 300),
                'max_depth': trial.suggest_int('max_depth', 3, 20),
                'min_samples_split': trial.suggest_int('min_samples_split', 2, 20),
                'min_samples_leaf': trial.suggest_int('min_samples_leaf', 1, 10),
                'max_features': trial.suggest_categorical('max_features', ['sqrt', 'log2', 0.5, 0.7])
            }
            
            if self.task == 'classification':
                model = RandomForestClassifier(**params, random_state=42, n_jobs=-1)
                scoring = 'accuracy'
            else:
                model = RandomForestRegressor(**params, random_state=42, n_jobs=-1)
                scoring = 'neg_mean_squared_error'
            
            cv = TimeSeriesSplit(n_splits=self.cv_splits)
            score = cross_val_score(model, X, y, cv=cv, scoring=scoring, n_jobs=-1).mean()
            
            return score
        
        study = optuna.create_study(direction='maximize' if self.task == 'classification' else 'minimize')
        study.optimize(objective, n_trials=100, show_progress_bar=False)
        
        self.best_params = study.best_params
        self.best_score = study.best_value
        
        print(f"✅ Optuna optimization complete!")
        print(f"   Best score: {self.best_score:.4f}")
        print(f"   Best params: {self.best_params}")
        
        # Train final model with best params
        if self.task == 'classification':
            model = RandomForestClassifier(**self.best_params, random_state=42, n_jobs=-1)
        else:
            model = RandomForestRegressor(**self.best_params, random_state=42, n_jobs=-1)
        
        model.fit(X, y)
        
        return {
            'best_model': model,
            'best_params': self.best_params,
            'best_score': self.best_score,
            'optimization_history': study.trials_dataframe()
        }
    
    def _optuna_optimize_xgb(self, X: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
        """Optimize XGBoost with Optuna - FREE"""
        import xgboost as xgb
        from sklearn.model_selection import cross_val_score
        
        def objective(trial):
            params = {
                'n_estimators': trial.suggest_int('n_estimators', 50, 300),
                'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3, log=True),
                'max_depth': trial.suggest_int('max_depth', 3, 10),
                'min_child_weight': trial.suggest_int('min_child_weight', 1, 7),
                'subsample': trial.suggest_float('subsample', 0.6, 1.0),
                'colsample_bytree': trial.suggest_float('colsample_bytree', 0.6, 1.0)
            }
            
            if self.task == 'classification':
                model = xgb.XGBClassifier(**params, random_state=42, eval_metric='logloss')
                scoring = 'accuracy'
            else:
                model = xgb.XGBRegressor(**params, random_state=42)
                scoring = 'neg_mean_squared_error'
            
            cv = TimeSeriesSplit(n_splits=self.cv_splits)
            score = cross_val_score(model, X, y, cv=cv, scoring=scoring, n_jobs=-1).mean()
            
            return score
        
        study = optuna.create_study(direction='maximize' if self.task == 'classification' else 'minimize')
        study.optimize(objective, n_trials=100, show_progress_bar=False)
        
        self.best_params = study.best_params
        self.best_score = study.best_value
        
        print(f"✅ Optuna optimization complete!")
        print(f"   Best score: {self.best_score:.4f}")
        
        # Train final model
        if self.task == 'classification':
            model = xgb.XGBClassifier(**self.best_params, random_state=42, eval_metric='logloss')
        else:
            model = xgb.XGBRegressor(**self.best_params, random_state=42)
        
        model.fit(X, y)
        
        return {
            'best_model': model,
            'best_params': self.best_params,
            'best_score': self.best_score
        }


def auto_optimize_model(X: np.ndarray, y: np.ndarray, 
                        model_type: str = 'rf', 
                        task: str = 'classification') -> Dict[str, Any]:
    """
    Automatically optimize any model - 100% FREE
    
    Args:
        X: Features
        y: Target
        model_type: 'rf' (Random Forest) or 'xgb' (XGBoost)
        task: 'classification' or 'regression'
    
    Returns:
        Optimized model and parameters
    """
    optimizer = HyperparameterOptimizer(task=task, cv_splits=5)
    
    # Choose best method (Optuna > Random > Grid)
    method = 'optuna' if OPTUNA_AVAILABLE else 'random'
    
    if model_type == 'rf':
        return optimizer.optimize_random_forest(X, y, method=method)
    elif model_type == 'xgb':
        return optimizer.optimize_xgboost(X, y, method=method)
    else:
        raise ValueError(f"Unknown model type: {model_type}")


if __name__ == "__main__":
    print("Testing Hyperparameter Optimization (100% FREE)...")
    
    # Generate sample data
    from sklearn.datasets import make_classification
    X, y = make_classification(n_samples=1000, n_features=20, random_state=42)
    
    # Optimize Random Forest
    result = auto_optimize_model(X, y, model_type='rf', task='classification')
    
    print(f"\n✅ Optimization Complete!")
    print(f"   Best Model: {result['best_model'].__class__.__name__}")
    print(f"   Best Score: {result['best_score']:.4f}")
    
    if OPTUNA_AVAILABLE:
        print("\n🚀 Optuna (Bayesian Optimization) is available - using best method!")
    else:
        print("\n💡 Tip: Install Optuna for faster optimization: pip install optuna")
