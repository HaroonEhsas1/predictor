#!/usr/bin/env python3
"""
Gold Daily Swing Predictor (XAUUSD)

Predicts 24-48 hour directional moves for spot gold vs USD using a
multi-factor scoring system similar to your forex predictor.

Key components:
- Gold price action (RSI, MACD, MAs, ATR, exhaustion/reversal)
- US 10Y yields (real yield proxy)
- Dollar index (DXY)
- Risk sentiment (VIX + ES futures)
- Economic calendar risk (FMP API)

Output:
- Direction: UP / DOWN / NEUTRAL
- Confidence: 40-95%
- Target & Stop (ATR-based, 2:1 R:R)
- Position size suggestion (% of normal)
"""

import sys
from pathlib import Path
from datetime import datetime

import yfinance as yf
import pandas as pd

# Ensure local imports work when run as a script
sys.path.insert(0, str(Path(__file__).parent))

from gold_config import get_gold_config
from forex_data_fetcher import ForexDataFetcher


class GoldDailyPredictor:
    """Gold (XAUUSD) 24-48h swing prediction engine."""

    def __init__(self):
        self.config = get_gold_config()
        self.symbol = self.config["symbol"]
        self.data_fetcher = ForexDataFetcher()

        print("\n" + "=" * 80)
        print("🥇 GOLD DAILY SWING PREDICTOR (XAUUSD)")
        print("=" * 80 + "\n")

    # ------------------------------------------------------------------
    # DATA & TECHNICALS
    # ------------------------------------------------------------------
    def fetch_gold_history(self, period: str = "180d"):
        """Fetch historical XAUUSD price data (daily bars)."""
        try:
            ticker = yf.Ticker(self.symbol)
            hist = ticker.history(period=period, interval="1d")

            if hist.empty:
                print(f"⚠️ No data for {self.symbol}")
                return None

            return hist
        except Exception as e:
            print(f"⚠️ Error fetching {self.symbol}: {e}")
            return None

    def calculate_technical_indicators(self, hist: pd.DataFrame) -> dict:
        """Calculate core technical indicators for gold.

        Returns:
            dict with rsi, macd, ma_50, ma_200, current_price, trend, atr
        """
        close = hist["Close"]
        high = hist["High"]
        low = hist["Low"]

        # RSI (14)
        delta = close.diff()
        gain = delta.where(delta > 0, 0).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        current_rsi = float(rsi.iloc[-1]) if not rsi.empty else 50.0

        # MACD (12,26,9)
        ema_12 = close.ewm(span=12, adjust=False).mean()
        ema_26 = close.ewm(span=26, adjust=False).mean()
        macd = ema_12 - ema_26
        signal = macd.ewm(span=9, adjust=False).mean()
        macd_value = float(macd.iloc[-1] - signal.iloc[-1]) if len(macd) > 0 else 0.0

        # Moving averages
        ma_50 = close.rolling(50).mean()
        ma_200 = close.rolling(200).mean() if len(close) >= 200 else ma_50

        current_price = float(close.iloc[-1])
        ma_50_val = float(ma_50.iloc[-1]) if not ma_50.empty else current_price
        ma_200_val = float(ma_200.iloc[-1]) if not ma_200.empty else current_price

        # Trend classification
        if current_price > ma_50_val > ma_200_val:
            trend = "UPTREND"
        elif current_price < ma_50_val < ma_200_val:
            trend = "DOWNTREND"
        else:
            trend = "SIDEWAYS"

        # ATR (14) in USD
        tr1 = high - low
        tr2 = (high - close.shift(1)).abs()
        tr3 = (low - close.shift(1)).abs()
        true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr_series = true_range.rolling(window=14).mean()
        atr = float(atr_series.iloc[-1]) if not atr_series.empty else 0.0

        return {
            "rsi": current_rsi,
            "macd": macd_value,
            "ma_50": ma_50_val,
            "ma_200": ma_200_val,
            "current_price": current_price,
            "trend": trend,
            "atr": atr,
        }

    # ------------------------------------------------------------------
    # COMPONENT ANALYSES
    # ------------------------------------------------------------------
    def analyze_price_action(self, technical: dict):
        """Analyze gold's own price action and structure.

        Uses RSI, MACD, trend, distance to MA, and futures exhaustion/reversal
        from ForexDataFetcher.fetch_gold_price().
        """
        rsi = technical["rsi"]
        macd = technical["macd"]
        trend = technical["trend"]
        current_price = technical["current_price"]
        ma_50 = technical["ma_50"]

        score = 0.0
        explanation = []

        # RSI zones
        explanation.append(f"RSI: {rsi:.1f}")
        if rsi > 70:
            score -= 0.08
            explanation.append("→ Overbought (reversal risk)")
        elif rsi > 60:
            score -= 0.04
            explanation.append("→ Slightly overbought")
        elif rsi < 30:
            score += 0.08
            explanation.append("→ Oversold (bounce potential)")
        elif rsi < 40:
            score += 0.04
            explanation.append("→ Mildly oversold")
        else:
            explanation.append("→ Neutral zone")

        # MACD
        explanation.append(f"\nMACD: {macd:+.5f}")
        if macd > 0:
            score += 0.04
            explanation.append("→ Bullish momentum")
        elif macd < 0:
            score -= 0.04
            explanation.append("→ Bearish momentum")

        # Trend
        explanation.append(f"\nTrend: {trend}")
        if trend == "UPTREND":
            score += 0.05
            explanation.append("→ Trend supports upside")
        elif trend == "DOWNTREND":
            score -= 0.05
            explanation.append("→ Trend supports downside")

        # Distance from 50-day MA (mean reversion bias)
        ma_distance_pct = ((current_price - ma_50) / ma_50) * 100 if ma_50 else 0.0
        explanation.append(f"\nPrice vs 50-MA: {ma_distance_pct:+.2f}%")
        if abs(ma_distance_pct) > 3:
            if ma_distance_pct > 0:
                score -= 0.04
                explanation.append("→ Extended above MA (pullback risk)")
            else:
                score += 0.04
                explanation.append("→ Extended below MA (bounce potential)")

        # Futures-based exhaustion / reversal (GC=F)
        gold_futures = self.data_fetcher.fetch_gold_price()
        if gold_futures:
            gf_change = gold_futures["change_pct"]
            gf_rsi = gold_futures.get("rsi", 50)
            exhaustion = gold_futures.get("exhaustion_risk", False)
            reversal = gold_futures.get("reversal_signal", False)

            explanation.append(
                f"\nFutures (GC=F): {gold_futures['price']:.2f} USD ({gf_change:+.2f}%), RSI {gf_rsi:.1f}"
            )

            if exhaustion:
                # Blow-off top in futures = contrarian bearish for gold
                score -= 0.10
                explanation.append(
                    "→ ⚠️ EXHAUSTION: strong rally + overbought (topping risk)"
                )
            elif reversal:
                # Capitulation low in futures = contrarian bullish
                score += 0.10
                explanation.append(
                    "→ ✅ REVERSAL: strong selloff + oversold (bottoming risk)"
                )
        else:
            explanation.append("\nFutures data unavailable (GC=F)")

        # Clip to reasonable bounds
        score = max(min(score, 0.20), -0.20)
        return score, "\n".join(explanation)

    def analyze_candles(self, hist: pd.DataFrame):
        if hist is None or len(hist) < 3:
            return 0.0, "Candle patterns: insufficient data"

        recent = hist.tail(3)
        c2 = recent.iloc[0]
        c0 = recent.iloc[1]
        c1 = recent.iloc[2]

        def body(c):
            return float(c["Close"] - c["Open"])

        def rng(c):
            return float(c["High"] - c["Low"])

        b1 = body(c1)
        b0 = body(c0)
        r1 = rng(c1)

        score = 0.0
        lines = [
            f"Last candle: O={c1['Open']:.2f}, H={c1['High']:.2f}, L={c1['Low']:.2f}, C={c1['Close']:.2f}"
        ]

        # Engulfing patterns
        if b0 < 0 and b1 > 0 and c1["Open"] <= c0["Close"] and c1["Close"] >= c0["Open"]:
            score += 0.06
            lines.append("→ Bullish engulfing pattern")
        elif b0 > 0 and b1 < 0 and c1["Open"] >= c0["Close"] and c1["Close"] <= c0["Open"]:
            score -= 0.06
            lines.append("→ Bearish engulfing pattern")

        upper_wick = float(c1["High"] - max(c1["Open"], c1["Close"]))
        lower_wick = float(min(c1["Open"], c1["Close"]) - c1["Low"])
        body_size = abs(b1)

        if r1 > 0:
            upper_ratio = upper_wick / r1
            lower_ratio = lower_wick / r1
        else:
            upper_ratio = 0.0
            lower_ratio = 0.0

        if lower_ratio > 0.5 and body_size < r1 * 0.3 and c0["Close"] < c2["Close"]:
            score += 0.05
            lines.append("→ Hammer-like candle after decline (bounce potential)")

        if upper_ratio > 0.5 and body_size < r1 * 0.3 and c0["Close"] > c2["Close"]:
            score -= 0.05
            lines.append("→ Shooting star-like candle after rally (reversal risk)")

        if len(lines) == 1:
            lines.append("→ No strong candlestick pattern detected")

        score = max(min(score, 0.10), -0.10)
        return score, "\n".join(lines)

    def plot_gold_chart(self, hist: pd.DataFrame, filename: str = "gold_chart.png"):
        if hist is None or hist.empty:
            print("⚠️ Cannot plot gold chart: no data")
            return

        try:
            import matplotlib.pyplot as plt
            import matplotlib.dates as mdates
        except Exception as e:
            print(f"⚠️ Charting unavailable (matplotlib not installed): {e}")
            return

        try:
            from mplfinance.original_flavor import candlestick_ohlc
            have_candles = True
        except Exception:
            have_candles = False

        data = hist.tail(90).copy()
        if data.empty:
            print("⚠️ Not enough data to plot chart")
            return

        dates = mdates.date2num(data.index.to_pydatetime())
        try:
            ohlc = list(
                zip(
                    dates,
                    data["Open"].astype(float),
                    data["High"].astype(float),
                    data["Low"].astype(float),
                    data["Close"].astype(float),
                )
            )
        except Exception as e:
            print(f"⚠️ Chart data error: {e}")
            return

        fig, ax = plt.subplots(figsize=(10, 6))
        if have_candles:
            candlestick_ohlc(ax, ohlc, width=0.6, colorup="green", colordown="red", alpha=0.8)
            ax.xaxis_date()
            fig.autofmt_xdate()
        else:
            ax.plot(data.index, data["Close"].astype(float), color="blue")

        ax.set_title("Gold (GC=F) - Recent Daily Candles")
        ax.set_xlabel("Date")
        ax.set_ylabel("Price (USD)")

        output_path = Path(__file__).parent / filename
        try:
            fig.savefig(output_path, dpi=120, bbox_inches="tight")
            print(f"🖼 Gold chart saved to {output_path}")
        except Exception as e:
            print(f"⚠️ Failed to save chart: {e}")
        finally:
            plt.close(fig)

    def analyze_yields(self):
        """Analyze US 10Y yield impact on gold (inverse relationship)."""
        yield_data = self.data_fetcher.fetch_10y_yield()
        if not yield_data:
            return 0.0, "10Y yield data unavailable"

        yld = yield_data["yield"]
        change = yield_data["change"]
        trend = yield_data["trend"]

        explanation = [
            f"10Y Yield: {yld:.2f}% ({change:+.2f})",
            f"Trend: {trend}",
        ]

        score = 0.0
        # Rising yields are typically negative for gold
        if change > 0.15:
            score = -0.10
            explanation.append("→ Strong rise in yields (bearish gold)")
        elif change > 0.05:
            score = -0.05
            explanation.append("→ Moderate rise in yields (headwind)")
        elif change < -0.15:
            score = 0.10
            explanation.append("→ Strong fall in yields (bullish gold)")
        elif change < -0.05:
            score = 0.05
            explanation.append("→ Moderate fall in yields (tailwind)")
        else:
            explanation.append("→ Small change (neutral)")

        return score, "\n".join(explanation)

    def analyze_dxy(self):
        """Analyze Dollar Index (DXY) impact on gold (typically inverse)."""
        try:
            dxy = yf.Ticker("DX-Y.NYB")
            dxy_hist = dxy.history(period="10d")
            if dxy_hist.empty:
                return 0.0, "DXY data unavailable"

            current = float(dxy_hist["Close"].iloc[-1])
            past = float(dxy_hist["Close"].iloc[0])
            change_pct = ((current - past) / past) * 100

            explanation = [f"DXY: {current:.2f} ({change_pct:+.2f}% 10-day)"]

            score = 0.0
            if change_pct > 1.5:
                score = -0.08
                explanation.append("→ Strong dollar rally (bearish gold)")
            elif change_pct > 0.5:
                score = -0.04
                explanation.append("→ Dollar strengthening (headwind)")
            elif change_pct < -1.5:
                score = 0.08
                explanation.append("→ Strong dollar drop (bullish gold)")
            elif change_pct < -0.5:
                score = 0.04
                explanation.append("→ Dollar weakening (tailwind)")
            else:
                explanation.append("→ Sideways dollar (neutral)")

            return score, "\n".join(explanation)
        except Exception as e:
            return 0.0, f"DXY error: {e}"

    def analyze_risk_sentiment(self):
        """Analyze global risk sentiment via VIX and ES futures.

        - Risk-OFF (fear, falling stocks) tends to support gold.
        - Risk-ON (calm, rising stocks) tends to be a slight headwind.
        """
        score = 0.0
        explanation = []

        # VIX
        try:
            vix = yf.Ticker("^VIX")
            vix_hist = vix.history(period="5d")
            if not vix_hist.empty:
                current_vix = float(vix_hist["Close"].iloc[-1])
                prev_vix = float(vix_hist["Close"].iloc[0])
                vix_change = current_vix - prev_vix

                explanation.append(f"VIX: {current_vix:.2f} (Δ {vix_change:+.2f})")

                if vix_change > 2:
                    score += 0.05  # Fear rising sharply → risk-off → bullish gold
                    explanation.append("→ Fear rising (risk-off, supports gold)")
                elif vix_change < -2:
                    score -= 0.05  # Fear collapsing → risk-on → mild headwind
                    explanation.append("→ Fear falling (risk-on, slight headwind)")
        except Exception as e:
            explanation.append(f"VIX error: {e}")

        # ES futures (forward-looking risk sentiment)
        try:
            es_data = self.data_fetcher.fetch_es_futures()
            if es_data:
                es_change = es_data["change_pct"]
                sentiment = es_data["sentiment"]
                explanation.append(
                    f"ES Futures: {es_change:+.2f}% ({sentiment}, forward-looking)"
                )

                if sentiment == "risk_off" and es_change < -1.0:
                    score += 0.06  # Strong risk-off
                    explanation.append("→ Strong risk-off (supports gold)")
                elif sentiment == "risk_off":
                    score += 0.03
                    explanation.append("→ Mild risk-off (mildly bullish gold)")
                elif sentiment == "risk_on" and es_change > 1.0:
                    score -= 0.04
                    explanation.append("→ Strong risk-on (headwind for gold)")
        except Exception as e:
            explanation.append(f"ES futures error: {e}")

        # Clip
        score = max(min(score, 0.12), -0.12)
        return score, "\n".join(explanation)

    def analyze_calendar(self):
        """Use economic calendar (FMP) to assess event risk.

        High-impact upcoming events reduce confidence (uncertainty).
        Directional effect is small; the main role is confidence penalty.

        Returns:
            (directional_score, explanation, risk_level)
        """
        calendar_fmp = self.data_fetcher.fetch_economic_calendar_fmp(days_ahead=3)
        if not calendar_fmp:
            return 0.0, "Economic calendar: unavailable (manual check recommended)", "LOW"

        risk_level = calendar_fmp.get("risk_level", "LOW")
        event_count = calendar_fmp.get("high_impact_count", 0)

        explanation_lines = [
            f"Risk Level: {risk_level}",
            f"High-impact events (next 3 days): {event_count}",
        ]

        major_events = calendar_fmp.get("major_events") or []
        if major_events:
            ev = major_events[0]
            explanation_lines.append(
                f"Next major: {ev.get('event', 'N/A')} ({ev.get('country', 'N/A')})"
            )

        # Small directional bias: more risk → small negative score (encourages caution)
        if risk_level == "HIGH":
            calendar_score = -0.03
            explanation_lines.append("→ HIGH event risk (reduced conviction)")
        elif risk_level == "MEDIUM":
            calendar_score = -0.01
            explanation_lines.append("→ MEDIUM event risk")
        else:
            calendar_score = 0.0
            explanation_lines.append("→ LOW event risk")

        return calendar_score, "\n".join(explanation_lines), risk_level

    def analyze_gold_session_and_day(self):
        now_utc = datetime.utcnow()
        weekday = now_utc.weekday()
        hour = now_utc.hour

        confidence_multiplier = 1.0
        explanation_parts = []

        if weekday == 0:
            confidence_multiplier *= 0.95
            explanation_parts.append("Monday: slower, positioning/adjustment flows → -5% conviction")
        elif weekday in (1, 2, 3):
            confidence_multiplier *= 1.05
            explanation_parts.append("Tuesday–Thursday: prime days for gold trends → +5% conviction")
        elif weekday == 4:
            confidence_multiplier *= 0.95
            explanation_parts.append("Friday: profit-taking and weekend flatting → -5% conviction")
            if hour >= 18:
                confidence_multiplier *= 0.90
                explanation_parts.append("Late Friday US session (post 18:00 UTC): higher reversal risk → additional -10% conviction")

        if not explanation_parts:
            explanation_parts.append("Day-of-week effect: neutral")

        return confidence_multiplier, "\n".join(explanation_parts)

    # ------------------------------------------------------------------
    # PREDICTION ENGINE
    # ------------------------------------------------------------------
    def generate_prediction(self):
        """Generate a complete gold prediction for the next 24-48 hours."""
        hist = self.fetch_gold_history()
        if hist is None:
            return None

        technical = self.calculate_technical_indicators(hist)

        print("=" * 80)
        print("📈 ANALYSIS BREAKDOWN (GOLD / XAUUSD)")
        print("=" * 80 + "\n")

        scores = {}

        # 1. Price action (30%)
        price_score, price_exp = self.analyze_price_action(technical)
        scores["price_action"] = price_score * 10 * 0.30
        print("🥇 Price Action (30% weight):")
        print("   " + price_exp.replace("\n", "\n   ") + "\n")
        print(
            f"   Base Score: {price_score:+.3f} → Amplified: {price_score*10:+.3f} → Weighted: {scores['price_action']:+.3f}\n"
        )

        # 1b. Candlestick patterns (10%)
        candle_score, candle_exp = self.analyze_candles(hist)
        scores["candles"] = candle_score * 10 * 0.10
        print("🕯️ Candles (10% weight):")
        print("   " + candle_exp.replace("\n", "\n   ") + "\n")
        print(
            f"   Base Score: {candle_score:+.3f} → Amplified: {candle_score*10:+.3f} → Weighted: {scores['candles']:+.3f}\n"
        )

        # 2. Yields (20%)
        y_score, y_exp = self.analyze_yields()
        scores["yields"] = y_score * 10 * 0.20
        print("📉 10Y Yields (20% weight):")
        print("   " + y_exp.replace("\n", "\n   ") + "\n")
        print(
            f"   Base Score: {y_score:+.3f} → Amplified: {y_score*10:+.3f} → Weighted: {scores['yields']:+.3f}\n"
        )

        # 3. DXY (15%)
        dxy_score, dxy_exp = self.analyze_dxy()
        scores["dxy"] = dxy_score * 10 * 0.15
        print("💵 Dollar Index (15% weight):")
        print("   " + dxy_exp.replace("\n", "\n   ") + "\n")
        print(
            f"   Base Score: {dxy_score:+.3f} → Amplified: {dxy_score*10:+.3f} → Weighted: {scores['dxy']:+.3f}\n"
        )

        # 4. Risk sentiment (15%)
        risk_score, risk_exp = self.analyze_risk_sentiment()
        scores["risk_sentiment"] = risk_score * 10 * 0.15
        print("🌍 Risk Sentiment (15% weight):")
        print("   " + risk_exp.replace("\n", "\n   ") + "\n")
        print(
            f"   Base Score: {risk_score:+.3f} → Amplified: {risk_score*10:+.3f} → Weighted: {scores['risk_sentiment']:+.3f}\n"
        )

        # 5. Economic calendar (10%)
        cal_score, cal_exp, cal_risk = self.analyze_calendar()
        scores["calendar"] = cal_score * 10 * 0.10
        print("📅 Economic Calendar (10% weight):")
        print("   " + cal_exp.replace("\n", "\n   ") + "\n")
        print(
            f"   Base Score: {cal_score:+.3f} → Amplified: {cal_score*10:+.3f} → Weighted: {scores['calendar']:+.3f}\n"
        )

        # Total score
        total_score = sum(scores.values())

        print("=" * 80)
        print("🎯 PREDICTION CALCULATION (GOLD)")
        print("=" * 80 + "\n")

        print("📊 Component Scores:")
        for name, val in scores.items():
            print(f"   {name}: {val:+.3f}")
        print("   " + "-" * 40)
        print(f"   TOTAL: {total_score:+.3f}\n")

        # Direction thresholds (symmetric)
        threshold = 0.08
        abs_score = abs(total_score)

        if total_score >= threshold:
            direction = "UP"
        elif total_score <= -threshold:
            direction = "DOWN"
        else:
            direction = "NEUTRAL"

        # Confidence: honest, symmetric around 50%
        if abs_score < 0.01:
            confidence_base = 50.0
        elif abs_score < 0.15:
            # 50% → ~84% over 0.01–0.15
            confidence_base = 50.0 + (abs_score * 230.0)
        else:
            # Above 0.15, slower ramp up toward 95%
            confidence_base = 84.5 + (abs_score - 0.15) * 100.0

        confidence_base = min(confidence_base, 95.0)

        # For neutral calls, cap confidence so system doesn't sound overconfident
        if direction == "NEUTRAL":
            confidence_base = min(confidence_base, 60.0)

        # Session multiplier (reuse FX session logic for liquidity timing)
        session_info = self.data_fetcher.get_session_strategy()
        confidence = confidence_base * session_info["confidence_multiplier"]

        day_conf_mult, day_exp = self.analyze_gold_session_and_day()
        confidence *= day_conf_mult

        # Calendar risk penalty
        if cal_risk == "HIGH":
            confidence *= 0.90
        elif cal_risk == "MEDIUM":
            confidence *= 0.95

        confidence = max(40.0, min(confidence, 95.0))

        # ATR-based target & stop (USD)
        current_price = technical["current_price"]
        atr = technical["atr"] or self.config["typical_daily_range"]

        if confidence >= 75:
            target_atr = 2.5
            position_size = 100
        elif confidence >= 65:
            target_atr = 2.0
            position_size = 75
        elif confidence >= 55:
            target_atr = 1.5
            position_size = 50
        else:
            target_atr = 0.0
            position_size = 0

        target_dollars = atr * target_atr
        stop_dollars = target_dollars / 2 if target_dollars > 0 else 0.0

        if direction == "UP" and target_dollars > 0:
            target_price = current_price + target_dollars
            stop_price = current_price - stop_dollars
        elif direction == "DOWN" and target_dollars > 0:
            target_price = current_price - target_dollars
            stop_price = current_price + stop_dollars
        else:
            target_price = current_price
            stop_price = current_price

        risk_reward = (target_dollars / stop_dollars) if stop_dollars > 0 else 0.0

        print("=" * 80)
        print("🎯 PREDICTION RESULT (GOLD)")
        print("=" * 80 + "\n")
        print(f"📍 Direction: {direction}")
        print(f"🎲 Confidence: {confidence:.1f}%")
        print(f"💰 Current Price: {current_price:.2f} USD")
        if direction != "NEUTRAL" and target_dollars > 0:
            print(f"🎯 Target: {target_price:.2f} USD (Δ {target_dollars:+.2f})")
            print(f"🛑 Stop Loss: {stop_price:.2f} USD (Δ {stop_dollars:+.2f})")
            print(f"📊 Risk:Reward: 1:{risk_reward:.1f}")
            print(f"📏 Position Size: {position_size}% of normal")
        else:
            print("ℹ️ No strong edge → treat as NEUTRAL / SKIP")

        print(f"📈 Score: {total_score:+.3f}")
        print("⏰ Hold Period: 24-48 hours")

        print("\n" + "=" * 80)
        print("💡 RECOMMENDATION (GOLD / XAUUSD)")
        print("=" * 80 + "\n")

        if direction == "NEUTRAL" or confidence < self.config["min_confidence"]:
            print("   ❌ LOW CONFIDENCE - Skip or wait for better setup")
        elif confidence >= 75:
            print("   ✅ HIGH CONFIDENCE - Strong setup (full size)")
        elif confidence >= 65:
            print("   ⚠️ MODERATE CONFIDENCE - 75% size, manage risk")
        else:
            print("   ⚙️ LOW/MEDIUM CONFIDENCE - 50% size test trade")

        print("\n" + "=" * 80 + "\n")

        try:
            self.plot_gold_chart(hist)
        except Exception as e:
            print(f"⚠️ Chart error: {e}")

        return {
            "symbol": self.symbol,
            "direction": direction,
            "confidence": confidence,
            "current_price": current_price,
            "target_price": target_price,
            "stop_price": stop_price,
            "risk_reward": risk_reward,
            "position_size": position_size,
            "score": total_score,
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        }


if __name__ == "__main__":
    predictor = GoldDailyPredictor()
    prediction = predictor.generate_prediction()

    if prediction:
        print("✅ Gold prediction generated successfully!")
        print(f"   Direction: {prediction['direction']}")
        print(f"   Confidence: {prediction['confidence']:.1f}%")
        print(f"   Position Size: {prediction['position_size']}%")
    else:
        print("❌ Failed to generate gold prediction")
