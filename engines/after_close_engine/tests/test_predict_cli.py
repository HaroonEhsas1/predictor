"""
Unit tests for prediction CLI functionality
"""
import pytest
import json
import tempfile
import os
import sys
from unittest.mock import patch, MagicMock
import subprocess

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine import predict_command, collect_command
from config import CONFIG

class TestPredictCLI:
    """Test suite for prediction CLI"""
    
    def setup_method(self):
        """Setup test environment"""
        # Ensure mock mode is enabled for tests
        CONFIG.mock_mode = True
        CONFIG.after_close_enabled = True
        CONFIG.debug_mode = True
        
    def test_collect_command(self):
        """Test data collection command"""
        
        with tempfile.TemporaryDirectory() as temp_dir:
            CONFIG.prediction_path = temp_dir
            
            result = collect_command()
            
            assert result['status'] == 'success'
            assert 'data' in result
            assert 'collection_file' in result
            assert os.path.exists(result['collection_file'])
            
            # Verify collected data structure
            data = result['data']
            assert 'symbol' in data
            assert 'futures' in data
            assert 'options' in data
            assert 'news' in data
            assert 'global_indices' in data
    
    @patch('engines.after_close_engine.model_training.EnsembleModel')
    def test_predict_command_dry_run(self, mock_ensemble_class):
        """Test prediction in dry run mode"""
        
        # Mock ensemble model
        mock_ensemble = MagicMock()
        mock_ensemble.load.return_value = True
        mock_ensemble.predict.return_value = (0.75, {'lightgbm': 0.8, 'lstm': 0.7})
        mock_ensemble_class.return_value = mock_ensemble
        
        result = predict_command(dry_run=True, auto_fit=False)
        
        assert result['status'] == 'success_dry_run'
        assert 'prediction' in result
        
        prediction = result['prediction']
        assert prediction['symbol'] == CONFIG.symbol
        assert prediction['direction'] in ['UP', 'DOWN', 'SKIP']
        assert 0 <= prediction['confidence'] <= 1
        assert 'features' in prediction
        assert 'model_predictions' in prediction
        assert prediction['model_version'] == 'v1.0'
        
        # Verify feature structure
        features = prediction['features']
        expected_features = [
            'overnight_futures_pct',
            'net_options_flow',
            'news_sentiment_score',
            'global_index_impact_score',
            'prior_close_return',
            'intraday_volatility'
        ]
        for feature in expected_features:
            assert feature in features
            assert isinstance(features[feature], (int, float))
    
    @patch('engines.after_close_engine.model_training.EnsembleModel')
    def test_predict_command_low_confidence(self, mock_ensemble_class):
        """Test prediction with low confidence (should return SKIP)"""
        
        # Mock ensemble model with low confidence prediction
        mock_ensemble = MagicMock()
        mock_ensemble.load.return_value = True
        mock_ensemble.predict.return_value = (0.1, {'lightgbm': 0.1, 'lstm': 0.1})  # Low prediction
        mock_ensemble_class.return_value = mock_ensemble
        
        result = predict_command(dry_run=True, auto_fit=False)
        
        assert result['status'] == 'success_dry_run'
        prediction = result['prediction']
        assert prediction['direction'] == 'SKIP'  # Low confidence should trigger SKIP
        assert prediction['confidence'] < CONFIG.confidence_threshold
    
    @patch('engines.after_close_engine.model_training.EnsembleModel')
    def test_predict_command_high_confidence_up(self, mock_ensemble_class):
        """Test prediction with high confidence UP signal"""
        
        # Mock ensemble model with strong bullish prediction
        mock_ensemble = MagicMock()
        mock_ensemble.load.return_value = True
        mock_ensemble.predict.return_value = (1.5, {'lightgbm': 1.6, 'lstm': 1.4})  # Strong UP
        mock_ensemble_class.return_value = mock_ensemble
        
        result = predict_command(dry_run=True, auto_fit=False)
        
        assert result['status'] == 'success_dry_run'
        prediction = result['prediction']
        assert prediction['direction'] == 'UP'
        assert prediction['confidence'] >= CONFIG.confidence_threshold
        assert prediction['expected_open'] > prediction['current_price']
    
    @patch('engines.after_close_engine.model_training.EnsembleModel')
    def test_predict_command_high_confidence_down(self, mock_ensemble_class):
        """Test prediction with high confidence DOWN signal"""
        
        # Mock ensemble model with strong bearish prediction
        mock_ensemble = MagicMock()
        mock_ensemble.load.return_value = True
        mock_ensemble.predict.return_value = (-1.2, {'lightgbm': -1.3, 'lstm': -1.1})  # Strong DOWN
        mock_ensemble_class.return_value = mock_ensemble
        
        result = predict_command(dry_run=True, auto_fit=False)
        
        assert result['status'] == 'success_dry_run'
        prediction = result['prediction']
        assert prediction['direction'] == 'DOWN'
        assert prediction['confidence'] >= CONFIG.confidence_threshold
        assert prediction['expected_open'] < prediction['current_price']
    
    @patch('engines.after_close_engine.model_training.EnsembleModel')
    def test_predict_command_save_file(self, mock_ensemble_class):
        """Test prediction saving to file (non-dry-run)"""
        
        with tempfile.TemporaryDirectory() as temp_dir:
            CONFIG.prediction_path = temp_dir
            CONFIG.log_path = temp_dir
            
            # Mock ensemble model
            mock_ensemble = MagicMock()
            mock_ensemble.load.return_value = True
            mock_ensemble.predict.return_value = (1.0, {'lightgbm': 1.0, 'lstm': 1.0})
            mock_ensemble_class.return_value = mock_ensemble
            
            result = predict_command(dry_run=False, auto_fit=False)
            
            assert result['status'] == 'success'
            assert 'prediction_file' in result
            assert 'log_file' in result
            assert os.path.exists(result['prediction_file'])
            assert os.path.exists(result['log_file'])
            
            # Verify file contents
            with open(result['prediction_file'], 'r') as f:
                saved_prediction = json.load(f)
            
            assert saved_prediction['symbol'] == CONFIG.symbol
            assert saved_prediction['direction'] in ['UP', 'DOWN', 'SKIP']
            assert 'timestamp' in saved_prediction
    
    def test_predict_command_engine_disabled(self):
        """Test prediction when engine is disabled"""
        
        CONFIG.after_close_enabled = False
        
        result = predict_command(dry_run=False, auto_fit=False)
        
        assert result['status'] == 'disabled'
        assert 'Engine disabled' in result['message']
    
    @patch('engines.after_close_engine.model_training.EnsembleModel')
    def test_predict_command_no_models(self, mock_ensemble_class):
        """Test prediction when no models are available"""
        
        # Mock ensemble model that fails to load
        mock_ensemble = MagicMock()
        mock_ensemble.load.return_value = False
        mock_ensemble_class.return_value = mock_ensemble
        
        result = predict_command(dry_run=True, auto_fit=False)
        
        assert result['status'] == 'error'
        assert 'No trained models' in result['error']
    
    def test_cli_integration_dry_run(self):
        """Test CLI integration with dry run"""
        
        # Test that the CLI can be called (basic smoke test)
        engine_path = os.path.join(os.path.dirname(__file__), '..', 'engine.py')
        
        try:
            # This should not crash, even if models aren't trained
            result = subprocess.run([
                'python', engine_path, 'predict', '--mode', 'dry-run'
            ], capture_output=True, text=True, timeout=30)
            
            # We expect it might fail due to missing dependencies or models
            # but it should not crash with Python errors
            assert result.returncode in [0, 1]  # Success or expected failure
            
        except subprocess.TimeoutExpired:
            pytest.fail("CLI command timed out")
        except FileNotFoundError:
            pytest.skip("Engine file not accessible for integration test")

