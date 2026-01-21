#!/usr/bin/env python3
"""
Comprehensive Next-Day Predictor (Multi-Stock Support)
Analyzes: News, Sentiment, Futures, Options Flow, Technical Indicators, Sector Data
Fast initialization - No heavy TensorFlow models
Supports: AMD, AVGO, and other stocks via stock_config.py
"""

import sys
import io

# Fix Windows console encoding for emoji support
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(
        sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(
        sys.stderr.buffer, encoding='utf-8', errors='replace')

import yfinance as yf
import requests
from datetime import datetime, timedelta
import pytz
import os
from typing import Dict, Any
import json
from dotenv import load_dotenv
from volume_profile import calculate_vwap

# Load environment variables from .env file
load_dotenv()

# Import Hidden Edge Engine
try:
    from hidden_edge_engine import HiddenEdgeEngine
    HIDDEN_EDGE_AVAILABLE = True
except ImportError:
    HIDDEN_EDGE_AVAILABLE = False
    print("⚠️ Hidden Edge Engine not available")

# Import Additional Signals (Phase 1 - Free signals)
try:
    from additional_signals import AdditionalSignals
    ADDITIONAL_SIGNALS_AVAILABLE = True
except ImportError:
    ADDITIONAL_SIGNALS_AVAILABLE = False
    print("⚠️ Additional Signals not available")

# Import Intelligent Conflict Resolver (Phase 5 - Smart conflict resolution)
try:
    from intelligent_conflict_resolver import IntelligentConflictResolver
    CONFLICT_RESOLVER_AVAILABLE = True
except ImportError:
    CONFLICT_RESOLVER_AVAILABLE = False
    print("⚠️ Intelligent Conflict Resolver not available")

# Import ORCL Catalyst Detector (Option 3 - ORCL-specific catalysts)
try:
    from orcl_catalyst_detector import OracleCatalystDetector
    ORCL_CATALYST_AVAILABLE = True
except ImportError:
    ORCL_CATALYST_AVAILABLE = False
    print("⚠️ ORCL Catalyst Detector not available")

# Import stock config
try:
    from stock_config import STOCK_SYMBOL, get_stock_config, get_stock_weight_adjustments
    DEFAULT_SYMBOL = STOCK_SYMBOL
except:
    DEFAULT_SYMBOL = "AMD"

    def get_stock_config(symbol):
        return {}

    def get_stock_weight_adjustments(symbol):
        return {
            'news': 0.20, 'futures': 0.20, 'options': 0.15,
            'technical': 0.15, 'sector': 0.10, 'reddit': 0.10,
            'institutional': 0.10
        }

# Import Stock-Specific Enhancements
try:
    from stock_specific_enhancements import StockSpecificEnhancements
    ENHANCEMENTS_AVAILABLE = True
except ImportError:
    ENHANCEMENTS_AVAILABLE = False
    print("⚠️ Stock-specific enhancements not available")

# Import Pattern Knowledge System
try:
    from real_time_pattern_detector import RealTimePatternDetector
    PATTERN_KNOWLEDGE_AVAILABLE = True
except ImportError:
    PATTERN_KNOWLEDGE_AVAILABLE = False
    print("⚠️ Pattern knowledge system not available")


class ComprehensiveNextDayPredictor:
    """Comprehensive prediction engine with multi-source analysis"""

    def __init__(self, symbol: str = None):
        self.symbol = symbol or DEFAULT_SYMBOL
        self.stock_config = get_stock_config(self.symbol)
        self.weight_adjustments = get_stock_weight_adjustments(self.symbol)
        self.api_keys = {
            'alpha_vantage': os.getenv('ALPHA_VANTAGE_API_KEY'),
            'finnhub': os.getenv('FINNHUB_API_KEY'),
            'fmp': os.getenv('FMP_API_KEY'),
        }

        # Print stock-specific configuration
        if self.stock_config:
            print(
                f"\n🎯 Loaded config for {self.symbol}: {self.stock_config.get('name', self.symbol)}")
            print(
                f"   Typical Volatility: {self.stock_config.get('typical_volatility', 0.015)*100:.1f}%")

    def get_news_sentiment(self) -> Dict[str, Any]:
        """Collect and analyze news sentiment"""
        print("\n📰 Analyzing News Sentiment...")

        news_data = {'overall_score': 0.0, 'bullish_count': 0,
                     'bearish_count': 0, 'sources': [], 'has_data': False}

        try:
            # Finnhub News - analyze headlines since sentiment field often missing
            # CHANGED: 2 days -> 6 hours for CURRENT news only
            if self.api_keys['finnhub']:
                try:
                    # Get news from last 6 hours only (more current)
                    from_time = (datetime.now()-timedelta(hours=6)
                                 ).strftime('%Y-%m-%d')
                    url = f"https://finnhub.io/api/v1/company-news?symbol={self.symbol}&from={from_time}&to={datetime.now().strftime('%Y-%m-%d')}&token={self.api_keys['finnhub']}"
                    response = requests.get(url, timeout=10)
                    if response.status_code == 200:
                        articles = response.json()[:10]

                        # Keyword-based analysis since Finnhub sentiment field unreliable
                        bullish_keywords = ['surge', 'rally', 'gain', 'rise', 'bullish',
                                            'upgrade', 'beats', 'growth', 'strong', 'buy', 'up', 'high']
                        bearish_keywords = ['drop', 'fall', 'decline', 'bearish',
                                            'downgrade', 'miss', 'weak', 'loss', 'sell', 'down', 'low']

                        for article in articles:
                            headline = article.get('headline', '').lower()
                            summary = article.get('summary', '').lower()
                            text = headline + ' ' + summary

                            bullish_score = sum(
                                1 for word in bullish_keywords if word in text)
                            bearish_score = sum(
                                1 for word in bearish_keywords if word in text)

                            if bullish_score > bearish_score:
                                news_data['bullish_count'] += 1
                            elif bearish_score > bullish_score:
                                news_data['bearish_count'] += 1

                        news_data['sources'].append('Finnhub')
                        print(f"   ✅ Finnhub: {len(articles)} articles")
                except:
                    pass

            # Alpha Vantage News
            if self.api_keys['alpha_vantage']:
                try:
                    url = f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers={self.symbol}&apikey={self.api_keys['alpha_vantage']}"
                    response = requests.get(url, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        if 'feed' in data:
                            for item in data['feed'][:15]:
                                for ticker_sentiment in item.get('ticker_sentiment', []):
                                    if ticker_sentiment.get('ticker') == self.symbol:
                                        score = float(ticker_sentiment.get(
                                            'ticker_sentiment_score', 0))
                                        if score > 0.15:
                                            news_data['bullish_count'] += 1
                                        elif score < -0.15:
                                            news_data['bearish_count'] += 1
                            news_data['sources'].append('Alpha Vantage')
                            print(
                                f"   ✅ Alpha Vantage: {len(data['feed'][:15])} articles")
                except:
                    pass

            # FMP News with keyword analysis
            if self.api_keys['fmp']:
                try:
                    url = f"https://financialmodelingprep.com/api/v3/stock_news?tickers={self.symbol}&limit=20&apikey={self.api_keys['fmp']}"
                    response = requests.get(url, timeout=10)
                    if response.status_code == 200:
                        articles = response.json()
                        bullish_keywords = [
                            'surge', 'rally', 'gain', 'rise', 'bullish', 'upgrade', 'beats', 'growth', 'strong']
                        bearish_keywords = [
                            'drop', 'fall', 'decline', 'bearish', 'downgrade', 'miss', 'weak', 'loss']

                        for article in articles:
                            text = (article.get('title', '') + ' ' +
                                    article.get('text', '')).lower()
                            bullish_score = sum(
                                1 for word in bullish_keywords if word in text)
                            bearish_score = sum(
                                1 for word in bearish_keywords if word in text)
                            if bullish_score > bearish_score:
                                news_data['bullish_count'] += 1
                            elif bearish_score > bullish_score:
                                news_data['bearish_count'] += 1
                        news_data['sources'].append('FMP')
                        print(f"   ✅ FMP: {len(articles)} articles")
                except:
                    pass

            total = news_data['bullish_count'] + news_data['bearish_count']
            if total > 0:
                news_data['overall_score'] = (
                    news_data['bullish_count'] - news_data['bearish_count']) / total
                news_data['has_data'] = True
                print(
                    f"   📊 Bullish: {news_data['bullish_count']} | Bearish: {news_data['bearish_count']}")
                print(f"   📈 News Score: {news_data['overall_score']:+.3f}")

                # IMPROVEMENT #5: News Freshness Decay
                # News from >4 hours ago is less reliable at prediction time (3:50 PM)
                # Since we're fetching news from last 6 hours, check current time
                current_hour = datetime.now().hour

                # If running at 3:50 PM (15:50), news from before 11:50 AM is >4 hours old
                # Apply conservative decay to avoid breaking what works
                # Running in afternoon (typical 3:50 PM run)
                if current_hour >= 15:
                    # News from 6 hours ago (morning) may be stale
                    news_age_estimate = 5  # Assume average news age is ~5 hours

                    if news_age_estimate > 4:
                        original_score = news_data['overall_score']
                        # Keep 70% (conservative - don't break Monday's success)
                        decay_factor = 0.7
                        news_data['overall_score'] = original_score * \
                            decay_factor
                        print(
                            f"   ⏰ News Freshness Decay: {original_score:+.3f} → {news_data['overall_score']:+.3f} (30% discount for afternoon staleness)")
            else:
                print(f"   ⚠️ No news data (using neutral)")
        except Exception as e:
            print(f"   ❌ Error: {str(e)[:50]}")

        return news_data

    def get_futures_sentiment(self) -> Dict[str, Any]:
        """Analyze futures markets"""
        print("\n📈 Analyzing Futures...")
        futures_data = {'es_change': 0.0, 'nq_change': 0.0,
                        'overall_sentiment': 0.0, 'has_data': False}

        try:
            es = yf.Ticker("ES=F").history(period="1d")
            if not es.empty:
                futures_data['es_change'] = (
                    (es['Close'].iloc[-1] - es['Open'].iloc[0]) / es['Open'].iloc[0]) * 100
                print(f"   ES: {futures_data['es_change']:+.2f}%")

            nq = yf.Ticker("NQ=F").history(period="1d")
            if not nq.empty:
                futures_data['nq_change'] = (
                    (nq['Close'].iloc[-1] - nq['Open'].iloc[0]) / nq['Open'].iloc[0]) * 100
                print(f"   NQ: {futures_data['nq_change']:+.2f}%")

            # Weight ES/NQ based on stock characteristics
            # Tech stocks lean more toward Nasdaq, diversified stocks more balanced
            if self.symbol in ['NVDA', 'AMD', 'AVGO', 'QCOM']:  # Pure tech/semiconductor
                futures_data['overall_sentiment'] = futures_data['es_change'] * \
                    0.40 + futures_data['nq_change'] * 0.60
            else:  # More balanced stocks
                futures_data['overall_sentiment'] = futures_data['es_change'] * \
                    0.50 + futures_data['nq_change'] * 0.50
            print(
                f"   📊 Futures Sentiment: {futures_data['overall_sentiment']:+.3f}%")

            # Store percentage for proper scoring (don't divide by 100 - keep as percentage)
            futures_data['overall_sentiment_pct'] = futures_data['overall_sentiment']
            futures_data['has_data'] = not es.empty or not nq.empty
        except Exception as e:
            print(f"   ❌ Error: {str(e)[:50]}")

        return futures_data

    def get_options_flow(self) -> Dict[str, Any]:
        """Analyze options flow"""
        print("\n📊 Analyzing Options...")
        options_data = {'put_call_ratio': 0.0,
                        'sentiment': 'neutral', 'analysis': ''}

        try:
            ticker = yf.Ticker(self.symbol)
            exp_dates = ticker.options
            if exp_dates:
                options_chain = ticker.option_chain(exp_dates[0])
                total_call_vol = options_chain.calls['volume'].sum()
                total_put_vol = options_chain.puts['volume'].sum()

                if total_call_vol > 0:
                    options_data['put_call_ratio'] = total_put_vol / \
                        total_call_vol

                    # FIXED: Tightened thresholds from 0.7/1.3 to 0.8/1.2
                    # Old neutral zone was too wide, causing bullish bias
                    if options_data['put_call_ratio'] < 0.8:  # FIXED: Was 0.7
                        options_data['sentiment'] = 'bullish'
                        options_data['analysis'] = 'Heavy call buying'
                    elif options_data['put_call_ratio'] > 1.2:  # FIXED: Was 1.3
                        options_data['sentiment'] = 'bearish'
                        options_data['analysis'] = 'Heavy put buying'
                    else:
                        options_data['sentiment'] = 'neutral'
                        options_data['analysis'] = 'Balanced activity'

                    print(
                        f"   P/C: {options_data['put_call_ratio']:.2f} ({options_data['sentiment'].upper()})")
                    print(f"   {options_data['analysis']}")
        except:
            print(f"   ⚠️ Options data unavailable")

        return options_data

    def get_technical_analysis(self) -> Dict[str, Any]:
        """Technical analysis"""
        print("\n📉 Technical Analysis...")
        technical = {'rsi': 50, 'macd_signal': 'neutral',
                     'trend': 'neutral', 'momentum_score': 0}

        try:
            hist = yf.Ticker(self.symbol).history(period="3mo")
            if len(hist) > 14:
                # RSI
                delta = hist['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                technical['rsi'] = 100 - (100 / (1 + rs.iloc[-1]))

                # MACD
                exp1 = hist['Close'].ewm(span=12, adjust=False).mean()
                exp2 = hist['Close'].ewm(span=26, adjust=False).mean()
                macd = exp1 - exp2
                signal = macd.ewm(span=9, adjust=False).mean()
                technical['macd_signal'] = 'bullish' if macd.iloc[-1] > signal.iloc[-1] else 'bearish'

                # Trend
                ma20 = hist['Close'].rolling(window=20).mean().iloc[-1]
                current = hist['Close'].iloc[-1]
                technical['trend'] = 'uptrend' if current > ma20 else 'downtrend'

                # Momentum
                technical['momentum_score'] = (
                    (hist['Close'].iloc[-1] - hist['Close'].iloc[-6]) / hist['Close'].iloc[-6]) * 100

                # FIX #5: MEAN REVERSION DETECTION
                # Count consecutive up/down days to detect overextended moves
                consecutive_up = 0
                consecutive_down = 0
                for i in range(len(hist) - 1, max(len(hist) - 6, 0), -1):
                    day_change = hist['Close'].iloc[i] - hist['Open'].iloc[i]
                    if day_change > 0:
                        consecutive_up += 1
                        consecutive_down = 0  # Reset
                    else:
                        consecutive_down += 1
                        consecutive_up = 0  # Reset

                    # Stop counting once we hit a reversal
                    if (consecutive_up > 0 and day_change < 0) or (consecutive_down > 0 and day_change > 0):
                        break

                technical['consecutive_up'] = consecutive_up
                technical['consecutive_down'] = consecutive_down

                # Mean reversion signal
                technical['mean_reversion_signal'] = 'none'
                if consecutive_up >= 2 and technical['rsi'] > 60:
                    # Likely reversal down
                    technical['mean_reversion_signal'] = 'bearish'
                elif consecutive_down >= 2 and technical['rsi'] < 40:
                    # Likely bounce up
                    technical['mean_reversion_signal'] = 'bullish'

                print(f"   RSI: {technical['rsi']:.1f}")
                print(f"   MACD: {technical['macd_signal'].upper()}")
                print(f"   Trend: {technical['trend'].upper()}")
                print(f"   Momentum: {technical['momentum_score']:+.2f}%")

                if technical['mean_reversion_signal'] != 'none':
                    if consecutive_up >= 2:
                        print(
                            f"   ⚠️ Mean Reversion: {consecutive_up} up days + RSI {technical['rsi']:.1f} → Reversal risk")
                    elif consecutive_down >= 2:
                        print(
                            f"   💡 Mean Reversion: {consecutive_down} down days + RSI {technical['rsi']:.1f} → Bounce likely")
        except Exception as e:
            print(f"   ❌ Error: {str(e)[:50]}")

        return technical

    def get_sector_analysis(self) -> Dict[str, Any]:
        """Sector analysis"""
        print("\n🏭 Sector Analysis...")
        sector = {'sector_sentiment': 0.0}

        try:
            # Get sector ETF from config or use XLK for tech
            sector_etf = self.stock_config.get('sector_etf', 'XLK')
            etf_ticker = yf.Ticker(sector_etf).history(period="5d")

            if len(etf_ticker) >= 2:
                etf_chg = (
                    (etf_ticker['Close'].iloc[-1] - etf_ticker['Close'].iloc[-2]) / etf_ticker['Close'].iloc[-2]) * 100
                sector['sector_sentiment'] = etf_chg / 100
                print(f"   {sector_etf}: {etf_chg:+.2f}%")

            # Check competitors if available
            competitors = self.stock_config.get('competitors', [])
            if competitors:
                comp_changes = []
                for comp in competitors[:2]:  # Only check first 2
                    try:
                        comp_hist = yf.Ticker(comp).history(period="5d")
                        if len(comp_hist) >= 2:
                            comp_chg = (
                                (comp_hist['Close'].iloc[-1] - comp_hist['Close'].iloc[-2]) / comp_hist['Close'].iloc[-2]) * 100
                            comp_changes.append(comp_chg)
                            print(f"   {comp}: {comp_chg:+.2f}%")
                    except:
                        pass

                if comp_changes:
                    avg_comp = sum(comp_changes) / len(comp_changes)
                    sector['sector_sentiment'] = (
                        sector['sector_sentiment'] + avg_comp/100) / 2
        except:
            print(f"   ⚠️ Sector data unavailable")

        return sector

    def get_reddit_sentiment(self) -> Dict[str, Any]:
        """Analyze Reddit sentiment with timeout protection"""
        print("\n💬 Reddit Sentiment Analysis...")
        reddit_data = {'sentiment_score': 0.0,
                       'post_count': 0, 'overall': 'neutral'}

        try:
            # Try Reddit with 15-second timeout protection
            import threading

            result_container = [None]
            exception_container = [None]

            def fetch_reddit():
                try:
                    from reddit_sentiment_tracker import RedditSentimentTracker
                    tracker = RedditSentimentTracker()
                    result_container[0] = tracker.get_overall_reddit_sentiment()
                except Exception as e:
                    exception_container[0] = e

            thread = threading.Thread(target=fetch_reddit)
            thread.daemon = True
            thread.start()
            thread.join(timeout=15)  # 15 second timeout

            if thread.is_alive():
                print("   ⚠️ Reddit API timeout (>15s) - using neutral")
                return reddit_data

            if exception_container[0]:
                print(
                    f"   ⚠️ Reddit error: {str(exception_container[0])[:30]}")
                return reddit_data

            result = result_container[0]

            try:

                if result and 'error' not in result:
                    # Convert 0-10 score to -1 to +1 range
                    # 0-10 → -1 to +1: (score - 5) / 5
                    reddit_data['sentiment_score'] = (
                        result.get('score', 5) - 5) / 5
                    reddit_data['post_count'] = result.get('mentions', 0)
                    reddit_data['overall'] = result.get(
                        'sentiment', 'neutral').lower()
                    reddit_data['has_data'] = result.get('mentions', 0) > 0

                    print(f"   Sentiment: {reddit_data['overall'].upper()}")
                    print(f"   Score: {reddit_data['sentiment_score']:+.3f}")
                    print(f"   Mentions: {reddit_data['post_count']}")
                    print(f"   Impact: {result.get('impact', 'UNKNOWN')}")
                else:
                    print(f"   ⚠️ No Reddit data available")
            except:
                # Fallback: Simple keyword-based sentiment from stock ticker
                ticker = yf.Ticker(self.symbol)
                if hasattr(ticker, 'news'):
                    # Use news headlines as proxy
                    bullish_words = ['bull', 'buy',
                                     'long', 'upgrade', 'gain', 'surge']
                    bearish_words = ['bear', 'sell',
                                     'short', 'downgrade', 'loss', 'drop']

                    bull_count = 0
                    bear_count = 0

                    for article in ticker.news[:10]:
                        title = article.get('title', '').lower()
                        bull_count += sum(1 for word in bullish_words if word in title)
                        bear_count += sum(1 for word in bearish_words if word in title)

                    if bull_count + bear_count > 0:
                        reddit_data['sentiment_score'] = (
                            bull_count - bear_count) / (bull_count + bear_count)
                        reddit_data['post_count'] = bull_count + bear_count
                        reddit_data['overall'] = 'bullish' if reddit_data['sentiment_score'] > 0 else 'bearish' if reddit_data['sentiment_score'] < 0 else 'neutral'
                        print(
                            f"   Sentiment (via news): {reddit_data['overall'].upper()}")
                        print(
                            f"   Score: {reddit_data['sentiment_score']:+.3f}")
                    else:
                        print(f"   ⚠️ Limited sentiment data")
                else:
                    print(f"   ⚠️ Reddit sentiment unavailable")
        except Exception as e:
            print(f"   ❌ Error: {str(e)[:50]}")

        return reddit_data

    def get_institutional_flow(self) -> Dict[str, Any]:
        """Analyze institutional money flow"""
        print("\n🏦 Institutional Flow Analysis...")
        inst_data = {'flow_direction': 'neutral',
                     'signal_strength': 0.0, 'indicators': []}

        try:
            ticker = yf.Ticker(self.symbol)
            hist = ticker.history(period="10d")

            if len(hist) >= 5:
                # Volume trend analysis
                recent_volume = hist['Volume'].tail(3).mean()
                prev_volume = hist['Volume'].head(5).mean()
                volume_ratio = recent_volume / prev_volume if prev_volume > 0 else 1

                # Price + Volume accumulation/distribution
                recent_price_change = (
                    (hist['Close'].iloc[-1] - hist['Close'].iloc[-3]) / hist['Close'].iloc[-3]) * 100

                # Dark pool indicator (high volume on green days = accumulation)
                if volume_ratio > 1.2 and recent_price_change > 0:
                    inst_data['flow_direction'] = 'accumulation'
                    inst_data['signal_strength'] = min(
                        (volume_ratio - 1) * 0.5, 0.3)
                    inst_data['indicators'].append('Volume surge on up days')
                elif volume_ratio > 1.2 and recent_price_change < 0:
                    inst_data['flow_direction'] = 'distribution'
                    inst_data['signal_strength'] = - \
                        min((volume_ratio - 1) * 0.5, 0.3)
                    inst_data['indicators'].append('Volume surge on down days')

                # Check for institutional buying patterns (small dips on high volume)
                last_3_days = hist.tail(3)
                dip_buys = 0
                for i in range(len(last_3_days)):
                    day = last_3_days.iloc[i]
                    if day['Close'] < day['Open'] and day['Volume'] > prev_volume * 1.1:
                        dip_buys += 1

                if dip_buys >= 2:
                    inst_data['flow_direction'] = 'accumulation'
                    inst_data['signal_strength'] = 0.2
                    inst_data['indicators'].append('Dip buying detected')

                print(f"   Flow: {inst_data['flow_direction'].upper()}")
                print(f"   Volume Ratio: {volume_ratio:.2f}x")
                print(
                    f"   Signal Strength: {inst_data['signal_strength']:+.3f}")
                if inst_data['indicators']:
                    for indicator in inst_data['indicators']:
                        print(f"   • {indicator}")
            else:
                print(f"   ⚠️ Insufficient data for flow analysis")

        except Exception as e:
            print(f"   ❌ Error: {str(e)[:50]}")

        return inst_data

    def get_twitter_sentiment(self) -> Dict[str, Any]:
        """Analyze Twitter sentiment with timeout protection"""
        print("\n🐦 Twitter Sentiment Analysis...")
        twitter_data = {'sentiment_score': 0.0, 'tweet_count': 0,
                        'overall': 'neutral', 'has_data': False}

        try:
            # Try Twitter with 15-second timeout protection
            import threading

            result_container = [None]
            exception_container = [None]

            def fetch_twitter():
                try:
                    from twitter_sentiment_tracker import TwitterSentimentTracker
                    tracker = TwitterSentimentTracker()
                    result_container[0] = tracker.get_twitter_sentiment_score()
                except Exception as e:
                    exception_container[0] = e

            thread = threading.Thread(target=fetch_twitter)
            thread.daemon = True
            thread.start()
            thread.join(timeout=15)  # 15 second timeout

            if thread.is_alive():
                print("   ⚠️ Twitter API timeout (>15s) - using neutral")
                return twitter_data

            if exception_container[0]:
                print(
                    f"   ⚠️ Twitter error: {str(exception_container[0])[:30]}")
                return twitter_data

            result = result_container[0]

            try:

                if result and 'error' not in result:
                    # Convert 0-10 score to -1 to +1 range
                    # 0-10 → -1 to +1: (score - 5) / 5
                    twitter_data['sentiment_score'] = (
                        result.get('score', 5) - 5) / 5
                    twitter_data['tweet_count'] = result.get('tweets', 0)
                    twitter_data['overall'] = result.get(
                        'sentiment', 'neutral').lower()
                    twitter_data['has_data'] = result.get('tweets', 0) > 0

                    print(f"   Sentiment: {twitter_data['overall'].upper()}")
                    print(f"   Score: {twitter_data['sentiment_score']:+.3f}")
                    print(f"   Tweets: {twitter_data['tweet_count']}")
                    print(f"   Impact: {result.get('impact', 'UNKNOWN')}")
                else:
                    print(f"   ⚠️ No Twitter data available")
            except Exception as e:
                print(f"   ⚠️ Twitter tracker error: {str(e)[:50]}")
        except Exception as e:
            print(f"   ❌ Error: {str(e)[:50]}")

        return twitter_data

    def get_vix_fear_gauge(self) -> Dict[str, Any]:
        """Analyze VIX (Market Fear Gauge)"""
        print("\n📊 VIX Fear Gauge Analysis...")
        vix_data = {'sentiment_score': 0.0, 'vix_level': 0.0,
                    'vix_change_pct': 0.0, 'market_fear': 'neutral', 'has_data': False}

        try:
            vix = yf.Ticker("^VIX").history(period="5d")

            if len(vix) >= 2:
                current_vix = float(vix['Close'].iloc[-1])
                prev_vix = float(vix['Close'].iloc[-2])
                vix_change = ((current_vix - prev_vix) / prev_vix) * 100

                vix_data['vix_level'] = current_vix
                vix_data['vix_change_pct'] = vix_change
                vix_data['has_data'] = True

                # VIX Interpretation:
                # < 12: Very low fear (extreme complacency) - caution
                # 12-15: Low fear (calm market) - bullish
                # 15-20: Normal fear - neutral
                # 20-30: Elevated fear - bearish
                # > 30: High fear (panic) - very bearish

                # Sentiment score based on VIX level
                if current_vix < 12:
                    # Complacency (slightly bullish but risky)
                    level_sentiment = 0.3
                    vix_data['market_fear'] = 'very_low'
                elif current_vix < 15:
                    level_sentiment = 0.5  # Calm (bullish)
                    vix_data['market_fear'] = 'low'
                elif current_vix < 20:
                    level_sentiment = 0.0  # Normal (neutral)
                    vix_data['market_fear'] = 'normal'
                elif current_vix < 30:
                    level_sentiment = -0.4  # Elevated (bearish)
                    vix_data['market_fear'] = 'elevated'
                else:
                    level_sentiment = -0.7  # Panic (very bearish)
                    vix_data['market_fear'] = 'high'

                # Sentiment based on VIX change (trending)
                if vix_change > 10:
                    trend_sentiment = -0.3  # Fear spiking (bearish)
                elif vix_change > 5:
                    trend_sentiment = -0.15  # Fear rising (slightly bearish)
                elif vix_change < -10:
                    trend_sentiment = 0.3  # Fear dropping (bullish)
                elif vix_change < -5:
                    trend_sentiment = 0.15  # Fear declining (slightly bullish)
                else:
                    trend_sentiment = 0.0  # Stable

                # Combined sentiment (60% level, 40% trend)
                vix_data['sentiment_score'] = (
                    level_sentiment * 0.6) + (trend_sentiment * 0.4)

                print(
                    f"   VIX Level: {current_vix:.2f} ({vix_data['market_fear'].upper()})")
                print(f"   VIX Change: {vix_change:+.2f}%")
                print(f"   Sentiment: {vix_data['sentiment_score']:+.3f}")

                if current_vix < 15:
                    print(f"   ✅ Low fear - Bullish for stocks")
                elif current_vix > 25:
                    print(f"   ⚠️ High fear - Bearish for stocks")
            else:
                print(f"   ⚠️ Insufficient VIX data")

        except Exception as e:
            print(f"   ❌ Error: {str(e)[:50]}")

        return vix_data

    def get_premarket_action(self) -> Dict[str, Any]:
        """Analyze Pre-Market Price Action"""
        print("\n🌅 Pre-Market Action Analysis...")
        premarket_data = {'sentiment_score': 0.0, 'premarket_change_pct': 0.0,
                          'volume_ratio': 0.0, 'direction': 'neutral', 'has_data': False}

        # Initialize hist early so it's available in all code paths
        hist = None

        try:
            # FIX #12: Use ticker.info for more reliable premarket price (CRITICAL FIX!)
            try:
                ticker = yf.Ticker(self.symbol)
                info = ticker.info

                # Get yesterday's close from info (more reliable)
                yesterday_close = info.get('previousClose', None)
                if not yesterday_close:
                    # Fallback to history
                    hist = yf.Ticker(self.symbol).history(period="5d")
                    if len(hist) < 2:
                        print(f"   ⚠️ Insufficient historical data")
                        return premarket_data
                    yesterday_close = float(hist['Close'].iloc[-2])
                else:
                    yesterday_close = float(yesterday_close)
                    # Also fetch hist for potential fallback use
                    hist = yf.Ticker(self.symbol).history(period="5d")

                # Try to get premarket price from info (most reliable)
                premarket_price = info.get('preMarketPrice', None)

                if premarket_price is not None and premarket_price > 0:
                    # Got live premarket price!
                    current_price = float(premarket_price)
                    premarket_change = (
                        (current_price - yesterday_close) / yesterday_close) * 100
                else:
                    # Fallback: Try interval method
                    premarket = ticker.history(
                        period="1d", interval="1m", prepost=True)

                    if not premarket.empty:
                        current_price = float(premarket['Close'].iloc[-1])
                        premarket_change = (
                            (current_price - yesterday_close) / yesterday_close) * 100
                    else:
                        raise Exception("No premarket data available")

                # Process the premarket data (common for both methods)
                premarket_data['premarket_change_pct'] = premarket_change
                premarket_data['has_data'] = True

                # Sentiment based on pre-market move
                # Pre-market often predicts opening direction
                if premarket_change > 1.5:
                    # Strong pre-market bullish
                    premarket_data['sentiment_score'] = 0.7
                    premarket_data['direction'] = 'strong_bullish'
                elif premarket_change > 0.5:
                    premarket_data['sentiment_score'] = 0.4  # Moderate bullish
                    premarket_data['direction'] = 'bullish'
                elif premarket_change > 0:
                    premarket_data['sentiment_score'] = 0.2  # Slightly bullish
                    premarket_data['direction'] = 'slightly_bullish'
                elif premarket_change < -1.5:
                    premarket_data['sentiment_score'] = -0.7  # Strong bearish
                    premarket_data['direction'] = 'strong_bearish'
                elif premarket_change < -0.5:
                    premarket_data['sentiment_score'] = - \
                        0.4  # Moderate bearish
                    premarket_data['direction'] = 'bearish'
                elif premarket_change < 0:
                    premarket_data['sentiment_score'] = -0.2  # Slightly bearish
                    premarket_data['direction'] = 'slightly_bearish'
                else:
                    premarket_data['sentiment_score'] = 0.0
                    premarket_data['direction'] = 'flat'

                print(f"   Pre-Market Change: {premarket_change:+.2f}%")
                print(f"   Direction: {premarket_data['direction'].upper()}")
                print(
                    f"   Sentiment: {premarket_data['sentiment_score']:+.3f}")

                if abs(premarket_change) > 1.0:
                    print(f"   📈 Significant pre-market move detected")

            except Exception as inner_e:
                # If pre-market unavailable, use yesterday's close to today momentum
                print(
                    f"   ⚠️ Pre-market data unavailable: {str(inner_e)[:50]}")

                # Ensure hist is available
                if hist is None or hist.empty:
                    hist = yf.Ticker(self.symbol).history(period="5d")

                if not hist.empty and len(hist) >= 1:
                    # Fallback: Use current regular hours price vs yesterday close
                    yesterday_close_fallback = float(
                        hist['Close'].iloc[-2]) if len(hist) >= 2 else float(hist['Close'].iloc[-1])
                    current_price = float(hist['Close'].iloc[-1])
                    change = ((current_price - yesterday_close_fallback) /
                              yesterday_close_fallback) * 100

                    # Use a dampened version since this is not true pre-market
                    premarket_data['sentiment_score'] = change / \
                        100 * 0.5  # Cap at -0.5 to +0.5
                    premarket_data['premarket_change_pct'] = change
                    premarket_data['has_data'] = True
                    premarket_data['direction'] = 'regular_hours'

                    print(f"   ⚠️ Using regular hours data (no pre-market available)")
                    print(f"   Recent Change: {change:+.2f}%")
                else:
                    print(f"   ⚠️ No historical data available for fallback")

        except Exception as e:
            print(f"   ❌ Error: {str(e)[:50]}")

        return premarket_data

    def get_analyst_ratings(self) -> Dict[str, Any]:
        """Analyze Analyst Ratings & Recommendations"""
        print("\n🎯 Analyst Ratings Analysis...")
        analyst_data = {'sentiment_score': 0.0, 'upgrades': 0, 'downgrades': 0,
                        'buy_rating': 0, 'hold_rating': 0, 'sell_rating': 0, 'has_data': False}

        try:
            # Try Finnhub first
            if self.api_keys['finnhub']:
                try:
                    url = f"https://finnhub.io/api/v1/stock/recommendation?symbol={self.symbol}&token={self.api_keys['finnhub']}"
                    response = requests.get(url, timeout=5)

                    if response.status_code == 200:
                        data = response.json()

                        if data and len(data) > 0:
                            # Get most recent recommendation (last 30 days)
                            recent = data[0]  # Most recent

                            analyst_data['buy_rating'] = recent.get(
                                'buy', 0) + recent.get('strongBuy', 0)
                            analyst_data['hold_rating'] = recent.get('hold', 0)
                            analyst_data['sell_rating'] = recent.get(
                                'sell', 0) + recent.get('strongSell', 0)
                            analyst_data['has_data'] = True

                            total_analysts = analyst_data['buy_rating'] + \
                                analyst_data['hold_rating'] + \
                                analyst_data['sell_rating']

                            if total_analysts > 0:
                                # Calculate sentiment based on analyst ratings
                                # Buy = +1, Hold = 0, Sell = -1
                                buy_score = analyst_data['buy_rating'] / \
                                    total_analysts
                                sell_score = analyst_data['sell_rating'] / \
                                    total_analysts

                                # Sentiment ranges from -1 (all sell) to +1 (all buy)
                                analyst_data['sentiment_score'] = buy_score - \
                                    sell_score

                                # Check for recent changes (compare to previous month if available)
                                if len(data) > 1:
                                    prev = data[1]
                                    prev_buy = prev.get(
                                        'buy', 0) + prev.get('strongBuy', 0)
                                    prev_sell = prev.get(
                                        'sell', 0) + prev.get('strongSell', 0)

                                    analyst_data['upgrades'] = max(
                                        0, analyst_data['buy_rating'] - prev_buy)
                                    analyst_data['downgrades'] = max(
                                        0, analyst_data['sell_rating'] - prev_sell)

                                print(f"   📊 Analyst Ratings:")
                                print(
                                    f"      Buy:  {analyst_data['buy_rating']} ({buy_score*100:.1f}%)")
                                print(
                                    f"      Hold: {analyst_data['hold_rating']}")
                                print(
                                    f"      Sell: {analyst_data['sell_rating']} ({sell_score*100:.1f}%)")
                                print(
                                    f"   Sentiment: {analyst_data['sentiment_score']:+.3f}")

                                if analyst_data['upgrades'] > 0:
                                    print(
                                        f"   ✅ Recent upgrades: {analyst_data['upgrades']}")
                                if analyst_data['downgrades'] > 0:
                                    print(
                                        f"   ⚠️ Recent downgrades: {analyst_data['downgrades']}")

                                return analyst_data

                except Exception as e:
                    print(f"   ⚠️ Finnhub error: {str(e)[:30]}")

            # Try FMP as backup
            if self.api_keys['fmp']:
                try:
                    url = f"https://financialmodelingprep.com/api/v3/rating/{self.symbol}?apikey={self.api_keys['fmp']}"
                    response = requests.get(url, timeout=5)

                    if response.status_code == 200:
                        data = response.json()

                        if data and len(data) > 0:
                            recent = data[0]
                            rating = recent.get('rating', '').lower()

                            # FMP ratings: Strong Buy, Buy, Hold, Sell, Strong Sell
                            if 'strong buy' in rating or 'buy' in rating:
                                analyst_data['sentiment_score'] = 0.7 if 'strong' in rating else 0.5
                                analyst_data['buy_rating'] = 1
                            elif 'hold' in rating:
                                analyst_data['sentiment_score'] = 0.0
                                analyst_data['hold_rating'] = 1
                            elif 'sell' in rating:
                                analyst_data['sentiment_score'] = - \
                                    0.7 if 'strong' in rating else -0.5
                                analyst_data['sell_rating'] = 1

                            analyst_data['has_data'] = True

                            print(f"   📊 FMP Rating: {rating.upper()}")
                            print(
                                f"   Sentiment: {analyst_data['sentiment_score']:+.3f}")

                            return analyst_data

                except Exception as e:
                    print(f"   ⚠️ FMP error: {str(e)[:30]}")

            print(f"   ⚠️ No analyst rating data available")

        except Exception as e:
            print(f"   ❌ Error: {str(e)[:50]}")

        return analyst_data

    def get_dxy_dollar_index(self) -> Dict[str, Any]:
        """Analyze Dollar Index (DXY) - Currency Impact"""
        print("\n💵 Dollar Index (DXY) Analysis...")
        dxy_data = {'sentiment_score': 0.0, 'dxy_level': 0.0,
                    'dxy_change_pct': 0.0, 'trend': 'neutral', 'has_data': False}

        try:
            # Get DXY (Dollar Index)
            dxy = yf.Ticker("DX-Y.NYB").history(period="10d")

            if len(dxy) >= 5:
                current_dxy = float(dxy['Close'].iloc[-1])
                week_ago_dxy = float(dxy['Close'].iloc[0])
                dxy_change = ((current_dxy - week_ago_dxy) /
                              week_ago_dxy) * 100

                dxy_data['dxy_level'] = current_dxy
                dxy_data['dxy_change_pct'] = dxy_change
                dxy_data['has_data'] = True

                # Dollar Index Interpretation for Tech Stocks:
                # Strong dollar = Headwind for exports (bearish)
                # Weak dollar = Tailwind for exports (bullish)
                #
                # AMD: ~40% international revenue
                # AVGO: ~50% international revenue

                if dxy_change > 2.0:
                    dxy_data['sentiment_score'] = - \
                        0.6  # Strong dollar = bearish
                    dxy_data['trend'] = 'strong_up'
                elif dxy_change > 1.0:
                    # Rising dollar = slightly bearish
                    dxy_data['sentiment_score'] = -0.3
                    dxy_data['trend'] = 'up'
                elif dxy_change > 0:
                    dxy_data['sentiment_score'] = -0.1  # Mild dollar strength
                    dxy_data['trend'] = 'slightly_up'
                elif dxy_change < -2.0:
                    dxy_data['sentiment_score'] = 0.6  # Weak dollar = bullish
                    dxy_data['trend'] = 'strong_down'
                elif dxy_change < -1.0:
                    # Falling dollar = slightly bullish
                    dxy_data['sentiment_score'] = 0.3
                    dxy_data['trend'] = 'down'
                elif dxy_change < 0:
                    dxy_data['sentiment_score'] = 0.1  # Mild dollar weakness
                    dxy_data['trend'] = 'slightly_down'
                else:
                    dxy_data['sentiment_score'] = 0.0
                    dxy_data['trend'] = 'flat'

                print(f"   DXY Level: {current_dxy:.2f}")
                print(f"   7-Day Change: {dxy_change:+.2f}%")
                print(f"   Trend: {dxy_data['trend'].upper()}")
                print(f"   Sentiment: {dxy_data['sentiment_score']:+.3f}")

                if abs(dxy_change) > 1.5:
                    print(f"   💵 Significant currency move detected")

            else:
                print(f"   ⚠️ Insufficient DXY data")

        except Exception as e:
            print(f"   ❌ Error: {str(e)[:50]}")

        return dxy_data

    def get_earnings_proximity(self) -> Dict[str, Any]:
        """Analyze Earnings Proximity - Volatility Adjustment"""
        print("\n📅 Earnings Proximity Analysis...")
        earnings_data = {'sentiment_score': 0.0, 'days_to_earnings': 999,
                         'volatility_multiplier': 1.0, 'is_earnings_week': False, 'has_data': False}

        try:
            # Try to get earnings date from yfinance
            ticker = yf.Ticker(self.symbol)

            # Get earnings calendar - handle different formats
            try:
                calendar = ticker.calendar
                next_earnings = None

                # Handle different calendar formats
                if calendar is not None:
                    # Format 1: DataFrame with 'Earnings Date' column
                    if hasattr(calendar, 'empty') and not calendar.empty:
                        if 'Earnings Date' in calendar:
                            next_earnings = calendar['Earnings Date']
                            if isinstance(next_earnings, list) and len(next_earnings) > 0:
                                next_earnings = next_earnings[0]
                    # Format 2: Dict with 'Earnings Date' key
                    elif isinstance(calendar, dict) and 'Earnings Date' in calendar:
                        earnings_date = calendar['Earnings Date']
                        if isinstance(earnings_date, list) and len(earnings_date) > 0:
                            next_earnings = earnings_date[0]
                        else:
                            next_earnings = earnings_date

                if next_earnings:
                    from datetime import datetime
                    import pytz
                    import pandas as pd

                    # Get current ET time
                    et_tz = pytz.timezone('US/Eastern')
                    now_et = datetime.now(et_tz)

                    # Use date-only comparison to avoid timezone/datetime issues
                    from datetime import date as dt_date

                    # Extract date from earnings data
                    if isinstance(next_earnings, pd.Timestamp):
                        earnings_date = next_earnings.date()
                    elif isinstance(next_earnings, datetime):
                        earnings_date = next_earnings.date()
                    elif isinstance(next_earnings, dt_date):
                        earnings_date = next_earnings
                    else:
                        raise ValueError(
                            f"Unexpected earnings date type: {type(next_earnings)}")

                    # Get today's date
                    today = now_et.date()

                    # Calculate days until earnings
                    days_to_earnings = (earnings_date - today).days
                    earnings_data['days_to_earnings'] = days_to_earnings
                    earnings_data['has_data'] = True

                    # Earnings Proximity Interpretation:
                    # < 3 days: Very high volatility, reduce confidence
                    # 3-7 days: High volatility, moderate caution
                    # 7-14 days: Elevated volatility
                    # > 14 days: Normal

                    if days_to_earnings < 0:
                        # Earnings just passed
                        earnings_data['sentiment_score'] = 0.0
                        earnings_data['volatility_multiplier'] = 1.0
                        print(f"   ✔️ Earnings recently passed")
                    elif days_to_earnings <= 3:
                        # Neutral direction
                        earnings_data['sentiment_score'] = 0.0
                        earnings_data['volatility_multiplier'] = 1.8
                        earnings_data['is_earnings_week'] = True
                        print(
                            f"   🚨 EARNINGS IN {days_to_earnings} DAYS - Very High Volatility!")
                        print(
                            f"   ⚠️ Volatility Multiplier: {earnings_data['volatility_multiplier']:.1f}x")
                    elif days_to_earnings <= 7:
                        earnings_data['sentiment_score'] = 0.0
                        earnings_data['volatility_multiplier'] = 1.5
                        earnings_data['is_earnings_week'] = True
                        print(
                            f"   📅 Earnings in {days_to_earnings} days - High Volatility")
                        print(
                            f"   ⚠️ Volatility Multiplier: {earnings_data['volatility_multiplier']:.1f}x")
                    elif days_to_earnings <= 14:
                        earnings_data['sentiment_score'] = 0.0
                        earnings_data['volatility_multiplier'] = 1.2
                        print(
                            f"   📅 Earnings in {days_to_earnings} days - Elevated Volatility")
                        print(
                            f"   Volatility Multiplier: {earnings_data['volatility_multiplier']:.1f}x")
                    else:
                        earnings_data['sentiment_score'] = 0.0
                        earnings_data['volatility_multiplier'] = 1.0
                        print(
                            f"   ✅ Earnings in {days_to_earnings} days - Normal period")

                    return earnings_data

            except Exception as inner_e:
                print(
                    f"   ⚠️ Could not fetch earnings calendar: {str(inner_e)[:30]}")

            # If we can't get earnings data, assume normal volatility
            print(f"   ℹ️ Earnings date not available - assuming normal period")
            earnings_data['has_data'] = False

        except Exception as e:
            print(f"   ❌ Error: {str(e)[:50]}")

        return earnings_data

    def get_short_interest(self) -> Dict[str, Any]:
        """Analyze Short Interest - Squeeze Potential"""
        print("\n🔺 Short Interest Analysis...")
        short_data = {'sentiment_score': 0.0, 'short_percent': 0.0,
                      'squeeze_potential': 'none', 'has_data': False}

        try:
            ticker = yf.Ticker(self.symbol)
            info = ticker.info

            if info:
                # Try to get short interest data
                # Convert to percentage
                short_percent = info.get('shortPercentOfFloat', 0) * 100

                if short_percent > 0:
                    short_data['short_percent'] = short_percent
                    short_data['has_data'] = True

                    # Short Interest Interpretation:
                    # Low (<5%): Normal, no squeeze potential
                    # Moderate (5-10%): Some squeeze potential if momentum up
                    # High (10-20%): Significant squeeze potential
                    # Very High (>20%): Extreme squeeze potential
                    #
                    # Combined with price momentum for sentiment

                    # Get recent price momentum
                    hist = yf.Ticker(self.symbol).history(period="5d")
                    if len(hist) >= 2:
                        recent_momentum = (
                            (hist['Close'].iloc[-1] - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2]) * 100

                        # High short interest + upward momentum = bullish (squeeze)
                        # High short interest + downward momentum = neutral to bearish

                        if short_percent < 5:
                            short_data['sentiment_score'] = 0.0
                            short_data['squeeze_potential'] = 'none'
                            print(
                                f"   Short Interest: {short_percent:.1f}% - Normal")
                        elif short_percent < 10:
                            if recent_momentum > 0:
                                # Mild squeeze potential
                                short_data['sentiment_score'] = 0.2
                                short_data['squeeze_potential'] = 'low'
                                print(
                                    f"   Short Interest: {short_percent:.1f}% - Moderate")
                                print(
                                    f"   ✅ Upward momentum + shorts = Mild squeeze potential")
                            else:
                                short_data['sentiment_score'] = - \
                                    0.1  # Shorts have control
                                short_data['squeeze_potential'] = 'none'
                                print(
                                    f"   Short Interest: {short_percent:.1f}% - Moderate")
                                print(
                                    f"   ⚠️ Downward momentum - Shorts in control")
                        elif short_percent < 20:
                            if recent_momentum > 1:
                                # Strong squeeze potential
                                short_data['sentiment_score'] = 0.5
                                short_data['squeeze_potential'] = 'high'
                                print(
                                    f"   Short Interest: {short_percent:.1f}% - HIGH 🟡")
                                print(
                                    f"   📈 Strong upward momentum - SHORT SQUEEZE POTENTIAL!")
                            elif recent_momentum > 0:
                                # Moderate squeeze
                                short_data['sentiment_score'] = 0.3
                                short_data['squeeze_potential'] = 'medium'
                                print(
                                    f"   Short Interest: {short_percent:.1f}% - HIGH")
                                print(f"   📈 Upward momentum - Squeeze building")
                            else:
                                short_data['sentiment_score'] = - \
                                    0.2  # Heavy shorting
                                short_data['squeeze_potential'] = 'none'
                                print(
                                    f"   Short Interest: {short_percent:.1f}% - HIGH")
                                print(f"   📉 Downward momentum - Shorts winning")
                        else:  # > 20%
                            if recent_momentum > 1:
                                # Extreme squeeze
                                short_data['sentiment_score'] = 0.8
                                short_data['squeeze_potential'] = 'extreme'
                                print(
                                    f"   Short Interest: {short_percent:.1f}% - EXTREME 🔴")
                                print(
                                    f"   🚀 Massive upward momentum - MAJOR SQUEEZE ALERT!")
                            elif recent_momentum > 0:
                                short_data['sentiment_score'] = 0.4
                                short_data['squeeze_potential'] = 'high'
                                print(
                                    f"   Short Interest: {short_percent:.1f}% - EXTREME")
                                print(f"   📈 Upward momentum - High squeeze risk")
                            else:
                                short_data['sentiment_score'] = - \
                                    0.3  # Very heavy shorting
                                short_data['squeeze_potential'] = 'none'
                                print(
                                    f"   Short Interest: {short_percent:.1f}% - EXTREME")
                                print(
                                    f"   📉 Downward momentum - Heavy short pressure")

                    print(
                        f"   Sentiment: {short_data['sentiment_score']:+.3f}")
                else:
                    print(f"   ⚠️ Short interest data not available")
            else:
                print(f"   ⚠️ Could not fetch stock info")

        except Exception as e:
            print(f"   ❌ Error: {str(e)[:50]}")

        return short_data

    def generate_comprehensive_prediction(self) -> Dict[str, Any]:
        """Generate prediction"""
        print("\n" + "="*80)
        print(f"🚀 COMPREHENSIVE NEXT-DAY PREDICTION ENGINE - {self.symbol}")
        print("="*80)

        et_tz = pytz.timezone('US/Eastern')
        now_et = datetime.now(et_tz)
        print(f"⏰ {now_et.strftime('%Y-%m-%d %I:%M %p ET')}")

        # FIX #13: Get LIVE current price for INTRADAY trading (CRITICAL!)
        ticker = yf.Ticker(self.symbol)
        info = ticker.info
        hist = ticker.history(period="5d")

        # Determine if market is open (9:30 AM - 4:00 PM ET, Mon-Fri)
        market_open_time = now_et.replace(
            hour=9, minute=30, second=0, microsecond=0)
        market_close_time = now_et.replace(
            hour=16, minute=0, second=0, microsecond=0)
        is_market_hours = (now_et.weekday() < 5 and
                           market_open_time <= now_et <= market_close_time)

        try:
            if is_market_hours:
                # During market hours: Use LIVE current price
                current_price = info.get(
                    'regularMarketPrice', None) or info.get('currentPrice', None)
                if current_price:
                    current_price = float(current_price)
                    print(f"💰 {self.symbol}: ${current_price:.2f} (LIVE)")
                else:
                    # Fallback to last close
                    if not hist.empty and 'Close' in hist.columns and not hist['Close'].empty:
                        current_price = float(hist['Close'].iloc[-1])
                        print(f"💰 {self.symbol}: ${current_price:.2f} (from history)")
                    else:
                        raise ValueError(f"No historical close price available for {self.symbol}")
            else:
                # Outside market hours: Use last close
                if not hist.empty and 'Close' in hist.columns and not hist['Close'].empty:
                    current_price = float(hist['Close'].iloc[-1])
                    print(f"💰 {self.symbol}: ${current_price:.2f}")
                else:
                    raise ValueError(f"No historical close price available for {self.symbol}")
        except (ValueError, IndexError) as e:
            print(f"❌ Error fetching price for {self.symbol}: {str(e)}")
            return None

        # Calculate TODAY's intraday change (critical for intraday trading!)
        today_open = info.get('regularMarketOpen',
                              None) or info.get('open', None)
        if today_open and is_market_hours:
            today_open = float(today_open)
            intraday_change_pct = (
                (current_price - today_open) / today_open) * 100
            print(
                f"📊 Today's Move: {intraday_change_pct:+.2f}% (Open: ${today_open:.2f})")
            if abs(intraday_change_pct) > 2:
                if intraday_change_pct > 0:
                    print(f"   ✅ Strong intraday rally detected")
                else:
                    print(f"   ⚠️ Strong intraday selloff detected")
        else:
            intraday_change_pct = 0
            today_open = None

        # Collect all data (now 14 sources - Phase 1 + Phase 2 enhancement)
        news = self.get_news_sentiment()
        futures = self.get_futures_sentiment()
        options = self.get_options_flow()
        technical = self.get_technical_analysis()
        sector = self.get_sector_analysis()
        reddit = self.get_reddit_sentiment()
        twitter = self.get_twitter_sentiment()
        vix = self.get_vix_fear_gauge()                   # Phase 1
        premarket = self.get_premarket_action()           # Phase 1

        # FIX #8: Track premarket price but DON'T replace current_price!
        # current_price = TODAY's close (reference for target calculation)
        # premarket_price = TOMORROW's premarket (used for gap detection only)
        base_price = current_price  # TODAY's closing price - this is our reference

        if premarket.get('has_data', False):
            premarket_change_pct = premarket.get('premarket_change_pct', 0)
            if abs(premarket_change_pct) > 0.5:  # Significant move
                # Calculate what premarket price would be (for information only)
                premarket_price = base_price * (1 + premarket_change_pct / 100)
                print(f"\n📊 PREMARKET GAP DETECTED:")
                print(f"   Today's Close: ${base_price:.2f}")
                print(
                    f"   Premarket Next Day: ${premarket_price:.2f} ({premarket_change_pct:+.2f}%)")
                print(f"   Gap: {premarket_change_pct:+.2f}%")
                print(
                    f"   💡 Using close price (${base_price:.2f}) as reference for target calculation")
                # Do NOT replace current_price - it should remain as today's close

        analyst_ratings = self.get_analyst_ratings()      # Phase 1
        dxy = self.get_dxy_dollar_index()                 # Phase 2 NEW
        earnings_proximity = self.get_earnings_proximity()  # Phase 2 NEW
        short_interest = self.get_short_interest()        # Phase 2 NEW
        institutional = self.get_institutional_flow()

        try:
            vwap_info = calculate_vwap(self.symbol)
        except Exception:
            vwap_info = {
                'success': False,
                'vwap_distance_pct': 0.0,
                'volume_ratio': 1.0,
            }

        # Phase 3 Enhancement: Hidden Edge Signals (8 alternative sources)
        if HIDDEN_EDGE_AVAILABLE:
            try:
                edge_engine = HiddenEdgeEngine(self.symbol)
                hidden_edge = edge_engine.collect_all_signals()
            except Exception as e:
                print(f"   ⚠️ Hidden Edge error: {str(e)[:50]}")
                hidden_edge = {'composite_score': 0.0, 'has_data': False}
        else:
            hidden_edge = {'composite_score': 0.0, 'has_data': False}

        # Phase 4 Enhancement: Additional Signals (3 free high-quality signals)
        # These help break ties and increase confidence on mixed signal days
        if ADDITIONAL_SIGNALS_AVAILABLE:
            try:
                additional_engine = AdditionalSignals(self.symbol)
                additional_results = additional_engine.get_all_signals()

                # Extract individual signals
                relative_strength = additional_results['relative_strength']
                money_flow = additional_results['money_flow_index']
                bollinger = additional_results['bollinger_bands']
            except Exception as e:
                print(f"   ⚠️ Additional Signals error: {str(e)[:50]}")
                relative_strength = {'score': 0.0, 'has_data': False}
                money_flow = {'score': 0.0, 'has_data': False}
                bollinger = {'score': 0.0, 'has_data': False}
        else:
            relative_strength = {'score': 0.0, 'has_data': False}
            money_flow = {'score': 0.0, 'has_data': False}
            bollinger = {'score': 0.0, 'has_data': False}

        # Phase 5 Enhancement: Stock-Specific Enhancements (AMD & NVDA)
        # Advanced indicators for improved accuracy
        if ENHANCEMENTS_AVAILABLE and self.symbol in ['AMD', 'NVDA']:
            try:
                enhancements_engine = StockSpecificEnhancements(self.symbol)
                enhancements = enhancements_engine.get_all_enhancements()
            except Exception as e:
                print(f"   ⚠️ Enhancements error: {str(e)[:50]}")
                enhancements = {}
        else:
            enhancements = {}

        # Track data quality (now 18 sources: 14 original + 1 hidden edge + 3 additional)
        data_sources_active = sum([
            news.get('has_data', False),
            futures.get('has_data', False),
            vix.get('has_data', False),              # Phase 1
            premarket.get('has_data', False),        # Phase 1
            analyst_ratings.get('has_data', False),  # Phase 1
            dxy.get('has_data', False),              # Phase 2 NEW
            earnings_proximity.get('has_data', False),  # Phase 2 NEW
            short_interest.get('has_data', False),   # Phase 2 NEW
            # Phase 3 NEW (composite of 8 alt sources)
            hidden_edge.get('has_data', False),
            relative_strength.get('has_data', False),  # Phase 4 NEW
            money_flow.get('has_data', False),         # Phase 4 NEW
            bollinger.get('has_data', False),          # Phase 4 NEW
            1,  # Options always tries
            1,  # Technical always tries
            1,  # Sector always tries
            1,  # Reddit always tries
            1,  # Twitter always tries
            1,  # Institutional always tries
        ])
        data_quality_pct = (data_sources_active / 18) * \
            100  # Now 18 sources (was 15)

        # Calculate prediction
        print("\n" + "="*80)
        print("🎯 PREDICTION CALCULATION")
        print("="*80)

        # Use stock-specific weight adjustments
        weights = self.weight_adjustments

        print(f"\n⚖️ Using {self.symbol}-specific weights:")
        for factor, weight in sorted(weights.items(), key=lambda x: x[1], reverse=True):
            print(
                f"   {factor.capitalize():15s} {weight:.2f} ({weight*100:.0f}%)")

        news_score = news['overall_score'] * weights['news']
        # FIX: Don't divide by 100 - futures already in proper range for scoring
        # Futures of +1% should contribute meaningfully (not just 0.002)
        # Divide by 10 instead of 100
        futures_score = (futures['overall_sentiment'] /
                         10) * weights['futures']
        options_score = weights['options'] if options['sentiment'] == 'bullish' else - \
            weights['options'] if options['sentiment'] == 'bearish' else 0

        # FIX: Technical scoring must be symmetric to avoid bias
        # OLD: technical_score = weights['technical'] if technical['trend'] == 'uptrend' else -weights['technical']
        # This was BIASED - neutral trends got negative score!
        if technical['trend'] == 'uptrend':
            technical_score = weights['technical']
        elif technical['trend'] == 'downtrend':
            technical_score = -weights['technical']
        else:  # neutral
            technical_score = 0.0

        # MACD adjustment (symmetric)
        if technical['macd_signal'] == 'bullish':
            technical_score += weights['technical'] * 0.3
        elif technical['macd_signal'] == 'bearish':
            technical_score -= weights['technical'] * 0.3

        # RSI OVERBOUGHT/OVERSOLD ADJUSTMENT (FIXED - lowered thresholds)
        # High RSI = overbought = BEARISH (reversal risk)
        # Low RSI = oversold = BULLISH (bounce opportunity)
        # FIX: Changed thresholds from 70/30 to 65/35 for earlier reversal detection
        rsi = technical.get('rsi', 50)
        if rsi > 65:  # FIXED: Was 70, now 65
            # Overbought - bearish reversal risk
            rsi_penalty = min((rsi - 65) / 35, 1.0) * \
                weights['technical'] * 0.5
            technical_score -= rsi_penalty
            if rsi > 70:  # FIXED: Was 75, now 70
                print(
                    f"   ⚠️ RSI {rsi:.1f} OVERBOUGHT - Bearish penalty: -{rsi_penalty:.3f}")
        elif rsi < 35:  # FIXED: Was 30, now 35
            # Oversold - bullish bounce opportunity
            rsi_boost = min((35 - rsi) / 35, 1.0) * weights['technical'] * 0.5
            technical_score += rsi_boost
            if rsi < 30:  # FIXED: Was 25, now 30
                print(
                    f"   💡 RSI {rsi:.1f} OVERSOLD - Bullish boost: +{rsi_boost:.3f}")

        # FIX #5: Apply mean reversion adjustment
        mean_reversion = technical.get('mean_reversion_signal', 'none')
        if mean_reversion == 'bearish':
            # Multiple up days + high RSI = reversal likely
            reversion_penalty = weights['technical'] * 0.4
            technical_score -= reversion_penalty
            print(f"   ⚠️ Mean Reversion penalty: -{reversion_penalty:.3f}")
        elif mean_reversion == 'bullish':
            # Multiple down days + low RSI = bounce likely
            reversion_boost = weights['technical'] * 0.4
            technical_score += reversion_boost
            print(f"   💡 Mean Reversion boost: +{reversion_boost:.3f}")

        sector_score = sector['sector_sentiment'] * weights['sector']
        reddit_score = reddit['sentiment_score'] * weights['reddit']
        twitter_score = twitter['sentiment_score'] * weights['twitter']
        # Phase 1 scores
        vix_score = vix['sentiment_score'] * weights['vix']
        premarket_score = premarket['sentiment_score'] * weights['premarket']
        analyst_score = analyst_ratings['sentiment_score'] * \
            weights['analyst_ratings']
        # Phase 2 scores NEW
        dxy_score = dxy['sentiment_score'] * weights['dxy']
        earnings_score = earnings_proximity['sentiment_score'] * \
            weights['earnings_proximity']
        short_score = short_interest['sentiment_score'] * \
            weights['short_interest']
        institutional_score = institutional['signal_strength'] * \
            weights['institutional']
        # Phase 3 score NEW (Hidden Edge composite)
        hidden_edge_score = hidden_edge.get(
            'composite_score', 0.0) * weights.get('hidden_edge', 0.10)

        # FIX #14: INTRADAY MOMENTUM SCORE (NEW - for intraday trading!)
        # This captures TODAY's actual price action
        intraday_score = 0
        if 'intraday_change_pct' in locals() and today_open:
            if intraday_change_pct < -2:  # Selloff today
                # Strong bearish signal - stock rejecting current levels
                intraday_score = (intraday_change_pct / 10) * \
                    0.08  # Weight: 8%
            elif intraday_change_pct > 2:  # Rally today
                # Check if overbought (reversal risk)
                if technical.get('rsi', 50) > 65:
                    # Rally + overbought = exhaustion
                    intraday_score = -(intraday_change_pct / 20) * 0.08
                else:
                    # Healthy rally
                    intraday_score = (intraday_change_pct / 10) * 0.08

        vwap_score = 0.0
        if vwap_info.get('success'):
            vwap_distance_pct = float(vwap_info.get('vwap_distance_pct', 0.0) or 0.0)
            vwap_volume_ratio = float(vwap_info.get('volume_ratio', 1.0) or 1.0)
            if abs(vwap_distance_pct) > 0.5:
                magnitude = min(abs(vwap_distance_pct) / 5.0, 0.08) * weights['technical']
                if vwap_distance_pct > 0:
                    vwap_score = magnitude
                else:
                    vwap_score = -magnitude
                if vwap_volume_ratio < 0.8:
                    vwap_score *= 0.5
                elif vwap_volume_ratio > 1.5:
                    vwap_score *= 1.2

        time_of_day_score = 0.0
        if 'is_market_hours' in locals() and is_market_hours:
            hour_float = now_et.hour + now_et.minute / 60.0
            if 9.5 <= hour_float <= 10.5:
                time_of_day_score = intraday_score * 0.25
            elif 12.0 <= hour_float <= 13.5:
                time_of_day_score = -abs(intraday_score) * 0.30
            elif hour_float >= 15.0:
                time_of_day_score = intraday_score * 0.20

        # Phase 4: Additional Signals Scoring (3 new signals)
        # These directly use their calculated scores (already normalized)
        relative_strength_score = relative_strength.get(
            'score', 0.0)  # Already 0.03-0.06 range
        # Already 0.02-0.05 range
        money_flow_score = money_flow.get('score', 0.0)
        # Already 0.02-0.04 range
        bollinger_score = bollinger.get('score', 0.0)
        # Total weight from these 3: ~0.05-0.15 (5-15%) - helps break ties!

        # Phase 5: Stock-Specific Enhancements Scoring (AMD & NVDA)
        enhancements_total = 0.0
        if enhancements:
            # NVDA: Relative strength vs SMH
            if 'relative_strength_smh' in enhancements and enhancements['relative_strength_smh'].get('has_data', False):
                nvda_rs_score = enhancements['relative_strength_smh'].get(
                    'score', 0.0)
                enhancements_total += nvda_rs_score

            # AMD: 200-day MA distance
            if 'ma200_distance' in enhancements and enhancements['ma200_distance'].get('has_data', False):
                amd_ma_score = enhancements['ma200_distance'].get('score', 0.0)
                enhancements_total += amd_ma_score

            # Both: Hyperscaler CapEx trend
            if 'hyperscaler_capex' in enhancements and enhancements['hyperscaler_capex'].get('has_data', False):
                capex_score = enhancements['hyperscaler_capex'].get(
                    'score', 0.0)
                enhancements_total += capex_score

        # Calculate base total score first (before pattern adjustment)
        base_total_score = news_score + futures_score + options_score + technical_score + sector_score + reddit_score + twitter_score + vix_score + premarket_score + analyst_score + dxy_score + \
            earnings_score + short_score + institutional_score + hidden_edge_score + intraday_score + vwap_score + time_of_day_score + \
            relative_strength_score + money_flow_score + \
            bollinger_score + enhancements_total

        # Phase 6: Get pattern adjustment (needs base score for direction)
        pattern_adjustment_score = 0.0
        pattern_adjustment = {'adjustment': 0.0,
                              'warnings': [], 'capacity_limits': {}}
        if PATTERN_KNOWLEDGE_AVAILABLE and self.symbol in ['AMD', 'NVDA', 'PLTR']:
            try:
                pattern_detector = RealTimePatternDetector(self.symbol)
                pattern_analysis = pattern_detector.analyze_current_conditions()

                if pattern_analysis.get('has_data', False):
                    # Get prediction adjustment based on patterns
                    pattern_adjustment_result = pattern_detector.get_prediction_adjustment({
                        'direction': 'UP' if base_total_score > 0 else 'DOWN',
                        'confidence': 50 + abs(base_total_score) * 233
                    })
                    pattern_adjustment_score = pattern_adjustment_result.get(
                        'adjustment', 0.0)
                    pattern_adjustment = pattern_adjustment_result  # Store for display

                    # Display pattern insights
                    if pattern_analysis.get('normal_behavior', {}).get('status') == 'abnormal':
                        print(f"\n   ⚠️ ABNORMAL BEHAVIOR DETECTED:")
                        for reason in pattern_analysis['normal_behavior'].get('reasons', []):
                            print(f"      • {reason}")

                    if pattern_analysis.get('capacity_analysis', {}).get('capacity_warning'):
                        print(f"\n   ⚠️ CAPACITY WARNING:")
                        print(
                            f"      {pattern_analysis['capacity_analysis']['capacity_warning']}")

                    pump_dump = pattern_analysis.get('pump_dump_signals', {})
                    if pump_dump.get('pump_likely', False):
                        print(
                            f"\n   🚀 PUMP SIGNAL DETECTED (Score: {pump_dump.get('pump_score', 0):.2f})")
                        if pump_dump.get('pump_triggers'):
                            print(
                                f"      Triggers: {', '.join(pump_dump['pump_triggers'])}")

                    if pump_dump.get('dump_likely', False):
                        print(
                            f"\n   📉 DUMP SIGNAL DETECTED (Score: {pump_dump.get('dump_score', 0):.2f})")
                        if pump_dump.get('dump_triggers'):
                            print(
                                f"      Triggers: {', '.join(pump_dump['dump_triggers'])}")
            except Exception as e:
                print(f"   ⚠️ Pattern knowledge error: {str(e)[:50]}")
                pattern_adjustment_score = 0.0
                pattern_adjustment = {'adjustment': 0.0,
                                      'warnings': [], 'capacity_limits': {}}

        # Final total score with pattern adjustment
        total_score = base_total_score + pattern_adjustment_score

        print(f"\n📊 Scores:")
        print(f"   Analyst Ratings: {analyst_score:+.3f}")
        print(f"   Pre-Market:   {premarket_score:+.3f}")
        print(f"   VIX:          {vix_score:+.3f}")
        print(f"   Earnings Prox: {earnings_score:+.3f}")
        print(f"   Short Interest: {short_score:+.3f}")
        print(f"   DXY:          {dxy_score:+.3f}")
        print(f"   News:         {news_score:+.3f}")
        print(f"   Futures:      {futures_score:+.3f}")
        print(f"   Options:      {options_score:+.3f}")
        print(f"   Technical:    {technical_score:+.3f}")
        print(f"   Sector:       {sector_score:+.3f}")
        print(f"   Reddit:       {reddit_score:+.3f}")
        print(f"   Twitter:      {twitter_score:+.3f}")
        print(f"   Institutional: {institutional_score:+.3f}")
        if HIDDEN_EDGE_AVAILABLE and hidden_edge.get('has_data', False):
            print(f"   Hidden Edge:  {hidden_edge_score:+.3f} (8 alt sources)")
        if intraday_score != 0:
            print(
                f"   Intraday:     {intraday_score:+.3f} (TODAY's move: {intraday_change_pct:+.2f}%)")
        if vwap_score != 0.0:
            print(f"   VWAP:         {vwap_score:+.3f}")
        if time_of_day_score != 0.0:
            print(f"   Session Time: {time_of_day_score:+.3f}")
        # Phase 4: Display additional signals
        if ADDITIONAL_SIGNALS_AVAILABLE:
            additional_total = relative_strength_score + money_flow_score + bollinger_score
            if abs(additional_total) > 0.001:  # Only show if significant
                print(f"   --- Additional Signals (Phase 4) ---")
                if abs(relative_strength_score) > 0.001:
                    print(f"   Rel. Strength: {relative_strength_score:+.3f}")
                if abs(money_flow_score) > 0.001:
                    print(f"   Money Flow:   {money_flow_score:+.3f}")
                if abs(bollinger_score) > 0.001:
                    print(f"   Bollinger:    {bollinger_score:+.3f}")
                print(
                    f"   Additional Total: {additional_total:+.3f} (helps break ties!)")

        # Phase 5: Display stock-specific enhancements
        if enhancements and abs(enhancements_total) > 0.001:
            print(f"   --- Stock-Specific Enhancements (Phase 5) ---")
            if self.symbol == 'NVDA':
                if 'relative_strength_smh' in enhancements and enhancements['relative_strength_smh'].get('has_data', False):
                    print(
                        f"   NVDA vs SMH: {enhancements['relative_strength_smh'].get('score', 0.0):+.3f}")
            if self.symbol == 'AMD':
                if 'ma200_distance' in enhancements and enhancements['ma200_distance'].get('has_data', False):
                    print(
                        f"   AMD 200MA: {enhancements['ma200_distance'].get('score', 0.0):+.3f}")
            if 'hyperscaler_capex' in enhancements and enhancements['hyperscaler_capex'].get('has_data', False):
                print(
                    f"   Hyperscaler CapEx: {enhancements['hyperscaler_capex'].get('score', 0.0):+.3f}")
            print(f"   Enhancements Total: {enhancements_total:+.3f}")

        # Phase 6: Display pattern knowledge adjustments
        if PATTERN_KNOWLEDGE_AVAILABLE and self.symbol in ['AMD', 'NVDA', 'PLTR'] and abs(pattern_adjustment_score) > 0.001:
            print(f"   --- Pattern Knowledge (Phase 6) ---")
            print(f"   Pattern Adjustment: {pattern_adjustment_score:+.3f}")
            if pattern_adjustment.get('warnings'):
                for warning in pattern_adjustment['warnings']:
                    print(f"   {warning}")
            if pattern_adjustment.get('capacity_limits'):
                caps = pattern_adjustment['capacity_limits']
                print(
                    f"   Capacity Limits: +{caps.get('max_up', 0):.2f}% / {caps.get('max_down', 0):.2f}%")

        print(f"   " + "-"*40)
        print(f"   TOTAL (raw):  {total_score:+.3f}")

        # FIX #3: REVERSAL DETECTION (Contrarian Logic)
        # When everything is extremely bullish, it's often a top signal
        reversal_detected = False
        if total_score > 0.25:  # Very bullish reading
            rsi = technical.get('rsi', 50)
            is_overbought = rsi > 65
            is_options_bullish = options['sentiment'] == 'bullish'
            is_news_very_positive = news.get('overall_score', 0) > 0.6

            if is_overbought and is_options_bullish and is_news_very_positive:
                reversal_detected = True
                print(f"\n   ⚠️ REVERSAL RISK DETECTED:")
                print(
                    f"      RSI: {rsi:.1f} (overbought)")
                print(
                    f"      Options: Bullish (P/C: {options.get('put_call_ratio', 0):.2f})")
                print(
                    f"      News: Very positive ({news.get('overall_score', 0):.2f})")
                print(f"      → Applying contrarian penalty")

                # Apply strong reversal penalty
                reversal_penalty = total_score * 0.40  # Reduce by 40%
                total_score -= reversal_penalty
                print(f"      Penalty: -{reversal_penalty:.3f}")

        # FIX #6: EXTREME READING PENALTY
        # Extreme scores (> 0.30) often precede reversals - dampen them
        original_score = total_score
        if total_score > 0.30:
            # Apply diminishing returns above 0.30
            excess = total_score - 0.30
            dampened_excess = excess * 0.50  # Cut excess in half
            total_score = 0.30 + dampened_excess
            print(f"\n   📉 EXTREME BULLISH READING - Dampened:")
            print(
                f"      Original: {original_score:+.3f} → Adjusted: {total_score:+.3f}")
        elif total_score < -0.30:
            # Apply diminishing returns below -0.30
            excess = abs(total_score) - 0.30
            dampened_excess = excess * 0.50  # Cut excess in half
            total_score = -0.30 - dampened_excess
            print(f"\n   📈 EXTREME BEARISH READING - Dampened:")
            print(
                f"      Original: {original_score:+.3f} → Adjusted: {total_score:+.3f}")

        if total_score != original_score:
            print(f"   TOTAL (adjusted): {total_score:+.3f}")

        # FIX #15: RED CLOSE DISTRIBUTION DETECTION (NEW!)
        # Detect when stock closes RED near daily lows despite bullish fundamentals
        # This indicates DISTRIBUTION (smart money selling) and often precedes further weakness
        try:
            # Get today's OHLC data
            today_hist = ticker.history(period='1d')
            if not today_hist.empty:
                today_open = float(today_hist['Open'].iloc[-1])
                today_high = float(today_hist['High'].iloc[-1])
                today_low = float(today_hist['Low'].iloc[-1])
                today_close = float(today_hist['Close'].iloc[-1])

                # Calculate intraday metrics
                intraday_change_pct = (
                    (today_close - today_open) / today_open) * 100
                daily_range = today_high - today_low

                if daily_range > 0:
                    # Where did it close in the range? 0% = low, 100% = high
                    close_position = (today_close - today_low) / daily_range

                    # Check for RED CLOSE DISTRIBUTION pattern
                    if intraday_change_pct < -1.0:  # Closed down more than 1%
                        if close_position < 0.30:  # Closed in bottom 30% of range
                            # This is DISTRIBUTION - selling pressure dominated
                            distribution_penalty = -0.05

                            # Check for DIVERGENCE (bullish fundamentals, weak price)
                            divergence_detected = False

                            # If options bullish but price weak = smart money selling
                            if options_score > 0.05:
                                divergence_detected = True
                                divergence_penalty = -0.05
                                distribution_penalty += divergence_penalty

                            # If news bullish but price weak = news already priced in, now selling
                            if news_score > 0.05:
                                if not divergence_detected:  # Don't double count
                                    divergence_detected = True
                                    divergence_penalty = -0.03
                                    distribution_penalty += divergence_penalty

                            total_score += distribution_penalty

                            print(f"\n   🚨 RED CLOSE DISTRIBUTION DETECTED:")
                            print(
                                f"      Today's Close: {intraday_change_pct:+.2f}% (RED)")
                            print(
                                f"      Close Position: {close_position*100:.0f}% of range (NEAR LOW)")
                            print(
                                f"      → This indicates DISTRIBUTION (selling pressure)")

                            if divergence_detected:
                                print(
                                    f"      ⚠️ DIVERGENCE: Bullish fundamentals but weak price action")
                                print(
                                    f"      → Smart money may be selling into strength")

                            print(
                                f"      Distribution Penalty: {distribution_penalty:.3f}")
                            print(
                                f"   TOTAL (after distribution): {total_score:+.3f}")

                    # Opposite: GREEN close near HIGH = accumulation (reinforce bullish)
                    elif intraday_change_pct > 1.0:  # Closed up more than 1%
                        if close_position > 0.70:  # Closed in top 30% of range
                            # This is ACCUMULATION - buying pressure dominated
                            # Don't add penalty, but note it in output
                            print(f"\n   ✅ GREEN CLOSE ACCUMULATION:")
                            print(
                                f"      Today's Close: {intraday_change_pct:+.2f}% (GREEN)")
                            print(
                                f"      Close Position: {close_position*100:.0f}% of range (NEAR HIGH)")
                            print(
                                f"      → Buying pressure strong (bullish confirmation)")

        except Exception as e:
            # If can't get intraday data, skip this fix
            pass

        # FIX #7: PREMARKET GAP OVERRIDE (NEW!)
        # If RSI overbought AND premarket gapping down = VERY BEARISH
        # This catches situations where options/news are stale but market is rejecting
        # EXCEPTION: If fundamentals are very strong, skip this and let bounce logic handle it
        rsi = technical.get('rsi', 50)
        premarket_change = premarket.get('premarket_change_pct', 0)

        # Calculate fundamental strength for override decision
        fundamental_strength_check = 0
        if news_score != 0:
            fundamental_strength_check += news_score
        if options_score != 0:
            fundamental_strength_check += options_score
        if analyst_score != 0:
            fundamental_strength_check += analyst_score
        fundamental_avg_check = fundamental_strength_check / \
            3 if fundamental_strength_check != 0 else 0

        # Debug: Show fundamental check
        if abs(premarket_change) > 1.0 and rsi > 65:
            print(
                f"\n🔍 FUNDAMENTAL CHECK: {fundamental_avg_check:.3f} (news={news_score:+.3f}, opt={options_score:+.3f}, analyst={analyst_score:+.3f})")
            print(
                f"   Overbought override will {'SKIP' if fundamental_avg_check >= 0.03 else 'APPLY'} (threshold 0.03)")

        # Overbought + gap down + weak fundamentals
        if rsi > 65 and premarket_change < -1.0 and fundamental_avg_check < 0.03:
            # Calculate gap penalty proportional to gap size
            gap_penalty = abs(premarket_change) * 0.03  # 3% penalty per 1% gap

            # ADDITIONAL: Discount stale bullish signals (news/options from yesterday)
            # When market gaps down, yesterday's bullish news/options are outdated
            stale_discount = 0
            if news_score > 0:
                # Reduce by 80% (AGGRESSIVE)
                stale_reduction = news_score * 0.80
                stale_discount += stale_reduction
            if options_score > 0:
                stale_reduction = options_score * \
                    0.80  # Reduce by 80% (AGGRESSIVE)
                stale_discount += stale_reduction

            total_penalty = gap_penalty + stale_discount
            total_score -= total_penalty

            print(f"\n   ⚠️ PREMARKET GAP DOWN OVERRIDE:")
            print(f"      RSI: {rsi:.1f} (overbought)")
            print(f"      Premarket Gap: {premarket_change:+.2f}%")
            print(f"      → Market rejecting rally despite bullish signals")
            print(f"      Gap Penalty: -{gap_penalty:.3f}")
            if stale_discount > 0:
                print(
                    f"      Stale Data Discount: -{stale_discount:.3f} (80% discount on stale bullish data)")
            print(f"      Total Penalty: -{total_penalty:.3f}")
            print(f"   TOTAL (after gap): {total_score:+.3f}")
        elif rsi < 35 and premarket_change > 1.0:  # Oversold + gap up > 1%
            # Bullish gap override (bounce confirmation)
            gap_boost = premarket_change * 0.03  # 3% boost per 1% gap

            # SYMMETRIC LOGIC: Discount stale bearish signals (news/options from yesterday)
            # When market gaps up from oversold, yesterday's bearish news/options are outdated
            stale_discount = 0
            if news_score < 0:
                stale_reduction = abs(news_score) * \
                    0.80  # Reduce bearish impact by 80%
                stale_discount += stale_reduction
                news_contribution_removed = news_score * 0.80  # What we're removing
                total_score -= news_contribution_removed  # Remove 80% of bearish contribution
            if options_score < 0:
                stale_reduction = abs(options_score) * \
                    0.80  # Reduce bearish impact by 80%
                stale_discount += stale_reduction
                options_contribution_removed = options_score * 0.80  # What we're removing
                # Remove 80% of bearish contribution
                total_score -= options_contribution_removed

            total_boost = gap_boost + stale_discount
            total_score += gap_boost  # Add the gap boost

            print(f"\n   💡 PREMARKET GAP UP OVERRIDE:")
            print(f"      RSI: {rsi:.1f} (oversold)")
            print(f"      Premarket Gap: {premarket_change:+.2f}%")
            print(f"      → Market confirming bounce despite bearish signals")
            print(f"      Gap Boost: +{gap_boost:.3f}")
            if stale_discount > 0:
                print(
                    f"      Stale Data Discount: +{stale_discount:.3f} (80% discount on stale bearish data)")
            print(f"      Total Boost: +{total_boost:.3f}")
            print(f"   TOTAL (after gap): {total_score:+.3f}")

        # SYMMETRIC: UNIVERSAL GAP UP LOGIC (NEW!)
        # Even without oversold RSI, a big gap up shows market strength
        # Apply a boost and discount stale bearish signals (symmetric to gap down logic)
        elif premarket_change > 1.5:  # Any gap up > 1.5% regardless of RSI
            # Boost (2% per 1% gap, symmetric to gap down)
            gap_boost = premarket_change * 0.02

            # Discount stale bearish signals (symmetric to bullish discount on gap down)
            stale_discount = 0
            if news_score < 0:
                stale_reduction = abs(news_score) * \
                    0.60  # Reduce bearish impact by 60%
                stale_discount += stale_reduction
                news_contribution_removed = news_score * 0.60
                total_score -= news_contribution_removed  # Remove 60% of bearish contribution
            if options_score < 0:
                stale_reduction = abs(options_score) * \
                    0.60  # Reduce bearish impact by 60%
                stale_discount += stale_reduction
                options_contribution_removed = options_score * 0.60
                # Remove 60% of bearish contribution
                total_score -= options_contribution_removed

            total_boost = gap_boost + stale_discount
            total_score += gap_boost  # Add the gap boost

            print(f"\n   📈 SIGNIFICANT GAP UP DETECTED:")
            print(f"      Premarket Gap: {premarket_change:+.2f}%")
            print(
                f"      RSI: {rsi:.1f} (not oversold but gap is significant)")
            print(f"      → Market showing strength, discounting stale bearish signals")
            print(f"      Gap Boost: +{gap_boost:.3f}")
            if stale_discount > 0:
                print(
                    f"      Stale Data Discount: +{stale_discount:.3f} (60% discount on stale bearish data)")
            print(f"      Total Boost: +{total_boost:.3f}")
            print(f"   TOTAL (after gap): {total_score:+.3f}")

        # FIX #11: WEAK SIGNAL + STRONG FUTURES = FLIP (SYMMETRIC)
        # If score barely positive but futures negative, market is showing weakness → flip DOWN
        # If score barely negative but futures positive, market is showing strength → flip UP
        futures_sentiment = futures.get('overall_sentiment', 0)
        if 0.0 < total_score < 0.05 and futures_sentiment < -0.5:
            flip_amount = total_score + 0.05  # Flip to slightly negative
            total_score = -0.05
            print(f"\n   ⚠️ WEAK POSITIVE + NEGATIVE FUTURES:")
            print(
                f"      Score barely positive: {total_score + flip_amount:.3f}")
            print(f"      Futures negative: {futures_sentiment:.2f}%")
            print(f"      → Flipping to DOWN (market showing weakness)")
            print(f"   TOTAL (flipped): {total_score:+.3f}")
        elif -0.05 < total_score < 0.0 and futures_sentiment > 0.5:
            # SYMMETRIC: Weak negative + positive futures = flip to UP
            flip_amount = total_score - 0.05  # Flip to slightly positive
            total_score = +0.05
            print(f"\n   💡 WEAK NEGATIVE + POSITIVE FUTURES:")
            print(
                f"      Score barely negative: {total_score + flip_amount:.3f}")
            print(f"      Futures positive: {futures_sentiment:.2f}%")
            print(f"      → Flipping to UP (market showing strength)")
            print(f"   TOTAL (flipped): {total_score:+.3f}")

        # Show data quality (Phase 2: upgraded from 11 to 14 sources)
        print(
            f"\n📊 Data Quality: {data_quality_pct:.0f}% ({data_sources_active}/14 sources active)")
        if data_quality_pct < 50:
            print(f"   ⚠️ WARNING: Low data quality - prediction may be unreliable")

        # ========================================================================
        # OCT 22 IMPROVEMENTS: 5 Critical Fixes for Better Accuracy
        # ========================================================================

        # IMPROVEMENT #1: Market Regime Detection
        # Check SPY/QQQ to detect market-wide weakness/strength
        try:
            spy = yf.Ticker('SPY')
            spy_hist = spy.history(period='2d')

            market_regime_detected = False
            market_bias_adjustment = 0.0

            if len(spy_hist) >= 2:
                spy_yesterday = spy_hist['Close'].iloc[-2]
                spy_today = spy_hist['Close'].iloc[-1]
                spy_change_pct = (
                    (spy_today - spy_yesterday) / spy_yesterday) * 100

                # Check QQQ for tech stocks
                qqq = yf.Ticker('QQQ')
                qqq_hist = qqq.history(period='2d')

                if len(qqq_hist) >= 2:
                    qqq_yesterday = qqq_hist['Close'].iloc[-2]
                    qqq_today = qqq_hist['Close'].iloc[-1]
                    qqq_change_pct = (
                        (qqq_today - qqq_yesterday) / qqq_yesterday) * 100

                    market_change = (spy_change_pct + qqq_change_pct) / 2
                    market_regime_detected = True

                    print(f"\n📊 MARKET REGIME DETECTION:")
                    print(
                        f"   SPY: {spy_change_pct:+.2f}%, QQQ: {qqq_change_pct:+.2f}%")

                    if market_change < -0.5:
                        # REDUCED from -0.05 (OCT 24 FIX: prevent universal bias)
                        market_bias_adjustment = -0.025
                        print(
                            f"   ⚠️ BEARISH Market - Reducing bullish bias by {market_bias_adjustment:.3f}")
                    elif market_change > 0.5:
                        # REDUCED from +0.05 (OCT 24 FIX: prevent universal bias)
                        market_bias_adjustment = +0.025
                        print(
                            f"   ✅ BULLISH Market - Boosting bullish bias by {market_bias_adjustment:+.3f}")
                    else:
                        print(f"   ➡️ NEUTRAL Market - No bias adjustment")

                    # Apply market bias
                    if market_bias_adjustment != 0:
                        total_score += market_bias_adjustment
                        print(
                            f"   TOTAL (with market bias): {total_score:+.3f}")
        except Exception as e:
            print(f"   ⚠️ Market regime detection unavailable: {str(e)[:50]}")

        # IMPROVEMENT #2: Technical Veto Power (MOST IMPORTANT!)
        # When technical conflicts with total direction, investigate
        technical_veto_applied = False
        if technical_score * total_score < 0 and abs(technical_score) > 0.05:
            # Technical conflicts with overall direction
            technical_strength = abs(technical_score)
            total_strength = abs(total_score)

            if technical_strength > total_strength * 0.3:
                # Technical warning is strong enough to matter
                original_total = total_score
                original_confidence_estimate = 55 + \
                    abs(total_score) * 125  # Rough estimate

                # Reduce total score by 25%
                total_score = total_score * 0.75

                # Technical veto: reduce total score AND confidence (REDUCED from -30% to -15%)
                technical_veto_applied = True
                # Reduce confidence by 15% (was 30%)
                technical_veto_multiplier = 0.85
                # Reduce score by 25% (was 40%)
                total_score = total_score * 0.75
                print(f"\n⚠️ TECHNICAL VETO ACTIVATED:")
                print(
                    f"   Technical: {technical_score:+.3f} conflicts with Total: {original_total:+.3f}")
                print(
                    f"   Technical strength: {technical_strength:.3f} (>{total_strength*0.3:.3f} threshold)")
                print(
                    f"   Total Score Reduced: {original_total:+.3f} → {total_score:+.3f} (40% reduction)")
                print(f"   Confidence will be reduced by 15%")
                print(
                    f"   ⚠️ WARNING: Technical analysis disagrees - proceed with caution!")

        # IMPROVEMENT #3: Options Conflict Adjustment
        # When options conflicts with news+technical, reduce its influence
        options_adjustment_applied = False
        combined_news_tech = news_score + technical_score
        if options_score * combined_news_tech < 0 and abs(combined_news_tech) > abs(options_score) * 0.5:
            # Options conflicts with combined news+technical signal
            original_options = options_score
            reduction = options_score * 0.5  # Keep only 50%

            # Recalculate total_score with adjusted options
            total_score -= reduction

            options_adjustment_applied = True
            print(f"\n⚠️ OPTIONS CONFLICT DETECTED:")
            print(
                f"   Options: {original_options:+.3f} conflicts with News+Tech: {combined_news_tech:+.3f}")
            print(
                f"   Options weight reduced by 50%: {original_options:+.3f} → {original_options - reduction:+.3f}")
            print(
                f"   Total Score Adjusted: {total_score + reduction:+.3f} → {total_score:+.3f}")
            print(f"   ⚠️ WARNING: Options signal may be unreliable")

        # IMPROVEMENT #4: Count Signal Conflicts for Confidence Penalty
        # Build scores dict for conflict analysis
        scores_dict = {
            'news': news_score,
            'futures': futures_score,
            'options': options_score,
            'technical': technical_score,
            'sector': sector_score,
            'reddit': reddit_score,
            'twitter': twitter_score,
            'vix': vix_score,
            'premarket': premarket_score,
            'analyst_ratings': analyst_score,
            'institutional': institutional_score
        }

        # IMPROVEMENT #5: INTELLIGENT CONFLICT RESOLUTION (Phase 5)
        # Instead of just penalizing conflicts, UNDERSTAND which signals matter more
        intelligent_resolution_applied = False
        resolution_info = None

        if CONFLICT_RESOLVER_AVAILABLE:
            try:
                resolver = IntelligentConflictResolver()

                # Prepare market context data
                # Calculate fundamental strength for BOUNCE_SETUP detection
                fundamental_strength = 0
                fundamental_count = 0
                if news_score != 0:
                    fundamental_strength += news_score
                    fundamental_count += 1
                if options_score != 0:
                    fundamental_strength += options_score
                    fundamental_count += 1
                if analyst_score != 0:
                    fundamental_strength += analyst_score
                    fundamental_count += 1

                if fundamental_count > 0:
                    fundamental_avg = fundamental_strength / fundamental_count
                else:
                    fundamental_avg = 0

                market_context = {
                    'rsi': technical.get('rsi', 50),
                    'vix_level': vix.get('vix_level', 18),
                    'vix_change': vix.get('vix_change', 0),
                    'intraday_change': intraday_change_pct if 'intraday_change_pct' in locals() else 0,
                    'market_change': (spy_change + qqq_change) / 2 if 'spy_change' in locals() and 'qqq_change' in locals() else 0,
                    'premarket_gap': premarket.get('premarket_change_pct', 0),
                    'spy_change': spy_change if 'spy_change' in locals() else 0,
                    'qqq_change': qqq_change if 'qqq_change' in locals() else 0,
                    'institutional_flow': institutional_score,
                    'options_pcr': options.get('put_call_ratio', 1.0),
                    'days_to_earnings': 100,  # Default, can be enhanced later
                    'fundamental_strength': fundamental_avg,  # For BOUNCE_SETUP detection
                }

                # Convert scores to signal format
                signals_for_resolver = {
                    name: {
                        'score': score,
                        'direction': 'UP' if score > 0 else 'DOWN' if score < 0 else 'NEUTRAL'
                    }
                    for name, score in scores_dict.items()
                }

                # Apply intelligent resolution
                adjusted_signals, resolution_info = resolver.resolve_conflict(
                    signals_for_resolver, market_context)

                if resolution_info:
                    intelligent_resolution_applied = True

                    # Display what rule was applied
                    print(f"\n" + "="*80)
                    print(f"🧠 INTELLIGENT CONFLICT RESOLUTION")
                    print(f"="*80)
                    print(f"\n📊 Situation: {resolution_info['rule_applied']}")
                    print(f"💡 Logic: {resolution_info['reasoning']}")
                    print(f"\n📈 Signal Hierarchy (Most Important First):")
                    for i, sig in enumerate(resolution_info['hierarchy'][:4], 1):
                        print(f"   {i}. {sig.upper()}")

                    # Recalculate total_score with adjusted signals
                    old_total = total_score

                    # Apply adjustments to scores
                    if 'news' in adjusted_signals and adjusted_signals['news'].get('boosted'):
                        boost = adjusted_signals['news']['boost_factor']
                        adjustment = news_score * (boost - 1)
                        total_score += adjustment
                        print(
                            f"   ✅ News boosted ×{boost:.2f}: {news_score:+.3f} → {news_score * boost:+.3f}")
                    elif 'news' in adjusted_signals and adjusted_signals['news'].get('reduced'):
                        reduction = adjusted_signals['news']['reduction_factor']
                        adjustment = news_score * (reduction - 1)
                        total_score += adjustment
                        print(
                            f"   ⚠️ News reduced ×{reduction:.2f}: {news_score:+.3f} → {news_score * reduction:+.3f}")

                    if 'futures' in adjusted_signals and adjusted_signals['futures'].get('boosted'):
                        boost = adjusted_signals['futures']['boost_factor']
                        adjustment = futures_score * (boost - 1)
                        total_score += adjustment
                        print(
                            f"   ✅ Futures boosted ×{boost:.2f}: {futures_score:+.3f} → {futures_score * boost:+.3f}")

                    if 'technical' in adjusted_signals and adjusted_signals['technical'].get('boosted'):
                        boost = adjusted_signals['technical']['boost_factor']
                        adjustment = technical_score * (boost - 1)
                        total_score += adjustment
                        print(
                            f"   ✅ Technical boosted ×{boost:.2f}: {technical_score:+.3f} → {technical_score * boost:+.3f}")
                    elif 'technical' in adjusted_signals and adjusted_signals['technical'].get('reduced'):
                        reduction = adjusted_signals['technical']['reduction_factor']
                        adjustment = technical_score * (reduction - 1)
                        total_score += adjustment
                        print(
                            f"   ⚠️ Technical reduced ×{reduction:.2f}: {technical_score:+.3f} → {technical_score * reduction:+.3f}")
                        print(
                            f"   💡 BOUNCE SETUP: Ignoring bearish technical (it's the setup, not the prediction!)")

                    if 'institutional' in adjusted_signals and adjusted_signals['institutional'].get('boosted'):
                        boost = adjusted_signals['institutional']['boost_factor']
                        adjustment = institutional_score * (boost - 1)
                        total_score += adjustment
                        print(
                            f"   ✅ Institutional boosted ×{boost:.2f}: {institutional_score:+.3f} → {institutional_score * boost:+.3f}")

                    print(
                        f"\n🎯 Score After Intelligent Resolution: {old_total:+.3f} → {total_score:+.3f}")
                    print(f"💡 System UNDERSTANDS which signals matter more!")
                    print("="*80)

            except Exception as e:
                print(f"   ⚠️ Conflict resolver error: {str(e)[:100]}")

        # Determine main direction (after intelligent adjustments)
        main_direction = 1 if total_score > 0 else -1

        # Count conflicts
        conflicting_signals = []
        aligned_signals = []

        for name, score in scores_dict.items():
            if abs(score) > 0.01:  # Only count significant signals
                if score * main_direction < 0:
                    conflicting_signals.append(name)
                else:
                    aligned_signals.append(name)

        conflict_count = len(conflicting_signals)

        # Calculate conflict penalty based on count (REDUCED penalties)
        if conflict_count == 0:
            conflict_penalty_multiplier = 1.0  # No penalty
        elif conflict_count == 1:
            conflict_penalty_multiplier = 0.97  # 3% penalty (was 5%)
        elif conflict_count == 2:
            conflict_penalty_multiplier = 0.93  # 7% penalty (was 15%)
        else:  # 3 or more conflicts
            conflict_penalty_multiplier = 0.90  # 10% penalty (was 25%)

        if conflict_count > 0:
            print(f"\n📊 SIGNAL CONFLICT ANALYSIS:")
            print(
                f"   Aligned signals: {len(aligned_signals)} {aligned_signals}")
            print(
                f"   Conflicting signals: {conflict_count} {conflicting_signals}")
            print(
                f"   Confidence penalty: {conflict_penalty_multiplier*100:.0f}% (will reduce confidence)")
            if conflict_count >= 2:
                print(
                    f"   ⚠️ WARNING: Multiple conflicting signals - prediction less reliable")

        # SUMMARY: Show which improvements were applied
        improvements_applied = []
        if market_regime_detected and market_bias_adjustment != 0:
            improvements_applied.append(
                f"Market Regime ({market_bias_adjustment:+.3f})")
        if intelligent_resolution_applied:
            improvements_applied.append(
                f"Intelligent Resolution ({resolution_info['rule_applied']})")
        if technical_veto_applied:
            improvements_applied.append("Technical Veto")
        if options_adjustment_applied:
            improvements_applied.append("Options Adjustment")
        if conflict_count > 0:
            improvements_applied.append(
                f"Conflict Penalty ({conflict_count} conflicts)")

        if improvements_applied:
            print(
                f"\n🔧 IMPROVEMENTS APPLIED: {', '.join(improvements_applied)}")
            if intelligent_resolution_applied:
                print(
                    f"   🧠 INTELLIGENT resolution applied - System understood context!")
            else:
                print(
                    f"   These Oct 22 fixes improve accuracy by detecting conflicts and market weakness")

        # ========================================================================
        # End of Oct 22 Improvements
        # ========================================================================

        # Determine direction with stricter thresholds to avoid neutral trap
        # FIX: Use >= and <= to include threshold values in UP/DOWN, not NEUTRAL
        if total_score >= 0.04:  # Lowered from 0.05 to avoid neutral trap
            direction = "UP"
            # Piecewise linear formula for better confidence scaling
            if abs(total_score) <= 0.10:
                confidence = 55 + abs(total_score) * 125
            else:
                confidence = 67.5 + (abs(total_score) - 0.10) * 115
            confidence = min(confidence, 88)
        elif total_score <= -0.04:  # Lowered from -0.05
            direction = "DOWN"
            # Piecewise linear formula for better confidence scaling
            if abs(total_score) <= 0.10:
                confidence = 55 + abs(total_score) * 125
            else:
                confidence = 67.5 + (abs(total_score) - 0.10) * 115
            confidence = min(confidence, 88)
        else:
            direction = "NEUTRAL"
            confidence = 50
            # Reduce confidence for NEUTRAL if data quality is low
            if data_quality_pct < 50:
                confidence = 30  # Very low confidence if based on missing data

        # Apply Oct 22 Improvement confidence penalties
        original_confidence = confidence

        # Apply technical veto confidence penalty
        if technical_veto_applied:
            confidence = confidence * technical_veto_multiplier
            print(
                f"\n   Technical Veto Penalty: {original_confidence:.2f}% → {confidence:.2f}% (-30%)")
            original_confidence = confidence

        # Apply conflict penalty
        if conflict_count > 0:
            confidence = confidence * conflict_penalty_multiplier
            penalty_pct = (1 - conflict_penalty_multiplier) * 100
            print(
                f"   Conflict Penalty: {original_confidence:.2f}% → {confidence:.2f}% (-{penalty_pct:.0f}%)")

        # Show final adjusted confidence
        if technical_veto_applied or conflict_count > 0:
            print(f"\n   🎯 FINAL ADJUSTED CONFIDENCE: {confidence:.2f}%")

        # ========================================================================
        # BALANCED CONFIDENCE FILTERING (Oct 22 Balance Adjustment)
        # ========================================================================
        # Slightly stricter filtering to avoid marginal trades
        # Based on analysis: 60% is borderline, 62% is safer

        # Base threshold (lowered to 55% for more quality predictions)
        confidence_threshold = 55  # Lowered from 60% to capture more bounces

        # Adjust threshold based on VIX (market volatility)
        vix_level = vix.get('vix_level', 18)
        if vix_level > 20:
            # High volatility = need stronger signals
            # Raised but still lower than before (was 65)
            confidence_threshold = 60
            print(
                f"\n   📈 VIX {vix_level:.1f} > 20 - Raising threshold to {confidence_threshold}% (volatile market)")
        elif vix_level < 15:
            # Low volatility = can take more trades
            confidence_threshold = 55
            print(
                f"\n   📉 VIX {vix_level:.1f} < 15 - Lowering threshold to {confidence_threshold}% (stable market)")
        else:
            # Normal volatility
            print(
                f"\n   ➡️ VIX {vix_level:.1f} - Using standard threshold {confidence_threshold}%")

        # Additional check: Multiple conflicts get small threshold boost only
        if conflict_count >= 3:
            # Only boost threshold slightly for 3+ conflicts
            conflict_threshold_boost = 2  # Just 2% boost (was 5%)
            confidence_threshold = min(
                confidence_threshold + conflict_threshold_boost, 63)
            print(
                f"   ⚠️ {conflict_count} conflicts detected - Threshold boosted to {confidence_threshold}%")

        # Final trade decision
        if confidence < confidence_threshold:
            print(
                f"\n   ❌ TRADE FILTERED: {confidence:.2f}% < {confidence_threshold}% threshold")
            print(f"   ⚠️ This trade should be SKIPPED!")

        # Calculate DYNAMIC target based on multiple factors
        # Base volatility (stock-specific)
        # Default 1.5% if config missing
        base_vol = self.stock_config.get('typical_volatility', 0.015)

        # Start with base volatility
        dynamic_volatility = base_vol

        # Factor 1: Confidence/Score Strength - REALISTIC for overnight gaps
        # Only boost target modestly - most overnight moves are 1-2%
        if confidence >= 85:
            confidence_multiplier = 1.08  # Very high confidence = 8% larger target
        elif confidence >= 75:
            confidence_multiplier = 1.05  # High confidence = 5% larger
        elif confidence >= 65:
            confidence_multiplier = 1.02  # Above average = 2% larger
        else:
            confidence_multiplier = 0.97  # Lower confidence = slightly smaller

        # ADDITIONAL: Score magnitude bonus (only for very strong signals)
        score_magnitude = abs(total_score)
        if score_magnitude > 0.35:
            score_multiplier = 1.15  # Extremely strong signal = 15% bonus
        elif score_magnitude > 0.30:
            score_multiplier = 1.10  # Very strong signal = 10% bonus
        elif score_magnitude > 0.25:
            score_multiplier = 1.06  # Strong signal = 6% bonus
        elif score_magnitude > 0.20:
            score_multiplier = 1.03  # Good signal = 3% bonus
        else:
            score_multiplier = 1.0  # Normal - no bonus

        dynamic_volatility *= confidence_multiplier * score_multiplier

        # Factor 2: Earnings Proximity Volatility Multiplier
        # Near earnings = expect larger moves
        earnings_vol_mult = earnings_proximity.get(
            'volatility_multiplier', 1.0)
        dynamic_volatility *= earnings_vol_mult

        # Factor 3: VIX Level
        # High VIX = more volatility expected
        vix_level = vix.get('vix_level', 20)
        if vix_level > 30:
            # High volatility environment - allow larger moves
            vix_multiplier = 1.4  # 40% more volatility
        elif vix_level > 25:
            vix_multiplier = 1.2  # 20% more volatility
        elif vix_level > 20:
            vix_multiplier = 1.1  # 10% more volatility
        elif vix_level < 12:
            vix_multiplier = 0.8  # 20% less volatility
        else:
            vix_multiplier = 1.0  # Normal

        dynamic_volatility *= vix_multiplier

        # Factor 4: Pre-Market Strength - ADAPTIVE with Gap Exhaustion Logic
        # Large gaps often exhaust momentum - be conservative
        premarket_change = abs(premarket.get('premarket_change_pct', 0))
        premarket_direction = premarket.get('premarket_change_pct', 0)

        # GAP EXHAUSTION LOGIC: Large gaps reduce next-day momentum
        if premarket_change > 8.0:
            # Huge gap (>8%) - likely profit taking, REDUCE target
            premarket_multiplier = 0.90  # Reduce by 10%
            print(
                f"   ⚠️ Large gap detected ({premarket_change:.1f}%) - reducing target (gap exhaustion)")
        elif premarket_change > 5.0:
            # Large gap (5-8%) - momentum may be exhausted, neutral
            premarket_multiplier = 0.95  # Slight reduction
            print(
                f"   ℹ️ Significant gap ({premarket_change:.1f}%) - conservative target")
        elif premarket_change > 3.0:
            # Moderate gap - small boost only
            premarket_multiplier = 1.03  # Minimal boost
        elif premarket_change > 1.5:
            # Small gap - healthy continuation
            premarket_multiplier = 1.05
        else:
            # No significant gap
            premarket_multiplier = 1.0

        dynamic_volatility *= premarket_multiplier

        # Factor 5: Short Squeeze Potential
        # High short interest + momentum = bigger moves possible
        squeeze_potential = short_interest.get('squeeze_potential', 'none')
        if squeeze_potential == 'extreme':
            squeeze_multiplier = 1.5  # Extreme squeeze = 50% larger move
        elif squeeze_potential == 'high':
            squeeze_multiplier = 1.3  # High = 30% larger
        elif squeeze_potential in ['medium', 'low']:
            squeeze_multiplier = 1.1  # Some potential = 10% larger
        else:
            squeeze_multiplier = 1.0

        dynamic_volatility *= squeeze_multiplier

        # ADAPTIVE MAXIMUM: Based on recent volatility and market conditions
        # Adjust max cap based on VIX and recent price action
        if vix_level > 30:
            # High volatility environment - allow larger moves
            max_cap_multiplier = 2.0
        elif vix_level > 25:
            max_cap_multiplier = 1.8
        elif vix_level > 20:
            max_cap_multiplier = 1.6
        else:
            # Low volatility - be more conservative
            max_cap_multiplier = 1.4

        max_volatility = base_vol * max_cap_multiplier
        min_volatility = base_vol * 0.6
        dynamic_volatility = max(min_volatility, min(
            dynamic_volatility, max_volatility))

        # REALISTIC OVERNIGHT GAP TARGETS
        # Don't artificially cap at historical average - strong signals deserve larger targets
        historical_avg_gap = self.stock_config.get(
            'historical_avg_gap', base_vol)

        # Set MAXIMUM possible target based on stock volatility and conditions
        # These are realistic maximums based on actual overnight gaps:
        # AMD: Can gap $3-6 (1.3-2.6% on $230)
        # AVGO: Can gap $5-10 (1.4-2.9% on $350)
        # ORCL: Can gap $5-12 (1.7-4.1% on $290)

        # REALISTIC OVERNIGHT TARGETS
        # The configured "typical_volatility" represents MAX possible gap
        # Most overnight moves should be 50-80% of that maximum
        # Only very strong signals approach the configured maximum

        # Base target scaling: Start conservative
        if confidence >= 85 and score_magnitude > 0.30:
            # Exceptional signal - can approach configured maximum
            base_scaling = 0.85  # 85% of configured volatility
            print(f"   🔥 Exceptional signal strength")
        elif confidence >= 75 and score_magnitude > 0.25:
            # Strong signal - moderate target
            base_scaling = 0.70  # 70% of configured volatility
        elif confidence >= 65:
            # Good signal - conservative target
            base_scaling = 0.60  # 60% of configured volatility
        else:
            # Weak signal - very conservative
            base_scaling = 0.50  # 50% of configured volatility

        # Apply base scaling before other multipliers
        dynamic_volatility *= base_scaling

        # MAXIMUM cap based on conditions
        if vix_level > 30 or (premarket_change > 8 and vix_level > 25):
            # Extreme volatility - allow reaching configured maximum
            max_target = base_vol * 1.1
            print(
                f"   🚨 Extreme volatility - max target: {max_target*100:.2f}%")
        elif vix_level > 25 or premarket_change > 5:
            # High volatility - allow 90% of configured maximum
            max_target = base_vol * 0.95
            print(f"   📈 High volatility - max target: {max_target*100:.2f}%")
        else:
            # Normal conditions - cap at 80% of configured maximum
            max_target = base_vol * 0.80

        # Apply reasonable maximum cap (but don't artificially reduce strong signals)
        if dynamic_volatility > max_target:
            print(
                f"   📊 Target capped at maximum: {max_target*100:.2f}% (from {dynamic_volatility*100:.2f}%)")
            dynamic_volatility = max_target

        # Minimum target (avoid unrealistically small predictions)
        min_target = historical_avg_gap * 0.7  # At least 70% of historical average
        if dynamic_volatility < min_target:
            dynamic_volatility = min_target

        # MOMENTUM EXHAUSTION CHECK: Only apply if extremely overextended
        try:
            hist_5d = yf.Ticker(self.symbol).history(period='5d')
            if len(hist_5d) >= 3:
                recent_3d_change = (
                    (hist_5d['Close'].iloc[-1] - hist_5d['Close'].iloc[-3]) / hist_5d['Close'].iloc[-3]) * 100

                # Only reduce target if VERY overextended (>12% in 3 days)
                if abs(recent_3d_change) > 12:
                    consolidation_factor = 0.90  # Mild reduction only
                    print(
                        f"   🔄 Very strong 3-day move: {recent_3d_change:+.1f}% - slight reduction")
                    dynamic_volatility *= consolidation_factor
        except:
            pass

        # Log dynamic target calculation
        print(f"\n🎯 Dynamic Target Calculation:")
        print(f"   Base Volatility: {base_vol*100:.2f}%")
        print(f"   Confidence Multiplier: {confidence_multiplier:.2f}x")
        if earnings_vol_mult != 1.0:
            print(f"   Earnings Multiplier: {earnings_vol_mult:.2f}x")
        print(
            f"   VIX Multiplier: {vix_multiplier:.2f}x (VIX: {vix_level:.1f})")
        if premarket_multiplier != 1.0:
            print(
                f"   Pre-Market Multiplier: {premarket_multiplier:.2f}x ({premarket_change:+.2f}%)")
        if squeeze_multiplier != 1.0:
            print(
                f"   Squeeze Multiplier: {squeeze_multiplier:.2f}x ({squeeze_potential})")
        print(
            f"   Final Dynamic Volatility: {dynamic_volatility*100:.2f}% (was {base_vol*100:.2f}%)")

        # Apply dynamic volatility to calculate target
        if direction == "UP":
            target_price = current_price * (1 + dynamic_volatility)
        elif direction == "DOWN":
            target_price = current_price * (1 - dynamic_volatility)
        else:
            target_price = current_price

        expected_change = target_price - current_price
        expected_change_pct = (expected_change / current_price) * 100

        # Generate detailed explanation
        explanation = self._generate_explanation(direction, confidence, total_score, {
            'news': (news, news_score),
            'futures': (futures, futures_score),
            'options': (options, options_score),
            'technical': (technical, technical_score),
            'sector': (sector, sector_score),
            'reddit': (reddit, reddit_score),
            'institutional': (institutional, institutional_score)
        })

        # Display
        print("\n" + "="*80)
        print("🎯 PREDICTION RESULT")
        print("="*80)
        print(
            f"\n{'📈' if direction == 'UP' else '📉' if direction == 'DOWN' else '➡️'} DIRECTION: {direction}")
        print(f"🎲 CONFIDENCE: {confidence:.1f}%")
        print(f"💰 TODAY'S CLOSE: ${current_price:.2f} (reference price)")
        print(f"🎯 TARGET (Tomorrow): ${target_price:.2f}")
        print(
            f"📊 EXPECTED MOVE: ${expected_change:+.2f} ({expected_change_pct:+.2f}%)")
        print(f"📈 SCORE: {total_score:+.3f}")

        print(f"\n" + "-"*80)
        print(f"📝 EXPLANATION:")
        print(explanation)

        print(f"\n" + "-"*80)
        print(f"💡 RECOMMENDATION:")

        # Use the adaptive threshold we calculated earlier
        if confidence >= 70:
            print(
                f"   ✅ HIGH CONFIDENCE ({confidence:.1f}%) - FULL POSITION (100%)")
            print(f"   Strong {direction} signal with clear conviction")
            print(f"   Position Size: 5-10% of portfolio")
        elif confidence >= confidence_threshold:
            print(
                f"   ⚠️ MODERATE CONFIDENCE ({confidence:.1f}%) - PARTIAL POSITION (50%)")
            print(f"   Decent {direction} signal, confirm at 6 AM premarket")
            print(f"   Position Size: 2.5-5% of portfolio")
            print(f"   Add 50% more if gap confirms in premarket")
        else:
            print(f"   ⏸️ LOW CONFIDENCE ({confidence:.1f}%) - SKIP TRADE")
            print(
                f"   Below {confidence_threshold}% threshold - insufficient conviction")
            print(
                f"   Reason: {'Mixed signals' if conflict_count > 0 else 'Weak signal'}")
            if conflict_count > 0:
                print(f"   {conflict_count} conflicting signals detected")
            print(f"   🚫 DO NOT TRADE - Stay on sidelines")

        print("="*80)

        return {
            'direction': direction,
            'confidence': confidence,
            'current_price': current_price,
            'target_price': target_price,
            'expected_change': expected_change,
            'expected_move_pct': expected_change_pct,  # Added for summary display
            'total_score': total_score,
            'explanation': explanation
        }

    def _generate_explanation(self, direction: str, confidence: float, total_score: float, factors: Dict) -> str:
        """Generate detailed explanation for the prediction"""
        lines = []

        if direction == "NEUTRAL":
            lines.append("\n   ⚖️ MIXED SIGNALS - No clear direction")
            lines.append(
                f"   Total score ({total_score:+.3f}) is near zero, indicating conflicting factors:\n")

            # Categorize bullish and bearish signals
            bullish = []
            bearish = []
            neutral = []

            for name, (data, score) in factors.items():
                if score > 0.02:
                    bullish.append((name, score, data))
                elif score < -0.02:
                    bearish.append((name, score, data))
                else:
                    neutral.append((name, score, data))

            if bullish:
                lines.append("   📈 BULLISH FACTORS:")
                for name, score, data in sorted(bullish, key=lambda x: x[1], reverse=True):
                    lines.append(f"      • {name.title()}: {score:+.3f}")
                    if name == 'options' and data.get('sentiment') == 'bullish':
                        lines.append(
                            f"        → P/C ratio {data['put_call_ratio']:.2f} shows heavy call buying")
                    elif name == 'technical' and data.get('trend') == 'uptrend':
                        lines.append(
                            f"        → Uptrend with RSI {data['rsi']:.1f}")
                    elif name == 'institutional' and data.get('flow_direction') == 'accumulation':
                        lines.append(
                            f"        → {', '.join(data.get('indicators', []))}")
                lines.append("")

            if bearish:
                lines.append("   📉 BEARISH FACTORS:")
                for name, score, data in sorted(bearish, key=lambda x: x[1]):
                    lines.append(f"      • {name.title()}: {score:+.3f}")
                    if name == 'futures':
                        lines.append(
                            f"        → ES {data['es_change']:+.2f}%, NQ {data['nq_change']:+.2f}%")
                    elif name == 'technical' and data.get('trend') == 'downtrend':
                        lines.append(
                            f"        → Downtrend, MACD {data['macd_signal']}, momentum {data['momentum_score']:+.2f}%")
                    elif name == 'sector':
                        lines.append(
                            f"        → Sector weakness dragging price down")
                lines.append("")

            lines.append("   💡 CONCLUSION:")
            lines.append(
                "      Bullish and bearish forces are roughly balanced.")
            lines.append(
                "      Wait for clearer signals before entering a position.")
            lines.append(
                "      Consider watching for: breakout above/below key levels,")
            lines.append(
                "      futures turning positive, or technical indicators aligning.")

        elif direction == "UP":
            lines.append(f"\n   📈 BULLISH OUTLOOK (Score: {total_score:+.3f})")
            lines.append("   Multiple factors supporting upward movement:\n")

            # List positive contributors
            for name, (data, score) in sorted(factors.items(), key=lambda x: x[1][1], reverse=True):
                if score > 0.01:
                    lines.append(f"      ✅ {name.title()}: {score:+.3f}")

            # Note any conflicting signals
            negatives = [(name, score) for name, (data, score)
                         in factors.items() if score < -0.01]
            if negatives:
                lines.append("\n   ⚠️ Conflicting signals:")
                for name, score in negatives:
                    lines.append(f"      • {name.title()}: {score:+.3f}")

        else:  # DOWN
            lines.append(f"\n   📉 BEARISH OUTLOOK (Score: {total_score:+.3f})")
            lines.append("   Multiple factors supporting downward movement:\n")

            # List negative contributors
            for name, (data, score) in sorted(factors.items(), key=lambda x: x[1][1]):
                if score < -0.01:
                    lines.append(f"      ❌ {name.title()}: {score:+.3f}")

            # Note any conflicting signals
            positives = [(name, score) for name, (data, score)
                         in factors.items() if score > 0.01]
            if positives:
                lines.append("\n   ⚠️ Conflicting signals:")
                for name, score in positives:
                    lines.append(f"      • {name.title()}: {score:+.3f}")

        return "\n".join(lines)


if __name__ == "__main__":
    import sys

    # Get symbol from command line argument or use default
    symbol = sys.argv[1] if len(sys.argv) > 1 else None

    try:
        predictor = ComprehensiveNextDayPredictor(symbol=symbol)
        prediction = predictor.generate_comprehensive_prediction()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
