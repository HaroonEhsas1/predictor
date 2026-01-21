#!/usr/bin/env python3
"""
Forex Daily Swing Predictor
Similar to comprehensive_nextday_predictor.py but for forex pairs
Predicts 24-48 hour moves (not scalping!)

Author: AI Trading System
Date: October 21, 2025
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from forex_config import get_forex_config
from forex_data_fetcher import ForexDataFetcher

class ForexDailyPredictor:
    """
    Forex Daily Swing Prediction System
    Predicts 24-48 hour moves based on:
    - Interest rate differentials (20%)
    - Technical indicators (15%)
    - DXY (Dollar Index) (10%)
    - Risk sentiment (VIX, S&P) (10%)
    - Economic calendar (15%)
    - Central bank sentiment (10%)
    - COT positioning (8%)
    - Correlations (7%)
    - Session timing (5%)
    """
    
    def __init__(self, pair='EUR/USD'):
        self.pair = pair
        self.config = get_forex_config(pair)
        self.weights = self.config['weights']
        self.symbol = self.config['symbol']
        self.data_fetcher = ForexDataFetcher()  # Initialize data fetcher
        
        print(f"\n{'='*80}")
        print(f"🌍 Forex Daily Swing Predictor: {pair}")
        print(f"{'='*80}\n")
    
    def fetch_forex_data(self):
        """Fetch forex price data"""
        try:
            ticker = yf.Ticker(self.symbol)
            hist = ticker.history(period='90d')
            
            if hist.empty:
                print(f"⚠️ No data for {self.symbol}")
                return None
            
            return hist
        except Exception as e:
            print(f"⚠️ Error fetching {self.symbol}: {e}")
            return None
    
    def calculate_technical_indicators(self, hist):
        """Calculate technical indicators (similar to stock system)"""
        
        close = hist['Close']
        
        # RSI (14-period)
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        current_rsi = float(rsi.iloc[-1]) if not rsi.empty else 50
        
        # MACD
        ema_12 = close.ewm(span=12).mean()
        ema_26 = close.ewm(span=26).mean()
        macd = ema_12 - ema_26
        signal = macd.ewm(span=9).mean()
        macd_value = float(macd.iloc[-1] - signal.iloc[-1]) if len(macd) > 0 else 0
        
        # Moving Averages
        ma_50 = close.rolling(50).mean()
        ma_200 = close.rolling(200).mean() if len(close) >= 200 else ma_50
        
        current_price = float(close.iloc[-1])
        ma_50_val = float(ma_50.iloc[-1]) if not ma_50.empty else current_price
        ma_200_val = float(ma_200.iloc[-1]) if not ma_200.empty else current_price
        
        # Trend determination
        if current_price > ma_50_val > ma_200_val:
            trend = 'UPTREND'
        elif current_price < ma_50_val < ma_200_val:
            trend = 'DOWNTREND'
        else:
            trend = 'SIDEWAYS'
        
        return {
            'rsi': current_rsi,
            'macd': macd_value,
            'ma_50': ma_50_val,
            'ma_200': ma_200_val,
            'current_price': current_price,
            'trend': trend
        }
    
    def analyze_interest_rates(self):
        """Analyze interest rate differential"""
        
        # Fetch LIVE interest rates
        live_rates = self.data_fetcher.fetch_interest_rates()
        
        # Parse pair to get currencies
        if self.pair == 'EUR/USD':
            base = 'EUR'
            quote = 'USD'
        elif self.pair == 'GBP/USD':
            base = 'GBP'
            quote = 'USD'
        elif self.pair == 'USD/JPY':
            base = 'USD'
            quote = 'JPY'
        else:
            return 0.0, "Unknown pair"
        
        base_rate = live_rates.get(base, 0)
        quote_rate = live_rates.get(quote, 0)
        
        differential = base_rate - quote_rate
        
        # Higher differential = stronger base currency
        # FIX #3: Increase to 0.05 per 1% differential (more sensitive, interest rates are #1 in forex)
        # -1.5% differential → -0.075 score (significant bearish signal)
        score = min(max(differential * 0.05, -0.15), 0.15)
        
        explanation = f"{base} rate: {base_rate}%, {quote} rate: {quote_rate}%"
        explanation += f"\nDifferential: {differential:+.2f}% → "
        
        if differential > 1:
            explanation += f"Favors {base} (buy {self.pair})"
        elif differential < -1:
            explanation += f"Favors {quote} (sell {self.pair})"
        else:
            explanation += "Neutral"
        
        return score, explanation
    
    def analyze_dxy(self):
        """Analyze Dollar Index (DXY)"""
        try:
            dxy = yf.Ticker('DX-Y.NYB')
            dxy_hist = dxy.history(period='10d')
            
            if dxy_hist.empty:
                return 0.0, "DXY data unavailable"
            
            current_dxy = float(dxy_hist['Close'].iloc[-1])
            prev_dxy = float(dxy_hist['Close'].iloc[-5])
            
            dxy_change_pct = ((current_dxy - prev_dxy) / prev_dxy) * 100
            
            # For USD pairs: DXY up = USD strong
            if 'USD' in self.pair:
                if self.pair.startswith('USD'):
                    # USD/JPY: DXY up = pair up
                    score = dxy_change_pct * 0.02  # 0.02 per 1% DXY move
                else:
                    # EUR/USD, GBP/USD: DXY up = pair down
                    score = -dxy_change_pct * 0.02
            else:
                score = 0.0
            
            explanation = f"DXY: {current_dxy:.2f} ({dxy_change_pct:+.2f}% 5-day)"
            
            return score, explanation
        
        except Exception as e:
            return 0.0, f"DXY error: {e}"
    
    def analyze_risk_sentiment(self):
        """Analyze risk-on/risk-off (VIX, S&P 500)"""
        score = 0.0
        explanation = []
        
        # VIX (Fear gauge)
        try:
            vix = yf.Ticker('^VIX')
            vix_hist = vix.history(period='5d')
            
            if not vix_hist.empty:
                current_vix = float(vix_hist['Close'].iloc[-1])
                prev_vix = float(vix_hist['Close'].iloc[0]) if len(vix_hist) > 1 else current_vix
                vix_change = current_vix - prev_vix
                
                explanation.append(f"VIX: {current_vix:.2f}")
                
                # FIX: Use VIX CHANGE (fear trend), not just level
                if vix_change > 2:
                    risk_score = -0.05  # Fear spiking = risk-off
                    explanation.append(f"(+{vix_change:.1f} = Fear rising = Risk-OFF)")
                elif vix_change > 1:
                    risk_score = -0.03
                    explanation.append(f"(+{vix_change:.1f} = Fear increasing)")
                elif vix_change < -2:
                    risk_score = 0.05  # Fear collapsing = risk-on
                    explanation.append(f"({vix_change:.1f} = Fear falling = Risk-ON)")
                elif vix_change < -1:
                    risk_score = 0.03
                    explanation.append(f"({vix_change:.1f} = Fear decreasing)")
                else:
                    # Fallback to static level if no big change
                    if current_vix < 15:
                        risk_score = 0.03
                        explanation.append("(Low fear = Risk-ON)")
                    elif current_vix > 25:
                        risk_score = -0.03
                        explanation.append("(High fear = Risk-OFF)")
                    else:
                        risk_score = 0.0
                        explanation.append("(Normal)")
                
                # Apply to pairs
                if self.pair == 'USD/JPY':
                    # JPY is safe haven: risk-on = USD/JPY up
                    score += risk_score
                elif self.pair in ['EUR/USD', 'GBP/USD']:
                    # Risk-on = favor EUR/GBP over USD
                    score += risk_score * 0.5
        
        except Exception as e:
            explanation.append(f"VIX error: {e}")
        
        # FORWARD-LOOKING: ES Futures (what market expects)
        try:
            es_data = self.data_fetcher.fetch_es_futures()
            
            if es_data:
                es_change = es_data['change_pct']
                es_sentiment = es_data['sentiment']
                
                explanation.append(f"ES Futures: {es_change:+.2f}% (forward-looking)")
                
                # ES futures = PREDICTIVE (what market expects)
                if es_sentiment == 'risk_on':
                    explanation.append("(Futures up = Risk-ON expected)")
                    if self.pair == 'USD/JPY':
                        score += 0.04  # Stronger signal (futures are predictive)
                    elif self.pair in ['EUR/USD', 'GBP/USD']:
                        score += 0.03  # Risk-on favors EUR/GBP
                elif es_sentiment == 'risk_off':
                    explanation.append("(Futures down = Risk-OFF expected)")
                    if self.pair == 'USD/JPY':
                        score -= 0.04  # Flight to safety
                    elif self.pair in ['EUR/USD', 'GBP/USD']:
                        score -= 0.03  # Risk-off favors USD
            else:
                # Fallback to past S&P data if futures unavailable
                spx = yf.Ticker('^GSPC')
                spx_hist = spx.history(period='5d')
                
                if not spx_hist.empty:
                    spx_change = ((spx_hist['Close'].iloc[-1] - spx_hist['Close'].iloc[0]) / 
                                 spx_hist['Close'].iloc[0]) * 100
                    
                    explanation.append(f"S&P 500: {spx_change:+.2f}% (5-day, backward-looking)")
                    
                    # S&P past performance (weaker signal than futures)
                    if spx_change > 1:
                        explanation.append("(Stocks up = Risk-ON)")
                        if self.pair == 'USD/JPY':
                            score += 0.02  # Weaker than futures
                        elif self.pair in ['EUR/USD', 'GBP/USD']:
                            score += 0.015
                    elif spx_change < -1:
                        explanation.append("(Stocks down = Risk-OFF)")
                        if self.pair == 'USD/JPY':
                            score -= 0.02
                        elif self.pair in ['EUR/USD', 'GBP/USD']:
                            score -= 0.015
        
        except Exception as e:
            explanation.append(f"Risk sentiment error: {e}")
        
        return score, "\n".join(explanation)
    
    def analyze_technical(self, technical_data):
        """Analyze technical indicators"""
        
        rsi = technical_data['rsi']
        macd = technical_data['macd']
        trend = technical_data['trend']
        current_price = technical_data['current_price']
        ma_50 = technical_data['ma_50']
        
        score = 0.0
        explanation = []
        
        # RSI Analysis (similar to stock system FIX #1)
        explanation.append(f"RSI: {rsi:.1f}")
        if rsi > 70:
            score -= 0.08
            explanation.append("→ Overbought (bearish)")
        elif rsi > 60:
            score -= 0.03
            explanation.append("→ Slightly overbought")
        elif rsi < 30:
            score += 0.08
            explanation.append("→ Oversold (bullish)")
        elif rsi < 40:
            # FIX: Increase from +0.03 to +0.05 (RSI <40 is meaningfully oversold)
            score += 0.05
            explanation.append("→ Oversold (bounce potential)")
        else:
            explanation.append("→ Neutral")
        
        # MACD
        explanation.append(f"\nMACD: {macd:+.5f}")
        if macd > 0:
            score += 0.04
            explanation.append("→ Bullish momentum")
        else:
            score -= 0.04
            explanation.append("→ Bearish momentum")
        
        # Trend
        explanation.append(f"\nTrend: {trend}")
        if trend == 'UPTREND':
            score += 0.05
            explanation.append("→ Bullish")
        elif trend == 'DOWNTREND':
            score -= 0.05
            explanation.append("→ Bearish")
        
        # Price vs MA
        ma_distance = ((current_price - ma_50) / ma_50) * 100
        explanation.append(f"\nPrice vs 50-MA: {ma_distance:+.2f}%")
        
        if abs(ma_distance) > 2:
            # Mean reversion bias (FIX #2 from stocks)
            if ma_distance > 0:
                score -= 0.03  # Far above MA = potential pullback
                explanation.append("→ Extended above MA (reversal risk)")
            else:
                score += 0.03  # Far below MA = potential bounce
                explanation.append("→ Extended below MA (bounce potential)")
        
        return score, "\n".join(explanation)
    
    def analyze_gold_correlation(self):
        """Analyze Gold correlation with MOMENTUM EXHAUSTION detection"""
        
        gold_data = self.data_fetcher.fetch_gold_price()
        
        if not gold_data:
            return 0.0, "Gold data unavailable"
        
        gold_change = gold_data['change_pct']
        gold_trend = gold_data['trend']
        gold_rsi = gold_data.get('rsi', 50)
        exhaustion_risk = gold_data.get('exhaustion_risk', False)
        reversal_signal = gold_data.get('reversal_signal', False)
        
        score = 0.0
        explanation = f"Gold: ${gold_data['price']:.2f} ({gold_change:+.2f}%)\n"
        explanation += f"RSI: {gold_rsi:.1f}, Trend: {gold_trend}"
        
        # MOMENTUM EXHAUSTION LOGIC (Contrarian)
        if exhaustion_risk:
            # Gold rallied hard + overbought = REVERSAL RISK (bearish for Gold = bullish for USD)
            if self.pair in ['EUR/USD', 'GBP/USD']:
                score = -0.05  # Contrarian: Gold exhausted = pair weakness
                explanation += f"\n→ ⚠️ EXHAUSTION RISK: Gold overbought ({gold_rsi:.0f} RSI) after +{gold_change:.1f}% rally"
                explanation += "\n→ Contrarian signal: Reversal expected (bearish for EUR/USD)"
            elif self.pair == 'USD/JPY':
                score = 0.05  # Gold weakness = USD strength
                explanation += f"\n→ ⚠️ EXHAUSTION RISK: Gold overbought, USD may strengthen"
        
        elif reversal_signal:
            # Gold oversold after selloff = BOUNCE POTENTIAL (bullish for Gold = bearish for USD)
            if self.pair in ['EUR/USD', 'GBP/USD']:
                score = 0.05  # Gold bounce = pair strength
                explanation += f"\n→ ✅ BOUNCE POTENTIAL: Gold oversold ({gold_rsi:.0f} RSI) after {gold_change:.1f}% drop"
                explanation += "\n→ Reversal signal: Bounce expected (bullish for EUR/USD)"
            elif self.pair == 'USD/JPY':
                score = -0.05  # Gold bounce = USD weakness
                explanation += f"\n→ ✅ BOUNCE POTENTIAL: Gold oversold, USD may weaken"
        
        else:
            # Normal correlation (trend-following)
            if self.pair in ['EUR/USD', 'GBP/USD']:
                # Positive correlation: Gold up = pair up
                correlation_factor = 0.70
                score = (gold_change / 100) * correlation_factor * 0.10
                explanation += "\n→ Positive correlation (Gold up = pair up)"
            elif self.pair == 'USD/JPY':
                # Negative correlation: Gold up = pair down
                correlation_factor = -0.60
                score = (gold_change / 100) * correlation_factor * 0.10
                explanation += "\n→ Negative correlation (Gold up = pair down)"
        
        return score, explanation
    
    def analyze_10y_yield(self):
        """Analyze 10Y Treasury Yield impact"""
        
        yield_data = self.data_fetcher.fetch_10y_yield()
        
        if not yield_data:
            return 0.0, "10Y yield unavailable"
        
        yield_change = yield_data['change']
        usd_impact = yield_data['usd_impact']
        
        score = 0.0
        explanation = f"10Y Yield: {yield_data['yield']:.2f}% ({yield_change:+.2f})\n"
        explanation += f"Trend: {yield_data['trend']}\n"
        explanation += f"USD Impact: {usd_impact}"
        
        # Rising yields = USD strength
        if self.pair.endswith('USD'):
            # EUR/USD, GBP/USD: Rising yields = pair down
            score = -yield_change * 0.02
        elif self.pair.startswith('USD'):
            # USD/JPY: Rising yields = pair up
            score = yield_change * 0.02
        
        return score, explanation
    
    def analyze_support_resistance(self, hist):
        """Analyze support/resistance levels"""
        
        sr_data = self.data_fetcher.calculate_support_resistance(hist)
        
        if not sr_data:
            return 0.0, "S/R unavailable"
        
        score = 0.0
        explanation = f"Current: {sr_data['current_price']:.4f}\n"
        explanation += f"Resistance: {sr_data['resistance']:.4f} ({sr_data['distance_to_resistance_pct']:+.2f}%)\n"
        explanation += f"Support: {sr_data['support']:.4f} ({sr_data['distance_to_support_pct']:+.2f}%)"
        
        # Near resistance = bearish bias
        if sr_data['near_resistance']:
            score -= 0.05
            explanation += "\n⚠️ NEAR RESISTANCE - Reversal risk"
        
        # Near support = bullish bias
        if sr_data['near_support']:
            score += 0.05
            explanation += "\n⚠️ NEAR SUPPORT - Bounce potential"
        
        return score, explanation, sr_data
    
    def analyze_pivot_points(self, hist):
        """Analyze pivot points"""
        
        pivot_data = self.data_fetcher.calculate_pivot_points(hist)
        
        if not pivot_data:
            return 0.0, "Pivots unavailable"
        
        score = 0.0
        explanation = f"Pivot: {pivot_data['pivot']:.4f}\n"
        explanation += f"R1: {pivot_data['r1']:.4f} | S1: {pivot_data['s1']:.4f}\n"
        explanation += f"Bias: {pivot_data['bias']}"
        
        # Apply pivot bias
        if pivot_data['bias'] == 'bullish':
            score += 0.03
        elif pivot_data['bias'] == 'bearish':
            score -= 0.03
        
        return score, explanation
    
    def generate_prediction(self):
        """Generate complete forex prediction"""
        
        # Fetch data
        hist = self.fetch_forex_data()
        if hist is None:
            return None
        
        print(f"📊 Analyzing {self.pair}...")
        
        # Calculate technical indicators
        technical_data = self.calculate_technical_indicators(hist)
        
        print(f"\n{'='*80}")
        print(f"📈 ANALYSIS BREAKDOWN")
        print(f"{'='*80}\n")
        
        # Analyze each component
        scores = {}
        
        # FIX #1: Amplify and weight all components consistently (multiply by 10 for signal strength)
        
        # 1. Interest Rates (20%) - MOST IMPORTANT
        rate_score, rate_exp = self.analyze_interest_rates()
        # Amplify by 10, then apply weight
        scores['interest_rates'] = rate_score * 10 * self.weights['interest_rates']
        print(f"💰 Interest Rates ({self.weights['interest_rates']*100:.0f}% weight):")
        print(f"   {rate_exp}")
        print(f"   Base Score: {rate_score:+.3f} → Amplified: {rate_score*10:+.3f} → Weighted: {scores['interest_rates']:+.3f}\n")
        
        # 2. Technical (18%) - INCREASED for real-time responsiveness
        tech_score, tech_exp = self.analyze_technical(technical_data)
        scores['technical'] = tech_score * 10 * 0.18  # Use 18% instead of config
        print(f"📊 Technical Analysis (18% weight):")
        print(f"   {tech_exp}")
        print(f"   Base Score: {tech_score:+.3f} → Amplified: {tech_score*10:+.3f} → Weighted: {scores['technical']:+.3f}\n")
        
        # 3. DXY (12%) - INCREASED for real-time responsiveness
        dxy_score, dxy_exp = self.analyze_dxy()
        scores['dxy'] = dxy_score * 10 * 0.12  # Use 12% instead of config
        print(f"💵 Dollar Index (12% weight):")
        print(f"   {dxy_exp}")
        print(f"   Base Score: {dxy_score:+.3f} → Amplified: {dxy_score*10:+.3f} → Weighted: {scores['dxy']:+.3f}\n")
        
        # 4. Risk Sentiment (12%) - INCREASED for forward-looking signals
        risk_score, risk_exp = self.analyze_risk_sentiment()
        scores['risk_sentiment'] = risk_score * 10 * 0.12  # Use 12% instead of config
        print(f"📉 Risk Sentiment (12% weight):")
        print(f"   {risk_exp}")
        print(f"   Base Score: {risk_score:+.3f} → Amplified: {risk_score*10:+.3f} → Weighted: {scores['risk_sentiment']:+.3f}\n")
        
        # 5. Gold Correlation (7% correlations weight)
        gold_score, gold_exp = self.analyze_gold_correlation()
        # FIX: Apply correlations weight (0.07)
        scores['gold'] = gold_score * 10 * self.weights['correlations']
        print(f"🪙 Gold Correlation ({self.weights['correlations']*100:.0f}% weight):")
        print(f"   {gold_exp}")
        print(f"   Base Score: {gold_score:+.3f} → Amplified: {gold_score*10:+.3f} → Weighted: {scores['gold']:+.3f}\n")
        
        # 6. 10Y Treasury Yield (part of correlations)
        yield_score, yield_exp = self.analyze_10y_yield()
        # FIX: Apply correlations weight
        scores['10y_yield'] = yield_score * 10 * self.weights['correlations']
        print(f"📈 10Y Yield Impact ({self.weights['correlations']*100:.0f}% weight):")
        print(f"   {yield_exp}")
        print(f"   Base Score: {yield_score:+.3f} → Amplified: {yield_score*10:+.3f} → Weighted: {scores['10y_yield']:+.3f}\n")
        
        # 7. Support/Resistance (enhances technical - 5% additional)
        sr_score, sr_exp, sr_data = self.analyze_support_resistance(hist)
        scores['support_resistance'] = sr_score * 10 * 0.05
        print(f"📊 Support/Resistance Levels (5% weight):")
        print(f"   {sr_exp}")
        print(f"   Base Score: {sr_score:+.3f} → Amplified: {sr_score*10:+.3f} → Weighted: {scores['support_resistance']:+.3f}\n")
        
        # 8. Pivot Points (enhances technical - 5% additional)
        pivot_score, pivot_exp = self.analyze_pivot_points(hist)
        scores['pivots'] = pivot_score * 10 * 0.05
        print(f"🎯 Pivot Points (5% weight):")
        print(f"   {pivot_exp}")
        print(f"   Base Score: {pivot_score:+.3f} → Amplified: {pivot_score*10:+.3f} → Weighted: {scores['pivots']:+.3f}\n")
        
        # 9. Economic Calendar Warning
        calendar = self.data_fetcher.check_economic_calendar_today()
        print(f"📅 Economic Calendar Check:")
        print(f"   Risk Level: {calendar['risk_level'].upper()}")
        if calendar['warnings']:
            for warning in calendar['warnings']:
                print(f"   {warning}")
        print(f"   {calendar['recommendation']}\n")
        
        # 10. PRO: Round Number Psychology (3% weight)
        current_price = technical_data['current_price']
        round_analysis = self.data_fetcher.analyze_round_numbers(current_price)
        # FIX: Apply weight to round numbers
        scores['round_numbers'] = round_analysis['score'] * 10 * 0.03
        print(f"🎯 PRO: Round Number Analysis (3% weight):")
        print(f"   Major Above: {round_analysis['major_above']:.4f} ({round_analysis['distance_to_major_above_pips']:.0f} pips)")
        print(f"   Major Below: {round_analysis['major_below']:.4f} ({round_analysis['distance_to_major_below_pips']:.0f} pips)")
        if round_analysis['warnings']:
            for warning in round_analysis['warnings']:
                print(f"   {warning}")
        print(f"   Base Score: {round_analysis['score']:+.3f} → Amplified: {round_analysis['score']*10:+.3f} → Weighted: {scores['round_numbers']:+.3f}\n")
        
        # 11. PRO: Session Strategy
        session_info = self.data_fetcher.get_session_strategy()
        print(f"⏰ PRO: Session Analysis:")
        print(f"   Current Session: {session_info['session']}")
        print(f"   Volatility: {session_info['volatility']}")
        print(f"   Quality: {session_info['trade_quality']}")
        print(f"   {session_info['advice']}\n")
        
        # 12. PRO: Carry Trade Analysis (included in interest rates component)
        live_rates = self.data_fetcher.fetch_interest_rates()
        carry_analysis = self.data_fetcher.analyze_carry_trade(self.pair, live_rates)
        # FIX: Apply weight (2% additional to interest rates)
        scores['carry_trade'] = carry_analysis['score'] * 10 * 0.02
        print(f"💰 PRO: Carry Trade Bias (2% weight):")
        print(f"   {carry_analysis['explanation']}")
        print(f"   Base Score: {carry_analysis['score']:+.3f} → Amplified: {carry_analysis['score']*10:+.3f} → Weighted: {scores['carry_trade']:+.3f}\n")
        
        # 13. NEW: Economic Calendar (FMP API) - 5% weight
        calendar_fmp = self.data_fetcher.fetch_economic_calendar_fmp(days_ahead=3)
        if calendar_fmp:
            # High-impact events = uncertainty = reduce confidence
            risk_level = calendar_fmp['risk_level']
            event_count = calendar_fmp['high_impact_count']
            
            if risk_level == 'HIGH':
                calendar_score = -0.03  # Major events coming = high uncertainty
            elif risk_level == 'MEDIUM':
                calendar_score = -0.01  # Some events
            else:
                calendar_score = 0.00  # Clear calendar = good
            
            scores['economic_calendar'] = calendar_score * 10 * 0.05
            print(f"📅 NEW: Economic Calendar (5% weight - FMP API):")
            print(f"   Risk Level: {risk_level} ({event_count} high-impact events next 3 days)")
            if calendar_fmp['major_events']:
                print(f"   Upcoming: {calendar_fmp['major_events'][0]['event']} ({calendar_fmp['major_events'][0]['country']})")
            print(f"   Base Score: {calendar_score:+.3f} → Weighted: {scores['economic_calendar']:+.3f}\n")
        else:
            scores['economic_calendar'] = 0.0
            print(f"📅 Economic Calendar: Manual check recommended\n")
        
        # 14. NEW: News Sentiment (FMP API) - 5% weight
        pair_clean = self.pair.replace('/', '')
        news_sentiment = self.data_fetcher.fetch_forex_news_sentiment_fmp(pair=pair_clean)
        if news_sentiment:
            # Sentiment: -1 to +1
            sentiment_score = news_sentiment['sentiment_score'] * 0.05
            scores['news_sentiment'] = sentiment_score * 10 * 0.05
            
            print(f"📰 NEW: News Sentiment (5% weight - FMP API):")
            print(f"   Sentiment: {news_sentiment['sentiment']} ({news_sentiment['sentiment_score']:+.2f})")
            print(f"   Recent: {news_sentiment['news_count']} articles (Bullish:{news_sentiment['bullish_mentions']} vs Bearish:{news_sentiment['bearish_mentions']})")
            if news_sentiment['recent_headlines']:
                print(f"   Latest: {news_sentiment['recent_headlines'][0][:60]}...")
            print(f"   Base Score: {sentiment_score:+.3f} → Weighted: {scores['news_sentiment']:+.3f}\n")
        else:
            scores['news_sentiment'] = 0.0
            print(f"📰 News Sentiment: Not available\n")
        
        # 15. NEW: Currency Strength Index - 8% weight (POWERFUL!)
        currency_strength = self.data_fetcher.calculate_currency_strength()
        if currency_strength:
            # Extract base and quote currencies
            if self.pair == 'EUR/USD':
                base, quote = 'EUR', 'USD'
            elif self.pair == 'GBP/USD':
                base, quote = 'GBP', 'USD'
            elif self.pair == 'USD/JPY':
                base, quote = 'USD', 'JPY'
            else:
                base, quote = None, None
            
            if base and quote:
                base_strength = currency_strength['strengths'][base]
                quote_strength = currency_strength['strengths'][quote]
                
                # Relative strength determines direction
                strength_diff = (base_strength - quote_strength) / 10  # Normalize
                strength_score = min(max(strength_diff, -0.10), 0.10)
                
                scores['currency_strength'] = strength_score * 10 * 0.05  # REDUCED from 8% to 5% (slow-moving)
                
                print(f"💪 NEW: Currency Strength Index (5% weight - REDUCED):")
                print(f"   Rankings: {' > '.join(currency_strength['rankings'])}")
                print(f"   {base}: {base_strength:+.2f} vs {quote}: {quote_strength:+.2f}")
                print(f"   Strongest: {currency_strength['strongest']}, Weakest: {currency_strength['weakest']}")
                print(f"   Base Score: {strength_score:+.3f} → Amplified: {strength_score*10:+.3f} → Weighted: {scores['currency_strength']:+.3f}\n")
            else:
                scores['currency_strength'] = 0.0
        else:
            scores['currency_strength'] = 0.0
            print(f"💪 Currency Strength: Not available\n")
        
        # 16. ALPHA VANTAGE NEWS (You have the key!) - 7% weight
        pair_clean = self.pair.replace('/', '')
        av_news = self.data_fetcher.fetch_news_sentiment_alpha_vantage(pair=pair_clean)
        if av_news:
            sentiment_score = av_news['sentiment_score'] * 0.10  # Scale to ±0.10
            scores['av_news'] = sentiment_score * 10 * 0.07
            
            print(f"📰 ALPHA VANTAGE NEWS (7% weight - YOUR API):")
            print(f"   Sentiment: {av_news['sentiment']} ({av_news['sentiment_score']:+.3f})")
            print(f"   Articles: {av_news['article_count']} analyzed")
            print(f"   Confidence: {av_news['confidence']:.2f}")
            if av_news['headlines']:
                print(f"   Top: {av_news['headlines'][0][:70]}...")
            print(f"   Base Score: {sentiment_score:+.3f} → Weighted: {scores['av_news']:+.3f}\n")
        else:
            scores['av_news'] = 0.0
            print(f"📰 Alpha Vantage News: Not available\n")
        
        # 17. LONDON MOMENTUM DETECTOR - 8% weight (CRITICAL for 6:30 AM!)
        london_mom = self.data_fetcher.detect_london_momentum()
        if london_mom:
            # Check if London setup aligns with pair
            if self.pair in ['EUR/USD', 'GBP/USD']:
                # For EUR/USD: USD weak = bullish
                if london_mom['trend'] == 'usd_weak':
                    london_score = 0.08  # Strong bullish
                elif london_mom['trend'] == 'usd_strong':
                    london_score = -0.08  # Strong bearish
                else:
                    london_score = 0.0
            elif self.pair == 'USD/JPY':
                # For USD/JPY: USD strong = bullish
                if london_mom['trend'] == 'usd_strong':
                    london_score = 0.08
                elif london_mom['trend'] == 'usd_weak':
                    london_score = -0.08
                else:
                    london_score = 0.0
            else:
                london_score = 0.0
            
            scores['london_momentum'] = london_score * 10 * 0.04  # REDUCED from 8% to 4% (only relevant at London open)
            
            print(f"🌅 LONDON MOMENTUM (4% weight - REDUCED):")
            print(f"   USD Trend: {london_mom['trend']}")
            print(f"   London Setup: {london_mom['london_setup']}")
            print(f"   Pairs Analyzed: {london_mom['pairs_analyzed']}")
            print(f"   Base Score: {london_score:+.3f} → Amplified: {london_score*10:+.3f} → Weighted: {scores['london_momentum']:+.3f}\n")
        else:
            scores['london_momentum'] = 0.0
            print(f"🌅 London Momentum: Not available\n")
        
        # 18. VOLUME PROFILE - 6% weight (Institutional activity)
        volume_prof = self.data_fetcher.analyze_volume_profile(self.symbol)
        if volume_prof:
            if volume_prof['signal'] == 'bullish' and volume_prof['strength'] == 'strong':
                volume_score = 0.06
            elif volume_prof['signal'] == 'bearish' and volume_prof['strength'] == 'strong':
                volume_score = -0.06
            elif volume_prof['signal'] == 'building':
                volume_score = 0.03 if volume_prof['price_change'] > 0 else -0.03
            else:
                volume_score = 0.0
            
            scores['volume_profile'] = volume_score * 10 * 0.04  # REDUCED from 6% to 4%
            
            print(f"📊 VOLUME PROFILE (4% weight - REDUCED):")
            print(f"   Signal: {volume_prof['signal']} ({volume_prof['strength']})")
            print(f"   Volume Ratio: {volume_prof['volume_ratio']:.2f}x average")
            print(f"   Price Change: {volume_prof['price_change']:+.2f}%")
            print(f"   Base Score: {volume_score:+.3f} → Weighted: {scores['volume_profile']:+.3f}\n")
        else:
            scores['volume_profile'] = 0.0
            print(f"📊 Volume Profile: Not available\n")
        
        # 19. TREND STRENGTH - 7% weight (ADX-like)
        trend_str = self.data_fetcher.calculate_trend_strength(self.symbol)
        if trend_str:
            if trend_str['trend_direction'] == 'uptrend' and trend_str['strength_level'] == 'strong':
                trend_score = 0.08
            elif trend_str['trend_direction'] == 'downtrend' and trend_str['strength_level'] == 'strong':
                trend_score = -0.08
            elif trend_str['trend_direction'] == 'uptrend' and trend_str['strength_level'] == 'moderate':
                trend_score = 0.04
            elif trend_str['trend_direction'] == 'downtrend' and trend_str['strength_level'] == 'moderate':
                trend_score = -0.04
            else:
                trend_score = 0.0  # Ranging = skip
            
            scores['trend_strength'] = trend_score * 10 * 0.05  # REDUCED from 7% to 5%
            
            print(f"📈 TREND STRENGTH (5% weight - REDUCED):")
            print(f"   Direction: {trend_str['trend_direction']} ({trend_str['strength_level']})")
            print(f"   Tradeable: {'YES ✅' if trend_str['tradeable'] else 'NO ❌'}")
            print(f"   Strength Value: {trend_str['trend_strength']:.3f}")
            print(f"   Base Score: {trend_score:+.3f} → Weighted: {scores['trend_strength']:+.3f}\n")
        else:
            scores['trend_strength'] = 0.0
            print(f"📈 Trend Strength: Not available\n")
        
        # 20. MULTI-TIMEFRAME CONFIRMATION - 10% weight (HIGH CONFIDENCE BOOSTER!)
        mtf = self.data_fetcher.multi_timeframe_confirmation(self.symbol)
        if mtf:
            if mtf['alignment'] == 'bullish' and mtf['strength'] == 'strong':
                mtf_score = 0.10  # All timeframes bullish = VERY strong signal
            elif mtf['alignment'] == 'bearish' and mtf['strength'] == 'strong':
                mtf_score = -0.10
            elif mtf['alignment'] == 'bullish' and mtf['strength'] == 'moderate':
                mtf_score = 0.05
            elif mtf['alignment'] == 'bearish' and mtf['strength'] == 'moderate':
                mtf_score = -0.05
            else:
                mtf_score = 0.0  # Mixed = no edge
            
            scores['multi_timeframe'] = mtf_score * 10 * 0.06  # REDUCED from 10% to 6% (slow-moving data)
            
            print(f"⏳ MULTI-TIMEFRAME (6% weight - REDUCED):")
            print(f"   Alignment: {mtf['alignment']} ({mtf['strength']})")
            print(f"   1H: {mtf['timeframes'].get('1h', 'N/A')}, Daily: {mtf['timeframes'].get('daily', 'N/A')}")
            print(f"   Confidence: {mtf['confidence']*100:.0f}%")
            print(f"   Base Score: {mtf_score:+.3f} → Amplified: {mtf_score*10:+.3f} → Weighted: {scores['multi_timeframe']:+.3f}\n")
        else:
            scores['multi_timeframe'] = 0.0
            print(f"⏳ Multi-Timeframe: Not available\n")
        
        # Calculate total score
        total_score = sum(scores.values())
        
        print(f"{'='*80}")
        print(f"🎯 PREDICTION CALCULATION")
        print(f"{'='*80}\n")
        
        print(f"📊 Component Scores:")
        for component, score in scores.items():
            print(f"   {component}: {score:+.3f}")
        print(f"   " + "-"*40)
        print(f"   TOTAL: {total_score:+.3f}\n")
        
        # FIX #3: IMPROVED confidence scaling - uses 60-95% range with piecewise function
        if total_score >= 0.08:
            direction = "BUY" if not self.pair.startswith('USD') else "LONG"
            # Piecewise: 65-85% for scores 0.08-0.15, then 85-95% for 0.15-0.25+
            if abs(total_score) < 0.15:
                confidence_base = 65 + abs(total_score) * 285  # 65 + (0.08*285) = 88%
            else:
                confidence_base = 88 + (abs(total_score) - 0.15) * 70  # Slower scaling above 0.15
        elif total_score <= -0.08:
            direction = "SELL" if not self.pair.startswith('USD') else "SHORT"
            # Same piecewise scaling
            if abs(total_score) < 0.15:
                confidence_base = 65 + abs(total_score) * 285
            else:
                confidence_base = 88 + (abs(total_score) - 0.15) * 70
        else:
            direction = "NEUTRAL"
            # For neutral: 50-70% range for scores 0-0.08
            confidence_base = 50 + abs(total_score) * 250
        
        confidence = min(confidence_base, 95)  # INCREASED cap to 95% for exceptional signals
        
        # Apply PRO session multipliers
        confidence *= session_info['confidence_multiplier']
        confidence = min(confidence, 95)  # Re-cap after adjustment
        
        # Calculate targets
        current_price = technical_data['current_price']
        daily_pips = self.config['typical_daily_pips']
        pip_value = self.config['pip_value']
        
        # Target: 50-100 pips based on confidence
        target_pips = int(50 + (confidence - 65) * 2)  # 50-90 pips
        target_pips = int(target_pips * session_info['target_multiplier'])  # PRO: Session adjustment
        stop_pips = int(target_pips / 2)  # 2:1 R:R
        
        if direction in ["BUY", "LONG"]:
            target_price = current_price + (target_pips * pip_value)
            stop_price = current_price - (stop_pips * pip_value)
        elif direction in ["SELL", "SHORT"]:
            target_price = current_price - (target_pips * pip_value)
            stop_price = current_price + (stop_pips * pip_value)
        else:
            target_price = current_price
            stop_price = current_price
        
        # Output prediction
        print(f"{'='*80}")
        print(f"🎯 PREDICTION RESULT")
        print(f"{'='*80}\n")
        
        print(f"📍 Direction: {direction}")
        print(f"🎲 Confidence: {confidence:.1f}%")
        print(f"💰 Current Price: {current_price:.4f}")
        
        if direction != "NEUTRAL":
            print(f"🎯 Target: {target_price:.4f} ({target_pips:+d} pips)")
            print(f"🛑 Stop Loss: {stop_price:.4f} ({stop_pips:+d} pips)")
            print(f"📊 Risk:Reward: 1:{target_pips/stop_pips:.1f}")
        
        print(f"📈 Score: {total_score:+.3f}")
        print(f"⏰ Hold Period: 24-48 hours")
        
        print(f"\n{'='*80}")
        print(f"💡 RECOMMENDATION")
        print(f"{'='*80}\n")
        
        if confidence >= 70:
            print(f"   ✅ HIGH CONFIDENCE - Good trade setup")
        elif confidence >= 60:  # FIX: Lower threshold to 60% (forex 60-70% is acceptable)
            print(f"   ⚠️ MODERATE CONFIDENCE - Acceptable if risk managed")
        else:
            print(f"   ❌ LOW CONFIDENCE - Skip or wait for better setup")
        
        print(f"\n{'='*80}\n")
        
        return {
            'pair': self.pair,
            'direction': direction,
            'confidence': confidence,
            'current_price': current_price,
            'target_price': target_price,
            'stop_price': stop_price,
            'target_pips': target_pips if direction != "NEUTRAL" else 0,
            'score': total_score,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

# Main execution
if __name__ == "__main__":
    # Run prediction for EUR/USD (start with this)
    predictor = ForexDailyPredictor('EUR/USD')
    prediction = predictor.generate_prediction()
    
    if prediction:
        print(f"✅ Prediction generated successfully!")
        print(f"   Direction: {prediction['direction']}")
        print(f"   Confidence: {prediction['confidence']:.1f}%")
    else:
        print(f"❌ Failed to generate prediction")
