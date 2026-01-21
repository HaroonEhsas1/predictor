#!/usr/bin/env python3
"""
Unified Predictor for Professional Stock Prediction Engine
Coordinates intraday and next-day predictions with existing system integration
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

@dataclass
class UnifiedPrediction:
    """Container for unified prediction results"""
    symbol: str
    prediction_type: str  # 'intraday_1m', 'intraday_swing', 'nextday_preclose', 'nextday_preopen'
    direction: str
    confidence: float
    target_price: float
    expected_return_pct: float
    position_size: float
    risk_level: str
    time_horizon: str
    execution_details: Dict[str, Any]
    model_details: Dict[str, Any]
    timestamp: str

class UnifiedPredictor:
    """
    Professional unified prediction coordinator
    Manages both intraday and next-day prediction systems
    """
    
    def __init__(self):
        """Initialize unified predictor"""
        self.prediction_cache = {}
        self.cache_duration = {'1m': 30, 'swing': 300, 'nextday': 1800}  # seconds
        
        # Import engine components
        try:
            from .data_collector import data_collector
            from .feature_engineer import feature_engineer
            from .ensemble_intraday import intraday_ensemble
            from .gap_nextday import gap_nextday_predictor
            
            self.data_collector = data_collector
            self.feature_engineer = feature_engineer
            self.intraday_ensemble = intraday_ensemble
            self.gap_predictor = gap_nextday_predictor
            
            self.engine_available = True
            print("✅ Engine components loaded successfully")
            
        except ImportError as e:
            print(f"⚠️  Engine components not fully available: {e}")
            self.engine_available = False
        
        # Integration with existing system
        try:
            from main import UnifiedPredictionEngine
            self.existing_engine = UnifiedPredictionEngine()
            self.existing_available = True
            print("✅ Integrated with existing prediction engine")
        except ImportError:
            self.existing_available = False
            print("⚠️  No existing prediction engine found")
        
        # Prediction scheduling
        self.scheduler_active = False
        self.prediction_thread = None
        
        print("✅ UnifiedPredictor initialized")
    
    def predict_1minute(self, symbol: str = "AMD") -> UnifiedPrediction:
        """
        Ultra-fast 1-minute prediction optimized for low latency
        """
        start_time = time.time()
        
        try:
            # Check cache first
            cache_key = f"1m_{symbol}"
            if self._check_cache(cache_key, self.cache_duration['1m']):
                return self.prediction_cache[cache_key]['result']
            
            # Get intraday features (fast)
            if self.engine_available:
                intraday_data = self.data_collector.get_intraday_features(symbol, '1m')
                
                if intraday_data.get('features'):
                    # Engineer features (fast)
                    feature_set = self.feature_engineer.engineer_intraday_features(intraday_data, symbol)
                    
                    # Get prediction from ensemble
                    prediction_result = self.intraday_ensemble.predict_1minute(feature_set.__dict__, symbol)
                    
                    # Convert to unified format
                    unified_prediction = self._convert_intraday_to_unified(
                        prediction_result, symbol, '1m', intraday_data.get('features', {})
                    )
                    
                    # Cache result
                    self.prediction_cache[cache_key] = {
                        'result': unified_prediction,
                        'timestamp': time.time()
                    }
                    
                    execution_time = (time.time() - start_time) * 1000
                    print(f"⚡ 1-minute prediction: {unified_prediction.direction} ({execution_time:.1f}ms)")
                    
                    return unified_prediction
            
            # Fallback to existing system
            if self.existing_available:
                return self._fallback_to_existing(symbol, '1m')
            
            # Default prediction
            return self._create_default_prediction(symbol, '1m')
            
        except Exception as e:
            print(f"⚠️  1-minute prediction error: {str(e)[:50]}")
            return self._create_default_prediction(symbol, '1m')
    
    def predict_swing_intraday(self, symbol: str = "AMD", timeframe: str = "15m") -> UnifiedPrediction:
        """
        Swing intraday prediction for 15m, 30m, 1h timeframes
        """
        try:
            # Check cache
            cache_key = f"swing_{timeframe}_{symbol}"
            if self._check_cache(cache_key, self.cache_duration['swing']):
                return self.prediction_cache[cache_key]['result']
            
            if self.engine_available:
                # Get intraday data for swing timeframe
                intraday_data = self.data_collector.get_intraday_features(symbol, timeframe)
                
                if intraday_data.get('features'):
                    # Engineer comprehensive features
                    feature_set = self.feature_engineer.engineer_intraday_features(intraday_data, symbol)
                    
                    # Get swing prediction
                    prediction_result = self.intraday_ensemble.predict_swing_intraday(
                        feature_set.__dict__, symbol, timeframe
                    )
                    
                    # Convert to unified format
                    unified_prediction = self._convert_intraday_to_unified(
                        prediction_result, symbol, f'swing_{timeframe}', intraday_data.get('features', {})
                    )
                    
                    # Cache result
                    self.prediction_cache[cache_key] = {
                        'result': unified_prediction,
                        'timestamp': time.time()
                    }
                    
                    print(f"📈 {timeframe} swing prediction: {unified_prediction.direction}")
                    return unified_prediction
            
            # Fallback
            if self.existing_available:
                return self._fallback_to_existing(symbol, f'swing_{timeframe}')
            
            return self._create_default_prediction(symbol, f'swing_{timeframe}')
            
        except Exception as e:
            print(f"⚠️  Swing prediction error: {str(e)[:50]}")
            return self._create_default_prediction(symbol, f'swing_{timeframe}')
    
    def predict_nextday_preclose(self, symbol: str = "AMD") -> UnifiedPrediction:
        """
        Next-day prediction at market close (comprehensive analysis)
        """
        print(f"🌙 Pre-close next-day analysis for {symbol}...")
        
        try:
            # Check cache
            cache_key = f"nextday_preclose_{symbol}"
            if self._check_cache(cache_key, self.cache_duration['nextday']):
                return self.prediction_cache[cache_key]['result']
            
            if self.engine_available:
                # Get comprehensive next-day dataset
                nextday_dataset = self.data_collector.get_nextday_dataset(symbol)
                
                if nextday_dataset:
                    # Engineer next-day features
                    feature_set = self.feature_engineer.engineer_nextday_features(nextday_dataset, symbol)
                    
                    # Get pre-close prediction
                    nextday_prediction = self.gap_predictor.predict_preclose(nextday_dataset, symbol)
                    
                    # Convert to unified format
                    unified_prediction = self._convert_nextday_to_unified(
                        nextday_prediction, symbol, 'preclose', feature_set
                    )
                    
                    # Cache result
                    self.prediction_cache[cache_key] = {
                        'result': unified_prediction,
                        'timestamp': time.time()
                    }
                    
                    print(f"✅ Pre-close: {unified_prediction.direction} gap {unified_prediction.expected_return_pct:.2f}%")
                    return unified_prediction
            
            # Fallback to existing next-day system
            return self._fallback_nextday_prediction(symbol, 'preclose')
            
        except Exception as e:
            print(f"⚠️  Pre-close prediction error: {str(e)[:50]}")
            return self._create_default_prediction(symbol, 'nextday_preclose')
    
    def predict_nextday_preopen(self, symbol: str = "AMD") -> UnifiedPrediction:
        """
        Next-day prediction at pre-market (with overnight updates)
        """
        print(f"🌅 Pre-open next-day analysis for {symbol}...")
        
        try:
            cache_key = f"nextday_preopen_{symbol}"
            if self._check_cache(cache_key, 300):  # 5-minute cache for pre-open
                return self.prediction_cache[cache_key]['result']
            
            if self.engine_available:
                # Get updated dataset with overnight context
                nextday_dataset = self.data_collector.get_nextday_dataset(symbol)
                
                if nextday_dataset:
                    feature_set = self.feature_engineer.engineer_nextday_features(nextday_dataset, symbol)
                    
                    # Get pre-open prediction with overnight updates
                    nextday_prediction = self.gap_predictor.predict_preopen(nextday_dataset, symbol)
                    
                    unified_prediction = self._convert_nextday_to_unified(
                        nextday_prediction, symbol, 'preopen', feature_set
                    )
                    
                    self.prediction_cache[cache_key] = {
                        'result': unified_prediction,
                        'timestamp': time.time()
                    }
                    
                    print(f"✅ Pre-open: Target ${unified_prediction.target_price:.2f}")
                    return unified_prediction
            
            return self._fallback_nextday_prediction(symbol, 'preopen')
            
        except Exception as e:
            print(f"⚠️  Pre-open prediction error: {str(e)[:50]}")
            return self._create_default_prediction(symbol, 'nextday_preopen')
    
    def get_comprehensive_analysis(self, symbol: str = "AMD") -> Dict[str, Any]:
        """
        Get comprehensive analysis combining all prediction types
        """
        print(f"🔍 Comprehensive analysis for {symbol}...")
        
        try:
            market_state = scheduler.get_market_state()
            
            analysis = {
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'market_state': market_state['session_phase'],
                'predictions': {},
                'summary': {},
                'recommendations': {}
            }
            
            # Get appropriate predictions based on market state
            if market_state['market_open']:
                # Market open - get intraday predictions
                analysis['predictions']['1_minute'] = self.predict_1minute(symbol).__dict__
                analysis['predictions']['swing_15m'] = self.predict_swing_intraday(symbol, '15m').__dict__
                
                # Get detailed gap report if near close
                if market_state.get('minutes_to_close', 400) < 60:
                    analysis['predictions']['nextday_prep'] = self.predict_nextday_preclose(symbol).__dict__
                    
            elif market_state.get('pre_market'):
                # Pre-market - get pre-open prediction
                analysis['predictions']['preopen'] = self.predict_nextday_preopen(symbol).__dict__
                
            else:
                # After hours or weekend - get next-day analysis
                analysis['predictions']['nextday'] = self.predict_nextday_preclose(symbol).__dict__
            
            # Generate summary and recommendations
            analysis['summary'] = self._generate_analysis_summary(analysis['predictions'])
            analysis['recommendations'] = self._generate_trading_recommendations(analysis['predictions'])
            
            return analysis
            
        except Exception as e:
            print(f"⚠️  Comprehensive analysis error: {str(e)[:50]}")
            return {'error': str(e), 'symbol': symbol}
    
    def start_continuous_predictions(self, symbol: str = "AMD", interval_seconds: int = 30):
        """
        Start continuous prediction updates during market hours
        """
        if self.scheduler_active:
            print("⚠️  Scheduler already active")
            return
        
        self.scheduler_active = True
        self.prediction_thread = threading.Thread(
            target=self._continuous_prediction_loop,
            args=(symbol, interval_seconds),
            daemon=True
        )
        self.prediction_thread.start()
        
        print(f"🔄 Started continuous predictions for {symbol} (every {interval_seconds}s)")
    
    def stop_continuous_predictions(self):
        """Stop continuous prediction updates"""
        self.scheduler_active = False
        if self.prediction_thread:
            self.prediction_thread.join(timeout=5)
        print("⏹️  Stopped continuous predictions")
    
    def _continuous_prediction_loop(self, symbol: str, interval: int):
        """Continuous prediction loop (runs in separate thread)"""
        while self.scheduler_active:
            try:
                market_state = scheduler.get_market_state()
                
                if market_state['market_open']:
                    # During market hours - run 1-minute predictions
                    prediction = self.predict_1minute(symbol)
                    print(f"🔄 Auto: {prediction.direction} ({prediction.confidence:.1%})")
                    
                elif market_state.get('pre_market'):
                    # Pre-market - run pre-open predictions
                    prediction = self.predict_nextday_preopen(symbol)
                    print(f"🌅 Pre-market: {prediction.direction}")
                
                # Sleep for interval
                time.sleep(interval)
                
            except Exception as e:
                print(f"⚠️  Continuous prediction error: {str(e)[:50]}")
                time.sleep(interval)
    
    def _check_cache(self, key: str, max_age: int) -> bool:
        """Check if cached prediction is still valid"""
        if key not in self.prediction_cache:
            return False
        
        cache_age = time.time() - self.prediction_cache[key]['timestamp']
        return cache_age < max_age
    
    def _convert_intraday_to_unified(self, prediction_result, symbol: str, pred_type: str, features: Dict) -> UnifiedPrediction:
        """Convert intraday prediction result to unified format"""
        try:
            current_price = features.get('price_current', 0.0)
            expected_change = prediction_result.price_target - current_price if hasattr(prediction_result, 'price_target') else 0.0
            expected_return_pct = (expected_change / current_price * 100) if current_price > 0 else 0.0
            
            # Position sizing based on confidence
            confidence = getattr(prediction_result, 'confidence', 0.5)
            if confidence >= 0.8:
                position_size = 0.05  # 5% for high confidence
            elif confidence >= 0.7:
                position_size = 0.03  # 3% for medium confidence
            else:
                position_size = 0.01  # 1% for low confidence
            
            return UnifiedPrediction(
                symbol=symbol,
                prediction_type=f'intraday_{pred_type}',
                direction=getattr(prediction_result, 'direction', 'SIDEWAYS'),
                confidence=confidence,
                target_price=getattr(prediction_result, 'price_target', current_price),
                expected_return_pct=expected_return_pct,
                position_size=position_size,
                risk_level=self._determine_risk_level(confidence, expected_return_pct),
                time_horizon='1m' if '1m' in pred_type else '15m-1h',
                execution_details={
                    'execution_time_ms': getattr(prediction_result, 'execution_time_ms', 0),
                    'model_agreement': getattr(prediction_result, 'model_agreement', 0),
                },
                model_details={
                    'individual_predictions': getattr(prediction_result, 'individual_predictions', {}),
                    'feature_importance': getattr(prediction_result, 'feature_importance', {})
                },
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            print(f"⚠️  Intraday conversion error: {str(e)[:50]}")
            return self._create_default_prediction(symbol, pred_type)
    
    def _convert_nextday_to_unified(self, nextday_prediction, symbol: str, pred_type: str, feature_set) -> UnifiedPrediction:
        """Convert next-day prediction to unified format"""
        try:
            return UnifiedPrediction(
                symbol=symbol,
                prediction_type=f'nextday_{pred_type}',
                direction=getattr(nextday_prediction, 'direction', 'FLAT'),
                confidence=getattr(nextday_prediction, 'confidence', 0.5),
                target_price=getattr(nextday_prediction, 'target_price', 0.0),
                expected_return_pct=getattr(nextday_prediction, 'expected_gap_pct', 0.0),
                position_size=getattr(nextday_prediction, 'position_size', 0.0),
                risk_level=getattr(nextday_prediction, 'risk_level', 'MEDIUM'),
                time_horizon=getattr(nextday_prediction, 'time_horizon', 'next-day'),
                execution_details={
                    'profit_range': getattr(nextday_prediction, 'profit_range', (0.0, 0.0)),
                    'contextual_analysis': getattr(nextday_prediction, 'contextual_analysis', {})
                },
                model_details={
                    'execution_details': getattr(nextday_prediction, 'execution_details', {})
                },
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            print(f"⚠️  Next-day conversion error: {str(e)[:50]}")
            return self._create_default_prediction(symbol, pred_type)
    
    def _fallback_to_existing(self, symbol: str, pred_type: str) -> UnifiedPrediction:
        """Fallback to existing prediction engine"""
        try:
            if self.existing_available:
                # Run existing prediction cycle
                existing_result = self.existing_engine.run_prediction_cycle()
                
                # Convert to unified format (simplified)
                return UnifiedPrediction(
                    symbol=symbol,
                    prediction_type=f'existing_{pred_type}',
                    direction='SIDEWAYS',  # Default
                    confidence=0.6,
                    target_price=0.0,
                    expected_return_pct=0.0,
                    position_size=0.0,
                    risk_level='MEDIUM',
                    time_horizon=pred_type,
                    execution_details={'source': 'existing_engine'},
                    model_details={},
                    timestamp=datetime.now().isoformat()
                )
                
        except Exception as e:
            print(f"⚠️  Existing engine fallback error: {str(e)[:50]}")
        
        return self._create_default_prediction(symbol, pred_type)
    
    def _fallback_nextday_prediction(self, symbol: str, pred_type: str) -> UnifiedPrediction:
        """Fallback for next-day predictions"""
        try:
            # Try existing next-day predictor
            from professional_next_day_predictor import ProfessionalNextDayPredictor
            existing_nextday = ProfessionalNextDayPredictor()
            
            # Get basic next-day prediction
            result = existing_nextday.predict_next_day_gap(symbol)
            
            return UnifiedPrediction(
                symbol=symbol,
                prediction_type=f'nextday_{pred_type}_fallback',
                direction=result.get('direction', 'FLAT'),
                confidence=result.get('confidence', 0.5),
                target_price=result.get('target_price', 0.0),
                expected_return_pct=result.get('expected_gap_pct', 0.0),
                position_size=result.get('position_size', 0.0),
                risk_level=result.get('risk_level', 'MEDIUM'),
                time_horizon='next-day',
                execution_details={'source': 'existing_nextday'},
                model_details={},
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            print(f"⚠️  Next-day fallback error: {str(e)[:50]}")
            return self._create_default_prediction(symbol, pred_type)
    
    def _create_default_prediction(self, symbol: str, pred_type: str) -> UnifiedPrediction:
        """Create default prediction for error cases"""
        return UnifiedPrediction(
            symbol=symbol,
            prediction_type=f'default_{pred_type}',
            direction='SIDEWAYS',
            confidence=0.4,
            target_price=0.0,
            expected_return_pct=0.0,
            position_size=0.0,
            risk_level='HIGH',
            time_horizon='unknown',
            execution_details={'error': 'Default prediction'},
            model_details={},
            timestamp=datetime.now().isoformat()
        )
    
    def _determine_risk_level(self, confidence: float, expected_return: float) -> str:
        """Determine risk level based on confidence and expected return"""
        if confidence >= 0.8 and abs(expected_return) >= 1.0:
            return 'LOW'
        elif confidence >= 0.6 and abs(expected_return) >= 0.5:
            return 'MEDIUM'
        else:
            return 'HIGH'
    
    def _generate_analysis_summary(self, predictions: Dict) -> Dict[str, Any]:
        """Generate summary from multiple predictions"""
        if not predictions:
            return {'status': 'No predictions available'}
        
        # Count directions
        directions = [pred.get('direction', 'SIDEWAYS') for pred in predictions.values()]
        direction_counts = {d: directions.count(d) for d in set(directions)}
        
        # Average confidence
        confidences = [pred.get('confidence', 0.5) for pred in predictions.values()]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.5
        
        # Consensus direction
        consensus_direction = max(direction_counts, key=direction_counts.get) if direction_counts else 'SIDEWAYS'
        
        return {
            'consensus_direction': consensus_direction,
            'average_confidence': avg_confidence,
            'prediction_count': len(predictions),
            'direction_distribution': direction_counts,
            'high_confidence_predictions': len([c for c in confidences if c >= 0.7])
        }
    
    def _generate_trading_recommendations(self, predictions: Dict) -> Dict[str, Any]:
        """Generate trading recommendations from predictions"""
        summary = self._generate_analysis_summary(predictions)
        
        if not predictions:
            return {'recommendation': 'HOLD', 'reason': 'No predictions available'}
        
        avg_confidence = summary['average_confidence']
        consensus_direction = summary['consensus_direction']
        high_confidence_count = summary['high_confidence_predictions']
        
        if avg_confidence >= 0.75 and high_confidence_count >= 2 and consensus_direction != 'SIDEWAYS':
            recommendation = f'STRONG_{consensus_direction}'
            position_size = 0.05
        elif avg_confidence >= 0.6 and consensus_direction != 'SIDEWAYS':
            recommendation = consensus_direction
            position_size = 0.03
        else:
            recommendation = 'HOLD'
            position_size = 0.0
        
        return {
            'recommendation': recommendation,
            'position_size': position_size,
            'confidence': avg_confidence,
            'reason': f'Based on {len(predictions)} predictions with {high_confidence_count} high confidence'
        }

# Create global instance
unified_predictor = UnifiedPredictor()