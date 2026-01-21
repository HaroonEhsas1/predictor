"""
PREMARKET NEWS CATALYST ANALYZER
Fetches and analyzes overnight news to detect catalysts

Features:
- Fetch news from multiple sources
- Rate news quality (strong/weak catalyst)
- Detect catalyst type (earnings, guidance, deal, etc)
- Stock-specific keyword matching
"""

import requests
import os
from datetime import datetime, timedelta
import pytz
from typing import Dict, Any, List
from premarket_config import get_stock_config

class PremarketNewsAnalyzer:
    """
    Analyzes overnight news for premarket catalysts
    """
    
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.config = get_stock_config(symbol)
        
        # API keys (from environment or config)
        self.finnhub_key = os.getenv('FINNHUB_API_KEY', 'your_key_here')
        self.alpha_vantage_key = os.getenv('ALPHA_VANTAGE_API_KEY', 'your_key_here')
    
    def fetch_overnight_news(self) -> List[Dict[str, Any]]:
        """
        Fetch news from last 12 hours
        """
        
        print(f"\n📰 Fetching Overnight News for {self.symbol}...")
        
        news_items = []
        
        # Try Finnhub
        try:
            news_items.extend(self._fetch_finnhub_news())
        except Exception as e:
            print(f"   ⚠️ Finnhub error: {e}")
        
        # Try Alpha Vantage
        try:
            news_items.extend(self._fetch_alpha_vantage_news())
        except Exception as e:
            print(f"   ⚠️ Alpha Vantage error: {e}")
        
        # Filter for recency (last 12 hours)
        et_tz = pytz.timezone('US/Eastern')
        now_et = datetime.now(et_tz)
        cutoff = now_et - timedelta(hours=12)
        
        recent_news = []
        for item in news_items:
            if item.get('datetime'):
                if item['datetime'] > cutoff:
                    recent_news.append(item)
        
        print(f"   Found {len(recent_news)} recent news items")
        
        return recent_news
    
    def _fetch_finnhub_news(self) -> List[Dict[str, Any]]:
        """Fetch from Finnhub API"""
        
        if self.finnhub_key == 'your_key_here':
            return []
        
        url = f"https://finnhub.io/api/v1/company-news"
        params = {
            'symbol': self.symbol,
            'from': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
            'to': datetime.now().strftime('%Y-%m-%d'),
            'token': self.finnhub_key
        }
        
        response = requests.get(url, params=params, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            news_items = []
            
            for item in data[:20]:  # Limit to 20 most recent
                news_items.append({
                    'source': 'Finnhub',
                    'headline': item.get('headline', ''),
                    'summary': item.get('summary', ''),
                    'datetime': datetime.fromtimestamp(item.get('datetime', 0), pytz.timezone('US/Eastern')),
                    'url': item.get('url', '')
                })
            
            return news_items
        
        return []
    
    def _fetch_alpha_vantage_news(self) -> List[Dict[str, Any]]:
        """Fetch from Alpha Vantage API"""
        
        if self.alpha_vantage_key == 'your_key_here':
            return []
        
        url = f"https://www.alphavantage.co/query"
        params = {
            'function': 'NEWS_SENTIMENT',
            'tickers': self.symbol,
            'apikey': self.alpha_vantage_key,
            'limit': 50
        }
        
        response = requests.get(url, params=params, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            news_items = []
            
            if 'feed' in data:
                for item in data['feed'][:20]:
                    # Parse time
                    time_str = item.get('time_published', '')
                    try:
                        dt = datetime.strptime(time_str, '%Y%m%dT%H%M%S')
                        dt = pytz.timezone('US/Eastern').localize(dt)
                    except:
                        dt = datetime.now(pytz.timezone('US/Eastern'))
                    
                    news_items.append({
                        'source': 'AlphaVantage',
                        'headline': item.get('title', ''),
                        'summary': item.get('summary', ''),
                        'datetime': dt,
                        'sentiment': item.get('overall_sentiment_label', 'Neutral')
                    })
            
            return news_items
        
        return []
    
    def analyze_catalyst_quality(self, news_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze news quality and detect catalysts
        
        Returns:
        - has_catalyst: bool
        - catalyst_type: earnings/guidance/deal/product/regulation/none
        - catalyst_strength: strong/medium/weak
        - sentiment: bullish/bearish/neutral
        - confidence: 0-100%
        """
        
        print(f"\n🔍 Analyzing Catalyst Quality...")
        
        if not news_items:
            return {
                'has_catalyst': False,
                'catalyst_type': 'none',
                'catalyst_strength': 'none',
                'sentiment': 'neutral',
                'confidence': 0,
                'news_count': 0
            }
        
        # Get stock-specific catalysts and keywords
        primary_catalysts = self.config.get('primary_catalysts', [])
        positive_keywords = self.config.get('positive_keywords', [])
        negative_keywords = self.config.get('negative_keywords', [])
        
        # Analyze each news item
        catalyst_scores = {
            'earnings': 0,
            'guidance': 0,
            'deal': 0,
            'product': 0,
            'regulation': 0,
            'general': 0
        }
        
        sentiment_score = 0
        sentiment_count = 0
        
        for item in news_items:
            text = (item['headline'] + ' ' + item.get('summary', '')).lower()
            
            # Detect catalyst type
            if any(word in text for word in ['earnings', 'eps', 'revenue', 'quarter', 'q1', 'q2', 'q3', 'q4']):
                catalyst_scores['earnings'] += 2
            
            if any(word in text for word in ['guidance', 'forecast', 'outlook', 'expects', 'projects']):
                catalyst_scores['guidance'] += 2
            
            if any(word in text for word in ['acquisition', 'merger', 'deal', 'buyout', 'partnership']):
                catalyst_scores['deal'] += 2
            
            if any(word in text for word in ['product', 'launch', 'release', 'announce', 'unveil']):
                catalyst_scores['product'] += 1
            
            if any(word in text for word in ['regulation', 'lawsuit', 'fine', 'investigation', 'antitrust']):
                catalyst_scores['regulation'] += 1
            
            # Check stock-specific catalysts
            for catalyst in primary_catalysts:
                if catalyst.lower() in text:
                    catalyst_scores['general'] += 1
            
            # Analyze sentiment
            positive_count = sum(1 for word in positive_keywords if word.lower() in text)
            negative_count = sum(1 for word in negative_keywords if word.lower() in text)
            
            if positive_count > negative_count:
                sentiment_score += (positive_count - negative_count)
                sentiment_count += 1
            elif negative_count > positive_count:
                sentiment_score -= (negative_count - positive_count)
                sentiment_count += 1
        
        # Determine primary catalyst
        max_catalyst = max(catalyst_scores.items(), key=lambda x: x[1])
        catalyst_type = max_catalyst[0] if max_catalyst[1] > 0 else 'none'
        catalyst_value = max_catalyst[1]
        
        # Rate catalyst strength
        if catalyst_value >= 4:
            catalyst_strength = 'strong'
            confidence = min(90, 60 + catalyst_value * 5)
        elif catalyst_value >= 2:
            catalyst_strength = 'medium'
            confidence = min(75, 50 + catalyst_value * 5)
        elif catalyst_value >= 1:
            catalyst_strength = 'weak'
            confidence = min(60, 40 + catalyst_value * 5)
        else:
            catalyst_strength = 'none'
            confidence = 0
        
        # Determine sentiment
        if sentiment_count > 0:
            avg_sentiment = sentiment_score / max(sentiment_count, 1)
            if avg_sentiment > 0.5:
                sentiment = 'bullish'
            elif avg_sentiment < -0.5:
                sentiment = 'bearish'
            else:
                sentiment = 'neutral'
        else:
            sentiment = 'neutral'
        
        result = {
            'has_catalyst': catalyst_type != 'none',
            'catalyst_type': catalyst_type,
            'catalyst_strength': catalyst_strength,
            'sentiment': sentiment,
            'confidence': confidence,
            'news_count': len(news_items),
            'catalyst_scores': catalyst_scores
        }
        
        print(f"   Catalyst: {catalyst_type.upper()} ({catalyst_strength})")
        print(f"   Sentiment: {sentiment.upper()}")
        print(f"   Confidence: {confidence}%")
        print(f"   News Items: {len(news_items)}")
        
        return result
    
    def get_news_boost(self, catalyst_analysis: Dict[str, Any], 
                       gap_direction: str) -> float:
        """
        Calculate confidence boost from news
        
        Args:
            catalyst_analysis: Result from analyze_catalyst_quality
            gap_direction: 'up' or 'down'
        
        Returns:
            Confidence adjustment (-20 to +20%)
        """
        
        if not catalyst_analysis['has_catalyst']:
            return -12  # No catalyst = penalty
        
        strength = catalyst_analysis['catalyst_strength']
        sentiment = catalyst_analysis['sentiment']
        
        # Base boost by strength
        if strength == 'strong':
            boost = 15
        elif strength == 'medium':
            boost = 10
        elif strength == 'weak':
            boost = 5
        else:
            boost = 0
        
        # Adjust for sentiment alignment
        if gap_direction == 'up' and sentiment == 'bullish':
            boost += 5  # Aligned = extra boost
        elif gap_direction == 'up' and sentiment == 'bearish':
            boost -= 15  # Conflict = penalty
        elif gap_direction == 'down' and sentiment == 'bearish':
            boost += 5  # Aligned
        elif gap_direction == 'down' and sentiment == 'bullish':
            boost -= 15  # Conflict
        
        return max(-20, min(20, boost))
    
    def analyze_overnight_catalyst(self) -> Dict[str, Any]:
        """
        Complete overnight catalyst analysis
        """
        
        # Fetch news
        news_items = self.fetch_overnight_news()
        
        # Analyze catalyst
        catalyst = self.analyze_catalyst_quality(news_items)
        
        # Return complete analysis
        return {
            'has_news': len(news_items) > 0,
            'news_items': news_items[:5],  # Top 5 for display
            'catalyst': catalyst
        }


if __name__ == "__main__":
    # Test
    print("\n" + "="*80)
    print("PREMARKET NEWS ANALYZER - TEST")
    print("="*80)
    
    for symbol in ['NVDA', 'META']:
        analyzer = PremarketNewsAnalyzer(symbol)
        result = analyzer.analyze_overnight_catalyst()
        
        print(f"\n{symbol}:")
        print(f"   News Items: {len(result['news_items'])}")
        print(f"   Has Catalyst: {result['catalyst']['has_catalyst']}")
        if result['catalyst']['has_catalyst']:
            print(f"   Type: {result['catalyst']['catalyst_type']}")
            print(f"   Strength: {result['catalyst']['catalyst_strength']}")
            print(f"   Sentiment: {result['catalyst']['sentiment']}")
        
        print("\n")
