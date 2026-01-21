#!/usr/bin/env python3
"""
Professional Trader Integration Module
Replaces all neutral/HOLD logic with decisive directional predictions
"""

from professional_trader_system import ProfessionalTraderSystem
from typing import Dict, Any, Optional
import logging

class ProfessionalTraderIntegration:
    """
    Integration layer that eliminates ALL neutral zones and always provides directional signals
    Designed to replace the over-engineered confidence thresholds and neutral logic
    """
    
    def __init__(self, symbol: str = "AMD"):
        self.professional_system = ProfessionalTraderSystem(symbol)
        self.symbol = symbol
        
        # NO CONFIDENCE THRESHOLDS - Professional traders don't need artificial limits
        # NO NEUTRAL ZONES - Market always moves up or down
        # NO GATING SYSTEMS - Professional traders make decisions with available information
        
        print(f"🎯 Professional Integration initialized - ZERO neutral zones, ALWAYS directional")
    
    def replace_neutral_prediction(self, original_prediction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Replace any neutral/HOLD/WAIT prediction with a professional directional prediction
        This is the core function that eliminates indecision
        """
        
        # Check if original prediction is neutral/indecisive
        original_direction = original_prediction.get('direction', '').upper()
        original_signal = original_prediction.get('signal', '').upper()
        original_decision = original_prediction.get('decision', '').upper()
        
        neutral_indicators = ['NEUTRAL', 'HOLD', 'WAIT', 'NO_TRADE', 'STABLE', 'SIDEWAYS', 'SKIP']
        
        is_neutral = any(indicator in [original_direction, original_signal, original_decision] for indicator in neutral_indicators)
        
        if is_neutral:
            print(f"🚨 REPLACING NEUTRAL SIGNAL: {original_direction}/{original_signal}/{original_decision}")
            
            # Get professional trader decision
            professional_prediction = self.professional_system.predict_direction()
            
            # Override with professional decision
            enhanced_prediction = original_prediction.copy()
            enhanced_prediction.update({
                'direction': professional_prediction['direction'],  # Always UP or DOWN
                'signal': 'BUY' if professional_prediction['direction'] == 'UP' else 'SELL',
                'decision': professional_prediction['direction'],
                'confidence': professional_prediction['confidence'],
                'target_price': professional_prediction['target_price'],
                'expected_move': professional_prediction['expected_move'],
                'reasoning': professional_prediction['reasoning'],
                'professional_override': True,
                'original_was_neutral': True,
                'data_sources': professional_prediction['data_sources_used']
            })
            
            print(f"✅ PROFESSIONAL OVERRIDE: {professional_prediction['direction']} with {professional_prediction['confidence']:.1f}% confidence")
            return enhanced_prediction
        
        else:
            # Original prediction was already directional, enhance it with professional analysis
            return self._enhance_directional_prediction(original_prediction)
    
    def _enhance_directional_prediction(self, prediction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance already directional predictions with professional trader analysis
        """
        try:
            # Get professional analysis for confirmation
            professional_prediction = self.professional_system.predict_direction()
            
            enhanced_prediction = prediction.copy()
            
            # Add professional confirmation
            enhanced_prediction['professional_confirmation'] = {
                'professional_direction': professional_prediction['direction'],
                'professional_confidence': professional_prediction['confidence'],
                'alignment': prediction.get('direction', '').upper() == professional_prediction['direction'],
                'reasoning_summary': professional_prediction['reasoning'][:3]  # Top 3 reasons
            }
            
            # If professional system disagrees significantly, log it but keep original
            if enhanced_prediction['professional_confirmation']['alignment']:
                enhanced_prediction['confidence'] = min(
                    enhanced_prediction.get('confidence', 50) + 10,  # Boost confidence when aligned
                    95
                )
            
            return enhanced_prediction
            
        except Exception as e:
            print(f"⚠️ Professional enhancement failed: {e}")
            return prediction
    
    def force_directional_decision(self, signals: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Force a directional decision - replaces _resolve_final_decision logic
        NEVER returns NO_TRADE or neutral - always UP or DOWN
        """
        
        print("🎯 FORCING DIRECTIONAL DECISION - No neutral allowed")
        
        # Get professional trader decision
        professional_prediction = self.professional_system.predict_direction()
        
        # Extract useful info from original signals if available
        original_confidence = signals.get('confidence', 0)
        original_expected_move = signals.get('expected_move', 0)
        
        # Professional trader decision - always directional
        forced_decision = {
            'decision': professional_prediction['direction'],  # Always UP or DOWN
            'direction': professional_prediction['direction'],
            'signal': 'BUY' if professional_prediction['direction'] == 'UP' else 'SELL',
            'confidence': professional_prediction['confidence'],
            'expected_move': professional_prediction['expected_move'],
            'target_price': professional_prediction['target_price'],
            'current_price': professional_prediction['current_price'],
            'reasoning': professional_prediction['reasoning'],
            'professional_forced': True,
            'original_confidence': original_confidence,
            'original_expected_move': original_expected_move,
            'audit': {
                'rules_applied': 'Professional trader - no neutral zones',
                'checks_failed': ['Professional traders always decide'],
                'professional_override': True
            }
        }
        
        print(f"✅ FORCED DECISION: {forced_decision['decision']} with {forced_decision['confidence']:.1f}% confidence")
        return forced_decision
    
    def eliminate_confidence_gating(self, original_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Eliminate confidence gating that blocks trades
        Professional traders work with available information, not artificial thresholds
        """
        
        # Check if original result was blocked by confidence gating
        trade_signal = original_result.get('trade_signal', '')
        gate_reasons = original_result.get('gate_reasons', [])
        
        confidence_blocked = any('confidence' in reason.lower() for reason in gate_reasons)
        consensus_blocked = any('consensus' in reason.lower() for reason in gate_reasons)
        gap_blocked = any('gap' in reason.lower() for reason in gate_reasons)
        
        if confidence_blocked or consensus_blocked or gap_blocked or trade_signal in ['NO_TRADE', 'HOLD', 'WAIT']:
            print(f"🚨 ELIMINATING GATING: {gate_reasons}")
            
            # Get professional trader decision to override gating
            professional_prediction = self.professional_system.predict_direction()
            
            # Override gated result
            ungated_result = original_result.copy()
            ungated_result.update({
                'trade_signal': professional_prediction['direction'],
                'direction': professional_prediction['direction'],
                'confidence': professional_prediction['confidence'],
                'position_size': self._calculate_professional_position_size(professional_prediction['confidence']),
                'target_price': professional_prediction['target_price'],
                'expected_move': professional_prediction['expected_move'],
                'gate_reasons': ['Professional trader override - no artificial thresholds'],
                'passed_gates': ['Professional analysis complete'],
                'professional_override': True,
                'original_gate_reasons': gate_reasons
            })
            
            print(f"✅ GATING ELIMINATED: {professional_prediction['direction']} signal with {professional_prediction['confidence']:.1f}% confidence")
            return ungated_result
        
        return original_result
    
    def _calculate_professional_position_size(self, confidence: float) -> float:
        """
        Calculate position size based on professional trader confidence
        No artificial minimums - scale with confidence
        """
        
        # Professional traders scale position with conviction
        # Higher confidence = larger position (within risk limits)
        base_position = 0.02  # 2% base position
        confidence_multiplier = confidence / 100  # Scale 0-1
        
        position_size = base_position * confidence_multiplier
        
        # Risk controls: cap position size and ensure meaningful minimums
        max_position = 0.05  # Maximum 5% position for safety
        min_position = 0.002 if confidence > 50 else 0.001  # Scale minimum with confidence
        
        return max(min(position_size, max_position), min_position)
    
    def replace_scalper_hold_logic(self, scalper_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Replace scalper HOLD logic with directional signals
        """
        
        if scalper_result.get('direction') == 'HOLD' or scalper_result.get('confidence', 0) == 0:
            print("🚨 REPLACING SCALPER HOLD with professional signal")
            
            # Get professional short-term prediction
            professional_prediction = self.professional_system.predict_direction()
            
            # Override HOLD with directional signal
            enhanced_result = scalper_result.copy()
            enhanced_result.update({
                'direction': professional_prediction['direction'],
                'confidence': professional_prediction['confidence'],
                'target_profit': abs(professional_prediction['expected_move']),
                'stop_loss': abs(professional_prediction['expected_move']) * 0.5,  # 2:1 ratio
                'reason': f"Professional override: {professional_prediction['reasoning'][0]}",
                'professional_scalper_override': True
            })
            
            return enhanced_result
        
        return scalper_result
    
    def get_always_directional_prediction(self) -> Dict[str, Any]:
        """
        Main entry point for getting a prediction that is ALWAYS directional
        This replaces any function that might return neutral
        """
        
        print("🎯 GENERATING ALWAYS-DIRECTIONAL PREDICTION")
        
        # Get comprehensive professional trader analysis
        prediction = self.professional_system.predict_direction()
        
        # Ensure it's properly formatted for integration
        directional_prediction = {
            'direction': prediction['direction'],  # Always UP or DOWN
            'signal': 'BUY' if prediction['direction'] == 'UP' else 'SELL',
            'decision': prediction['direction'],
            'confidence': prediction['confidence'],  # Always >= 55%
            'current_price': prediction['current_price'],
            'target_price': prediction['target_price'],
            'expected_move': prediction['expected_move'],
            'position_size': self._calculate_professional_position_size(prediction['confidence']),
            'reasoning': prediction['reasoning'],
            'signals_summary': prediction['signals_summary'],
            'data_sources': prediction['data_sources_used'],
            'timestamp': prediction['timestamp'],
            'professional_system': True,
            'never_neutral': True
        }
        
        print(f"✅ DIRECTIONAL PREDICTION: {directional_prediction['direction']} ({directional_prediction['confidence']:.1f}%)")
        return directional_prediction

# Global integration instance
professional_integration = ProfessionalTraderIntegration()

# Helper functions to replace neutral logic throughout the codebase

def force_directional_decision(signals: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Replace _resolve_final_decision - NEVER returns NO_TRADE"""
    return professional_integration.force_directional_decision(signals, context)

def eliminate_gating_logic(result: Dict[str, Any]) -> Dict[str, Any]:
    """Replace gating systems that block trades"""
    return professional_integration.eliminate_confidence_gating(result)

def replace_neutral_prediction(prediction: Dict[str, Any]) -> Dict[str, Any]:
    """Replace any neutral prediction with directional one"""
    return professional_integration.replace_neutral_prediction(prediction)

def get_professional_prediction() -> Dict[str, Any]:
    """Get a guaranteed directional prediction"""
    return professional_integration.get_always_directional_prediction()

def replace_scalper_hold(scalper_result: Dict[str, Any]) -> Dict[str, Any]:
    """Replace scalper HOLD signals"""
    return professional_integration.replace_scalper_hold_logic(scalper_result)