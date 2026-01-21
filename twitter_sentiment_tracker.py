"""
Twitter/X Sentiment Tracker for AMD
Uses tweepy (Twitter API v2) to analyze:
1. $AMD mentions (Cashtag)
2. Sentiment analysis
3. Engagement metrics (likes, retweets)
4. Influencer mentions
"""

import tweepy
import re
from datetime import datetime, timedelta
from typing import Dict, List
import os
from dotenv import load_dotenv

load_dotenv()

class TwitterSentimentTracker:
    """Track stock sentiment on Twitter/X for any symbol."""
    
    def __init__(self):
        """Initialize Twitter API connection."""
        # Load credentials from .env
        self.bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        
        # Initialize Twitter client (API v2)
        try:
            if self.bearer_token:
                self.client = tweepy.Client(bearer_token=self.bearer_token)
                print("✅ Twitter API connected")
            else:
                print("⚠️ Twitter API not configured")
                self.client = None
        except Exception as e:
            print(f"❌ Twitter API connection failed: {e}")
            self.client = None
    
    def analyze_sentiment(self, text: str) -> float:
        """
        Simple sentiment analysis (-1 to +1).
        Same logic as Reddit tracker.
        """
        # Bullish keywords
        bullish_words = [
            'moon', 'rocket', 'bullish', 'calls', 'buy', 'long', 'bull',
            'gains', 'profit', 'up', 'surge', 'rally', 'breakout', 'strong',
            'beat', 'upgrade', 'growth', 'soar', 'climbs', 'jumped', '🚀', '📈', '💚'
        ]
        
        # Bearish keywords
        bearish_words = [
            'crash', 'bearish', 'puts', 'sell', 'short', 'bear', 'losses',
            'down', 'drop', 'fall', 'plunge', 'weak', 'miss', 'downgrade',
            'decline', 'tumbles', 'sinks', 'slumps', '📉', '💔', '🔴'
        ]
        
        text_lower = text.lower()
        
        # Count occurrences
        bullish_count = sum(1 for word in bullish_words if word in text_lower)
        bearish_count = sum(1 for word in bearish_words if word in text_lower)
        
        # Calculate sentiment
        total = bullish_count + bearish_count
        if total == 0:
            return 0.0
        
        sentiment = (bullish_count - bearish_count) / total
        return round(sentiment, 3)
    
    def get_stock_tweets(self, symbol: str, limit: int = 100) -> Dict:
        """
        Get recent tweets mentioning a stock symbol.
        
        Args:
            symbol: Stock symbol to search for (AMD, AVGO, ORCL, etc.)
            limit: Maximum tweets to analyze
            
        Returns:
            Dict with sentiment and engagement metrics
        """
        if not self.client:
            return {'error': 'Twitter API not connected'}
        
        try:
            # Search for stock mentions (free tier compatible - no cashtag operator)
            # Cashtag ($SYMBOL) requires Twitter API premium tier
            # Search for symbol in English tweets, excluding retweets
            query = f'{symbol} lang:en -is:retweet'
            
            # Get tweets from last 24 hours
            # Twitter requires end_time to be at least 10 seconds before current time
            end_time = datetime.utcnow() - timedelta(seconds=30)  # 30 seconds buffer
            start_time = end_time - timedelta(hours=24)
            
            tweets = self.client.search_recent_tweets(
                query=query,
                max_results=min(limit, 100),  # Twitter free tier limit
                start_time=start_time,
                end_time=end_time,
                tweet_fields=['created_at', 'public_metrics', 'author_id']
            )
            
            if not tweets.data:
                return {
                    'tweets': 0,
                    'sentiment': 0.0,
                    'engagement': 0
                }
            
            total_score = 0
            total_engagement = 0
            tweet_list = []
            
            for tweet in tweets.data:
                text = tweet.text
                sentiment = self.analyze_sentiment(text)
                
                # Engagement = likes + retweets + replies
                metrics = tweet.public_metrics
                engagement = (
                    metrics['like_count'] +
                    metrics['retweet_count'] * 2 +  # Retweets weighted more
                    metrics['reply_count']
                )
                
                # Weight sentiment by engagement
                weighted_sentiment = sentiment * min(engagement, 100) / 100
                
                tweet_list.append({
                    'text': text[:100],
                    'sentiment': sentiment,
                    'likes': metrics['like_count'],
                    'retweets': metrics['retweet_count'],
                    'engagement': engagement
                })
                
                total_score += weighted_sentiment
                total_engagement += engagement
            
            # Average sentiment
            avg_sentiment = total_score / len(tweets.data) if len(tweets.data) > 0 else 0.0
            
            return {
                'tweets': len(tweets.data),
                'sentiment': round(avg_sentiment, 3),
                'total_engagement': total_engagement,
                'avg_engagement': round(total_engagement / len(tweets.data), 1),
                'top_tweets': sorted(tweet_list, key=lambda x: x['engagement'], reverse=True)[:5]
            }
            
        except Exception as e:
            print(f"⚠️ Twitter API error: {e}")
            return {'error': str(e)}
    
    def get_twitter_sentiment_score(self, symbol: str = 'AMD') -> Dict:
        """
        Get overall Twitter sentiment score (0-10) for system integration.
        
        Args:
            symbol: Stock symbol to search for (AMD, AVGO, ORCL, etc.)
        """
        print(f"\n🐦 Analyzing Twitter Sentiment for {symbol}...")
        
        result = self.get_stock_tweets(symbol, limit=100)
        
        if 'error' in result:
            print(f"   ⚠️ Twitter API error: {result['error']}")
            return {
                'score': 5,
                'sentiment': 'NEUTRAL',
                'tweets': 0,
                'impact': 'NONE'
            }
        
        tweets = result.get('tweets', 0)
        raw_sentiment = result.get('sentiment', 0.0)
        engagement = result.get('total_engagement', 0)
        
        if tweets == 0:
            return {
                'score': 5,
                'sentiment': 'NEUTRAL',
                'tweets': 0,
                'impact': 'NONE'
            }
        
        # Convert sentiment (-1 to +1) → score (0 to 10)
        score = (raw_sentiment + 1) * 5
        
        # Determine impact based on volume and engagement
        if tweets > 50 and engagement > 1000:
            impact = 'HIGH'
        elif tweets > 20 and engagement > 300:
            impact = 'MEDIUM'
        else:
            impact = 'LOW'
        
        # Sentiment label
        if score >= 7:
            sentiment_label = 'BULLISH'
        elif score >= 4:
            sentiment_label = 'NEUTRAL'
        else:
            sentiment_label = 'BEARISH'
        
        print(f"   🐦 Tweets Found: {tweets}")
        print(f"   📊 Twitter Score: {score:.1f}/10 ({sentiment_label})")
        print(f"   💥 Total Engagement: {engagement:,}")
        print(f"   💡 Impact Level: {impact}")
        
        return {
            'score': round(score, 2),
            'raw_sentiment': round(raw_sentiment, 3),
            'sentiment': sentiment_label,
            'tweets': tweets,
            'engagement': engagement,
            'impact': impact
        }

if __name__ == "__main__":
    # Test Twitter sentiment tracker
    print("🐦 TWITTER SENTIMENT TRACKER TEST\n")
    
    tracker = TwitterSentimentTracker()
    
    if tracker.client:
        result = tracker.get_twitter_sentiment_score()
        
        print(f"\n{'='*60}")
        print(f"🎯 TWITTER SENTIMENT ANALYSIS COMPLETE")
        print(f"{'='*60}")
        print(f"Score: {result['score']}/10")
        print(f"Sentiment: {result['sentiment']}")
        print(f"Tweets: {result['tweets']}")
        print(f"Impact: {result['impact']}")
    else:
        print("\n❌ Twitter API not configured")
        print("\nAdd to your .env file:")
        print("TWITTER_BEARER_TOKEN=your_bearer_token")
        print("\nGet your bearer token from: https://developer.twitter.com/")
