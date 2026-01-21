#!/usr/bin/env python3
"""
Execution Guardrails Module
Final validation layer for trade execution with multi-horizon consensus
"""

import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import TRADING_RULES

@dataclass
class ExecutionSignal:
    """Represents a trading signal from one horizon"""
    horizon: str
    direction: str
    confidence: float
    expected_move: float
    atr_risk: float
    timestamp: datetime
    data_quality: str

class ExecutionGuardrails:
    """Final execution validation with institutional-grade checks"""
    
    def __init__(self):
        self.institutional_threshold = 0.80
        self.max_atr_multiplier = 2.0
        self.required_horizons = ['next_day', 'swing', 'intraday']
        self.consensus_threshold = 0.80
        
    def validate_execution(self, signals: List[ExecutionSignal], 
                          market_conditions: Dict[str, Any]) -> Dict[str, Any]:
        """
        Master execution validation
        
        Returns:
            Dict with execution decision and detailed reasoning
        """
        
        # Step 1: Basic signal validation
        basic_validation = self._validate_basic_requirements(signals)
        if not basic_validation['passed']:
            return self._create_rejection_result('BASIC_VALIDATION', basic_validation['reason'])
        
        # Step 2: Multi-horizon consensus
        consensus_validation = self._validate_multi_horizon_consensus(signals)
        if not consensus_validation['passed']:
            return self._create_rejection_result('CONSENSUS', consensus_validation['reason'])
        
        # Step 3: Confidence threshold
        confidence_validation = self._validate_confidence_threshold(signals)
        if not confidence_validation['passed']:
            return self._create_rejection_result('CONFIDENCE', confidence_validation['reason'])
        
        # Step 4: Risk-reward validation
        risk_validation = self._validate_risk_reward(signals)
        if not risk_validation['passed']:
            return self._create_rejection_result('RISK_REWARD', risk_validation['reason'])
        
        # Step 5: Market conditions
        market_validation = self._validate_market_conditions(market_conditions)
        if not market_validation['passed']:
            return self._create_rejection_result('MARKET_CONDITIONS', market_validation['reason'])
        
        # Step 6: Final execution parameters
        execution_params = self._calculate_execution_parameters(signals, market_conditions)
        
        return self._create_approval_result(signals, execution_params)
    
    def _validate_basic_requirements(self, signals: List[ExecutionSignal]) -> Dict[str, Any]:
        """Validate basic signal requirements"""
        if not signals:
            return {'passed': False, 'reason': 'No signals provided'}
        
        # Check for minimum signal quality
        valid_signals = [s for s in signals if s.data_quality == 'live' and s.confidence > 0.5]
        if len(valid_signals) < 2:
            return {'passed': False, 'reason': f'Only {len(valid_signals)} valid signals (need ≥2)'}
        
        # Check for conflicting directions
        directions = [s.direction for s in valid_signals if s.direction in ['BUY', 'SELL']]
        if len(set(directions)) > 1:
            return {'passed': False, 'reason': f'Conflicting directions: {set(directions)}'}
        
        return {'passed': True, 'reason': 'Basic validation passed'}
    
    def _validate_multi_horizon_consensus(self, signals: List[ExecutionSignal]) -> Dict[str, Any]:
        """Validate that multiple horizons agree"""
        horizon_signals = {}
        for signal in signals:
            if signal.data_quality == 'live':
                horizon_signals[signal.horizon] = signal
        
        # Need at least 2 horizons
        if len(horizon_signals) < 2:
            return {'passed': False, 'reason': f'Only {len(horizon_signals)} horizons (need ≥2)'}
        
        # Check direction consensus
        directions = [s.direction for s in horizon_signals.values() if s.direction in ['BUY', 'SELL']]
        if not directions:
            return {'passed': False, 'reason': 'No clear directional signals'}
        
        # Calculate consensus percentage
        primary_direction = max(set(directions), key=directions.count)
        consensus_pct = directions.count(primary_direction) / len(directions)
        
        if consensus_pct < self.consensus_threshold:
            return {'passed': False, 'reason': f'Consensus {consensus_pct:.1%} < {self.consensus_threshold:.1%}'}
        
        return {'passed': True, 'reason': f'{consensus_pct:.1%} consensus on {primary_direction}'}
    
    def _validate_confidence_threshold(self, signals: List[ExecutionSignal]) -> Dict[str, Any]:
        """Validate institutional confidence threshold"""
        valid_signals = [s for s in signals if s.data_quality == 'live']
        
        if not valid_signals:
            return {'passed': False, 'reason': 'No valid signals for confidence check'}
        
        # Calculate weighted average confidence
        total_weight = 0
        weighted_confidence = 0
        
        weights = {'next_day': 0.4, 'swing': 0.35, 'intraday': 0.25}
        
        for signal in valid_signals:
            weight = weights.get(signal.horizon, 0.2)
            weighted_confidence += signal.confidence * weight
            total_weight += weight
        
        avg_confidence = weighted_confidence / total_weight if total_weight > 0 else 0
        
        if avg_confidence < self.institutional_threshold:
            return {'passed': False, 'reason': f'Confidence {avg_confidence:.1%} < {self.institutional_threshold:.1%}'}
        
        return {'passed': True, 'reason': f'Confidence {avg_confidence:.1%} meets threshold'}
    
    def _validate_risk_reward(self, signals: List[ExecutionSignal]) -> Dict[str, Any]:
        """Validate risk-reward parameters"""
        valid_signals = [s for s in signals if s.data_quality == 'live']
        
        for signal in valid_signals:
            # Check ATR risk vs expected move
            if signal.atr_risk > 0 and signal.expected_move > 0:
                atr_multiple = signal.expected_move / signal.atr_risk
                
                if atr_multiple > self.max_atr_multiplier:
                    return {
                        'passed': False, 
                        'reason': f'{signal.horizon} ATR multiple {atr_multiple:.1f}x > {self.max_atr_multiplier}x'
                    }
        
        # Calculate average risk-reward
        risk_rewards = []
        for signal in valid_signals:
            if signal.atr_risk > 0:
                rr = signal.expected_move / signal.atr_risk
                risk_rewards.append(rr)
        
        if risk_rewards:
            avg_rr = np.mean(risk_rewards)
            if avg_rr < 1.5:  # Minimum 1.5:1 risk-reward
                return {'passed': False, 'reason': f'Risk-reward {avg_rr:.1f}:1 < 1.5:1'}
        
        return {'passed': True, 'reason': 'Risk-reward validation passed'}
    
    def _validate_market_conditions(self, market_conditions: Dict[str, Any]) -> Dict[str, Any]:
        """Validate current market conditions"""
        
        # Check market session
        if not market_conditions.get('market_open', False):
            return {'passed': False, 'reason': 'Market not open'}
        
        # Check volatility regime
        vix = market_conditions.get('vix', 20)
        if vix > 40:  # High fear
            return {'passed': False, 'reason': f'VIX too high: {vix:.1f}'}
        
        # Check if close to earnings
        days_to_earnings = market_conditions.get('days_to_earnings', 30)
        if days_to_earnings < 2:
            return {'passed': False, 'reason': f'Too close to earnings: {days_to_earnings} days'}
        
        return {'passed': True, 'reason': 'Market conditions favorable'}
    
    def _calculate_execution_parameters(self, signals: List[ExecutionSignal], 
                                      market_conditions: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate final execution parameters"""
        valid_signals = [s for s in signals if s.data_quality == 'live']
        
        # Determine primary direction
        directions = [s.direction for s in valid_signals if s.direction in ['BUY', 'SELL']]
        primary_direction = max(set(directions), key=directions.count)
        
        # Calculate position size based on consensus
        consensus_pct = directions.count(primary_direction) / len(directions)
        
        if consensus_pct >= 0.90:
            position_size = 0.07  # 7% max
        elif consensus_pct >= 0.85:
            position_size = 0.05  # 5%
        elif consensus_pct >= 0.80:
            position_size = 0.03  # 3%
        else:
            position_size = 0.01  # 1% minimum
        
        # Calculate weighted confidence
        weights = {'next_day': 0.4, 'swing': 0.35, 'intraday': 0.25}
        total_weight = 0
        weighted_confidence = 0
        
        for signal in valid_signals:
            weight = weights.get(signal.horizon, 0.2)
            weighted_confidence += signal.confidence * weight
            total_weight += weight
        
        final_confidence = weighted_confidence / total_weight if total_weight > 0 else 0
        
        # Calculate risk parameters
        avg_atr_risk = np.mean([s.atr_risk for s in valid_signals if s.atr_risk > 0])
        avg_expected_move = np.mean([s.expected_move for s in valid_signals if s.expected_move > 0])
        
        return {
            'direction': primary_direction,
            'position_size': position_size,
            'confidence': final_confidence,
            'consensus_pct': consensus_pct,
            'risk_per_share': avg_atr_risk,
            'expected_move': avg_expected_move,
            'risk_reward_ratio': avg_expected_move / avg_atr_risk if avg_atr_risk > 0 else 0,
            'participating_horizons': [s.horizon for s in valid_signals]
        }
    
    def _create_rejection_result(self, stage: str, reason: str) -> Dict[str, Any]:
        """Create standardized rejection result"""
        return {
            'execute': False,
            'action': 'HOLD',
            'stage_failed': stage,
            'reason': reason,
            'position_size': 0.0,
            'confidence': 0.0,
            'risk_level': 'HIGH',
            'validation_details': {
                'basic_validation': stage == 'BASIC_VALIDATION',
                'consensus_check': stage != 'BASIC_VALIDATION',
                'confidence_check': stage not in ['BASIC_VALIDATION', 'CONSENSUS'],
                'risk_check': stage not in ['BASIC_VALIDATION', 'CONSENSUS', 'CONFIDENCE'],
                'market_check': stage == 'MARKET_CONDITIONS'
            }
        }
    
    def _create_approval_result(self, signals: List[ExecutionSignal], 
                              execution_params: Dict[str, Any]) -> Dict[str, Any]:
        """Create standardized approval result"""
        return {
            'execute': True,
            'action': execution_params['direction'],
            'position_size': execution_params['position_size'],
            'confidence': execution_params['confidence'],
            'consensus_pct': execution_params['consensus_pct'],
            'risk_reward_ratio': execution_params['risk_reward_ratio'],
            'participating_horizons': execution_params['participating_horizons'],
            'risk_level': self._calculate_risk_level(execution_params),
            'reason': f"All guardrails passed: {execution_params['consensus_pct']:.1%} consensus",
            'validation_details': {
                'basic_validation': True,
                'consensus_check': True,
                'confidence_check': True,
                'risk_check': True,
                'market_check': True
            },
            'execution_summary': {
                'institutional_grade': execution_params['confidence'] >= self.institutional_threshold,
                'multi_horizon_confirmed': len(execution_params['participating_horizons']) >= 2,
                'risk_controlled': execution_params['risk_reward_ratio'] >= 1.5
            }
        }
    
    def _calculate_risk_level(self, execution_params: Dict[str, Any]) -> str:
        """Calculate overall risk level for execution"""
        confidence = execution_params.get('confidence', 0)
        consensus = execution_params.get('consensus_pct', 0)
        risk_reward = execution_params.get('risk_reward_ratio', 0)
        
        if confidence >= 0.85 and consensus >= 0.90 and risk_reward >= 2.0:
            return 'LOW'
        elif confidence >= 0.75 and consensus >= 0.80 and risk_reward >= 1.5:
            return 'MEDIUM'
        else:
            return 'HIGH'

# Global execution guardrails
execution_guardrails = ExecutionGuardrails()