#!/usr/bin/env python3
"""
Forex Data Fetcher - Live Data Sources
Replaces hardcoded values with real-time data
Integrates: FRED, Alpha Vantage, FMP, Polygon APIs
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ForexDataFetcher:
    """Fetch live forex data from various sources"""
    
    def __init__(self):
        self.cache = {}
        self.cache_duration = 3600  # 1 hour cache
        
        # Load API keys from environment
        self.fred_api_key = os.getenv('FRED_API_KEY')
        self.alpha_vantage_key = os.getenv('ALPHA_VANTAGE_API_KEY')
        self.fmp_api_key = os.getenv('FMP_API_KEY')
        self.polygon_api_key = os.getenv('POLYGON_API_KEY')
        
        # Print API status
        apis_loaded = []
        if self.fred_api_key: apis_loaded.append('FRED✓')
        if self.alpha_vantage_key: apis_loaded.append('AlphaVantage✓')
        if self.fmp_api_key: apis_loaded.append('FMP✓')
        if self.polygon_api_key: apis_loaded.append('Polygon✓')
        
        if apis_loaded:
            print(f"🔑 APIs Loaded: {' | '.join(apis_loaded)}")
        else:
            print("⚠️ No API keys loaded from .env file")
    
    def fetch_interest_rates(self, use_fred=True, fred_api_key=None):
        """
        Fetch current interest rates (AUTO-UPDATES USD via FRED API)
        
        Parameters:
        - use_fred: If True, attempts to use FRED API for USD rate (DEFAULT: True)
        - fred_api_key: FRED API key (optional - uses public endpoint if None)
        
        Live Rates:
        - USD: Auto-fetched from FRED API (Fed Funds Rate)
        - EUR: Manual (update after ECB meetings)
        - GBP: Manual (update after BoE meetings)
        - JPY: Manual (update after BoJ meetings)
        """
        
        # Initialize with manual baseline (fallback)
        rates = {
            'USD': 5.50,  # Fed Funds Rate (Fallback if FRED fails)
            'EUR': 4.00,  # ECB Deposit Rate (Manual - update after meetings)
            'GBP': 5.00,  # BoE Base Rate (Manual - update after meetings)
            'JPY': 0.10   # BoJ Policy Rate (Manual - rarely changes)
        }
        
        # Method 1: Try FRED API for USD rate (AUTO-UPDATE)
        if use_fred:
            try:
                # Try using fredapi package first
                try:
                    from fredapi import Fred
                    
                    # Use API key priority: parameter > environment > try CSV fallback
                    api_key_to_use = fred_api_key or self.fred_api_key
                    
                    if api_key_to_use:
                        fred = Fred(api_key=api_key_to_use)
                    else:
                        # No API key, will fallback to CSV method
                        raise ImportError("No FRED API key, trying CSV")
                    
                    usd_rate = float(fred.get_series_latest_release('DFF')[-1])
                    rates['USD'] = usd_rate
                    
                    print(f"✅ Interest rates (USD auto-fetched from FRED):")
                    print(f"   USD: {rates['USD']:.2f}% (LIVE from FRED API) ✓")
                    
                except ImportError:
                    # Fallback: Try direct FRED API call without package
                    import requests
                    
                    # FRED API endpoint (no key required for recent data)
                    url = 'https://fred.stlouisfed.org/graph/fredgraph.csv?id=DFF'
                    response = requests.get(url, timeout=5)
                    
                    if response.status_code == 200:
                        # Parse CSV response
                        lines = response.text.strip().split('\n')
                        if len(lines) > 1:
                            # Last line has most recent data
                            last_line = lines[-1].split(',')
                            if len(last_line) >= 2 and last_line[1] != '.':
                                usd_rate = float(last_line[1])
                                rates['USD'] = usd_rate
                                print(f"✅ Interest rates (USD auto-fetched from FRED):")
                                print(f"   USD: {rates['USD']:.2f}% (LIVE from FRED) ✓")
                            else:
                                raise ValueError("Invalid FRED data")
                    else:
                        raise ValueError(f"FRED API returned {response.status_code}")
                        
            except Exception as e:
                print(f"⚠️ FRED API failed: {e}")
                print(f"   Using manual USD rate: {rates['USD']}%")
                print(f"✅ Interest rates (manual fallback):")
                print(f"   USD: {rates['USD']:.2f}% (Manual - verify current rate!)")
        else:
            print(f"✅ Interest rates (manual mode):")
            print(f"   USD: {rates['USD']:.2f}% (Manual)")
        
        # Print other manual rates
        print(f"   EUR: {rates['EUR']:.2f}% (Manual - update after ECB meetings)")
        print(f"   GBP: {rates['GBP']:.2f}% (Manual - update after BoE meetings)")
        print(f"   JPY: {rates['JPY']:.2f}% (Manual - rarely changes)")
        print(f"\n   ⚠️ UPDATE MANUAL RATES AFTER CENTRAL BANK MEETINGS:")
        print(f"   - ECB (every 6 weeks): https://www.ecb.europa.eu/")
        print(f"   - BoE (monthly): https://www.bankofengland.co.uk/")
        print(f"   - BoJ (rarely): https://www.boj.or.jp/en/")
        
        return rates
    
    def calculate_support_resistance(self, hist, period=20):
        """
        Calculate support and resistance levels
        """
        if hist is None or len(hist) < period:
            return None
        
        # Get recent highs and lows
        recent_highs = hist['High'].tail(period)
        recent_lows = hist['Low'].tail(period)
        
        # Find swing points
        resistance_levels = []
        support_levels = []
        
        # Method 1: Recent peaks and troughs
        for i in range(2, len(recent_highs)-2):
            # Check if it's a peak (higher than neighbors)
            if recent_highs.iloc[i] > recent_highs.iloc[i-1] and \
               recent_highs.iloc[i] > recent_highs.iloc[i+1]:
                resistance_levels.append(float(recent_highs.iloc[i]))
            
            # Check if it's a trough (lower than neighbors)
            if recent_lows.iloc[i] < recent_lows.iloc[i-1] and \
               recent_lows.iloc[i] < recent_lows.iloc[i+1]:
                support_levels.append(float(recent_lows.iloc[i]))
        
        # Get current price
        current_price = float(hist['Close'].iloc[-1])
        
        # Find nearest resistance above current price
        resistance_above = [r for r in resistance_levels if r > current_price]
        nearest_resistance = min(resistance_above) if resistance_above else current_price * 1.02
        
        # Find nearest support below current price
        support_below = [s for s in support_levels if s < current_price]
        nearest_support = max(support_below) if support_below else current_price * 0.98
        
        # Calculate distances
        distance_to_resistance = ((nearest_resistance - current_price) / current_price) * 100
        distance_to_support = ((current_price - nearest_support) / current_price) * 100
        
        return {
            'resistance': nearest_resistance,
            'support': nearest_support,
            'current_price': current_price,
            'distance_to_resistance_pct': distance_to_resistance,
            'distance_to_support_pct': distance_to_support,
            'near_resistance': distance_to_resistance < 0.5,  # Within 0.5%
            'near_support': distance_to_support < 0.5
        }
    
    def calculate_pivot_points(self, hist):
        """
        Calculate daily pivot points (standard method)
        """
        if hist is None or len(hist) < 2:
            return None
        
        # Get yesterday's data
        yesterday = hist.iloc[-2]
        high = float(yesterday['High'])
        low = float(yesterday['Low'])
        close = float(yesterday['Close'])
        
        # Standard Pivot Points
        pivot = (high + low + close) / 3
        
        # Resistance levels
        r1 = (2 * pivot) - low
        r2 = pivot + (high - low)
        r3 = high + 2 * (pivot - low)
        
        # Support levels
        s1 = (2 * pivot) - high
        s2 = pivot - (high - low)
        s3 = low - 2 * (high - pivot)
        
        current_price = float(hist['Close'].iloc[-1])
        
        # Determine position relative to pivot
        if current_price > pivot:
            bias = 'bullish'
            next_target = r1
            next_support = pivot
        else:
            bias = 'bearish'
            next_target = s1
            next_support = s2
        
        return {
            'pivot': pivot,
            'r1': r1,
            'r2': r2,
            'r3': r3,
            's1': s1,
            's2': s2,
            's3': s3,
            'bias': bias,
            'next_target': next_target,
            'next_support': next_support
        }
    
    def fetch_gold_price(self):
        """
        Fetch Gold price and trend with MOMENTUM EXHAUSTION detection
        """
        try:
            gold = yf.Ticker('GC=F')  # Gold Futures
            gold_hist = gold.history(period='30d')  # Need more data for RSI
            
            if gold_hist.empty:
                return None
            
            current_gold = float(gold_hist['Close'].iloc[-1])
            week_ago_gold = float(gold_hist['Close'].iloc[-10]) if len(gold_hist) >= 10 else gold_hist['Close'].iloc[0]
            
            gold_change_pct = ((current_gold - week_ago_gold) / week_ago_gold) * 100
            
            # Calculate RSI for exhaustion detection
            close = gold_hist['Close']
            delta = close.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            current_rsi = float(rsi.iloc[-1]) if not rsi.empty else 50
            
            # MOMENTUM EXHAUSTION DETECTION
            exhaustion_risk = False
            reversal_signal = False
            
            if gold_change_pct > 3 and current_rsi > 70:
                # Strong rally + overbought = EXHAUSTION RISK
                exhaustion_risk = True
                trend = 'exhausted_up'  # Topping signal
            elif gold_change_pct < -3 and current_rsi < 30:
                # Strong selloff + oversold = BOUNCE POTENTIAL
                reversal_signal = True
                trend = 'oversold_down'  # Bottoming signal
            elif gold_change_pct > 1:
                trend = 'strong_up'
            elif gold_change_pct > 0.3:
                trend = 'up'
            elif gold_change_pct < -1:
                trend = 'strong_down'
            elif gold_change_pct < -0.3:
                trend = 'down'
            else:
                trend = 'neutral'
            
            return {
                'price': current_gold,
                'change_pct': gold_change_pct,
                'trend': trend,
                'rsi': current_rsi,
                'exhaustion_risk': exhaustion_risk,
                'reversal_signal': reversal_signal
            }
        
        except Exception as e:
            print(f"⚠️ Gold data error: {e}")
            return None
    
    def fetch_es_futures(self):
        """
        Fetch ES (S&P 500) Futures - FORWARD-LOOKING risk sentiment
        This shows what market EXPECTS tomorrow (not yesterday's performance)
        """
        try:
            # ES futures (E-mini S&P 500)
            es = yf.Ticker('ES=F')
            es_hist = es.history(period='5d')
            
            if es_hist.empty:
                return None
            
            current_es = float(es_hist['Close'].iloc[-1])
            prev_close_es = float(es_hist['Close'].iloc[-2]) if len(es_hist) > 1 else current_es
            
            # ES futures change (intraday or overnight)
            es_change_pct = ((current_es - prev_close_es) / prev_close_es) * 100
            
            # Determine risk sentiment from futures
            if es_change_pct > 0.5:
                sentiment = 'risk_on'
                sentiment_strength = 'strong' if es_change_pct > 1.0 else 'moderate'
            elif es_change_pct < -0.5:
                sentiment = 'risk_off'
                sentiment_strength = 'strong' if es_change_pct < -1.0 else 'moderate'
            else:
                sentiment = 'neutral'
                sentiment_strength = 'weak'
            
            return {
                'price': current_es,
                'change_pct': es_change_pct,
                'sentiment': sentiment,
                'strength': sentiment_strength,
                'forward_looking': True  # This is PREDICTIVE (futures)
            }
        
        except Exception as e:
            print(f"⚠️ ES Futures data error: {e}")
            return None
    
    def fetch_oil_price(self):
        """
        Fetch Oil price and trend (for CAD correlation)
        """
        try:
            oil = yf.Ticker('CL=F')  # Crude Oil Futures
            oil_hist = oil.history(period='10d')
            
            if oil_hist.empty:
                return None
            
            current_oil = float(oil_hist['Close'].iloc[-1])
            week_ago_oil = float(oil_hist['Close'].iloc[0])
            
            oil_change_pct = ((current_oil - week_ago_oil) / week_ago_oil) * 100
            
            # Determine trend
            if oil_change_pct > 2:
                trend = 'strong_up'
            elif oil_change_pct > 0.5:
                trend = 'up'
            elif oil_change_pct < -2:
                trend = 'strong_down'
            elif oil_change_pct < -0.5:
                trend = 'down'
            else:
                trend = 'neutral'
            
            return {
                'price': current_oil,
                'change_pct': oil_change_pct,
                'trend': trend
            }
        
        except Exception as e:
            print(f"⚠️ Oil data error: {e}")
            return None
    
    def fetch_10y_yield(self):
        """
        Fetch 10Y Treasury Yield (for interest rate expectations)
        """
        try:
            tnx = yf.Ticker('^TNX')
            tnx_hist = tnx.history(period='10d')
            
            if tnx_hist.empty:
                return None
            
            current_yield = float(tnx_hist['Close'].iloc[-1])
            week_ago_yield = float(tnx_hist['Close'].iloc[0])
            
            yield_change = current_yield - week_ago_yield
            
            # Rising yields = USD strength
            if yield_change > 0.1:
                trend = 'rising'
                usd_impact = 'bullish'
            elif yield_change < -0.1:
                trend = 'falling'
                usd_impact = 'bearish'
            else:
                trend = 'stable'
                usd_impact = 'neutral'
            
            return {
                'yield': current_yield,
                'change': yield_change,
                'trend': trend,
                'usd_impact': usd_impact
            }
        
        except Exception as e:
            print(f"⚠️ 10Y Yield error: {e}")
            return None
    
    def check_economic_calendar_today(self):
        """
        Check if major economic events today/tomorrow
        Manual method - user should check Forex Factory
        """
        today = datetime.now()
        day_of_month = today.day
        day_of_week = today.weekday()  # 0=Monday, 4=Friday
        
        warnings = []
        risk_level = 'normal'
        
        # Check for NFP (First Friday of month)
        if day_of_week == 4 and 1 <= day_of_month <= 7:
            warnings.append("⚠️ NFP (Non-Farm Payrolls) likely tomorrow!")
            risk_level = 'high'
        
        # Check for mid-month (CPI usually)
        if 10 <= day_of_month <= 15:
            warnings.append("⚠️ Mid-month: Check for CPI/PPI releases")
            risk_level = 'medium'
        
        # Check for FOMC week (usually 3rd week)
        if 15 <= day_of_month <= 22:
            warnings.append("⚠️ FOMC meeting week possible - check calendar")
            risk_level = 'medium'
        
        # Month-end (often volatile)
        if day_of_month >= 28:
            warnings.append("ℹ️ Month-end: Increased volatility possible")
        
        return {
            'risk_level': risk_level,
            'warnings': warnings,
            'recommendation': 'Check Forex Factory calendar before trading!' if warnings else 'Normal trading conditions'
        }

    def analyze_round_numbers(self, current_price):
        """
        Analyze proximity to round numbers (PRO TRADER METHOD)
        Market makers place huge orders at round numbers
        """
        # Find nearest major round numbers (e.g., 1.1500, 1.1600)
        major_below = int(current_price * 100) / 100
        major_above = major_below + 0.01
        
        # Find nearest minor round numbers (e.g., 1.1550)
        minor_step = 0.005
        minor_below = int(current_price / minor_step) * minor_step
        minor_above = minor_below + minor_step
        
        # Calculate distances in pips
        distance_to_major_above = (major_above - current_price) * 10000
        distance_to_major_below = (current_price - major_below) * 10000
        
        score = 0.0
        warnings = []
        
        # Near major round number above (resistance)
        if distance_to_major_above < 15:  # Within 15 pips
            score -= 0.05  # Bearish (resistance)
            warnings.append(f"⚠️ NEAR MAJOR RESISTANCE: {major_above:.4f} ({distance_to_major_above:.0f} pips)")
        
        # Near major round number below (support)
        if distance_to_major_below < 15:  # Within 15 pips
            score += 0.05  # Bullish (support)
            warnings.append(f"⚠️ NEAR MAJOR SUPPORT: {major_below:.4f} ({distance_to_major_below:.0f} pips)")
        
        return {
            'score': score,
            'major_above': major_above,
            'major_below': major_below,
            'distance_to_major_above_pips': distance_to_major_above,
            'distance_to_major_below_pips': distance_to_major_below,
            'warnings': warnings
        }
    
    def get_session_strategy(self):
        """
        Get current forex session and trading strategy (PRO TRADER METHOD)
        London/NY overlap = BEST, Asian = AVOID
        Uses UTC for universal compatibility
        """
        from datetime import datetime
        import pytz
        
        # FIX: Use UTC as reference (works for all timezones!)
        utc_now = datetime.now(pytz.UTC)
        hour_utc = utc_now.hour
        
        # Display current time for verification
        print(f"\n⏰ Current Time: {utc_now.strftime('%Y-%m-%d %H:%M UTC')}")
        
        # Sessions in UTC (Standard for Forex):
        # Asian: 23:00-07:00 UTC (Tokyo + Sydney)
        # London: 07:00-16:00 UTC
        # NY: 13:00-22:00 UTC
        # Overlap: 13:00-16:00 UTC (London + NY = BEST!)
        
        if (hour_utc >= 23) or (hour_utc < 7):
            # Asian session (11 PM - 7 AM UTC)
            session_info = {
                'session': 'Asian',
                'volatility': 'Low',
                'advice': 'LOW LIQUIDITY - Avoid or use small positions',
                'confidence_multiplier': 0.70,  # Reduce confidence 30%
                'target_multiplier': 0.50,  # Half targets
                'trade_quality': 'Poor'
            }
        elif 7 <= hour_utc < 13:
            # London session (7 AM - 1 PM UTC)
            session_info = {
                'session': 'London',
                'volatility': 'High',
                'advice': 'High volume - Good trading conditions',
                'confidence_multiplier': 1.0,
                'target_multiplier': 1.0,
                'trade_quality': 'Good'
            }
        elif 13 <= hour_utc < 16:
            # London/NY Overlap (1 PM - 4 PM UTC) - BEST!
            session_info = {
                'session': 'Overlap',
                'volatility': 'Very High',
                'advice': 'BEST TIME - Highest liquidity & trends',
                'confidence_multiplier': 1.15,  # Boost 15%!
                'target_multiplier': 1.30,  # Bigger targets
                'trade_quality': 'Excellent'
            }
        elif 16 <= hour_utc < 22:
            # NY session (4 PM - 10 PM UTC)
            session_info = {
                'session': 'NY_Late',
                'volatility': 'Medium',
                'advice': 'Decent conditions, watch for reversals',
                'confidence_multiplier': 0.95,
                'target_multiplier': 0.90,
                'trade_quality': 'Fair'
            }
        else:
            # After hours (10 PM - 11 PM UTC)
            session_info = {
                'session': 'After_Hours',
                'volatility': 'Very Low',
                'advice': 'LOW LIQUIDITY - Avoid trading',
                'confidence_multiplier': 0.60,
                'target_multiplier': 0.40,
                'trade_quality': 'Poor'
            }
        
        print(f"📍 Forex Session: {session_info['session']} ({session_info['trade_quality']})")
        print(f"📊 Confidence Multiplier: {session_info['confidence_multiplier']:.2f}x")
        print(f"💡 Advice: {session_info['advice']}\n")
        
        return session_info
    
    def fetch_economic_calendar_fmp(self, days_ahead=7):
        """
        Fetch economic calendar from FMP API (LIVE DATA)
        Shows upcoming high-impact events
        """
        if not self.fmp_api_key:
            return None
        
        try:
            from_date = datetime.now().strftime('%Y-%m-%d')
            to_date = (datetime.now() + timedelta(days=days_ahead)).strftime('%Y-%m-%d')
            
            url = f"https://financialmodelingprep.com/api/v3/economic_calendar?from={from_date}&to={to_date}&apikey={self.fmp_api_key}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                events = response.json()
                
                # Filter high-impact events
                high_impact = [e for e in events if e.get('impact') == 'High']
                
                # Check for USD, EUR, GBP, JPY events
                major_events = []
                for event in high_impact:
                    currency = event.get('country', '')
                    if any(c in currency.upper() for c in ['US', 'EURO', 'UK', 'JAPAN']):
                        major_events.append({
                            'date': event.get('date'),
                            'event': event.get('event'),
                            'country': currency,
                            'impact': event.get('impact'),
                            'actual': event.get('actual'),
                            'forecast': event.get('estimate')
                        })
                
                return {
                    'total_events': len(events),
                    'high_impact_count': len(high_impact),
                    'major_events': major_events[:5],  # Top 5
                    'risk_level': 'HIGH' if len(major_events) > 2 else 'MEDIUM' if len(major_events) > 0 else 'LOW'
                }
        
        except Exception as e:
            print(f"⚠️ FMP Economic Calendar error: {e}")
            return None
    
    def fetch_forex_news_sentiment_fmp(self, pair='EURUSD'):
        """
        Fetch forex news sentiment from FMP API
        """
        if not self.fmp_api_key:
            return None
        
        try:
            # Convert pair format EUR/USD -> EURUSD
            ticker = pair.replace('/', '')
            
            url = f"https://financialmodelingprep.com/api/v3/stock_news?tickers={ticker}&limit=20&apikey={self.fmp_api_key}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                news = response.json()
                
                if news:
                    # Calculate sentiment score
                    bullish = sum(1 for n in news if 'bullish' in n.get('text', '').lower() or 'rally' in n.get('text', '').lower())
                    bearish = sum(1 for n in news if 'bearish' in n.get('text', '').lower() or 'sell' in n.get('text', '').lower())
                    
                    sentiment_score = (bullish - bearish) / len(news) if news else 0
                    
                    return {
                        'news_count': len(news),
                        'bullish_mentions': bullish,
                        'bearish_mentions': bearish,
                        'sentiment_score': sentiment_score,  # -1 to +1
                        'sentiment': 'bullish' if sentiment_score > 0.2 else 'bearish' if sentiment_score < -0.2 else 'neutral',
                        'recent_headlines': [n.get('title') for n in news[:3]]
                    }
        
        except Exception as e:
            print(f"⚠️ FMP News Sentiment error: {e}")
            return None
    
    def calculate_currency_strength(self):
        """
        Calculate currency strength index for USD, EUR, GBP, JPY
        Uses cross-pair analysis to determine which currency is strongest
        """
        try:
            pairs = {
                'EUR/USD': 'EURUSD=X',
                'GBP/USD': 'GBPUSD=X',
                'USD/JPY': 'USDJPY=X',
                'EUR/JPY': 'EURJPY=X',
                'GBP/JPY': 'GBPJPY=X',
                'EUR/GBP': 'EURGBP=X'
            }
            
            strengths = {'USD': 0, 'EUR': 0, 'GBP': 0, 'JPY': 0}
            
            for pair_name, ticker in pairs.items():
                try:
                    pair_data = yf.Ticker(ticker)
                    hist = pair_data.history(period='2d')  # FIXED: Changed from 5d to 2d for 1-day lookback
                    
                    if not hist.empty and len(hist) >= 2:
                        # FIXED: Use yesterday-to-today change instead of 5-day change
                        change = ((hist['Close'].iloc[-1] - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2]) * 100
                        
                        # Split pair (e.g., EUR/USD -> EUR and USD)
                        base = pair_name.split('/')[0]
                        quote = pair_name.split('/')[1]
                        
                        # Positive change = base currency stronger
                        strengths[base] += change
                        strengths[quote] -= change
                
                except:
                    continue
            
            # Normalize scores
            if strengths:
                # Sort by strength
                sorted_currencies = sorted(strengths.items(), key=lambda x: x[1], reverse=True)
                
                return {
                    'strengths': strengths,
                    'strongest': sorted_currencies[0][0],
                    'weakest': sorted_currencies[-1][0],
                    'rankings': [c[0] for c in sorted_currencies]
                }
        
        except Exception as e:
            print(f"⚠️ Currency Strength error: {e}")
            return None
    
    def fetch_news_sentiment_alpha_vantage(self, pair='EURUSD'):
        """
        Fetch news sentiment from Alpha Vantage API (YOU HAVE THIS KEY!)
        MORE RELIABLE than FMP for forex news
        """
        if not self.alpha_vantage_key:
            return None
        
        try:
            # Alpha Vantage news sentiment endpoint
            ticker = f"FOREX:{pair}"
            url = f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers={ticker}&apikey={self.alpha_vantage_key}"
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'feed' in data and data['feed']:
                    articles = data['feed'][:20]  # Last 20 articles
                    
                    # Calculate sentiment
                    total_sentiment = 0
                    count = 0
                    
                    for article in articles:
                        for ticker_sentiment in article.get('ticker_sentiment', []):
                            if ticker in ticker_sentiment.get('ticker', ''):
                                sentiment_score = float(ticker_sentiment.get('ticker_sentiment_score', 0))
                                total_sentiment += sentiment_score
                                count += 1
                    
                    avg_sentiment = total_sentiment / count if count > 0 else 0
                    
                    return {
                        'article_count': len(articles),
                        'sentiment_score': avg_sentiment,  # -1 to +1
                        'sentiment': 'bullish' if avg_sentiment > 0.15 else 'bearish' if avg_sentiment < -0.15 else 'neutral',
                        'confidence': abs(avg_sentiment),
                        'headlines': [a.get('title', '') for a in articles[:3]],
                        'source': 'Alpha Vantage'
                    }
        
        except Exception as e:
            print(f"⚠️ Alpha Vantage News error: {e}")
            return None
    
    def detect_london_momentum(self):
        """
        Detect strong momentum at London open (CRITICAL for 6:30 AM entries!)
        Analyzes Asian session setup for London breakout potential
        """
        try:
            # Check major pairs for momentum alignment
            pairs = ['EURUSD=X', 'GBPUSD=X', 'USDJPY=X']
            
            momentum_scores = []
            
            for ticker in pairs:
                try:
                    data = yf.Ticker(ticker)
                    hist = data.history(period='2d', interval='1h')
                    
                    if not hist.empty and len(hist) >= 8:
                        # Last 8 hours (Asian session)
                        recent = hist.tail(8)
                        
                        # Calculate momentum
                        price_change = ((recent['Close'].iloc[-1] - recent['Close'].iloc[0]) / 
                                       recent['Close'].iloc[0]) * 100
                        
                        # Volume trend
                        vol_recent = recent['Volume'].tail(4).mean()
                        vol_older = recent['Volume'].head(4).mean()
                        vol_increasing = vol_recent > vol_older * 1.2
                        
                        momentum_scores.append({
                            'pair': ticker,
                            'momentum': price_change,
                            'volume_trend': 'increasing' if vol_increasing else 'flat'
                        })
                
                except:
                    continue
            
            if momentum_scores:
                # Check if USD is strong/weak across all pairs
                usd_strength = sum(m['momentum'] for m in momentum_scores) / len(momentum_scores)
                
                return {
                    'usd_momentum': usd_strength,
                    'trend': 'usd_strong' if usd_strength > 0.15 else 'usd_weak' if usd_strength < -0.15 else 'neutral',
                    'london_setup': 'bullish' if usd_strength < -0.2 else 'bearish' if usd_strength > 0.2 else 'range',
                    'pairs_analyzed': len(momentum_scores)
                }
        
        except Exception as e:
            print(f"⚠️ London Momentum error: {e}")
            return None
    
    def analyze_volume_profile(self, pair_symbol):
        """
        Analyze volume profile for institutional activity
        High volume = big money positioning
        """
        try:
            data = yf.Ticker(pair_symbol)
            hist = data.history(period='5d', interval='1h')
            
            if hist.empty or len(hist) < 20:
                return None
            
            # Calculate average volume
            avg_volume = hist['Volume'].mean()
            recent_volume = hist['Volume'].tail(8).mean()  # Last 8 hours
            
            # Volume spike detection
            volume_ratio = recent_volume / avg_volume if avg_volume > 0 else 1
            
            # Price-volume correlation
            price_change = ((hist['Close'].iloc[-1] - hist['Close'].iloc[-8]) / 
                          hist['Close'].iloc[-8]) * 100
            
            # Strong volume + strong move = institutional activity
            if volume_ratio > 1.5 and abs(price_change) > 0.3:
                signal = 'bullish' if price_change > 0 else 'bearish'
                strength = 'strong'
            elif volume_ratio > 1.2:
                signal = 'building' 
                strength = 'moderate'
            else:
                signal = 'neutral'
                strength = 'weak'
            
            return {
                'volume_ratio': volume_ratio,
                'recent_volume': recent_volume,
                'avg_volume': avg_volume,
                'signal': signal,
                'strength': strength,
                'price_change': price_change
            }
        
        except Exception as e:
            print(f"⚠️ Volume Profile error: {e}")
            return None
    
    def calculate_trend_strength(self, pair_symbol):
        """
        Calculate trend strength using ADX-like logic
        Strong trend = high confidence, weak trend = skip
        """
        try:
            data = yf.Ticker(pair_symbol)
            hist = data.history(period='30d')
            
            if hist.empty or len(hist) < 20:
                return None
            
            close = hist['Close']
            high = hist['High']
            low = hist['Low']
            
            # Calculate directional movement
            up_move = high.diff()
            down_move = -low.diff()
            
            # Positive and negative directional indicators
            plus_dm = up_move.where((up_move > down_move) & (up_move > 0), 0)
            minus_dm = down_move.where((down_move > up_move) & (down_move > 0), 0)
            
            # Smooth with 14-period moving average
            plus_di = plus_dm.rolling(14).mean()
            minus_di = minus_dm.rolling(14).mean()
            
            # Calculate trend strength (simplified ADX)
            current_plus = float(plus_di.iloc[-1]) if not plus_di.empty else 0
            current_minus = float(minus_di.iloc[-1]) if not minus_di.empty else 0
            
            trend_strength = abs(current_plus - current_minus)
            
            # Determine trend direction and strength
            if current_plus > current_minus * 1.5:
                direction = 'uptrend'
                strength_level = 'strong' if trend_strength > 0.5 else 'moderate'
            elif current_minus > current_plus * 1.5:
                direction = 'downtrend'
                strength_level = 'strong' if trend_strength > 0.5 else 'moderate'
            else:
                direction = 'ranging'
                strength_level = 'weak'
            
            return {
                'trend_direction': direction,
                'trend_strength': trend_strength,
                'strength_level': strength_level,
                'plus_di': current_plus,
                'minus_di': current_minus,
                'tradeable': strength_level in ['strong', 'moderate']
            }
        
        except Exception as e:
            print(f"⚠️ Trend Strength error: {e}")
            return None
    
    def multi_timeframe_confirmation(self, pair_symbol):
        """
        Check if trend is aligned across multiple timeframes
        1H + 4H + Daily alignment = HIGH CONFIDENCE!
        """
        try:
            data = yf.Ticker(pair_symbol)
            
            timeframes = {
                '1h': data.history(period='5d', interval='1h'),
                '4h': data.history(period='30d', interval='1d'),  # Approximate 4h
                'daily': data.history(period='90d', interval='1d')
            }
            
            trends = {}
            
            for tf, hist in timeframes.items():
                if not hist.empty and len(hist) >= 20:
                    # Simple trend: price vs 20-period MA
                    ma_20 = hist['Close'].rolling(20).mean()
                    current_price = hist['Close'].iloc[-1]
                    ma_value = ma_20.iloc[-1]
                    
                    if current_price > ma_value * 1.002:  # 0.2% above
                        trends[tf] = 'bullish'
                    elif current_price < ma_value * 0.998:  # 0.2% below
                        trends[tf] = 'bearish'
                    else:
                        trends[tf] = 'neutral'
            
            # Check alignment
            if len(trends) >= 2:
                bullish_count = sum(1 for t in trends.values() if t == 'bullish')
                bearish_count = sum(1 for t in trends.values() if t == 'bearish')
                
                if bullish_count >= 2:
                    alignment = 'bullish'
                    confidence = bullish_count / len(trends)
                elif bearish_count >= 2:
                    alignment = 'bearish'
                    confidence = bearish_count / len(trends)
                else:
                    alignment = 'mixed'
                    confidence = 0.5
                
                return {
                    'alignment': alignment,
                    'confidence': confidence,
                    'timeframes': trends,
                    'strength': 'strong' if confidence >= 0.66 else 'moderate' if confidence >= 0.5 else 'weak'
                }
        
        except Exception as e:
            print(f"⚠️ Multi-timeframe error: {e}")
            return None
    
    def fetch_cot_report(self, currency='EUR'):
        """
        Fetch COT (Commitment of Traders) report data
        Shows institutional positioning (bullish/bearish)
        """
        try:
            # COT reports are published weekly by CFTC
            # This is a simplified version - full implementation would parse CFTC data
            
            # For now, return indicator that this would be valuable
            return {
                'available': False,
                'note': 'COT reports show institutional positioning - implement if needed',
                'importance': 'HIGH',
                'frequency': 'Weekly (Fridays)'
            }
        
        except Exception as e:
            return None
    
    def analyze_carry_trade(self, pair, rates):
        """
        Analyze carry trade bias (PRO TRADER METHOD)
        Hedge funds borrow low rate, invest high rate
        Creates persistent multi-week/month trends
        """
        # Parse pair to get currencies
        if pair == 'EUR/USD':
            base_rate = rates.get('EUR', 4.0)
            quote_rate = rates.get('USD', 5.5)
            base = 'EUR'
            quote = 'USD'
        elif pair == 'GBP/USD':
            base_rate = rates.get('GBP', 5.0)
            quote_rate = rates.get('USD', 5.5)
            base = 'GBP'
            quote = 'USD'
        elif pair == 'USD/JPY':
            base_rate = rates.get('USD', 5.5)
            quote_rate = rates.get('JPY', 0.1)
            base = 'USD'
            quote = 'JPY'
        else:
            return {'score': 0, 'explanation': 'Pair not configured for carry'}
        
        # Calculate carry differential
        carry_differential = base_rate - quote_rate
        
        score = 0.0
        explanation = f"Carry Trade Analysis:\n"
        explanation += f"   {base}: {base_rate}% vs {quote}: {quote_rate}%\n"
        explanation += f"   Differential: {carry_differential:+.2f}%\n"
        
        # Significant carry bias
        if abs(carry_differential) > 2.0:
            # Strong carry differential
            if carry_differential > 2.0:
                score = 0.03  # Bullish for pair
                explanation += f"   → STRONG CARRY BIAS: Favors holding {base} (BUY {pair})\n"
                explanation += f"   → Hedge funds earn {carry_differential:.1f}% holding this position"
            else:
                score = -0.03  # Bearish for pair
                explanation += f"   → STRONG CARRY BIAS: Favors holding {quote} (SELL {pair})\n"
                explanation += f"   → Hedge funds earn {abs(carry_differential):.1f}% shorting this position"
        elif abs(carry_differential) > 1.0:
            # Moderate carry
            score = 0.015 if carry_differential > 0 else -0.015
            explanation += f"   → Moderate carry bias\n"
        else:
            explanation += f"   → Neutral (minimal carry effect)"
        
        return {
            'score': score,
            'carry_differential': carry_differential,
            'explanation': explanation,
            'timeframe': 'Multi-week to months'
        }

# Test the fetcher
if __name__ == "__main__":
    print("\n" + "="*80)
    print("🌍 FOREX DATA FETCHER - TEST")
    print("="*80)
    
    fetcher = ForexDataFetcher()
    
    # Test interest rates
    print("\n1. INTEREST RATES:")
    rates = fetcher.fetch_interest_rates()
    
    # Test Gold
    print("\n2. GOLD CORRELATION:")
    gold = fetcher.fetch_gold_price()
    if gold:
        print(f"   Price: ${gold['price']:.2f}")
        print(f"   Change: {gold['change_pct']:+.2f}%")
        print(f"   Trend: {gold['trend']}")
    
    # Test Oil
    print("\n3. OIL CORRELATION:")
    oil = fetcher.fetch_oil_price()
    if oil:
        print(f"   Price: ${oil['price']:.2f}")
        print(f"   Change: {oil['change_pct']:+.2f}%")
        print(f"   Trend: {oil['trend']}")
    
    # Test 10Y Yield
    print("\n4. 10Y TREASURY YIELD:")
    yield_data = fetcher.fetch_10y_yield()
    if yield_data:
        print(f"   Yield: {yield_data['yield']:.2f}%")
        print(f"   Change: {yield_data['change']:+.2f}")
        print(f"   USD Impact: {yield_data['usd_impact']}")
    
    # Test Economic Calendar
    print("\n5. ECONOMIC CALENDAR CHECK:")
    calendar = fetcher.check_economic_calendar_today()
    print(f"   Risk Level: {calendar['risk_level']}")
    if calendar['warnings']:
        for warning in calendar['warnings']:
            print(f"   {warning}")
    print(f"   {calendar['recommendation']}")
    
    # Test Support/Resistance
    print("\n6. SUPPORT/RESISTANCE (EUR/USD):")
    try:
        eurusd = yf.Ticker('EURUSD=X')
        hist = eurusd.history(period='30d')
        sr = fetcher.calculate_support_resistance(hist)
        if sr:
            print(f"   Current: {sr['current_price']:.4f}")
            print(f"   Resistance: {sr['resistance']:.4f} ({sr['distance_to_resistance_pct']:+.2f}%)")
            print(f"   Support: {sr['support']:.4f} ({sr['distance_to_support_pct']:+.2f}%)")
            if sr['near_resistance']:
                print(f"   ⚠️ NEAR RESISTANCE - Reversal risk!")
            if sr['near_support']:
                print(f"   ⚠️ NEAR SUPPORT - Bounce potential!")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test Pivot Points
    print("\n7. PIVOT POINTS (EUR/USD):")
    try:
        pivots = fetcher.calculate_pivot_points(hist)
        if pivots:
            print(f"   Pivot: {pivots['pivot']:.4f}")
            print(f"   R1: {pivots['r1']:.4f}")
            print(f"   S1: {pivots['s1']:.4f}")
            print(f"   Bias: {pivots['bias']}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n" + "="*80)
    print("✅ Data fetcher test complete!")
    print("="*80 + "\n")
