"""
Unit tests for fetchers module
"""
import pytest
import json
from unittest.mock import patch, mock_open
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fetchers import (
    fetch_futures, 
    fetch_options_summary, 
    fetch_news_sentiment, 
    fetch_global_indices,
    read_intraday_snapshot,
    collect_all_data
)
from config import CONFIG

class TestFetchers:
    """Test suite for data fetchers"""
    
    def test_fetch_futures_mock_mode(self):
        """Test futures fetching in mock mode"""
        CONFIG.mock_mode = True
        
        result = fetch_futures()
        
        assert isinstance(result, dict)
        assert 'ES_pct' in result
        assert 'NQ_pct' in result
        assert 'timestamp' in result
        assert result['source'] == 'mock'
        assert isinstance(result['ES_pct'], (int, float))
        assert isinstance(result['NQ_pct'], (int, float))
        assert -3.0 <= result['ES_pct'] <= 3.0  # Reasonable range
        assert -3.0 <= result['NQ_pct'] <= 3.0
    
    def test_fetch_options_summary_mock_mode(self):
        """Test options fetching in mock mode"""
        CONFIG.mock_mode = True
        
        result = fetch_options_summary("AMD")
        
        assert isinstance(result, dict)
        assert result['symbol'] == 'AMD'
        assert 'call_flow' in result
        assert 'put_flow' in result
        assert 'total_flow' in result
        assert 'call_put_ratio' in result
        assert 'unusual_activity' in result
        assert result['source'] == 'mock'
        
        # Verify mathematical consistency
        assert result['call_flow'] + result['put_flow'] == result['total_flow']
        if result['put_flow'] > 0:
            expected_ratio = result['call_flow'] / result['put_flow']
            assert abs(result['call_put_ratio'] - expected_ratio) < 0.01
    
    def test_fetch_news_sentiment_mock_mode(self):
        """Test news sentiment fetching in mock mode"""
        CONFIG.mock_mode = True
        
        result = fetch_news_sentiment("AMD")
        
        assert isinstance(result, dict)
        assert result['symbol'] == 'AMD'
        assert 'sentiment_score' in result
        assert 'headline_count' in result
        assert 'top_headlines' in result
        assert result['source'] == 'mock'
        assert -1.0 <= result['sentiment_score'] <= 1.0  # Sentiment range
        assert isinstance(result['top_headlines'], list)
        assert len(result['top_headlines']) <= result['headline_count']
    
    def test_fetch_global_indices_mock_mode(self):
        """Test global indices fetching in mock mode"""
        CONFIG.mock_mode = True
        
        result = fetch_global_indices()
        
        assert isinstance(result, dict)
        assert 'nikkei_pct' in result
        assert 'hang_seng_pct' in result
        assert 'ftse_pct' in result
        assert 'dax_pct' in result
        assert 'cac40_pct' in result
        assert result['source'] == 'mock'
        
        # Check reasonable ranges for market moves
        for key in ['nikkei_pct', 'hang_seng_pct', 'ftse_pct', 'dax_pct', 'cac40_pct']:
            assert -5.0 <= result[key] <= 5.0  # Reasonable daily range
    
    @patch('builtins.open', mock_open(read_data='{"test": "data", "price": 168.50}'))
    def test_read_intraday_snapshot_success(self):
        """Test successful snapshot reading"""
        
        result = read_intraday_snapshot()
        
        assert result is not None
        assert isinstance(result, dict)
        assert result['test'] == 'data'
        assert result['price'] == 168.50
    
    @patch('builtins.open', side_effect=FileNotFoundError())
    def test_read_intraday_snapshot_not_found(self):
        """Test snapshot reading when file not found"""
        
        result = read_intraday_snapshot()
        
        assert result is None
    
    @patch('builtins.open', side_effect=json.JSONDecodeError("Invalid JSON", "", 0))
    def test_read_intraday_snapshot_invalid_json(self):
        """Test snapshot reading with invalid JSON"""
        
        result = read_intraday_snapshot()
        
        assert result is None
    
    def test_collect_all_data(self):
        """Test comprehensive data collection"""
        CONFIG.mock_mode = True
        
        result = collect_all_data("AMD")
        
        assert isinstance(result, dict)
        assert result['symbol'] == 'AMD'
        assert 'collection_timestamp' in result
        assert 'futures' in result
        assert 'options' in result
        assert 'news' in result
        assert 'global_indices' in result
        assert 'snapshot' in result  # May be None
        
        # Verify timestamp format
        timestamp_str = result['collection_timestamp']
        datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))  # Should not raise
    
    def test_futures_fallback_mode(self):
        """Test futures fetching in fallback mode"""
        CONFIG.mock_mode = False
        
        result = fetch_futures()
        
        assert isinstance(result, dict)
        assert result['ES_pct'] == 0.0  # Fallback value
        assert result['NQ_pct'] == 0.0  # Fallback value
        assert result['source'] == 'fallback'
    
    def test_options_fallback_mode(self):
        """Test options fetching in fallback mode"""
        CONFIG.mock_mode = False
        
        result = fetch_options_summary("AMD")
        
        assert isinstance(result, dict)
        assert result['symbol'] == 'AMD'
        assert result['call_flow'] == 0
        assert result['put_flow'] == 0
        assert result['total_flow'] == 0
        assert result['source'] == 'fallback'

if __name__ == '__main__':
    pytest.main([__file__, '-v'])