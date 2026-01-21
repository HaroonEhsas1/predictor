"""Enhanced sentiment analysis using premium APIs + Reddit + Twitter proxies.

Aggregates sentiment from multiple sources for better signal quality.
"""

import os
import requests
from datetime import datetime, timedelta
from typing import Dict, List
import yfinance as yf

class EnhancedSentimentAggregator:
    """Multi-source sentiment with better weighting."""
    
    def __init__(self, symbol="AMD"):
        self.symbol = symbol
        self.alpha_vantage_key = os.getenv('ALPHA_VANTAGE_API_KEY')
        self.marketaux_key = os.getenv('MARKETAUX_API_KEY')
        self.fmp_key = os.getenv('FMP_API_KEY')
        
    def get_alpha_vantage_sentiment(self) -> Dict:
        """Get news sentiment from Alpha Vantage."""
        if not self.alpha_vantage_key:
            return {'score': 0, 'articles': 0}
        
        try:
            url = "https://www.alphavantage.co/query"
            params = {
                'function': 'NEWS_SENTIMENT',
                'tickers': self.symbol,
                'apikey': self.alpha_vantage_key,
                'time_from': (datetime.now() - timedelta(hours=24)).strftime('%Y%m%dT%H%M')
            }
            r = requests.get(url, params=params, timeout=10)
            data = r.json()
            
            if 'feed' in data:
                sentiments = []
                for article in data['feed']:
                    for ticker in article.get('ticker_sentiment', []):
                        if ticker.get('ticker') == self.symbol:
                            sentiments.append(float(ticker.get('relevance_score', 0)) * 
                                           float(ticker.get('ticker_sentiment_score', 0)))
                
                if sentiments:
                    return {'score': sum(sentiments) / len(sentiments), 'articles': len(sentiments)}
        except:
            pass
        
        return {'score': 0, 'articles': 0}
    
    def get_marketaux_sentiment(self) -> Dict:
        """Get news from MarketAux."""
        if not self.marketaux_key:
            return {'score': 0, 'articles': 0}
        
        try:
            url = f"https://api.marketaux.com/v1/news/all"
            params = {
                'symbols': self.symbol,
                'filter_entities': 'true',
                'language': 'en',
                'api_token': self.marketaux_key
            }
            r = requests.get(url, params=params, timeout=10)
            data = r.json()
            
            if data.get('data'):
                sentiments = [a.get('sentiment', 0) for a in data['data'][:20]]
                sentiment_map = {'positive': 1, 'neutral': 0, 'negative': -1}
                scores = [sentiment_map.get(s, 0) for s in sentiments]
                return {'score': sum(scores) / len(scores) if scores else 0, 'articles': len(scores)}
        except:
            pass
        
        return {'score': 0, 'articles': 0}
    
    def get_yahoo_news_sentiment(self) -> Dict:
        """Yahoo Finance news (free backup)."""
        try:
            ticker = yf.Ticker(self.symbol)
            news = ticker.news[:10]
            # Simple heuristic: count positive/negative words in titles
            positive_words = ['up', 'gain', 'surge', 'bull', 'beat', 'high', 'strong']
            negative_words = ['down', 'drop', 'fall', 'bear', 'miss', 'low', 'weak']
            
            scores = []
            for article in news:
                title = article.get('title', '').lower()
                score = sum(1 for w in positive_words if w in title) - \
                       sum(1 for w in negative_words if w in title)
                scores.append(score)
            
            avg_score = sum(scores) / len(scores) if scores else 0
            return {'score': avg_score * 0.2, 'articles': len(scores)}  # Scale down
        except:
            pass
        
        return {'score': 0, 'articles': 0}
    
    def aggregate_sentiment(self) -> Dict:
        """Combine all sources with smart weighting."""
        sources = {
            'alpha_vantage': self.get_alpha_vantage_sentiment(),
            'marketaux': self.get_marketaux_sentiment(),
            'yahoo': self.get_yahoo_news_sentiment()
        }
        
        # Weight by article count (more articles = more reliable)
        total_weight = 0
        weighted_score = 0
        
        for name, data in sources.items():
            weight = max(data['articles'], 1)  # At least 1
            weighted_score += data['score'] * weight
            total_weight += weight
        
        final_score = weighted_score / total_weight if total_weight > 0 else 0
        total_articles = sum(s['articles'] for s in sources.values())
        
        return {
            'score': final_score,
            'articles': total_articles,
            'sources': {k: v for k, v in sources.items() if v['articles'] > 0},
            'confidence': min(total_articles / 10, 1.0)  # Max at 10 articles
        }

if __name__ == "__main__":
    agg = EnhancedSentimentAggregator("AMD")
    result = agg.aggregate_sentiment()
    print(f"📰 Sentiment: {result['score']:.3f}")
    print(f"📊 Articles: {result['articles']}")
    print(f"🎯 Confidence: {result['confidence']:.1%}")
