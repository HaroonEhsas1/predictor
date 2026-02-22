#!/usr/bin/env python3
"""
ENHANCED SENTIMENT ANALYSIS SYSTEM
Multi-source sentiment analysis with intelligent fallbacks and API rate limit handling
"""

import os
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, List
import yfinance as yf
import numpy as np
from dotenv import load_dotenv

load_dotenv()


class AdvancedNLPSentimentEngine:
    """Advanced NLP-based sentiment analysis with weighted word matching"""
    
    def __init__(self):
        # Comprehensive sentiment dictionaries with weights
        self.bullish_words = {
            'strong': 0.8, 'surge': 0.8, 'rally': 0.85, 'gain': 0.7, 'rise': 0.7,
            'bullish': 0.9, 'upgrade': 0.85, 'beats': 0.9, 'growth': 0.8, 'buy': 0.75,
            'soars': 0.9, 'breakthrough': 0.85, 'profit': 0.7, 'beat': 0.9, 'outperform': 0.85,
            'accelerating': 0.8, 'positive': 0.7, 'approval': 0.85, 'approve': 0.85,
            'partnership': 0.7, 'acquisition': 0.65, 'expansion': 0.7, 'record': 0.75,
            'innovation': 0.8, 'efficient': 0.7, 'success': 0.75, 'excellent': 0.85,
            'exceptional': 0.85, 'outpace': 0.8, 'optimistic': 0.75, 'commitment': 0.6,
            'upbeat': 0.8, 'solid': 0.7, 'solid': 0.7
        }
        
        self.bearish_words = {
            'drop': 0.8, 'fall': 0.75, 'decline': 0.75, 'bearish': 0.9, 'downgrade': 0.9,
            'miss': 0.85, 'weak': 0.8, 'loss': 0.75, 'sell': 0.7, 'plunge': 0.95,
            'warning': 0.85, 'risk': 0.65, 'down': 0.7, 'concern': 0.7, 'uncertain': 0.65,
            'challenge': 0.65, 'difficult': 0.65, 'negative': 0.8, 'disappoint': 0.85,
            'recall': 0.9, 'bankruptcy': 1.0, 'fraud': 1.0, 'lawsuit': 0.9, 'crash': 0.95,
            'break': 0.75, 'falter': 0.8, 'struggle': 0.8, 'delay': 0.7,
            'underperform': 0.85, 'cutback': 0.8, 'layoff': 0.9, 'investigation': 0.85,
            'concern': 0.7, 'slump': 0.85, 'tumble': 0.85
        }
    
    def analyze_text(self, text: str) -> float:
        """Analyze text sentiment using weighted word matching"""
        if not text:
            return 0.0
        
        text_lower = text.lower()
        bull_score = 0.0
        bear_score = 0.0
        word_count = 0
        
        # Score bullish words
        for word, weight in self.bullish_words.items():
            count = text_lower.count(word)
            if count > 0:
                bull_score += count * weight
                word_count += count
        
        # Score bearish words
        for word, weight in self.bearish_words.items():
            count = text_lower.count(word)
            if count > 0:
                bear_score += count * weight
                word_count += count
        
        # Normalize sentiment (-1.0 to +1.0)
        if word_count == 0:
            return 0.0
        
        net_score = (bull_score - bear_score) / word_count
        return max(-1.0, min(1.0, net_score))  # Clamp to [-1, 1]


