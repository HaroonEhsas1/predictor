#!/usr/bin/env python3
"""
Professional Stock Prediction Engine - Main Coordinator
Unified engine combining intraday ML ensemble and next-day gap analysis
"""

import os
import sys
import time
import asyncio
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import warnings
warnings.filterwarnings('ignore')

# Import existing system components
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from manager.scheduler import scheduler
from config import TRADING_RULES, MODEL_CONFIG

@dataclass
class EngineStatus:
    """Container for engine status"""
    components_loaded: Dict[str, bool]
    performance_metrics: Dict[str, float]
    last_predictions: Dict[str, Any]
    training_status: Dict[str, Any]
    cache_stats: Dict[str, Any]
    uptime_seconds: float
    total_predictions: int
    error_count: int

class ProfessionalEngine:
    """
    Professional Stock Prediction Engine
    Main coordinator for the entire prediction system
    """
    
    def __init__(self, symbol: str = "AMD"):
        """Initialize the professional engine"""
        self.symbol = symbol
        self.start_time = time.time()
        self.total_predictions = 0
        self.error_count = 0
        
        # Component availability tracking
        self.components = {
            'data_collector': False,
            'feature_engineer': False,
            'intraday_ensemble': False,
            'gap_predictor': False,
            'model_trainer': False,
            'unified_predictor': False,
            'visualizer': False,
            'logger': False
        }
        
        # Initialize all engine components
        self._initialize_engine_components()
        
        # Scheduling and automation
        self.scheduler_thread = None
        self.scheduler_active = False
        
        # Performance tracking
        self.performance_metrics = {
            'avg_prediction_time_ms': 0.0,
            'cache_hit_rate': 0.0,
            'model_accuracy': 0.0,
            'data_quality_score': 0.0
        }
        
        print("✅ Professional Stock Prediction Engine initialized")
        print(f"🎯 Target Symbol: {self.symbol}")
        print(f"⚙️  Components Loaded: {sum(self.components.values())}/{len(self.components)}")
    
    def run_comprehensive_prediction(self) -> Dict[str, Any]:
        """
        Run comprehensive prediction analysis
        Main entry point for complete prediction cycle
        """
        prediction_start = time.time()
        
        try:
            print(f"\n🔄 Running comprehensive prediction for {self.symbol}...")
            
            # Get market state
            market_state = scheduler.get_market_state()
            
            # Initialize result structure
            comprehensive_result = {
                'symbol': self.symbol,
                'timestamp': datetime.now().isoformat(),
                'market_state': market_state['session_phase'],
                'engine_status': self._get_engine_status(),
                'predictions': {},
                'analysis': {},
                'recommendations': {},
                'performance': {}
            }
            
            # Run appropriate predictions based on market state
            if market_state['market_open']:
                # Market open - run intraday predictions
                comprehensive_result['predictions'].update(
                    self._run_intraday_predictions()
                )
                
                # If near market close, also prepare next-day analysis
                if market_state.get('minutes_to_close', 400) < 60:
                    comprehensive_result['predictions']['nextday_prep'] = self._run_nextday_preclose()
                    
            elif market_state.get('pre_market'):
                # Pre-market - run pre-open analysis
                comprehensive_result['predictions']['preopen'] = self._run_nextday_preopen()
                
            else:
                # After hours or weekend - run next-day analysis
                comprehensive_result['predictions']['nextday'] = self._run_nextday_preclose()
            
            # Generate comprehensive analysis
            if comprehensive_result['predictions']:
                comprehensive_result['analysis'] = self._generate_comprehensive_analysis(
                    comprehensive_result['predictions']
                )
                
                comprehensive_result['recommendations'] = self._generate_trading_recommendations(
                    comprehensive_result['analysis']
                )
            
            # Performance metrics
            prediction_time = (time.time() - prediction_start) * 1000
            comprehensive_result['performance'] = {
                'total_prediction_time_ms': prediction_time,
                'predictions_generated': len(comprehensive_result['predictions']),
                'engine_uptime_hours': (time.time() - self.start_time) / 3600
            }
            
            # Update counters
            self.total_predictions += len(comprehensive_result['predictions'])
            
            # Log results
            if self.components['logger']:
                self._log_comprehensive_results(comprehensive_result)
            
            # Display results
            if self.components['visualizer']:
                self._display_comprehensive_results(comprehensive_result)
            
            print(f"✅ Comprehensive prediction completed ({prediction_time:.1f}ms)")
            return comprehensive_result
            
        except Exception as e:
            self.error_count += 1
            print(f"❌ Comprehensive prediction error: {str(e)}")
            return self._create_error_result(str(e))
    
    def run_continuous_monitoring(self, interval_seconds: int = 60):
        """
        Start continuous prediction monitoring during market hours
        Automated prediction updates
        """
        if self.scheduler_active:
            print("⚠️  Scheduler already active")
            return
        
        self.scheduler_active = True
        self.scheduler_thread = threading.Thread(
            target=self._continuous_monitoring_loop,
            args=(interval_seconds,),
            daemon=True
        )
        self.scheduler_thread.start()
        
        print(f"🔄 Started continuous monitoring (every {interval_seconds}s)")
    
    def stop_continuous_monitoring(self):
        """Stop continuous monitoring"""
        self.scheduler_active = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=10)
        print("⏹️  Stopped continuous monitoring")
    
    def retrain_all_models(self) -> Dict[str, Any]:
        """
        Comprehensive model retraining
        Retrains both intraday and next-day models
        """
        print("🔄 Starting comprehensive model retraining...")
        
        try:
            if not self.components['model_trainer']:
                return {'error': 'Model trainer not available'}
            
            # Run comprehensive retraining
            training_results = self.model_trainer.retrain_all_models(self.symbol)
            
            # Log training results
            if self.components['logger'] and training_results:
                self.engine_logger.log_training_session(training_results, self.symbol)
            
            print("✅ Model retraining completed")
            return training_results
            
        except Exception as e:
            self.error_count += 1
            print(f"❌ Model retraining error: {str(e)}")
            return {'error': str(e)}
    
    def get_engine_status(self) -> EngineStatus:
        """Get comprehensive engine status"""
        return EngineStatus(
            components_loaded=self.components.copy(),
            performance_metrics=self.performance_metrics.copy(),
            last_predictions={},  # Would populate with recent predictions
            training_status=self._get_training_status(),
            cache_stats=self._get_cache_stats(),
            uptime_seconds=time.time() - self.start_time,
            total_predictions=self.total_predictions,
            error_count=self.error_count
        )
    
    def health_check(self) -> Dict[str, Any]:
        """
        Comprehensive health check of all engine components
        """
        health_status = {
            'overall_health': 'HEALTHY',
            'timestamp': datetime.now().isoformat(),
            'components': {},
            'performance': {},
            'issues': []
        }
        
        try:
            # Check each component
            for component_name, is_loaded in self.components.items():
                if is_loaded:
                    # Component is loaded, test basic functionality
                    try:
                        if component_name == 'data_collector':
                            # Test data collection
                            test_data = self.data_collector.get_intraday_features(self.symbol, '1m')
                            health_status['components'][component_name] = 'HEALTHY' if test_data else 'WARNING'
                        
                        elif component_name == 'unified_predictor':
                            # Test prediction
                            test_pred = self.unified_predictor._create_default_prediction(self.symbol, 'test')
                            health_status['components'][component_name] = 'HEALTHY' if test_pred else 'WARNING'
                        
                        else:
                            # Basic component loaded check
                            health_status['components'][component_name] = 'HEALTHY'
                            
                    except Exception as e:
                        health_status['components'][component_name] = 'ERROR'
                        health_status['issues'].append(f"{component_name}: {str(e)[:50]}")
                else:
                    health_status['components'][component_name] = 'NOT_LOADED'
                    health_status['issues'].append(f"{component_name} not loaded")
            
            # Performance checks
            error_rate = self.error_count / max(self.total_predictions, 1)
            if error_rate > 0.1:  # More than 10% error rate
                health_status['issues'].append(f"High error rate: {error_rate:.1%}")
                health_status['overall_health'] = 'WARNING'
            
            # Memory and performance checks
            uptime_hours = (time.time() - self.start_time) / 3600
            health_status['performance'] = {
                'uptime_hours': uptime_hours,
                'total_predictions': self.total_predictions,
                'error_rate': error_rate,
                'predictions_per_hour': self.total_predictions / max(uptime_hours, 0.1)
            }
            
            # Overall health determination
            healthy_components = sum(1 for status in health_status['components'].values() if status == 'HEALTHY')
            total_components = len(health_status['components'])
            
            if healthy_components < total_components * 0.5:
                health_status['overall_health'] = 'CRITICAL'
            elif len(health_status['issues']) > 0:
                health_status['overall_health'] = 'WARNING'
            
            return health_status
            
        except Exception as e:
            return {
                'overall_health': 'CRITICAL',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _initialize_engine_components(self):
        """Initialize all engine components"""
        print("🔧 Initializing engine components...")
        
        # Data Collector
        try:
            from .data_collector import data_collector
            self.data_collector = data_collector
            self.components['data_collector'] = True
        except Exception as e:
            print(f"⚠️  DataCollector initialization failed: {str(e)[:50]}")
        
        # Feature Engineer
        try:
            from .feature_engineer import feature_engineer
            self.feature_engineer = feature_engineer
            self.components['feature_engineer'] = True
        except Exception as e:
            print(f"⚠️  FeatureEngineer initialization failed: {str(e)[:50]}")
        
        # Intraday Ensemble
        try:
            from .ensemble_intraday import intraday_ensemble
            self.intraday_ensemble = intraday_ensemble
            self.components['intraday_ensemble'] = True
        except Exception as e:
            print(f"⚠️  IntradayEnsemble initialization failed: {str(e)[:50]}")
        
        # Gap Predictor
        try:
            from .gap_nextday import gap_nextday_predictor
            self.gap_predictor = gap_nextday_predictor
            self.components['gap_predictor'] = True
        except Exception as e:
            print(f"⚠️  GapPredictor initialization failed: {str(e)[:50]}")
        
        # Model Trainer
        try:
            from .trainer import model_trainer
            self.model_trainer = model_trainer
            self.components['model_trainer'] = True
        except Exception as e:
            print(f"⚠️  ModelTrainer initialization failed: {str(e)[:50]}")
        
        # Unified Predictor
        try:
            from .predictor import unified_predictor
            self.unified_predictor = unified_predictor
            self.components['unified_predictor'] = True
        except Exception as e:
            print(f"⚠️  UnifiedPredictor initialization failed: {str(e)[:50]}")
        
        # Visualizer
        try:
            from .visualizer import engine_visualizer
            self.engine_visualizer = engine_visualizer
            self.components['visualizer'] = True
        except Exception as e:
            print(f"⚠️  EngineVisualizer initialization failed: {str(e)[:50]}")
        
        # Logger
        try:
            from .logger import engine_logger
            self.engine_logger = engine_logger
            self.components['logger'] = True
        except Exception as e:
            print(f"⚠️  EngineLogger initialization failed: {str(e)[:50]}")
    
    def _run_intraday_predictions(self) -> Dict[str, Any]:
        """Run intraday predictions (1-minute and swing)"""
        intraday_predictions = {}
        
        try:
            if self.components['unified_predictor']:
                # 1-minute prediction
                pred_1m = self.unified_predictor.predict_1minute(self.symbol)
                intraday_predictions['1_minute'] = pred_1m.__dict__
                
                # Swing predictions for multiple timeframes
                for timeframe in ['15m', '1h']:
                    pred_swing = self.unified_predictor.predict_swing_intraday(self.symbol, timeframe)
                    intraday_predictions[f'swing_{timeframe}'] = pred_swing.__dict__
            
        except Exception as e:
            print(f"⚠️  Intraday predictions error: {str(e)[:50]}")
            
        return intraday_predictions
    
    def _run_nextday_preclose(self) -> Dict[str, Any]:
        """Run next-day pre-close prediction"""
        try:
            if self.components['unified_predictor']:
                pred = self.unified_predictor.predict_nextday_preclose(self.symbol)
                return pred.__dict__
        except Exception as e:
            print(f"⚠️  Next-day pre-close error: {str(e)[:50]}")
        return {}
    
    def _run_nextday_preopen(self) -> Dict[str, Any]:
        """Run next-day pre-open prediction"""
        try:
            if self.components['unified_predictor']:
                pred = self.unified_predictor.predict_nextday_preopen(self.symbol)
                return pred.__dict__
        except Exception as e:
            print(f"⚠️  Next-day pre-open error: {str(e)[:50]}")
        return {}
    
    def _generate_comprehensive_analysis(self, predictions: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive analysis from all predictions"""
        try:
            if self.components['unified_predictor']:
                # Use unified predictor's analysis generation
                analysis = self.unified_predictor._generate_analysis_summary(predictions)
                return analysis
        except Exception as e:
            print(f"⚠️  Analysis generation error: {str(e)[:50]}")
        
        return {'status': 'Analysis generation failed'}
    
    def _generate_trading_recommendations(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate trading recommendations from analysis"""
        try:
            if self.components['unified_predictor']:
                # Get recommendations from predictions
                recommendations = self.unified_predictor._generate_trading_recommendations(analysis)
                return recommendations
        except Exception as e:
            print(f"⚠️  Recommendations generation error: {str(e)[:50]}")
        
        return {'recommendation': 'HOLD', 'reason': 'Analysis failed'}
    
    def _continuous_monitoring_loop(self, interval: int):
        """Continuous monitoring loop (runs in separate thread)"""
        while self.scheduler_active:
            try:
                # Run appropriate predictions based on market state
                market_state = scheduler.get_market_state()
                
                if market_state['market_open']:
                    # During market hours - run intraday predictions
                    result = self.run_comprehensive_prediction()
                    print(f"🔄 Auto-prediction completed: {len(result.get('predictions', {}))} predictions")
                
                elif market_state.get('pre_market'):
                    # Pre-market - run pre-open analysis
                    result = self._run_nextday_preopen()
                    print(f"🌅 Pre-market analysis completed")
                
                # Sleep for interval
                time.sleep(interval)
                
            except Exception as e:
                print(f"⚠️  Continuous monitoring error: {str(e)[:50]}")
                time.sleep(interval)
    
    def _log_comprehensive_results(self, results: Dict[str, Any]):
        """Log comprehensive results"""
        try:
            if self.components['logger']:
                # Log each prediction
                predictions = results.get('predictions', {})
                for pred_type, pred_data in predictions.items():
                    self.engine_logger.log_prediction(pred_data, self.symbol, pred_type)
                
                # Log performance metrics
                performance = results.get('performance', {})
                if performance:
                    self.engine_logger.log_performance_metrics(performance, 'engine')
                
                # Log engine event
                self.engine_logger.log_engine_event(
                    'comprehensive_prediction_completed',
                    {'predictions_count': len(predictions)}
                )
        except Exception as e:
            print(f"⚠️  Results logging error: {str(e)[:50]}")
    
    def _display_comprehensive_results(self, results: Dict[str, Any]):
        """Display comprehensive results"""
        try:
            if self.components['visualizer']:
                # Display comprehensive analysis
                analysis_data = {
                    'symbol': results.get('symbol'),
                    'market_state': results.get('market_state'),
                    'predictions': results.get('predictions', {}),
                    'analysis': results.get('analysis', {}),
                    'recommendations': results.get('recommendations', {})
                }
                
                self.engine_visualizer.display_comprehensive_analysis(analysis_data)
                
                # Display engine status
                engine_status = {
                    'components': self.components,
                    'performance': results.get('performance', {}),
                    'cache': self._get_cache_stats()
                }
                
                self.engine_visualizer.display_engine_status(engine_status)
                
        except Exception as e:
            print(f"⚠️  Results display error: {str(e)[:50]}")
    
    def _get_engine_status(self) -> Dict[str, Any]:
        """Get current engine status"""
        return {
            'components_loaded': sum(self.components.values()),
            'total_components': len(self.components),
            'uptime_seconds': time.time() - self.start_time,
            'total_predictions': self.total_predictions,
            'error_count': self.error_count
        }
    
    def _get_training_status(self) -> Dict[str, Any]:
        """Get training status"""
        try:
            if self.components['model_trainer']:
                return self.model_trainer.get_training_status()
        except:
            pass
        return {'status': 'Training status unavailable'}
    
    def _get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            cache_stats = {'total_cache_entries': 0, 'hit_rate': 0.0}
            
            if self.components['unified_predictor']:
                cache_size = len(self.unified_predictor.prediction_cache)
                cache_stats['prediction_cache_entries'] = cache_size
                cache_stats['total_cache_entries'] += cache_size
            
            return cache_stats
        except:
            return {'status': 'Cache stats unavailable'}
    
    def _create_error_result(self, error_msg: str) -> Dict[str, Any]:
        """Create error result structure"""
        return {
            'symbol': self.symbol,
            'timestamp': datetime.now().isoformat(),
            'error': error_msg,
            'engine_status': self._get_engine_status(),
            'predictions': {},
            'analysis': {'status': 'Failed due to error'},
            'recommendations': {'recommendation': 'HOLD', 'reason': 'System error'},
            'performance': {'error': True}
        }

# Create global instance
professional_engine = ProfessionalEngine()