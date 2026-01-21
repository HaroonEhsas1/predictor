#!/usr/bin/env python3
"""
Calibration Helper - Auto-fit calibrators from prediction database
Makes it easy to use Enhanced Confidence Gating without manual setup
"""

import os
import sys
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, Tuple

try:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'database'))
    from replit_database_bridge import prediction_db
    DB_AVAILABLE = True
except ImportError:
    prediction_db = None
    DB_AVAILABLE = False

from enhanced_confidence_gating import EnhancedConfidenceGating


def auto_fit_from_database(gating_system: EnhancedConfidenceGating, 
                          min_samples: int = 30,
                          lookback_days: int = 90) -> bool:
    """
    Automatically fit calibrators from prediction database history
    
    Args:
        gating_system: EnhancedConfidenceGating instance to fit
        min_samples: Minimum samples needed for fitting
        lookback_days: Days of history to use
        
    Returns:
        True if successfully fitted, False otherwise
    """
    
    if not DB_AVAILABLE or prediction_db is None:
        print("⚠️ Prediction database not available - cannot auto-fit")
        return False
    
    try:
        print(f"🔍 Searching for historical predictions (last {lookback_days} days)...")
        
        cutoff_date = datetime.now() - timedelta(days=lookback_days)
        
        historical_data = prediction_db.get_predictions_after(cutoff_date)
        
        if not historical_data or len(historical_data) < min_samples:
            print(f"⚠️ Insufficient historical data: {len(historical_data) if historical_data else 0} samples (need {min_samples})")
            return False
        
        predictions = []
        outcomes = []
        
        for record in historical_data:
            if 'confidence' in record and 'actual_outcome' in record:
                pred_prob = float(record['confidence'])
                
                if record['direction'] == 'DOWN':
                    pred_prob = 1 - pred_prob
                
                actual = 1 if record['actual_outcome'] == record['direction'] else 0
                
                predictions.append(pred_prob)
                outcomes.append(actual)
        
        if len(predictions) < min_samples:
            print(f"⚠️ Insufficient valid predictions: {len(predictions)} (need {min_samples})")
            return False
        
        print(f"✓ Found {len(predictions)} valid prediction-outcome pairs")
        
        gating_system.fit_calibrators(
            np.array(predictions),
            np.array(outcomes)
        )
        
        print(f"✅ Auto-fitted calibrators from database history")
        return True
        
    except Exception as e:
        print(f"⚠️ Auto-fit failed: {e}")
        return False


def auto_fit_from_csv(gating_system: EnhancedConfidenceGating,
                     csv_path: str = 'logs/predictions.csv',
                     min_samples: int = 30) -> bool:
    """
    Automatically fit calibrators from CSV prediction log
    
    Args:
        gating_system: EnhancedConfidenceGating instance to fit
        csv_path: Path to predictions CSV file
        min_samples: Minimum samples needed for fitting
        
    Returns:
        True if successfully fitted, False otherwise
    """
    
    try:
        if not os.path.exists(csv_path):
            print(f"⚠️ CSV file not found: {csv_path}")
            return False
        
        print(f"🔍 Loading predictions from {csv_path}...")
        
        df = pd.read_csv(csv_path)
        
        if len(df) < min_samples:
            print(f"⚠️ Insufficient data in CSV: {len(df)} rows (need {min_samples})")
            return False
        
        if 'confidence' not in df.columns or 'actual_outcome' not in df.columns:
            print(f"⚠️ CSV missing required columns (confidence, actual_outcome)")
            return False
        
        predictions = []
        outcomes = []
        
        for _, row in df.iterrows():
            if pd.notna(row['confidence']) and pd.notna(row['actual_outcome']):
                pred_prob = float(row['confidence'])
                
                if 'direction' in row and row['direction'] == 'DOWN':
                    pred_prob = 1 - pred_prob
                
                actual = 1 if row['actual_outcome'] else 0
                
                predictions.append(pred_prob)
                outcomes.append(actual)
        
        if len(predictions) < min_samples:
            print(f"⚠️ Insufficient valid predictions: {len(predictions)} (need {min_samples})")
            return False
        
        print(f"✓ Found {len(predictions)} valid prediction-outcome pairs")
        
        gating_system.fit_calibrators(
            np.array(predictions),
            np.array(outcomes)
        )
        
        print(f"✅ Auto-fitted calibrators from CSV history")
        return True
        
    except Exception as e:
        print(f"⚠️ Auto-fit from CSV failed: {e}")
        return False


def create_fitted_gating_system(min_confidence: float = 0.75,
                               min_consensus: float = 0.80,
                               auto_fit: bool = True) -> EnhancedConfidenceGating:
    """
    Convenience function to create a fitted gating system
    
    Args:
        min_confidence: Minimum confidence threshold
        min_consensus: Minimum ensemble consensus
        auto_fit: Attempt to auto-fit from available data
        
    Returns:
        Configured EnhancedConfidenceGating instance (fitted if data available)
    """
    
    gating = EnhancedConfidenceGating(min_confidence, min_consensus)
    
    if auto_fit:
        fitted = auto_fit_from_database(gating)
        
        if not fitted:
            fitted = auto_fit_from_csv(gating)
        
        if not fitted:
            print("\n⚠️ Could not auto-fit calibrators - using conservative fallback")
            print("   System will use identity mapping until historical data is available")
            print("   To manually fit: gating.fit_calibrators(predictions, outcomes)")
    
    return gating


if __name__ == "__main__":
    print("="*60)
    print("CALIBRATION HELPER - Auto-Fitting Demo")
    print("="*60)
    
    gating = create_fitted_gating_system(auto_fit=True)
    
    if gating.calibrators_fitted:
        print("\n✅ SUCCESS: Gating system ready to use with fitted calibrators")
        
        test_predictions = {
            'model1': 0.72,
            'model2': 0.68,
            'model3': 0.75
        }
        
        market_conditions = {
            'volatility': 22.5,
            'regime': 'normal'
        }
        
        result = gating.evaluate_gating_decision(
            test_predictions,
            market_conditions,
            None
        )
        
        print(f"\n📊 Test Evaluation:")
        print(f"   Signal: {result['trade_signal']}")
        print(f"   Confidence: {result['confidence']:.1%}")
        print(f"   Gates Passed: {result['gates_passed']}/{result['gates_total']}")
    else:
        print("\n⚠️ Calibrators not fitted - system will use conservative fallback")
        print("   Add historical data to enable full calibration features")
