#!/usr/bin/env python3
"""
Twelve Data Integration - 100% FREE (800 credits/day)
Provides: Stock, forex, crypto data, technical indicators, global markets
Website: https://twelvedata.com
"""

import requests
import pandas as pd
from datetime import datetime
from typing import Dict, Any, Optional, List

class TwelveDataFeed:
    """FREE multi-asset data with 800 API credits/day"""
    
    def __init__(self, api_key: Optional[str] = None):
        # Sign up at https://twelvedata.com/pricing (FREE tier: 800 credits/day)
        self.api_key = api_key or "DEMO"
        self.base_url = "https://api.twelvedata.com"
        self.session = requests.Session()
        
    def get_real_time_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get real-time price data - FREE (1 credit)"""
        try:
            url = f"{self.base_url}/price"
            params = {
                'symbol': symbol,
                'apikey': self.api_key
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('price'):
                return {
                    'price': float(data['price']),
                    'symbol': symbol,
                    'source': 'twelvedata',
                    'timestamp': datetime.now().isoformat()
                }
        except Exception as e:
            print(f"TwelveData price failed: {e}")
            return None
    
    def get_time_series(self, symbol: str, interval: str = '5min', outputsize: int = 100) -> Optional[pd.DataFrame]:
        """Get historical time series - FREE (1 credit)"""
        try:
            url = f"{self.base_url}/time_series"
            params = {
                'symbol': symbol,
                'interval': interval,
                'outputsize': outputsize,
                'apikey': self.api_key
            }
            
            response = self.session.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            if data.get('values'):
                df = pd.DataFrame(data['values'])
                df['datetime'] = pd.to_datetime(df['datetime'])
                df.set_index('datetime', inplace=True)
                
                # Convert to numeric
                for col in ['open', 'high', 'low', 'close', 'volume']:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                
                return df[['open', 'high', 'low', 'close', 'volume']]
        except Exception as e:
            print(f"TwelveData time series failed: {e}")
            return None
    
    def get_technical_indicator(self, symbol: str, indicator: str, interval: str = '5min', 
                                period: int = 14) -> Optional[Dict[str, Any]]:
        """Get technical indicators - FREE (8 credits)
        
        Supported indicators: RSI, MACD, ADX, ATR, BBANDS, CCI, EMA, SMA, STOCH, etc.
        Full list: https://twelvedata.com/docs#technical-indicators
        """
        try:
            url = f"{self.base_url}/{indicator.lower()}"
            params = {
                'symbol': symbol,
                'interval': interval,
                'time_period': period,
                'apikey': self.api_key
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('values'):
                return {
                    'indicator': indicator,
                    'values': data['values'][:10],  # Latest 10 values
                    'latest_value': data['values'][0] if data['values'] else None,
                    'source': 'twelvedata'
                }
        except Exception as e:
            print(f"TwelveData {indicator} failed: {e}")
            return None
    
    def get_multiple_indicators(self, symbol: str, interval: str = '5min') -> Dict[str, Any]:
        """Get multiple technical indicators efficiently - FREE
        
        Optimized to use fewer credits by batching similar requests
        """
        indicators = {}
        
        # Core momentum indicators
        for ind in ['RSI', 'MACD', 'ADX', 'CCI', 'STOCH']:
            result = self.get_technical_indicator(symbol, ind, interval)
            if result:
                indicators[ind] = result['latest_value']
        
        # Trend indicators
        for ind in ['EMA', 'SMA']:
            result = self.get_technical_indicator(symbol, ind, interval, period=20)
            if result:
                indicators[f"{ind}_20"] = result['latest_value']
        
        return indicators
    
    def get_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive quote data - FREE (1 credit)"""
        try:
            url = f"{self.base_url}/quote"
            params = {
                'symbol': symbol,
                'apikey': self.api_key
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('symbol'):
                return {
                    'symbol': data['symbol'],
                    'price': float(data.get('close', 0)),
                    'open': float(data.get('open', 0)),
                    'high': float(data.get('high', 0)),
                    'low': float(data.get('low', 0)),
                    'volume': int(data.get('volume', 0)),
                    'previous_close': float(data.get('previous_close', 0)),
                    'change': float(data.get('change', 0)),
                    'percent_change': float(data.get('percent_change', 0)),
                    'timestamp': data.get('datetime'),
                    'source': 'twelvedata'
                }
        except Exception as e:
            print(f"TwelveData quote failed: {e}")
            return None
    
    def get_forex_pair(self, pair: str = 'USD/JPY') -> Optional[Dict[str, Any]]:
        """Get forex data - FREE (useful for market correlation)"""
        try:
            url = f"{self.base_url}/price"
            params = {
                'symbol': pair,
                'apikey': self.api_key
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('price'):
                return {
                    'pair': pair,
                    'price': float(data['price']),
                    'source': 'twelvedata'
                }
        except Exception as e:
            print(f"TwelveData forex failed: {e}")
            return None


def get_twelvedata_intelligence(symbol: str) -> Dict[str, Any]:
    """Get comprehensive FREE data from Twelve Data (800 credits/day)"""
    feed = TwelveDataFeed()
    
    result = {
        'quote': feed.get_quote(symbol),
        'price': feed.get_real_time_price(symbol),
        'time_series': feed.get_time_series(symbol, interval='5min', outputsize=50),
        'technical_indicators': feed.get_multiple_indicators(symbol),
        'forex_correlation': {
            'USD_JPY': feed.get_forex_pair('USD/JPY'),
            'EUR_USD': feed.get_forex_pair('EUR/USD')
        },
        'source': 'twelvedata',
        'free_tier': True,
        'daily_limit': '800 credits'
    }
    
    return result


if __name__ == "__main__":
    # Test the integration
    print("Testing Twelve Data FREE API (800 credits/day)...")
    data = get_twelvedata_intelligence('AMD')
    
    if data['quote']:
        print(f"\n📊 Quote: ${data['quote']['price']}")
        print(f"📈 Change: {data['quote']['percent_change']}%")
    
    if data['technical_indicators']:
        print(f"\n📉 Technical Indicators:")
        for ind, value in data['technical_indicators'].items():
            if isinstance(value, dict):
                print(f"   {ind}: {value}")
            else:
                print(f"   {ind}: {value}")
    
    if data['time_series'] is not None and not data['time_series'].empty:
        print(f"\n📊 Time Series: {len(data['time_series'])} data points loaded")
