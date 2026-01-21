"""Weekly retraining script with regularization to fix overfitting.

Run this every Sunday to keep models fresh and prevent drift.
Usage: python scripts/retrain.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
from sklearn.model_selection import TimeSeriesSplit
from sklearn.linear_model import Ridge, LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.calibration import CalibratedClassifierCV
import lightgbm as lgb
import joblib
from pathlib import Path

# Paths
MODELS_DIR = Path(__file__).parent.parent / "models"
MODELS_DIR.mkdir(exist_ok=True)

def fetch_training_data(symbol="AMD", days=365):
    """Fetch fresh training data."""
    print(f"📊 Fetching {days} days of data for {symbol}...")
    ticker = yf.Ticker(symbol)
    df = ticker.history(period=f"{days}d", interval="1d")
    
    # Calculate gap (next open - today close)
    df['Gap'] = (df['Open'].shift(-1) - df['Close']) / df['Close'] * 100
    df['Gap_Direction'] = (df['Gap'] > 0.1).astype(int)  # 1=UP, 0=DOWN
    
    # Features
    df['Returns_1d'] = df['Close'].pct_change(1)
    df['Returns_5d'] = df['Close'].pct_change(5)
    df['Volume_Ratio'] = df['Volume'] / df['Volume'].rolling(20).mean()
    df['RSI'] = 100 - (100 / (1 + (df['Close'].diff().clip(lower=0).rolling(14).mean() / 
                                     (-df['Close'].diff().clip(upper=0).rolling(14).mean()))))
    
    df.dropna(inplace=True)
    return df

def train_regularized_models(df):
    """Train 3 models with strong regularization."""
    features = ['Returns_1d', 'Returns_5d', 'Volume_Ratio', 'RSI']
    X = df[features].values
    y = df['Gap_Direction'].values
    
    # Time-series cross-validation
    tscv = TimeSeriesSplit(n_splits=5)
    
    models = {}
    
    # 1. Ridge Regression (simple baseline)
    print("🔧 Training Ridge baseline...")
    ridge = Ridge(alpha=10.0)  # Strong regularization
    ridge.fit(X, y)
    models['ridge'] = ridge
    
    # 2. Logistic Regression with L2
    print("🔧 Training Logistic Regression...")
    logistic = LogisticRegression(C=0.1, max_iter=1000)  # Strong penalty
    logistic.fit(X, y)
    # Calibrate probabilities
    calibrated = CalibratedClassifierCV(logistic, method='isotonic', cv=tscv)
    calibrated.fit(X, y)
    models['logistic_calibrated'] = calibrated
    
    # 3. LightGBM with regularization
    print("🔧 Training LightGBM...")
    lgbm = lgb.LGBMClassifier(
        n_estimators=100,
        max_depth=3,  # Shallow trees
        learning_rate=0.05,
        reg_alpha=1.0,  # L1 regularization
        reg_lambda=1.0,  # L2 regularization
        min_child_samples=50,
        random_state=42
    )
    lgbm.fit(X, y)
    models['lightgbm'] = lgbm
    
    # Evaluate
    for name, model in models.items():
        preds = model.predict(X)
        acc = (preds == y).mean()
        print(f"✅ {name}: {acc:.1%} training accuracy")
    
    return models, features

def save_models(models, features):
    """Save models with timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d")
    for name, model in models.items():
        path = MODELS_DIR / f"{name}_{timestamp}.pkl"
        joblib.dump(model, path)
        print(f"💾 Saved: {path}")
    
    # Save feature names
    joblib.dump(features, MODELS_DIR / f"features_{timestamp}.pkl")

if __name__ == "__main__":
    print("🚀 Starting weekly model retraining...")
    df = fetch_training_data(days=730)  # 2 years
    models, features = train_regularized_models(df)
    save_models(models, features)
    print("✅ Retraining complete!")
