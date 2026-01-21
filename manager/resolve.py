#!/usr/bin/env python3
"""
Signal Resolution Module
Unified signal processing, gating, position sizing, and risk assessment
"""

import os
import sys
from typing import Dict, Any, Optional, Tuple
import numpy as np

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import TRADING_RULES, DATA_QUALITY, RISK_LEVELS
from manager.scheduler import scheduler

class SignalResolver:
    """Unified signal resolution and risk management"""
    
    def __init__(self):
        self.trading_rules = TRADING_RULES
        self.data_quality_levels = DATA_QUALITY
        self.risk_levels = RISK_LEVELS
        
    def calculate_unified_risk(self, volatility: float, vix: float = None) -> str:
        """Calculate single, unified risk level"""
        # Combine volatility and VIX if available
        risk_score = volatility
        
        if vix is not None:
            # Normalize VIX (typical range 10-80)
            vix_normalized = min(vix / 40.0, 1.0)  # Cap at 40 VIX = 1.0
            risk_score = (volatility * 0.7) + (vix_normalized * 0.3)
        
        # Map to risk levels
        for level, (low, high) in self.risk_levels.items():
            if low <= risk_score < high:
                return level
        
        return 'HIGH'  # Default for extreme values
    
    def apply_trading_gates(self, prediction: Dict[str, Any]) -> Dict[str, Any]:
        """Apply unified trading gates and position sizing"""
        result = prediction.copy()
        
        # Extract key metrics
        ensemble_consensus = prediction.get('ensemble_consensus', 0.0)
        expected_gap_usd = abs(prediction.get('expected_gap_usd', 0.0))
        backtest_accuracy = prediction.get('backtest_accuracy', 0.0)
        data_quality = prediction.get('data_quality', DATA_QUALITY['STALE'])
        market_state = scheduler.get_market_state()
        
        # Gate 1: Minimum backtest accuracy for live trading
        live_trading_enabled = backtest_accuracy >= self.trading_rules['live_trading_accuracy_threshold']
        
        # Gate 2: Ensemble consensus threshold
        consensus_met = ensemble_consensus >= self.trading_rules['ensemble_consensus_threshold']
        
        # Gate 3: Minimum expected gap
        gap_met = expected_gap_usd >= self.trading_rules['minimum_gap_usd']
        
        # Gate 4: Data quality and market state
        market_conditions_ok = (
            data_quality == DATA_QUALITY['LIVE'] and 
            market_state['market_open']
        )
        
        # Determine action
        if not live_trading_enabled:
            action = 'MONITOR'
            size = 0.0
            reason = f"Backtest accuracy {backtest_accuracy:.1%} < {self.trading_rules['live_trading_accuracy_threshold']:.1%}"
        elif not market_conditions_ok:
            action = 'MONITOR'
            size = 0.0
            reason = f"Market closed or data quality: {data_quality}"
        elif not (consensus_met and gap_met):
            action = 'HOLD'
            size = 0.0
            if not consensus_met:
                reason = f"Consensus {ensemble_consensus:.1%} < {self.trading_rules['ensemble_consensus_threshold']:.1%}"
            else:
                reason = f"Gap ${expected_gap_usd:.2f} < ${self.trading_rules['minimum_gap_usd']}"
        else:
            # All gates passed - determine position size
            action = prediction.get('direction', 'HOLD')
            size = self._calculate_position_size(ensemble_consensus, data_quality)
            reason = "All trading gates passed"
        
        # Update result
        result.update({
            'action': action,
            'position_size': size,
            'gating_result': {
                'live_trading_enabled': live_trading_enabled,
                'consensus_met': consensus_met,
                'gap_met': gap_met,
                'market_conditions_ok': market_conditions_ok,
                'reason': reason
            }
        })
        
        return result
    
    def _calculate_position_size(self, consensus: float, data_quality: str) -> float:
        """Calculate position size based on consensus and data quality"""
        if data_quality != DATA_QUALITY['LIVE']:
            return 0.0
        
        sizing_rules = self.trading_rules['position_sizing']
        
        if consensus < 0.70:
            return 0.0
        elif consensus < 0.75:
            return sizing_rules['consensus_70_75']
        elif consensus < 0.80:
            return sizing_rules['consensus_75_80']
        else:
            return sizing_rules['consensus_80_plus']
    
    def finalize_signal(self, prediction: Dict[str, Any]) -> Dict[str, Any]:
        """Complete signal processing with all validations"""
        # Apply trading gates
        gated_prediction = self.apply_trading_gates(prediction)
        
        # Calculate unified risk
        volatility = prediction.get('volatility', 0.03)
        vix = prediction.get('vix', None)
        unified_risk = self.calculate_unified_risk(volatility, vix)
        
        # Market state
        market_state = scheduler.get_market_state()
        
        # Final result
        final_result = {
            **gated_prediction,
            'risk_level': unified_risk,
            'market_state': market_state['session_phase'],
            'timestamp_utc': market_state['times']['utc_iso'],
            'timestamp_et': market_state['times']['et_formatted'],
            'is_trading_day': market_state['is_trading_day'],
            'final_validation': {
                'should_trade': (
                    gated_prediction['action'] in ['BUY', 'SELL'] and 
                    gated_prediction['position_size'] > 0
                ),
                'risk_assessment': unified_risk,
                'position_justified': gated_prediction['position_size'] > 0,
                'all_gates_passed': gated_prediction['gating_result']['reason'] == "All trading gates passed"
            }
        }
        
        return final_result
    
    def validate_consistency(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        """Validate signal for internal consistency"""
        issues = []
        
        # Check for contradictory risk levels
        if 'risk_level' in signal and 'alternative_risk' in signal:
            if signal['risk_level'] != signal['alternative_risk']:
                issues.append(f"Conflicting risk levels: {signal['risk_level']} vs {signal['alternative_risk']}")
        
        # Check position sizing consistency
        if signal.get('action') == 'HOLD' and signal.get('position_size', 0) > 0:
            issues.append("HOLD action with non-zero position size")
        
        # Check confidence vs consensus
        confidence = signal.get('confidence', 0)
        consensus = signal.get('ensemble_consensus', 0)
        if abs(confidence - consensus) > 0.3:
            issues.append(f"Large confidence/consensus divergence: {confidence:.1%} vs {consensus:.1%}")
        
        # Check data quality vs action
        data_quality = signal.get('data_quality', '')
        action = signal.get('action', '')
        if data_quality != DATA_QUALITY['LIVE'] and action in ['BUY', 'SELL']:
            issues.append(f"Trade signal on {data_quality} data quality")
        
        return {
            'is_consistent': len(issues) == 0,
            'issues': issues,
            'validation_passed': len(issues) == 0
        }

# Global resolver instance
signal_resolver = SignalResolver()