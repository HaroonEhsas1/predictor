#!/usr/bin/env python3
"""
Premium Data Aggregator
Combines FMP and MarketAux data with existing sources for institutional-grade analysis
"""

import os
import sys
import logging
from datetime import datetime
from typing import Dict, Any, Optional

# Add parent to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sources.fmp_integration import fmp_provider
from sources.marketaux_integration import marketaux_provider

logger = logging.getLogger(__name__)

class PremiumDataAggregator:
    """
    Aggregates premium data from FMP and MarketAux
    Provides institutional-grade fundamental and sentiment data
    """
    
    def __init__(self):
        self.fmp = fmp_provider
        self.marketaux = marketaux_provider
        
        # Log available sources
        sources = []
        if self.fmp.enabled:
            sources.append("FMP")
        if self.marketaux.enabled:
            sources.append("MarketAux")
        
        if sources:
            logger.info(f"✅ Premium Data: {', '.join(sources)} enabled")
        else:
            logger.warning("⚠️ Premium Data: No premium sources available")
    
    def get_fundamental_data(self, symbol: str) -> Dict[str, Any]:
        """
        Get comprehensive fundamental data from FMP
        Returns: analyst estimates, price targets, earnings, metrics, ownership
        """
        result = {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'source': 'premium_aggregator',
            'fmp_enabled': self.fmp.enabled
        }
        
        if not self.fmp.enabled:
            return result
        
        # Get comprehensive FMP data
        fmp_data = self.fmp.get_comprehensive_analysis(symbol)
        result['fmp_data'] = fmp_data
        
        # Extract key metrics for easy access
        if fmp_data.get('price_target'):
            pt = fmp_data['price_target']
            result['price_target_mean'] = pt.get('target_mean', 0)
            result['price_target_upside'] = 0
            
            if fmp_data.get('profile') and fmp_data['profile'].get('price'):
                current_price = fmp_data['profile']['price']
                if current_price > 0:
                    result['price_target_upside'] = ((pt.get('target_mean', 0) - current_price) / current_price) * 100
        
        if fmp_data.get('analyst_estimates'):
            est = fmp_data['analyst_estimates']
            result['eps_estimate'] = est.get('estimated_eps_avg', 0)
            result['revenue_estimate'] = est.get('estimated_revenue_avg', 0)
            result['analyst_count'] = est.get('number_analysts_estimated_eps', 0)
        
        if fmp_data.get('key_metrics'):
            metrics = fmp_data['key_metrics']
            result['pe_ratio'] = metrics.get('pe_ratio', 0)
            result['pb_ratio'] = metrics.get('pb_ratio', 0)
            result['roe'] = metrics.get('roe', 0)
            result['debt_to_equity'] = metrics.get('debt_to_equity', 0)
        
        if fmp_data.get('financial_score'):
            score = fmp_data['financial_score']
            result['quality_score'] = score.get('overall_score', 0)
        
        return result
    
    def get_sentiment_data(self, symbol: str) -> Dict[str, Any]:
        """
        Get comprehensive sentiment data from MarketAux
        Returns: news sentiment, trending status, alerts
        """
        result = {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'source': 'premium_aggregator',
            'marketaux_enabled': self.marketaux.enabled
        }
        
        if not self.marketaux.enabled:
            return result
        
        # Get comprehensive MarketAux data
        marketaux_data = self.marketaux.get_comprehensive_sentiment(symbol)
        result['marketaux_data'] = marketaux_data
        
        # Extract key sentiment metrics for easy access
        if marketaux_data.get('news_24h'):
            news = marketaux_data['news_24h']
            result['news_sentiment_24h'] = news.get('average_sentiment', 0)
            result['news_direction_24h'] = news.get('sentiment_direction', 'NEUTRAL')
            result['news_article_count_24h'] = news.get('article_count', 0)
        
        if marketaux_data.get('sentiment_stats'):
            stats = marketaux_data['sentiment_stats'].get('stats', [])
            if stats:
                result['sentiment_avg'] = stats[0].get('sentiment_avg', 0)
                result['sentiment_doc_count'] = stats[0].get('total_documents', 0)
        
        if marketaux_data.get('negative_alerts'):
            alerts = marketaux_data['negative_alerts']
            result['negative_alert_count'] = alerts.get('alert_count', 0)
            result['has_negative_alerts'] = alerts.get('alert_count', 0) > 0
        
        return result
    
    def get_institutional_signals(self, symbol: str) -> Dict[str, Any]:
        """
        Get institutional-grade signals combining FMP and MarketAux
        Returns: analyst sentiment, institutional ownership, news flow
        """
        result = {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'signals': []
        }
        
        # FMP institutional data
        if self.fmp.enabled:
            institutional = self.fmp.get_institutional_ownership(symbol)
            insider = self.fmp.get_insider_trading(symbol, limit=10)
            
            if institutional:
                result['institutional_ownership'] = institutional
                
                # Signal: High institutional ownership
                if institutional.get('number_of_holders', 0) > 100:
                    result['signals'].append({
                        'type': 'INSTITUTIONAL_INTEREST',
                        'strength': 'HIGH',
                        'description': f"{institutional['number_of_holders']} institutional holders"
                    })
            
            if insider:
                # Analyze recent insider trading
                buys = sum(1 for t in insider if 'P-Purchase' in t.get('transaction_type', ''))
                sells = sum(1 for t in insider if 'S-Sale' in t.get('transaction_type', ''))
                
                result['insider_trades'] = {'buys': buys, 'sells': sells, 'recent': insider[:5]}
                
                if buys > sells:
                    result['signals'].append({
                        'type': 'INSIDER_BUYING',
                        'strength': 'MODERATE' if buys - sells < 3 else 'STRONG',
                        'description': f"{buys} buys vs {sells} sells"
                    })
        
        # MarketAux sentiment signals
        if self.marketaux.enabled:
            sentiment = self.marketaux.get_news_sentiment(symbol, hours_back=24)
            
            if sentiment:
                result['news_sentiment'] = sentiment
                
                # Signal: Strong positive sentiment
                if sentiment.get('average_sentiment', 0) > 0.3:
                    result['signals'].append({
                        'type': 'POSITIVE_NEWS_FLOW',
                        'strength': 'STRONG',
                        'description': f"Sentiment: {sentiment['average_sentiment']:.2f}"
                    })
                
                # Signal: Strong negative sentiment
                elif sentiment.get('average_sentiment', 0) < -0.3:
                    result['signals'].append({
                        'type': 'NEGATIVE_NEWS_FLOW',
                        'strength': 'STRONG',
                        'description': f"Sentiment: {sentiment['average_sentiment']:.2f}"
                    })
        
        result['signal_count'] = len(result['signals'])
        
        return result
    
    def get_complete_analysis(self, symbol: str) -> Dict[str, Any]:
        """
        Get complete premium analysis combining all sources
        Returns: Fundamental data, sentiment, institutional signals
        """
        logger.info(f"🎯 Premium Analysis: Starting for {symbol}")
        
        analysis = {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'sources_enabled': {
                'fmp': self.fmp.enabled,
                'marketaux': self.marketaux.enabled
            }
        }
        
        # Fundamental data from FMP
        analysis['fundamentals'] = self.get_fundamental_data(symbol)
        
        # Sentiment data from MarketAux
        analysis['sentiment'] = self.get_sentiment_data(symbol)
        
        # Combined institutional signals
        analysis['institutional'] = self.get_institutional_signals(symbol)
        
        # Generate overall assessment
        analysis['assessment'] = self._generate_assessment(analysis)
        
        logger.info(f"✅ Premium Analysis: Complete for {symbol}")
        
        return analysis
    
    def _generate_assessment(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate overall assessment from all data sources"""
        assessment = {
            'score': 50,  # Neutral baseline
            'factors': [],
            'recommendation': 'NEUTRAL'
        }
        
        # Analyst sentiment
        if analysis['fundamentals'].get('price_target_upside'):
            upside = analysis['fundamentals']['price_target_upside']
            if upside > 20:
                assessment['score'] += 15
                assessment['factors'].append(f"Strong analyst upside: {upside:.1f}%")
            elif upside > 10:
                assessment['score'] += 10
                assessment['factors'].append(f"Moderate analyst upside: {upside:.1f}%")
            elif upside < -10:
                assessment['score'] -= 10
                assessment['factors'].append(f"Analyst downside: {upside:.1f}%")
        
        # News sentiment
        if analysis['sentiment'].get('news_sentiment_24h'):
            sentiment = analysis['sentiment']['news_sentiment_24h']
            if sentiment > 0.2:
                assessment['score'] += 10
                assessment['factors'].append(f"Positive news sentiment: {sentiment:.2f}")
            elif sentiment < -0.2:
                assessment['score'] -= 10
                assessment['factors'].append(f"Negative news sentiment: {sentiment:.2f}")
        
        # Financial quality
        if analysis['fundamentals'].get('quality_score'):
            quality = analysis['fundamentals']['quality_score']
            if quality > 7:
                assessment['score'] += 10
                assessment['factors'].append(f"High quality score: {quality}")
            elif quality < 3:
                assessment['score'] -= 10
                assessment['factors'].append(f"Low quality score: {quality}")
        
        # Institutional signals
        signal_count = analysis['institutional'].get('signal_count', 0)
        if signal_count > 0:
            positive_signals = sum(1 for s in analysis['institutional']['signals'] 
                                 if s['type'] in ['INSTITUTIONAL_INTEREST', 'INSIDER_BUYING', 'POSITIVE_NEWS_FLOW'])
            negative_signals = sum(1 for s in analysis['institutional']['signals'] 
                                 if s['type'] in ['NEGATIVE_NEWS_FLOW'])
            
            assessment['score'] += (positive_signals * 5)
            assessment['score'] -= (negative_signals * 5)
        
        # Final recommendation
        if assessment['score'] >= 65:
            assessment['recommendation'] = 'BULLISH'
        elif assessment['score'] <= 35:
            assessment['recommendation'] = 'BEARISH'
        else:
            assessment['recommendation'] = 'NEUTRAL'
        
        return assessment


# Global instance
premium_aggregator = PremiumDataAggregator()


if __name__ == "__main__":
    # Test the premium aggregator
    logging.basicConfig(level=logging.INFO)
    
    symbol = "AMD"
    
    print(f"\n🎯 Complete Premium Analysis for {symbol}\n")
    print("=" * 60)
    
    analysis = premium_aggregator.get_complete_analysis(symbol)
    
    print(f"\n📊 Data Sources:")
    print(f"  FMP: {'✅ Enabled' if analysis['sources_enabled']['fmp'] else '❌ Disabled'}")
    print(f"  MarketAux: {'✅ Enabled' if analysis['sources_enabled']['marketaux'] else '❌ Disabled'}")
    
    if analysis['sources_enabled']['fmp']:
        print(f"\n💰 Fundamentals:")
        fund = analysis['fundamentals']
        if fund.get('price_target_mean'):
            print(f"  Price Target: ${fund['price_target_mean']:.2f} ({fund.get('price_target_upside', 0):.1f}% upside)")
        if fund.get('eps_estimate'):
            print(f"  EPS Estimate: ${fund['eps_estimate']:.2f}")
        if fund.get('quality_score'):
            print(f"  Quality Score: {fund['quality_score']}")
    
    if analysis['sources_enabled']['marketaux']:
        print(f"\n📰 Sentiment:")
        sent = analysis['sentiment']
        if sent.get('news_sentiment_24h') is not None:
            print(f"  24h Sentiment: {sent['news_sentiment_24h']:.3f} ({sent.get('news_direction_24h', 'N/A')})")
        if sent.get('news_article_count_24h'):
            print(f"  Article Count: {sent['news_article_count_24h']}")
    
    print(f"\n🎯 Assessment:")
    assess = analysis['assessment']
    print(f"  Score: {assess['score']}/100")
    print(f"  Recommendation: {assess['recommendation']}")
    if assess['factors']:
        print(f"  Key Factors:")
        for factor in assess['factors']:
            print(f"    • {factor}")
    
    print(f"\n" + "=" * 60)
