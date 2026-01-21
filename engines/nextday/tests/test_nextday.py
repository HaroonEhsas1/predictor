"""
Unit tests for Next-Day Prediction Engine
Ensures institutional-grade reliability and safety
"""

import unittest
import numpy as np
import pandas as pd
from datetime import datetime, timezone
import os
import tempfile
import shutil

# Import modules to test
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from config import NextDayConfig, CONFIG
from features import NextDayFeatureEngine
from models import NextDayModelEngine
from gate import PredictionGate, RiskManager
from predict import NextDayPredictor

class TestNextDayConfig(unittest.TestCase):
    """Test configuration management"""
    
    def test_default_config(self):
        """Test default configuration values"""
        config = NextDayConfig()
        
        self.assertFalse(config.enabled)  # Disabled by default
        self.assertTrue(config.dry_run)   # Dry run by default
        self.assertEqual(config.min_confidence, 0.80)
        self.assertEqual(config.min_ensemble_consensus, 0.80)
        self.assertLessEqual(config.max_position_size, 0.02)  # 2% max
    
    def test_config_validation(self):
        """Test configuration validation"""
        config = NextDayConfig()
        
        # Safety checks
        self.assertLessEqual(config.max_position_size, 0.05)  # Reasonable limit
        self.assertGreaterEqual(config.min_confidence, 0.5)   # Meaningful threshold
        self.assertGreaterEqual(config.cv_folds, 3)           # Sufficient CV

class TestFeatureEngine(unittest.TestCase):
    """Test feature engineering"""
    
    def setUp(self):
        """Set up test data"""
        self.feature_engine = NextDayFeatureEngine()
        
        # Create sample market data
        dates = pd.date_range('2024-01-01', periods=100, freq='D', tz=timezone.utc)
        
        self.sample_data = {
            'amd': pd.DataFrame({
                'Open': np.random.uniform(150, 170, 100),
                'High': np.random.uniform(155, 175, 100),
                'Low': np.random.uniform(145, 165, 100),
                'Close': np.random.uniform(150, 170, 100),
                'Volume': np.random.uniform(50000000, 150000000, 100),
            }, index=dates),
            'vix': pd.DataFrame({
                'Close': np.random.uniform(12, 25, 100),
            }, index=dates),
            'soxx': pd.DataFrame({
                'Close': np.random.uniform(400, 500, 100),
            }, index=dates)
        }
        
        # Add basic derived columns
        for name, df in self.sample_data.items():
            if 'Close' in df.columns:
                df['returns'] = df['Close'].pct_change()
                df['volatility'] = df['returns'].rolling(20).std()
    
    def test_feature_engineering(self):
        """Test feature engineering pipeline"""
        features_df = self.feature_engine.engineer_features(self.sample_data)
        
        # Check basic structure
        self.assertFalse(features_df.empty)
        self.assertIn('target_gap_pct', features_df.columns)
        
        # Check feature count
        feature_cols = [col for col in features_df.columns if col != 'target_gap_pct']
        self.assertGreaterEqual(len(feature_cols), 10)  # Should have multiple features
        
        # Check for NaN handling
        self.assertFalse(features_df.isnull().all().any())  # No completely null columns
    
    def test_scaler_functionality(self):
        """Test scaler fitting and transformation"""
        features_df = self.feature_engine.engineer_features(self.sample_data)
        
        # Fit scaler
        self.feature_engine.fit_scaler(features_df)
        self.assertIsNotNone(self.feature_engine.scaler)
        
        # Transform features
        transformed = self.feature_engine.transform_features(features_df)
        self.assertEqual(transformed.shape[0], len(features_df))
        
        # Check normalization (should have reasonable scale)
        self.assertLess(np.abs(transformed.mean()), 0.1)  # Roughly centered
        self.assertLess(abs(transformed.std() - 1.0), 0.5)  # Roughly unit variance

