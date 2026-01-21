"""
Integrated Sentiment Tracker
Combines:
1. Market Internals (advance/decline, highs/lows)
2. Reddit Sentiment (WallStreetBets, stocks, investing)
3. Twitter/X Sentiment ($AMD mentions)

Returns single 0-10 score for system integration
"""

from market_internals_tracker import MarketInternalsTracker
from reddit_sentiment_tracker import RedditSentimentTracker
from twitter_sentiment_tracker import TwitterSentimentTracker
from typing import Dict

class IntegratedSentimentTracker:
    """Combine market internals and social sentiment into single score."""
    
    def __init__(self):
        self.internals_tracker = MarketInternalsTracker()
        self.reddit_tracker = RedditSentimentTracker()
        self.twitter_tracker = TwitterSentimentTracker()
    
    def get_complete_sentiment_score(self) -> Dict:
        """
        Get complete sentiment analysis from all sources.
        
        Returns:
            score (0-10): Overall sentiment score
            breakdown: Individual component scores
            impact: Overall impact on AMD (BULLISH/BEARISH/NEUTRAL)
        """
        print("\n" + "="*60)
        print("🎯 INTEGRATED SENTIMENT ANALYSIS")
        print("="*60)
        
        # Get all components
        internals = self.internals_tracker.get_market_breadth_score()
        reddit = self.reddit_tracker.get_overall_reddit_sentiment()
        twitter = self.twitter_tracker.get_twitter_sentiment_score()
        
        # Weight components
        weights = {
            'market_internals': 0.50,  # Market breadth most important
            'reddit': 0.30,             # WSB has real trading impact
            'twitter': 0.20             # Supporting indicator
        }
        
        # Calculate weighted score
        total_score = (
            internals['total_score'] * weights['market_internals'] +
            reddit['score'] * weights['reddit'] +
            twitter['score'] * weights['twitter']
        )
        
        # Determine overall impact
        if total_score >= 7:
            overall_impact = 'BULLISH'
            confidence = 'HIGH'
        elif total_score >= 5.5:
            overall_impact = 'SLIGHTLY_BULLISH'
            confidence = 'MEDIUM'
        elif total_score >= 4.5:
            overall_impact = 'NEUTRAL'
            confidence = 'LOW'
        elif total_score >= 3:
            overall_impact = 'SLIGHTLY_BEARISH'
            confidence = 'MEDIUM'
        else:
            overall_impact = 'BEARISH'
            confidence = 'HIGH'
        
        # Print summary
        print(f"\n📊 COMPONENT SCORES:")
        print(f"   Market Internals: {internals['total_score']:.1f}/10 ({internals['assessment']})")
        print(f"   Reddit Sentiment: {reddit['score']:.1f}/10 ({reddit['sentiment']}) - {reddit['mentions']} mentions")
        print(f"   Twitter Sentiment: {twitter['score']:.1f}/10 ({twitter['sentiment']}) - {twitter['tweets']} tweets")
        
        print(f"\n🎯 INTEGRATED SCORE: {total_score:.2f}/10")
        print(f"📈 Overall Impact: {overall_impact}")
        print(f"💪 Confidence: {confidence}")
        
        return {
            'total_score': round(total_score, 2),
            'overall_impact': overall_impact,
            'confidence': confidence,
            'breakdown': {
                'market_internals': {
                    'score': internals['total_score'],
                    'weight': weights['market_internals'],
                    'assessment': internals['assessment']
                },
                'reddit': {
                    'score': reddit['score'],
                    'weight': weights['reddit'],
                    'sentiment': reddit['sentiment'],
                    'mentions': reddit['mentions']
                },
                'twitter': {
                    'score': twitter['score'],
                    'weight': weights['twitter'],
                    'sentiment': twitter['sentiment'],
                    'tweets': twitter['tweets']
                }
            }
        }
    
    def boost_prediction_confidence(self, base_confidence: float, prediction_direction: str) -> Dict:
        """
        Boost or penalize prediction confidence based on sentiment.
        
        Args:
            base_confidence: Original prediction confidence (0-1)
            prediction_direction: 'UP' or 'DOWN'
        
        Returns:
            adjusted_confidence: Modified confidence
            adjustment: How much was added/subtracted
            reason: Why adjustment was made
        """
        sentiment = self.get_complete_sentiment_score()
        sentiment_score = sentiment['total_score']
        
        # Determine sentiment direction
        if sentiment_score >= 6:
            sentiment_direction = 'UP'
        elif sentiment_score <= 4:
            sentiment_direction = 'DOWN'
        else:
            sentiment_direction = 'NEUTRAL'
        
        # Calculate adjustment
        if sentiment_direction == prediction_direction:
            # Sentiment confirms prediction
            adjustment = (sentiment_score - 5) * 0.02  # Max +10% boost
            reason = f"Sentiment confirms {prediction_direction} prediction"
        elif sentiment_direction == 'NEUTRAL':
            # No adjustment
            adjustment = 0.0
            reason = "Neutral sentiment - no adjustment"
        else:
            # Sentiment conflicts with prediction
            adjustment = (sentiment_score - 5) * 0.03  # Max -15% penalty
            reason = f"Sentiment conflicts with {prediction_direction} prediction"
        
        adjusted_confidence = base_confidence + adjustment
        adjusted_confidence = max(0.0, min(1.0, adjusted_confidence))  # Clamp 0-1
        
        return {
            'original_confidence': base_confidence,
            'adjusted_confidence': adjusted_confidence,
            'adjustment': round(adjustment, 3),
            'reason': reason,
            'sentiment_score': sentiment_score,
            'sentiment_impact': sentiment['overall_impact']
        }

def integrate_with_prediction_system():
    """
    Example integration with main prediction system.
    Add this to your prediction pipeline.
    """
    print("\n" + "="*60)
    print("🔧 EXAMPLE INTEGRATION WITH PREDICTION SYSTEM")
    print("="*60)
    
    # Initialize tracker
    tracker = IntegratedSentimentTracker()
    
    # Get sentiment
    sentiment = tracker.get_complete_sentiment_score()
    
    # Example: Apply to a prediction
    example_prediction = {
        'direction': 'UP',
        'confidence': 0.65
    }
    
    print(f"\n📊 BEFORE SENTIMENT ADJUSTMENT:")
    print(f"   Direction: {example_prediction['direction']}")
    print(f"   Confidence: {example_prediction['confidence']:.1%}")
    
    # Adjust confidence
    result = tracker.boost_prediction_confidence(
        example_prediction['confidence'],
        example_prediction['direction']
    )
    
    print(f"\n📊 AFTER SENTIMENT ADJUSTMENT:")
    print(f"   Direction: {example_prediction['direction']}")
    print(f"   Confidence: {result['adjusted_confidence']:.1%} ({result['adjustment']:+.1%})")
    print(f"   Reason: {result['reason']}")
    
    return sentiment, result

if __name__ == "__main__":
    # Test integrated tracker
    print("\n🎯 INTEGRATED SENTIMENT TRACKER TEST\n")
    
    integrate_with_prediction_system()
    
    print(f"\n{'='*60}")
    print("✅ INTEGRATION TEST COMPLETE")
    print("="*60)
    print("\nTo integrate into your main system:")
    print("1. Import: from integrated_sentiment_tracker import IntegratedSentimentTracker")
    print("2. Initialize: tracker = IntegratedSentimentTracker()")
    print("3. Get score: sentiment = tracker.get_complete_sentiment_score()")
    print("4. Adjust confidence: result = tracker.boost_prediction_confidence(conf, dir)")
