"""
Enhanced Prediction System
Integrates all 5 free enhancements into the main gap predictor
NO hardcoded values, NO directional bias, ALL real data
"""

import logging
import sys
from typing import Dict, Any, Optional
from datetime import datetime
import numpy as np

# Import enhancements
from enhancements import IntegratedEnhancementEngine

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EnhancedPredictionSystem:
    """
    Main prediction system with all 5 free enhancements integrated
    Provides unbiased, accurate predictions using real data
    """
    
    def __init__(self, symbol: str = "AMD"):
        self.symbol = symbol
        self.enhancement_engine = IntegratedEnhancementEngine(symbol)
        self.prediction_history = []
        
        logger.info(f"🚀 Enhanced Prediction System initialized for {symbol}")
        
        # Print enhancement status
        status = self.enhancement_engine.get_enhancement_summary()
        logger.info("=" * 80)
        logger.info("ENHANCEMENT STATUS:")
        for key, enhancement in status['enhancements'].items():
            logger.info(f"  {key}: {enhancement['status']}")
        logger.info("=" * 80)
    
    def gather_enhanced_data(self) -> Dict[str, Any]:
        """
        Gather all enhanced data from 5 free sources
        Returns comprehensive market intelligence
        """
        logger.info("📊 Gathering enhanced market data...")
        
        # 1. Enhanced market quotes (Finnhub > Yahoo Finance)
        market_data = self.enhancement_engine.get_enhanced_market_data()
        logger.info(f"✓ Market data source: {market_data.get('data_source')}")
        
        # 2. Real insider trading data (SEC Edgar)
        insider_data = self.enhancement_engine.get_insider_intelligence()
        logger.info(f"✓ Insider transactions (30d): {insider_data.get('transactions_30d', 0)}")
        
        # 3. Social sentiment (Reddit)
        social_data = self.enhancement_engine.get_social_sentiment()
        logger.info(f"✓ Reddit mentions: {social_data.get('mention_count', 0)}")
        
        # 4. News sentiment (Finnhub + enhanced analysis)
        news_data = self.enhancement_engine.get_news_sentiment()
        logger.info(f"✓ News articles analyzed: {news_data.get('article_count', 0)}")
        
        # 5. Analyst sentiment (Finnhub)
        analyst_data = self.enhancement_engine.get_analyst_sentiment()
        logger.info(f"✓ Analyst data: {'Available' if analyst_data.get('data_available') else 'Unavailable'}")
        
        # Aggregate all sentiment
        comprehensive_sentiment = self.enhancement_engine.get_comprehensive_sentiment()
        logger.info(f"✓ Aggregate sentiment: {comprehensive_sentiment.get('direction')} ({comprehensive_sentiment.get('aggregate_sentiment'):.3f})")
        
        return {
            'market_data': market_data,
            'insider_data': insider_data,
            'social_data': social_data,
            'news_data': news_data,
            'analyst_data': analyst_data,
            'comprehensive_sentiment': comprehensive_sentiment,
            'timestamp': datetime.now().isoformat()
        }
    
    def calculate_enhanced_features(self, enhanced_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Calculate prediction features from enhanced data
        NO hardcoded values - all calculated from real data
        """
        features = {}
        
        # Sentiment features (all normalized -1 to +1)
        sentiment = enhanced_data['comprehensive_sentiment']
        features['aggregate_sentiment_score'] = sentiment.get('aggregate_sentiment', 0.0)
        features['sentiment_confidence'] = sentiment.get('confidence', 0.0)
        
        # Insider features (0 to 1 scale)
        insider = enhanced_data['insider_data']
        features['insider_sentiment_30d'] = insider.get('sentiment_30d', {}).get('sentiment_score', 0.0)
        features['insider_signal_strength'] = insider.get('sentiment_30d', {}).get('signal_strength', 0.0)
        features['insider_transaction_count'] = min(insider.get('transactions_30d', 0) / 10, 1.0)  # Normalize
        
        # Social features (-1 to +1)
        social = enhanced_data['social_data']
        features['reddit_sentiment'] = social.get('sentiment_score', 0.0)
        features['reddit_signal_strength'] = social.get('signal_strength', 0.0)
        features['reddit_trending'] = 1.0 if social.get('trending', False) else 0.0
        
        # News features (-1 to +1)
        news = enhanced_data['news_data']
        features['news_sentiment'] = news.get('overall_score', 0.0)
        features['news_confidence'] = news.get('confidence', 0.0)
        
        # Analyst features (-1 to +1)
        analyst = enhanced_data['analyst_data']
        features['analyst_sentiment'] = analyst.get('recommendation_score', 0.0)
        features['analyst_available'] = 1.0 if analyst.get('data_available', False) else 0.0
        
        # Composite features
        features['multi_source_agreement'] = self._calculate_agreement(
            features['aggregate_sentiment_score'],
            features['insider_sentiment_30d'],
            features['reddit_sentiment'],
            features['news_sentiment']
        )
        
        return features
    
    def _calculate_agreement(self, *scores) -> float:
        """
        Calculate agreement across multiple sentiment scores
        High agreement = all scores point same direction
        Returns 0 to 1 (1 = perfect agreement)
        """
        scores = [s for s in scores if abs(s) > 0.01]  # Filter out near-zero scores
        
        if len(scores) < 2:
            return 0.0
        
        # Check if all scores have same sign (all positive or all negative)
        signs = [1 if s > 0 else -1 for s in scores]
        
        if len(set(signs)) == 1:
            # All same direction - calculate how tight the agreement is
            mean_score = sum(scores) / len(scores)
            variance = sum((s - mean_score) ** 2 for s in scores) / len(scores)
            agreement = 1.0 - min(variance, 1.0)
        else:
            # Mixed signals - low agreement
            agreement = 0.0
        
        return agreement
    
    def make_prediction(self, enhanced_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make prediction using enhanced data
        NO directional bias - purely data-driven
        """
        logger.info("🎯 Making enhanced prediction...")
        
        # Gather data if not provided
        if enhanced_data is None:
            enhanced_data = self.gather_enhanced_data()
        
        # Calculate features
        features = self.calculate_enhanced_features(enhanced_data)
        
        # Get aggregate sentiment
        aggregate_sentiment = features['aggregate_sentiment_score']
        sentiment_confidence = features['sentiment_confidence']
        multi_source_agreement = features['multi_source_agreement']
        
        # Calculate prediction confidence (0 to 1)
        # High confidence requires: strong sentiment + high confidence + multi-source agreement
        prediction_confidence = (
            min(abs(aggregate_sentiment), 1.0) * 0.4 +  # Sentiment strength
            sentiment_confidence * 0.3 +  # Sentiment confidence
            multi_source_agreement * 0.3  # Multi-source agreement
        )
        
        # Determine direction (UNBIASED thresholds)
        # Only predict direction if confidence is sufficient
        if prediction_confidence < 0.50:
            direction = 'NEUTRAL'
            confidence = prediction_confidence
        elif aggregate_sentiment > 0.20:  # Bullish threshold
            direction = 'BULLISH'
            confidence = prediction_confidence
        elif aggregate_sentiment < -0.20:  # Bearish threshold
            direction = 'BEARISH'
            confidence = prediction_confidence
        else:
            direction = 'NEUTRAL'
            confidence = prediction_confidence
        
        # Calculate signal strength (for position sizing)
        signal_strength = min(prediction_confidence * abs(aggregate_sentiment), 1.0)
        
        # Prepare prediction result
        prediction = {
            'symbol': self.symbol,
            'direction': direction,
            'confidence': confidence,
            'signal_strength': signal_strength,
            'aggregate_sentiment': aggregate_sentiment,
            'features': features,
            'data_sources': {
                'insider_available': enhanced_data['insider_data'].get('transactions_30d', 0) > 0,
                'social_available': enhanced_data['social_data'].get('mention_count', 0) > 0,
                'news_available': enhanced_data['news_data'].get('article_count', 0) > 0,
                'analyst_available': enhanced_data['analyst_data'].get('data_available', False)
            },
            'timestamp': datetime.now().isoformat()
        }
        
        # Store in history for bias detection
        self.prediction_history.append(prediction)
        
        # Log prediction
        logger.info("=" * 80)
        logger.info(f"PREDICTION for {self.symbol}:")
        logger.info(f"  Direction: {direction}")
        logger.info(f"  Confidence: {confidence:.2%}")
        logger.info(f"  Signal Strength: {signal_strength:.2%}")
        logger.info(f"  Aggregate Sentiment: {aggregate_sentiment:+.3f}")
        logger.info(f"  Multi-source Agreement: {multi_source_agreement:.2%}")
        logger.info("=" * 80)
        
        return prediction
    
    def validate_bias(self) -> Dict[str, Any]:
        """
        Validate system has no directional bias
        """
        bias_check = self.enhancement_engine.validate_no_bias(self.prediction_history)
        
        logger.info("=" * 80)
        logger.info("BIAS VALIDATION:")
        logger.info(f"  Status: {bias_check.get('bias_check')}")
        logger.info(f"  Sample size: {bias_check.get('sample_size')}")
        
        if 'distribution' in bias_check:
            dist = bias_check['distribution']
            logger.info(f"  Distribution: UP={dist.get('UP', 0):.1%}, DOWN={dist.get('DOWN', 0):.1%}, NEUTRAL={dist.get('NEUTRAL', 0):.1%}")
        
        logger.info(f"  Interpretation: {bias_check.get('interpretation')}")
        logger.info("=" * 80)
        
        return bias_check
    
    def analyze_feature_importance(self, models: Dict[str, Any], feature_names: list) -> Dict[str, Any]:
        """
        Analyze feature importance to ensure no bias
        """
        logger.info("📊 Analyzing feature importance...")
        
        report = self.enhancement_engine.analyze_model_features(
            models, feature_names
        )
        
        logger.info("=" * 80)
        logger.info("FEATURE IMPORTANCE ANALYSIS:")
        logger.info(f"  Bias: {report.get('bias_analysis', {}).get('interpretation', 'N/A')}")
        logger.info(f"  Stability: {report.get('stability_analysis', {}).get('interpretation', 'N/A')}")
        logger.info("  Top 5 Features:")
        
        for i, (feature, importance) in enumerate(report.get('top_features', [])[:5], 1):
            logger.info(f"    {i}. {feature}: {importance:.4f}")
        
        logger.info("=" * 80)
        
        return report


def main():
    """
    Demonstration of enhanced prediction system
    """
    print("\n" + "=" * 80)
    print("🚀 ENHANCED PREDICTION SYSTEM")
    print("5 Free Upgrades: Finnhub + SEC Edgar + Feature Analysis + Reddit + Sentiment")
    print("=" * 80 + "\n")
    
    # Initialize system
    system = EnhancedPredictionSystem(symbol="AMD")
    
    # Make prediction
    print("\n📊 Gathering enhanced data and making prediction...\n")
    prediction = system.make_prediction()
    
    # Validate no bias
    if len(system.prediction_history) >= 5:
        print("\n🔍 Validating system for directional bias...\n")
        system.validate_bias()
    
    print("\n✅ Enhanced prediction complete!")
    print(f"\nTo enable all features, set these API keys (all FREE):")
    print("  - FINNHUB_API_KEY: Get from https://finnhub.io/register (60 calls/min free)")
    print("\nSEC Edgar and Reddit require no API keys!\n")
    
    return prediction


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)
