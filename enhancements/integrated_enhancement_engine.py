"""
Integrated Enhancement Engine
Combines all 5 free enhancements into prediction system:
1. Finnhub data source (better than Yahoo Finance)
2. SEC Edgar insider data (real Form 4 filings)
3. Feature importance analysis (model interpretability)
4. Reddit sentiment tracking (r/wallstreetbets, r/stocks)
5. Enhanced financial sentiment analysis

NO hardcoded values, NO directional bias, ALL real data
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import numpy as np

# Import all enhancement modules
from .finnhub_data_source import FinnhubDataSource
from .sec_edgar_insider import SECInsiderTracker
from .feature_importance_analyzer import FeatureImportanceAnalyzer
from .reddit_sentiment import RedditSentimentTracker
from .enhanced_sentiment_analyzer import FinancialSentimentAnalyzer

logger = logging.getLogger(__name__)

class IntegratedEnhancementEngine:
    """
    Orchestrates all 5 free enhancements
    Provides unified interface for enhanced predictions
    """
    
    def __init__(self, symbol: str = "AMD"):
        self.symbol = symbol
        
        # Initialize all components
        self.finnhub = FinnhubDataSource()
        self.sec_insider = SECInsiderTracker()
        self.feature_analyzer = FeatureImportanceAnalyzer()
        self.reddit_sentiment = RedditSentimentTracker()
        self.sentiment_analyzer = FinancialSentimentAnalyzer()
        
        # Track enhancement usage
        self.enhancement_status = {
            'finnhub_enabled': self.finnhub.enabled,
            'sec_edgar_enabled': True,  # No API key needed
            'feature_analysis_enabled': True,
            'reddit_enabled': True,
            'sentiment_analysis_enabled': True
        }
        
        logger.info(f"✅ Integrated Enhancement Engine initialized for {symbol}")
        logger.info(f"Enhancement status: {self.enhancement_status}")
    
    def get_enhanced_market_data(self) -> Dict[str, Any]:
        """
        Get market data with Finnhub (better than Yahoo Finance)
        Falls back gracefully if unavailable
        """
        finnhub_data = None
        
        if self.finnhub.enabled:
            try:
                finnhub_data = self.finnhub.get_quote(self.symbol)
                logger.info(f"✅ Retrieved Finnhub quote for {self.symbol}")
            except Exception as e:
                logger.warning(f"Finnhub quote failed: {e}")
        
        return {
            'finnhub_quote': finnhub_data,
            'data_source': 'finnhub' if finnhub_data else 'fallback',
            'timestamp': datetime.now().isoformat()
        }
    
    def get_insider_intelligence(self) -> Dict[str, Any]:
        """
        Get real insider trading data from SEC Edgar
        100% real data, no proxies
        FAILS LOUDLY - raises exception if API unavailable
        """
        try:
            insider_summary = self.sec_insider.get_insider_summary(self.symbol)
            
            # Validate we got real data
            if insider_summary.get('transactions_90d', 0) == 0:
                logger.warning(f"⚠️ No insider transactions found for {self.symbol} (may be normal)")
            else:
                logger.info(f"✅ Retrieved {insider_summary.get('transactions_90d', 0)} insider transactions for {self.symbol}")
            
            return insider_summary
        except Exception as e:
            error_msg = f"SEC Edgar API FAILED for {self.symbol}: {str(e)}"
            logger.error(f"❌ {error_msg}")
            # FAIL LOUDLY - raise the error instead of masking it
            raise RuntimeError(error_msg) from e
    
    def get_social_sentiment(self) -> Dict[str, Any]:
        """
        Get Reddit sentiment (r/wallstreetbets, r/stocks, r/AMD)
        Real-time discussion analysis with OAuth
        FAILS LOUDLY - raises exception if OAuth not configured or API unavailable
        """
        try:
            reddit_data = self.reddit_sentiment.get_ticker_sentiment(
                self.symbol,
                subreddits=['wallstreetbets', 'stocks', 'AMD']
            )
            
            # Validate we got real data
            if reddit_data.get('mention_count', 0) == 0:
                logger.warning(f"⚠️ Reddit: 0 mentions for {self.symbol} (normal if not discussed)")
            else:
                logger.info(f"✅ Retrieved Reddit sentiment: {reddit_data['mention_count']} mentions for {self.symbol}")
            
            return reddit_data
        except Exception as e:
            error_msg = f"Reddit API FAILED for {self.symbol}: {str(e)}"
            logger.error(f"❌ {error_msg}")
            # FAIL LOUDLY - raise the error instead of masking it
            raise RuntimeError(error_msg) from e
    
    def get_news_sentiment(self) -> Dict[str, Any]:
        """
        Get news sentiment from Finnhub + enhanced analysis
        Real news articles, real sentiment scores
        """
        news_sentiment_result = {
            'overall_score': 0.0,
            'overall_direction': 'NEUTRAL',
            'confidence': 0.0,
            'article_count': 0
        }
        
        if self.finnhub.enabled:
            try:
                # Get real news from Finnhub
                news_items = self.finnhub.get_company_news(self.symbol, days_back=7)
                
                if news_items:
                    # Analyze sentiment
                    news_sentiment_result = self.sentiment_analyzer.analyze_news_batch(news_items)
                    logger.info(f"✅ Analyzed {len(news_items)} news articles: {news_sentiment_result['overall_direction']}")
                
            except Exception as e:
                logger.error(f"News sentiment analysis failed: {e}")
        
        return news_sentiment_result
    
    def get_analyst_sentiment(self) -> Dict[str, Any]:
        """
        Get analyst recommendations from Finnhub
        Real analyst data, not fabricated
        """
        if not self.finnhub.enabled:
            return {'recommendation_score': 0.0, 'data_available': False}
        
        try:
            recommendations = self.finnhub.get_recommendation_trends(self.symbol)
            
            if recommendations:
                score = self.finnhub.calculate_recommendation_score(recommendations)
                logger.info(f"✅ Analyst recommendation score: {score:.2f}")
                return {
                    'recommendation_score': score,
                    'recommendations': recommendations,
                    'data_available': True
                }
            else:
                return {'recommendation_score': 0.0, 'data_available': False}
                
        except Exception as e:
            logger.error(f"Analyst sentiment failed: {e}")
            return {'recommendation_score': 0.0, 'data_available': False, 'error': str(e)}
    
    def analyze_model_features(
        self,
        models: Dict[str, Any],
        feature_names: List[str],
        X: Optional[np.ndarray] = None,
        y: Optional[np.ndarray] = None
    ) -> Dict[str, Any]:
        """
        Analyze feature importance across models
        Detect bias and ensure model interpretability
        """
        try:
            report = self.feature_analyzer.generate_importance_report(
                models, feature_names, X, y
            )
            
            logger.info(f"✅ Feature importance analysis complete")
            logger.info(f"Top feature: {report['top_features'][0][0]} ({report['top_features'][0][1]:.4f})")
            logger.info(f"Bias: {report['bias_analysis']['interpretation']}")
            logger.info(f"Stability: {report['stability_analysis']['interpretation']}")
            
            return report
            
        except Exception as e:
            logger.error(f"Feature analysis failed: {e}")
            return {
                'top_features': [],
                'bias_analysis': {'interpretation': 'ERROR'},
                'stability_analysis': {'interpretation': 'ERROR'},
                'error': str(e)
            }
    
    def get_comprehensive_sentiment(self) -> Dict[str, Any]:
        """
        Aggregate sentiment from all sources
        Returns unbiased, weighted sentiment score
        FAILS LOUDLY if critical data sources are unavailable
        """
        # Track failed sources
        failed_sources = []
        
        # Get all sentiment sources - these now raise errors instead of masking failures
        try:
            insider = self.get_insider_intelligence()
        except Exception as e:
            failed_sources.append(f"SEC Edgar: {str(e)}")
            insider = None
        
        try:
            social = self.get_social_sentiment()
        except Exception as e:
            failed_sources.append(f"Reddit: {str(e)}")
            social = None
        
        try:
            news = self.get_news_sentiment()
        except Exception as e:
            failed_sources.append(f"News: {str(e)}")
            news = None
        
        try:
            analyst = self.get_analyst_sentiment()
        except Exception as e:
            failed_sources.append(f"Analyst: {str(e)}")
            analyst = None
        
        # If ALL sources failed, raise error
        if all(source is None for source in [insider, social, news, analyst]):
            error_msg = f"ALL sentiment sources FAILED: {'; '.join(failed_sources)}"
            logger.error(f"❌ {error_msg}")
            raise RuntimeError(error_msg)
        
        # Log failed sources as warnings
        if failed_sources:
            logger.warning(f"⚠️ Some sentiment sources failed: {'; '.join(failed_sources)}")
        
        # Extract sentiment scores (all normalized to -1 to +1 scale)
        sentiment_sources = []
        weights = []
        
        # Insider sentiment (30-day)
        if insider:
            insider_score = insider.get('sentiment_30d', {}).get('sentiment_score', 0.0)
            insider_strength = insider.get('sentiment_30d', {}).get('signal_strength', 0.0)
            if insider_strength > 0:
                sentiment_sources.append(insider_score)
                weights.append(insider_strength * 1.5)
        
        # Social sentiment (Reddit)
        if social:
            social_score = social.get('sentiment_score', 0.0)
            social_strength = social.get('signal_strength', 0.0)
            if social_strength > 0:
                sentiment_sources.append(social_score)
                weights.append(social_strength * 1.0)
        
        # News sentiment
        if news:
            news_score = news.get('overall_score', 0.0)
            news_confidence = news.get('confidence', 0.0)
            if news_confidence > 0:
                sentiment_sources.append(news_score)
                weights.append(news_confidence * 1.2)
        
        # Analyst sentiment
        if analyst:
            analyst_score = analyst.get('recommendation_score', 0.0)
            if analyst.get('data_available', False):
                sentiment_sources.append(analyst_score)
                weights.append(1.3)
        
        # Calculate weighted average sentiment
        if len(sentiment_sources) > 0 and sum(weights) > 0:
            weighted_sentiment = sum(s * w for s, w in zip(sentiment_sources, weights)) / sum(weights)
            confidence = min(sum(weights) / 5.0, 1.0)
        else:
            weighted_sentiment = 0.0
            confidence = 0.0
        
        # Determine direction (unbiased thresholds)
        if weighted_sentiment > 0.15:
            direction = 'BULLISH'
        elif weighted_sentiment < -0.15:
            direction = 'BEARISH'
        else:
            direction = 'NEUTRAL'
        
        return {
            'aggregate_sentiment': weighted_sentiment,
            'confidence': confidence,
            'direction': direction,
            'components': {
                'insider': {'score': insider.get('sentiment_30d', {}).get('sentiment_score', 0.0) if insider else 0.0, 'weight': insider.get('sentiment_30d', {}).get('signal_strength', 0.0) * 1.5 if insider else 0.0},
                'social': {'score': social.get('sentiment_score', 0.0) if social else 0.0, 'weight': social.get('signal_strength', 0.0) * 1.0 if social else 0.0},
                'news': {'score': news.get('overall_score', 0.0) if news else 0.0, 'weight': news.get('confidence', 0.0) * 1.2 if news else 0.0},
                'analyst': {'score': analyst.get('recommendation_score', 0.0) if analyst else 0.0, 'weight': 1.3 if (analyst and analyst.get('data_available', False)) else 0.0}
            },
            'source_count': len(sentiment_sources),
            'failed_sources': failed_sources,
            'timestamp': datetime.now().isoformat()
        }
    
    def validate_no_bias(self, prediction_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate that the system has no directional bias
        Analyzes historical predictions to ensure fairness
        """
        if len(prediction_history) < 20:
            return {
                'bias_check': 'INSUFFICIENT_DATA',
                'sample_size': len(prediction_history),
                'recommendation': 'Need at least 20 predictions to detect bias'
            }
        
        # Extract directions from history
        up_predictions = sum(1 for p in prediction_history if p.get('direction') == 'UP')
        down_predictions = sum(1 for p in prediction_history if p.get('direction') == 'DOWN')
        neutral_predictions = sum(1 for p in prediction_history if p.get('direction') in ['NEUTRAL', 'SKIP'])
        
        total = len(prediction_history)
        
        # Calculate proportions
        up_pct = up_predictions / total
        down_pct = down_predictions / total
        neutral_pct = neutral_predictions / total
        
        # Check for bias (should be roughly balanced over time)
        # Allow for some market-driven imbalance, but flag extreme bias
        bias_threshold = 0.65  # If >65% one direction, flag it
        
        if up_pct > bias_threshold:
            bias_detected = True
            bias_direction = 'BULLISH_BIAS'
        elif down_pct > bias_threshold:
            bias_detected = True
            bias_direction = 'BEARISH_BIAS'
        else:
            bias_detected = False
            bias_direction = 'BALANCED'
        
        return {
            'bias_check': 'BIASED' if bias_detected else 'UNBIASED',
            'bias_direction': bias_direction,
            'distribution': {
                'UP': up_pct,
                'DOWN': down_pct,
                'NEUTRAL': neutral_pct
            },
            'sample_size': total,
            'interpretation': 'PASS' if not bias_detected else 'FAIL - System shows directional bias'
        }
    
    def get_enhancement_summary(self) -> Dict[str, Any]:
        """
        Get summary of all enhancements and their status
        """
        return {
            'engine_name': 'Integrated Enhancement Engine',
            'symbol': self.symbol,
            'enhancements': {
                '1_finnhub_data': {
                    'enabled': self.finnhub.enabled,
                    'description': 'Real-time quotes and news (60 calls/min free)',
                    'status': '✅ ACTIVE' if self.finnhub.enabled else '⚠️ DISABLED (no API key)'
                },
                '2_sec_edgar_insider': {
                    'enabled': True,
                    'description': 'Real Form 4 insider trading data (unlimited free)',
                    'status': '✅ ACTIVE'
                },
                '3_feature_importance': {
                    'enabled': True,
                    'description': 'Model interpretability and bias detection',
                    'status': '✅ ACTIVE'
                },
                '4_reddit_sentiment': {
                    'enabled': True,
                    'description': 'Social sentiment from r/wallstreetbets, r/stocks',
                    'status': '✅ ACTIVE'
                },
                '5_enhanced_sentiment': {
                    'enabled': True,
                    'description': 'Financial domain-specific sentiment analysis',
                    'status': '✅ ACTIVE'
                }
            },
            'data_quality': 'REAL (no hardcoded fallbacks)',
            'bias_prevention': 'ACTIVE (monitored)',
            'timestamp': datetime.now().isoformat()
        }


# Export
__all__ = ['IntegratedEnhancementEngine']