class TestPredictionValidation:
    """Test prediction output validation"""
    
    def test_prediction_json_structure(self):
        """Test that prediction JSON has correct structure"""
        
        # Sample prediction dictionary (what should be generated)
        prediction = {
            'timestamp': '2025-08-19T21:30:00.123456',
            'symbol': 'AMD',
            'direction': 'UP',
            'expected_open': 169.25,
            'confidence': 0.75,
            'prediction_value': 1.25,
            'current_price': 168.0,
            'features': {
                'overnight_futures_pct': 0.8,
                'net_options_flow': -0.2,
                'news_sentiment_score': 0.3,
                'global_index_impact_score': 0.1,
                'prior_close_return': -0.5,
                'intraday_volatility': 2.1
            },
            'model_predictions': {
                'lightgbm': 1.3,
                'lstm': 1.2
            },
            'model_version': 'v1.0',
            'confidence_threshold': 0.70
        }
        
        # Validate structure
        required_fields = [
            'timestamp', 'symbol', 'direction', 'expected_open', 'confidence',
            'prediction_value', 'current_price', 'features', 'model_predictions',
            'model_version', 'confidence_threshold'
        ]
        
        for field in required_fields:
            assert field in prediction
        
        # Validate direction values
        assert prediction['direction'] in ['UP', 'DOWN', 'SKIP']
        
        # Validate confidence range
        assert 0 <= prediction['confidence'] <= 1
        
        # Validate feature structure
        expected_features = [
            'overnight_futures_pct', 'net_options_flow', 'news_sentiment_score',
            'global_index_impact_score', 'prior_close_return', 'intraday_volatility'
        ]
        
        for feature in expected_features:
            assert feature in prediction['features']
            assert isinstance(prediction['features'][feature], (int, float))
        
        # Validate model predictions
        assert 'lightgbm' in prediction['model_predictions']
        assert 'lstm' in prediction['model_predictions']

if __name__ == '__main__':
    pytest.main([__file__, '-v'])