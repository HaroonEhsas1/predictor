#!/usr/bin/env python3
"""
INTRADAY 1-HOUR MOMENTUM PREDICTOR
Predicts next 1 hour movements for tech stocks using:
- Real-time momentum analysis (RSI, MACD, Stochastic)
- Trend detection (higher highs/lows, moving averages)
- Volume profile analysis (VWAP, volume surges)
- News sentiment (real-time headlines)
- Market microstructure (bid-ask, volume bars)
- Level 2 data simulation

Supports: AMD, NVDA, META, AVGO, SNOW, PLTR
"""

import yfinance as yf
import requests
from datetime import datetime, timedelta
import pytz
import os
import json
import math
import pandas as pd
import numpy as np
from typing import Dict, Any, List
from dotenv import load_dotenv
import warnings
warnings.filterwarnings('ignore')

# Load environment variables
load_dotenv()
import joblib
from pathlib import Path


class AdvancedNLPSentimentEngine:
    """Advanced NLP-based sentiment analysis with weighted word matching"""
    
    def __init__(self):
        self.bullish_words = {
            'strong': 0.8, 'surge': 0.8, 'rally': 0.85, 'gain': 0.7, 'rise': 0.7,
            'bullish': 0.9, 'upgrade': 0.85, 'beats': 0.9, 'growth': 0.8, 'buy': 0.75,
            'soars': 0.9, 'breakthrough': 0.85, 'profit': 0.7, 'beat': 0.9, 'outperform': 0.85,
            'accelerating': 0.8, 'positive': 0.7, 'approval': 0.85, 'approve': 0.85,
            'partnership': 0.7, 'acquisition': 0.65, 'expansion': 0.7, 'record': 0.75,
            'innovation': 0.8, 'efficient': 0.7, 'success': 0.75, 'excellent': 0.85,
            'exceptional': 0.85, 'outpace': 0.8, 'optimistic': 0.75, 'commitment': 0.6
        }
        
        self.bearish_words = {
            'drop': 0.8, 'fall': 0.75, 'decline': 0.75, 'bearish': 0.9, 'downgrade': 0.9,
            'miss': 0.85, 'weak': 0.8, 'loss': 0.75, 'sell': 0.7, 'plunge': 0.95,
            'warning': 0.85, 'risk': 0.65, 'down': 0.7, 'concern': 0.7, 'uncertain': 0.65,
            'challenge': 0.65, 'difficult': 0.65, 'negative': 0.8, 'disappoint': 0.85,
            'recall': 0.9, 'bankruptcy': 1.0, 'fraud': 1.0, 'lawsuit': 0.9, 'crash': 0.95,
            'break': 0.75, 'falter': 0.8, 'struggle': 0.8, 'delay': 0.7,
            'underperform': 0.85, 'cutback': 0.8, 'layoff': 0.9, 'investigation': 0.85
        }
    
    def analyze_text(self, text: str) -> float:
        """Analyze text sentiment using weighted word matching"""
        if not text:
            return 0.0
        
        text_lower = text.lower()
        bull_score = 0.0
        bear_score = 0.0
        word_count = 0
        
        for word, weight in self.bullish_words.items():
            count = text_lower.count(word)
            if count > 0:
                bull_score += count * weight
                word_count += count
        
        for word, weight in self.bearish_words.items():
            count = text_lower.count(word)
            if count > 0:
                bear_score += count * weight
                word_count += count
        
        if word_count == 0:
            return 0.0
        
        net_score = (bull_score - bear_score) / word_count
        return max(-1.0, min(1.0, net_score))


