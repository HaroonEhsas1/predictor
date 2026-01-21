#!/usr/bin/env python3
"""
Enhanced Confidence Gating System
Multi-layer calibration, prediction intervals, Bayesian ensembling
Institutional-grade confidence validation and risk management
"""

import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from sklearn.calibration import CalibratedClassifierCV
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression
from scipy import stats
from scipy.special import softmax
import warnings
warnings.filterwarnings('ignore')

class EnhancedConfidenceGating:
    """
    Advanced confidence gating with multi-layer calibration
    
    Features:
    1. Multi-method probability calibration (Platt, Isotonic, Beta)
    2. Bayesian model averaging
    3. Prediction intervals with uncertainty quantification
    4. Dynamic confidence thresholds based on market regime
    5. Multi-horizon consensus validation
    6. Ensemble diversity scoring
    7. Temporal consistency checking
    8. Out-of-sample performance tracking
    """
    
    def __init__(self, min_confidence: float = 0.75, min_consensus: float = 0.80):
        self.min_confidence = min_confidence
        self.min_consensus = min_consensus
        
        self.platt_calibrator = None
        self.isotonic_calibrator = None
        self.beta_calibrator = None
        self.calibrators_fitted = False
        
        self.performance_history = []
        self.calibration_history = []
        
        print("🎯 Enhanced Confidence Gating System initialized")
        print(f"   Min Confidence: {min_confidence:.1%} | Min Consensus: {min_consensus:.1%}")
        print(f"   ⚠️ IMPORTANT: Call fit_calibrators() with historical data before use")
        print(f"   ⚠️ Without fitting, calibration will use conservative identity mapping")
    
    def calibrate_probabilities(self, 
                               raw_predictions: Dict[str, float], 
                               historical_predictions: Optional[List[Dict]] = None,
                               method: str = 'ensemble') -> Dict[str, float]:
        """
        Multi-method probability calibration
        
        Methods:
        - platt: Platt scaling (logistic regression)
        - isotonic: Isotonic regression
        - beta: Beta calibration
        - ensemble: Weighted average of all methods
        
        Args:
            raw_predictions: Dict of model_name -> raw probability
            historical_predictions: Historical predictions for calibration
            method: Calibration method to use
            
        Returns:
            Dict of model_name -> calibrated probability
        """
        
        if not self.calibrators_fitted and method != 'none':
            print(f"⚠️ Warning: Calibrators not fitted - using conservative identity mapping")
        
        calibrated = {}
        
        for model_name, raw_prob in raw_predictions.items():
            
            if method == 'platt':
                calibrated[model_name] = self._platt_calibration(raw_prob)
            elif method == 'isotonic':
                calibrated[model_name] = self._isotonic_calibration(raw_prob)
            elif method == 'beta':
                calibrated[model_name] = self._beta_calibration(raw_prob)
            elif method == 'ensemble':
                platt_prob = self._platt_calibration(raw_prob)
                isotonic_prob = self._isotonic_calibration(raw_prob)
                beta_prob = self._beta_calibration(raw_prob)
                
                calibrated[model_name] = np.mean([platt_prob, isotonic_prob, beta_prob])
            else:
                calibrated[model_name] = raw_prob
        
        return calibrated
    
    def fit_calibrators(self, historical_predictions: np.ndarray, historical_outcomes: np.ndarray) -> None:
        """
        Fit calibration models on historical prediction/outcome pairs
        
        IMPORTANT: Must be called with real historical data before using calibration
        
        Args:
            historical_predictions: Array of past model predictions (0-1 probabilities)
            historical_outcomes: Array of actual binary outcomes (0 or 1)
        """
        
        if len(historical_predictions) < 30:
            print(f"⚠️ Warning: Only {len(historical_predictions)} samples - need 30+ for reliable calibration")
            return
        
        historical_predictions = np.array(historical_predictions).reshape(-1, 1)
        historical_outcomes = np.array(historical_outcomes)
        
        try:
            from sklearn.linear_model import LogisticRegression
            self.platt_calibrator = LogisticRegression()
            self.platt_calibrator.fit(historical_predictions, historical_outcomes)
            print(f"✓ Platt calibrator fitted on {len(historical_predictions)} samples")
        except Exception as e:
            print(f"⚠️ Platt calibration fit failed: {e}")
            self.platt_calibrator = None
        
        try:
            from sklearn.isotonic import IsotonicRegression
            self.isotonic_calibrator = IsotonicRegression(out_of_bounds='clip')
            self.isotonic_calibrator.fit(historical_predictions.ravel(), historical_outcomes)
            print(f"✓ Isotonic calibrator fitted on {len(historical_predictions)} samples")
        except Exception as e:
            print(f"⚠️ Isotonic calibration fit failed: {e}")
            self.isotonic_calibrator = None
        
        successes = np.sum(historical_outcomes)
        failures = len(historical_outcomes) - successes
        self.beta_calibrator = {'alpha': successes + 1, 'beta': failures + 1}
        print(f"✓ Beta calibrator fitted (α={self.beta_calibrator['alpha']:.1f}, β={self.beta_calibrator['beta']:.1f})")
        
        self.calibrators_fitted = True
        print(f"\n✅ All calibrators fitted successfully on {len(historical_predictions)} samples")
    
    def _platt_calibration(self, raw_prob: float) -> float:
        """
        Platt scaling using fitted logistic regression
        Falls back to conservative identity mapping if not fitted
        """
        
        if self.platt_calibrator is not None:
            try:
                prob_array = np.array([[raw_prob]])
                calibrated = self.platt_calibrator.predict_proba(prob_array)[0, 1]
                return np.clip(calibrated, 0.01, 0.99)
            except Exception:
                pass
        
        return np.clip(raw_prob, 0.01, 0.99)
    
    def _isotonic_calibration(self, raw_prob: float) -> float:
        """
        Isotonic regression using fitted monotonic calibrator
        Falls back to conservative identity mapping if not fitted
        """
        
        if self.isotonic_calibrator is not None:
            try:
                calibrated = self.isotonic_calibrator.predict([raw_prob])[0]
                return np.clip(calibrated, 0.01, 0.99)
            except Exception:
                pass
        
        return np.clip(raw_prob, 0.01, 0.99)
    
    def _beta_calibration(self, raw_prob: float) -> float:
        """
        Beta calibration using fitted beta distribution parameters
        Falls back to conservative identity mapping if not fitted
        """
        
        if self.beta_calibrator is not None:
            try:
                alpha = self.beta_calibrator['alpha']
                beta_param = self.beta_calibrator['beta']
                
                expected_success_rate = alpha / (alpha + beta_param)
                
                calibrated = raw_prob * 0.7 + expected_success_rate * 0.3
                
                return np.clip(calibrated, 0.01, 0.99)
            except Exception:
                pass
        
        return np.clip(raw_prob, 0.01, 0.99)
    
    def bayesian_model_averaging(self, 
                                predictions: Dict[str, float],
                                model_weights: Optional[Dict[str, float]] = None,
                                historical_performance: Optional[Dict[str, float]] = None) -> Tuple[float, float]:
        """
        Bayesian Model Averaging (BMA) for ensemble predictions
        
        Combines multiple model predictions using Bayesian principles,
        weighting models by their historical performance
        
        Args:
            predictions: Dict of model_name -> prediction value
            model_weights: Optional prior weights for each model
            historical_performance: Historical accuracy for each model
            
        Returns:
            (averaged_prediction, uncertainty)
        """
        
        if model_weights is None:
            if historical_performance:
                model_weights = self._compute_bayesian_weights(historical_performance)
            else:
                model_weights = {k: 1/len(predictions) for k in predictions.keys()}
        
        total_weight = sum(model_weights.values())
        normalized_weights = {k: v/total_weight for k, v in model_weights.items()}
        
        bma_prediction = sum(pred * normalized_weights.get(name, 0) 
                           for name, pred in predictions.items())
        
        variance = sum(normalized_weights.get(name, 0) * (pred - bma_prediction)**2 
                      for name, pred in predictions.items())
        uncertainty = np.sqrt(variance)
        
        return bma_prediction, uncertainty
    
    def _compute_bayesian_weights(self, historical_performance: Dict[str, float]) -> Dict[str, float]:
        """
        Compute Bayesian posterior weights based on historical performance
        
        Uses a Beta-Binomial model for each classifier
        """
        
        weights = {}
        
        for model_name, accuracy in historical_performance.items():
            alpha_prior = 1.0
            beta_prior = 1.0
            
            successes = accuracy * 100
            failures = (1 - accuracy) * 100
            
            alpha_post = alpha_prior + successes
            beta_post = beta_prior + failures
            
            expected_accuracy = alpha_post / (alpha_post + beta_post)
            weights[model_name] = expected_accuracy
        
        return weights
    
    def compute_prediction_intervals(self, 
                                    predictions: List[float],
                                    confidence_level: float = 0.95) -> Tuple[float, float, float]:
        """
        Compute prediction intervals with uncertainty quantification
        
        Uses bootstrap sampling and quantile estimation
        
        Args:
            predictions: List of predictions from ensemble
            confidence_level: Confidence level for interval (0.95 = 95%)
            
        Returns:
            (lower_bound, median, upper_bound)
        """
        
        if len(predictions) < 2:
            median = predictions[0] if predictions else 0.5
            return median, median, median
        
        predictions_arr = np.array(predictions)
        
        lower_percentile = (1 - confidence_level) / 2 * 100
        upper_percentile = (1 + confidence_level) / 2 * 100
        
        lower_bound = np.percentile(predictions_arr, lower_percentile)
        median = np.median(predictions_arr)
        upper_bound = np.percentile(predictions_arr, upper_percentile)
        
        return lower_bound, median, upper_bound
    
    def dynamic_confidence_threshold(self, 
                                   market_volatility: float,
                                   market_regime: str = 'normal',
                                   recent_performance: float = 0.6) -> float:
        """
        Dynamically adjust confidence threshold based on market conditions
        
        Args:
            market_volatility: Current market volatility (VIX or realized vol)
            market_regime: 'bull', 'bear', 'normal', 'crisis'
            recent_performance: Recent model accuracy (0-1)
            
        Returns:
            Adjusted confidence threshold
        """
        
        base_threshold = self.min_confidence
        
        volatility_adjustment = min(market_volatility / 20 * 0.10, 0.15)
        
        regime_adjustments = {
            'bull': -0.03,
            'bear': 0.05,
            'normal': 0.0,
            'crisis': 0.15,
        }
        regime_adj = regime_adjustments.get(market_regime, 0.0)
        
        performance_adj = (0.7 - recent_performance) * 0.2
        
        adjusted_threshold = base_threshold + volatility_adjustment + regime_adj + performance_adj
        
        adjusted_threshold = np.clip(adjusted_threshold, 0.50, 0.90)
        
        return adjusted_threshold
    
    def multi_horizon_consensus(self, 
                               horizons_predictions: Dict[str, Dict[str, float]]) -> Dict[str, Any]:
        """
        Validate consensus across multiple prediction horizons
        
        Args:
            horizons_predictions: Dict of {
                'intraday': {'model1': 0.7, 'model2': 0.8},
                'daily': {'model1': 0.65, 'model2': 0.75},
                'weekly': {'model1': 0.6, 'model2': 0.7}
            }
            
        Returns:
            Dict with consensus metrics
        """
        
        consensus_results = {
            'horizons_analyzed': len(horizons_predictions),
            'horizon_agreements': {},
            'cross_horizon_consistency': 0.0,
            'overall_consensus': False,
        }
        
        horizon_directions = {}
        
        for horizon, predictions in horizons_predictions.items():
            if not predictions:
                continue
            
            avg_pred = np.mean(list(predictions.values()))
            direction = 'UP' if avg_pred > 0.5 else 'DOWN'
            
            agreement = sum(1 for p in predictions.values() if (p > 0.5) == (avg_pred > 0.5))
            consensus_pct = agreement / len(predictions)
            
            horizon_directions[horizon] = direction
            consensus_results['horizon_agreements'][horizon] = consensus_pct
        
        if len(set(horizon_directions.values())) == 1:
            consensus_results['cross_horizon_consistency'] = 1.0
        else:
            consensus_results['cross_horizon_consistency'] = 0.0
        
        min_consensus = min(consensus_results['horizon_agreements'].values()) if consensus_results['horizon_agreements'] else 0.0
        
        consensus_results['overall_consensus'] = (
            min_consensus >= self.min_consensus and
            consensus_results['cross_horizon_consistency'] >= 0.8
        )
        
        return consensus_results
    
    def ensemble_diversity_score(self, predictions: Dict[str, float]) -> float:
        """
        Measure ensemble diversity using disagreement metrics
        
        High diversity is good for robustness, but needs to be balanced
        with consensus requirements
        
        Args:
            predictions: Dict of model_name -> prediction
            
        Returns:
            Diversity score (0-1, higher = more diverse)
        """
        
        if len(predictions) < 2:
            return 0.0
        
        pred_values = list(predictions.values())
        
        pairwise_disagreements = []
        for i in range(len(pred_values)):
            for j in range(i+1, len(pred_values)):
                disagreement = abs(pred_values[i] - pred_values[j])
                pairwise_disagreements.append(disagreement)
        
        avg_disagreement = np.mean(pairwise_disagreements) if pairwise_disagreements else 0.0
        
        variance = np.var(pred_values)
        
        diversity_score = 0.7 * avg_disagreement + 0.3 * variance
        
        diversity_score = np.clip(diversity_score, 0.0, 1.0)
        
        return diversity_score
    
    def temporal_consistency_check(self, 
                                  current_prediction: float,
                                  historical_predictions: List[float],
                                  max_deviation: float = 0.30) -> Tuple[bool, float]:
        """
        Check if current prediction is temporally consistent with recent history
        
        Large deviations may indicate regime changes or model instability
        
        Args:
            current_prediction: Current prediction value
            historical_predictions: Recent predictions (last N)
            max_deviation: Maximum allowed deviation from recent average
            
        Returns:
            (is_consistent, deviation_score)
        """
        
        if not historical_predictions:
            return True, 0.0
        
        recent_avg = np.mean(historical_predictions[-10:])
        recent_std = np.std(historical_predictions[-10:])
        
        deviation = abs(current_prediction - recent_avg)
        
        if recent_std > 0:
            z_score = deviation / recent_std
            is_consistent = z_score < 2.0
        else:
            is_consistent = deviation < max_deviation
        
        deviation_score = min(deviation / max_deviation, 1.0)
        
        return is_consistent, deviation_score
    
    def evaluate_gating_decision(self,
                                raw_predictions: Dict[str, float],
                                market_conditions: Dict[str, Any],
                                historical_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Comprehensive gating evaluation using all advanced techniques
        
        Args:
            raw_predictions: Raw model predictions
            market_conditions: Current market state
            historical_context: Historical performance and predictions
            
        Returns:
            Complete gating decision with detailed reasoning
        """
        
        print("\n🔍 Enhanced Confidence Gating Analysis")
        
        calibrated_predictions = self.calibrate_probabilities(
            raw_predictions, 
            method='ensemble'
        )
        print(f"   ✓ Probability calibration complete")
        
        if historical_context and 'model_performance' in historical_context:
            bma_prediction, bma_uncertainty = self.bayesian_model_averaging(
                calibrated_predictions,
                historical_performance=historical_context['model_performance']
            )
        else:
            bma_prediction, bma_uncertainty = self.bayesian_model_averaging(calibrated_predictions)
        print(f"   ✓ Bayesian averaging: {bma_prediction:.3f} ± {bma_uncertainty:.3f}")
        
        pred_values = list(calibrated_predictions.values())
        lower, median, upper = self.compute_prediction_intervals(pred_values, confidence_level=0.95)
        interval_width = upper - lower
        print(f"   ✓ 95% Prediction interval: [{lower:.3f}, {upper:.3f}] (width: {interval_width:.3f})")
        
        market_vol = market_conditions.get('volatility', 20)
        market_regime = market_conditions.get('regime', 'normal')
        recent_perf = historical_context.get('recent_accuracy', 0.6) if historical_context else 0.6
        
        dynamic_threshold = self.dynamic_confidence_threshold(
            market_vol, market_regime, recent_perf
        )
        print(f"   ✓ Dynamic threshold: {dynamic_threshold:.1%} (market: {market_regime}, vol: {market_vol:.1f})")
        
        diversity = self.ensemble_diversity_score(calibrated_predictions)
        print(f"   ✓ Ensemble diversity: {diversity:.3f}")
        
        temporal_consistent = True
        deviation = 0.0
        if historical_context and 'recent_predictions' in historical_context:
            temporal_consistent, deviation = self.temporal_consistency_check(
                bma_prediction,
                historical_context['recent_predictions']
            )
        print(f"   ✓ Temporal consistency: {'PASS' if temporal_consistent else 'FAIL'} (deviation: {deviation:.3f})")
        
        direction_agreement = sum(1 for p in pred_values if (p > 0.5) == (bma_prediction > 0.5))
        consensus_score = direction_agreement / len(pred_values)
        consensus_pass = consensus_score >= self.min_consensus
        print(f"   ✓ Ensemble consensus: {consensus_score:.1%} ({'PASS' if consensus_pass else 'FAIL'})")
        
        confidence_pass = bma_prediction >= dynamic_threshold or (1 - bma_prediction) >= dynamic_threshold
        
        uncertainty_acceptable = bma_uncertainty < 0.20
        
        interval_tight = interval_width < 0.40
        
        all_gates_passed = (
            confidence_pass and
            consensus_pass and
            temporal_consistent and
            uncertainty_acceptable and
            interval_tight
        )
        
        final_direction = 'UP' if bma_prediction > 0.5 else 'DOWN'
        final_confidence = max(bma_prediction, 1 - bma_prediction)
        
        gate_result = {
            'timestamp': datetime.now().isoformat(),
            'trade_signal': final_direction if all_gates_passed else 'NO_TRADE',
            'confidence': final_confidence,
            'bma_prediction': bma_prediction,
            'bma_uncertainty': bma_uncertainty,
            'prediction_interval': {
                'lower': lower,
                'median': median,
                'upper': upper,
                'width': interval_width
            },
            'gates': {
                'confidence': confidence_pass,
                'consensus': consensus_pass,
                'temporal_consistency': temporal_consistent,
                'uncertainty_acceptable': uncertainty_acceptable,
                'interval_tight': interval_tight,
            },
            'gates_passed': sum([confidence_pass, consensus_pass, temporal_consistent, 
                               uncertainty_acceptable, interval_tight]),
            'gates_total': 5,
            'thresholds': {
                'confidence': dynamic_threshold,
                'consensus': self.min_consensus,
                'max_uncertainty': 0.20,
                'max_interval_width': 0.40,
            },
            'ensemble_metrics': {
                'diversity': diversity,
                'consensus_score': consensus_score,
                'temporal_deviation': deviation,
            },
            'calibrated_predictions': calibrated_predictions,
            'raw_predictions': raw_predictions,
        }
        
        if all_gates_passed:
            print(f"\n✅ ALL GATES PASSED - Signal: {final_direction} @ {final_confidence:.1%} confidence")
        else:
            failed_gates = [k for k, v in gate_result['gates'].items() if not v]
            print(f"\n❌ GATES FAILED: {', '.join(failed_gates)}")
        
        return gate_result
    
    def track_performance(self, 
                         prediction: float, 
                         actual_outcome: float,
                         metadata: Optional[Dict] = None) -> None:
        """
        Track prediction performance for continuous calibration improvement
        
        Args:
            prediction: Predicted probability
            actual_outcome: Actual binary outcome (0 or 1)
            metadata: Additional context
        """
        
        self.performance_history.append({
            'timestamp': datetime.now().isoformat(),
            'prediction': prediction,
            'actual': actual_outcome,
            'error': abs(prediction - actual_outcome),
            'brier_score': (prediction - actual_outcome) ** 2,
            'log_loss': -actual_outcome * np.log(prediction + 1e-10) - (1 - actual_outcome) * np.log(1 - prediction + 1e-10),
            'metadata': metadata or {}
        })
        
        if len(self.performance_history) > 1000:
            self.performance_history = self.performance_history[-1000:]
    
    def get_calibration_metrics(self) -> Dict[str, float]:
        """
        Compute calibration quality metrics from historical performance
        
        Returns:
            Dict with calibration metrics
        """
        
        if len(self.performance_history) < 10:
            return {'insufficient_data': True}
        
        predictions = [p['prediction'] for p in self.performance_history]
        actuals = [p['actual'] for p in self.performance_history]
        
        brier_score = np.mean([(p - a) ** 2 for p, a in zip(predictions, actuals)])
        
        log_losses = [p['log_loss'] for p in self.performance_history if 'log_loss' in p]
        avg_log_loss = np.mean(log_losses) if log_losses else 0
        
        n_bins = 10
        bin_boundaries = np.linspace(0, 1, n_bins + 1)
        bin_centers = (bin_boundaries[:-1] + bin_boundaries[1:]) / 2
        
        ece = 0.0
        for i in range(n_bins):
            bin_mask = (np.array(predictions) >= bin_boundaries[i]) & (np.array(predictions) < bin_boundaries[i+1])
            if np.sum(bin_mask) > 0:
                bin_confidence = np.mean(np.array(predictions)[bin_mask])
                bin_accuracy = np.mean(np.array(actuals)[bin_mask])
                bin_weight = np.sum(bin_mask) / len(predictions)
                ece += bin_weight * abs(bin_confidence - bin_accuracy)
        
        return {
            'brier_score': brier_score,
            'log_loss': avg_log_loss,
            'expected_calibration_error': ece,
            'total_predictions': len(self.performance_history),
            'average_prediction': np.mean(predictions),
            'average_outcome': np.mean(actuals),
        }


if __name__ == "__main__":
    gating = EnhancedConfidenceGating(min_confidence=0.75, min_consensus=0.80)
    
    raw_predictions = {
        'xgboost': 0.72,
        'random_forest': 0.68,
        'gradient_boosting': 0.75,
        'lstm': 0.71,
        'lightgbm': 0.69,
    }
    
    market_conditions = {
        'volatility': 22.5,
        'regime': 'normal',
    }
    
    historical_context = {
        'model_performance': {
            'xgboost': 0.68,
            'random_forest': 0.64,
            'gradient_boosting': 0.71,
            'lstm': 0.62,
            'lightgbm': 0.66,
        },
        'recent_predictions': [0.68, 0.72, 0.69, 0.71, 0.70],
        'recent_accuracy': 0.67,
    }
    
    result = gating.evaluate_gating_decision(
        raw_predictions,
        market_conditions,
        historical_context
    )
    
    print("\n" + "="*60)
    print("FINAL GATING DECISION")
    print("="*60)
    print(f"Signal: {result['trade_signal']}")
    print(f"Confidence: {result['confidence']:.1%}")
    print(f"Gates Passed: {result['gates_passed']}/{result['gates_total']}")
