#!/usr/bin/env python3
"""
MarketAux API Integration
Provides news sentiment analysis with entity extraction and trending stocks
"""

import os
import requests
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import time

logger = logging.getLogger(__name__)

class MarketAuxProvider:
    """MarketAux API integration for news sentiment and trending analysis"""
    
    def __init__(self):
        self.api_token = os.getenv('MARKETAUX_API_KEY', '')
        self.base_url = 'https://api.marketaux.com/v1'
        self.enabled = bool(self.api_token)
        
        if self.enabled:
            logger.info("✅ MarketAux API: Connected")
        else:
            logger.warning("⚠️ MarketAux API: Disabled (no API key)")
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make API request with error handling"""
        if not self.enabled:
            return None
        
        try:
            url = f"{self.base_url}/{endpoint}"
            
            # Add API token to params
            if params is None:
                params = {}
            params['api_token'] = self.api_token
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.Timeout:
            logger.error(f"MarketAux API timeout for {endpoint}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"MarketAux API error for {endpoint}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected MarketAux error: {e}")
            return None
    
    def get_news_sentiment(self, symbols: str, hours_back: int = 24, language: str = 'en') -> Optional[Dict[str, Any]]:
        """
        Get latest news with sentiment analysis for given symbols
        
        Args:
            symbols: Comma-separated ticker symbols (e.g., 'AMD,NVDA,INTC')
            hours_back: How many hours of news to fetch
            language: Language code (default: 'en')
        
        Returns: News articles with sentiment scores and entity analysis
        """
        published_after = (datetime.now() - timedelta(hours=hours_back)).isoformat()
        
        params = {
            'symbols': symbols,
            'published_after': published_after,
            'language': language,
            'limit': 50
        }
        
        data = self._make_request('news/all', params)
        
        if data and 'data' in data:
            articles = []
            total_sentiment = 0
            sentiment_count = 0
            
            for article in data['data']:
                # Extract sentiment from entities
                entities = article.get('entities', [])
                article_sentiment = 0
                
                if entities:
                    for entity in entities:
                        if entity.get('sentiment_score'):
                            article_sentiment += entity['sentiment_score']
                    article_sentiment = article_sentiment / len(entities) if entities else 0
                
                total_sentiment += article_sentiment
                sentiment_count += 1
                
                articles.append({
                    'title': article.get('title', ''),
                    'description': article.get('description', ''),
                    'url': article.get('url', ''),
                    'published_at': article.get('published_at', ''),
                    'source': article.get('source', ''),
                    'sentiment_score': article_sentiment,
                    'entities': [
                        {
                            'symbol': e.get('symbol', ''),
                            'name': e.get('name', ''),
                            'sentiment': e.get('sentiment_score', 0),
                            'match_score': e.get('match_score', 0)
                        }
                        for e in entities
                    ]
                })
            
            avg_sentiment = total_sentiment / sentiment_count if sentiment_count > 0 else 0
            
            return {
                'symbols': symbols,
                'article_count': len(articles),
                'average_sentiment': round(avg_sentiment, 3),
                'sentiment_direction': 'BULLISH' if avg_sentiment > 0.1 else 'BEARISH' if avg_sentiment < -0.1 else 'NEUTRAL',
                'articles': articles[:10],  # Top 10 most recent
                'timestamp': datetime.now().isoformat(),
                'source': 'marketaux'
            }
        
        return None
    
    def get_sentiment_aggregation(self, symbols: str, hours_back: int = 24) -> Optional[Dict[str, Any]]:
        """
        Get aggregated sentiment statistics for symbols
        Returns: Total documents, average sentiment per symbol
        """
        published_after = (datetime.now() - timedelta(hours=hours_back)).isoformat()
        
        params = {
            'symbols': symbols,
            'published_after': published_after,
            'language': 'en'
        }
        
        data = self._make_request('entity/stats/aggregation', params)
        
        if data and 'data' in data:
            stats = []
            
            for item in data['data']:
                stats.append({
                    'symbol': item.get('key', ''),
                    'total_documents': item.get('total_documents', 0),
                    'sentiment_avg': item.get('sentiment_avg', 0),
                    'sentiment_direction': 'BULLISH' if item.get('sentiment_avg', 0) > 0.1 else 'BEARISH' if item.get('sentiment_avg', 0) < -0.1 else 'NEUTRAL'
                })
            
            return {
                'symbols': symbols,
                'hours_analyzed': hours_back,
                'stats': stats,
                'timestamp': datetime.now().isoformat(),
                'source': 'marketaux'
            }
        
        return None
    
    def get_sentiment_time_series(self, symbols: str, interval: str = 'hour', days_back: int = 7) -> Optional[Dict[str, Any]]:
        """
        Get time-series sentiment data
        
        Args:
            symbols: Comma-separated symbols
            interval: 'minute', 'hour', 'day', 'week', 'month'
            days_back: Number of days to analyze
        
        Returns: Time-series sentiment data
        """
        published_after = (datetime.now() - timedelta(days=days_back)).isoformat()
        published_before = datetime.now().isoformat()
        
        params = {
            'symbols': symbols,
            'interval': interval,
            'group_by': 'symbol',
            'published_after': published_after,
            'published_before': published_before
        }
        
        data = self._make_request('entity/stats/intraday', params)
        
        if data and 'data' in data:
            time_series = []
            
            for point in data['data']:
                time_series.append({
                    'date': point.get('date', ''),
                    'data': point.get('data', [])
                })
            
            return {
                'symbols': symbols,
                'interval': interval,
                'days_analyzed': days_back,
                'time_series': time_series,
                'timestamp': datetime.now().isoformat(),
                'source': 'marketaux'
            }
        
        return None
    
    def get_trending_entities(self, countries: str = 'us', min_doc_count: int = 5, hours_back: int = 24) -> Optional[Dict[str, Any]]:
        """
        Get trending stocks/entities based on news volume and sentiment
        
        Args:
            countries: Country codes (e.g., 'us,ca')
            min_doc_count: Minimum number of articles to be considered trending
            hours_back: Hours to analyze
        
        Returns: Trending entities with volume + sentiment scores
        """
        published_after = (datetime.now() - timedelta(hours=hours_back)).isoformat()
        
        params = {
            'countries': countries,
            'min_doc_count': min_doc_count,
            'published_after': published_after,
            'language': 'en'
        }
        
        data = self._make_request('entity/trending/aggregation', params)
        
        if data and 'data' in data:
            trending = []
            
            for item in data['data']:
                trending.append({
                    'symbol': item.get('key', ''),
                    'total_documents': item.get('total_documents', 0),
                    'sentiment_avg': item.get('sentiment_avg', 0),
                    'trending_score': item.get('score', 0),  # Combined volume + sentiment
                    'sentiment_direction': 'BULLISH' if item.get('sentiment_avg', 0) > 0.1 else 'BEARISH' if item.get('sentiment_avg', 0) < -0.1 else 'NEUTRAL'
                })
            
            return {
                'countries': countries,
                'hours_analyzed': hours_back,
                'trending_count': len(trending),
                'trending_entities': trending[:20],  # Top 20
                'timestamp': datetime.now().isoformat(),
                'source': 'marketaux'
            }
        
        return None
    
    def get_negative_sentiment_alerts(self, symbols: str, threshold: float = -0.2, hours_back: int = 6) -> Optional[Dict[str, Any]]:
        """
        Get alerts for stocks with significantly negative sentiment
        
        Args:
            symbols: Comma-separated symbols to monitor
            threshold: Sentiment threshold (e.g., -0.2 for very negative)
            hours_back: Hours to check
        
        Returns: Stocks with negative sentiment alerts
        """
        published_after = (datetime.now() - timedelta(hours=hours_back)).isoformat()
        
        params = {
            'symbols': symbols,
            'sentiment_lte': threshold,
            'published_after': published_after,
            'language': 'en',
            'limit': 20
        }
        
        data = self._make_request('news/all', params)
        
        if data and 'data' in data:
            alerts = []
            
            for article in data['data']:
                entities = article.get('entities', [])
                
                for entity in entities:
                    if entity.get('sentiment_score', 0) <= threshold:
                        alerts.append({
                            'symbol': entity.get('symbol', ''),
                            'title': article.get('title', ''),
                            'sentiment_score': entity.get('sentiment_score', 0),
                            'published_at': article.get('published_at', ''),
                            'url': article.get('url', ''),
                            'source': article.get('source', '')
                        })
            
            return {
                'symbols': symbols,
                'threshold': threshold,
                'alert_count': len(alerts),
                'alerts': alerts[:10],  # Top 10 alerts
                'timestamp': datetime.now().isoformat(),
                'source': 'marketaux'
            }
        
        return None
    
    def get_comprehensive_sentiment(self, symbol: str) -> Dict[str, Any]:
        """
        Get comprehensive sentiment analysis for a symbol
        Returns: News, aggregated stats, trending status
        """
        if not self.enabled:
            return {'enabled': False, 'source': 'marketaux'}
        
        logger.info(f"📰 MarketAux: Fetching sentiment analysis for {symbol}")
        
        result = {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'source': 'marketaux',
            'enabled': True
        }
        
        # Recent news sentiment (24 hours)
        result['news_24h'] = self.get_news_sentiment(symbol, hours_back=24)
        time.sleep(0.2)
        
        # Aggregated sentiment stats
        result['sentiment_stats'] = self.get_sentiment_aggregation(symbol, hours_back=24)
        time.sleep(0.2)
        
        # Check for negative alerts (last 6 hours)
        result['negative_alerts'] = self.get_negative_sentiment_alerts(symbol, threshold=-0.2, hours_back=6)
        time.sleep(0.2)
        
        # Time series sentiment (last 7 days, hourly)
        result['sentiment_trend'] = self.get_sentiment_time_series(symbol, interval='hour', days_back=7)
        
        logger.info(f"✅ MarketAux: Sentiment analysis complete for {symbol}")
        
        return result


# Global instance
marketaux_provider = MarketAuxProvider()


if __name__ == "__main__":
    # Test the integration
    logging.basicConfig(level=logging.INFO)
    
    symbol = "AMD"
    
    # Test news sentiment
    print(f"\n📰 MarketAux Sentiment Analysis for {symbol}:")
    
    sentiment = marketaux_provider.get_comprehensive_sentiment(symbol)
    
    print(f"Enabled: {sentiment.get('enabled')}")
    
    if sentiment.get('news_24h'):
        news = sentiment['news_24h']
        print(f"\n24-Hour News Summary:")
        print(f"  Articles: {news['article_count']}")
        print(f"  Avg Sentiment: {news['average_sentiment']:.3f}")
        print(f"  Direction: {news['sentiment_direction']}")
    
    if sentiment.get('sentiment_stats'):
        stats = sentiment['sentiment_stats']['stats'][0] if sentiment['sentiment_stats']['stats'] else {}
        print(f"\nSentiment Stats:")
        print(f"  Total Documents: {stats.get('total_documents', 0)}")
        print(f"  Avg Sentiment: {stats.get('sentiment_avg', 0):.3f}")
    
    # Test trending entities
    print(f"\n🔥 Trending Stocks:")
    trending = marketaux_provider.get_trending_entities(hours_back=24)
    if trending:
        for entity in trending['trending_entities'][:5]:
            print(f"  {entity['symbol']}: Score={entity['trending_score']:.2f}, Sentiment={entity['sentiment_avg']:.3f}")
