"""
Finnhub Free API Data Source (60 calls/min free tier)
Provides real-time quotes, news, and earnings data
No hardcoded values - all data is real-time from API
"""

import requests
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import time

logger = logging.getLogger(__name__)

class FinnhubDataSource:
    """
    Free Finnhub API integration (60 requests/minute)
    Get API key from: https://finnhub.io/register
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get('FINNHUB_API_KEY')
        self.base_url = "https://finnhub.io/api/v1"
        self.session = requests.Session()
        self.last_request_time = 0
        self.min_request_interval = 1.0  # Rate limit: 60/min = 1 per second
        
        if not self.api_key:
            logger.warning("FINNHUB_API_KEY not set - Finnhub data source disabled")
            self.enabled = False
        else:
            self.enabled = True
            logger.info("✅ Finnhub data source initialized")
    
    def _rate_limit(self):
        """Respect rate limit of 60 calls/minute"""
        if not self.enabled:
            return
            
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_request_interval:
            time.sleep(self.min_request_interval - elapsed)
        self.last_request_time = time.time()
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """Make API request with error handling"""
        if not self.enabled:
            return None
            
        self._rate_limit()
        
        try:
            url = f"{self.base_url}/{endpoint}"
            if params is None:
                params = {}
            params['token'] = self.api_key
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                logger.warning("Finnhub rate limit exceeded")
            else:
                logger.error(f"Finnhub HTTP error: {e}")
            return None
        except Exception as e:
            logger.error(f"Finnhub request failed: {e}")
            return None
    
    def get_quote(self, symbol: str) -> Optional[Dict[str, float]]:
        """
        Get real-time quote (no fallbacks, real data only)
        Returns: {current_price, high, low, open, previous_close, change_pct, timestamp}
        """
        data = self._make_request("quote", {"symbol": symbol})
        
        if not data or 'c' not in data:
            return None
        
        # Return only real data - no fabrication
        return {
            'current_price': float(data.get('c', 0)),  # Current price
            'high': float(data.get('h', 0)),           # High of day
            'low': float(data.get('l', 0)),            # Low of day
            'open': float(data.get('o', 0)),           # Open price
            'previous_close': float(data.get('pc', 0)), # Previous close
            'change_pct': float(data.get('dp', 0)),    # Percent change
            'timestamp': int(data.get('t', 0)),        # Unix timestamp
            'source': 'finnhub'
        }
    
    def get_company_news(self, symbol: str, days_back: int = 7) -> List[Dict[str, Any]]:
        """
        Get real company news (not fabricated)
        Returns list of news articles with headline, summary, source, sentiment
        """
        to_date = datetime.now().strftime('%Y-%m-%d')
        from_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        
        data = self._make_request("company-news", {
            "symbol": symbol,
            "from": from_date,
            "to": to_date
        })
        
        if not data or not isinstance(data, list):
            return []
        
        # Return real news data only
        news_items = []
        for item in data[:50]:  # Limit to 50 most recent
            if item.get('headline') and item.get('datetime'):
                news_items.append({
                    'headline': item.get('headline', ''),
                    'summary': item.get('summary', ''),
                    'source': item.get('source', ''),
                    'url': item.get('url', ''),
                    'datetime': item.get('datetime', 0),
                    'category': item.get('category', ''),
                    'sentiment': None  # Will be analyzed separately
                })
        
        return news_items
    
    def get_earnings_calendar(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get earnings calendar data
        Returns: {earnings_date, estimate, actual, surprise}
        """
        data = self._make_request("calendar/earnings", {"symbol": symbol})
        
        if not data or 'earningsCalendar' not in data:
            return None
        
        earnings = data.get('earningsCalendar', [])
        if not earnings:
            return None
        
        # Get most recent/upcoming earnings
        latest = earnings[0]
        
        return {
            'date': latest.get('date'),
            'eps_estimate': latest.get('epsEstimate'),
            'eps_actual': latest.get('epsActual'),
            'revenue_estimate': latest.get('revenueEstimate'),
            'revenue_actual': latest.get('revenueActual'),
            'surprise_percent': latest.get('surprisePercent'),
            'source': 'finnhub'
        }
    
    def get_recommendation_trends(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get analyst recommendation trends
        Returns real analyst data (buy/hold/sell counts)
        """
        data = self._make_request("stock/recommendation", {"symbol": symbol})
        
        if not data or not isinstance(data, list) or len(data) == 0:
            return None
        
        # Get most recent recommendations
        latest = data[0]
        
        return {
            'period': latest.get('period'),
            'strong_buy': int(latest.get('strongBuy', 0)),
            'buy': int(latest.get('buy', 0)),
            'hold': int(latest.get('hold', 0)),
            'sell': int(latest.get('sell', 0)),
            'strong_sell': int(latest.get('strongSell', 0)),
            'source': 'finnhub'
        }
    
    def calculate_recommendation_score(self, recommendations: Dict[str, Any]) -> float:
        """
        Calculate unbiased recommendation score from analyst data
        Returns: -1.0 (bearish) to +1.0 (bullish), 0 = neutral
        """
        if not recommendations:
            return 0.0
        
        # Weight recommendations by strength
        strong_buy = recommendations.get('strong_buy', 0) * 2
        buy = recommendations.get('buy', 0) * 1
        hold = recommendations.get('hold', 0) * 0
        sell = recommendations.get('sell', 0) * -1
        strong_sell = recommendations.get('strong_sell', 0) * -2
        
        total_recommendations = (recommendations.get('strong_buy', 0) + 
                                recommendations.get('buy', 0) +
                                recommendations.get('hold', 0) +
                                recommendations.get('sell', 0) +
                                recommendations.get('strong_sell', 0))
        
        if total_recommendations == 0:
            return 0.0
        
        # Normalize to -1 to +1 range
        weighted_sum = strong_buy + buy + hold + sell + strong_sell
        max_possible = total_recommendations * 2  # All strong buy
        
        return weighted_sum / max_possible if max_possible > 0 else 0.0
    
    def get_market_sentiment(self, symbol: str) -> Dict[str, Any]:
        """
        Aggregate sentiment from news and recommendations
        No fabricated data - returns None if data unavailable
        """
        news = self.get_company_news(symbol, days_back=7)
        recommendations = self.get_recommendation_trends(symbol)
        
        return {
            'news_count': len(news),
            'recommendation_score': self.calculate_recommendation_score(recommendations),
            'recommendations': recommendations,
            'timestamp': datetime.now().isoformat(),
            'source': 'finnhub'
        }


# Export
__all__ = ['FinnhubDataSource']
