"""
Reddit Sentiment Tracker - Real WallStreetBets Data
Uses PRAW (Python Reddit API Wrapper) to analyze:
1. r/wallstreetbets mentions of AMD
2. r/stocks discussions
3. r/investing sentiment
4. Upvote ratio (positive vs negative sentiment)
"""

import praw
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import os
from dotenv import load_dotenv

load_dotenv()

class RedditSentimentTracker:
    """Track stock sentiment on Reddit (WallStreetBets, stocks, investing) for any symbol."""
    
    def __init__(self):
        """Initialize Reddit API connection."""
        # Load credentials from .env
        self.client_id = os.getenv('REDDIT_CLIENT_ID')
        self.client_secret = os.getenv('REDDIT_CLIENT_SECRET')
        self.username = os.getenv('REDDIT_USERNAME')
        self.password = os.getenv('REDDIT_PASSWORD')
        self.user_agent = f"AMD_Sentiment_Tracker by /u/{self.username}"
        
        # Initialize Reddit instance
        try:
            self.reddit = praw.Reddit(
                client_id=self.client_id,
                client_secret=self.client_secret,
                username=self.username,
                password=self.password,
                user_agent=self.user_agent
            )
            print("✅ Reddit API connected")
        except Exception as e:
            print(f"❌ Reddit API connection failed: {e}")
            self.reddit = None
        
        # Subreddits to monitor
        self.subreddits = ['wallstreetbets', 'stocks', 'investing', 'AMD_Stock']
    
    def analyze_sentiment(self, text: str) -> float:
        """
        Simple sentiment analysis (-1 to +1).
        Positive words → positive score
        Negative words → negative score
        """
        # Bullish keywords
        bullish_words = [
            'moon', 'rocket', 'bullish', 'calls', 'buy', 'long', 'bull',
            'gains', 'profit', 'up', 'surge', 'rally', 'breakout', 'strong',
            'beat', 'upgrade', 'growth', 'soar', 'climbs', 'jumped'
        ]
        
        # Bearish keywords
        bearish_words = [
            'crash', 'bearish', 'puts', 'sell', 'short', 'bear', 'losses',
            'down', 'drop', 'fall', 'plunge', 'weak', 'miss', 'downgrade',
            'decline', 'tumbles', 'sinks', 'slumps'
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
    
    def get_stock_mentions(self, symbol: str, subreddit_name: str, limit: int = 100) -> Dict:
        """
        Get stock mentions from specific subreddit.
        
        Args:
            symbol: Stock symbol to search for (AMD, AVGO, ORCL, etc.)
            subreddit_name: Name of subreddit to search
            limit: Maximum posts to analyze
            
        Returns:
            Dict with sentiment score and engagement metrics
        """
        if not self.reddit:
            return {'error': 'Reddit API not connected'}
        
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            
            # Search for stock mentions in last 24 hours
            # Search for $SYMBOL or SYMBOL (e.g., $AMD or AMD)
            search_query = f"({symbol} OR ${symbol})"
            
            mentions = []
            total_score = 0
            total_upvotes = 0
            total_comments = 0
            
            # Search recent posts for this specific stock
            for submission in subreddit.search(search_query, time_filter='day', limit=limit):
                # Calculate age in hours
                created_utc = submission.created_utc
                age_hours = (datetime.now().timestamp() - created_utc) / 3600
                
                # Only posts from last 24 hours
                if age_hours > 24:
                    continue
                
                # Analyze title + selftext
                text = f"{submission.title} {submission.selftext}"
                sentiment = self.analyze_sentiment(text)
                
                # Weight by engagement (upvotes + comments)
                engagement = submission.score + submission.num_comments
                weighted_sentiment = sentiment * min(engagement, 1000) / 1000
                
                mentions.append({
                    'title': submission.title[:100],
                    'score': submission.score,
                    'comments': submission.num_comments,
                    'sentiment': sentiment,
                    'url': submission.url
                })
                
                total_score += weighted_sentiment
                total_upvotes += submission.score
                total_comments += submission.num_comments
            
            if len(mentions) == 0:
                return {
                    'mentions': 0,
                    'sentiment': 0.0,
                    'engagement': 0
                }
            
            # Average sentiment (weighted by engagement)
            avg_sentiment = total_score / len(mentions)
            
            return {
                'mentions': len(mentions),
                'sentiment': round(avg_sentiment, 3),
                'total_upvotes': total_upvotes,
                'total_comments': total_comments,
                'engagement': total_upvotes + total_comments,
                'top_posts': mentions[:5]  # Top 5 posts
            }
            
        except Exception as e:
            print(f"⚠️ Error fetching from r/{subreddit_name}: {e}")
            return {'error': str(e)}
    
    def get_wallstreetbets_sentiment(self, symbol: str = 'AMD') -> Dict:
        """
        Get stock sentiment from r/wallstreetbets specifically.
        WSB has most trading impact.
        
        Args:
            symbol: Stock symbol to search for (AMD, AVGO, ORCL, etc.)
        """
        return self.get_stock_mentions(symbol, 'wallstreetbets', limit=200)
    
    def get_overall_reddit_sentiment(self, symbol: str = 'AMD') -> Dict:
        """
        Aggregate sentiment across all monitored subreddits.
        Returns 0-10 score for system integration.
        
        Args:
            symbol: Stock symbol to search for (AMD, AVGO, ORCL, etc.)
        """
        print(f"\n🔴 Analyzing Reddit Sentiment for {symbol}...")
        
        all_sentiments = []
        total_mentions = 0
        subreddit_results = {}
        
        for sub in self.subreddits:
            result = self.get_stock_mentions(symbol, sub, limit=100)
            
            if 'error' in result:
                continue
            
            mentions = result.get('mentions', 0)
            sentiment = result.get('sentiment', 0.0)
            engagement = result.get('engagement', 0)
            
            if mentions > 0:
                # Weight by mentions and engagement
                weight = min(mentions * engagement, 10000) / 10000
                weighted_sentiment = sentiment * weight
                all_sentiments.append(weighted_sentiment)
                total_mentions += mentions
                
                subreddit_results[sub] = {
                    'mentions': mentions,
                    'sentiment': sentiment,
                    'engagement': engagement
                }
                
                print(f"   r/{sub}: {mentions} mentions, sentiment: {sentiment:+.2f}")
        
        if len(all_sentiments) == 0:
            return {
                'score': 5,
                'sentiment': 'NEUTRAL',
                'mentions': 0,
                'impact': 'LOW'
            }
        
        # Average sentiment (-1 to +1)
        avg_sentiment = sum(all_sentiments) / len(all_sentiments)
        
        # Convert to 0-10 score
        # -1 → 0 (very bearish)
        #  0 → 5 (neutral)
        # +1 → 10 (very bullish)
        score = (avg_sentiment + 1) * 5
        
        # Determine impact level
        if total_mentions > 50:
            impact = 'HIGH'
        elif total_mentions > 20:
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
        
        print(f"   📊 Overall Reddit Score: {score:.1f}/10 ({sentiment_label})")
        print(f"   📈 Total Mentions: {total_mentions}")
        print(f"   💥 Impact Level: {impact}")
        
        return {
            'score': round(score, 2),
            'raw_sentiment': round(avg_sentiment, 3),
            'sentiment': sentiment_label,
            'mentions': total_mentions,
            'impact': impact,
            'subreddit_breakdown': subreddit_results
        }

if __name__ == "__main__":
    # Test Reddit sentiment tracker
    print("🔴 REDDIT SENTIMENT TRACKER TEST\n")
    
    tracker = RedditSentimentTracker()
    
    if tracker.reddit:
        result = tracker.get_overall_reddit_sentiment()
        
        print(f"\n{'='*60}")
        print(f"🎯 REDDIT SENTIMENT ANALYSIS COMPLETE")
        print(f"{'='*60}")
        print(f"Score: {result['score']}/10")
        print(f"Sentiment: {result['sentiment']}")
        print(f"Total Mentions: {result['mentions']}")
        print(f"Impact: {result['impact']}")
    else:
        print("\n❌ Reddit API not configured")
        print("\nAdd to your .env file:")
        print("REDDIT_CLIENT_ID=your_client_id")
        print("REDDIT_CLIENT_SECRET=your_client_secret")
        print("REDDIT_USERNAME=your_username")
        print("REDDIT_PASSWORD=your_password")
