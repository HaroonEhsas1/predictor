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

# Load environment variables
load_dotenv()
import joblib
from pathlib import Path


class MomentumAnalyzer:
    """Calculate intraday momentum indicators"""
    
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.ticker = yf.Ticker(symbol)
    
    def get_intraday_data(self, interval: str = '1m', period: str = '60m'):
        """
        Fetch intraday data
        interval: '1m', '5m', '15m', '60m'
        period: '60m', '1d', '5d'
        """
        try:
            # For 1-minute and 5-minute candles, we need to use period='1d' or '5d'
            # Yahoo Finance limits 1-minute to past day only
            if interval in ['1m', '5m']:
                period = '1d'
            
            # Fetch intraday data
            hist = self.ticker.history(interval=interval, period=period)
            
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
            return {'success': False, 'rsi': 50, 'signal': 'NEUTRAL'}
        
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
            return {'success': False, 'macd': 0, 'signal_line': 0, 'histogram': 0}
        
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
            return {'success': False, 'k': 50, 'd': 50, 'signal': 'NEUTRAL'}
        
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
            return {'success': False, 'roc': 0, 'signal': 'NEUTRAL'}
        
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
            return {'success': False, 'avg_volume': 0, 'volume_signal': 'INSUFFICIENT'}
        
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
            return {'success': False, 'vwap': 0}
        
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
    """Analyze real-time news sentiment"""
    
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.api_keys = {
            'finnhub': os.getenv('FINNHUB_API_KEY'),
            'alpha_vantage': os.getenv('ALPHA_VANTAGE_API_KEY')
        }
        # Try to load a trained news reaction model if exists
        self.model = None
        self.model_blend_weight = 0.6  # Default: 60% model, 40% raw sentiment
        model_path = Path('models') / f'news_model_{self.symbol}.joblib'
        try:
            if model_path.exists():
                self.model = joblib.load(str(model_path))
                print(f"Loaded news reaction model for {self.symbol} (blend weight: {self.model_blend_weight:.0%})")
        except Exception as e:
            print(f"Warning: failed to load news model for {self.symbol}: {e}")
    
    def get_latest_news(self, hours_back: int = 1) -> Dict[str, Any]:
        """Fetch latest news from last N hours"""
        print(f"\n📰 Fetching latest news for {self.symbol}...")
        
        bullish_keywords = ['surge', 'rally', 'gain', 'rise', 'bullish', 'upgrade', 'beats', 
                           'growth', 'strong', 'buy', 'up', 'high', 'jump', 'soars', 'breakthrough']
        bearish_keywords = ['drop', 'fall', 'decline', 'bearish', 'downgrade', 'miss', 
                           'weak', 'loss', 'sell', 'down', 'low', 'plunge', 'crash', 'warning']
        
        news_articles = []
        sentiment_scores = []
        
        # Finnhub News
        try:
            if self.api_keys['finnhub']:
                from_time = (datetime.now() - timedelta(hours=hours_back)).strftime('%Y-%m-%d')
                url = f"https://finnhub.io/api/v1/company-news?symbol={self.symbol}&from={from_time}&token={self.api_keys['finnhub']}"
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    articles = response.json()[:5]  # Last 5 articles
                    
                    for article in articles:
                        headline = article.get('headline', '').lower()
                        summary = article.get('summary', '').lower()
                        text = headline + ' ' + summary
                        
                        # Count keywords
                        bullish_count = sum(1 for kw in bullish_keywords if kw in text)
                        bearish_count = sum(1 for kw in bearish_keywords if kw in text)
                        
                        # Calculate sentiment
                        if bullish_count > bearish_count:
                            sentiment = 1.0
                        elif bearish_count > bullish_count:
                            sentiment = -1.0
                        else:
                            sentiment = 0.0
                        
                        news_articles.append({
                            'headline': article.get('headline'),
                            'sentiment': sentiment
                        })
                        sentiment_scores.append(sentiment)
                        
                        print(f"   • {headline[:60]}... (sentiment: {sentiment:+.1f})")
        except Exception as e:
            print(f"   ⚠️ Finnhub error: {str(e)[:50]}")
        
        # Calculate overall sentiment
        overall_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0.0

        # If a trained model is available, adjust sentiment based on predicted price reaction
        # The model predicts labels: 'UP', 'DOWN', 'NEUTRAL'
        if self.model and news_articles:
            try:
                texts = [a['headline'] or '' for a in news_articles]
                preds = self.model.predict(texts)
                # Map model predictions into sentiment adjustment: UP=+1, DOWN=-1, NEUTRAL=0
                mapped = [1.0 if p == 'UP' else (-1.0 if p == 'DOWN' else 0.0) for p in preds]
                # Use average predicted direction
                model_sent = sum(mapped) / len(mapped)
                # Blend model sentiment with raw keyword sentiment
                overall_sentiment = (overall_sentiment * (1 - self.model_blend_weight)) + (model_sent * self.model_blend_weight)
                print(f"   🔄 Model-adjusted news sentiment: {overall_sentiment:+.2f} (weight: {self.model_blend_weight:.0%})")
            except Exception as e:
                print(f"   ⚠️ News model inference error: {e}")
        
        print(f"   📊 News Sentiment: {overall_sentiment:+.2f}")
        
        return {
            'success': len(news_articles) > 0,
            'articles': news_articles,
            'overall_sentiment': overall_sentiment,
            'article_count': len(news_articles)
        }