class EnhancedNewsAnalyzer:
    """Multi-source news sentiment with intelligent fallback logic"""
    
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.apis = {
            'finnhub': os.getenv('FINNHUB_API_KEY'),
            'marketaux': os.getenv('MARKETAUX_API_KEY'),
            'eodhd': os.getenv('EODHD_API_KEY'),
            'fmp': os.getenv('FMP_API_KEY'),
        }
        self.nlp_engine = AdvancedNLPSentimentEngine()
    
    def get_finnhub_news(self) -> Dict[str, Any]:
        """Get news from Finnhub (Primary source)"""
        if not self.apis['finnhub']:
            return None
        
        try:
            from_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            to_date = datetime.now().strftime('%Y-%m-%d')
            url = f"https://finnhub.io/api/v1/company-news?symbol={self.symbol}&from={from_date}&to={to_date}&token={self.apis['finnhub']}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                articles = response.json()[:15]
                scores = [self.nlp_engine.analyze_text(
                    article.get('headline', '') + ' ' + article.get('summary', '')
                ) for article in articles]
                
                avg_score = sum(scores) / len(scores) if scores else 0.0
                return {
                    'score': avg_score,
                    'count': len(articles),
                    'source': 'finnhub'
                }
        except Exception as e:
            print(f"   ⚠️ Finnhub error: {str(e)[:50]}")
        
        return None
    
    def get_marketaux_news(self) -> Dict[str, Any]:
        """Get news from MarketAux (Alternative source)"""
        if not self.apis['marketaux']:
            return None
        
        try:
            url = f"https://api.marketaux.com/v1/news/all?filter_entities=true&entity_types=ticker&entity_ticker={self.symbol}&limit=15&api_token={self.apis['marketaux']}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                articles = response.json().get('data', [])[:15]
                scores = []
                
                for article in articles:
                    sentiment_tag = article.get('sentiment', '').lower()
                    if sentiment_tag == 'positive':
                        score = 0.7
                    elif sentiment_tag == 'negative':
                        score = -0.7
                    else:
                        text = article.get('title', '') + ' ' + article.get('description', '')
                        score = self.nlp_engine.analyze_text(text)
                    scores.append(score)
                
                avg_score = sum(scores) / len(scores) if scores else 0.0
                return {
                    'score': avg_score,
                    'count': len(articles),
                    'source': 'marketaux'
                }
        except Exception as e:
            print(f"   ⚠️ MarketAux error: {str(e)[:50]}")
        
        return None
    
    def get_eodhd_news(self) -> Dict[str, Any]:
        """Get news from EODHD (Free alternative source)"""
        if not self.apis['eodhd']:
            return None
        
        try:
            url = f"https://eodhd.com/api/news?s={self.symbol}&limit=15&api_token={self.apis['eodhd']}&fmt=json"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                articles = data if isinstance(data, list) else data.get('data', [])
                articles = articles[:15]
                
                scores = [self.nlp_engine.analyze_text(
                    article.get('title', '') + ' ' + article.get('content', '')
                ) for article in articles]
                
                avg_score = sum(scores) / len(scores) if scores else 0.0
                return {
                    'score': avg_score,
                    'count': len(articles),
                    'source': 'eodhd'
                }
        except Exception:
            pass
        
        return None
    
    def get_yfinance_news(self) -> Dict[str, Any]:
        """Get news from YFinance (Free fallback)"""
        try:
            ticker = yf.Ticker(self.symbol)
            news = ticker.news
            
            if not news:
                return None
            
            articles = news[:15]
            scores = [self.nlp_engine.analyze_text(
                str(item.get('title', '') if isinstance(item, dict) else item)
            ) for item in articles]
            
            avg_score = sum(scores) / len(scores) if scores else 0.0
            return {
                'score': avg_score,
                'count': len(articles),
                'source': 'yfinance'
            }
        except Exception:
            pass
        
        return None
    
    def get_combined_news_sentiment(self) -> Dict[str, Any]:
        """Get sentiment from multiple sources with intelligent fallback"""
        print(f"\n📊 Fetching multi-source news sentiment for {self.symbol}...")
        
        sources = []
        
        # Try primary source
        finnhub = self.get_finnhub_news()
        if finnhub and finnhub['count'] > 0:
            sources.append(finnhub)
            print(f"   ✅ Finnhub ({finnhub['count']} articles): {finnhub['score']:+.2f}")
        
        # Try secondary sources
        marketaux = self.get_marketaux_news()
        if marketaux and marketaux['count'] > 0:
            sources.append(marketaux)
            print(f"   ✅ MarketAux ({marketaux['count']} articles): {marketaux['score']:+.2f}")
        
        # If limited data, try alternatives
        if sum(s['count'] for s in sources) < 10:
            eodhd = self.get_eodhd_news()
            if eodhd and eodhd['count'] > 0:
                sources.append(eodhd)
                print(f"   ✅ EODHD ({eodhd['count']} articles): {eodhd['score']:+.2f}")
        
        if sum(s['count'] for s in sources) < 8:
            yfinance = self.get_yfinance_news()
            if yfinance and yfinance['count'] > 0:
                sources.append(yfinance)
                print(f"   ✅ YFinance ({yfinance['count']} articles): {yfinance['score']:+.2f}")
        
        if not sources:
            print(f"   ⚠️ No news articles found")
            return {
                'overall_sentiment': 0.0,
                'article_count': 0,
                'sources': []
            }
        
        # Weighted average (by reliability)
        weights = {
            'finnhub': 0.4,
            'marketaux': 0.3,
            'eodhd': 0.2,
            'yfinance': 0.1
        }
        
        combined_score = 0.0
        total_weight = 0.0
        total_articles = 0
        
        for source in sources:
            weight = weights.get(source['source'], 0.1)
            combined_score += source['score'] * weight
            total_weight += weight
            total_articles += source['count']
        
        final_score = combined_score / total_weight if total_weight > 0 else 0.0
        print(f"   📊 Combined Score: {final_score:+.2f} (from {total_articles} articles)")
        
        return {
            'overall_sentiment': final_score,
            'article_count': total_articles,
            'sources': sources
        }


