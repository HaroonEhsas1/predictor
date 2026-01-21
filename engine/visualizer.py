#!/usr/bin/env python3
"""
Engine Visualizer for Professional Stock Prediction Engine
Integrates with existing visualization systems
"""

import os
import sys
from typing import Dict, List, Any, Optional
import warnings
warnings.filterwarnings('ignore')

# Import existing visualization components
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class EngineVisualizer:
    """
    Professional visualization system for the engine
    Extends existing visualization capabilities
    """
    
    def __init__(self):
        """Initialize engine visualizer"""
        # Try to integrate with existing visualization systems
        try:
            from ui.printout import printer
            from visualizations.chart_generator import ChartGenerator
            from visualization_manager import VisualizationManager
            
            self.printer = printer
            self.chart_generator = ChartGenerator()
            self.viz_manager = VisualizationManager()
            self.existing_available = True
            print("✅ Integrated with existing visualization systems")
            
        except ImportError as e:
            print(f"⚠️  Some visualization components not available: {e}")
            self.existing_available = False
        
        print("✅ EngineVisualizer initialized")
    
    def display_intraday_prediction(self, prediction: Dict[str, Any], symbol: str):
        """Display intraday prediction results"""
        try:
            if self.existing_available:
                # Use existing printer for consistent output
                self.printer.print_prediction_block(prediction, "intraday")
            else:
                # Fallback display
                self._fallback_display_prediction(prediction, "Intraday")
                
        except Exception as e:
            print(f"⚠️  Intraday visualization error: {str(e)[:50]}")
            self._fallback_display_prediction(prediction, "Intraday")
    
    def display_nextday_prediction(self, prediction: Dict[str, Any], symbol: str):
        """Display next-day prediction results"""
        try:
            if self.existing_available:
                self.printer.print_prediction_block(prediction, "nextday")
            else:
                self._fallback_display_prediction(prediction, "Next-Day")
                
        except Exception as e:
            print(f"⚠️  Next-day visualization error: {str(e)[:50]}")
            self._fallback_display_prediction(prediction, "Next-Day")
    
    def display_comprehensive_analysis(self, analysis: Dict[str, Any]):
        """Display comprehensive analysis results"""
        try:
            symbol = analysis.get('symbol', 'UNKNOWN')
            print(f"\n🔍 COMPREHENSIVE ANALYSIS - {symbol}")
            print("=" * 60)
            
            # Market state
            market_state = analysis.get('market_state', 'Unknown')
            print(f"📊 Market State: {market_state}")
            
            # Predictions summary
            predictions = analysis.get('predictions', {})
            if predictions:
                print(f"\n📈 Active Predictions: {len(predictions)}")
                for pred_type, pred_data in predictions.items():
                    direction = pred_data.get('direction', 'UNKNOWN')
                    confidence = pred_data.get('confidence', 0.0) * 100
                    print(f"   {pred_type}: {direction} ({confidence:.1f}%)")
            
            # Summary
            summary = analysis.get('summary', {})
            if summary:
                consensus = summary.get('consensus_direction', 'SIDEWAYS')
                avg_conf = summary.get('average_confidence', 0.0) * 100
                print(f"\n🎯 Consensus: {consensus} ({avg_conf:.1f}% avg confidence)")
            
            # Recommendations
            recommendations = analysis.get('recommendations', {})
            if recommendations:
                rec = recommendations.get('recommendation', 'HOLD')
                size = recommendations.get('position_size', 0.0) * 100
                print(f"💡 Recommendation: {rec}")
                if size > 0:
                    print(f"📊 Suggested Position: {size:.1f}%")
            
            print("=" * 60)
            
        except Exception as e:
            print(f"⚠️  Comprehensive analysis display error: {str(e)[:50]}")
    
    def display_engine_status(self, status: Dict[str, Any]):
        """Display engine status and performance metrics"""
        try:
            print("\n⚙️  ENGINE STATUS")
            print("=" * 40)
            
            # Component status
            components = status.get('components', {})
            for component, available in components.items():
                status_icon = "✅" if available else "❌"
                print(f"{status_icon} {component}")
            
            # Performance metrics
            performance = status.get('performance', {})
            if performance:
                print(f"\n📊 Performance Metrics:")
                for metric, value in performance.items():
                    if isinstance(value, float):
                        print(f"   {metric}: {value:.3f}")
                    else:
                        print(f"   {metric}: {value}")
            
            # Cache status
            cache_info = status.get('cache', {})
            if cache_info:
                hit_rate = cache_info.get('hit_rate', 0.0) * 100
                print(f"\n💾 Cache Hit Rate: {hit_rate:.1f}%")
            
            print("=" * 40)
            
        except Exception as e:
            print(f"⚠️  Engine status display error: {str(e)[:50]}")
    
    def _fallback_display_prediction(self, prediction: Dict[str, Any], pred_type: str):
        """Fallback display for predictions when existing system unavailable"""
        try:
            print(f"\n📊 {pred_type.upper()} PREDICTION")
            print("-" * 30)
            
            direction = prediction.get('direction', 'UNKNOWN')
            confidence = prediction.get('confidence', 0.0) * 100
            target_price = prediction.get('target_price', 0.0)
            
            print(f"Direction: {direction}")
            print(f"Confidence: {confidence:.1f}%")
            
            if target_price > 0:
                print(f"Target Price: ${target_price:.2f}")
            
            expected_return = prediction.get('expected_return_pct', 0.0)
            if abs(expected_return) > 0.1:
                print(f"Expected Return: {expected_return:.2f}%")
            
            risk_level = prediction.get('risk_level', 'UNKNOWN')
            print(f"Risk Level: {risk_level}")
            
            print("-" * 30)
            
        except Exception as e:
            print(f"⚠️  Fallback display error: {str(e)[:30]}")

# Create global instance
engine_visualizer = EngineVisualizer()