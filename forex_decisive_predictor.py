#!/usr/bin/env python3
"""
Forex DECISIVE Predictor - Makes Actionable Calls
Based on signal hierarchy and tiebreaker logic

Key Differences from Standard Predictor:
1. Signal Hierarchy: Leading indicators (futures, options) weighted 2x
2. Lower Thresholds: 0.03 score (vs 0.08), 50% confidence (vs 65%)
3. Tiebreaker Logic: Uses support/resistance bias, momentum
4. Position Sizing: Scales with confidence (50-100%)
5. MAKES CALLS instead of always saying "skip"

Author: Decisive Trading System
Created: October 23, 2025
"""

from forex_daily_predictor import ForexDailyPredictor
import sys

class ForexDecisivePredictor(ForexDailyPredictor):
    """
    Decisive forex predictor - makes actionable calls
    """
    
    def __init__(self, pair='EUR/USD'):
        super().__init__(pair)
        print("\n🔥 DECISIVE MODE ACTIVATED")
        print("=" * 80)
        print("💪 Philosophy: Trust leading signals, make decisive calls")
        print("🎯 Goal: Actionable predictions, not just caution")
        print("=" * 80)
    
    def classify_signals(self, scores, technical_data):
        """
        Classify signals into Tier 1 (Leading), Tier 2 (Confirming), Tier 3 (Sentiment)
        """
        
        # TIER 1: Leading Indicators (predict future)
        tier1_signals = {
            'dxy': scores.get('dxy', 0),
            'risk_sentiment': scores.get('risk_sentiment', 0),
            'currency_strength': scores.get('currency_strength', 0),
            'multi_timeframe': scores.get('multi_timeframe', 0),
        }
        
        # TIER 2: Confirming Indicators (validate trends)
        tier2_signals = {
            'technical': scores.get('technical', 0),
            'support_resistance': scores.get('support_resistance', 0),
            'pivots': scores.get('pivots', 0),
            'trend_strength': scores.get('trend_strength', 0),
            'volume_profile': scores.get('volume_profile', 0),
        }
        
        # TIER 3: Sentiment Indicators (contrarian use)
        tier3_signals = {
            'news_sentiment': scores.get('news_sentiment', 0),
            'av_news': scores.get('av_news', 0),
        }
        
        # Fundamental (always important)
        fundamental = {
            'interest_rates': scores.get('interest_rates', 0),
            'gold': scores.get('gold', 0),
            '10y_yield': scores.get('10y_yield', 0),
        }
        
        return tier1_signals, tier2_signals, tier3_signals, fundamental
    
    def apply_decisive_logic(self, scores, total_score, technical_data):
        """
        Apply decisive tiebreaker logic when signals conflict
        """
        
        print(f"\n{'='*80}")
        print(f"🎯 DECISIVE ANALYSIS")
        print(f"{'='*80}\n")
        
        # Classify signals
        tier1, tier2, tier3, fundamental = self.classify_signals(scores, technical_data)
        
        # Analyze Tier 1 (most important)
        tier1_bullish = sum(1 for v in tier1.values() if v > 0.005)
        tier1_bearish = sum(1 for v in tier1.values() if v < -0.005)
        tier1_total = sum(tier1.values())
        
        print(f"📊 TIER 1 (Leading Indicators):")
        for name, score in tier1.items():
            print(f"   {name}: {score:+.3f}")
        print(f"   Bullish: {tier1_bullish}, Bearish: {tier1_bearish}")
        print(f"   Total: {tier1_total:+.3f}")
        
        # Analyze Tier 2
        tier2_total = sum(tier2.values())
        print(f"\n📊 TIER 2 (Confirming Indicators):")
        print(f"   Total: {tier2_total:+.3f}")
        
        # Support/Resistance bias
        current_price = technical_data['current_price']
        sr_bias = 0.0
        
        if scores.get('support_resistance', 0) > 0.015:
            sr_bias = 0.02  # Near support = bullish bias
            print(f"   ✅ Near support → +0.02 bullish bias")
        elif scores.get('support_resistance', 0) < -0.015:
            sr_bias = -0.02  # Near resistance = bearish bias  
            print(f"   ⚠️ Near resistance → -0.02 bearish bias")
        
        # RSI extreme bias
        rsi = technical_data['rsi']
        rsi_bias = 0.0
        
        if rsi < 35:
            rsi_bias = 0.015  # Oversold = bullish bias
            print(f"   ✅ RSI {rsi:.1f} oversold → +0.015 bullish bias")
        elif rsi > 65:
            rsi_bias = -0.015  # Overbought = bearish bias
            print(f"   ⚠️ RSI {rsi:.1f} overbought → -0.015 bearish bias")
        
        # Decisive Score = Tier1 (2x weight) + Tier2 + biases
        decisive_score = (tier1_total * 2.0) + tier2_total + sr_bias + rsi_bias + sum(fundamental.values())
        
        print(f"\n💪 DECISIVE CALCULATION:")
        print(f"   Tier 1 (2x weight): {tier1_total:+.3f} × 2 = {tier1_total*2:+.3f}")
        print(f"   Tier 2:             {tier2_total:+.3f}")
        print(f"   S/R Bias:           {sr_bias:+.3f}")
        print(f"   RSI Bias:           {rsi_bias:+.3f}")
        print(f"   Fundamental:        {sum(fundamental.values()):+.3f}")
        print(f"   ─────────────────────────────")
        print(f"   DECISIVE SCORE:     {decisive_score:+.3f}")
        
        # Determine confidence based on signal alignment
        if tier1_bullish > tier1_bearish and tier2_total > 0:
            confidence_boost = 10  # Aligned signals
            print(f"   ✅ Tier 1 & 2 aligned → +10% confidence")
        elif tier1_bearish > tier1_bullish and tier2_total < 0:
            confidence_boost = 10
            print(f"   ✅ Tier 1 & 2 aligned → +10% confidence")
        else:
            confidence_boost = 0
            print(f"   ⚠️ Mixed signals → no confidence boost")
        
        return decisive_score, confidence_boost
    
    def generate_decisive_prediction(self):
        """
        Generate prediction with decisive logic
        """
        
        # Get standard prediction first
        hist = self.fetch_forex_data()
        if hist is None:
            return None
        
        print(f"📊 Analyzing {self.pair}...")
        technical_data = self.calculate_technical_indicators(hist)
        
        print(f"\n{'='*80}")
        print(f"📈 ANALYSIS BREAKDOWN")
        print(f"{'='*80}\n")
        
        # Get all component scores (same as parent)
        scores = {}
        
        # Run all analyses
        rate_score, rate_exp = self.analyze_interest_rates()
        scores['interest_rates'] = rate_score * 10 * 0.20
        
        tech_score, tech_exp = self.analyze_technical(technical_data)
        scores['technical'] = tech_score * 10 * 0.18
        
        dxy_score, dxy_exp = self.analyze_dxy()
        scores['dxy'] = dxy_score * 10 * 0.12
        
        risk_score, risk_exp = self.analyze_risk_sentiment()
        scores['risk_sentiment'] = risk_score * 10 * 0.12
        
        gold_score, gold_exp = self.analyze_gold_correlation()
        scores['gold'] = gold_score * 10 * 0.07
        
        yield_score, yield_exp = self.analyze_10y_yield()
        scores['10y_yield'] = yield_score * 10 * 0.07
        
        sr_score, sr_exp, sr_data = self.analyze_support_resistance(hist)
        scores['support_resistance'] = sr_score * 10 * 0.05
        
        pivot_score, pivot_exp = self.analyze_pivot_points(hist)
        scores['pivots'] = pivot_score * 10 * 0.05
        
        # Get session info
        session_info = self.data_fetcher.get_session_strategy()
        
        # Additional components (simplified for decisive mode)
        currency_strength = self.data_fetcher.calculate_currency_strength()
        if currency_strength:
            base, quote = 'EUR', 'USD' if self.pair == 'EUR/USD' else ('GBP', 'USD')
            base_strength = currency_strength['strengths'].get(base, 0)
            quote_strength = currency_strength['strengths'].get(quote, 0)
            strength_diff = (base_strength - quote_strength) / 10
            strength_score = min(max(strength_diff, -0.10), 0.10)
            scores['currency_strength'] = strength_score * 10 * 0.05
        else:
            scores['currency_strength'] = 0
        
        mtf = self.data_fetcher.multi_timeframe_confirmation(self.symbol)
        if mtf:
            if mtf['alignment'] == 'bullish' and mtf['strength'] == 'strong':
                mtf_score = 0.10
            elif mtf['alignment'] == 'bearish' and mtf['strength'] == 'strong':
                mtf_score = -0.10
            elif mtf['alignment'] == 'bullish':
                mtf_score = 0.05
            elif mtf['alignment'] == 'bearish':
                mtf_score = -0.05
            else:
                mtf_score = 0.0
            scores['multi_timeframe'] = mtf_score * 10 * 0.06
        else:
            scores['multi_timeframe'] = 0
        
        # Calculate standard total
        total_score = sum(scores.values())
        
        # Apply DECISIVE LOGIC
        decisive_score, confidence_boost = self.apply_decisive_logic(scores, total_score, technical_data)
        
        # DECISIVE THRESHOLDS (much lower!)
        print(f"\n{'='*80}")
        print(f"🎯 DECISIVE DETERMINATION")
        print(f"{'='*80}\n")
        
        if decisive_score >= 0.03:  # Lowered from 0.08!
            direction = "BUY"
            # Piecewise confidence with boost
            if abs(decisive_score) < 0.10:
                confidence_base = 50 + abs(decisive_score) * 300
            else:
                confidence_base = 80 + (abs(decisive_score) - 0.10) * 100
        elif decisive_score <= -0.03:  # Lowered from -0.08!
            direction = "SELL"
            if abs(decisive_score) < 0.10:
                confidence_base = 50 + abs(decisive_score) * 300
            else:
                confidence_base = 80 + (abs(decisive_score) - 0.10) * 100
        else:
            direction = "NEUTRAL"
            confidence_base = 45 + abs(decisive_score) * 500
        
        # Add confidence boost
        confidence = min(confidence_base + confidence_boost, 95)
        
        # Apply session multiplier
        confidence *= session_info['confidence_multiplier']
        confidence = min(confidence, 95)
        
        print(f"📍 Direction: {direction}")
        print(f"📊 Decisive Score: {decisive_score:+.3f}")
        print(f"🎲 Base Confidence: {confidence_base:.1f}%")
        print(f"✨ Boost: +{confidence_boost}%")
        print(f"🎯 Final Confidence: {confidence:.1f}%")
        
        # Calculate targets
        current_price = technical_data['current_price']
        daily_pips = self.config['typical_daily_pips']
        pip_value = self.config['pip_value']
        
        # Position sizing based on confidence
        if confidence >= 70:
            position_size = 100  # Full size
            target_pips = int(daily_pips * 1.0)
        elif confidence >= 60:
            position_size = 75  # 3/4 size
            target_pips = int(daily_pips * 0.75)
        elif confidence >= 50:
            position_size = 50  # Half size
            target_pips = int(daily_pips * 0.5)
        else:
            position_size = 0
            target_pips = 0
        
        stop_pips = int(target_pips / 2)  # 2:1 R:R
        
        if direction == "BUY":
            target_price = current_price + (target_pips * pip_value)
            stop_price = current_price - (stop_pips * pip_value)
        elif direction == "SELL":
            target_price = current_price - (target_pips * pip_value)
            stop_price = current_price + (stop_pips * pip_value)
        else:
            target_price = current_price
            stop_price = current_price
        
        # Output
        print(f"\n{'='*80}")
        print(f"🎯 DECISIVE PREDICTION RESULT")
        print(f"{'='*80}\n")
        
        print(f"📍 Direction: {direction}")
        print(f"🎲 Confidence: {confidence:.1f}%")
        print(f"💰 Current Price: {current_price:.4f}")
        
        if direction != "NEUTRAL":
            print(f"🎯 Target: {target_price:.4f} ({target_pips:+d} pips)")
            print(f"🛑 Stop Loss: {stop_price:.4f} ({stop_pips:+d} pips)")
            print(f"📊 Risk:Reward: 1:{target_pips/stop_pips:.1f}")
            print(f"📏 Position Size: {position_size}% of normal")
        
        print(f"📈 Decisive Score: {decisive_score:+.3f}")
        print(f"⏰ Hold Period: 24-48 hours")
        
        print(f"\n{'='*80}")
        print(f"💡 DECISIVE RECOMMENDATION")
        print(f"{'='*80}\n")
        
        if confidence >= 70:
            print(f"   ✅ HIGH CONFIDENCE - Full position")
        elif confidence >= 60:
            print(f"   ⚠️ MODERATE CONFIDENCE - 75% position")
        elif confidence >= 50:
            print(f"   ⚙️ LOW CONFIDENCE - 50% position (test trade)")
        else:
            print(f"   ❌ VERY LOW CONFIDENCE - Skip this one")
        
        print(f"\n{'='*80}\n")
        
        return {
            'pair': self.pair,
            'direction': direction,
            'confidence': confidence,
            'current_price': current_price,
            'target': target_price,
            'stop_loss': stop_price,
            'target_pips': target_pips if direction != "NEUTRAL" else 0,
            'stop_pips': stop_pips if direction != "NEUTRAL" else 0,
            'risk_reward': target_pips / stop_pips if stop_pips > 0 else 0,
            'position_size': position_size,
            'score': decisive_score,
            'timestamp': self.data_fetcher.__dict__.get('timestamp', 'N/A')
        }

def predict_forex_decisive(pair='EUR/USD'):
    """Run decisive forex prediction"""
    predictor = ForexDecisivePredictor(pair)
    return predictor.generate_decisive_prediction()

if __name__ == "__main__":
    # Run decisive prediction for EUR/USD
    prediction = predict_forex_decisive('EUR/USD')
    
    if prediction:
        print(f"✅ Decisive prediction generated!")
        print(f"   Direction: {prediction['direction']}")
        print(f"   Confidence: {prediction['confidence']:.1f}%")
        print(f"   Position Size: {prediction['position_size']}%")
    else:
        print(f"❌ Failed to generate prediction")
