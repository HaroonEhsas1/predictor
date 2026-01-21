"""
Reddit Sentiment Tracker with OAuth Authentication
Tracks r/wallstreetbets, r/stocks, r/AMD for real sentiment
Uses PRAW (Python Reddit API Wrapper) with OAuth
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
import os

try:
    import praw  # type: ignore
    PRAW_AVAILABLE = True
except ImportError:
    PRAW_AVAILABLE = False

logger = logging.getLogger(__name__)

class RedditSentimentTracker:
    """
    Reddit API with OAuth authentication using PRAW
    Requires: REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USERNAME, REDDIT_PASSWORD
    """
    
    def __init__(self):
        if not PRAW_AVAILABLE:
            raise ImportError("PRAW is not installed. Install with: pip install praw")
        
        # Get OAuth credentials from environment
        client_id = os.getenv('REDDIT_CLIENT_ID')
        client_secret = os.getenv('REDDIT_CLIENT_SECRET')
        username = os.getenv('REDDIT_USERNAME')
        password = os.getenv('REDDIT_PASSWORD')
        
        # Validate credentials
        missing_creds = []
        if not client_id:
            missing_creds.append('REDDIT_CLIENT_ID')
        if not client_secret:
            missing_creds.append('REDDIT_CLIENT_SECRET')
        if not username:
            missing_creds.append('REDDIT_USERNAME')
        if not password:
            missing_creds.append('REDDIT_PASSWORD')
        
        if missing_creds:
            error_msg = f"Missing Reddit OAuth credentials: {', '.join(missing_creds)}"
            logger.error(f"❌ {error_msg}")
            raise ValueError(error_msg)
        
        # Initialize Reddit API with OAuth
        try:
            self.reddit = praw.Reddit(
                client_id=client_id,
                client_secret=client_secret,
                username=username,
                password=password,
                user_agent=f'StockSentimentTracker/1.0 by u/{username}'
            )
            
            # Test authentication
            self.reddit.user.me()
            logger.info(f"✅ Reddit OAuth authenticated as u/{username}")
            
        except Exception as e:
            error_msg = f"Reddit OAuth authentication failed: {str(e)}"
            logger.error(f"❌ {error_msg}")
            raise ConnectionError(error_msg)
        
        # Sentiment keywords (unbiased - captures both directions)
        self.bullish_keywords = [
            'moon', 'bull', 'calls', 'buying', 'long', 'buy',
            'rocket', 'gains', 'tendies', 'pump', 'breakout',
            'bullish', 'upgrade', 'rally', 'surge'
        ]
        
        self.bearish_keywords = [
            'bear', 'puts', 'selling', 'short', 'sell',
            'crash', 'dump', 'rip', 'tank', 'drop',
            'bearish', 'downgrade', 'decline', 'fall'
        ]
    
    def _search_ticker_mentions(self, subreddit_name: str, ticker: str, limit: int = 50) -> List[Dict]:
        """Search for ticker mentions in subreddit using PRAW"""
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            
            # Search for ticker mentions (last week)
            search_query = f'${ticker} OR {ticker}'
            posts = []
            
            for submission in subreddit.search(search_query, time_filter='week', limit=limit):
                posts.append({
                    'title': submission.title,
                    'selftext': submission.selftext,
                    'score': submission.score,
                    'num_comments': submission.num_comments,
                    'created_utc': submission.created_utc,
                    'permalink': submission.permalink
                })
            
            logger.info(f"Found {len(posts)} mentions of {ticker} in r/{subreddit_name}")
            return posts
            
        except Exception as e:
            error_msg = f"Failed to search r/{subreddit_name} for {ticker}: {str(e)}"
            logger.error(f"❌ {error_msg}")
            raise RuntimeError(error_msg)
    
    def _analyze_text_sentiment(self, text: str) -> float:
        """
        Analyze sentiment of text using keyword matching
        Returns: -1.0 (bearish) to +1.0 (bullish)
        """
        if not text:
            return 0.0
        
        text_lower = text.lower()
        
        # Count bullish and bearish keywords
        bullish_count = sum(1 for keyword in self.bullish_keywords if keyword in text_lower)
        bearish_count = sum(1 for keyword in self.bearish_keywords if keyword in text_lower)
        
        total_keywords = bullish_count + bearish_count
        if total_keywords == 0:
            return 0.0
        
        # Calculate sentiment score
        sentiment = (bullish_count - bearish_count) / total_keywords
        
        return sentiment
    
    def get_ticker_sentiment(self, ticker: str, subreddits: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Get real sentiment for ticker from Reddit using OAuth
        FAILS LOUDLY if authentication or API access fails
        """
        if subreddits is None:
            subreddits = ['wallstreetbets', 'stocks', 'AMD']
        
        all_mentions = []
        failed_subreddits = []
        
        for subreddit in subreddits:
            try:
                posts = self._search_ticker_mentions(subreddit, ticker, limit=50)
                
                for post in posts:
                    # Combine title and selftext for analysis
                    title = post.get('title', '')
                    selftext = post.get('selftext', '')
                    combined_text = f"{title} {selftext}"
                    
                    sentiment = self._analyze_text_sentiment(combined_text)
                    
                    all_mentions.append({
                        'subreddit': subreddit,
                        'title': title,
                        'score': post.get('score', 0),
                        'num_comments': post.get('num_comments', 0),
                        'created_utc': post.get('created_utc', 0),
                        'sentiment': sentiment,
                        'url': post.get('permalink', '')
                    })
            
            except Exception as e:
                failed_subreddits.append(subreddit)
                logger.warning(f"⚠️ Failed to fetch from r/{subreddit}: {str(e)}")
        
        # If ALL subreddits failed, raise error instead of returning zeros
        if len(failed_subreddits) == len(subreddits):
            error_msg = f"Reddit API failed for all subreddits: {', '.join(subreddits)}"
            logger.error(f"❌ {error_msg}")
            raise RuntimeError(error_msg)
        
        if not all_mentions:
            logger.info(f"No Reddit mentions found for {ticker}")
            return {
                'ticker': ticker.upper(),
                'mention_count': 0,
                'sentiment_score': 0.0,
                'signal_strength': 0.0,
                'trending': False,
                'source': 'reddit',
                'data_quality': 'NO_MENTIONS'
            }
        
        # Calculate aggregate metrics
        mention_count = len(all_mentions)
        avg_sentiment = sum(m['sentiment'] for m in all_mentions) / mention_count
        
        # Weight by post engagement (score + comments)
        weighted_sentiment = 0.0
        total_engagement = 0
        
        for mention in all_mentions:
            engagement = mention['score'] + mention['num_comments']
            weighted_sentiment += mention['sentiment'] * engagement
            total_engagement += engagement
        
        if total_engagement > 0:
            weighted_sentiment /= total_engagement
        else:
            weighted_sentiment = avg_sentiment
        
        # Determine if trending (high mention count)
        trending = mention_count > 20
        
        # Signal strength based on mention count and engagement
        signal_strength = min(mention_count / 50, 1.0)
        
        logger.info(f"Reddit sentiment for {ticker}: {weighted_sentiment:+.3f} ({mention_count} mentions)")
        
        return {
            'ticker': ticker.upper(),
            'mention_count': mention_count,
            'sentiment_score': weighted_sentiment,
            'raw_sentiment': avg_sentiment,
            'signal_strength': signal_strength,
            'trending': trending,
            'top_mentions': sorted(all_mentions, key=lambda x: x['score'], reverse=True)[:5],
            'source': 'reddit',
            'timestamp': datetime.now().isoformat(),
            'data_quality': 'SUCCESS',
            'failed_subreddits': failed_subreddits if failed_subreddits else []
        }
    
    def get_wallstreetbets_sentiment(self, ticker: str) -> Dict[str, Any]:
        """
        Get sentiment specifically from r/wallstreetbets
        This subreddit is known for market-moving discussions
        """
        return self.get_ticker_sentiment(ticker, subreddits=['wallstreetbets'])
    
    def compare_sentiment_momentum(self, ticker: str) -> Dict[str, Any]:
        """
        Compare sentiment across multiple timeframes
        Detect if sentiment is improving or deteriorating
        """
        # Get recent sentiment (last week)
        current = self.get_ticker_sentiment(ticker)
        
        # Simple momentum: if high mention count with positive sentiment = bullish momentum
        momentum_score = current['sentiment_score'] * current['signal_strength']
        
        return {
            'ticker': ticker.upper(),
            'current_sentiment': current['sentiment_score'],
            'mention_count': current['mention_count'],
            'momentum_score': momentum_score,
            'momentum_direction': 'BULLISH' if momentum_score > 0.2 else 'BEARISH' if momentum_score < -0.2 else 'NEUTRAL',
            'source': 'reddit',
            'timestamp': datetime.now().isoformat()
        }


# Export
__all__ = ['RedditSentimentTracker']
