#!/usr/bin/env python3
"""
StockData.org Integration - 100% FREE (No limits mentioned)
Provides: Real-time prices, intraday data (6+ years), extended hours, news, sentiment
Website: https://www.stockdata.org
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List

class StockDataFeed:
    """FREE real-time stock data with news and sentiment"""
    
    def __init__(self, api_key: Optional[str] = None):
        # StockData.org offers free tier - check their website for API key
        self.api_key = api_key or "DEMO"  # Some endpoints work without key
        self.base_url = "https://api.stockdata.org/v1"
        self.session = requests.Session()
        self.session.headers.update({'Accept': 'application/json'})
        
    def get_real_time_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get real-time quote data - FREE"""
        try:
            url = f"{self.base_url}/data/quote"
            params = {
                'symbols': symbol,
                'api_token': self.api_key
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('data'):
                quote = data['data'][0]
                return {
                    'price': quote.get('price'),
                    'change': quote.get('change'),
                    'change_percent': quote.get('change_percent'),
                    'volume': quote.get('volume'),
                    'day_high': quote.get('day_high'),
                    'day_low': quote.get('day_low'),
                    'day_open': quote.get('day_open'),
                    'previous_close': quote.get('previous_close'),
                    'timestamp': quote.get('last_update_utc'),
                    'source': 'stockdata.org'
                }
        except Exception as e:
            print(f"StockData quote failed: {e}")
            return None
    
    def get_intraday_data(self, symbol: str, interval: str = '5min', days: int = 5) -> Optional[pd.DataFrame]:
        """Get intraday historical data (6+ years available) - FREE"""
        try:
            url = f"{self.base_url}/data/intraday"
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            params = {
                'symbols': symbol,
                'interval': interval,
                'date_from': start_date.strftime('%Y-%m-%d'),
                'date_to': end_date.strftime('%Y-%m-%d'),
                'api_token': self.api_key
            }
            
            response = self.session.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            if data.get('data'):
                df = pd.DataFrame(data['data'])
                df['timestamp'] = pd.to_datetime(df['date'])
                df.set_index('timestamp', inplace=True)
                return df[['open', 'high', 'low', 'close', 'volume']]
        except Exception as e:
            print(f"StockData intraday failed: {e}")
            return None
    
    def get_extended_hours(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get pre-market and after-hours data - FREE"""
        try:
            url = f"{self.base_url}/data/quote"
            params = {
                'symbols': symbol,
                'extended_hours': 'true',
                'api_token': self.api_key
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('data'):
                quote = data['data'][0]
                return {
                    'premarket_price': quote.get('premarket_price'),
                    'premarket_change': quote.get('premarket_change'),
                    'afterhours_price': quote.get('afterhours_price'),
                    'afterhours_change': quote.get('afterhours_change'),
                    'source': 'stockdata.org'
                }
        except Exception as e:
            print(f"StockData extended hours failed: {e}")
            return None
    
    def get_news_sentiment(self, symbol: str, limit: int = 20) -> Optional[Dict[str, Any]]:
        """Get news with sentiment analysis from 5,000+ sources - FREE"""
        try:
            url = f"{self.base_url}/news"
            params = {
                'symbols': symbol,
                'limit': limit,
                'api_token': self.api_key
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('data'):
                articles = data['data']
                
                # Calculate aggregate sentiment
                sentiments = [a.get('sentiment', 0) for a in articles if a.get('sentiment')]
                avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0
                
                return {
                    'articles': articles[:10],  # Top 10 recent
                    'total_count': len(articles),
                    'avg_sentiment': avg_sentiment,
                    'sentiment_direction': 'bullish' if avg_sentiment > 0.1 else 'bearish' if avg_sentiment < -0.1 else 'neutral',
                    'recent_headlines': [a.get('title') for a in articles[:5]],
                    'source': 'stockdata.org'
                }
        except Exception as e:
            print(f"StockData news failed: {e}")
            return None


def get_stockdata_intelligence(symbol: str) -> Dict[str, Any]:
    """Get comprehensive FREE data from StockData.org"""
    feed = StockDataFeed()
    
    result = {
        'quote': feed.get_real_time_quote(symbol),
        'extended_hours': feed.get_extended_hours(symbol),
        'news_sentiment': feed.get_news_sentiment(symbol),
        'intraday_data': feed.get_intraday_data(symbol, interval='5min', days=5),
        'source': 'stockdata.org',
        'free_tier': True
    }
    
    return result


if __name__ == "__main__":
    # Test the integration
    print("Testing StockData.org FREE API...")
    data = get_stockdata_intelligence('AMD')
    
    if data['quote']:
        print(f"\n📊 Real-time Quote: ${data['quote']['price']}")
        print(f"📈 Change: {data['quote']['change_percent']}%")
    
    if data['extended_hours']:
        print(f"\n🌙 After Hours: ${data['extended_hours'].get('afterhours_price', 'N/A')}")
    
    if data['news_sentiment']:
        print(f"\n📰 News Sentiment: {data['news_sentiment']['sentiment_direction'].upper()}")
        print(f"   Average Score: {data['news_sentiment']['avg_sentiment']:.3f}")
