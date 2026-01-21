"""
Free Enhancements Package
5 Free upgrades to improve prediction accuracy:
1. Finnhub data source (better than Yahoo Finance)
2. SEC Edgar insider data (real Form 4 filings)
3. Feature importance analysis (model interpretability)
4. Reddit sentiment tracking
5. Enhanced financial sentiment analysis

All enhancements use real data with no hardcoded fallbacks
"""

from .finnhub_data_source import FinnhubDataSource
from .sec_edgar_insider import SECInsiderTracker
from .feature_importance_analyzer import FeatureImportanceAnalyzer
from .reddit_sentiment import RedditSentimentTracker
from .enhanced_sentiment_analyzer import FinancialSentimentAnalyzer
from .integrated_enhancement_engine import IntegratedEnhancementEngine

__all__ = [
    'FinnhubDataSource',
    'SECInsiderTracker',
    'FeatureImportanceAnalyzer',
    'RedditSentimentTracker',
    'FinancialSentimentAnalyzer',
    'IntegratedEnhancementEngine'
]

__version__ = '1.0.0'