class EnhancedEconomicAnalyzer:
    """Economic context analyzer with VIX and rate data fallbacks"""
    
    def __init__(self):
        self.fred_key = os.getenv('FRED_API_KEY')
        self.nlp_engine = AdvancedNLPSentimentEngine()
    
    def get_vix_fred(self) -> Dict[str, Any]:
        """Get VIX from FRED"""
        if not self.fred_key:
            return None
        
        try:
            url = f"https://api.stlouisfed.org/fred/series/data?series_id=VIXCLS&api_key={self.fred_key}&file_type=json&limit=1"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                obs = response.json().get('observations', [])
                if obs:
                    vix = float(obs[-1]['value'])
                    return {'vix': vix, 'source': 'fred'}
        except Exception:
            pass
        
        return None
    
    def get_vix_yfinance(self) -> Dict[str, Any]:
        """Get VIX from YFinance"""
        try:
            vix_ticker = yf.Ticker('^VIX')
            hist = vix_ticker.history(period='1d')
            if len(hist) > 0:
                vix = hist['Close'].iloc[-1]
                return {'vix': vix, 'source': 'yfinance'}
        except Exception:
            pass
        
        return None
    
    def get_economic_sentiment(self) -> Dict[str, Any]:
        """Get VIX-based economic sentiment"""
        print(f"\n🌍 Economic Context:")
        
        # Try to get VIX
        vix_data = self.get_vix_fred()
        if not vix_data:
            vix_data = self.get_vix_yfinance()
        
        if vix_data:
            vix = vix_data['vix']
            source = vix_data['source']
            print(f"   ✅ VIX ({source}): {vix:.1f}")
            
            # VIX sentiment: higher = fear = bearish
            if vix > 25:
                sentiment = -0.3
                signal = 'HIGH_FEAR'
            elif vix > 20:
                sentiment = -0.15
                signal = 'ELEVATED_VIX'
            elif vix < 12:
                sentiment = 0.3
                signal = 'LOW_VOLATILITY'
            else:
                sentiment = 0.0
                signal = 'NORMAL'
            
            return {
                'overall_sentiment': sentiment,
                'vix': vix,
                'signal': signal
            }
        else:
            print(f"   ⚠️ VIX data unavailable")
            return {
                'overall_sentiment': 0.0,
                'vix': 20.0,
                'signal': 'UNAVAILABLE'
            }