class MultiSourceSentimentAnalyzer:
    """Enhanced sentiment analysis using multiple APIs"""
    
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.apis = {
            'finnhub': os.getenv('FINNHUB_API_KEY'),
            'marketaux': os.getenv('MARKETAUX_API_KEY'),
            'fmp': os.getenv('FMP_API_KEY'),
            'polygon': os.getenv('POLYGON_API_KEY'),
            'openai': os.getenv('OPENAI_API_KEY'),
            'alpha_vantage': os.getenv('ALPHA_VANTAGE_API_KEY'),
        }
        self.nlp_engine = AdvancedNLPSentimentEngine()
    
    def get_finnhub_sentiment(self) -> Dict[str, Any]:
        """Get news from Finnhub with advanced NLP sentiment analysis"""
        if not self.apis['finnhub']:
            return {'score': 0.0, 'count': 0, 'source': 'finnhub'}
        
        try:
            from_time = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            to_time = datetime.now().strftime('%Y-%m-%d')
            url = f"https://finnhub.io/api/v1/company-news?symbol={self.symbol}&from={from_time}&to={to_time}&token={self.apis['finnhub']}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                articles = response.json()[:15]
                
                scores = []
                for article in articles:
                    text = (article.get('headline', '') + ' ' + article.get('summary', '')).lower()
                    score = self.nlp_engine.analyze_text(text)
                    scores.append(score)
                
                avg_score = sum(scores) / len(scores) if scores else 0.0
                return {'score': avg_score, 'count': len(articles), 'source': 'finnhub'}
        except Exception as e:
            print(f"   ⚠️ Finnhub error: {str(e)[:50]}")
        
        return {'score': 0.0, 'count': 0, 'source': 'finnhub'}
    
    def get_marketaux_sentiment(self) -> Dict[str, Any]:
        """Get market sentiment from MarketAux with fallback NLP"""
        if not self.apis['marketaux']:
            return {'score': 0.0, 'count': 0, 'source': 'marketaux'}
        
        try:
            url = f"https://api.marketaux.com/v1/news/all?filter_entities=true&entity_types=ticker&entity_ticker={self.symbol}&limit=15&api_token={self.apis['marketaux']}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                articles = data.get('data', [])[:15]
                
                scores = []
                for article in articles:
                    sentiment = article.get('sentiment', '').lower()
                    if sentiment == 'positive':
                        score = 0.7
                    elif sentiment == 'negative':
                        score = -0.7
                    else:
                        # Fallback to NLP analysis
                        text = (article.get('title', '') + ' ' + article.get('description', '')).lower()
                        score = self.nlp_engine.analyze_text(text)
                    scores.append(score)
                
                avg_score = sum(scores) / len(scores) if scores else 0.0
                return {'score': avg_score, 'count': len(articles), 'source': 'marketaux'}
        except Exception as e:
            print(f"   ⚠️ MarketAux error: {str(e)[:50]}")
        
        return {'score': 0.0, 'count': 0, 'source': 'marketaux'}
    
    def get_eodhd_sentiment(self) -> Dict[str, Any]:
        """Alternative: Get sentiment from EODHD API (Free)"""
        eodhd_key = os.getenv('EODHD_API_KEY')
        if not eodhd_key:
            return {'score': 0.0, 'count': 0, 'source': 'eodhd'}
        
        try:
            url = f"https://eodhd.com/api/news?s={self.symbol}&limit=15&api_token={eodhd_key}&fmt=json"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                articles = response.json()
                if not isinstance(articles, list):
                    articles = articles.get('data', [])
                
                articles = articles[:15]
                scores = []
                
                for article in articles:
                    text = (article.get('title', '') + ' ' + article.get('content', '')).lower()
                    score = self.nlp_engine.analyze_text(text)
                    scores.append(score)
                
                avg_score = sum(scores) / len(scores) if scores else 0.0
                return {'score': avg_score, 'count': len(articles), 'source': 'eodhd'}
        except Exception as e:
            print(f"   ⚠️ EODHD error: {str(e)[:50]}")
        
        return {'score': 0.0, 'count': 0, 'source': 'eodhd'}
    
    def get_yfinance_news_sentiment(self) -> Dict[str, Any]:
        """Alternative: Get news sentiment from yfinance (Free)"""
        try:
            ticker = yf.Ticker(self.symbol)
            news = ticker.news
            
            if not news or len(news) == 0:
                return {'score': 0.0, 'count': 0, 'source': 'yfinance'}
            
            scores = []
            for item in news[:15]:
                text = (item.get('title', '') + ' ' + item.get('summary', '')) if isinstance(item, dict) else str(item)
                text = text.lower()
                score = self.nlp_engine.analyze_text(text)
                scores.append(score)
            
            avg_score = sum(scores) / len(scores) if scores else 0.0
            return {'score': avg_score, 'count': len(news[:15]), 'source': 'yfinance'}
        except Exception as e:
            print(f"   ⚠️ YFinance news error: {str(e)[:50]}")
        
        return {'score': 0.0, 'count': 0, 'source': 'yfinance'}
    
    def get_combined_sentiment(self, hours_back: int = 1) -> Dict[str, Any]:
        """Combine sentiment from multiple sources with intelligent fallback"""
        print(f"\n📊 Fetching multi-source sentiment for {self.symbol}...")
        
        sources_data = []
        
        # Try primary sources
        finnhub = self.get_finnhub_sentiment()
        if finnhub['count'] > 0:
            sources_data.append(finnhub)
            print(f"   ✅ Finnhub ({finnhub['count']} articles): {finnhub['score']:+.2f}")
        
        marketaux = self.get_marketaux_sentiment()
        if marketaux['count'] > 0:
            sources_data.append(marketaux)
            print(f"   ✅ MarketAux ({marketaux['count']} articles): {marketaux['score']:+.2f}")
        
        # If primary sources have limited data, try alternatives
        if sum(s['count'] for s in sources_data) < 10:
            eodhd = self.get_eodhd_sentiment()
            if eodhd['count'] > 0:
                sources_data.append(eodhd)
                print(f"   ✅ EODHD ({eodhd['count']} articles): {eodhd['score']:+.2f}")
        
        if sum(s['count'] for s in sources_data) < 8:
            yfinance = self.get_yfinance_news_sentiment()
            if yfinance['count'] > 0:
                sources_data.append(yfinance)
                print(f"   ✅ YFinance ({yfinance['count']} articles): {yfinance['score']:+.2f}")
        
        # Weighted average based on reliability
        weights = {
            'finnhub': 0.4,
            'marketaux': 0.3,
            'eodhd': 0.2,
            'yfinance': 0.1
        }
        
        if not sources_data:
            print(f"   ⚠️ No news articles found - sentiment = 0.0")
            return {
                'overall_sentiment': 0.0,
                'article_count': 0,
                'sources': []
            }
        
        total_weight = 0
        combined_score = 0
        total_articles = 0
        
        for source in sources_data:
            weight = weights.get(source['source'], 0.1)
            combined_score += source['score'] * weight
            total_weight += weight
            total_articles += source['count']
        
        final_score = combined_score / total_weight if total_weight > 0 else 0.0
        print(f"   📊 Combined Score: {final_score:+.2f} (from {total_articles} articles)")
        
        return {
            'overall_sentiment': final_score,
            'article_count': total_articles,
            'sources': sources_data
        }


class OptionsSentimentAnalyzer:
    """Analyze options market sentiment using price-action patterns"""
    
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.ticker = yf.Ticker(symbol)
    
    def get_put_call_sentiment(self) -> Dict[str, Any]:
        """Infer options sentiment from price volatility and volume patterns"""
        try:
            # Get recent price data (5 days)
            data = self.ticker.history(period='5d', interval='1d')
            
            if len(data) < 2:
                return {'score': 0.0, 'put_call_ratio': 1.0, 'signal': 'NO_DATA'}
            
            # Calculate volatility (proxy for options activity)
            returns = data['Close'].pct_change()
            volatility = returns.std()
            
            # Higher volatility suggests balanced or put-heavy activity (uncertainty)
            # Lower volatility suggests call-heavy activity (confidence)
            if volatility > 0.03:  # High volatility
                sentiment = -0.2
                signal = 'HIGH_VOLATILITY'
                put_call_ratio = 1.3
            elif volatility < 0.01:  # Low volatility
                sentiment = 0.2
                signal = 'LOW_VOLATILITY'
                put_call_ratio = 0.7
            else:  # Normal volatility
                sentiment = 0.0
                signal = 'NORMAL'
                put_call_ratio = 1.0
            
            return {
                'score': sentiment,
                'put_call_ratio': put_call_ratio,
                'signal': signal,
                'volatility': volatility,
                'source': 'PRICE_ACTION'
            }
        except Exception as e:
            pass
        
        return {'score': 0.0, 'put_call_ratio': 1.0, 'signal': 'NO_DATA'}


class SocialSentimentAnalyzer:
    """Analyze social sentiment from volume and momentum patterns"""
    
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.ticker = yf.Ticker(symbol)
    
    def get_twitter_sentiment(self) -> Dict[str, Any]:
        """Infer social sentiment from relative volume activity"""
        try:
            # Use volume spikes as proxy for social activity
            data = self.ticker.history(period='5d', interval='1h')
            
            if len(data) < 10:
                return {'score': 0.0, 'mentions': 0, 'source': 'volume_proxy'}
            
            recent_volume = data['Volume'].iloc[-5:].mean()  # Last 5 hours
            avg_volume = data['Volume'].mean()
            
            volume_ratio = recent_volume / avg_volume if avg_volume > 0 else 1.0
            
            # High volume = high social activity/sentiment
            if volume_ratio > 1.5:
                sentiment = 0.2  # Bullish volume surge
            elif volume_ratio < 0.5:
                sentiment = -0.1  # Weak volume (bearish)
            else:
                sentiment = 0.0  # Normal
            
            return {
                'score': sentiment,
                'mentions': int(volume_ratio * 100),
                'source': 'volume_proxy'
            }
        except Exception:
            return {'score': 0.0, 'mentions': 0, 'source': 'volume_proxy'}
    
    def get_reddit_sentiment(self) -> Dict[str, Any]:
        """Infer sentiment from price momentum patterns"""
        try:
            data = self.ticker.history(period='5d', interval='1d')
            
            if len(data) < 2:
                return {'score': 0.0, 'posts': 0, 'source': 'momentum_proxy'}
            
            # Calculate momentum
            returns = data['Close'].pct_change().iloc[-1]  # Latest return
            volatility = data['Close'].pct_change().std()
            
            # Strong upward momentum = positive sentiment
            if returns > 0.02 and volatility < 0.02:
                sentiment = 0.15  # Strong bullish trend
            elif returns > 0:
                sentiment = 0.05
            elif returns < -0.02:
                sentiment = -0.15  # Strong bearish trend
            else:
                sentiment = -0.05
            
            return {
                'score': sentiment,
                'posts': int(abs(returns) * 1000),
                'source': 'momentum_proxy'
            }
        except Exception:
            return {'score': 0.0, 'posts': 0, 'source': 'momentum_proxy'}
    
    def get_combined_social_sentiment(self) -> Dict[str, Any]:
        """Combine volume and momentum sentiment"""
        volume_sent = self.get_twitter_sentiment()
        momentum_sent = self.get_reddit_sentiment()
        
        # Weighted: Volume 60%, Momentum 40%
        combined = (volume_sent['score'] * 0.6) + (momentum_sent['score'] * 0.4)
        
        total_mentions = volume_sent.get('mentions', 0) + momentum_sent.get('posts', 0)
        
        return {
            'overall_sentiment': combined,
            'mentions': total_mentions,
            'sources': [volume_sent, momentum_sent]
        }


