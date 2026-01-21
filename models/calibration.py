#!/usr/bin/env python3
"""
Probability Calibration Module
Implements Platt scaling and isotonic regression for confidence calibration
"""

import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_predict
from typing import Dict, List, Tuple, Optional
import pickle
import os

class ProbabilityCalibrator:
    """Calibrates model confidence outputs to true probabilities"""
    
    def __init__(self, method: str = 'platt'):
        self.method = method  # 'platt' or 'isotonic'
        self.calibrator = None
        self.is_fitted = False
        self.calibration_curve_data = None
        
    def fit_calibration(self, confidences: np.ndarray, outcomes: np.ndarray) -> Dict[str, float]:
        """
        Fit calibration model
        
        Args:
            confidences: Raw confidence scores [0,1]
            outcomes: True binary outcomes (1=correct, 0=incorrect)
        """
        if len(confidences) < 10:
            raise ValueError("Need at least 10 data points for calibration")
        
        confidences = np.array(confidences).reshape(-1, 1)
        outcomes = np.array(outcomes)
        
        if self.method == 'platt':
            # Platt scaling (sigmoid)
            self.calibrator = LogisticRegression()
            self.calibrator.fit(confidences, outcomes)
        else:
            # Isotonic regression
            self.calibrator = IsotonicRegression(out_of_bounds='clip')
            self.calibrator.fit(confidences.flatten(), outcomes)
        
        self.is_fitted = True
        
        # Generate calibration curve data
        self._generate_calibration_curve(confidences, outcomes)
        
        # Calculate calibration metrics
        calibrated_probs = self.transform(confidences.flatten())
        metrics = self._calculate_calibration_metrics(confidences.flatten(), outcomes, calibrated_probs)
        
        return metrics
    
    def transform(self, confidences: np.ndarray) -> np.ndarray:
        """Transform raw confidences to calibrated probabilities"""
        if not self.is_fitted:
            return confidences  # Return raw if not calibrated
        
        confidences = np.array(confidences).reshape(-1, 1)
        
        if self.method == 'platt':
            return self.calibrator.predict_proba(confidences)[:, 1]
        else:
            return self.calibrator.transform(confidences.flatten())
    
    def _generate_calibration_curve(self, confidences: np.ndarray, outcomes: np.ndarray):
        """Generate reliability diagram data"""
        conf_flat = confidences.flatten()
        
        # Create bins
        bins = np.linspace(0, 1, 11)  # 10 bins
        bin_centers = (bins[:-1] + bins[1:]) / 2
        
        bin_accuracies = []
        bin_confidences = []
        bin_counts = []
        
        for i in range(len(bins) - 1):
            mask = (conf_flat >= bins[i]) & (conf_flat < bins[i + 1])
            if i == len(bins) - 2:  # Last bin includes right edge
                mask = (conf_flat >= bins[i]) & (conf_flat <= bins[i + 1])
            
            if mask.sum() > 0:
                bin_accuracy = outcomes[mask].mean()
                bin_confidence = conf_flat[mask].mean()
                bin_count = mask.sum()
                
                bin_accuracies.append(bin_accuracy)
                bin_confidences.append(bin_confidence)
                bin_counts.append(bin_count)
            else:
                bin_accuracies.append(0)
                bin_confidences.append(bin_centers[i])
                bin_counts.append(0)
        
        self.calibration_curve_data = {
            'bin_centers': bin_centers,
            'bin_accuracies': bin_accuracies,
            'bin_confidences': bin_confidences,
            'bin_counts': bin_counts
        }
    
    def _calculate_calibration_metrics(self, raw_conf: np.ndarray, 
                                     outcomes: np.ndarray, 
                                     calibrated_conf: np.ndarray) -> Dict[str, float]:
        """Calculate calibration quality metrics"""
        
        # Brier Score (lower is better)
        brier_raw = np.mean((raw_conf - outcomes) ** 2)
        brier_calibrated = np.mean((calibrated_conf - outcomes) ** 2)
        
        # Expected Calibration Error
        ece_raw = self._calculate_ece(raw_conf, outcomes)
        ece_calibrated = self._calculate_ece(calibrated_conf, outcomes)
        
        # Reliability (calibration quality)
        reliability_raw = self._calculate_reliability(raw_conf, outcomes)
        reliability_calibrated = self._calculate_reliability(calibrated_conf, outcomes)
        
        return {
            'brier_score_improvement': brier_raw - brier_calibrated,
            'ece_improvement': ece_raw - ece_calibrated,
            'reliability_improvement': reliability_calibrated - reliability_raw,
            'calibrated_brier': brier_calibrated,
            'calibrated_ece': ece_calibrated,
            'calibrated_reliability': reliability_calibrated
        }
    
    def _calculate_ece(self, confidences: np.ndarray, outcomes: np.ndarray) -> float:
        """Calculate Expected Calibration Error"""
        bins = np.linspace(0, 1, 11)
        ece = 0
        
        for i in range(len(bins) - 1):
            mask = (confidences >= bins[i]) & (confidences < bins[i + 1])
            if i == len(bins) - 2:
                mask = (confidences >= bins[i]) & (confidences <= bins[i + 1])
            
            if mask.sum() > 0:
                bin_accuracy = outcomes[mask].mean()
                bin_confidence = confidences[mask].mean()
                bin_weight = mask.sum() / len(confidences)
                
                ece += bin_weight * abs(bin_confidence - bin_accuracy)
        
        return ece
    
    def _calculate_reliability(self, confidences: np.ndarray, outcomes: np.ndarray) -> float:
        """Calculate reliability (perfect = 1.0)"""
        bins = np.linspace(0, 1, 11)
        weighted_squared_errors = 0
        total_weight = 0
        
        for i in range(len(bins) - 1):
            mask = (confidences >= bins[i]) & (confidences < bins[i + 1])
            if i == len(bins) - 2:
                mask = (confidences >= bins[i]) & (confidences <= bins[i + 1])
            
            if mask.sum() > 0:
                bin_accuracy = outcomes[mask].mean()
                bin_confidence = confidences[mask].mean()
                bin_weight = mask.sum()
                
                weighted_squared_errors += bin_weight * (bin_confidence - bin_accuracy) ** 2
                total_weight += bin_weight
        
        if total_weight == 0:
            return 0
        
        mse = weighted_squared_errors / total_weight
        return 1 / (1 + mse)  # Convert to reliability score
    
    def save_calibrator(self, filepath: str):
        """Save calibrator to file"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'wb') as f:
            pickle.dump({
                'calibrator': self.calibrator,
                'method': self.method,
                'is_fitted': self.is_fitted,
                'calibration_curve_data': self.calibration_curve_data
            }, f)
    
    def load_calibrator(self, filepath: str):
        """Load calibrator from file"""
        if os.path.exists(filepath):
            with open(filepath, 'rb') as f:
                data = pickle.load(f)
                self.calibrator = data['calibrator']
                self.method = data['method']
                self.is_fitted = data['is_fitted']
                self.calibration_curve_data = data['calibration_curve_data']
                return True
        return False

class EnsembleCalibrationManager:
    """Manages calibration for multiple prediction horizons"""
    
    def __init__(self):
        self.calibrators = {
            'next_day': ProbabilityCalibrator('platt'),
            'swing': ProbabilityCalibrator('isotonic'),
            'intraday': ProbabilityCalibrator('platt')
        }
        self.model_dir = 'models/calibration/'
        os.makedirs(self.model_dir, exist_ok=True)
    
    def fit_all_calibrators(self, historical_data: Dict[str, pd.DataFrame]):
        """Fit calibrators for all horizons"""
        results = {}
        
        for horizon, data in historical_data.items():
            if horizon in self.calibrators and len(data) >= 10:
                confidences = data['confidence'].values
                outcomes = data['correct'].values  # 1 if prediction was correct
                
                try:
                    metrics = self.calibrators[horizon].fit_calibration(confidences, outcomes)
                    results[horizon] = metrics
                    
                    # Save calibrator
                    self.calibrators[horizon].save_calibrator(
                        os.path.join(self.model_dir, f'{horizon}_calibrator.pkl')
                    )
                    
                except Exception as e:
                    print(f"Failed to calibrate {horizon}: {e}")
                    results[horizon] = {'error': str(e)}
        
        return results
    
    def load_all_calibrators(self):
        """Load all saved calibrators"""
        for horizon in self.calibrators:
            filepath = os.path.join(self.model_dir, f'{horizon}_calibrator.pkl')
            self.calibrators[horizon].load_calibrator(filepath)
    
    def calibrate_prediction(self, horizon: str, raw_confidence: float) -> float:
        """Calibrate a single prediction confidence"""
        if horizon in self.calibrators:
            return float(self.calibrators[horizon].transform([raw_confidence])[0])
        return raw_confidence
    
    def get_calibration_quality(self, horizon: str) -> Dict[str, float]:
        """Get calibration quality metrics for a horizon"""
        if horizon in self.calibrators and self.calibrators[horizon].calibration_curve_data:
            curve_data = self.calibrators[horizon].calibration_curve_data
            
            # Calculate overall calibration quality
            bin_diffs = []
            for acc, conf, count in zip(curve_data['bin_accuracies'], 
                                      curve_data['bin_confidences'], 
                                      curve_data['bin_counts']):
                if count > 0:
                    bin_diffs.append(abs(acc - conf))
            
            return {
                'mean_calibration_error': np.mean(bin_diffs) if bin_diffs else 1.0,
                'calibration_quality': 1 - np.mean(bin_diffs) if bin_diffs else 0.0,
                'bins_with_data': sum(1 for c in curve_data['bin_counts'] if c > 0)
            }
        
        return {'calibration_quality': 0.0}

# Global calibration manager
calibration_manager = EnsembleCalibrationManager()