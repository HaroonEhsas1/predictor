"""
Main prediction interface for next-day gap predictions
Orchestrates data collection, feature engineering, and model inference
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
import traceback

try:
    from .config import CONFIG
    from .data_ingest import DataIngestionEngine
    from .features import NextDayFeatureEngine
    from .models import NextDayModelEngine
    from .gate import PredictionGate, RiskManager
except ImportError:
    try:
        from engines.nextday.config import CONFIG
        from engines.nextday.data_ingest import DataIngestionEngine
        from engines.nextday.features import NextDayFeatureEngine
        from engines.nextday.models import NextDayModelEngine
        from engines.nextday.gate import PredictionGate, RiskManager
    except ImportError:
        from config import CONFIG
        from data_ingest import DataIngestionEngine
        from features import NextDayFeatureEngine
        from models import NextDayModelEngine
        from gate import PredictionGate, RiskManager

logger = logging.getLogger(__name__)

class NextDayPredictor:
    """
    Main prediction orchestrator for institutional next-day gap predictions
    Coordinates all components and provides clean prediction interface
    """
    
    def __init__(self, model_version: Optional[str] = None):
        self.data_engine = DataIngestionEngine()
        self.feature_engine = NextDayFeatureEngine()
        self.model_engine = NextDayModelEngine()
        self.gate = PredictionGate()
        self.risk_manager = RiskManager()
        
        self.is_initialized = False
        self.model_version = model_version
        
    def initialize(self) -> bool:
        """
        Initialize predictor by loading models and validating setup
        
        Returns:
            Success status
        """
        
        logger.info("Initializing Next-Day Prediction Engine...")
        
        try:
            # Check feature flag
            if not CONFIG.enabled:
                logger.warning("Next-day engine disabled by feature flag")
                return False
            
            # Load trained models
            models_loaded = self.model_engine.load_models(self.model_version)
            
            if not models_loaded:
                logger.error("Failed to load trained models")
                return False
            
            # Validate configuration
            self._validate_config()
            
            self.is_initialized = True
            logger.info("✓ Next-day prediction engine initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            logger.debug(traceback.format_exc())
            return False
    
    def generate_prediction(self, lookback_days: int = 60) -> Dict[str, Any]:
        """
        Generate next-day gap prediction with full institutional workflow
        
        Args:
            lookback_days: Days of historical data for feature engineering
            
        Returns:
            Complete prediction result with gating and risk assessment
        """
        
        if not self.is_initialized:
            if not self.initialize():
                return self._fallback_response("Predictor not initialized")
        
        logger.info(f"Generating next-day prediction (lookback: {lookback_days} days)...")
        
        try:
            # Step 1: Data Ingestion with validation
            logger.info("Step 1: Collecting and validating market data...")
            market_data = self.data_engine.fetch_comprehensive_data(lookback_days)
            
            if not market_data:
                return self._fallback_response("Failed to collect market data")
            
            # Step 2: Feature Engineering
            logger.info("Step 2: Engineering institutional-grade features...")
            features_df = self.feature_engine.engineer_features(market_data)
            
            if features_df.empty:
                return self._fallback_response("Feature engineering failed")
            
            # Step 3: Model Prediction
            logger.info("Step 3: Generating ensemble prediction...")
            prediction_result = self.model_engine.predict(features_df)
            
            if prediction_result.get('direction') == 'SKIP' and 'error' in prediction_result.get('reason', ''):
                return self._fallback_response(f"Model prediction failed: {prediction_result.get('reason')}")
            
            # Step 4: Gating and Risk Management
            logger.info("Step 4: Applying institutional gating rules...")
            gated_result = self.gate.evaluate_signal(prediction_result)
            
            # Step 5: Final risk checks
            if gated_result['trade_signal'] != 'NO_TRADE':
                risk_approved, risk_reason = self.risk_manager.check_risk_limits(
                    gated_result.get('position_size', 0.0),
                    gated_result['trade_signal']
                )
                
                if not risk_approved:
                    gated_result['trade_signal'] = 'NO_TRADE'
                    gated_result['gate_reasons'].append(f"Risk limit: {risk_reason}")
            
            # Add metadata
            gated_result.update({
                'prediction_timestamp': datetime.now().isoformat(),
                'lookback_days': lookback_days,
                'data_sources': list(market_data.keys()),
                'feature_count': len(features_df.columns) - 1,  # Exclude target
                'model_version': self.model_version or 'latest',
                'dry_run_mode': CONFIG.dry_run
            })
            
            # Log final result
            signal = gated_result['trade_signal']
            confidence = gated_result.get('confidence', 0.0)
            logger.info(f"✓ Prediction complete: {signal} ({confidence:.1%} confidence)")
            
            return gated_result
            
        except Exception as e:
            logger.error(f"Prediction generation failed: {e}")
            logger.debug(traceback.format_exc())
            return self._fallback_response(f"Prediction failed: {str(e)}")
    
    def train_models(self, lookback_days: int = 252) -> Dict[str, Any]:
        """
        Train new models using historical data
        
        Args:
            lookback_days: Days of historical data for training
            
        Returns:
            Training results and validation metrics
        """
        
        logger.info(f"Training next-day models with {lookback_days} days of data...")
        
        try:
            # Collect training data
            logger.info("Collecting historical training data...")
            market_data = self.data_engine.fetch_comprehensive_data(lookback_days)
            
            if not market_data:
                raise ValueError("Failed to collect training data")
            
            # Engineer features for training
            logger.info("Engineering features for training...")
            features_df = self.feature_engine.engineer_features(market_data)
            
            if features_df.empty:
                raise ValueError("Feature engineering failed")
            
            # Train models
            logger.info("Training ensemble models...")
            training_results = self.model_engine.train_models(features_df, save_artifacts=True)
            
            logger.info(f"✓ Model training complete: {training_results['n_samples']} samples, "
                       f"{training_results['n_features']} features")
            
            return training_results
            
        except Exception as e:
            logger.error(f"Model training failed: {e}")
            logger.debug(traceback.format_exc())
            raise
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status and health of prediction engine"""
        
        return {
            'initialized': self.is_initialized,
            'enabled': CONFIG.enabled,
            'dry_run': CONFIG.dry_run,
            'confidence_threshold': CONFIG.min_confidence,
            'consensus_threshold': CONFIG.min_ensemble_consensus,
            'models_loaded': bool(self.model_engine.models),
            'scaler_fitted': self.feature_engine.scaler is not None,
            'model_version': self.model_version,
            'gating_stats': self.gate.get_gating_stats()
        }
    
    def _validate_config(self) -> None:
        """Validate configuration for institutional compliance"""
        
        if CONFIG.min_confidence < 0.7:
            logger.warning(f"Low confidence threshold: {CONFIG.min_confidence:.0%} < 70%")
        
        if CONFIG.min_ensemble_consensus < 0.7:
            logger.warning(f"Low consensus threshold: {CONFIG.min_ensemble_consensus:.0%} < 70%")
        
        if CONFIG.max_position_size > 0.05:
            logger.warning(f"High position size limit: {CONFIG.max_position_size:.1%} > 5%")
    
    def _fallback_response(self, reason: str) -> Dict[str, Any]:
        """Generate safe fallback response when prediction fails"""
        
        return {
            'direction': 'SKIP',
            'confidence': 0.0,
            'trade_signal': 'NO_TRADE',
            'position_size': 0.0,
            'reason': reason,
            'predicted_gap_pct': 0.0,
            'expected_open': 0.0,
            'gate_reasons': [reason],
            'prediction_timestamp': datetime.now().isoformat(),
            'dry_run_mode': CONFIG.dry_run,
            'fallback_mode': True
        }

