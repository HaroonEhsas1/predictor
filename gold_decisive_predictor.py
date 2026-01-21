#!/usr/bin/env python3
"""
Gold DECISIVE Predictor - Makes Actionable Calls for XAUUSD

Based on the same components as GoldDailyPredictor but with:
- Emphasis on leading macro signals (yields, DXY, risk sentiment)
- Lower thresholds → more trades
- Extra tiebreaker logic using RSI / extension
- Position sizing scaled by confidence
"""

from datetime import datetime

from gold_daily_predictor import GoldDailyPredictor


class GoldDecisivePredictor(GoldDailyPredictor):
    """Decisive gold predictor for XAUUSD using GC futures as proxy."""

    def __init__(self):
        super().__init__()
        print("\n🔥 GOLD DECISIVE MODE ACTIVATED")
        print("=" * 80)
        print("💪 Philosophy: Trust leading macro + price signals, make decisive calls")
        print("🎯 Goal: More actionable gold trades, not just caution")
        print("=" * 80)

    def classify_signals(self, scores):
        """Classify signals into tiers for decisive logic."""
        tier1 = {
            "yields": scores.get("yields", 0.0),
            "dxy": scores.get("dxy", 0.0),
            "risk_sentiment": scores.get("risk_sentiment", 0.0),
        }

        tier2 = {
            "price_action": scores.get("price_action", 0.0),
            "candles": scores.get("candles", 0.0),
        }

        tier3 = {
            "calendar": scores.get("calendar", 0.0),
        }

        return tier1, tier2, tier3

    def apply_decisive_logic(self, scores, technical):
        """Apply decisive tiebreaker logic on top of component scores."""
        print("\n" + "=" * 80)
        print("🎯 DECISIVE ANALYSIS (GOLD)")
        print("=" * 80 + "\n")

        tier1, tier2, tier3 = self.classify_signals(scores)

        tier1_total = sum(tier1.values())
        tier2_total = sum(tier2.values())

        tier1_bullish = sum(1 for v in tier1.values() if v > 0.0)
        tier1_bearish = sum(1 for v in tier1.values() if v < 0.0)

        print("📊 TIER 1 (Leading Macro):")
        for name, val in tier1.items():
            print(f"   {name}: {val:+.3f}")
        print(f"   Bullish: {tier1_bullish}, Bearish: {tier1_bearish}")
        print(f"   Total: {tier1_total:+.3f}\n")

        print("📊 TIER 2 (Price Action):")
        print(f"   price_action: {tier2_total:+.3f}\n")

        # Biases from current RSI and extension vs 50 MA
        rsi = technical["rsi"]
        current_price = technical["current_price"]
        ma_50 = technical["ma_50"]
        ma_distance_pct = ((current_price - ma_50) / ma_50) * 100 if ma_50 else 0.0

        rsi_bias = 0.0
        extension_bias = 0.0

        if rsi < 35:
            rsi_bias = 0.02
            print(f"   ✅ RSI {rsi:.1f} oversold → +0.02 bullish bias")
        elif rsi > 65:
            rsi_bias = -0.02
            print(f"   ⚠️ RSI {rsi:.1f} overbought → -0.02 bearish bias")

        if ma_distance_pct > 5.0:
            extension_bias = -0.02
            print(f"   ⚠️ +{ma_distance_pct:.1f}% above 50-MA → -0.02 mean-reversion bias")
        elif ma_distance_pct < -5.0:
            extension_bias = 0.02
            print(f"   ✅ {ma_distance_pct:.1f}% below 50-MA → +0.02 bounce bias")

        decisive_score = (tier1_total * 2.0) + tier2_total + rsi_bias + extension_bias

        print("\n💪 DECISIVE CALCULATION (GOLD):")
        print(f"   Tier 1 (2x): {tier1_total:+.3f} × 2 = {tier1_total * 2:+.3f}")
        print(f"   Tier 2:      {tier2_total:+.3f}")
        print(f"   RSI Bias:    {rsi_bias:+.3f}")
        print(f"   Ext Bias:    {extension_bias:+.3f}")
        print("   " + "-" * 28)
        print(f"   DECISIVE:    {decisive_score:+.3f}")

        # Alignment-based confidence boost
        if tier1_bullish > tier1_bearish and tier2_total > 0:
            confidence_boost = 8.0
            print("   ✅ Tier 1 & price action aligned bullish → +8% confidence")
        elif tier1_bearish > tier1_bullish and tier2_total < 0:
            confidence_boost = 8.0
            print("   ✅ Tier 1 & price action aligned bearish → +8% confidence")
        else:
            confidence_boost = 0.0
            print("   ⚠️ Mixed signals → no alignment boost")

        return decisive_score, confidence_boost

    def generate_decisive_prediction(self):
        """Generate decisive prediction for gold (XAUUSD)."""
        hist = self.fetch_gold_history()
        if hist is None:
            return None

        technical = self.calculate_technical_indicators(hist)

        print("\n" + "=" * 80)
        print("📈 ANALYSIS BREAKDOWN (DECISIVE GOLD)")
        print("=" * 80 + "\n")

        scores = {}

        # Reuse same component analyses as standard gold predictor
        price_score, price_exp = self.analyze_price_action(technical)
        scores["price_action"] = price_score * 10 * 0.30
        print("🥇 Price Action (30% weight):")
        print("   " + price_exp.replace("\n", "\n   ") + "\n")

        candle_score, candle_exp = self.analyze_candles(hist)
        scores["candles"] = candle_score * 10 * 0.10
        print("🕯️ Candles (10% weight):")
        print("   " + candle_exp.replace("\n", "\n   ") + "\n")

        y_score, y_exp = self.analyze_yields()
        scores["yields"] = y_score * 10 * 0.20
        print("📉 10Y Yields (20% weight):")
        print("   " + y_exp.replace("\n", "\n   ") + "\n")

        dxy_score, dxy_exp = self.analyze_dxy()
        scores["dxy"] = dxy_score * 10 * 0.15
        print("💵 Dollar Index (15% weight):")
        print("   " + dxy_exp.replace("\n", "\n   ") + "\n")

        risk_score, risk_exp = self.analyze_risk_sentiment()
        scores["risk_sentiment"] = risk_score * 10 * 0.15
        print("🌍 Risk Sentiment (15% weight):")
        print("   " + risk_exp.replace("\n", "\n   ") + "\n")

        cal_score, cal_exp, cal_risk = self.analyze_calendar()
        scores["calendar"] = cal_score * 10 * 0.10
        print("📅 Economic Calendar (10% weight):")
        print("   " + cal_exp.replace("\n", "\n   ") + "\n")

        # Apply decisive logic on top of these component scores
        decisive_score, confidence_boost = self.apply_decisive_logic(scores, technical)

        # Lower thresholds than standard mode
        threshold = 0.04
        abs_decisive = abs(decisive_score)

        print("\n" + "=" * 80)
        print("🎯 DECISIVE DETERMINATION (GOLD)")
        print("=" * 80 + "\n")

        if decisive_score >= threshold:
            direction = "UP"
            if abs_decisive < 0.12:
                confidence_base = 50.0 + abs_decisive * 320.0
            else:
                confidence_base = 80.0 + (abs_decisive - 0.12) * 120.0
        elif decisive_score <= -threshold:
            direction = "DOWN"
            if abs_decisive < 0.12:
                confidence_base = 50.0 + abs_decisive * 320.0
            else:
                confidence_base = 80.0 + (abs_decisive - 0.12) * 120.0
        else:
            direction = "NEUTRAL"
            confidence_base = 45.0 + abs_decisive * 400.0

        confidence_base = min(confidence_base, 95.0)

        # Add alignment boost
        confidence = confidence_base + confidence_boost

        # Session multiplier
        session_info = self.data_fetcher.get_session_strategy()
        confidence *= session_info["confidence_multiplier"]

        day_conf_mult, day_exp = self.analyze_gold_session_and_day()
        confidence *= day_conf_mult

        # Calendar risk penalty
        if cal_risk == "HIGH":
            confidence *= 0.90
        elif cal_risk == "MEDIUM":
            confidence *= 0.95

        confidence = max(40.0, min(confidence, 95.0))

        print(f"📍 Direction: {direction}")
        print(f"📊 Decisive Score: {decisive_score:+.3f}")
        print(f"🎲 Base Confidence: {confidence_base:.1f}%")
        print(f"✨ Boost: +{confidence_boost:.1f}%")
        print(f"🎯 Final Confidence: {confidence:.1f}%")

        # ATR-based targets and sizing (reuse logic style from standard predictor)
        current_price = technical["current_price"]
        atr = technical["atr"] or self.config["typical_daily_range"]

        if confidence >= 70:
            target_atr = 2.0
            position_size = 100
        elif confidence >= 60:
            target_atr = 1.5
            position_size = 75
        elif confidence >= 50:
            target_atr = 1.0
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

        print("\n" + "=" * 80)
        print("🎯 DECISIVE PREDICTION RESULT (GOLD)")
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
            print("ℹ️ No strong decisive edge → treat as NEUTRAL / SKIP")

        print(f"📈 Decisive Score: {decisive_score:+.3f}")
        print("⏰ Hold Period: 24-48 hours")

        print("\n" + "=" * 80)
        print("💡 GOLD DECISIVE RECOMMENDATION")
        print("=" * 80 + "\n")

        if direction == "NEUTRAL" or confidence < 50.0:
            print("   ❌ VERY LOW CONFIDENCE - Skip this one")
        elif confidence >= 70.0:
            print("   ✅ HIGH CONFIDENCE - Full position")
        elif confidence >= 60.0:
            print("   ⚠️ MODERATE CONFIDENCE - 75% position")
        else:
            print("   ⚙️ LOW CONFIDENCE - 50% position (test trade)")

        print("\n" + "=" * 80 + "\n")

        try:
            self.plot_gold_chart(hist, filename="gold_chart_decisive.png")
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
            "score": decisive_score,
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        }


def predict_gold_decisive():
    """Convenience wrapper to run decisive gold prediction."""
    predictor = GoldDecisivePredictor()
    return predictor.generate_decisive_prediction()


if __name__ == "__main__":
    prediction = predict_gold_decisive()
    if prediction:
        print("✅ Gold decisive prediction generated!")
        print(f"   Direction: {prediction['direction']}")
        print(f"   Confidence: {prediction['confidence']:.1f}%")
        print(f"   Position Size: {prediction['position_size']}%")
    else:
        print("❌ Failed to generate decisive gold prediction")
