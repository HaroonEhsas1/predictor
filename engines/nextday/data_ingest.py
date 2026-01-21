"""
Professional data ingestion module for next-day predictions
Implements institutional-grade data validation and normalization
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple, Any
import logging
import warnings
try:
    from .config import CONFIG
except ImportError:
    try:
        from engines.nextday.config import CONFIG
    except ImportError:
        from config import CONFIG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataIngestionEngine:
    """
    Professional data ingestion with validation and normalization
    Implements institutional best practices for data quality
    """
    
    def __init__(self):
        self.symbols = {
            'amd': 'AMD',
            'futures_es': 'ES=F',
            'futures_nq': 'NQ=F', 
            'vix': '^VIX',
            'soxx': 'SOXX',
            'nvda': 'NVDA'
        }
        
    def fetch_comprehensive_data(self, lookback_days: int = 60) -> Dict[str, pd.DataFrame]:
        """
        Fetch comprehensive market data with validation
        
        Args:
            lookback_days: Days of historical data to fetch
            
        Returns:
            Dictionary of validated DataFrames with UTC timestamps
        """
        
        logger.info(f"Fetching {lookback_days} days of market data...")
        
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=lookback_days)
        
        data = {}
        validation_results = {}
        
        for name, symbol in self.symbols.items():
            try:
                logger.info(f"Fetching {name} ({symbol})...")
                df = self._fetch_single_asset(symbol, start_date, end_date)
                
                if df is not None:
                    # Validate data quality
                    validation = self._validate_data_quality(df, name, symbol)
                    validation_results[name] = validation
                    
                    if validation['is_valid']:
                        data[name] = df
                        logger.info(f"✓ {name}: {len(df)} valid samples")
                    else:
                        logger.warning(f"✗ {name}: Failed validation - {validation['reason']}")
                        
            except Exception as e:
                logger.error(f"Failed to fetch {name} ({symbol}): {e}")
                validation_results[name] = {
                    'is_valid': False, 
                    'reason': f'Fetch error: {str(e)}'
                }
        
        # Check if we have minimum required data
        if not self._check_minimum_requirements(data, validation_results):
            raise ValueError("Insufficient data quality for reliable predictions")
            
        logger.info(f"Successfully ingested {len(data)} assets")
        return data
    
    def _fetch_single_asset(self, symbol: str, start_date: datetime, end_date: datetime) -> Optional[pd.DataFrame]:
        """Fetch single asset with error handling"""
        
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")  # Suppress yfinance warnings
                
                ticker = yf.Ticker(symbol)
                hist = ticker.history(
                    start=start_date.date(),
                    end=end_date.date(),
                    interval='1d',
                    auto_adjust=True,
                    prepost=False
                )
                
                if hist.empty:
                    logger.warning(f"No data returned for {symbol}")
                    return None
                
                # Convert to UTC timezone
                if hasattr(hist.index, 'tz') and hist.index.tz is None:
                    hist.index = pd.to_datetime(hist.index).tz_localize('UTC')
                elif hasattr(hist.index, 'tz_convert'):
                    hist.index = hist.index.tz_convert('UTC')
                
                # Add basic derived features
                hist['returns'] = hist['Close'].pct_change()
                hist['volatility'] = hist['returns'].rolling(20).std() * np.sqrt(252)
                hist['volume_ratio'] = hist['Volume'] / hist['Volume'].rolling(20).mean()
                
                return hist
                
        except Exception as e:
            logger.error(f"Error fetching {symbol}: {e}")
            return None
    
    def _validate_data_quality(self, df: pd.DataFrame, name: str, symbol: str) -> Dict[str, Any]:
        """
        Comprehensive data quality validation
        Implements institutional data integrity checks
        """
        
        if df is None or df.empty:
            return {'is_valid': False, 'reason': 'Empty dataset'}
        
        validation = {
            'is_valid': True,
            'reason': '',
            'sample_count': len(df),
            'missing_data_pct': 0.0,
            'price_anomalies': [],
            'volume_anomalies': []
        }
        
        # Check minimum sample count
        min_samples = CONFIG.required_lookback_days * 0.7  # Allow for weekends
        if len(df) < min_samples:
            validation['is_valid'] = False
            validation['reason'] = f'Insufficient samples: {len(df)} < {min_samples}'
            return validation
        
        # Check for missing data
        missing_pct = df[['Open', 'High', 'Low', 'Close', 'Volume']].isnull().sum().max() / len(df)
        validation['missing_data_pct'] = missing_pct
        
        if missing_pct > CONFIG.max_missing_data_pct:
            validation['is_valid'] = False
            validation['reason'] = f'Too much missing data: {missing_pct:.1%} > {CONFIG.max_missing_data_pct:.1%}'
            return validation
        
        # Check for price anomalies (gaps > 20%)
        returns = df['Close'].pct_change().abs()
        large_gaps = returns[returns > 0.20]
        if len(large_gaps) > 2:
            validation['price_anomalies'] = large_gaps.index.tolist()
            logger.warning(f"{name}: Found {len(large_gaps)} large price gaps")
        
        # Check for volume anomalies (zero volume days)
        zero_volume_days = (df['Volume'] == 0).sum()
        if zero_volume_days > len(df) * 0.02:  # More than 2% zero volume days
            validation['volume_anomalies'].append(f'{zero_volume_days} zero volume days')
        
        # Check timestamp consistency (no large gaps)
        time_gaps = df.index.to_series().diff()
        large_time_gaps = time_gaps[time_gaps > pd.Timedelta(days=5)]  # More than 5 days
        if len(large_time_gaps) > 3:
            validation['is_valid'] = False
            validation['reason'] = f'Inconsistent timestamps: {len(large_time_gaps)} large gaps'
            return validation
        
        logger.info(f"✓ {name} validation passed: {validation['sample_count']} samples, {validation['missing_data_pct']:.1%} missing")
        return validation
    
    def _check_minimum_requirements(self, data: Dict[str, pd.DataFrame], validation_results: Dict[str, Dict]) -> bool:
        """Check if minimum data requirements are met for reliable predictions"""
        
        # Must have AMD data
        if 'amd' not in data:
            logger.error("Critical: AMD data not available")
            return False
        
        # Must have at least 2 market indicators
        available_indicators = [name for name in ['vix', 'soxx', 'nvda'] if name in data]
        if len(available_indicators) < 2:
            logger.error(f"Insufficient market indicators: {len(available_indicators)} < 2")
            return False
        
        # Check if we have recent data (within last 5 days)
        latest_amd_date = data['amd'].index.max()
        if hasattr(latest_amd_date, 'to_pydatetime'):
            latest_amd_date = latest_amd_date.to_pydatetime()
        elif hasattr(latest_amd_date, 'date'):
            latest_amd_date = latest_amd_date
        else:
            latest_amd_date = pd.to_datetime(latest_amd_date)
        days_old = (datetime.now(timezone.utc) - latest_amd_date).days
        if days_old > 5:
            logger.error(f"AMD data too stale: {days_old} days old")
            return False
        
        logger.info("✓ Minimum data requirements satisfied")
        return True
    
    def get_futures_data(self) -> Dict[str, float]:
        """Get real-time futures data for overnight analysis"""
        
        try:
            futures_data = {}
            
            for name in ['futures_es', 'futures_nq']:
                symbol = self.symbols[name]
                ticker = yf.Ticker(symbol)
                
                # Get recent data
                hist = ticker.history(period='5d', interval='1h')
                if not hist.empty:
                    current_price = float(hist['Close'].iloc[-1])
                    prev_close = float(hist['Close'].iloc[-2])
                    futures_data[name] = {
                        'current': current_price,
                        'prev_close': prev_close,
                        'change_pct': (current_price - prev_close) / prev_close
                    }
            
            return futures_data
            
        except Exception as e:
            logger.error(f"Failed to get futures data: {e}")
            return {}
    
    def normalize_timestamps(self, data: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """Ensure all data has consistent UTC timestamps"""
        
        normalized = {}
        
        for name, df in data.items():
            df_copy = df.copy()
            
            # Ensure UTC timezone
            if hasattr(df_copy.index, 'tz'):
                if df_copy.index.tz is None:
                    df_copy.index = df_copy.index.tz_localize('UTC')
                elif df_copy.index.tz != timezone.utc:
                    df_copy.index = df_copy.index.tz_convert('UTC')
            
            normalized[name] = df_copy
        
        return normalized

# Export main class and utility functions
__all__ = ['DataIngestionEngine']