class TestModelEngine(unittest.TestCase):
    """Test model training and prediction"""
    
    def setUp(self):
        """Set up test environment"""
        self.model_engine = NextDayModelEngine()
        
        # Create temporary directory for models
        self.temp_dir = tempfile.mkdtemp()
        CONFIG.models_path = self.temp_dir
        
        # Create sample features DataFrame
        n_samples = 200
        n_features = 15
        
        feature_names = self.model_engine.feature_engine.feature_names[:n_features]
        
        self.sample_features = pd.DataFrame(
            np.random.randn(n_samples, n_features),
            columns=feature_names
        )
        
        # Add realistic target (small gaps with some signal)
        noise = np.random.randn(n_samples) * 0.01
        signal = np.sin(np.linspace(0, 4*np.pi, n_samples)) * 0.005
        self.sample_features['target_gap_pct'] = signal + noise
    
    def tearDown(self):
        """Clean up test environment"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_model_training(self):
        """Test model training pipeline"""
        results = self.model_engine.train_models(self.sample_features, save_artifacts=False)
        
        # Check training results
        self.assertIn('cv_results', results)
        self.assertIn('n_samples', results)
        self.assertIn('ensemble_weights', results)
        
        # Check models were trained
        self.assertGreater(len(self.model_engine.models), 0)
        
        # Check ensemble weights
        weights = results['ensemble_weights']
        self.assertAlmostEqual(sum(weights.values()), 1.0, places=2)
    
    def test_prediction_structure(self):
        """Test prediction output structure"""
        # Train models first
        self.model_engine.train_models(self.sample_features, save_artifacts=False)
        
        # Make prediction
        result = self.model_engine.predict(self.sample_features.tail(10))
        
        # Check required fields
        required_fields = ['direction', 'confidence', 'predicted_gap_pct', 'expected_open']
        for field in required_fields:
            self.assertIn(field, result)
        
        # Check data types
        self.assertIn(result['direction'], ['UP', 'DOWN', 'SKIP'])
        self.assertIsInstance(result['confidence'], float)
        self.assertGreaterEqual(result['confidence'], 0.0)
        self.assertLessEqual(result['confidence'], 1.0)

class TestPredictionGate(unittest.TestCase):
    """Test gating system"""
    
    def setUp(self):
        """Set up gating tests"""
        self.gate = PredictionGate()
        
        # Sample prediction result
        self.sample_prediction = {
            'direction': 'UP',
            'confidence': 0.85,
            'predicted_gap_pct': 0.015,
            'model_predictions': {
                'gradient_boosting': 0.012,
                'random_forest': 0.018,
                'ridge': 0.015
            }
        }
    
    def test_confidence_gating(self):
        """Test confidence threshold gating"""
        # High confidence should pass
        high_conf_pred = self.sample_prediction.copy()
        high_conf_pred['confidence'] = 0.85
        
        result = self.gate.evaluate_signal(high_conf_pred)
        self.assertIn("Confidence", ' '.join(result.get('passed_gates', [])))
        
        # Low confidence should fail
        low_conf_pred = self.sample_prediction.copy()
        low_conf_pred['confidence'] = 0.60
        
        result = self.gate.evaluate_signal(low_conf_pred)
        self.assertIn("Low confidence", ' '.join(result.get('gate_reasons', [])))
    
    def test_consensus_gating(self):
        """Test ensemble consensus gating"""
        # Good consensus (all positive)
        good_consensus = self.sample_prediction.copy()
        good_consensus['model_predictions'] = {
            'model1': 0.01,
            'model2': 0.015,
            'model3': 0.02
        }
        
        result = self.gate.evaluate_signal(good_consensus)
        consensus_pass, consensus_score = self.gate._check_ensemble_consensus(
            good_consensus['model_predictions']
        )
        self.assertTrue(consensus_pass)
        
        # Poor consensus (mixed directions)
        poor_consensus = self.sample_prediction.copy()
        poor_consensus['model_predictions'] = {
            'model1': 0.01,
            'model2': -0.015,
            'model3': 0.02
        }
        
        result = self.gate.evaluate_signal(poor_consensus)
        consensus_pass, consensus_score = self.gate._check_ensemble_consensus(
            poor_consensus['model_predictions']
        )
        self.assertLess(consensus_score, CONFIG.min_ensemble_consensus)
    
    def test_dry_run_enforcement(self):
        """Test dry run mode enforcement"""
        # Ensure dry run prevents actual trades
        CONFIG.dry_run = True
        
        result = self.gate.evaluate_signal(self.sample_prediction)
        
        if CONFIG.dry_run:
            self.assertEqual(result['trade_signal'], 'NO_TRADE')
            self.assertIn("Dry run mode", ' '.join(result.get('gate_reasons', [])))

class TestRiskManager(unittest.TestCase):
    """Test risk management"""
    
    def setUp(self):
        """Set up risk manager"""
        self.risk_manager = RiskManager()
    
    def test_position_size_limits(self):
        """Test position size limit enforcement"""
        # Normal position should pass
        approved, reason = self.risk_manager.check_risk_limits(0.01, 'UP')  # 1%
        self.assertTrue(approved)
        
        # Oversized position should fail
        approved, reason = self.risk_manager.check_risk_limits(0.10, 'UP')  # 10%
        self.assertFalse(approved)
        self.assertIn("Position too large", reason)

class TestIntegration(unittest.TestCase):
    """Integration tests for full prediction pipeline"""
    
    def setUp(self):
        """Set up integration test"""
        # Create temporary directory
        self.temp_dir = tempfile.mkdtemp()
        CONFIG.models_path = self.temp_dir
        
        # Disable feature flag initially
        CONFIG.enabled = False
        CONFIG.dry_run = True
    
    def tearDown(self):
        """Clean up"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_disabled_feature_flag(self):
        """Test behavior when feature is disabled"""
        predictor = NextDayPredictor()
        
        # Should fail to initialize when disabled
        success = predictor.initialize()
        self.assertFalse(success)
    
    def test_fallback_behavior(self):
        """Test fallback when models not available"""
        CONFIG.enabled = True  # Enable feature
        
        predictor = NextDayPredictor()
        
        # Should return SKIP when no models available
        result = predictor.generate_prediction()
        
        self.assertEqual(result['direction'], 'SKIP')
        self.assertEqual(result['trade_signal'], 'NO_TRADE')
        self.assertIn('reason', result)

def run_tests():
    """Run all tests"""
    print("🧪 Running Next-Day Prediction Engine Tests...")
    print("=" * 60)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestNextDayConfig,
        TestFeatureEngine, 
        TestModelEngine,
        TestPredictionGate,
        TestRiskManager,
        TestIntegration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("✓ All tests passed!")
    else:
        print(f"✗ {len(result.failures)} failures, {len(result.errors)} errors")
    
    return result.wasSuccessful()

if __name__ == '__main__':
    run_tests()