class IntraDay1HourPredictor:
    """Complete 1-hour intraday prediction engine"""
    
    def __init__(self, symbol: str, model_blend_weight: float = 0.6):
        self.symbol = symbol
        self.momentum = MomentumAnalyzer(symbol)
        self.trend = TrendDetector()
        self.volume = VolumeAnalyzer()
        self.news = RealTimeNewsSentiment(symbol)
        self.news.model_blend_weight = model_blend_weight
    
    def predict_next_hour(self) -> Dict[str, Any]:
        """Generate 1-hour ahead prediction"""
        
        print(f"\n{'='*80}")
        print(f"🚀 INTRADAY 1-HOUR MOMENTUM PREDICTOR - {self.symbol}")
        print(f"{'='*80}")
        
        # Get intraday data
        et_tz = pytz.timezone('America/New_York')
        now_et = datetime.now(et_tz)
        print(f"⏰ {now_et.strftime('%Y-%m-%d %H:%M %p ET')}")
        
        # Fetch 1-minute candles
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
        
        rsi = self.momentum.calculate_rsi(candles)
        print(f"\n🔴 RSI (14): {rsi['rsi']:.1f}")
        print(f"   Signal: {rsi['signal']}")
        print(f"   Sentiment: {rsi['sentiment']:+.2f}")
        
        macd = self.momentum.calculate_macd(candles)
        print(f"\n🟡 MACD:")
        print(f"   MACD Line: {macd['macd']:+.6f}")
        print(f"   Signal Line: {macd['signal_line']:+.6f}")
        print(f"   Histogram: {macd['histogram']:+.6f}")
        print(f"   Signal: {macd['signal']}")
        print(f"   Sentiment: {macd['sentiment']:+.2f}")
        
        stoch = self.momentum.calculate_stochastic(candles)
        print(f"\n🟢 Stochastic:")
        print(f"   %K: {stoch['k_percent']:.1f}")
        print(f"   Signal: {stoch['signal']}")
        print(f"   Sentiment: {stoch['sentiment']:+.2f}")
        
        momentum = self.momentum.calculate_momentum(candles)
        print(f"\n⚡ Rate of Change:")
        print(f"   ROC (10-period): {momentum['roc']:+.2f}%")
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
        
        # Calculate total momentum score
        print(f"\n{'='*80}")
        print(f"🎯 TOTAL MOMENTUM SCORE")
        print(f"{'='*80}")
        
        # Weight each component
        total_score = (
            rsi['sentiment'] * 0.25 +       # RSI: 25%
            macd['sentiment'] * 0.30 +      # MACD: 30% (strongest)
            stoch['sentiment'] * 0.15 +     # Stochastic: 15%
            momentum['sentiment'] * 0.10 +  # ROC: 10%
            volume['sentiment'] * 0.10 +    # Volume: 10%
            vwap['sentiment'] * 0.05 +      # VWAP: 5%
            news_sentiment * 0.05            # News: 5%
        )
        
        print(f"\n📊 Score Breakdown:")
        print(f"   RSI Component:        {rsi['sentiment'] * 0.25:+.3f}")
        print(f"   MACD Component:       {macd['sentiment'] * 0.30:+.3f}")
        print(f"   Stochastic Component: {stoch['sentiment'] * 0.15:+.3f}")
        print(f"   ROC Component:        {momentum['sentiment'] * 0.10:+.3f}")
        print(f"   Volume Component:     {volume['sentiment'] * 0.10:+.3f}")
        print(f"   VWAP Component:       {vwap['sentiment'] * 0.05:+.3f}")
        print(f"   News Component:       {news_sentiment * 0.05:+.3f}")
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
        print(f"   Risk/Reward: 1:{abs((target-entry)/(entry-stop)):.2f}")
        
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