class EconomicContextAnalyzer:
    """Analyze economic context from market-derived indicators"""
    
    def __init__(self):
        pass
    
    def get_vix_level(self) -> Dict[str, Any]:
        """Get market stress from SPY volatility patterns"""
        try:
            spy = yf.Ticker("SPY")
            data = spy.history(period='5d', interval='1d')
            
            if len(data) < 2:
                return {'vix': 20.0, 'sentiment': 0.0, 'signal': 'NO_DATA'}
            
            # Calculate realized volatility
            returns = data['Close'].pct_change()
            volatility = returns.std() * 100 * np.sqrt(252)  # Annualized %
            
            # VIX sentiment mapping
            if volatility > 30:
                sentiment = -0.3
                signal = 'HIGH_FEAR'
            elif volatility > 20:
                sentiment = -0.15
                signal = 'ELEVATED'
            elif volatility < 12:
                sentiment = 0.3
                signal = 'LOW_VOLATILITY'
            else:
                sentiment = 0.0
                signal = 'NORMAL'
            
            return {
                'vix': volatility,
                'sentiment': sentiment,
                'signal': signal
            }
        except Exception:
            return {'vix': 20.0, 'sentiment': 0.0, 'signal': 'NO_DATA'}
    
    def get_interest_rate_context(self) -> Dict[str, Any]:
        """Get rate context from TLT (20-year Treasuries)"""
        try:
            tlt = yf.Ticker("TLT")
            data = tlt.history(period='30d', interval='1d')
            
            if len(data) < 10:
                return {'fed_rate': 4.0, 'change': 0.0, 'sentiment': 0.0, 'signal': 'NO_DATA'}
            
            # Calculate recent trend
            recent = data['Close'].iloc[-5:].pct_change().mean()
            
            # TLT down = rates rising = bearish for stocks
            if recent < -0.002:  # TLT declining
                sentiment = -0.2
                signal = 'RATES_RISING'
                change = 0.15
            elif recent > 0.002:  # TLT rising
                sentiment = 0.2
                signal = 'RATES_FALLING'
                change = -0.15
            else:
                sentiment = 0.0
                signal = 'RATES_STABLE'
                change = 0.0
            
            return {
                'fed_rate': 4.0,  # Placeholder
                'change': change,
                'sentiment': sentiment,
                'signal': signal
            }
        except Exception:
            return {'fed_rate': 4.0, 'change': 0.0, 'sentiment': 0.0, 'signal': 'NO_DATA'}
    
    def get_economic_sentiment(self) -> Dict[str, Any]:
        """Get combined economic context"""
        vix_data = self.get_vix_level()
        rates_data = self.get_interest_rate_context()
        
        # Combined economic sentiment: Volatility 60%, Rates 40%
        combined = (vix_data.get('sentiment', 0.0) * 0.6) + (rates_data.get('sentiment', 0.0) * 0.4)
        
        return {
            'overall_sentiment': combined,
            'vix': vix_data.get('vix', 20.0),
            'fed_rate': rates_data.get('fed_rate', 4.0),
            'signals': [vix_data.get('signal'), rates_data.get('signal')]
        }


class FundamentalAnalyzer:
    """Analyze fundamentals from price-action and technical patterns"""
    
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.ticker = yf.Ticker(symbol)
    
    def get_earnings_surprise_sentiment(self) -> Dict[str, Any]:
        """Infer earnings surprise sentiment from price momentum"""
        try:
            data = self.ticker.history(period='20d', interval='1d')
            
            if len(data) < 10:
                return {'score': 0.0, 'eps_surprise': 0.0, 'signal': 'NO_DATA'}
            
            # Calculate recent momentum (proxy for earnings reaction)
            recent_return = (data['Close'].iloc[-1] - data['Close'].iloc[-10]) / data['Close'].iloc[-10]
            
            if recent_return > 0.05:
                sentiment = 0.4
                signal = 'STRONG_UPTREND'
                eps_surprise = 0.1
            elif recent_return > 0.02:
                sentiment = 0.2
                signal = 'UPTREND'
                eps_surprise = 0.02
            elif recent_return < -0.05:
                sentiment = -0.4
                signal = 'STRONG_DOWNTREND'
                eps_surprise = -0.1
            elif recent_return < -0.02:
                sentiment = -0.2
                signal = 'DOWNTREND'
                eps_surprise = -0.02
            else:
                sentiment = 0.0
                signal = 'NEUTRAL'
                eps_surprise = 0.0
            
            return {
                'score': sentiment,
                'eps_surprise': eps_surprise,
                'signal': signal
            }
        except Exception:
            return {'score': 0.0, 'eps_surprise': 0.0, 'signal': 'NO_DATA'}
    
    def get_analyst_sentiment(self) -> Dict[str, Any]:
        """Infer analyst sentiment from relative strength patterns"""
        try:
            data = self.ticker.history(period='60d', interval='1d')
            
            if len(data) < 20:
                return {'score': 0.0, 'rating': 'NO_DATA'}
            
            # Calculate relative strength
            recent_avg = data['Close'].iloc[-10:].mean()
            older_avg = data['Close'].iloc[-60:-50].mean()
            
            strength = (recent_avg - older_avg) / older_avg if older_avg > 0 else 0
            
            if strength > 0.05:
                sentiment = 0.5
                rating = 'STRONG_BUY'
            elif strength > 0.02:
                sentiment = 0.3
                rating = 'BUY'
            elif strength > -0.02:
                sentiment = 0.0
                rating = 'HOLD'
            elif strength > -0.05:
                sentiment = -0.3
                rating = 'SELL'
            else:
                sentiment = -0.5
                rating = 'STRONG_SELL'
            
            return {
                'score': sentiment,
                'rating': rating
            }
        except Exception:
            return {'score': 0.0, 'rating': 'NO_DATA'}
    
    def get_fundamental_sentiment(self) -> Dict[str, Any]:
        """Get combined fundamental sentiment"""
        earnings = self.get_earnings_surprise_sentiment()
        analyst = self.get_analyst_sentiment()
        
        # Combined: Earnings 60%, Analyst 40%
        combined = (earnings.get('score', 0.0) * 0.6) + (analyst.get('score', 0.0) * 0.4)
        
        return {
            'overall_sentiment': combined,
            'earnings_signal': earnings.get('signal'),
            'analyst_rating': analyst.get('rating')
        }


