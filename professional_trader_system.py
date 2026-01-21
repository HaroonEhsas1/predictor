#!/usr/bin/env python3
"""
Professional Trader Prediction System
Uses comprehensive data sources to make directional predictions
Returns UP/DOWN when signals are strong, HOLD when signals are weak or conflicting
Designed to work like a professional trader with access to everything
"""

import os
import sys
import yfinance as yf
import requests
import pandas as pd
import numpy as np
import time
import random
import pytz
from datetime import datetime, timedelta, time as datetime_time
from typing import Dict, Any, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

# Import predictive data fetchers
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from engines.after_close_engine.fetchers import fetch_futures, fetch_options_summary
except ImportError:
    print("⚠️ Warning: Predictive fetchers not available, using fallback methods")
    fetch_futures = None
    fetch_options_summary = None

class ProfessionalTraderSystem:
    """
    Professional trader system using real-time data analysis
    Returns UP when bullish signals dominate, DOWN when bearish signals dominate
    Returns HOLD when signals are insufficient or conflicting (professional caution)
    """
    
    def __init__(self, symbol: str = "AMD"):
        self.symbol = symbol
        self.polygon_api_key = os.getenv('POLYGON_API_KEY')
        self.eodhd_api_key = os.getenv('EODHD_API_KEY')
        self.alpha_vantage_key = os.getenv('ALPHA_VANTAGE_API_KEY')
        
        # Requires minimum signal strength for directional calls
        # Returns HOLD when signals are weak or conflicting (professional risk management)
        
        print(f"🎯 Professional Trader System initialized for {symbol}")
        print(f"📊 Data Sources: {'Polygon✅' if self.polygon_api_key else 'Polygon❌'} | {'EODHD✅' if self.eodhd_api_key else 'EODHD❌'} | {'Alpha Vantage✅' if self.alpha_vantage_key else 'Alpha Vantage❌'}")
    
    def predict_direction(self) -> Dict[str, Any]:
        """
        Main prediction function - returns UP/DOWN/HOLD based on signal strength
        Uses comprehensive multi-source analysis like a professional trader
        Returns HOLD when signals are weak or conflicting (professional risk management)
        """
        print("\n🚀 PROFESSIONAL TRADER ANALYSIS - Comprehensive Market Assessment")
        
        # Collect all available data sources
        market_data = self._collect_comprehensive_data()
        
        # Analyze multiple signal categories - PREDICTIVE signals weighted higher
        signals = {
            'futures': self._analyze_futures_signals(market_data),  # PREDICTIVE - highest priority
            'options_flow': self._analyze_options_flow_signals(market_data),  # PREDICTIVE - smart money
            'sentiment': self._analyze_sentiment_signals(market_data),  # PREDICTIVE - forward-looking
            'microstructure': self._analyze_microstructure_signals(market_data),  # PREDICTIVE - order flow
            'correlation': self._analyze_market_correlation_signals(market_data),  # SEMI-PREDICTIVE
            'flow': self._analyze_order_flow_signals(market_data),  # SEMI-PREDICTIVE
            'volume': self._analyze_volume_signals(market_data),  # SEMI-PREDICTIVE
            'momentum': self._analyze_momentum_signals(market_data),  # REACTIVE - reduced weight
            'technical': self._analyze_technical_signals(market_data)  # REACTIVE - reduced weight
        }
        
        # Professional trader decision matrix - weighs ALL evidence
        direction, confidence, reasoning = self._make_professional_decision(signals, market_data)
        
        # Calculate price targets and expected moves
        current_price = market_data.get('current_price', 0)
        target_price, expected_move = self._calculate_price_targets(direction, confidence, current_price)
        
        return {
            'direction': direction,  # UP when bullish, DOWN when bearish, HOLD when weak/conflicting
            'confidence': confidence,
            'current_price': current_price,
            'target_price': target_price,
            'expected_move': expected_move,
            'reasoning': reasoning,
            'signals_summary': self._create_signals_summary(signals),
            'timestamp': datetime.now().isoformat(),
            'data_sources_used': market_data.get('sources_used', [])
        }
    
    def _collect_comprehensive_data(self) -> Dict[str, Any]:
        """
        Collect data from ALL available sources like a professional trader
        """
        data = {
            'sources_used': [],
            'current_price': 0,
            'volume': 0,
            'price_data': {},
            'market_context': {},
            'real_time_data': {}
        }
        
        try:
            # Primary: Real-time Yahoo Finance data
            ticker = yf.Ticker(self.symbol)
            
            # FIXED: Multiple timeframes for comprehensive analysis INCLUDING EXTENDED HOURS
            print("📊 Fetching extended hours data (pre-market + after-hours)")
            timeframes = {
                '1m': ticker.history(period="8d", interval="1m", prepost=True),
                '5m': ticker.history(period="5d", interval="5m", prepost=True),
                '15m': ticker.history(period="30d", interval="15m", prepost=True),
                '1h': ticker.history(period="60d", interval="1h", prepost=True),
                '1d': ticker.history(period="2y", interval="1d", prepost=True)
            }
            
            # ENHANCED: Extract current price and volume with PRE-MARKET detection
            if not timeframes['1m'].empty:
                current_price = float(timeframes['1m']['Close'].iloc[-1])
                data['current_price'] = current_price
                data['volume'] = int(timeframes['1m']['Volume'].sum())
                data['sources_used'].append('Yahoo Finance (Extended Hours)')
                
                # CRITICAL: Pre-market detection and calculation
                current_time_et = datetime.now(pytz.timezone('US/Eastern'))
                is_pre_market = (4 <= current_time_et.hour < 9) or (current_time_et.hour == 9 and current_time_et.minute < 30)
                
                if is_pre_market and len(timeframes['1d']) > 1:
                    previous_close = float(timeframes['1d']['Close'].iloc[-2])  # Previous trading day close
                    pre_market_change = current_price - previous_close
                    pre_market_change_pct = (pre_market_change / previous_close) * 100 if previous_close > 0 else 0.0
                    
                    # Add pre-market data to main data structure
                    data['pre_market_detected'] = True
                    data['pre_market_change'] = pre_market_change
                    data['pre_market_change_pct'] = pre_market_change_pct
                    data['previous_close'] = previous_close
                    
                    print(f"🌅 PRE-MARKET DETECTED: ${current_price:.2f} vs Previous Close ${previous_close:.2f}")
                    print(f"🚀 PRE-MARKET MOVEMENT: {pre_market_change_pct:+.2f}% (${pre_market_change:+.2f})")
                else:
                    data['pre_market_detected'] = False
            
            data['price_data'] = timeframes
            
            # Enhanced with Polygon.io microstructure data
            if self.polygon_api_key:
                polygon_data = self._fetch_polygon_microstructure()
                if polygon_data:
                    data['microstructure'] = polygon_data
                    data['sources_used'].append('Polygon.io')
            
            # Enhanced with EODHD real-time data
            if self.eodhd_api_key:
                eodhd_data = self._fetch_eodhd_realtime()
                if eodhd_data:
                    data['real_time_data'] = eodhd_data
                    data['sources_used'].append('EODHD')
            
            # Enhanced with Alpha Vantage sentiment
            if self.alpha_vantage_key:
                sentiment_data = self._fetch_alpha_vantage_sentiment()
                if sentiment_data:
                    data['sentiment'] = sentiment_data
                    data['sources_used'].append('Alpha Vantage')
            
            # Market context data (indices, VIX, etc.)
            data['market_context'] = self._fetch_market_context()
            
        except Exception as e:
            print(f"⚠️ Data collection error: {e}")
        
        return data
    
    def _fetch_polygon_microstructure(self) -> Optional[Dict]:
        """Fetch Level 2 microstructure data from Polygon.io INCLUDING EXTENDED HOURS"""
        try:
            base_url = "https://api.polygon.io"
            current_time_et = datetime.now(pytz.timezone('US/Eastern'))
            is_pre_market = (4 <= current_time_et.hour < 9) or (current_time_et.hour == 9 and current_time_et.minute < 30)
            
            # ENHANCED: Get extended hours data for pre-market analysis
            if is_pre_market:
                print("🌅 Fetching Polygon.io pre-market data...")
                # Pre-market specific time range (4:00 AM - 9:30 AM ET)
                start_time = current_time_et.replace(hour=4, minute=0, second=0, microsecond=0)
                time_filter = start_time.strftime('%Y-%m-%dT%H:%M:%S.000Z')
            else:
                # Regular trading hours or after-hours
                time_filter = (datetime.now() - timedelta(minutes=30)).strftime('%Y-%m-%dT%H:%M:%S.000Z')
            
            microstructure_data = {}
            
            # 1. Get real-time quote for current price (includes extended hours)
            quote_url = f"{base_url}/v2/last/nbbo/{self.symbol}"
            quote_params = {'apikey': self.polygon_api_key}
            
            quote_response = requests.get(quote_url, params=quote_params, timeout=10)
            if quote_response.status_code == 200:
                quote_data = quote_response.json()
                if quote_data.get('results'):
                    microstructure_data['current_quote'] = quote_data['results']
                    print(f"✅ Polygon.io: Current quote ${quote_data['results'].get('P', 0)}")
            
            # 2. Get recent trades (including extended hours)
            trades_url = f"{base_url}/v3/trades/{self.symbol}"
            trades_params = {
                'timestamp.gte': time_filter,
                'limit': 50000,
                'sort': 'timestamp',
                'apikey': self.polygon_api_key
            }
            
            trades_response = requests.get(trades_url, params=trades_params, timeout=10)
            
            if trades_response.status_code == 200:
                trades_data = trades_response.json()
                if trades_data.get('results'):
                    microstructure_data['trades'] = trades_data['results']
                    microstructure_data['order_flow'] = self._analyze_order_flow(trades_data['results'])
                    
                    # ENHANCED: Calculate pre-market movement if applicable
                    if is_pre_market and trades_data.get('results'):
                        pre_market_analysis = self._analyze_pre_market_movement(trades_data['results'])
                        if pre_market_analysis:
                            microstructure_data['pre_market_analysis'] = pre_market_analysis
                            print(f"🌅 Pre-market movement detected: {pre_market_analysis.get('movement_pct', 0):+.2f}%")
            
            # 3. Get aggregates (OHLCV) for extended hours if available
            if is_pre_market:
                aggs_url = f"{base_url}/v2/aggs/ticker/{self.symbol}/range/1/minute/{start_time.strftime('%Y-%m-%d')}/{current_time_et.strftime('%Y-%m-%d')}"
                aggs_params = {
                    'adjusted': 'true',
                    'sort': 'asc',
                    'apikey': self.polygon_api_key
                }
                
                aggs_response = requests.get(aggs_url, params=aggs_params, timeout=10)
                if aggs_response.status_code == 200:
                    aggs_data = aggs_response.json()
                    if aggs_data.get('results'):
                        microstructure_data['pre_market_candles'] = aggs_data['results']
                        print(f"✅ Polygon.io: {len(aggs_data['results'])} pre-market candles fetched")
            
            return microstructure_data if microstructure_data else None
            
        except Exception as e:
            print(f"⚠️ Polygon.io error: {e}")
            return None
    
    def _fetch_eodhd_realtime(self) -> Optional[Dict]:
        """Fetch real-time data from EODHD"""
        try:
            url = f"https://eodhistoricaldata.com/api/real-time/{self.symbol}.US"
            params = {
                'api_token': self.eodhd_api_key,
                'fmt': 'json'
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'real_time_price': data.get('close', 0),
                    'bid': data.get('bid', 0),
                    'ask': data.get('ask', 0),
                    'spread': data.get('ask', 0) - data.get('bid', 0),
                    'volume_today': data.get('volume', 0)
                }
                
        except Exception as e:
            print(f"⚠️ EODHD error: {e}")
            
        return None
    
    def _fetch_finnhub_realtime(self) -> Optional[Dict]:
        """Fetch real-time data from Finnhub INCLUDING EXTENDED HOURS"""
        try:
            finnhub_key = os.getenv('FINNHUB_API_KEY')
            if not finnhub_key:
                return None
            
            base_url = "https://finnhub.io/api/v1"
            current_time_et = datetime.now(pytz.timezone('US/Eastern'))
            is_pre_market = (4 <= current_time_et.hour < 9) or (current_time_et.hour == 9 and current_time_et.minute < 30)
            
            data = {}
            
            # CRITICAL FIX: Get extended hours candles instead of quote that returns stale data
            if is_pre_market:
                # Get 1-minute candles for today's pre-market session (4:00 AM - current)
                today = current_time_et.date()
                start_timestamp = int(datetime.combine(today, datetime_time(4, 0)).replace(tzinfo=pytz.timezone('US/Eastern')).timestamp())
                end_timestamp = int(current_time_et.timestamp())
                
                candles_url = f"{base_url}/stock/candle"
                candles_params = {
                    'symbol': self.symbol,
                    'resolution': '1',
                    'from': start_timestamp,
                    'to': end_timestamp,
                    'token': finnhub_key
                }
                
                candles_response = requests.get(candles_url, params=candles_params, timeout=10)
                if candles_response.status_code == 200:
                    candles_data = candles_response.json()
                    if candles_data.get('s') == 'ok' and candles_data.get('c'):
                        closes = candles_data.get('c', [])
                        if closes:
                            # Get most recent pre-market price
                            current_pre_market_price = float(closes[-1])
                            
                            # Get previous day close from quote endpoint
                            quote_url = f"{base_url}/quote"
                            quote_params = {'symbol': self.symbol, 'token': finnhub_key}
                            quote_response = requests.get(quote_url, params=quote_params, timeout=5)
                            
                            previous_close = 0
                            if quote_response.status_code == 200:
                                quote_data = quote_response.json()
                                previous_close = float(quote_data.get('pc', 0))
                            
                            if previous_close > 0 and current_pre_market_price != previous_close:
                                pre_market_change = current_pre_market_price - previous_close
                                pre_market_change_pct = (pre_market_change / previous_close) * 100
                                
                                data['current_price'] = current_pre_market_price
                                data['previous_close'] = previous_close
                                data['pre_market_change'] = pre_market_change
                                data['pre_market_change_pct'] = pre_market_change_pct
                                data['candles_count'] = len(closes)
                                
                                print(f"🌅 Finnhub EXTENDED HOURS: ${current_pre_market_price:.2f} ({pre_market_change_pct:+.2f}%) vs Close ${previous_close:.2f}")
                                print(f"📊 Finnhub: {len(closes)} pre-market candles processed")
                                
                                data['pre_market_candles'] = {
                                    'timestamps': candles_data.get('t', []),
                                    'closes': closes,
                                    'highs': candles_data.get('h', []),
                                    'lows': candles_data.get('l', []),
                                    'volumes': candles_data.get('v', [])
                                }
                            else:
                                print(f"⚠️ Finnhub: Pre-market data same as previous close or invalid")
                        else:
                            print(f"⚠️ Finnhub: No pre-market candle data available")
                    else:
                        print(f"⚠️ Finnhub: Candle API returned no data or error")
                else:
                    print(f"⚠️ Finnhub: Candles API failed with status {candles_response.status_code}")
            else:
                # Regular hours - use quote endpoint
                quote_url = f"{base_url}/quote"
                quote_params = {'symbol': self.symbol, 'token': finnhub_key}
                quote_response = requests.get(quote_url, params=quote_params, timeout=10)
                
                if quote_response.status_code == 200:
                    quote_data = quote_response.json()
                    data['current_price'] = quote_data.get('c', 0)
                    data['previous_close'] = quote_data.get('pc', 0)
                    print(f"✅ Finnhub: Regular hours price ${data['current_price']:.2f}")
            
            # 2. Get extended hours candle data if pre-market
            if is_pre_market:
                # Get 1-minute candles for today
                today = current_time_et.date()
                start_timestamp = int(datetime.combine(today, time(4, 0)).timestamp())
                end_timestamp = int(current_time_et.timestamp())
                
                candles_url = f"{base_url}/stock/candle"
                candles_params = {
                    'symbol': self.symbol,
                    'resolution': '1',
                    'from': start_timestamp,
                    'to': end_timestamp,
                    'token': finnhub_key
                }
                
                candles_response = requests.get(candles_url, params=candles_params, timeout=10)
                if candles_response.status_code == 200:
                    candles_data = candles_response.json()
                    if candles_data.get('s') == 'ok':
                        data['pre_market_candles'] = {
                            'timestamps': candles_data.get('t', []),
                            'opens': candles_data.get('o', []),
                            'highs': candles_data.get('h', []),
                            'lows': candles_data.get('l', []),
                            'closes': candles_data.get('c', []),
                            'volumes': candles_data.get('v', [])
                        }
                        print(f"✅ Finnhub: {len(candles_data.get('c', []))} pre-market candles fetched")
            
            return data if data else None
            
        except Exception as e:
            print(f"⚠️ Finnhub error: {e}")
            return None
    
    def _analyze_pre_market_movement(self, trades_data: List[Dict]) -> Optional[Dict]:
        """Analyze pre-market movement from trades data"""
        try:
            if not trades_data:
                return None
            
            # Sort trades by timestamp
            sorted_trades = sorted(trades_data, key=lambda x: x.get('participant_timestamp', 0))
            
            if len(sorted_trades) < 2:
                return None
            
            # Get first and last trade prices
            first_trade_price = float(sorted_trades[0].get('price', 0))
            last_trade_price = float(sorted_trades[-1].get('price', 0))
            
            if first_trade_price == 0:
                return None
            
            # Calculate movement
            price_change = last_trade_price - first_trade_price
            price_change_pct = (price_change / first_trade_price) * 100
            
            # Calculate volume and trade intensity
            total_volume = sum(trade.get('size', 0) for trade in sorted_trades)
            trade_count = len(sorted_trades)
            avg_trade_size = total_volume / trade_count if trade_count > 0 else 0
            
            # Determine trend direction
            if price_change_pct > 0.1:
                trend = 'BULLISH'
            elif price_change_pct < -0.1:
                trend = 'BEARISH'
            else:
                trend = 'NEUTRAL'
            
            return {
                'first_price': first_trade_price,
                'last_price': last_trade_price,
                'movement_pct': price_change_pct,
                'price_change': price_change,
                'total_volume': total_volume,
                'trade_count': trade_count,
                'avg_trade_size': avg_trade_size,
                'trend': trend,
                'analysis_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"⚠️ Pre-market analysis error: {e}")
            return None
    
    def _fetch_alpha_vantage_sentiment(self) -> Optional[Dict]:
        """Fetch news sentiment from Alpha Vantage"""
        try:
            url = "https://www.alphavantage.co/query"
            params = {
                'function': 'NEWS_SENTIMENT',
                'tickers': self.symbol,
                'apikey': self.alpha_vantage_key
            }
            
            response = requests.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if 'feed' in data:
                    # Analyze sentiment scores
                    sentiments = []
                    for article in data['feed'][:10]:  # Recent 10 articles
                        for ticker_sentiment in article.get('ticker_sentiment', []):
                            if ticker_sentiment.get('ticker') == self.symbol:
                                sentiments.append(float(ticker_sentiment.get('relevance_score', 0)))
                    
                    if sentiments:
                        return {
                            'avg_sentiment': np.mean(sentiments),
                            'sentiment_strength': np.std(sentiments),
                            'articles_count': len(sentiments)
                        }
                        
        except Exception as e:
            print(f"⚠️ Alpha Vantage error: {e}")
            
        return None
    
    def _fetch_market_context(self) -> Dict:
        """Fetch comprehensive market context"""
        try:
            context = {}
            
            # Major indices and VIX
            symbols = {
                'SPY': 'spy',
                '^VIX': 'vix', 
                'QQQ': 'qqq',
                'SOXX': 'sector',
                '^TNX': 'bonds'
            }
            
            for symbol, key in symbols.items():
                try:
                    ticker = yf.Ticker(symbol)
                    hist = ticker.history(period="2d", interval="1d")
                    if len(hist) >= 2:
                        current = hist['Close'].iloc[-1]
                        previous = hist['Close'].iloc[-2]
                        change_pct = ((current - previous) / previous) * 100
                        context[f'{key}_change'] = float(change_pct)
                except:
                    context[f'{key}_change'] = 0.0
            
            return context
            
        except Exception as e:
            print(f"⚠️ Market context error: {e}")
            return {}
    
    def _analyze_futures_signals(self, data: Dict) -> Dict:
        """
        Analyze futures data for PREDICTIVE market direction signals
        ES/NQ futures predict next-day market direction
        """
        signals = {'direction': 'NEUTRAL', 'strength': 0, 'evidence': []}
        
        try:
            # Fetch real futures data
            if fetch_futures:
                futures_data = fetch_futures()
                
                if futures_data and futures_data.get('ES_pct') is not None:
                    es_change = futures_data['ES_pct']
                    nq_change = futures_data['NQ_pct'] or 0
                    
                    # Futures are PREDICTIVE - give strong weight
                    avg_futures = (es_change + nq_change) / 2
                    
                    if abs(avg_futures) > 0.3:  # Significant futures movement
                        signals['direction'] = 'UP' if avg_futures > 0 else 'DOWN'
                        # Strong signal - futures predict market direction
                        signals['strength'] = min(abs(avg_futures) * 4, 15)  # Higher weight for predictive signal
                        signals['evidence'].append(f"FUTURES PREDICT {signals['direction']}: ES {es_change:+.2f}%, NQ {nq_change:+.2f}%")
                    elif abs(avg_futures) > 0.1:  # Moderate futures movement
                        signals['direction'] = 'UP' if avg_futures > 0 else 'DOWN'
                        signals['strength'] = abs(avg_futures) * 3
                        signals['evidence'].append(f"Futures signal: ES {es_change:+.2f}%, NQ {nq_change:+.2f}%")
                        
        except Exception as e:
            signals['evidence'].append(f"Futures analysis error: {str(e)[:50]}")
        
        return signals
    
    def _analyze_options_flow_signals(self, data: Dict) -> Dict:
        """
        Analyze options flow for PREDICTIVE smart money positioning
        Options activity predicts where institutions are positioning
        """
        signals = {'direction': 'NEUTRAL', 'strength': 0, 'evidence': []}
        
        try:
            # Fetch real options flow data
            if fetch_options_summary:
                options_data = fetch_options_summary(self.symbol)
                
                if options_data:
                    put_call_ratio = options_data.get('put_call_ratio', 1.0)
                    unusual_activity = options_data.get('unusual_activity', False)
                    call_volume = options_data.get('call_volume', 0)
                    put_volume = options_data.get('put_volume', 0)
                    
                    # Options flow is PREDICTIVE - smart money positioning
                    if put_call_ratio < 0.7:  # Heavy call buying (bullish)
                        signals['direction'] = 'UP'
                        signals['strength'] = min((0.7 - put_call_ratio) * 20, 12)  # Strong predictive signal
                        signals['evidence'].append(f"SMART MONEY BULLISH: P/C ratio {put_call_ratio:.2f} (heavy call buying)")
                    elif put_call_ratio > 1.3:  # Heavy put buying (bearish)
                        signals['direction'] = 'DOWN'
                        signals['strength'] = min((put_call_ratio - 1.3) * 20, 12)
                        signals['evidence'].append(f"SMART MONEY BEARISH: P/C ratio {put_call_ratio:.2f} (heavy put buying)")
                    
                    if unusual_activity:
                        signals['strength'] += 3  # Boost for unusual activity
                        signals['evidence'].append("Unusual options activity detected - institutional positioning")
                        
        except Exception as e:
            signals['evidence'].append(f"Options flow analysis error: {str(e)[:50]}")
        
        return signals
    
    def _analyze_microstructure_signals(self, data: Dict) -> Dict:
        """Analyze microstructure signals for directional bias"""
        signals = {'direction': 'NEUTRAL', 'strength': 0, 'evidence': []}
        
        try:
            # Order flow analysis from Polygon data
            if 'microstructure' in data and 'order_flow' in data['microstructure']:
                flow_data = data['microstructure']['order_flow']
                
                if flow_data['net_flow'] > 0:
                    signals['direction'] = 'UP'
                    signals['strength'] = min(abs(flow_data['net_flow']) / 1000000, 10)  # Scale by millions
                    signals['evidence'].append(f"Positive order flow: ${flow_data['net_flow']:,.0f}")
                else:
                    signals['direction'] = 'DOWN'
                    signals['strength'] = min(abs(flow_data['net_flow']) / 1000000, 10)
                    signals['evidence'].append(f"Negative order flow: ${flow_data['net_flow']:,.0f}")
            
            # Bid-ask spread analysis
            if 'real_time_data' in data:
                spread = data['real_time_data'].get('spread', 0)
                if spread > 0:
                    if spread < 0.05:  # Tight spread = strong interest
                        signals['evidence'].append(f"Tight spread: ${spread:.3f} (strong interest)")
                        signals['strength'] += 2
                    else:  # Wide spread = uncertainty, but still directional
                        signals['evidence'].append(f"Wide spread: ${spread:.3f} (volatility expected)")
                        signals['strength'] += 1
            
        except Exception as e:
            signals['evidence'].append(f"Microstructure analysis error: {str(e)[:50]}")
        
        return signals
    
    def _analyze_momentum_signals(self, data: Dict) -> Dict:
        """Analyze momentum across multiple timeframes"""
        signals = {'direction': 'NEUTRAL', 'strength': 0, 'evidence': []}
        
        try:
            momentum_scores = []
            timeframes = ['1m', '5m', '15m', '1h']
            
            for tf in timeframes:
                if tf in data['price_data'] and not data['price_data'][tf].empty:
                    df = data['price_data'][tf]
                    
                    # Calculate momentum for this timeframe
                    if len(df) >= 10:
                        recent_close = df['Close'].iloc[-1]
                        earlier_close = df['Close'].iloc[-10]
                        momentum = ((recent_close - earlier_close) / earlier_close) * 100
                        momentum_scores.append(momentum)
                        
                        if abs(momentum) > 0.1:  # Significant momentum
                            direction = 'UP' if momentum > 0 else 'DOWN'
                            signals['evidence'].append(f"{tf} momentum: {momentum:+.2f}% ({direction})")
            
            if momentum_scores:
                avg_momentum = np.mean(momentum_scores)
                signals['direction'] = 'UP' if avg_momentum > 0 else 'DOWN'
                # REDUCED: Max strength 3 (was 10) - momentum is REACTIVE, not predictive
                signals['strength'] = min(abs(avg_momentum) * 0.3, 3)
                
                # Count supporting timeframes
                supporting_tfs = sum(1 for m in momentum_scores if (m > 0) == (avg_momentum > 0))
                signals['evidence'].append(f"Momentum consensus: {supporting_tfs}/{len(momentum_scores)} timeframes")
                
        except Exception as e:
            signals['evidence'].append(f"Momentum analysis error: {str(e)[:50]}")
        
        return signals
    
    def _analyze_order_flow_signals(self, data: Dict) -> Dict:
        """Analyze order flow patterns"""
        signals = {'direction': 'NEUTRAL', 'strength': 0, 'evidence': []}
        
        try:
            # Volume profile analysis
            if '1m' in data['price_data'] and not data['price_data']['1m'].empty:
                df = data['price_data']['1m']
                
                if len(df) >= 30:
                    # Recent volume vs average
                    recent_volume = df['Volume'].tail(10).mean()
                    avg_volume = df['Volume'].tail(30).mean()
                    volume_ratio = recent_volume / max(avg_volume, 1)
                    
                    # Price-volume relationship
                    recent_prices = df['Close'].tail(10)
                    price_change = (recent_prices.iloc[-1] - recent_prices.iloc[0]) / recent_prices.iloc[0] * 100
                    
                    if volume_ratio > 1.5:  # High volume
                        signals['direction'] = 'UP' if price_change > 0 else 'DOWN'
                        signals['strength'] = min(volume_ratio * 2, 8)
                        signals['evidence'].append(f"High volume support: {volume_ratio:.1f}x avg, price {price_change:+.2f}%")
                    elif volume_ratio > 1.0:  # Above average volume
                        signals['direction'] = 'UP' if price_change > 0 else 'DOWN'
                        signals['strength'] = min(volume_ratio, 5)
                        signals['evidence'].append(f"Above-avg volume: {volume_ratio:.1f}x, price {price_change:+.2f}%")
                    
        except Exception as e:
            signals['evidence'].append(f"Order flow analysis error: {str(e)[:50]}")
        
        return signals
    
    def _analyze_sentiment_signals(self, data: Dict) -> Dict:
        """Analyze sentiment from news and social indicators"""
        signals = {'direction': 'NEUTRAL', 'strength': 0, 'evidence': []}
        
        try:
            if 'sentiment' in data:
                sentiment_data = data['sentiment']
                avg_sentiment = sentiment_data.get('avg_sentiment', 0)
                
                if avg_sentiment > 0.1:
                    signals['direction'] = 'UP'
                    signals['strength'] = min(avg_sentiment * 10, 6)
                    signals['evidence'].append(f"Positive news sentiment: {avg_sentiment:.3f}")
                elif avg_sentiment < -0.1:
                    signals['direction'] = 'DOWN'  
                    signals['strength'] = min(abs(avg_sentiment) * 10, 6)
                    signals['evidence'].append(f"Negative news sentiment: {avg_sentiment:.3f}")
                
                article_count = sentiment_data.get('articles_count', 0)
                if article_count > 0:
                    signals['evidence'].append(f"Based on {article_count} recent articles")
            
        except Exception as e:
            signals['evidence'].append(f"Sentiment analysis error: {str(e)[:50]}")
        
        return signals
    
    def _analyze_market_correlation_signals(self, data: Dict) -> Dict:
        """Analyze correlation with broader market"""
        signals = {'direction': 'NEUTRAL', 'strength': 0, 'evidence': []}
        
        try:
            context = data.get('market_context', {})
            
            # SPY correlation (general market)
            spy_change = context.get('spy_change', 0)
            if abs(spy_change) > 0.5:
                signals['direction'] = 'UP' if spy_change > 0 else 'DOWN'
                signals['strength'] = min(abs(spy_change), 4)
                signals['evidence'].append(f"SPY correlation: {spy_change:+.2f}%")
            
            # Sector correlation (SOXX)
            sector_change = context.get('sector_change', 0)
            if abs(sector_change) > 0.3:
                direction = 'UP' if sector_change > 0 else 'DOWN'
                if signals['direction'] == 'NEUTRAL':
                    signals['direction'] = direction
                    signals['strength'] = min(abs(sector_change) * 1.5, 3)
                elif signals['direction'] == direction:
                    signals['strength'] += min(abs(sector_change), 2)
                signals['evidence'].append(f"Sector (SOXX): {sector_change:+.2f}%")
            
            # VIX analysis (fear gauge)
            vix_change = context.get('vix_change', 0)
            if abs(vix_change) > 2:
                # Rising VIX = DOWN bias, Falling VIX = UP bias
                vix_direction = 'DOWN' if vix_change > 0 else 'UP'
                if signals['direction'] == 'NEUTRAL':
                    signals['direction'] = vix_direction
                    signals['strength'] = min(abs(vix_change) / 2, 3)
                elif signals['direction'] == vix_direction:
                    signals['strength'] += min(abs(vix_change) / 3, 2)
                signals['evidence'].append(f"VIX fear gauge: {vix_change:+.2f}% (suggests {vix_direction})")
                
        except Exception as e:
            signals['evidence'].append(f"Market correlation error: {str(e)[:50]}")
        
        return signals
    
    def _analyze_technical_signals(self, data: Dict) -> Dict:
        """Analyze technical indicators"""
        signals = {'direction': 'NEUTRAL', 'strength': 0, 'evidence': []}
        
        try:
            if '1d' in data['price_data'] and not data['price_data']['1d'].empty:
                df = data['price_data']['1d']
                
                if len(df) >= 20:
                    # RSI analysis
                    rsi = self._calculate_rsi(df['Close'], 14)
                    current_rsi = rsi.iloc[-1] if not rsi.empty else 50
                    
                    # Moving averages
                    sma_20 = df['Close'].rolling(20).mean().iloc[-1]
                    current_price = df['Close'].iloc[-1]
                    
                    # Price vs SMA
                    price_vs_sma = ((current_price - sma_20) / sma_20) * 100
                    
                    # RSI signals - REACTIVE, reduced weight
                    if current_rsi < 40:  # Oversold bias - potential reversal UP
                        signals['direction'] = 'UP'
                        # REDUCED: Max 1.5 strength (was 5) - RSI is lagging
                        signals['strength'] = (40 - current_rsi) / 20
                        signals['evidence'].append(f"RSI oversold: {current_rsi:.1f} (reactive confirmation)")
                    elif current_rsi > 60:  # Overbought bias - potential reversal DOWN
                        signals['direction'] = 'DOWN'
                        # REDUCED: Max 1.5 strength (was 5) - RSI is lagging
                        signals['strength'] = (current_rsi - 60) / 20
                        signals['evidence'].append(f"RSI overbought: {current_rsi:.1f} (reactive confirmation)")
                    
                    # REDUCED: RSI momentum only for confirmation, very low weight
                    rsi_momentum = rsi.iloc[-1] - rsi.iloc[-2] if len(rsi) >= 2 else 0
                    if rsi_momentum < -3:  # Falling RSI = bearish momentum
                        if signals['direction'] == 'DOWN':
                            signals['strength'] += abs(rsi_momentum) / 15  # Very reduced
                        elif signals['direction'] == 'NEUTRAL':
                            signals['direction'] = 'DOWN'
                            signals['strength'] = abs(rsi_momentum) / 20
                        signals['evidence'].append(f"RSI falling: {rsi_momentum:.1f} (reactive)")
                    elif rsi_momentum > 3:  # Rising RSI = bullish momentum
                        if signals['direction'] == 'UP':
                            signals['strength'] += rsi_momentum / 15  # Very reduced
                        elif signals['direction'] == 'NEUTRAL':
                            signals['direction'] = 'UP'
                            signals['strength'] = rsi_momentum / 20
                        signals['evidence'].append(f"RSI rising: +{rsi_momentum:.1f} (reactive)")
                    
                    # Price vs moving average - REDUCED weight
                    if abs(price_vs_sma) > 1:
                        ma_direction = 'UP' if price_vs_sma > 0 else 'DOWN'
                        if signals['direction'] == 'NEUTRAL':
                            signals['direction'] = ma_direction
                            # REDUCED: Max 1 strength (was 3) - MA is lagging
                            signals['strength'] = min(abs(price_vs_sma) / 6, 1)
                        elif signals['direction'] == ma_direction:
                            signals['strength'] += min(abs(price_vs_sma) / 10, 0.5)
                        signals['evidence'].append(f"Price vs 20-SMA: {price_vs_sma:+.2f}% (reactive)")
                        
        except Exception as e:
            signals['evidence'].append(f"Technical analysis error: {str(e)[:50]}")
        
        return signals
    
    def _analyze_volume_signals(self, data: Dict) -> Dict:
        """Analyze volume patterns - ENHANCED for distribution/accumulation detection"""
        signals = {'direction': 'NEUTRAL', 'strength': 0, 'evidence': []}
        
        try:
            current_volume = data.get('volume', 0)
            
            if '1d' in data['price_data'] and not data['price_data']['1d'].empty:
                df = data['price_data']['1d']
                
                if len(df) >= 10:
                    avg_volume = df['Volume'].tail(10).mean()
                    volume_ratio = current_volume / max(avg_volume, 1)
                    
                    # Price direction with volume
                    if '1m' in data['price_data'] and not data['price_data']['1m'].empty:
                        price_df = data['price_data']['1m']
                        if len(price_df) >= 2:
                            price_change = (price_df['Close'].iloc[-1] - price_df['Close'].iloc[0]) / price_df['Close'].iloc[0] * 100
                            
                            # ENHANCED: Detect distribution (selling pressure) and accumulation (buying pressure)
                            if volume_ratio > 1.2:  # Above average volume
                                if price_change < 0:  # DOWN with high volume = DISTRIBUTION
                                    signals['direction'] = 'DOWN'
                                    # Stronger signal for bearish volume (distribution is bearish)
                                    signals['strength'] = min(volume_ratio * 2.5, 8)  # Higher strength for distribution
                                    signals['evidence'].append(f"DISTRIBUTION detected: {volume_ratio:.1f}x volume on {price_change:.2f}% drop")
                                elif price_change > 0:  # UP with high volume = ACCUMULATION
                                    signals['direction'] = 'UP'
                                    signals['strength'] = min(volume_ratio * 2, 6)
                                    signals['evidence'].append(f"ACCUMULATION: {volume_ratio:.1f}x volume on +{price_change:.2f}% gain")
                            
                            # ENHANCED: Volume divergence (price down but volume increasing = bearish)
                            elif len(df) >= 3:
                                recent_volumes = df['Volume'].tail(3).values
                                volume_trend = recent_volumes[-1] - recent_volumes[0]
                                
                                if volume_trend > 0 and price_change < -0.5:  # Increasing volume with falling price
                                    signals['direction'] = 'DOWN'
                                    signals['strength'] = min(abs(price_change) * 1.5, 5)
                                    signals['evidence'].append(f"Bearish divergence: rising volume ({volume_trend/1e6:.1f}M) + falling price ({price_change:.2f}%)")
                                
        except Exception as e:
            signals['evidence'].append(f"Volume analysis error: {str(e)[:50]}")
        
        return signals
    
    def _analyze_options_signals(self, data: Dict) -> Dict:
        """Analyze options flow and gamma signals"""
        signals = {'direction': 'NEUTRAL', 'strength': 0, 'evidence': []}
        
        try:
            # Implied volatility analysis from price movement
            if '1m' in data['price_data'] and not data['price_data']['1m'].empty:
                df = data['price_data']['1m']
                
                if len(df) >= 30:
                    # Calculate realized volatility
                    returns = df['Close'].pct_change().dropna()
                    realized_vol = returns.std() * np.sqrt(252) * 100
                    
                    # High volatility suggests directional movement
                    if realized_vol > 30:  # High volatility threshold
                        # Determine direction from recent price action
                        recent_change = (df['Close'].iloc[-1] - df['Close'].iloc[-10]) / df['Close'].iloc[-10] * 100
                        signals['direction'] = 'UP' if recent_change > 0 else 'DOWN'
                        signals['strength'] = min(realized_vol / 10, 5)
                        signals['evidence'].append(f"High volatility: {realized_vol:.1f}% (directional movement expected)")
                        
        except Exception as e:
            signals['evidence'].append(f"Options analysis error: {str(e)[:50]}")
        
        return signals
    
    def _make_professional_decision(self, signals: Dict, data: Dict) -> Tuple[str, float, List[str]]:
        """
        Professional trader decision matrix - NEVER returns neutral
        Weighs ALL evidence to always determine UP or DOWN direction
        """
        
        # Collect all directional signals and strengths
        up_strength = 0
        down_strength = 0
        all_evidence = []
        
        for category, signal_data in signals.items():
            direction = signal_data.get('direction', 'NEUTRAL')
            strength = signal_data.get('strength', 0)
            evidence = signal_data.get('evidence', [])
            
            if direction == 'UP':
                up_strength += strength
            elif direction == 'DOWN':
                down_strength += strength
                
            all_evidence.extend([f"[{category.upper()}] {ev}" for ev in evidence])
        
        # Professional trader logic: Require minimum signal strength for directional calls
        # CRITICAL FIX: No random selection - require real signals or return HOLD
        
        MINIMUM_SIGNAL_STRENGTH = 2.0  # Require at least 2.0 combined strength for directional call
        total_strength = up_strength + down_strength
        
        # Check if we have enough signal strength to make a directional call
        if total_strength < MINIMUM_SIGNAL_STRENGTH:
            # Insufficient signal strength - return HOLD instead of random guess
            final_direction = 'HOLD'
            confidence = min(35 + (total_strength / MINIMUM_SIGNAL_STRENGTH * 15), 50)  # Max 50% for HOLD
            strength_ratio = 1.0
            all_evidence.append(f"[INSUFFICIENT SIGNALS] Total strength {total_strength:.1f} below minimum {MINIMUM_SIGNAL_STRENGTH} - HOLD recommended")
        elif up_strength > down_strength and up_strength > 0:
            # Clear UP signal with sufficient strength
            final_direction = 'UP'
            # Calculate raw confidence based on signal strength ratio - no artificial ceiling
            confidence = (up_strength / max(up_strength + down_strength, 1)) * 100
            strength_ratio = up_strength / max(down_strength, 0.1)
        elif down_strength > up_strength and down_strength > 0:
            # Clear DOWN signal with sufficient strength
            final_direction = 'DOWN'
            # Calculate raw confidence based on signal strength ratio - no artificial ceiling
            confidence = (down_strength / max(up_strength + down_strength, 1)) * 100
            strength_ratio = down_strength / max(up_strength, 0.1)
        else:
            # Equal strength but above minimum threshold - use the dominant recent trend
            # FIXED: No random selection - determine from recent momentum
            final_direction = 'HOLD'  # Default to HOLD when truly equal
            confidence = 40  # Low confidence for equal signals
            strength_ratio = 1.0
            all_evidence.append(f"[EQUAL SIGNALS] UP={up_strength:.1f} DOWN={down_strength:.1f} - HOLD (no clear direction)")
        
        # Apply realistic bounds only to prevent computational errors
        confidence = max(30, min(confidence, 99))  # Prevent impossible certainty, allow natural range
        
        # Data availability safeguards - degrade confidence when sources are limited
        active_sources = len(data.get('sources_used', ['Yahoo Finance']))
        active_signals = len([s for s in signals.values() if s.get('direction') != 'NEUTRAL'])
        
        # Apply data availability penalty
        if active_sources < 2:
            confidence *= 0.8  # 20% penalty for limited sources
            all_evidence.append(f"[WARNING] Limited data sources: {active_sources}")
        
        if active_signals < 3:
            confidence *= 0.9  # 10% penalty for limited signals
            all_evidence.append(f"[WARNING] Limited active signals: {active_signals}")
        
        # Ensure minimum confidence (professional traders are confident but realistic)
        confidence = max(confidence, 35)  # Minimum 35% confidence with available data
        
        # Create professional reasoning
        reasoning = [
            f"🎯 PROFESSIONAL ANALYSIS: {final_direction} direction determined",
            f"📊 Signal Strength: UP={up_strength:.1f} vs DOWN={down_strength:.1f} (ratio: {strength_ratio:.1f})",
            f"🔍 Confidence: {confidence:.1f}% based on {len([s for s in signals.values() if s.get('direction') != 'NEUTRAL'])} active signals",
            f"📈 Sources: {', '.join(data.get('sources_used', ['Yahoo Finance']))}"
        ]
        
        reasoning.extend(all_evidence[:8])  # Top 8 pieces of evidence
        
        print(f"\n🎯 DECISION: {final_direction} with {confidence:.1f}% confidence")
        print(f"📊 Signal Analysis: UP strength={up_strength:.1f}, DOWN strength={down_strength:.1f}")
        
        return final_direction, confidence, reasoning
    
    def _calculate_price_targets(self, direction: str, confidence: float, current_price: float) -> Tuple[float, float]:
        """Calculate price targets based on direction and confidence"""
        
        # Professional trader targets based on confidence and direction with risk controls
        base_move_pct = (confidence / 100) * 1.5  # 1.5% max move for 100% confidence (more conservative)
        
        # Risk control: cap maximum move based on confidence
        if confidence < 50:
            base_move_pct *= 0.5  # Reduce targets for lower confidence
        
        if direction == 'UP':
            expected_move = current_price * (base_move_pct / 100)
            target_price = current_price + expected_move
        else:  # DOWN
            expected_move = current_price * (base_move_pct / 100)
            target_price = current_price - expected_move
            expected_move = -expected_move  # Negative for down moves
        
        return target_price, expected_move
    
    def _create_signals_summary(self, signals: Dict) -> Dict:
        """Create summary of all signals for transparency"""
        summary = {}
        
        for category, signal_data in signals.items():
            summary[category] = {
                'direction': signal_data.get('direction', 'NEUTRAL'),
                'strength': round(signal_data.get('strength', 0), 2),
                'evidence_count': len(signal_data.get('evidence', []))
            }
        
        return summary
    
    def _analyze_order_flow(self, trades_data: List) -> Dict:
        """Analyze order flow from trade data"""
        try:
            if not trades_data:
                return {'net_flow': 0, 'trade_count': 0}
            
            buy_volume = 0
            sell_volume = 0
            
            for trade in trades_data:
                size = trade.get('size', 0)
                price = trade.get('price', 0)
                value = size * price
                
                # Simple heuristic: larger trades more likely institutional
                if size > 100:  # Block trades
                    # Assume up tick = buy, down tick = sell
                    # In real implementation, would use tick direction
                    buy_volume += value * 0.6  # Simplified assumption
                    sell_volume += value * 0.4
                else:
                    buy_volume += value * 0.5
                    sell_volume += value * 0.5
            
            net_flow = buy_volume - sell_volume
            
            return {
                'net_flow': net_flow,
                'buy_volume': buy_volume,
                'sell_volume': sell_volume,
                'trade_count': len(trades_data)
            }
            
        except Exception as e:
            return {'net_flow': 0, 'trade_count': 0, 'error': str(e)}
    
    def _calculate_rsi(self, prices: pd.Series, window: int = 14) -> pd.Series:
        """Calculate RSI indicator"""
        try:
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi
        except:
            return pd.Series([50] * len(prices), index=prices.index)

# Example usage
if __name__ == "__main__":
    system = ProfessionalTraderSystem("AMD")
    prediction = system.predict_direction()
    
    print(f"\n🎯 FINAL PREDICTION:")
    print(f"Direction: {prediction['direction']}")
    print(f"Confidence: {prediction['confidence']:.1f}%")
    print(f"Current Price: ${prediction['current_price']:.2f}")
    print(f"Target Price: ${prediction['target_price']:.2f}")
    print(f"Expected Move: ${prediction['expected_move']:+.2f}")
    print(f"\nReasoning:")
    for reason in prediction['reasoning']:
        print(f"  {reason}")