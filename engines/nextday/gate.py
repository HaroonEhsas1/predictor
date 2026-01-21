"""
Professional gating system for next-day predictions
Implements institutional risk management and confidence thresholds
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

try:
    from .config import CONFIG
except ImportError:
    from config import CONFIG

logger = logging.getLogger(__name__)

class PredictionGate:
    """
    Institutional-grade gating system for trading signals
    Implements strict confidence and consensus requirements
    """
    
    def __init__(self):
        self.gate_history = []
        
    def evaluate_signal(self, prediction_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate prediction against gating rules
        
        Args:
            prediction_result: Raw prediction from model ensemble
            
        Returns:
            Gated result with trade recommendation and reasoning
        """
        
        logger.info("Evaluating prediction against institutional gating rules...")
        
        # Extract key metrics
        direction = prediction_result.get('direction', 'SKIP')
        confidence = prediction_result.get('confidence', 0.0)
        predicted_gap = prediction_result.get('predicted_gap_pct', 0.0)
        model_predictions = prediction_result.get('model_predictions', {})
        
        # Initialize gated result
        gated_result = prediction_result.copy()
        gated_result['trade_signal'] = 'NO_TRADE'
        gated_result['gate_reasons'] = []
        gated_result['passed_gates'] = []
        
        # Gate 1: Minimum confidence threshold
        confidence_pass = confidence >= CONFIG.min_confidence
        if confidence_pass:
            gated_result['passed_gates'].append(f"Confidence {confidence:.1%} >= {CONFIG.min_confidence:.0%}")
        else:
            gated_result['gate_reasons'].append(f"Low confidence: {confidence:.1%} < {CONFIG.min_confidence:.0%}")
        
        # Gate 2: Ensemble consensus
        consensus_pass, consensus_score = self._check_ensemble_consensus(model_predictions)
        if consensus_pass:
            gated_result['passed_gates'].append(f"Ensemble consensus {consensus_score:.1%} >= {CONFIG.min_ensemble_consensus:.0%}")
        else:
            gated_result['gate_reasons'].append(f"Poor consensus: {consensus_score:.1%} < {CONFIG.min_ensemble_consensus:.0%}")
        
        # Gate 3: Minimum gap magnitude (institutional threshold)
        gap_magnitude_pass = abs(predicted_gap) >= CONFIG.min_gap_threshold
        if gap_magnitude_pass:
            gated_result['passed_gates'].append(f"Gap magnitude {abs(predicted_gap):.1%} >= {CONFIG.min_gap_threshold:.1%}")
        else:
            gated_result['gate_reasons'].append(f"Gap too small: {abs(predicted_gap):.1%} < {CONFIG.min_gap_threshold:.1%}")
        
        # Gate 4: Dry run enforcement
        dry_run_gate = True
        if not CONFIG.dry_run:
            # Additional checks for live trading
            dry_run_gate = self._check_live_trading_conditions(gated_result)
            if not dry_run_gate:
                gated_result['gate_reasons'].append("Live trading conditions not met")
        
        # Gate 5: Feature flag check
        feature_enabled = CONFIG.enabled
        if not feature_enabled:
            gated_result['gate_reasons'].append("Next-day engine feature flag disabled")
        
        # Final gating decision
        all_gates_passed = (
            confidence_pass and 
            consensus_pass and 
            gap_magnitude_pass and 
            dry_run_gate and 
            feature_enabled
        )
        
        if all_gates_passed and not CONFIG.dry_run:
            gated_result['trade_signal'] = direction
            gated_result['position_size'] = self._calculate_position_size(confidence, predicted_gap)
            logger.info(f"✓ All gates passed - Trade signal: {direction}")
        else:
            gated_result['trade_signal'] = 'NO_TRADE'
            gated_result['position_size'] = 0.0
            
            if CONFIG.dry_run:
                gated_result['gate_reasons'].append("Dry run mode - no actual trades")
            
            logger.info(f"✗ Gating blocked trade - Reasons: {', '.join(gated_result['gate_reasons'])}")
        
        # Add gating metadata
        gated_result.update({
            'gating_timestamp': datetime.now().isoformat(),
            'confidence_threshold': CONFIG.min_confidence,
            'consensus_threshold': CONFIG.min_ensemble_consensus,
            'dry_run_mode': CONFIG.dry_run,
            'gates_passed': len(gated_result['passed_gates']),
            'gates_failed': len(gated_result['gate_reasons'])
        })
        
        # Log to gate history
        self._log_gate_decision(gated_result)
        
        return gated_result
    
    def _check_ensemble_consensus(self, model_predictions: Dict[str, float]) -> tuple[bool, float]:
        """
        Check if model ensemble has sufficient consensus
        
        Returns:
            (consensus_pass, consensus_score)
        """
        
        if len(model_predictions) < 2:
            return False, 0.0
        
        try:
            predictions = list(model_predictions.values())
            
            # Calculate direction agreement
            directions = [1 if p > 0 else -1 if p < 0 else 0 for p in predictions]
            
            # Count agreement
            if len(set(directions)) == 1:
                # Perfect agreement
                consensus_score = 1.0
            else:
                # Majority agreement
                from collections import Counter
                direction_counts = Counter(directions)
                majority_count = max(direction_counts.values())
                consensus_score = majority_count / len(directions)
            
            consensus_pass = consensus_score >= CONFIG.min_ensemble_consensus
            
            return consensus_pass, consensus_score
            
        except Exception as e:
            logger.error(f"Consensus check failed: {e}")
            return False, 0.0
    
    def _check_live_trading_conditions(self, result: Dict[str, Any]) -> bool:
        """
        Additional checks for live trading mode
        Only called when dry_run=False
        """
        
        # Check if we're in market hours or pre-market
        current_hour = datetime.now().hour
        if current_hour < 6 or current_hour > 20:  # Outside reasonable trading window
            return False
        
        # Check model age (don't trade with stale models)
        # TODO: Implement model training date check
        # For now, assume models are fresh enough if prediction was generated
        
        # Check for recent validation performance
        # TODO: Implement recent out-of-sample performance check
        # For now, rely on confidence thresholds already passed
        
        # Check if we have sufficient confidence for live trading
        confidence = result.get('confidence', 0.0)
        if confidence < CONFIG.min_confidence:
            return False
            
        # Check if prediction direction is valid (not error/neutral in dry run)
        direction = result.get('direction', 'SKIP')
        if direction in ['ERROR', 'SKIP']:
            return False
            
        # All checks passed - allow live trading
        return True
    
    def _calculate_position_size(self, confidence: float, predicted_gap: float) -> float:
        """
        Calculate position size based on confidence and expected return
        Implements Kelly criterion approximation with risk caps
        """
        
        try:
            # Base position size from confidence
            base_size = min(confidence * CONFIG.max_position_size, CONFIG.max_position_size)
            
            # Adjust for gap magnitude (higher expected return = larger position)
            gap_multiplier = min(abs(predicted_gap) * CONFIG.gap_size_multiplier, CONFIG.max_gap_multiplier)
            
            position_size = base_size * gap_multiplier
            
            # Apply institutional caps
            position_size = min(position_size, CONFIG.max_position_size)
            position_size = max(position_size, CONFIG.min_position_size)
            
            return position_size
            
        except Exception as e:
            logger.error(f"Position sizing failed: {e}")
            return CONFIG.min_position_size  # Minimal fallback position
    
    def _log_gate_decision(self, result: Dict[str, Any]) -> None:
        """Log gating decision for monitoring and analysis"""
        
        gate_log = {
            'timestamp': result.get('gating_timestamp'),
            'direction': result.get('direction'),
            'confidence': result.get('confidence'),
            'trade_signal': result.get('trade_signal'),
            'gates_passed': result.get('gates_passed'),
            'gates_failed': result.get('gates_failed'),
            'reasons': result.get('gate_reasons', [])
        }
        
        self.gate_history.append(gate_log)
        
        # Keep only recent history (last 100 decisions)
        if len(self.gate_history) > 100:
            self.gate_history = self.gate_history[-100:]
    
    def get_gating_stats(self) -> Dict[str, Any]:
        """Get statistics about recent gating decisions"""
        
        if not self.gate_history:
            return {'total_decisions': 0}
        
        total = len(self.gate_history)
        trades_approved = sum(1 for log in self.gate_history if log['trade_signal'] != 'NO_TRADE')
        
        avg_confidence = sum(log['confidence'] for log in self.gate_history) / total
        
        # Most common gate failures
        all_reasons = []
        for log in self.gate_history:
            all_reasons.extend(log['reasons'])
        
        from collections import Counter
        common_failures = Counter(all_reasons).most_common(5)
        
        return {
            'total_decisions': total,
            'trades_approved': trades_approved,
            'approval_rate': trades_approved / total,
            'avg_confidence': avg_confidence,
            'common_failures': common_failures
        }

class RiskManager:
    """
    Additional risk management layer for institutional compliance
    """
    
    def __init__(self):
        self.daily_exposure = 0.0
        self.open_positions = {}
        
    def check_risk_limits(self, position_size: float, direction: str) -> tuple[bool, str]:
        """
        Check if proposed position violates risk limits
        
        Returns:
            (approved, reason)
        """
        
        # Daily exposure limit
        new_exposure = self.daily_exposure + position_size
        if new_exposure > CONFIG.max_position_size * 3:  # 3x daily limit
            return False, f"Daily exposure limit: {new_exposure:.1%} > {CONFIG.max_position_size * 3:.1%}"
        
        # Position concentration (example check)
        if position_size > CONFIG.max_position_size:
            return False, f"Position too large: {position_size:.1%} > {CONFIG.max_position_size:.1%}"
        
        return True, "Risk checks passed"
    
    def update_exposure(self, position_size: float, direction: str) -> None:
        """Update tracking of current exposure"""
        self.daily_exposure += position_size

# Export main classes
__all__ = ['PredictionGate', 'RiskManager']