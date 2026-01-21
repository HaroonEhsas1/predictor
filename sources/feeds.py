#!/usr/bin/env python3
"""
Data Feeds Module
Robust data fetching with fallbacks and proper error handling
"""

import os
import sys
import time
import requests
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DATA_SOURCES, API_KEYS, DATA_QUALITY, PATHS
from manager.scheduler import scheduler

class DataFeedManager:
    """Manages all data sources with robust fallback logic"""
    
    def __init__(self):
        self.sources = DATA_SOURCES
        self.api_keys = API_KEYS
        self.cache_dir = PATHS['cache']
        self.last_fetch_times = {}
        
    def fetch_stock_data(self, symbol: str, timeframes: List[str] = None) -> Dict[str, Any]:
        """Main data fetching with intelligent fallback"""
        if timeframes is None:
            timeframes = ['1d', '1h', '15m', '5m', '1m']
        
        market_state = scheduler.get_market_state()
        fetch_strategy = scheduler.get_data_fetch_strategy()
        
        # Skip intraday on non-trading days
        if not market_state['is_trading_day']:
            timeframes = ['1d']  # Daily only
        
        results = {
            'symbol': symbol,
            'timeframes': {},
            'data_quality': DATA_QUALITY['STALE'],
            'sources_used': [],
            'fetch_timestamp': datetime.now().isoformat(),
            'market_state': market_state['session_phase']
        }
        
        # Try each source in priority order
        for source_name in sorted(self.sources.keys(), key=lambda x: self.sources[x]['priority']):
            try:
                source_data = self._fetch_from_source(source_name, symbol, timeframes)
                if source_data:
                    results['timeframes'].update(source_data)
                    results['sources_used'].append(source_name)
                    
                    # Determine data quality
                    if source_name == 'yahoo' and market_state['market_open']:
                        results['data_quality'] = DATA_QUALITY['LIVE']
                    elif len(results['sources_used']) == 1:
                        results['data_quality'] = DATA_QUALITY['LIVE']
                    else:
                        results['data_quality'] = DATA_QUALITY['FALLBACK']
                    
                    break  # Success with primary source
                    
            except Exception as e:
                print(f"⚠️  {source_name.upper()} failed: {str(e)[:100]}")
                time.sleep(self.sources[source_name]['rate_limit'])
                continue
        
        # Validate data completeness
        if not results['timeframes']:
            results['data_quality'] = DATA_QUALITY['STALE']
            print("❌ All data sources failed")
        
        return results
    
    def _fetch_from_source(self, source: str, symbol: str, timeframes: List[str]) -> Optional[Dict]:
        """Fetch data from specific source"""
        if source == 'yahoo':
            return self._fetch_yahoo_data(symbol, timeframes)
        elif source == 'polygon':
            return self._fetch_polygon_data(symbol, timeframes)
        elif source == 'eodhd':
            return self._fetch_eodhd_data(symbol, timeframes)
        elif source == 'stockdata':
            return self._fetch_stockdata_data(symbol, timeframes)
        elif source == 'twelvedata':
            return self._fetch_twelvedata_data(symbol, timeframes)
        return None
    
    def _fetch_yahoo_data(self, symbol: str, timeframes: List[str]) -> Dict[str, pd.DataFrame]:
        """Fetch data from Yahoo Finance"""
        results = {}
        ticker = yf.Ticker(symbol)
        
        timeframe_mapping = {
            '1m': ('1d', '1m'),     # Reduced to 1 day for better reliability
            '5m': ('5d', '5m'),     # Reduced period
            '15m': ('30d', '15m'),  # Reduced period  
            '1h': ('60d', '1h'),    # Reduced period
            '1d': ('2y', '1d')      # Reduced period
        }
        
        for tf in timeframes:
            if tf in timeframe_mapping:
                period, interval = timeframe_mapping[tf]
                try:
                    data = ticker.history(period=period, interval=interval)
                    if not data.empty:
                        results[tf] = data
                    else:
                        print(f"⚠️  Yahoo returned empty data for {tf}")
                except Exception as e:
                    error_msg = str(e).lower()
                    if "possibly delisted" in error_msg or "insufficient" in error_msg:
                        market_state = scheduler.get_market_state()
                        if not market_state['is_trading_day']:
                            print(f"📅 Weekend/Holiday: Skipping {tf} data for {symbol}")
                            continue
                        else:
                            # Try fallback with different period for intraday
                            if tf in ['1m', '5m']:
                                try:
                                    fallback_data = ticker.history(period='2d', interval=interval)
                                    if not fallback_data.empty:
                                        results[tf] = fallback_data.tail(100)  # Last 100 points
                                        print(f"✅ Yahoo fallback successful for {tf}")
                                        continue
                                except:
                                    pass
                            print(f"⚠️  Yahoo data issue: {str(e)[:80]}")
                    # Don't raise exception, let other sources try
                    print(f"⚠️  Yahoo {tf} failed: {str(e)[:60]}")
        
        return results
    
    def _fetch_polygon_data(self, symbol: str, timeframes: List[str]) -> Dict[str, pd.DataFrame]:
        """Fetch data from Polygon.io"""
        if not self.api_keys['polygon']:
            raise Exception("Polygon API key not configured")
        
        results = {}
        base_url = "https://api.polygon.io"
        
        # Implement intraday data for live trading
        timeframe_mapping = {
            '1m': ('minute', 1),
            '5m': ('minute', 5), 
            '15m': ('minute', 15),
            '1h': ('hour', 1),
            '1d': ('day', 1)
        }
        
        for tf in timeframes:
            if tf not in timeframe_mapping:
                continue
                
            multiplier_type, multiplier = timeframe_mapping[tf]
            
            try:
                # Calculate date range
                end_date = datetime.now().date()
                if tf == '1m':
                    start_date = end_date - timedelta(days=1)
                elif tf in ['5m', '15m']:
                    start_date = end_date - timedelta(days=5) 
                elif tf == '1h':
                    start_date = end_date - timedelta(days=30)
                else:  # 1d
                    start_date = end_date - timedelta(days=365)
                
                url = f"{base_url}/v2/aggs/ticker/{symbol}/range/{multiplier}/{multiplier_type}/{start_date}/{end_date}"
                params = {
                    'adjusted': 'true',
                    'sort': 'asc', 
                    'apikey': self.api_keys['polygon']
                }
                
                response = requests.get(url, params=params, timeout=15)
                
                if response.status_code == 401:
                    print(f"❌ Polygon API 401: Invalid or expired API key for {tf} data")
                    continue
                elif response.status_code == 403:
                    print(f"⚠️  Polygon 403: API key may need upgrade for {tf} data")
                    continue
                elif response.status_code != 200:
                    print(f"❌ Polygon API {response.status_code}: {response.text}")
                    continue
                    
                response.raise_for_status()
                
                data = response.json()
                if data.get('status') == 'OK' and data.get('results'):
                    # Convert to DataFrame with proper timestamps
                    df_data = []
                    for bar in data['results']:
                        timestamp = pd.to_datetime(bar['t'], unit='ms')
                        df_data.append({
                            'Open': float(bar['o']),
                            'High': float(bar['h']),
                            'Low': float(bar['l']),
                            'Close': float(bar['c']),
                            'Volume': int(bar['v']),
                            'Datetime': timestamp
                        })
                    
                    if df_data:
                        df = pd.DataFrame(df_data)
                        df.set_index('Datetime', inplace=True)
                        results[tf] = df
                        print(f"✅ Polygon {tf}: {len(df)} bars")
                
            except Exception as e:
                print(f"⚠️  Polygon {tf} failed: {str(e)[:60]}")
                continue
        
        return results
    
    def _fetch_eodhd_data(self, symbol: str, timeframes: List[str]) -> Dict[str, pd.DataFrame]:
        """Fetch data from EODHD"""
        if not self.api_keys['eodhd']:
            raise Exception("EODHD API key not configured")
        
        results = {}
        
        # Simplified implementation for daily data
        if '1d' in timeframes:
            try:
                url = f"https://eodhistoricaldata.com/api/eod/{symbol}.US"
                params = {
                    'api_token': self.api_keys['eodhd'],
                    'fmt': 'json',
                    'from': '2020-01-01'
                }
                
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                if data:
                    df_data = []
                    for entry in data:
                        df_data.append({
                            'Open': entry['open'],
                            'High': entry['high'],
                            'Low': entry['low'],
                            'Close': entry['close'],
                            'Volume': entry['volume']
                        })
                    
                    if df_data:
                        results['1d'] = pd.DataFrame(df_data)
                
            except Exception as e:
                raise Exception(f"EODHD daily data failed: {e}")
        
        return results
    
    def _fetch_stockdata_data(self, symbol: str, timeframes: List[str]) -> Dict[str, pd.DataFrame]:
        """Fetch data from StockData.org - FREE unlimited data"""
        from sources.stockdata_integration import StockDataFeed
        
        results = {}
        try:
            feed = StockDataFeed(api_key=self.api_keys.get('stockdata'))
            
            # Get real-time quote for current data
            quote = feed.get_real_time_quote(symbol)
            
            # Map timeframes to StockData intervals
            interval_mapping = {
                '1m': '1min',
                '5m': '5min',
                '15m': '15min',
                '1h': '1hour',
                '1d': 'day'
            }
            
            for tf in timeframes:
                if tf not in interval_mapping:
                    continue
                    
                try:
                    if tf == '1d':
                        df = feed.get_intraday_data(symbol, interval='day', days=730)
                    else:
                        df = feed.get_intraday_data(symbol, interval=interval_mapping[tf], days=5)
                    
                    if df is not None and not df.empty:
                        if 'open' in df.columns:
                            df.rename(columns={
                                'open': 'Open', 'high': 'High',
                                'low': 'Low', 'close': 'Close', 'volume': 'Volume'
                            }, inplace=True)
                        results[tf] = df
                        print(f"✅ StockData fetched {len(df)} bars for {tf}")
                except Exception as e:
                    print(f"⚠️  StockData {tf} failed: {str(e)[:60]}")
                    
        except Exception as e:
            print(f"⚠️  StockData fetch failed: {str(e)[:80]}")
            
        return results
    
    def _fetch_twelvedata_data(self, symbol: str, timeframes: List[str]) -> Dict[str, pd.DataFrame]:
        """Fetch data from TwelveData - FREE 800 calls/day"""
        from sources.twelvedata_integration import TwelveDataFeed
        
        results = {}
        try:
            feed = TwelveDataFeed(api_key=self.api_keys.get('twelvedata'))
            
            # Map timeframes to TwelveData intervals
            interval_mapping = {
                '1m': '1min',
                '5m': '5min',
                '15m': '15min',
                '1h': '1h',
                '1d': '1day'
            }
            
            for tf in timeframes:
                if tf not in interval_mapping:
                    continue
                    
                try:
                    outputsize = 300 if tf in ['1m', '5m'] else 500
                    df = feed.get_time_series(symbol, interval=interval_mapping[tf], outputsize=outputsize)
                    
                    if df is not None and not df.empty:
                        if 'open' in df.columns:
                            df.rename(columns={
                                'open': 'Open', 'high': 'High',
                                'low': 'Low', 'close': 'Close', 'volume': 'Volume'
                            }, inplace=True)
                        results[tf] = df
                        print(f"✅ TwelveData fetched {len(df)} bars for {tf}")
                except Exception as e:
                    print(f"⚠️  TwelveData {tf} failed: {str(e)[:60]}")
                    
        except Exception as e:
            print(f"⚠️  TwelveData fetch failed: {str(e)[:80]}")
            
        return results
    
    def validate_data_quality(self, data: Dict[str, Any]) -> bool:
        """Validate fetched data quality"""
        if not data.get('timeframes'):
            return False
        
        # Check for minimum data requirements
        for timeframe, df in data['timeframes'].items():
            if df.empty:
                continue
            
            # Check for basic OHLCV columns
            required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            if not all(col in df.columns for col in required_columns):
                return False
            
            # Check for reasonable data
            if df['Close'].isna().all():
                return False
        
        return True
    
    def get_cache_key(self, symbol: str, timeframe: str) -> str:
        """Generate cache key for data"""
        date_str = datetime.now().strftime('%Y-%m-%d')
        return f"{symbol}_{timeframe}_{date_str}"
    
    def cache_data(self, data: Dict[str, Any]):
        """Cache fetched data"""
        try:
            symbol = data['symbol']
            for timeframe, df in data['timeframes'].items():
                cache_key = self.get_cache_key(symbol, timeframe)
                cache_path = os.path.join(self.cache_dir, f"{cache_key}.pkl")
                df.to_pickle(cache_path)
        except Exception as e:
            print(f"⚠️  Cache save failed: {e}")
    
    def load_from_cache(self, symbol: str, timeframe: str) -> Optional[pd.DataFrame]:
        """Load data from cache if available"""
        try:
            cache_key = self.get_cache_key(symbol, timeframe)
            cache_path = os.path.join(self.cache_dir, f"{cache_key}.pkl")
            
            if os.path.exists(cache_path):
                return pd.read_pickle(cache_path)
        except Exception as e:
            print(f"⚠️  Cache load failed: {e}")
        
        return None

# Global data feed manager
data_manager = DataFeedManager()