def run_prediction_cli(model_version: Optional[str] = None, 
                      train_mode: bool = False,
                      lookback_days: int = 60) -> None:
    """
    Command-line interface for next-day predictions
    
    Args:
        model_version: Specific model version to use
        train_mode: Whether to train new models
        lookback_days: Days of historical data
    """
    
    predictor = NextDayPredictor(model_version)
    
    if train_mode:
        print("🔧 Training Mode - Building new models...")
        try:
            results = predictor.train_models(lookback_days=252)  # 1 year for training
            print(f"✓ Training complete:")
            print(f"  - Samples: {results['n_samples']}")
            print(f"  - Features: {results['n_features']}")
            print(f"  - Model version: {results['model_version']}")
            print(f"  - Ensemble weights: {results['ensemble_weights']}")
        except Exception as e:
            print(f"✗ Training failed: {e}")
            return
    
    print("🔮 Prediction Mode - Generating next-day signal...")
    
    try:
        result = predictor.generate_prediction(lookback_days)
        
        print(f"\n🎯 NEXT-DAY PREDICTION RESULT")
        print(f"{'='*50}")
        print(f"Direction: {result['direction']}")
        print(f"Confidence: {result.get('confidence', 0):.1%}")
        print(f"Trade Signal: {result['trade_signal']}")
        print(f"Expected Gap: {result.get('predicted_gap_pct', 0):+.2%}")
        print(f"Expected Open: ${result.get('expected_open', 0):.2f}")
        
        if result.get('position_size', 0) > 0:
            print(f"Position Size: {result['position_size']:.1%}")
        
        if result.get('gate_reasons'):
            print(f"\nGating Reasons:")
            for reason in result['gate_reasons']:
                print(f"  - {reason}")
        
        if result.get('passed_gates'):
            print(f"\nPassed Gates:")
            for gate in result['passed_gates']:
                print(f"  ✓ {gate}")
        
        print(f"\nDry Run Mode: {result.get('dry_run_mode', True)}")
        print(f"Timestamp: {result.get('prediction_timestamp', 'N/A')}")
        
    except Exception as e:
        print(f"✗ Prediction failed: {e}")

# Export main classes
__all__ = ['NextDayPredictor', 'run_prediction_cli']