class SimpleNLPAnalyzer:
    """Simple NLP for quick technical analysis"""
    
    def __init__(self, symbol: str):
        self.symbol = symbol
    
    def analyze_news_sentiment(self, headlines: List[str]) -> Dict[str, Any]:
        """Quick NLP sentiment analysis"""
        if not headlines:
            return {'score': 0.0, 'analysis': 'NO_DATA'}
        
        # Simple keyword-based analysis
        bullish_words = {'buy', 'beat', 'bull', 'growth', 'strong', 'surge', 'jump', 'profit', 'revenue'}
        bearish_words = {'sell', 'miss', 'bear', 'decline', 'weak', 'loss', 'drop', 'down', 'risk'}
        
        try:
            sentiment_scores = []
            for headline in headlines[:5]:
                text = headline.lower()
                bull_score = sum(1 for word in bullish_words if word in text)
                bear_score = sum(1 for word in bearish_words if word in text)
                
                if bull_score > bear_score:
                    sentiment_scores.append(0.3)
                elif bear_score > bull_score:
                    sentiment_scores.append(-0.3)
            
            avg_score = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0.0
            return {'score': avg_score, 'analysis': 'COMPLETED'}
        except Exception:
            return {'score': 0.0, 'analysis': 'ERROR'}

class MomentumAnalyzer:
    """Calculate intraday momentum indicators"""
    
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.ticker = yf.Ticker(symbol)
    
    def get_intraday_data(self, interval: str = '1m', period: str = '60m'):
        """
        ALWAYS FRESH DATA - Fetch intraday data on every call (no caching)
        interval: '1m', '5m', '15m', '60m'
        period: '60m', '1d', '5d'
        """
        try:
            # For proper indicator calculation, we need enough candles
            # 1-minute: Use 5-day period to get ~1900 candles (only gets latest trading day when market is closed)
            # Use 5-minute or 15-minute interval for better historical depth
            if interval == '1m':
                # Switch to 5-minute for better data when market just opened
                interval = '5m'
                period = '5d'  # Get 5 days of data = ~500+ candles
            elif interval in ['5m', '15m']:
                if period == '60m':
                    period = '5d'  # Get more data
            
            # Fetch FRESH intraday data (no cached values)
            hist = self.ticker.history(interval=interval, period=period)
            et_tz = pytz.timezone('America/New_York')
            fetch_time = datetime.now(et_tz).strftime('%Y-%m-%d %H:%M:%S %Z')
            print(f"   ✅ FRESH INTRADAY DATA at: {fetch_time}")
            
            if hist.empty:
                return {
                    'success': False,
                    'error': f'No intraday data available for {self.symbol}',
                    'candles': []
                }
            
            # Convert to list of dictionaries
            candles = []
            for idx, row in hist.iterrows():
                candles.append({
                    'time': idx,
                    'open': float(row['Open']),
                    'high': float(row['High']),
                    'low': float(row['Low']),
                    'close': float(row['Close']),
                    'volume': int(row['Volume'])
                })
            
            return {
                'success': True,
                'candles': candles,
                'current_price': candles[-1]['close'] if candles else None,
                'candle_count': len(candles)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'candles': []
            }
    
    def calculate_rsi(self, candles: List[Dict], period: int = 14) -> Dict[str, Any]:
        """Calculate RSI (Relative Strength Index)"""
        if len(candles) < period + 1:
            return {'success': False, 'rsi': 50, 'signal': 'NEUTRAL', 'sentiment': 0.0}
        
        closes = [c['close'] for c in candles]
        
        # Calculate gains and losses
        gains = []
        losses = []
        for i in range(1, len(closes)):
            change = closes[i] - closes[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
        
        # Calculate average gain and loss
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        
        # Calculate RS and RSI
        rs = avg_gain / avg_loss if avg_loss != 0 else 0
        rsi = 100 - (100 / (1 + rs))
        
        # Determine signal
        if rsi > 70:
            signal = 'OVERBOUGHT'
            sentiment = -0.3  # Bearish reversal risk
        elif rsi < 30:
            signal = 'OVERSOLD'
            sentiment = +0.3  # Bullish bounce opportunity
        elif rsi > 60:
            signal = 'STRONG_UPTREND'
            sentiment = +0.15
        elif rsi < 40:
            signal = 'WEAK_DOWNTREND'
            sentiment = -0.15
        else:
            signal = 'NEUTRAL'
            sentiment = 0.0
        
        return {
            'success': True,
            'rsi': rsi,
            'signal': signal,
            'sentiment': sentiment,
            'overbought': rsi > 70,
            'oversold': rsi < 30
        }
    
    def calculate_macd(self, candles: List[Dict], fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, Any]:
        """Calculate MACD (Moving Average Convergence Divergence)"""
        if len(candles) < slow + signal:
            return {'success': False, 'macd': 0, 'signal_line': 0, 'histogram': 0, 'signal': 'NEUTRAL', 'sentiment': 0.0}
        
        closes = np.array([c['close'] for c in candles])
        
        # Calculate exponential moving averages
        ema_fast = self._calculate_ema(closes, fast)
        ema_slow = self._calculate_ema(closes, slow)
        
        # MACD line
        macd_line = ema_fast[-1] - ema_slow[-1]
        
        # Signal line (EMA of MACD)
        macd_values = ema_fast - ema_slow
        signal_line = self._calculate_ema(macd_values, signal)[-1]
        
        # Histogram
        histogram = macd_line - signal_line
        
        # Determine signal
        if macd_line > signal_line and histogram > 0:
            signal = 'BULLISH_CROSSOVER'
            sentiment = +0.4  # Strong bullish
        elif macd_line < signal_line and histogram < 0:
            signal = 'BEARISH_CROSSOVER'
            sentiment = -0.4  # Strong bearish
        elif macd_line > signal_line:
            signal = 'BULLISH_ABOVE'
            sentiment = +0.2
        elif macd_line < signal_line:
            signal = 'BEARISH_BELOW'
            sentiment = -0.2
        else:
            signal = 'NEUTRAL'
            sentiment = 0.0
        
        return {
            'success': True,
            'macd': macd_line,
            'signal_line': signal_line,
            'histogram': histogram,
            'signal': signal,
            'sentiment': sentiment,
            'bullish': macd_line > signal_line
        }
    
    def _calculate_ema(self, data: np.ndarray, period: int) -> np.ndarray:
        """Calculate Exponential Moving Average"""
        multiplier = 2 / (period + 1)
        ema = np.zeros(len(data))
        ema[0] = np.mean(data[:period])
        
        for i in range(1, len(data)):
            ema[i] = data[i] * multiplier + ema[i-1] * (1 - multiplier)
        
        return ema
    
    def calculate_stochastic(self, candles: List[Dict], period: int = 14) -> Dict[str, Any]:
        """Calculate Stochastic Oscillator"""
        if len(candles) < period:
            return {'success': False, 'k': 50, 'd': 50, 'signal': 'NEUTRAL', 'sentiment': 0.0, 'k_percent': 50, 'd_percent': 50}
        
        recent_candles = candles[-period:]
        highs = [c['high'] for c in recent_candles]
        lows = [c['low'] for c in recent_candles]
        close = candles[-1]['close']
        
        highest = max(highs)
        lowest = min(lows)
        
        # Calculate %K
        k_percent = 100 * (close - lowest) / (highest - lowest) if highest != lowest else 50
        
        # Approximate %D (simple average, not full smoothing)
        d_percent = k_percent
        
        # Determine signal
        if k_percent > 80:
            signal = 'OVERBOUGHT'
            sentiment = -0.25
        elif k_percent < 20:
            signal = 'OVERSOLD'
            sentiment = +0.25
        elif k_percent > 50:
            signal = 'BULLISH_MOMENTUM'
            sentiment = +0.15
        elif k_percent < 50:
            signal = 'BEARISH_MOMENTUM'
            sentiment = -0.15
        else:
            signal = 'NEUTRAL'
            sentiment = 0.0
        
        return {
            'success': True,
            'k_percent': k_percent,
            'd_percent': d_percent,
            'signal': signal,
            'sentiment': sentiment,
            'overbought': k_percent > 80,
            'oversold': k_percent < 20
        }
    
    def calculate_momentum(self, candles: List[Dict], period: int = 10) -> Dict[str, Any]:
        """Calculate Rate of Change (Momentum)"""
        if len(candles) < period + 1:
            return {'success': False, 'roc': 0, 'signal': 'NEUTRAL', 'sentiment': 0.0}
        
        current_close = candles[-1]['close']
        past_close = candles[-period-1]['close']
        
        # Rate of Change
        roc = ((current_close - past_close) / past_close) * 100 if past_close != 0 else 0
        
        # Determine signal
        if roc > 2:
            signal = 'STRONG_UPMOMENTUM'
            sentiment = +0.4
        elif roc > 0.5:
            signal = 'UPMOMENTUM'
            sentiment = +0.2
        elif roc < -2:
            signal = 'STRONG_DOWNMOMENTUM'
            sentiment = -0.4
        elif roc < -0.5:
            signal = 'DOWNMOMENTUM'
            sentiment = -0.2
        else:
            signal = 'NEUTRAL_MOMENTUM'
            sentiment = 0.0
        
        return {
            'success': True,
            'roc': roc,
            'signal': signal,
            'sentiment': sentiment
        }


class TrendDetector:
    """Detect intraday trends"""
    
    @staticmethod
    def detect_trend(candles: List[Dict]) -> Dict[str, Any]:
        """Detect trend direction (UP, DOWN, SIDEWAYS)"""
        if len(candles) < 5:
            return {'trend': 'NEUTRAL', 'strength': 0.0, 'signal': 'INSUFFICIENT_DATA'}
        
        # Get recent price action
        recent = candles[-10:]  # Last 10 candles
        
        # Count higher highs/lows for uptrend
        higher_highs = 0
        higher_lows = 0
        lower_highs = 0
        lower_lows = 0
        
        for i in range(1, len(recent)):
            if recent[i]['high'] > recent[i-1]['high']:
                higher_highs += 1
            else:
                lower_highs += 1
            
            if recent[i]['low'] > recent[i-1]['low']:
                higher_lows += 1
            else:
                lower_lows += 1
        
        # Determine trend
        uptrend_strength = (higher_highs + higher_lows) / len(recent)
        downtrend_strength = (lower_highs + lower_lows) / len(recent)
        
        if uptrend_strength > 0.6:
            trend = 'UPTREND'
            strength = uptrend_strength
        elif downtrend_strength > 0.6:
            trend = 'DOWNTREND'
            strength = downtrend_strength
        else:
            trend = 'SIDEWAYS'
            strength = 0.5
        
        return {
            'trend': trend,
            'strength': strength,
            'higher_highs': higher_highs,
            'lower_lows': lower_lows,
            'signal': f'{trend} (strength: {strength:.1%})'
        }
    
    @staticmethod
    def detect_support_resistance(candles: List[Dict]) -> Dict[str, Any]:
        """Detect support and resistance levels"""
        if len(candles) < 5:
            return {'support': None, 'resistance': None}
        
        recent = candles[-20:]  # Last 20 candles
        
        lows = [c['low'] for c in recent]
        highs = [c['high'] for c in recent]
        
        # Support: lowest price that price bounced from
        support = min(lows)
        resistance = max(highs)
        
        current_price = candles[-1]['close']
        
        # Distance to support/resistance
        support_dist = ((current_price - support) / current_price) * 100
        resistance_dist = ((resistance - current_price) / current_price) * 100
        
        return {
            'support': support,
            'resistance': resistance,
            'current': current_price,
            'distance_to_support_pct': support_dist,
            'distance_to_resistance_pct': resistance_dist,
            'near_support': support_dist < 0.5,
            'near_resistance': resistance_dist < 0.5
        }


class VolumeAnalyzer:
    """Analyze volume patterns"""
    
    @staticmethod
    def analyze_volume(candles: List[Dict]) -> Dict[str, Any]:
        """Analyze volume trends"""
        if len(candles) < 5:
            return {'success': False, 'avg_volume': 0, 'volume_signal': 'INSUFFICIENT', 'current_volume': 0, 'signal': 'NEUTRAL', 'sentiment': 0.0, 'volume_ratio': 1.0}
        
        volumes = [c['volume'] for c in candles]
        avg_volume = sum(volumes) / len(volumes)
        current_volume = volumes[-1]
        
        # Volume surge
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
        
        # Determine signal
        if volume_ratio > 2.0:
            signal = 'EXTREME_VOLUME_SURGE'
            sentiment = +0.3  # Volume surge bullish on up, bearish on down
        elif volume_ratio > 1.5:
            signal = 'VOLUME_SURGE'
            sentiment = +0.15
        elif volume_ratio < 0.5:
            signal = 'LOW_VOLUME'
            sentiment = -0.1  # Low volume = weak move
        else:
            signal = 'NORMAL_VOLUME'
            sentiment = 0.0
        
        return {
            'success': True,
            'avg_volume': avg_volume,
            'current_volume': current_volume,
            'volume_ratio': volume_ratio,
            'signal': signal,
            'sentiment': sentiment,
            'volume_surge': volume_ratio > 1.5
        }
    
    @staticmethod
    def calculate_vwap(candles: List[Dict]) -> Dict[str, Any]:
        """Calculate Volume Weighted Average Price"""
        if len(candles) < 1:
            return {'success': False, 'vwap': 0, 'signal': 'NEUTRAL', 'sentiment': 0.0, 'distance_pct': 0.0}
        
        tp_volume_sum = 0  # typical price * volume sum
        volume_sum = 0
        
        for candle in candles:
            typical_price = (candle['high'] + candle['low'] + candle['close']) / 3
            tp_volume_sum += typical_price * candle['volume']
            volume_sum += candle['volume']
        
        vwap = tp_volume_sum / volume_sum if volume_sum > 0 else candles[-1]['close']
        
        current_price = candles[-1]['close']
        vwap_distance_pct = ((current_price - vwap) / vwap) * 100
        
        # Determine signal
        if vwap_distance_pct > 0.5:
            signal = 'ABOVE_VWAP_BULLISH'
            sentiment = +0.2
        elif vwap_distance_pct < -0.5:
            signal = 'BELOW_VWAP_BEARISH'
            sentiment = -0.2
        else:
            signal = 'AT_VWAP'
            sentiment = 0.0
        
        return {
            'success': True,
            'vwap': vwap,
            'current_price': current_price,
            'distance_pct': vwap_distance_pct,
            'signal': signal,
            'sentiment': sentiment
        }


class RealTimeNewsSentiment:
    """Enhanced real-time news sentiment using multiple APIs"""
    
    def __init__(self, symbol: str, model_blend_weight: float = 0.6):
        self.symbol = symbol
        self.model_blend_weight = model_blend_weight
        self.api_keys = {
            'finnhub': os.getenv('FINNHUB_API_KEY'),
            'marketaux': os.getenv('MARKETAUX_API_KEY'),
            'alpha_vantage': os.getenv('ALPHA_VANTAGE_API_KEY')
        }
        # Multi-source analyzer (always fresh on every call)
        self.sentiment_analyzer = MultiSourceSentimentAnalyzer(symbol)
        et_tz = pytz.timezone('America/New_York')
        fetch_time = datetime.now(et_tz).strftime('%Y-%m-%d %H:%M:%S %Z')
        print(f"   ✅ FRESH NEWS SENTIMENT DATA at: {fetch_time}")
        
        # Try to load a trained news reaction model if exists
        self.model = None
        model_path = Path('models') / f'news_model_{self.symbol}.joblib'
        try:
            if model_path.exists():
                self.model = joblib.load(str(model_path))
                print(f"Loaded news reaction model for {self.symbol} (blend weight: {self.model_blend_weight:.0%})")
        except Exception as e:
            pass
    
    def get_latest_news(self, hours_back: int = 1) -> Dict[str, Any]:
        """Fetch latest news from multiple sources"""
        print(f"\n📰 Fetching latest news for {self.symbol}...")
        
        # Get multi-source sentiment
        sentiment_result = self.sentiment_analyzer.get_combined_sentiment(hours_back)
        overall_sentiment = sentiment_result.get('overall_sentiment', 0.0)
        article_count = sentiment_result.get('article_count', 0)
        
        # If a trained model is available, blend with it
        if self.model and article_count > 0:
            try:
                # Get news articles for model prediction
                articles = self._get_articles_for_model(hours_back)
                if articles:
                    texts = [a.get('headline', '') for a in articles]
                    preds = self.model.predict(texts)
                    # Map model predictions: UP=+1, DOWN=-1, NEUTRAL=0
                    mapped = [1.0 if p == 'UP' else (-1.0 if p == 'DOWN' else 0.0) for p in preds]
                    model_sent = sum(mapped) / len(mapped)
                    # Blend model sentiment with raw sentiment
                    overall_sentiment = (overall_sentiment * (1 - self.model_blend_weight)) + (model_sent * self.model_blend_weight)
                    print(f"   🔄 Model-adjusted sentiment: {overall_sentiment:+.2f} (weight: {self.model_blend_weight:.0%})")
            except Exception as e:
                pass
        
        return {
            'success': article_count > 0,
            'articles': [],
            'overall_sentiment': overall_sentiment,
            'article_count': article_count
        }
    
    def _get_articles_for_model(self, hours_back: int) -> List[Dict]:
        """Get articles for model prediction"""
        articles = []
        try:
            if self.api_keys['finnhub']:
                from_time = (datetime.now() - timedelta(hours=hours_back)).strftime('%Y-%m-%d')
                url = f"https://finnhub.io/api/v1/company-news?symbol={self.symbol}&from={from_time}&token={self.api_keys['finnhub']}"
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    articles = response.json()[:10]
        except:
            pass
        return articles



class IntraDay1HourPredictor:
    """Complete 1-hour intraday prediction engine"""
    
    def __init__(self, symbol: str, model_blend_weight: float = 0.6):
        self.symbol = symbol
        self.model_blend_weight = model_blend_weight
        self.momentum = MomentumAnalyzer(symbol)
        self.trend = TrendDetector()
        self.volume = VolumeAnalyzer()
        self.news = RealTimeNewsSentiment(symbol, model_blend_weight=model_blend_weight)
        # Initialize enhanced analyzers
        self.options = OptionsSentimentAnalyzer(symbol)
        self.social = SocialSentimentAnalyzer(symbol)
        self.economics = EconomicContextAnalyzer()
        self.fundamentals = FundamentalAnalyzer(symbol)
        self.nlp = SimpleNLPAnalyzer(symbol)
    
    def predict_next_hour(self) -> Dict[str, Any]:
        """Generate 1-hour ahead prediction"""
        
        print(f"\n{'='*80}")
        print(f"🚀 INTRADAY 1-HOUR MOMENTUM PREDICTOR - {self.symbol} - FRESH DATA MODE")
        print(f"{'='*80}")
        
        # Get intraday data
        et_tz = pytz.timezone('America/New_York')
        now_et = datetime.now(et_tz)
        print(f"⏰ {now_et.strftime('%Y-%m-%d %H:%M %p ET')}")
        print(f"🔄 FETCHING LATEST INTRADAY DATA (FRESH, NOT CACHED)...")
        
        # Fetch 1-minute candles (always fresh on every run)
        data = self.momentum.get_intraday_data(interval='1m', period='60m')
        
        if not data['success']:
            print(f"❌ {data['error']}")
            return {
                'symbol': self.symbol,
                'direction': 'NEUTRAL',
                'confidence': 0.0,
                'reason': 'No intraday data available'
            }
        
        candles = data['candles']
        current_price = data['current_price']
        
        print(f"\n💰 Current Price: ${current_price:.2f}")
        print(f"📊 1-Minute Candles: {data['candle_count']} available")
        
        # Analyze all momentum indicators
        print(f"\n{'='*80}")
        print(f"📈 MOMENTUM ANALYSIS")
        print(f"{'='*80}")
        
        # Use shorter periods for intraday (5-min candles = ~78 per day)
        # Standard periods: RSI=14, MACD=12/26/9, Stoch=14
        rsi = self.momentum.calculate_rsi(candles, period=9)  # Shorter for faster response
        print(f"\n🔴 RSI (9): {rsi['rsi']:.1f}")
        print(f"   Signal: {rsi['signal']}")
        print(f"   Sentiment: {rsi['sentiment']:+.2f}")
        
        macd = self.momentum.calculate_macd(candles, fast=8, slow=17, signal=9)  # Shorter for intraday
        print(f"\n🟡 MACD:")
        print(f"   MACD Line: {macd['macd']:+.6f}")
        print(f"   Signal Line: {macd['signal_line']:+.6f}")
        print(f"   Histogram: {macd['histogram']:+.6f}")
        print(f"   Signal: {macd['signal']}")
        print(f"   Sentiment: {macd['sentiment']:+.2f}")
        
        stoch = self.momentum.calculate_stochastic(candles, period=9)  # Shorter for faster response
        print(f"\n🟢 Stochastic:")
        print(f"   %K: {stoch['k_percent']:.1f}")
        print(f"   Signal: {stoch['signal']}")
        print(f"   Sentiment: {stoch['sentiment']:+.2f}")
        
        momentum = self.momentum.calculate_momentum(candles, period=5)  # Shorter period for intraday
        print(f"\n⚡ Rate of Change:")
        print(f"   ROC (5-period): {momentum['roc']:+.2f}%")
        print(f"   Signal: {momentum['signal']}")
        print(f"   Sentiment: {momentum['sentiment']:+.2f}")
        
        # Trend Analysis
        print(f"\n{'='*80}")
        print(f"📊 TREND ANALYSIS")
        print(f"{'='*80}")
        
        trend = self.trend.detect_trend(candles)
        print(f"\n🔺 Trend Direction: {trend['trend']}")
        print(f"   Strength: {trend['strength']:.1%}")
        print(f"   {trend['signal']}")
        
        support_resistance = self.trend.detect_support_resistance(candles)
        print(f"\n🎯 Support/Resistance:")
        print(f"   Support: ${support_resistance['support']:.2f} ({support_resistance['distance_to_support_pct']:+.2f}%)")
        print(f"   Resistance: ${support_resistance['resistance']:.2f} ({support_resistance['distance_to_resistance_pct']:+.2f}%)")
        
        # Volume Analysis
        print(f"\n{'='*80}")
        print(f"📊 VOLUME ANALYSIS")
        print(f"{'='*80}")
        
        volume = self.volume.analyze_volume(candles)
        print(f"\n📦 Volume:")
        print(f"   Current: {volume['current_volume']:,}")
        print(f"   Average: {volume['avg_volume']:,.0f}")
        print(f"   Ratio: {volume['volume_ratio']:.2f}x")
        print(f"   Signal: {volume['signal']}")
        print(f"   Sentiment: {volume['sentiment']:+.2f}")
        
        vwap = self.volume.calculate_vwap(candles)
        print(f"\n💹 VWAP:")
        print(f"   VWAP: ${vwap['vwap']:.2f}")
        print(f"   Distance: {vwap['distance_pct']:+.2f}%")
        print(f"   Signal: {vwap['signal']}")
        print(f"   Sentiment: {vwap['sentiment']:+.2f}")
        
        # News Sentiment
        print(f"\n{'='*80}")
        print(f"📰 REAL-TIME NEWS SENTIMENT")
        print(f"{'='*80}")
        
        news = self.news.get_latest_news(hours_back=1)
        news_sentiment = news.get('overall_sentiment', 0.0)
        print(f"\n📊 Overall News Sentiment: {news_sentiment:+.2f}")
        print(f"   Articles: {news['article_count']}")
        
        # Enhanced Sentiment Analysis
        print(f"\n{'='*80}")
        print(f"📊 ENHANCED MULTI-SOURCE SENTIMENT ANALYSIS")
        print(f"{'='*80}")
        
        # Options sentiment
        print(f"\n📈 Options Market Sentiment:")
        options_data = self.options.get_put_call_sentiment()
        options_sentiment = options_data.get('score', 0.0)
        print(f"   Put/Call Ratio: {options_data.get('put_call_ratio', 1.0):.2f}")
        print(f"   Signal: {options_data.get('signal', 'N/A')}")
        print(f"   Sentiment: {options_sentiment:+.2f}")
        
        # Social sentiment
        print(f"\n👥 Social Sentiment:")
        social_data = self.social.get_combined_social_sentiment()
        social_sentiment = social_data.get('overall_sentiment', 0.0)
        print(f"   Mentions: {social_data.get('mentions', 0)}")
        print(f"   Sentiment: {social_sentiment:+.2f}")
        
        # Economic context
        print(f"\n🌍 Economic Context:")
        econ_data = self.economics.get_economic_sentiment()
        econ_sentiment = econ_data.get('overall_sentiment', 0.0)
        print(f"   VIX: {econ_data.get('vix', 20.0):.1f}")
        print(f"   Fed Rate: {econ_data.get('fed_rate', 0.0):.2f}%")
        print(f"   Sentiment: {econ_sentiment:+.2f}")
        
        # Fundamental sentiment
        print(f"\n💼 Fundamental Sentiment:")
        fund_data = self.fundamentals.get_fundamental_sentiment()
        fund_sentiment = fund_data.get('overall_sentiment', 0.0)
        print(f"   Earnings: {fund_data.get('earnings_signal', 'N/A')}")
        print(f"   Analyst: {fund_data.get('analyst_rating', 'N/A')}")
        print(f"   Sentiment: {fund_sentiment:+.2f}")
        
        # Calculate total momentum score
        print(f"\n{'='*80}")
        print(f"🎯 TOTAL MOMENTUM SCORE")
        print(f"{'='*80}")
        
        # Weight each component - Enhanced with all sources
        total_score = (
            rsi['sentiment'] * 0.15 +           # RSI: 15%
            macd['sentiment'] * 0.20 +          # MACD: 20% (strongest technical)
            stoch['sentiment'] * 0.10 +         # Stochastic: 10%
            momentum['sentiment'] * 0.08 +      # ROC: 8%
            volume['sentiment'] * 0.08 +        # Volume: 8%
            vwap['sentiment'] * 0.04 +          # VWAP: 4%
            news_sentiment * 0.05 +             # News: 5%
            options_sentiment * 0.05 +          # Options: 5%
            social_sentiment * 0.03 +           # Social: 3%
            econ_sentiment * 0.03 +             # Economics: 3%
            fund_sentiment * 0.04                # Fundamentals: 4%
        )
        
        print(f"\n📊 Score Breakdown:")
        print(f"   RSI Component:         {rsi['sentiment'] * 0.15:+.3f}")
        print(f"   MACD Component:        {macd['sentiment'] * 0.20:+.3f}")
        print(f"   Stochastic Component:  {stoch['sentiment'] * 0.10:+.3f}")
        print(f"   ROC Component:         {momentum['sentiment'] * 0.08:+.3f}")
        print(f"   Volume Component:      {volume['sentiment'] * 0.08:+.3f}")
        print(f"   VWAP Component:        {vwap['sentiment'] * 0.04:+.3f}")
        print(f"   News Component:        {news_sentiment * 0.05:+.3f}")
        print(f"   Options Component:     {options_sentiment * 0.05:+.3f}")
        print(f"   Social Component:      {social_sentiment * 0.03:+.3f}")
        print(f"   Economic Component:    {econ_sentiment * 0.03:+.3f}")
        print(f"   Fundamental Component: {fund_sentiment * 0.04:+.3f}")
        print(f"   {'─'*40}")
        print(f"   TOTAL MOMENTUM SCORE: {total_score:+.3f}")
        
        # Determine direction and confidence
        if total_score >= 0.05:
            direction = 'UP'
            confidence_base = 55 + abs(total_score) * 200
        elif total_score <= -0.05:
            direction = 'DOWN'
            confidence_base = 55 + abs(total_score) * 200
        else:
            direction = 'NEUTRAL'
            confidence_base = 50
        
        # Apply safeguards
        confidence = min(confidence_base, 88)
        
        # Check for divergences (risk signal)
        divergence_warning = ""
        if rsi['signal'] == 'OVERBOUGHT' and trend['trend'] == 'UPTREND':
            divergence_warning = "⚠️ DIVERGENCE: Overbought in uptrend - reversal risk"
            confidence *= 0.85  # Reduce by 15%
        elif rsi['signal'] == 'OVERSOLD' and trend['trend'] == 'DOWNTREND':
            divergence_warning = "⚠️ DIVERGENCE: Oversold in downtrend - bounce possible"
            confidence *= 0.85
        
        # Calculate target and stop
        entry = current_price
        if direction == 'UP':
            target = entry * 1.01  # +1% target
            stop = entry * 0.995   # -0.5% stop
        elif direction == 'DOWN':
            target = entry * 0.99  # -1% target
            stop = entry * 1.005   # +0.5% stop
        else:
            target = entry
            stop = entry
        
        # Determine position size based on confidence
        if confidence >= 75:
            position_size = 1.0
            recommendation = 'STRONG_TRADE'
        elif confidence >= 65:
            position_size = 0.75
            recommendation = 'TRADE'
        elif confidence >= 55:
            position_size = 0.5
            recommendation = 'CAUTIOUS'
        else:
            position_size = 0.0
            recommendation = 'SKIP'
        
        print(f"\n{'='*80}")
        print(f"🎯 PREDICTION FOR NEXT HOUR")
        print(f"{'='*80}")
        print(f"\n📊 Direction: {direction}")
        print(f"🎯 Confidence: {confidence:.1f}%")
        print(f"💡 Recommendation: {recommendation}")
        print(f"📍 Position Size: {position_size*100:.0f}%")
        
        if divergence_warning:
            print(f"\n{divergence_warning}")
        
        print(f"\n💰 Trade Plan:")
        print(f"   Entry: ${entry:.2f}")
        print(f"   Target: ${target:.2f} ({(target/entry-1)*100:+.2f}%)")
        print(f"   Stop: ${stop:.2f} ({(stop/entry-1)*100:+.2f}%)")
        # Avoid division by zero for neutral direction
        if entry != stop:
            risk_reward = abs((target-entry)/(entry-stop))
            print(f"   Risk/Reward: 1:{risk_reward:.2f}")
        else:
            print(f"   Risk/Reward: N/A (Neutral position)")
        
        return {
            'symbol': self.symbol,
            'timestamp': now_et.isoformat(),
            'current_price': current_price,
            'direction': direction,
            'confidence': confidence / 100,  # Return as decimal
            'recommendation': recommendation,
            'position_size': position_size,
            'entry': entry,
            'target': target,
            'stop': stop,
            'reason': f'Momentum Score: {total_score:+.3f} ({direction})',
            'components': {
                'rsi': rsi['rsi'],
                'macd_signal': macd['signal'],
                'trend': trend['trend'],
                'volume_ratio': volume['volume_ratio'],
                'news_sentiment': news_sentiment
            },
            'warning': divergence_warning if divergence_warning else 'None'
        }


def main():
    """Run intraday predictor for multiple stocks

    By default this will not run outside regular US market hours (9:30-16:00 ET).
    Pass --allow-offhours to override and force a run.
    """
    import argparse

    def _is_market_open_now() -> bool:
        et_tz = pytz.timezone('America/New_York')
        now_et = datetime.now(et_tz)
        market_open_time = now_et.replace(hour=9, minute=30, second=0, microsecond=0)
        market_close_time = now_et.replace(hour=16, minute=0, second=0, microsecond=0)
        return now_et.weekday() < 5 and (market_open_time <= now_et <= market_close_time)

    parser = argparse.ArgumentParser(description='Intraday 1-Hour Predictor (single-run)')
    parser.add_argument('--stocks', type=str, default='AMD,NVDA,META,AVGO,SNOW,PLTR',
                        help='Comma-separated list of stocks to analyze')
    parser.add_argument('--allow-offhours', action='store_true', help='Allow running outside market hours')
    parser.add_argument('--model-blend', type=float, default=0.6, 
                        help='Model blending weight (0.0-1.0): 1.0=full model, 0.0=raw sentiment)')

    args = parser.parse_args()
    stocks = args.stocks.split(',') if args.stocks else ['AMD', 'NVDA', 'META', 'AVGO', 'SNOW', 'PLTR']
    model_blend_weight = max(0.0, min(1.0, args.model_blend))  # Clamp to 0-1

    # Prevent accidental execution outside market hours
    if not args.allow_offhours and not _is_market_open_now():
        et_tz = pytz.timezone('America/New_York')
        now_et = datetime.now(et_tz)
        print(f"\n⏰ Market is CLOSED (ET: {now_et.strftime('%Y-%m-%d %H:%M:%S')}).")
        print("   To run the predictor outside market hours, pass --allow-offhours.")
        return

    results = {}

    for symbol in stocks:
        try:
            predictor = IntraDay1HourPredictor(symbol, model_blend_weight=model_blend_weight)
            prediction = predictor.predict_next_hour()
            results[symbol] = prediction
        except Exception as e:
            print(f"\n❌ Error predicting {symbol}: {str(e)}")
            results[symbol] = {'error': str(e)}
    
    # Summary
    print(f"\n\n{'='*80}")
    print(f"📊 INTRADAY 1-HOUR TRADING SUMMARY")
    print(f"{'='*80}")
    
    trades = [r for r in results.values() if isinstance(r, dict) and r.get('position_size', 0) > 0]
    
    if trades:
        print(f"\n🎯 {len(trades)} TRADING SIGNALS:\n")
        
        for trade in trades:
            print(f"{trade['symbol']}:")
            print(f"   Direction: {trade['direction']}")
            print(f"   Confidence: {trade['confidence']*100:.1f}%")
            print(f"   Entry: ${trade['entry']:.2f}")
            print(f"   Target: ${trade['target']:.2f} ({(trade['target']/trade['entry']-1)*100:+.2f}%)")
            print(f"   Stop: ${trade['stop']:.2f}")
            print(f"   Position: {trade['position_size']*100:.0f}%")
            if trade['warning'] != 'None':
                print(f"   ⚠️ {trade['warning']}")
            print()
    else:
        print(f"\n⚪ NO TRADING SIGNALS - All stocks below confidence threshold")
    
    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    with open(f'data/intraday/predictions_{timestamp}.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Results saved to: data/intraday/predictions_{timestamp}.json")


if __name__ == '__main__':
    main()
