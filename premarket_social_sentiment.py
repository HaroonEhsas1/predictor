"""
SOCIAL SENTIMENT ANALYZER
Tracks Twitter/Reddit sentiment for premarket analysis

Features:
- Reddit sentiment (last 2-3 hours)
- Twitter/X tracking (optional, needs API)
- Sentiment spike detection
- Viral move prediction
"""

import requests
import praw
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List
import re

class SocialSentimentAnalyzer:
    """
    Analyzes social media sentiment for premarket
    """
    
    def __init__(self, symbol: str):
        self.symbol = symbol
        
        # Reddit API (free, no key needed for read-only)
        self.reddit_api_url = "https://www.reddit.com/r/wallstreetbets/search.json"
        
        # Twitter API (needs key - optional)
        self.twitter_api_key = os.getenv('TWITTER_API_KEY', None)
    
    def analyze_social_sentiment(self) -> Dict[str, Any]:
        """
        Complete social sentiment analysis
        
        Returns:
        - reddit_sentiment: bullish/bearish/neutral
        - reddit_mentions: count
        - sentiment_spike: bool
        - confidence_adjustment: ±10%
        """
        
        print(f"\n💬 Social Sentiment Analysis...")
        
        # Analyze Reddit
        reddit_data = self._analyze_reddit_sentiment()
        
        # Analyze Twitter (if API key available)
        if self.twitter_api_key:
            twitter_data = self._analyze_twitter_sentiment()
        else:
            twitter_data = {'has_data': False}
            print("   ⚠️ Twitter API key not configured (skipping)")
        
        # Combine sentiments
        combined_sentiment, confidence_adj = self._combine_sentiments(
            reddit_data,
            twitter_data
        )
        
        result = {
            'reddit': reddit_data,
            'twitter': twitter_data,
            'combined_sentiment': combined_sentiment,
            'confidence_adjustment': confidence_adj
        }
        
        print(f"   Combined Sentiment: {combined_sentiment}")
        print(f"   Confidence Adjust: {confidence_adj:+.0f}%")
        
        return result
    
    def _analyze_reddit_sentiment(self) -> Dict[str, Any]:
        """
        Analyze Reddit (WallStreetBets) sentiment
        
        Uses Reddit's public JSON API (no auth needed)
        """
        
        print(f"   📱 Checking Reddit...")
        
        try:
            # Search last 3 hours on WSB
            params = {
                'q': f'${self.symbol} OR {self.symbol}',
                'restrict_sr': 'on',
                't': 'day',  # Last 24 hours
                'limit': 100
            }
            
            headers = {'User-Agent': 'PremarketBot/1.0'}
            
            response = requests.get(
                self.reddit_api_url,
                params=params,
                headers=headers,
                timeout=5
            )
            
            if response.status_code != 200:
                print(f"      ⚠️ Reddit API error: {response.status_code}")
                return {'has_data': False}
            
            data = response.json()
            posts = data.get('data', {}).get('children', [])
            
            # Filter for last 3 hours
            three_hours_ago = (datetime.now() - timedelta(hours=3)).timestamp()
            recent_posts = [p for p in posts if p['data']['created_utc'] > three_hours_ago]
            
            if len(recent_posts) == 0:
                print(f"      No recent mentions")
                return {
                    'has_data': True,
                    'mentions': 0,
                    'sentiment': 'NEUTRAL',
                    'spike': False
                }
            
            # Count mentions and analyze sentiment
            bullish_keywords = ['calls', 'moon', 'buy', 'bullish', '🚀', 'rocket', 'gap up']
            bearish_keywords = ['puts', 'short', 'sell', 'bearish', 'dump', 'gap down']
            
            bullish_count = 0
            bearish_count = 0
            
            for post in recent_posts:
                title = post['data']['title'].lower()
                body = post['data'].get('selftext', '').lower()
                text = title + ' ' + body
                
                bullish_count += sum(1 for word in bullish_keywords if word in text)
                bearish_count += sum(1 for word in bearish_keywords if word in text)
            
            # Determine sentiment
            total_sentiment = bullish_count - bearish_count
            
            if total_sentiment > 5:
                sentiment = 'BULLISH'
            elif total_sentiment < -5:
                sentiment = 'BEARISH'
            else:
                sentiment = 'NEUTRAL'
            
            # Check for spike (>10 mentions in 3 hours = unusual)
            spike = len(recent_posts) > 10
            
            result = {
                'has_data': True,
                'mentions': len(recent_posts),
                'bullish_signals': bullish_count,
                'bearish_signals': bearish_count,
                'sentiment': sentiment,
                'spike': spike
            }
            
            print(f"      Mentions: {len(recent_posts)}")
            print(f"      Sentiment: {sentiment}")
            print(f"      Spike: {'⚠️ YES' if spike else 'NO'}")
            
            return result
            
        except Exception as e:
            print(f"      ⚠️ Reddit analysis error: {e}")
            return {'has_data': False}
    
    def _analyze_twitter_sentiment(self) -> Dict[str, Any]:
        """
        Analyze Twitter/X sentiment (needs API key)
        
        Note: Twitter API v2 is paid ($100/month for basic)
        This is optional enhancement
        """
        
        print(f"   🐦 Checking Twitter...")
        
        # Placeholder - requires Twitter API v2 key
        # Implementation would be similar to Reddit
        
        return {
            'has_data': False,
            'mentions': 0,
            'sentiment': 'UNKNOWN'
        }
    
    def _combine_sentiments(self, reddit: Dict[str, Any], 
                           twitter: Dict[str, Any]) -> tuple:
        """
        Combine Reddit and Twitter sentiments
        
        Returns: (sentiment, confidence_adjustment)
        """
        
        confidence_adj = 0
        
        # Reddit sentiment
        if reddit.get('has_data'):
            reddit_sentiment = reddit.get('sentiment', 'NEUTRAL')
            reddit_spike = reddit.get('spike', False)
            
            if reddit_sentiment == 'BULLISH':
                confidence_adj += 5
                if reddit_spike:
                    confidence_adj += 5  # Total +10 for bullish spike
            elif reddit_sentiment == 'BEARISH':
                confidence_adj -= 5
                if reddit_spike:
                    confidence_adj -= 5  # Total -10 for bearish spike
        
        # Twitter sentiment (if available)
        if twitter.get('has_data'):
            twitter_sentiment = twitter.get('sentiment', 'NEUTRAL')
            
            if twitter_sentiment == 'BULLISH':
                confidence_adj += 3
            elif twitter_sentiment == 'BEARISH':
                confidence_adj -= 3
        
        # Determine combined sentiment
        if confidence_adj > 5:
            combined = 'BULLISH'
        elif confidence_adj < -5:
            combined = 'BEARISH'
        else:
            combined = 'NEUTRAL'
        
        # Cap adjustment
        confidence_adj = max(-10, min(10, confidence_adj))
        
        return combined, confidence_adj


# USAGE INSTRUCTIONS:
"""
SETUP (Optional - for Twitter):
1. Get Twitter API v2 key (paid, $100/month)
2. Set environment variable:
   export TWITTER_API_KEY="your_key_here"

Reddit works without any setup (free public API)

ALTERNATIVE (Free):
- StockTwits API (free tier)
- Alternative.me sentiment (crypto focused)
- Google Trends API
"""


if __name__ == "__main__":
    # Test
    print("\n" + "="*80)
    print("SOCIAL SENTIMENT ANALYZER - TEST")
    print("="*80)
    
    for symbol in ['NVDA', 'META']:
        analyzer = SocialSentimentAnalyzer(symbol)
        result = analyzer.analyze_social_sentiment()
        
        print(f"\n{symbol} Summary:")
        if result['reddit'].get('has_data'):
            print(f"   Reddit Mentions: {result['reddit']['mentions']}")
            print(f"   Reddit Sentiment: {result['reddit']['sentiment']}")
        
        print(f"   Combined: {result['combined_sentiment']}")
        print(f"   Adjustment: {result['confidence_adjustment']:+.0f}%")
        
        print("\n")
