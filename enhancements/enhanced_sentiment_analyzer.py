"""
Enhanced Sentiment Analysis (FREE)
Financial sentiment analysis without heavy ML models
Uses pattern matching and financial domain knowledge
No hardcoded sentiment - analyzes real text
"""

import re
import logging
from typing import Dict, List, Optional, Any
from collections import Counter

logger = logging.getLogger(__name__)

class FinancialSentimentAnalyzer:
    """
    Financial domain-specific sentiment analysis
    No transformer models needed - uses pattern matching and keywords
    """
    
    def __init__(self):
        # Strong bullish indicators
        self.strong_bullish = {
            'beat expectations': 3.0,
            'beats expectations': 3.0,
            'exceeded expectations': 3.0,
            'raises guidance': 2.5,
            'upgrades': 2.0,
            'upgraded': 2.0,
            'strong earnings': 2.5,
            'record revenue': 2.5,
            'record profit': 2.5,
            'breakout': 2.0,
            'all-time high': 2.0,
            'bullish': 1.5,
            'momentum': 1.5,
            'surges': 2.0,
            'soars': 2.0,
            'rallies': 1.5,
        }
        
        # Strong bearish indicators
        self.strong_bearish = {
            'missed expectations': -3.0,
            'misses expectations': -3.0,
            'lowers guidance': -2.5,
            'downgrades': -2.0,
            'downgraded': -2.0,
            'weak earnings': -2.5,
            'disappointing': -2.0,
            'bearish': -1.5,
            'plunges': -2.5,
            'crashes': -3.0,
            'tumbles': -2.0,
            'falls': -1.5,
            'drops': -1.5,
            'concerns': -1.5,
            'warning': -2.0,
        }
        
        # Moderate bullish
        self.moderate_bullish = {
            'positive': 1.0,
            'growth': 1.0,
            'gains': 1.0,
            'rises': 1.0,
            'up': 0.8,
            'increase': 1.0,
            'strong': 1.0,
            'optimistic': 1.2,
            'buy': 1.0,
            'long': 0.8,
        }
        
        # Moderate bearish
        self.moderate_bearish = {
            'negative': -1.0,
            'decline': -1.0,
            'losses': -1.0,
            'down': -0.8,
            'decrease': -1.0,
            'weak': -1.0,
            'pessimistic': -1.2,
            'sell': -1.0,
            'short': -0.8,
            'risk': -0.8,
        }
        
        # Price movement patterns
        self.price_patterns = {
            r'\+\d+\.?\d*%': 'positive_percent',
            r'-\d+\.?\d*%': 'negative_percent',
            r'up \d+\.?\d*%': 'positive_percent',
            r'down \d+\.?\d*%': 'negative_percent',
            r'gains? \$\d+': 'positive_dollar',
            r'loses? \$\d+': 'negative_dollar',
        }
        
        logger.info("✅ Financial sentiment analyzer initialized")
    
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of financial text
        Returns: sentiment score, confidence, and reasoning
        """
        if not text or len(text.strip()) == 0:
            return {
                'sentiment_score': 0.0,
                'confidence': 0.0,
                'direction': 'NEUTRAL',
                'signals': []
            }
        
        text_lower = text.lower()
        signals = []
        total_score = 0.0
        
        # Check strong signals
        for phrase, score in self.strong_bullish.items():
            if phrase in text_lower:
                signals.append({'phrase': phrase, 'score': score, 'type': 'strong_bullish'})
                total_score += score
        
        for phrase, score in self.strong_bearish.items():
            if phrase in text_lower:
                signals.append({'phrase': phrase, 'score': score, 'type': 'strong_bearish'})
                total_score += score
        
        # Check moderate signals
        for phrase, score in self.moderate_bullish.items():
            if phrase in text_lower:
                signals.append({'phrase': phrase, 'score': score, 'type': 'moderate_bullish'})
                total_score += score
        
        for phrase, score in self.moderate_bearish.items():
            if phrase in text_lower:
                signals.append({'phrase': phrase, 'score': score, 'type': 'moderate_bearish'})
                total_score += score
        
        # Check price patterns
        for pattern, pattern_type in self.price_patterns.items():
            matches = re.findall(pattern, text_lower)
            for match in matches:
                score = 1.5 if 'positive' in pattern_type else -1.5
                signals.append({'phrase': match, 'score': score, 'type': pattern_type})
                total_score += score
        
        # Normalize score to -1 to +1 range
        if len(signals) > 0:
            # Cap extreme scores
            max_possible = len(signals) * 3.0  # Max possible if all strong signals
            normalized_score = max(-1.0, min(1.0, total_score / max_possible))
            confidence = min(len(signals) / 10, 1.0)  # More signals = higher confidence
        else:
            normalized_score = 0.0
            confidence = 0.0
        
        # Determine direction
        if normalized_score > 0.2:
            direction = 'BULLISH'
        elif normalized_score < -0.2:
            direction = 'BEARISH'
        else:
            direction = 'NEUTRAL'
        
        return {
            'sentiment_score': normalized_score,  # -1 to +1
            'confidence': confidence,  # 0 to 1
            'direction': direction,
            'raw_score': total_score,
            'signal_count': len(signals),
            'signals': signals
        }
    
    def analyze_news_batch(self, news_items: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Analyze sentiment across multiple news items
        Aggregates sentiment with recency weighting
        """
        if not news_items:
            return {
                'overall_score': 0.0,
                'overall_direction': 'NEUTRAL',
                'confidence': 0.0,
                'article_count': 0
            }
        
        sentiments = []
        recency_weights = []
        
        for i, item in enumerate(news_items):
            # Combine headline and summary
            text = f"{item.get('headline', '')} {item.get('summary', '')}"
            
            # Analyze sentiment
            analysis = self.analyze_text(text)
            sentiments.append(analysis['sentiment_score'])
            
            # Weight more recent articles higher
            # Assume items are sorted by recency (most recent first)
            recency_weight = 1.0 / (1 + i * 0.1)  # Exponential decay
            recency_weights.append(recency_weight)
        
        # Calculate weighted average
        if sum(recency_weights) > 0:
            weighted_score = sum(s * w for s, w in zip(sentiments, recency_weights)) / sum(recency_weights)
        else:
            weighted_score = 0.0
        
        # Calculate confidence based on consistency and article count
        sentiment_std = 0.0
        if len(sentiments) > 1:
            sentiment_std = (sum((s - weighted_score) ** 2 for s in sentiments) / len(sentiments)) ** 0.5
            consistency = 1.0 - min(sentiment_std, 1.0)
            confidence = (consistency + min(len(sentiments) / 20, 1.0)) / 2
        else:
            confidence = 0.3  # Low confidence with only 1 article
        
        # Determine direction
        if weighted_score > 0.15:
            direction = 'BULLISH'
        elif weighted_score < -0.15:
            direction = 'BEARISH'
        else:
            direction = 'NEUTRAL'
        
        return {
            'overall_score': weighted_score,  # -1 to +1
            'overall_direction': direction,
            'confidence': confidence,  # 0 to 1
            'article_count': len(news_items),
            'individual_sentiments': sentiments,
            'sentiment_consistency': 1.0 - min(sentiment_std, 1.0)
        }
    
    def detect_sentiment_bias(self, analysis_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Detect if sentiment analysis has systematic bias
        Check if predictions consistently lean one direction
        """
        if not analysis_history or len(analysis_history) < 10:
            return {
                'bias_detected': False,
                'bias_direction': 'NONE',
                'bias_magnitude': 0.0,
                'interpretation': 'INSUFFICIENT_DATA'
            }
        
        scores = [item.get('overall_score', 0.0) for item in analysis_history]
        
        # Calculate mean and check if significantly different from 0
        mean_score = sum(scores) / len(scores)
        
        # Calculate standard error
        variance = sum((s - mean_score) ** 2 for s in scores) / len(scores)
        std_error = (variance / len(scores)) ** 0.5
        
        # Statistical test: is mean significantly different from 0?
        # Simple threshold-based approach
        bias_threshold = 0.15
        
        if abs(mean_score) > bias_threshold:
            bias_detected = True
            bias_direction = 'BULLISH' if mean_score > 0 else 'BEARISH'
            bias_magnitude = abs(mean_score)
        else:
            bias_detected = False
            bias_direction = 'NONE'
            bias_magnitude = 0.0
        
        return {
            'bias_detected': bias_detected,
            'bias_direction': bias_direction,
            'bias_magnitude': bias_magnitude,
            'mean_score': mean_score,
            'std_error': std_error,
            'interpretation': 'BIASED' if bias_detected else 'UNBIASED',
            'sample_size': len(scores)
        }


# Export
__all__ = ['FinancialSentimentAnalyzer']
