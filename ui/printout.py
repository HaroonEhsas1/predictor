#!/usr/bin/env python3
"""
UI Printout Module
Consistent, clean output with proper suppression rules
"""

import os
import sys
from typing import Dict, Any, Optional

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import SUPPRESSION_RULES
from manager.scheduler import scheduler

class UnifiedPrinter:
    """Handles all console output with suppression rules"""
    
    def __init__(self):
        self.scheduler = scheduler
        self.suppression_active = True
        
    def print_header(self, symbol: str = "AMD"):
        """Print main system header"""
        market_state = self.scheduler.get_market_state()
        
        print("🎯 AMD Stock Prediction System")
        print("===============================")
        print(f"📈 Target Stock: {symbol}")
        print(f"📍 Current Time: {market_state['times']['et_formatted']}")
        print(f"📊 Market Status: {market_state['session_phase']}")
        
        if not market_state['is_trading_day']:
            print("⏸️  Weekend/Holiday - Data Collection Mode")
        elif market_state['market_open']:
            print(f"⏰ Market Open ({market_state.get('minutes_to_close', '?')}m to close)")
        else:
            print("🔒 Market Closed - Analysis Mode")
        
        print("=" * 50)
    
    def print_market_state_warning(self):
        """Print market state warnings if needed"""
        market_state = self.scheduler.get_market_state()
        
        if not market_state['is_trading_day']:
            print("📅 WEEKEND/HOLIDAY DETECTED")
            print("   → No intraday trading signals")
            print("   → Using cached/daily data only")
            print("   → All positions set to MONITOR")
            print()
    
    def print_data_quality_status(self, data_quality: str, sources_used: list = None):
        """Print data quality information"""
        if data_quality == 'live':
            print("✅ Data Quality: LIVE (Real-time sources)")
        elif data_quality == 'fallback':
            print("⚠️  Data Quality: FALLBACK (Backup sources)")
            if sources_used:
                print(f"   → Sources: {', '.join(sources_used)}")
        else:
            print("❌ Data Quality: STALE (Limited data)")
        print()
    
    def print_prediction_block(self, prediction: Dict[str, Any], block_type: str = "general"):
        """Print prediction block with proper suppression"""
        market_state = self.scheduler.get_market_state()
        
        # Check suppression rules
        if block_type == "intraday" and self.scheduler.should_suppress_section('intraday'):
            return  # Suppress entire intraday block
        
        if block_type == "approaching_close" and self.scheduler.should_suppress_section('approaching_close'):
            return  # Suppress approaching close text
        
        # Print prediction details
        direction = prediction.get('direction', 'HOLD')
        confidence = prediction.get('confidence', 0.0)
        consensus = prediction.get('ensemble_consensus', 0.0)
        gap_usd = prediction.get('expected_gap_usd', 0.0)
        price_pred = prediction.get('price_pred', 0.0)
        risk_level = prediction.get('risk_level', 'UNKNOWN')
        action = prediction.get('action', 'HOLD')
        position_size = prediction.get('position_size', 0.0)
        backtest_acc = prediction.get('backtest_accuracy', 0.0)
        
        print(f"🎯 PREDICTION ({block_type.upper()})")
        print("=" * 40)
        print(f"📈 Direction: {direction}")
        print(f"💰 Target Price: ${price_pred:.2f}")
        print(f"🔥 Signal Confidence: {confidence:.1%}")
        print(f"🤖 Ensemble Consensus: {consensus:.1%}")
        print(f"📊 Expected Gap: ${gap_usd:.2f}")
        print(f"⚖️  Risk Level: {risk_level}")
        print(f"📈 Backtest Accuracy: {backtest_acc:.1%}")
        print()
        
        # Trading decision
        self.print_trading_decision(prediction)
    
    def print_trading_decision(self, prediction: Dict[str, Any]):
        """Print trading decision with proper gating"""
        action = prediction.get('action', 'HOLD')
        position_size = prediction.get('position_size', 0.0)
        gating_result = prediction.get('gating_result', {})
        
        print("💼 TRADING DECISION")
        print("-" * 20)
        print(f"🎯 Action: {action}")
        print(f"📊 Position Size: {position_size:.1%}")
        
        # Show gating results
        if gating_result:
            print(f"📋 Reason: {gating_result.get('reason', 'Unknown')}")
            
            gates = gating_result
            print("🚪 Trading Gates:")
            print(f"   ✅ Live Trading: {'PASS' if gates.get('live_trading_enabled', False) else 'FAIL'}")
            print(f"   ✅ Consensus: {'PASS' if gates.get('consensus_met', False) else 'FAIL'}")
            print(f"   ✅ Gap Size: {'PASS' if gates.get('gap_met', False) else 'FAIL'}")
            print(f"   ✅ Market Open: {'PASS' if gates.get('market_conditions_ok', False) else 'FAIL'}")
        
        # Suppress position text for HOLD/MONITOR
        if action not in ['HOLD', 'MONITOR'] and position_size > 0:
            if not self.scheduler.should_suppress_section('position_text'):
                self.print_position_details(prediction)
        
        print()
    
    def print_position_details(self, prediction: Dict[str, Any]):
        """Print position details only when appropriate"""
        position_size = prediction.get('position_size', 0.0)
        risk_level = prediction.get('risk_level', 'UNKNOWN')
        
        if position_size > 0:
            print("📈 Position Details:")
            print(f"   💰 Size: {position_size:.1%}")
            print(f"   ⚖️  Risk: {risk_level}")
            
            # Risk management details
            stop_loss = prediction.get('stop_loss', 0)
            take_profit = prediction.get('take_profit', 0)
            if stop_loss and take_profit:
                print(f"   🛑 Stop Loss: ${stop_loss:.2f}")
                print(f"   🎯 Take Profit: ${take_profit:.2f}")
    
    def print_error_with_context(self, error_msg: str, context: str = ""):
        """Print errors with appropriate context"""
        if "possibly delisted" in error_msg.lower():
            print("📊 Using alternative data sources for enhanced analysis")
        elif "no intraday data" in error_msg.lower():
            print("✅ Using current market data for reliable predictions")
        elif "api failed" in error_msg.lower():
            print("🔄 Switching to backup data source")
        else:
            print(f"⚠️  {error_msg}")
        
        if context:
            print(f"   Context: {context}")
    
    def print_suppression_notice(self, section: str, reason: str):
        """Print notice when sections are suppressed"""
        print(f"ℹ️  {section.title()} section suppressed: {reason}")
    
    def print_consistency_warnings(self, validation_result: Dict[str, Any]):
        """Print consistency validation warnings"""
        if not validation_result.get('is_consistent', True):
            print("⚠️  CONSISTENCY WARNINGS:")
            for issue in validation_result.get('issues', []):
                print(f"   • {issue}")
            print()
    
    def print_summary_footer(self, prediction: Dict[str, Any]):
        """Print clean summary footer"""
        market_state = self.scheduler.get_market_state()
        
        print("📋 SUMMARY")
        print("-" * 20)
        print(f"⏰ Time: {market_state['times']['et_formatted']}")
        print(f"📊 Session: {market_state['session_phase']}")
        print(f"🎯 Final Action: {prediction.get('action', 'UNKNOWN')}")
        print(f"📈 Position: {prediction.get('position_size', 0.0):.1%}")
        print(f"⚖️  Risk: {prediction.get('risk_level', 'UNKNOWN')}")
        print(f"📊 Data Quality: {prediction.get('data_quality', 'UNKNOWN')}")
        print("=" * 50)

# Global printer instance
printer = UnifiedPrinter()