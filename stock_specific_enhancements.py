"""
Stock-Specific Enhancements for AMD and NVDA
Advanced indicators and data sources for improved prediction accuracy
"""

import yfinance as yf
import requests
from datetime import datetime, timedelta
from typing import Dict, Any
import os


class StockSpecificEnhancements:
    """Advanced stock-specific indicators for AMD and NVDA"""

    def __init__(self, symbol: str):
        self.symbol = symbol.upper()
        self.ticker = yf.Ticker(self.symbol)

    def get_nvda_relative_strength_vs_smh(self) -> Dict[str, Any]:
        """
        Calculate NVDA's relative strength vs SMH (semiconductor ETF)
        NVDA outperforming SMH = strength, underperforming = weakness

        Returns:
            Dict with relative strength score and data
        """
        if self.symbol != 'NVDA':
            return {'score': 0.0, 'has_data': False, 'relative_performance': 0.0}

        try:
            print("\n📊 NVDA Relative Strength vs SMH...")

            # Get NVDA and SMH data
            nvda_hist = self.ticker.history(period="20d")
            smh_ticker = yf.Ticker('SMH')
            smh_hist = smh_ticker.history(period="20d")

            if len(nvda_hist) < 5 or len(smh_hist) < 5:
                return {'score': 0.0, 'has_data': False}

            # Calculate 5-day, 10-day, 20-day relative performance
            periods = [5, 10, 20]
            relative_scores = []

            for period in periods:
                if len(nvda_hist) >= period and len(smh_hist) >= period:
                    nvda_change = ((nvda_hist['Close'].iloc[-1] - nvda_hist['Close'].iloc[-period]) /
                                   nvda_hist['Close'].iloc[-period]) * 100
                    smh_change = ((smh_hist['Close'].iloc[-1] - smh_hist['Close'].iloc[-period]) /
                                  smh_hist['Close'].iloc[-period]) * 100

                    relative_perf = nvda_change - smh_change
                    relative_scores.append(relative_perf)

            if not relative_scores:
                return {'score': 0.0, 'has_data': False}

            # Weighted average (more weight to shorter periods)
            avg_relative = (relative_scores[0] * 0.5 +
                            relative_scores[1] * 0.3 +
                            relative_scores[2] * 0.2) if len(relative_scores) >= 3 else relative_scores[0]

            # Convert to score (-0.15 to +0.15 range)
            # NVDA outperforming by 3%+ = +0.09 boost
            # NVDA underperforming by 2%+ = -0.08 penalty
            if avg_relative > 3.0:
                score = 0.09  # Strong outperformance
            elif avg_relative > 1.5:
                score = 0.06  # Moderate outperformance
            elif avg_relative > 0.5:
                score = 0.03  # Slight outperformance
            elif avg_relative < -2.0:
                score = -0.08  # Significant underperformance
            elif avg_relative < -1.0:
                score = -0.05  # Moderate underperformance
            elif avg_relative < -0.5:
                score = -0.03  # Slight underperformance
            else:
                score = 0.0  # In line

            print(
                f"   NVDA vs SMH (5d/10d/20d): {relative_scores[0]:+.2f}% / {relative_scores[1]:+.2f}% / {relative_scores[2]:+.2f}%")
            print(f"   Average Relative Performance: {avg_relative:+.2f}%")
            if score > 0:
                print(f"   ✅ NVDA Outperforming SMH → +{score:.3f} boost")
            elif score < 0:
                print(f"   ⚠️ NVDA Underperforming SMH → {score:.3f} penalty")
            else:
                print(f"   ➡️ NVDA In Line with SMH")

            return {
                'score': score,
                'has_data': True,
                'relative_performance': avg_relative,
                '5d': relative_scores[0] if len(relative_scores) > 0 else 0,
                '10d': relative_scores[1] if len(relative_scores) > 1 else 0,
                '20d': relative_scores[2] if len(relative_scores) > 2 else 0
            }

        except Exception as e:
            print(f"   ⚠️ Error: {str(e)[:50]}")
            return {'score': 0.0, 'has_data': False}

    def get_amd_200day_ma_distance(self) -> Dict[str, Any]:
        """
        Calculate AMD's distance from 200-day moving average
        AMD mean-reverts to 200MA historically

        Returns:
            Dict with MA distance score and data
        """
        if self.symbol != 'AMD':
            return {'score': 0.0, 'has_data': False, 'distance_pct': 0.0}

        try:
            print("\n📊 AMD 200-Day MA Distance...")

            # Get 200 days of data
            hist = self.ticker.history(period="1y")

            if len(hist) < 200:
                return {'score': 0.0, 'has_data': False}

            # Calculate 200-day MA
            ma200 = hist['Close'].rolling(window=200).mean().iloc[-1]
            current_price = hist['Close'].iloc[-1]

            # Calculate distance percentage
            distance_pct = ((current_price - ma200) / ma200) * 100

            # Score logic:
            # >10% above 200MA + gap up → -0.08 (overbought, mean reversion risk)
            # >10% below 200MA + gap down → +0.08 (oversold, bounce opportunity)
            # Near 200MA → neutral

            score = 0.0
            if distance_pct > 10.0:
                # Significantly above 200MA - overbought risk
                score = -0.08
                print(f"   Current: ${current_price:.2f}")
                print(f"   200-Day MA: ${ma200:.2f}")
                print(f"   Distance: {distance_pct:+.2f}% (ABOVE)")
                print(
                    f"   ⚠️ Overbought - Mean reversion risk → -{abs(score):.3f} penalty")
            elif distance_pct < -10.0:
                # Significantly below 200MA - oversold bounce opportunity
                score = 0.08
                print(f"   Current: ${current_price:.2f}")
                print(f"   200-Day MA: ${ma200:.2f}")
                print(f"   Distance: {distance_pct:+.2f}% (BELOW)")
                print(
                    f"   💡 Oversold - Bounce opportunity → +{score:.3f} boost")
            else:
                # Near 200MA - neutral
                print(f"   Current: ${current_price:.2f}")
                print(f"   200-Day MA: ${ma200:.2f}")
                print(f"   Distance: {distance_pct:+.2f}% (NEAR MA)")
                print(f"   ➡️ Neutral - No mean reversion signal")

            return {
                'score': score,
                'has_data': True,
                'distance_pct': distance_pct,
                'current_price': current_price,
                'ma200': ma200
            }

        except Exception as e:
            print(f"   ⚠️ Error: {str(e)[:50]}")
            return {'score': 0.0, 'has_data': False}

    def get_hyperscaler_capex_trend(self) -> Dict[str, Any]:
        """
        Track hyperscaler CapEx trends (Microsoft, Google, Amazon, Meta)
        High CapEx = bullish for both AMD and NVDA (data center chips)

        Returns:
            Dict with CapEx trend score
        """
        if self.symbol not in ['AMD', 'NVDA']:
            return {'score': 0.0, 'has_data': False}

        try:
            print("\n📊 Hyperscaler CapEx Trend...")

            # This is a simplified version - in production, you'd parse earnings transcripts
            # For now, we'll use a proxy: track hyperscaler stock performance as CapEx indicator
            # Strong hyperscaler performance = likely high CapEx spending

            hyperscalers = ['MSFT', 'GOOGL', 'AMZN', 'META']
            capex_proxy_scores = []

            for ticker_symbol in hyperscalers:
                try:
                    ticker = yf.Ticker(ticker_symbol)
                    hist = ticker.history(period="3mo")

                    if len(hist) >= 20:
                        # 20-day performance as proxy for CapEx sentiment
                        change_20d = ((hist['Close'].iloc[-1] - hist['Close'].iloc[-20]) /
                                      hist['Close'].iloc[-20]) * 100
                        capex_proxy_scores.append(change_20d)
                        print(f"   {ticker_symbol}: {change_20d:+.2f}% (20d)")
                except:
                    pass

            if not capex_proxy_scores:
                return {'score': 0.0, 'has_data': False}

            avg_performance = sum(capex_proxy_scores) / len(capex_proxy_scores)

            # Convert to score
            # Strong hyperscaler performance = bullish for data center chips
            if avg_performance > 10.0:
                score = 0.15  # Very bullish
            elif avg_performance > 5.0:
                score = 0.10  # Bullish
            elif avg_performance > 0:
                score = 0.05  # Slightly bullish
            elif avg_performance < -10.0:
                score = -0.15  # Very bearish
            elif avg_performance < -5.0:
                score = -0.10  # Bearish
            elif avg_performance < 0:
                score = -0.05  # Slightly bearish
            else:
                score = 0.0

            print(
                f"   Average Hyperscaler Performance: {avg_performance:+.2f}%")
            if score > 0:
                print(
                    f"   ✅ Strong CapEx Proxy → +{score:.3f} boost (data center demand)")
            elif score < 0:
                print(
                    f"   ⚠️ Weak CapEx Proxy → {score:.3f} penalty (demand concerns)")
            else:
                print(f"   ➡️ Neutral CapEx Proxy")

            return {
                'score': score,
                'has_data': True,
                'avg_hyperscaler_performance': avg_performance,
                'method': 'proxy'  # Using stock performance as proxy
            }

        except Exception as e:
            print(f"   ⚠️ Error: {str(e)[:50]}")
            return {'score': 0.0, 'has_data': False}

    def get_nvda_insider_transactions(self) -> Dict[str, Any]:
        """
        Track NVDA insider transactions (CEO/executives buying/selling)
        Uses SEC EDGAR API (simplified - would need full implementation)

        Returns:
            Dict with insider transaction score
        """
        if self.symbol != 'NVDA':
            return {'score': 0.0, 'has_data': False}

        try:
            print("\n📊 NVDA Insider Transactions...")

            # NOTE: Full SEC EDGAR API implementation would require:
            # 1. SEC EDGAR API access
            # 2. Form 4 filing parsing
            # 3. Transaction type detection (buy/sell)
            # 4. Amount calculation

            # For now, return neutral (would need full implementation)
            print("   ⚠️ Insider transaction tracking requires SEC EDGAR API integration")
            print("   ➡️ Using neutral score (not implemented yet)")

            return {
                'score': 0.0,
                'has_data': False,
                'note': 'Requires SEC EDGAR API implementation'
            }

        except Exception as e:
            print(f"   ⚠️ Error: {str(e)[:50]}")
            return {'score': 0.0, 'has_data': False}

    def get_all_enhancements(self) -> Dict[str, Any]:
        """Get all stock-specific enhancements"""
        enhancements = {}

        # NVDA-specific
        if self.symbol == 'NVDA':
            enhancements['relative_strength_smh'] = self.get_nvda_relative_strength_vs_smh(
            )
            enhancements['insider_transactions'] = self.get_nvda_insider_transactions()

        # AMD-specific
        if self.symbol == 'AMD':
            enhancements['ma200_distance'] = self.get_amd_200day_ma_distance()

        # Both AMD and NVDA
        if self.symbol in ['AMD', 'NVDA']:
            enhancements['hyperscaler_capex'] = self.get_hyperscaler_capex_trend()

        return enhancements
