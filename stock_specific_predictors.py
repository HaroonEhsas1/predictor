"""
STOCK-SPECIFIC PREDICTION MODELS
Each stock gets its OWN independent predictor based on its UNIQUE patterns

USER INSIGHT: "Each stock should be independent - use its own patterns"
PROVEN: AMD 57% gaps vs AVGO 43% gaps - they ARE different!
"""

import json
import os


class BaseStockPredictor:
    """Base class for stock-specific predictors"""

    def __init__(self, symbol):
        self.symbol = symbol
        self.patterns = self._load_patterns() or {}

    def _load_patterns(self):
        """Load this stock's learned patterns"""
        filename = f"{self.symbol}_patterns.json"
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                return json.load(f)
        return None

    def predict(self, data):
        """Override in subclass"""
        raise NotImplementedError

    # ===== Shared helpers for all predictors =====
    def _dynamic_gap_threshold(self, base_min_gap, data):
        """Adjust minimum gap requirement by market regime & liquidity"""
        regime = (data.get('market_regime') or '').upper()
        vix = data.get('vix', 20)
        volume_ratio = data.get('volume_ratio', 1.0)

        regime_factor = {
            'LOW_VOL': 0.6,
            'NORMAL': 0.8,
            'ELEVATED': 0.9,
            'HIGH_VOL': 1.0
        }.get(regime, 0.85)

        # VIX fine-tuning
        if vix < 16:
            regime_factor *= 0.85
        elif vix > 28:
            regime_factor *= 1.05

        # Strong premarket participation allows slightly smaller gaps
        if volume_ratio > 1.3:
            regime_factor *= 0.85
        elif volume_ratio < 0.4:
            regime_factor *= 1.1

        dynamic_threshold = max(
            base_min_gap * regime_factor, base_min_gap * 0.4)
        return min(dynamic_threshold, base_min_gap * 1.25)

    def _macro_alignment_score(self, gap_pct, data):
        """Measure how well the broader tape supports the gap direction"""
        if gap_pct == 0:
            return 0.0
        direction_sign = 1 if gap_pct > 0 else -1
        references = []
        for key in ('spy_pct', 'nasdaq_pct'):
            val = data.get(key)
            if isinstance(val, (int, float)):
                references.append(val)
        # sector_alignment already bias-sized (~-0.3..0.3)
        sector_alignment = data.get('sector_alignment')
        if isinstance(sector_alignment, (int, float)):
            references.append(sector_alignment)

        if not references:
            return 0.0

        aligned = sum(1 for ref in references if direction_sign * ref > 0.0005)
        return aligned / len(references)

    def _scale_trap_penalty(self, penalty, gap_pct, data):
        """Reduce trap penalties when macro + sector agree with the move"""
        alignment = self._macro_alignment_score(gap_pct, data)
        # Allow up to 60% reduction when everything aligns
        reduction = penalty * 0.6 * alignment
        return penalty - reduction

    def _aligned_indicator_bias(self, gap_pct, indicator_bias):
        """Amplify supportive bias & dampen conflicting signals"""
        if not indicator_bias:
            return 0.0
        direction_sign = 1 if gap_pct > 0 else -1
        bias_sign = 1 if indicator_bias > 0 else -1
        magnitude = abs(indicator_bias)
        if direction_sign == bias_sign:
            return magnitude * 1.5
        return -magnitude * 0.5

    # ===== Pattern intelligence helpers =====
    def _get_pattern_stat(self, category, key, default=None):
        if not self.patterns:
            return default
        return (self.patterns.get(category) or {}).get(key, default)

    def _apply_pattern_context(self, confidence, data, gap_pct):
        """
        Blend pattern-derived stats (momentum, traps, intraday) into the current confidence.
        Returns the adjusted confidence and granular notes for debugging.
        """
        notes = []
        if not self.patterns:
            return confidence, notes

        trap_rate = self._get_pattern_stat('traps', 'trap_rate')
        if trap_rate is not None:
            adj = (0.5 - trap_rate) * 0.12
            if abs(adj) > 1e-3:
                confidence += adj
                bias = "lower" if adj < 0 else "higher"
                notes.append(f"Pattern trap rate ({trap_rate:.2f}) → {bias} base by {adj:+.2f}")

        continuation = self._get_pattern_stat('momentum', 'continuation_rate')
        if continuation is not None:
            adj = (continuation - 0.5) * 0.15
            if abs(adj) > 1e-3:
                confidence += adj
                notes.append(f"Momentum continuation {continuation:.2f} adds {adj:+.2f}")

        intraday = self.patterns.get('intraday', {})
        if intraday:
            if gap_pct > 0 and 'morning_strength_rate' in intraday:
                rate = intraday['morning_strength_rate']
                adj = (rate - 0.5) * 0.08
                if abs(adj) > 1e-3:
                    confidence += adj
                    notes.append(f"Morning strength {rate:.2f} adds {adj:+.2f} for gap up")
            if gap_pct < 0 and 'morning_fade_rate' in intraday:
                rate = intraday['morning_fade_rate']
                adj = (0.5 - rate) * 0.05
                if abs(adj) > 1e-3:
                    confidence += adj
                    notes.append(f"Morning fade {rate:.2f} adjusts {adj:+.2f} for gap down")

        return max(0.05, min(0.95, confidence)), notes


class AMDPredictor(BaseStockPredictor):
    """
    AMD-SPECIFIC PREDICTOR

    AMD's Unique Traits:
    - 57% gap follow-through (BEST!)
    - 43% trap rate (LOW)
    - Reliable gaps
    - Low morning fade (2%)

    Strategy: TRUST AMD's gaps more than others
    """

    def __init__(self):
        super().__init__('AMD')

        # AMD-SPECIFIC thresholds (learned from data)
        self.gap_trust = self._get_pattern_stat(
            'gaps', 'follow_through_rate', 0.569)
        self.trap_risk = self._get_pattern_stat('traps', 'trap_rate', 0.431)
        avg_gap = self._get_pattern_stat('gaps', 'avg_gap_size', 1.5)
        # Pattern file stores % terms, convert to decimal for min gap
        self.min_gap = max(0.01, min(0.04, (avg_gap or 1.5) / 100))
        self.intraday_reversal_risk = self._get_pattern_stat(
            'intraday', 'morning_fade_rate', 0.455)

    def predict(self, data):
        """AMD-specific prediction logic"""

        gap_pct = data.get('gap_pct', 0)
        volume = data.get('volume', 0)
        min_volume = data.get('min_volume', 1000000)
        volume_ratio = data.get('volume_ratio', 0)
        breakdown = [f"Base follow-through {self.gap_trust:.2f}"]

        min_gap_required = self._dynamic_gap_threshold(self.min_gap, data)

        if abs(gap_pct) > min_gap_required:
            # Base confidence from AMD's actual follow-through rate
            base_confidence = self.gap_trust  # 57%

            # AMD is reliable, so volume confirmation adds more
            if volume > min_volume:
                base_confidence += 0.10
                breakdown.append("Premarket volume cleared threshold (+0.10)")
            elif volume_ratio and volume_ratio > 0.6:
                base_confidence += 0.04
                breakdown.append("Volume ratio > 0.6 (+0.04)")
            elif volume_ratio and volume_ratio < 0.2:
                base_confidence -= 0.05
                breakdown.append("Volume ratio < 0.2 (-0.05)")

            # AMD's traps are low, so we're less cautious
            trap_flag = data.get('trap_signals', False)
            ma_distance = data.get('ma_distance', 0.0)
            trap_risk = data.get('trap_risk_score', 0.0)
            if trap_flag:
                # Overbought + gap down is actually supportive, so ignore trap flag there
                if not (gap_pct < 0 and ma_distance > 0.1):
                    penalty = self._scale_trap_penalty(
                        0.12 + trap_risk * 0.2, gap_pct, data)
                    # Only -15% (vs -25% for others)
                    base_confidence -= penalty
                    breakdown.append(
                        f"Indicator trap penalty {penalty:-.2f} (risk {trap_risk:.2f})")

            # AMD-specific: Reddit/WallStreetBets hype detection
            # AMD is heavily retail-driven - excessive hype = reversal risk
            reddit_sentiment = data.get(
                'reddit_sentiment', data.get('social_sentiment', 0))

            if reddit_sentiment > 0.15:  # Excessive hype
                base_confidence -= 0.15  # AMD retail euphoria = fade signal
                breakdown.append("Retail euphoria detected (-0.15)")
            elif reddit_sentiment > 0.08:  # Moderate hype
                base_confidence -= 0.08  # Caution on retail enthusiasm
                breakdown.append("Retail enthusiasm (-0.08)")
            elif reddit_sentiment < -0.10:  # Excessive fear
                base_confidence += 0.08  # Contrarian: retail panic = opportunity
                breakdown.append("Retail fear contrarian boost (+0.08)")

            # AMD-specific: Options activity (retail loves AMD options)
            unusual_options = data.get('unusual_options_activity', False)
            if unusual_options:
                base_confidence += 0.10  # Smart money positioning
                breakdown.append("Unusual options activity (+0.10)")

            # Earnings proximity check - reduce confidence if close to earnings
            earnings_days_away = data.get('earnings_days_away', 999)
            if earnings_days_away <= 5:  # Within 5 days of earnings
                base_confidence -= 0.10  # Uncertainty penalty
                breakdown.append("Earnings within 5 days (-0.10)")
            elif earnings_days_away <= 2:  # Very close to earnings
                base_confidence -= 0.20  # High uncertainty
                breakdown.append("Earnings imminent (-0.20)")

            # Technical trend indicator - placeholder for trend strength (e.g., ADX)
            trend_strength = data.get(
                'trend_strength', 0)  # Assume 0 to 1 scale
            if trend_strength > 0.5:  # Strong trend
                if (gap_pct > 0 and trend_strength > 0) or (gap_pct < 0 and trend_strength < 0):
                    base_confidence += 0.08  # Trend confirmation
                    breakdown.append("Trend confirmation (+0.08)")
                else:
                    base_confidence -= 0.08  # Trend contradiction
                    breakdown.append("Trend contradiction (-0.08)")

            # News catalyst placeholder - simulate based on gap size and volume as proxy
            # Lowered threshold for news impact
            if abs(gap_pct) > 2.0 and volume > min_volume * 1.2:  # Adjusted from 3.0% and 1.5x
                if gap_pct > 0:
                    base_confidence += 0.12  # Positive news catalyst likely
                    breakdown.append("Gap + volume implies positive catalyst (+0.12)")
                else:
                    base_confidence -= 0.12  # Negative news catalyst likely
                    breakdown.append("Gap + volume implies negative catalyst (-0.12)")

            # Options flow placeholder - simulate unusual options activity based on volume
            if volume > min_volume * 1.5:
                base_confidence += 0.07  # Likely unusual options activity
                breakdown.append("Volume > 1.5x min (+0.07)")

            # Institutional buying placeholder - simulate based on high volume and positive gap
            if volume > min_volume * 1.3 and gap_pct > 1.0:
                base_confidence += 0.06  # Likely institutional buying
                breakdown.append("Institutional flow proxy (+0.06)")

            # Indicator/internals bias integration
            indicator_bias = data.get('indicator_bias', 0.0)
            base_confidence += self._aligned_indicator_bias(
                gap_pct, indicator_bias)
            if indicator_bias:
                breakdown.append(
                    f"Indicator bias contribution ({indicator_bias:+.2f})")
            trend_strength = data.get('trend_strength', 0.0)
            if trend_strength:
                base_confidence += 0.06 * trend_strength
                breakdown.append(
                    f"Trend strength contribution (+{0.06 * trend_strength:.2f})")
            sector_alignment = data.get('sector_alignment', 0.0)
            base_confidence += 0.05 * sector_alignment
            if sector_alignment:
                breakdown.append(
                    f"Sector alignment contribution (+{0.05 * sector_alignment:.2f})")

            if ma_distance > 0.12:
                if gap_pct < 0:
                    base_confidence += 0.05  # Overbought + gap down = favorable
                else:
                    base_confidence -= 0.08  # Overbought risk
                breakdown.append("MA distance adjustment applied")
            elif ma_distance < -0.12:
                base_confidence += 0.05  # Oversold bounce
                breakdown.append("Oversold MA distance (+0.05)")

            # ========== INTEGRATE NEWS SENTIMENT BOOST (Priority 1) ==========
            news_sentiment = data.get('news_sentiment', 0.0)
            news_boost = data.get('news_confidence_boost', 0.0)
            
            if news_boost > 0:
                # Apply boost if sentiment aligns with direction
                if (gap_pct > 0 and news_sentiment > 0) or (gap_pct < 0 and news_sentiment < 0):
                    base_confidence += news_boost
                    breakdown.append(f"News sentiment aligned ({news_sentiment:+.2f}) (+{news_boost:.2f})")
                elif abs(news_sentiment) > 0.3:
                    # Reduce boost if sentiment opposes direction
                    base_confidence -= news_boost * 0.5
                    breakdown.append(f"News sentiment conflicting ({news_sentiment:+.2f}) (-{news_boost * 0.5:.2f})")

            # Penalty for high intraday reversal risk
            reversal_penalty = self.intraday_reversal_risk * \
                0.1  # Scale down the penalty impact
            # Reduce confidence due to AMD's known reversal tendency
            base_confidence -= reversal_penalty
            breakdown.append(
                f"Intraday reversal risk penalty (-{reversal_penalty:.2f})")

            base_confidence, pattern_notes = self._apply_pattern_context(
                base_confidence, data, gap_pct)
            breakdown.extend(pattern_notes)

            base_confidence = max(0.05, min(0.95, base_confidence))

            direction = 'UP' if gap_pct > 0 else 'DOWN'

            # AMD-SPECIFIC WARNING
            exit_strategy = 'EXIT_AT_935AM' if base_confidence > 0.55 else 'SKIP'

            return {
                'symbol': 'AMD',
                'direction': direction,
                'confidence': min(base_confidence, 0.95),
                'exit_strategy': exit_strategy,
                'reason': f"AMD gap {abs(gap_pct)*100:.1f}% - {self.gap_trust*100:.0f}% follow-through rate",
                'warning': "⚠️ AMD reverses intraday 45.5% - EXIT AT 9:35 AM!",
                'confidence_breakdown': breakdown
            }

        return {
            'symbol': 'AMD',
            'direction': 'NEUTRAL',
            'confidence': 0.50,
            'reason': f"AMD gap {abs(gap_pct)*100:.1f}% below dynamic threshold {min_gap_required*100:.1f}%",
            'confidence_breakdown': breakdown
        }


class NVDAPredictor(BaseStockPredictor):
    """
    NVDA-SPECIFIC PREDICTOR

    NVDA's Unique Traits:
    - 47% gap follow-through (coin flip)
    - 53% trap rate (HIGH!)
    - Many fake-outs
    - Low morning fade (2%)

    Strategy: Be CAUTIOUS with NVDA gaps - require confirmation
    """

    def __init__(self):
        super().__init__('NVDA')

        # NVDA-SPECIFIC thresholds
        self.gap_trust = self._get_pattern_stat(
            'gaps', 'follow_through_rate', 0.50)
        self.trap_risk = self._get_pattern_stat('traps', 'trap_rate', 0.48)
        avg_gap = self._get_pattern_stat('gaps', 'avg_gap_size', 0.2)
        # Lower bound remains tiny for NVDA to capture small gaps
        self.min_gap = max(0.001, min(0.02, (avg_gap or 0.2) / 100))

    def predict(self, data):
        """NVDA-specific prediction logic"""

        gap_pct = data.get('gap_pct', 0)
        volume = data.get('volume', 0)
        min_volume = data.get('min_volume', 300000)
        volume_ratio = data.get('volume_ratio', 0)
        breakdown = [f"Base follow-through {self.gap_trust:.2f}"]

        min_gap_required = self._dynamic_gap_threshold(self.min_gap, data)

        if abs(gap_pct) > min_gap_required:
            # NVDA has WEAK gap follow-through
            base_confidence = self.gap_trust  # Now 50%!

            # NVDA needs STRONG volume confirmation - further relaxed threshold
            if volume > min_volume * 0.7:  # Adjusted from 1.0x to 0.7x
                base_confidence += 0.12
                breakdown.append("Premarket volume >=70% of min (+0.12)")
            elif volume > min_volume * 0.6:  # Adjusted from 0.8x to 0.6x
                base_confidence += 0.03  # modest bump for acceptable flow
                breakdown.append("Premarket volume >=60% of min (+0.03)")
            else:
                base_confidence -= 0.07  # softer penalty for light volume
                breakdown.append("Premarket volume light (-0.07)")
            if volume_ratio:
                if volume_ratio > 0.8:
                    base_confidence += 0.05
                    breakdown.append("Volume ratio > 0.8 (+0.05)")
                elif volume_ratio < 0.3:
                    base_confidence -= 0.05
                    breakdown.append("Volume ratio < 0.3 (-0.05)")

            # NVDA has HIGH traps - be very cautious
            trap_flag = data.get('trap_signals', False)
            ma_distance = data.get('ma_distance', 0.0)
            trap_risk = data.get('trap_risk_score', 0.0)
            if trap_flag:
                if not (gap_pct < 0 and ma_distance > 0.1):
                    penalty = self._scale_trap_penalty(
                        0.13 + trap_risk * 0.22, gap_pct, data)
                    base_confidence -= penalty
                    breakdown.append(
                        f"Trap penalty {penalty:-.2f} (risk {trap_risk:.2f})")

            # NVDA-specific: AI news can override weak signals
            if data.get('ai_news', False) and gap_pct > 0:
                base_confidence += 0.15  # NVDA responds to AI news
                breakdown.append("AI news flag (+0.15)")

            # NVDA-specific: NASDAQ/QQQ confirmation CRITICAL (tech stock)
            # NVDA follows NASDAQ much more than individual stocks
            nasdaq_change = data.get('nasdaq_pct', data.get(
                'sector_pct', 0))  # Prefer NASDAQ

            if abs(nasdaq_change) > 0.5:  # NASDAQ moving
                if (gap_pct > 0 and nasdaq_change > 0) or (gap_pct < 0 and nasdaq_change < 0):
                    # NVDA following NASDAQ = HIGH confidence
                    # Stronger boost (NASDAQ confirmation)
                    base_confidence += 0.15
                    breakdown.append("NASDAQ alignment (+0.15)")
                else:
                    # NVDA diverging from NASDAQ = RED FLAG
                    base_confidence -= 0.12  # Softer penalty to avoid over-filtering
                    breakdown.append("NASDAQ divergence (-0.12)")

            # SMH (semiconductor ETF) alignment also important for NVDA
            smh_change = data.get('smh_pct', 0)
            if abs(smh_change) > 1.0:
                if (gap_pct > 0 and smh_change > 0) or (gap_pct < 0 and smh_change < 0):
                    base_confidence += 0.08  # SMH confirmation
                    breakdown.append("SMH confirmation (+0.08)")
                else:
                    base_confidence -= 0.06  # Reduced penalty to allow more trades
                    breakdown.append("SMH divergence (-0.06)")

            # Earnings proximity check - reduce confidence if close to earnings
            earnings_days_away = data.get('earnings_days_away', 999)
            if earnings_days_away <= 5:  # Within 5 days of earnings
                base_confidence -= 0.10  # Uncertainty penalty
                breakdown.append("Earnings within 5 days (-0.10)")
            elif earnings_days_away <= 2:  # Very close to earnings
                base_confidence -= 0.20  # High uncertainty
                breakdown.append("Earnings imminent (-0.20)")

            # Technical trend indicator - placeholder for trend strength (e.g., ADX)
            trend_strength = data.get(
                'trend_strength', 0)  # Assume 0 to 1 scale
            if trend_strength > 0.5:  # Strong trend
                if (gap_pct > 0 and trend_strength > 0) or (gap_pct < 0 and trend_strength < 0):
                    base_confidence += 0.08  # Trend confirmation
                    breakdown.append("Trend confirmation (+0.08)")
                else:
                    base_confidence -= 0.08  # Trend contradiction
                    breakdown.append("Trend contradiction (-0.08)")

            # News catalyst placeholder - simulate based on gap size and volume as proxy
            # Lowered threshold for news impact
            if abs(gap_pct) > 2.0 and volume > min_volume * 1.0:  # Adjusted from 2.5% and 1.2x
                if gap_pct > 0:
                    base_confidence += 0.15  # Positive AI news catalyst likely
                    breakdown.append("Gap+volume implies positive AI news (+0.15)")
                else:
                    base_confidence -= 0.15  # Negative news catalyst likely
                    breakdown.append("Gap+volume implies negative news (-0.15)")

            # Options flow placeholder - simulate unusual options activity based on volume
            if volume > min_volume * 1.3:
                base_confidence += 0.07  # Likely unusual options activity
                breakdown.append("Volume >1.3x min (+0.07)")

            # Institutional buying placeholder - simulate based on high volume and positive gap
            if volume > min_volume * 1.2 and gap_pct > 0.8:
                base_confidence += 0.06  # Likely institutional buying
                breakdown.append("Institutional flow proxy (+0.06)")

            indicator_bias = data.get('indicator_bias', 0.0)
            base_confidence += self._aligned_indicator_bias(
                gap_pct, indicator_bias)
            if indicator_bias:
                breakdown.append(
                    f"Indicator bias contribution ({indicator_bias:+.2f})")
            trend_strength = data.get('trend_strength', 0.0)
            base_confidence += 0.05 * trend_strength
            if trend_strength:
                breakdown.append(
                    f"Trend strength weight (+{0.05 * trend_strength:.2f})")
            sector_alignment = data.get('sector_alignment', 0.0)
            base_confidence += 0.08 * sector_alignment
            if sector_alignment:
                breakdown.append(
                    f"Sector alignment weight (+{0.08 * sector_alignment:.2f})")
            if ma_distance > 0.15:
                if gap_pct < 0:
                    base_confidence += 0.05
                else:
                    base_confidence -= 0.08
                breakdown.append("MA distance adjustment applied")
            elif ma_distance < -0.15:
                base_confidence += 0.06
                breakdown.append("Oversold MA distance (+0.06)")

            # ========== INTEGRATE NEWS SENTIMENT BOOST (Priority 1) ==========
            news_sentiment = data.get('news_sentiment', 0.0)
            news_boost = data.get('news_confidence_boost', 0.0)
            
            if news_boost > 0:
                # Apply boost if sentiment aligns with direction
                if (gap_pct > 0 and news_sentiment > 0) or (gap_pct < 0 and news_sentiment < 0):
                    base_confidence += news_boost
                    breakdown.append(f"News sentiment aligned ({news_sentiment:+.2f}) (+{news_boost:.2f})")
                elif abs(news_sentiment) > 0.3:
                    # Reduce boost if sentiment opposes direction
                    base_confidence -= news_boost * 0.5
                    breakdown.append(f"News sentiment conflicting ({news_sentiment:+.2f}) (-{news_boost * 0.5:.2f})")

            base_confidence, pattern_notes = self._apply_pattern_context(
                base_confidence, data, gap_pct)
            breakdown.extend(pattern_notes)

            base_confidence = max(0.05, min(0.95, base_confidence))

            direction = 'UP' if gap_pct > 0 else 'DOWN'

            # NVDA requires higher confidence threshold due to traps - lowered threshold further
            if base_confidence < 0.43:
                return {'symbol': 'NVDA', 'direction': 'NEUTRAL', 'confidence': base_confidence,
                        'reason': f"NVDA confidence {base_confidence:.0%} too low (48% trap rate!)",
                        'confidence_breakdown': breakdown}

            return {
                'symbol': 'NVDA',
                'direction': direction,
                'confidence': min(base_confidence, 0.95),
                'exit_strategy': 'TARGETS',  # NVDA doesn't fade much
                'reason': f"NVDA gap {abs(gap_pct)*100:.1f}% - CONFIRMED despite 50% follow-through",
                'warning': "⚠️ NVDA has 48% trap rate - require strong confirmation!",
                'confidence_breakdown': breakdown
            }

        return {
            'symbol': 'NVDA',
            'direction': 'NEUTRAL',
            'confidence': 0.50,
            'reason': f"NVDA gap {abs(gap_pct)*100:.1f}% below dynamic threshold {min_gap_required*100:.1f}%",
            'confidence_breakdown': breakdown
        }


class METAPredictor(BaseStockPredictor):
    """
    META-SPECIFIC PREDICTOR

    META's Unique Traits:
    - 54% gap follow-through (DECENT)
    - 46% trap rate (MEDIUM)
    - 41% momentum continuation (WEAK)
    - 10% morning fade (HIGHEST!)

    Strategy: CAUTIOUS with META - fades often
    """

    def __init__(self):
        super().__init__('META')

        # META-SPECIFIC thresholds
        self.gap_trust = self._get_pattern_stat(
            'gaps', 'follow_through_rate', 0.54)
        self.trap_risk = self._get_pattern_stat('traps', 'trap_rate', 0.46)
        avg_gap = self._get_pattern_stat('gaps', 'avg_gap_size', 1.5)
        self.min_gap = max(0.01, min(0.03, (avg_gap or 1.5) / 100))
        self.momentum_rate = self._get_pattern_stat(
            'momentum', 'continuation_rate', 0.41)
        self.morning_fade_risk = self._get_pattern_stat(
            'intraday', 'morning_fade_rate', 0.10)

    def predict(self, data):
        """META-specific prediction logic"""

        gap_pct = data.get('gap_pct', 0)
        volume = data.get('volume', 0)
        min_volume = data.get('min_volume', 1000000)
        volume_ratio = data.get('volume_ratio', 0)
        breakdown = [f"Base follow-through {self.gap_trust:.2f}"]

        min_gap_required = self._dynamic_gap_threshold(self.min_gap, data)

        if abs(gap_pct) > min_gap_required:
            # META has DECENT gap follow-through
            base_confidence = self.gap_trust  # 54%

            # META volume check
            if volume > min_volume * 1.2:
                base_confidence += 0.10
                breakdown.append("Volume > 1.2x min (+0.10)")
            elif volume > min_volume:
                base_confidence += 0.05
                breakdown.append("Volume > min (+0.05)")
            else:
                base_confidence -= 0.10  # Penalty for low volume
                breakdown.append("Volume below min (-0.10)")
            if volume_ratio:
                if volume_ratio > 1.0:
                    base_confidence += 0.05
                    breakdown.append("Volume ratio >1.0 (+0.05)")
                elif volume_ratio < 0.25:
                    base_confidence -= 0.05
                    breakdown.append("Volume ratio <0.25 (-0.05)")

            # META has MEDIUM traps
            trap_flag = data.get('trap_signals', False)
            ma_distance = data.get('ma_distance', 0.0)
            trap_risk = data.get('trap_risk_score', 0.0)
            if trap_flag:
                if not (gap_pct < 0 and ma_distance > 0.1):
                    penalty = self._scale_trap_penalty(
                        0.15 + trap_risk * 0.2, gap_pct, data)
                    base_confidence -= penalty
                    breakdown.append(
                        f"Trap penalty {penalty:-.2f} (risk {trap_risk:.2f})")

            # META-specific: Regulatory news = BIG negative
            if data.get('regulatory_news', False):
                base_confidence -= 0.20  # Regulatory risk hurts META
                breakdown.append("Regulatory news (-0.20)")

            # META-specific: Ad revenue or user growth news
            if data.get('ad_revenue_news', False) or data.get('user_growth_news', False):
                if gap_pct > 0:
                    base_confidence += 0.15  # Positive news confirms UP
                    breakdown.append("Ad/user news positive (+0.15)")
                else:
                    base_confidence -= 0.15  # Negative news confirms DOWN
                    breakdown.append("Ad/user news negative (-0.15)")

            # Earnings proximity check - reduce confidence if close to earnings
            earnings_days_away = data.get('earnings_days_away', 999)
            if earnings_days_away <= 5:  # Within 5 days of earnings
                base_confidence -= 0.10  # Uncertainty penalty
                breakdown.append("Earnings within 5 days (-0.10)")
            elif earnings_days_away <= 2:  # Very close to earnings
                base_confidence -= 0.20  # High uncertainty
                breakdown.append("Earnings imminent (-0.20)")

            # Technical trend indicator - placeholder for trend strength (e.g., ADX)
            trend_strength = data.get(
                'trend_strength', 0)  # Assume 0 to 1 scale
            if trend_strength > 0.5:  # Strong trend
                if (gap_pct > 0 and trend_strength > 0) or (gap_pct < 0 and trend_strength < 0):
                    base_confidence += 0.08  # Trend confirmation
                    breakdown.append("Trend confirmation (+0.08)")
                else:
                    base_confidence -= 0.08  # Trend contradiction
                    breakdown.append("Trend contradiction (-0.08)")
            indicator_bias = data.get('indicator_bias', 0.0)
            base_confidence += self._aligned_indicator_bias(
                gap_pct, indicator_bias)
            if indicator_bias:
                breakdown.append(
                    f"Indicator bias contribution ({indicator_bias:+.2f})")
            base_confidence += 0.05 * data.get('sector_alignment', 0.0)
            if data.get('sector_alignment'):
                breakdown.append(
                    f"Sector alignment contribution (+{0.05 * data.get('sector_alignment', 0.0):.2f})")
            if ma_distance > 0.1:
                if gap_pct < 0:
                    base_confidence += 0.04
                else:
                    base_confidence -= 0.05
                breakdown.append("MA distance adjustment applied")

            # ========== INTEGRATE NEWS SENTIMENT BOOST (Priority 1) ==========
            news_sentiment = data.get('news_sentiment', 0.0)
            news_boost = data.get('news_confidence_boost', 0.0)
            
            if news_boost > 0:
                # Apply boost if sentiment aligns with direction
                if (gap_pct > 0 and news_sentiment > 0) or (gap_pct < 0 and news_sentiment < 0):
                    base_confidence += news_boost
                    breakdown.append(f"News sentiment aligned ({news_sentiment:+.2f}) (+{news_boost:.2f})")
                elif abs(news_sentiment) > 0.3:
                    # Reduce boost if sentiment opposes direction
                    base_confidence -= news_boost * 0.5
                    breakdown.append(f"News sentiment conflicting ({news_sentiment:+.2f}) (-{news_boost * 0.5:.2f})")

            # Penalty for high morning fade risk
            fade_penalty = self.morning_fade_risk * 0.5  # Scale down the penalty impact
            # Reduce confidence due to META's known morning fade tendency
            base_confidence -= fade_penalty
            breakdown.append(
                f"Morning fade risk penalty (-{fade_penalty:.2f})")

            base_confidence, pattern_notes = self._apply_pattern_context(
                base_confidence, data, gap_pct)
            breakdown.extend(pattern_notes)
            base_confidence = max(0.05, min(0.95, base_confidence))

            direction = 'UP' if gap_pct > 0 else 'DOWN'

            if base_confidence < 0.50:
                return {'symbol': 'META', 'direction': 'NEUTRAL', 'confidence': base_confidence,
                        'reason': f"META confidence {base_confidence:.0%} too low (46% trap rate)",
                        'confidence_breakdown': breakdown}

            return {
                'symbol': 'META',
                'direction': direction,
                'confidence': min(base_confidence, 0.95),
                'exit_strategy': 'TARGETS',
                'reason': f"META gap {abs(gap_pct)*100:.1f}% - {self.gap_trust*100:.0f}% follow-through",
                'warning': f"⚠️ META weak momentum ({self.momentum_rate*100:.0f}%) - don't chase!",
                'confidence_breakdown': breakdown
            }

        return {
            'symbol': 'META',
            'direction': 'NEUTRAL',
            'confidence': 0.50,
            'reason': f"META gap {abs(gap_pct)*100:.1f}% below dynamic threshold {min_gap_required*100:.1f}%",
            'confidence_breakdown': breakdown
        }


class AVGOPredictor(BaseStockPredictor):
    """
    AVGO-SPECIFIC PREDICTOR

    AVGO's Unique Traits:
    - 43.5% gap follow-through (WORST!)
    - 56.5% trap rate (HIGHEST!)
    - 45% momentum continuation
    - 0% morning fade (never fades!)

    Strategy: BE VERY SKEPTICAL - require maximum confirmation
    """

    def __init__(self):
        super().__init__('AVGO')

        # AVGO-SPECIFIC thresholds
        self.gap_trust = self._get_pattern_stat(
            'gaps', 'follow_through_rate', 0.455)
        self.trap_risk = self._get_pattern_stat('traps', 'trap_rate', 0.565)
        avg_gap = self._get_pattern_stat('gaps', 'avg_gap_size', 1.5)
        self.min_gap = max(0.01, min(0.03, (avg_gap or 1.5) / 100))

    def predict(self, data):
        """AVGO-specific prediction logic"""

        gap_pct = data.get('gap_pct', 0)
        volume = data.get('volume', 0)
        min_volume = data.get('min_volume', 150000)
        volume_ratio = data.get('volume_ratio', 0)

        min_gap_required = self._dynamic_gap_threshold(self.min_gap, data)
        breakdown = [f"Base follow-through {self.gap_trust:.2f}"]

        if abs(gap_pct) > min_gap_required:
            # AVGO has WORST gap follow-through!
            base_confidence = self.gap_trust

            # AVGO needs MAXIMUM volume confirmation
            if volume > min_volume * 1.6:
                base_confidence += 0.14
                breakdown.append("Volume >1.6x min (+0.14)")
            elif volume > min_volume * 0.9:
                base_confidence += 0.04
                breakdown.append("Volume ≥0.9x min (+0.04)")
            else:
                base_confidence -= 0.10
                breakdown.append("Volume below 0.9x min (-0.10)")
            if volume_ratio:
                if volume_ratio > 0.9:
                    base_confidence += 0.06
                    breakdown.append("Volume ratio >0.9 (+0.06)")
                elif volume_ratio < 0.25:
                    base_confidence -= 0.05
                    breakdown.append("Volume ratio <0.25 (-0.05)")

            # Trap handling
            trap_flag = data.get('trap_signals', False)
            ma_distance = data.get('ma_distance', 0.0)
            trap_risk = data.get('trap_risk_score', 0.0)
            if trap_flag:
                if not (gap_pct < 0 and ma_distance > 0.12):
                    penalty = self._scale_trap_penalty(
                        0.20 + trap_risk * 0.25, gap_pct, data)
                    base_confidence -= penalty
                    breakdown.append(
                        f"Trap penalty {penalty:-.2f} (risk {trap_risk:.2f})")

            # AVGO-specific catalysts
            if data.get('ma_rumors', False):
                if not data.get('institutional_confirmation', False):
                    base_confidence -= 0.20
                    breakdown.append("Unconfirmed M&A rumor (-0.20)")
                else:
                    base_confidence += 0.15
                    breakdown.append("Confirmed M&A rumor (+0.15)")

            smh_change = data.get('smh_pct', data.get('sector_pct', 0))
            if abs(smh_change) > 1.0:
                if (gap_pct > 0 and smh_change > 0) or (gap_pct < 0 and smh_change < 0):
                    base_confidence += 0.15
                    breakdown.append("SMH alignment (+0.15)")
                else:
                    base_confidence -= 0.14
                    breakdown.append("SMH divergence (-0.14)")

            institutional_flow = data.get('institutional_buying', data.get(
                'institutional_confirmation', False))
            if institutional_flow:
                base_confidence += 0.18
                breakdown.append("Institutional confirmation (+0.18)")
            else:
                base_confidence -= 0.05
                breakdown.append("No institutional confirmation (-0.05)")

            if data.get('data_center_news', False) and gap_pct > 0:
                base_confidence += 0.12
                breakdown.append("Data center demand news (+0.12)")

            sector_change = data.get('sector_pct', data.get('smh_pct', 0))
            if abs(sector_change) > 1.0:
                if (gap_pct > 0 and sector_change > 0) or (gap_pct < 0 and sector_change < 0):
                    base_confidence += 0.15
                    breakdown.append("Sector confirmation (+0.15)")
                else:
                    base_confidence -= 0.12
                    breakdown.append("Sector divergence (-0.12)")

            earnings_days_away = data.get('earnings_days_away', 999)
            if earnings_days_away <= 5:
                base_confidence -= 0.10
                breakdown.append("Earnings within 5 days (-0.10)")
            elif earnings_days_away <= 2:
                base_confidence -= 0.20
                breakdown.append("Earnings imminent (-0.20)")

            trend_strength = data.get('trend_strength', 0)
            if trend_strength > 0.5:
                if (gap_pct > 0 and trend_strength > 0) or (gap_pct < 0 and trend_strength < 0):
                    base_confidence += 0.08
                    breakdown.append("Trend confirmation (+0.08)")
                else:
                    base_confidence -= 0.08
                    breakdown.append("Trend contradiction (-0.08)")

            indicator_bias = data.get('indicator_bias', 0.0)
            bias_adj = self._aligned_indicator_bias(gap_pct, indicator_bias)
            base_confidence += bias_adj
            if bias_adj:
                breakdown.append(f"Indicator bias contribution ({bias_adj:+.2f})")
            sector_alignment = data.get('sector_alignment', 0.0)
            if sector_alignment:
                base_confidence += 0.06 * sector_alignment
                breakdown.append(
                    f"Sector alignment contribution (+{0.06 * sector_alignment:.2f})")
            if ma_distance > 0.18:
                if gap_pct < 0:
                    base_confidence += 0.05
                else:
                    base_confidence -= 0.08
                breakdown.append("MA distance adjustment applied")
            elif ma_distance < -0.18:
                base_confidence += 0.06
                breakdown.append("Oversold MA distance (+0.06)")

            # ========== INTEGRATE NEWS SENTIMENT BOOST (Priority 1) ==========
            news_sentiment = data.get('news_sentiment', 0.0)
            news_boost = data.get('news_confidence_boost', 0.0)
            
            if news_boost > 0:
                # Apply boost if sentiment aligns with direction
                if (gap_pct > 0 and news_sentiment > 0) or (gap_pct < 0 and news_sentiment < 0):
                    base_confidence += news_boost
                    breakdown.append(f"News sentiment aligned ({news_sentiment:+.2f}) (+{news_boost:.2f})")
                elif abs(news_sentiment) > 0.3:
                    # Reduce boost if sentiment opposes direction
                    base_confidence -= news_boost * 0.5
                    breakdown.append(f"News sentiment conflicting ({news_sentiment:+.2f}) (-{news_boost * 0.5:.2f})")

            base_confidence, pattern_notes = self._apply_pattern_context(
                base_confidence, data, gap_pct)
            breakdown.extend(pattern_notes)
            base_confidence = max(0.05, min(0.95, base_confidence))

            direction = 'UP' if gap_pct > 0 else 'DOWN'

            if base_confidence < 0.55:
                return {'symbol': 'AVGO', 'direction': 'NEUTRAL', 'confidence': base_confidence,
                        'reason': f"AVGO confidence {base_confidence:.0%} too low (57% trap rate!)",
                        'confidence_breakdown': breakdown}

            return {
                'symbol': 'AVGO',
                'direction': direction,
                'confidence': min(base_confidence, 0.95),
                'exit_strategy': 'TARGETS',
                'reason': f"AVGO gap {abs(gap_pct)*100:.1f}% - HEAVILY CONFIRMED despite 43% follow-through",
                'warning': "🚨 AVGO has 57% TRAP RATE - highest of all! Maximum caution!",
                'confidence_breakdown': breakdown
            }

        return {
            'symbol': 'AVGO',
            'direction': 'NEUTRAL',
            'confidence': 0.50,
            'reason': f"AVGO gap {abs(gap_pct)*100:.1f}% below dynamic threshold {min_gap_required*100:.1f}%",
            'confidence_breakdown': breakdown
        }


class SNOWPredictor(BaseStockPredictor):
    """
    SNOW-SPECIFIC PREDICTOR

    SNOW's Unique Traits:
    - 51.2% gap follow-through (coin flip)
    - 48.8% trap rate (medium)
    - Follows cloud sector heavily (CRM, DDOG)
    - Revenue growth > profitability
    - Customer count = key metric

    Strategy: Require cloud sector confirmation + revenue catalyst
    """

    def __init__(self):
        super().__init__('SNOW')

        # SNOW-SPECIFIC thresholds
        self.gap_trust = self._get_pattern_stat(
            'gaps', 'follow_through_rate', 0.512)
        self.trap_risk = self._get_pattern_stat('traps', 'trap_rate', 0.488)
        avg_gap = self._get_pattern_stat('gaps', 'avg_gap_size', 1.5)
        self.min_gap = max(0.012, min(0.04, (avg_gap or 1.5) / 100))
        self.cloud_sector_correlation = 0.78  # Very high!

    def predict(self, data):
        """SNOW-specific prediction logic"""

        gap_pct = data.get('gap_pct', 0)
        volume = data.get('volume', 0)
        min_volume = data.get('min_volume', 5200000)
        volume_ratio = data.get('volume_ratio', 0)

        min_gap_required = self._dynamic_gap_threshold(self.min_gap, data)
        breakdown = [f"Base follow-through {self.gap_trust:.2f}"]

        if abs(gap_pct) > min_gap_required:
            base_confidence = self.gap_trust

            if volume > min_volume * 1.5:
                base_confidence += 0.12
                breakdown.append("Volume >1.5x institutional threshold (+0.12)")
            elif volume < min_volume * 0.7:
                base_confidence -= 0.15
                breakdown.append("Volume <0.7x institutional threshold (-0.15)")
            if volume_ratio:
                if volume_ratio > 0.9:
                    base_confidence += 0.05
                    breakdown.append("Volume ratio >0.9 (+0.05)")
                elif volume_ratio < 0.3:
                    base_confidence -= 0.05
                    breakdown.append("Volume ratio <0.3 (-0.05)")

            cloud_sector = data.get(
                'cloud_sector_pct', data.get('sector_pct', 0))
            if abs(cloud_sector) > 1.0:
                if (gap_pct > 0 and cloud_sector > 0) or (gap_pct < 0 and cloud_sector < 0):
                    base_confidence += 0.18
                    breakdown.append("Cloud sector alignment (+0.18)")
                else:
                    base_confidence -= 0.22
                    breakdown.append("Cloud sector divergence (-0.22)")

            revenue_growth_news = data.get('revenue_growth_news', False)
            customer_growth_news = data.get('customer_growth_news', False)
            if revenue_growth_news and gap_pct > 0:
                base_confidence += 0.16
                breakdown.append("Revenue growth news (+0.16)")
            elif customer_growth_news and gap_pct > 0:
                base_confidence += 0.14
                breakdown.append("Customer growth news (+0.14)")

            profitability_news = data.get('profitability_news', False)
            if profitability_news:
                base_confidence -= 0.10
                breakdown.append("Profitability concern (-0.10)")

            competition_news = data.get('competition_news', False)
            if competition_news:
                base_confidence -= 0.15
                breakdown.append("Competition pressure (-0.15)")

            valuation_concerns = data.get('valuation_concerns', False)
            if valuation_concerns and gap_pct > 0:
                base_confidence -= 0.12
                breakdown.append("Valuation concern (-0.12)")

            trap_flag = data.get('trap_signals', False)
            ma_distance = data.get('ma_distance', 0.0)
            trap_risk = data.get('trap_risk_score', 0.0)
            if trap_flag:
                if not (gap_pct < 0 and ma_distance > 0.1):
                    penalty = self._scale_trap_penalty(
                        0.17 + trap_risk * 0.17, gap_pct, data)
                    base_confidence -= penalty
                    breakdown.append(
                        f"Trap penalty {penalty:-.2f} (risk {trap_risk:.2f})")

            earnings_days_away = data.get('earnings_days_away', 999)
            if earnings_days_away <= 5:
                base_confidence -= 0.10
                breakdown.append("Earnings within 5 days (-0.10)")
            elif earnings_days_away <= 2:
                base_confidence -= 0.20
                breakdown.append("Earnings imminent (-0.20)")

            trend_strength = data.get('trend_strength', 0)
            if trend_strength > 0.5:
                if (gap_pct > 0 and trend_strength > 0) or (gap_pct < 0 and trend_strength < 0):
                    base_confidence += 0.08
                    breakdown.append("Trend confirmation (+0.08)")
                else:
                    base_confidence -= 0.08
                    breakdown.append("Trend contradiction (-0.08)")

            indicator_bias = data.get('indicator_bias', 0.0)
            bias_adj = self._aligned_indicator_bias(gap_pct, indicator_bias)
            base_confidence += bias_adj
            if bias_adj:
                breakdown.append(f"Indicator bias contribution ({bias_adj:+.2f})")
            sector_alignment = data.get('sector_alignment', 0.0)
            if sector_alignment:
                base_confidence += 0.08 * sector_alignment
                breakdown.append(
                    f"Sector alignment contribution (+{0.08 * sector_alignment:.2f})")
            if ma_distance > 0.1:
                if gap_pct < 0:
                    base_confidence += 0.04
                else:
                    base_confidence -= 0.05
                breakdown.append("MA distance adjustment applied")

            # ========== INTEGRATE NEWS SENTIMENT BOOST (Priority 1) ==========
            news_sentiment = data.get('news_sentiment', 0.0)
            news_boost = data.get('news_confidence_boost', 0.0)
            
            if news_boost > 0:
                # Apply boost if sentiment aligns with direction
                if (gap_pct > 0 and news_sentiment > 0) or (gap_pct < 0 and news_sentiment < 0):
                    base_confidence += news_boost
                    breakdown.append(f"News sentiment aligned ({news_sentiment:+.2f}) (+{news_boost:.2f})")
                elif abs(news_sentiment) > 0.3:
                    # Reduce boost if sentiment opposes direction
                    base_confidence -= news_boost * 0.5
                    breakdown.append(f"News sentiment conflicting ({news_sentiment:+.2f}) (-{news_boost * 0.5:.2f})")

            base_confidence, pattern_notes = self._apply_pattern_context(
                base_confidence, data, gap_pct)
            breakdown.extend(pattern_notes)
            base_confidence = max(0.05, min(0.95, base_confidence))

            direction = 'UP' if gap_pct > 0 else 'DOWN'

            if base_confidence < 0.55:
                return {'symbol': 'SNOW', 'direction': 'NEUTRAL', 'confidence': base_confidence,
                        'reason': f"SNOW confidence {base_confidence:.0%} too low (cloud sector check)",
                        'confidence_breakdown': breakdown}

            return {
                'symbol': 'SNOW',
                'direction': direction,
                'confidence': min(base_confidence, 0.95),
                'exit_strategy': 'TARGETS',
                'reason': f"SNOW gap {abs(gap_pct)*100:.1f}% - {self.gap_trust*100:.0f}% follow-through, cloud confirmed",
                'warning': "⚠️ SNOW follows cloud sector (CRM, DDOG) - check sector alignment!",
                'confidence_breakdown': breakdown
            }

        return {
            'symbol': 'SNOW',
            'direction': 'NEUTRAL',
            'confidence': 0.50,
            'reason': f"SNOW gap {abs(gap_pct)*100:.1f}% below dynamic threshold {min_gap_required*100:.1f}%",
            'confidence_breakdown': breakdown
        }


class PLTRPredictor(BaseStockPredictor):
    """
    PLTR-SPECIFIC PREDICTOR

    PLTR's Unique Traits:
    - 42.5% gap follow-through (VERY WEAK!)
    - 57.5% trap rate (VERY HIGH!)
    - Government contract driven
    - Meme stock tendencies (retail hype)
    - Extreme volatility
    - Defense sector correlation

    Strategy: BE VERY CAUTIOUS - require catalyst + fade retail hype
    """

    def __init__(self):
        super().__init__('PLTR')

        # PLTR-SPECIFIC thresholds
        self.gap_trust = self._get_pattern_stat(
            'gaps', 'follow_through_rate', 0.48)
        self.trap_risk = self._get_pattern_stat('traps', 'trap_rate', 0.52)
        avg_gap = self._get_pattern_stat('gaps', 'avg_gap_size', 1.8)
        self.min_gap = max(0.012, min(0.04, (avg_gap or 1.8) / 100))
        self.meme_stock = True  # PLTR has meme tendencies

    def predict(self, data):
        """PLTR-specific prediction logic"""

        gap_pct = data.get('gap_pct', 0)
        volume = data.get('volume', 0)
        min_volume = data.get('min_volume', 1000000)
        volume_ratio = data.get('volume_ratio', 0)

        min_gap_required = self._dynamic_gap_threshold(self.min_gap, data)
        breakdown = [f"Base follow-through {self.gap_trust:.2f}"]

        if abs(gap_pct) > min_gap_required:
            base_confidence = self.gap_trust

            if volume > min_volume * 1.2:
                base_confidence += 0.10
                breakdown.append("Volume >1.2x min (+0.10)")
            elif volume > min_volume:
                base_confidence += 0.05
                breakdown.append("Volume > min (+0.05)")
            else:
                base_confidence -= 0.10
                breakdown.append("Volume < min (-0.10)")
            if volume_ratio:
                if volume_ratio > 1.0:
                    base_confidence += 0.05
                    breakdown.append("Volume ratio >1.0 (+0.05)")
                elif volume_ratio < 0.25:
                    base_confidence -= 0.05
                    breakdown.append("Volume ratio <0.25 (-0.05)")

            trap_flag = data.get('trap_signals', False)
            ma_distance = data.get('ma_distance', 0.0)
            trap_risk = data.get('trap_risk_score', 0.0)
            if trap_flag:
                if not (gap_pct < 0 and ma_distance > 0.1):
                    penalty = self._scale_trap_penalty(
                        0.20 + trap_risk * 0.2, gap_pct, data)
                    base_confidence -= penalty
                    breakdown.append(
                        f"Trap penalty {penalty:-.2f} (risk {trap_risk:.2f})")

            if data.get('gov_contract_news', False):
                base_confidence += 0.20
                breakdown.append("Government contract news (+0.20)")

            social_sentiment = data.get('social_sentiment', 0)
            if self.meme_stock and abs(social_sentiment) > 0.2:
                if (gap_pct > 0 and social_sentiment > 0) or (gap_pct < 0 and social_sentiment < 0):
                    base_confidence += 0.15
                    breakdown.append("Retail sentiment aligned (+0.15)")
                else:
                    base_confidence -= 0.15
                    breakdown.append("Retail sentiment fading move (-0.15)")

            earnings_days_away = data.get('earnings_days_away', 999)
            if earnings_days_away <= 5:
                base_confidence -= 0.10
                breakdown.append("Earnings within 5 days (-0.10)")
            elif earnings_days_away <= 2:
                base_confidence -= 0.20
                breakdown.append("Earnings imminent (-0.20)")

            trend_strength = data.get('trend_strength', 0)
            if trend_strength > 0.5:
                if (gap_pct > 0 and trend_strength > 0) or (gap_pct < 0 and trend_strength < 0):
                    base_confidence += 0.08
                    breakdown.append("Trend confirmation (+0.08)")
                else:
                    base_confidence -= 0.08
                    breakdown.append("Trend contradiction (-0.08)")

            indicator_bias = data.get('indicator_bias', 0.0)
            bias_adj = self._aligned_indicator_bias(gap_pct, indicator_bias)
            base_confidence += bias_adj
            if bias_adj:
                breakdown.append(f"Indicator bias contribution ({bias_adj:+.2f})")
            sector_alignment = data.get('sector_alignment', 0.0)
            if sector_alignment:
                base_confidence += 0.05 * sector_alignment
                breakdown.append(
                    f"Sector alignment contribution (+{0.05 * sector_alignment:.2f})")
            sentiment_score = data.get('sentiment_score', 0.0)
            if sentiment_score:
                base_confidence += sentiment_score
                breakdown.append(
                    f"Advanced sentiment score contribution ({sentiment_score:+.2f})")
            if ma_distance > 0.12:
                if gap_pct < 0:
                    base_confidence += 0.04
                else:
                    base_confidence -= 0.05
                breakdown.append("MA distance adjustment applied")

            # ========== INTEGRATE NEWS SENTIMENT BOOST (Priority 1) ==========
            news_sentiment = data.get('news_sentiment', 0.0)
            news_boost = data.get('news_confidence_boost', 0.0)
            
            if news_boost > 0:
                # Apply boost if sentiment aligns with direction
                if (gap_pct > 0 and news_sentiment > 0) or (gap_pct < 0 and news_sentiment < 0):
                    base_confidence += news_boost
                    breakdown.append(f"News sentiment aligned ({news_sentiment:+.2f}) (+{news_boost:.2f})")
                elif abs(news_sentiment) > 0.3:
                    # Reduce boost if sentiment opposes direction
                    base_confidence -= news_boost * 0.5
                    breakdown.append(f"News sentiment conflicting ({news_sentiment:+.2f}) (-{news_boost * 0.5:.2f})")

            base_confidence, pattern_notes = self._apply_pattern_context(
                base_confidence, data, gap_pct)
            breakdown.extend(pattern_notes)
            base_confidence = max(0.05, min(0.95, base_confidence))

            direction = 'UP' if gap_pct > 0 else 'DOWN'

            if base_confidence < 0.47:
                return {'symbol': 'PLTR', 'direction': 'NEUTRAL', 'confidence': base_confidence,
                        'reason': f"PLTR confidence {base_confidence:.0%} too low (52% trap rate!)",
                        'confidence_breakdown': breakdown}

            return {
                'symbol': 'PLTR',
                'direction': direction,
                'confidence': min(base_confidence, 0.95),
                'exit_strategy': 'TARGETS',
                'reason': f"PLTR gap {abs(gap_pct)*100:.1f}% - HEAVILY CONFIRMED despite 48% follow-through",
                'warning': "🚨 PLTR: 52% TRAP RATE + meme stock - require catalyst or SKIP!",
                'confidence_breakdown': breakdown
            }

        return {
            'symbol': 'PLTR',
            'direction': 'NEUTRAL',
            'confidence': 0.50,
            'reason': f"PLTR gap {abs(gap_pct)*100:.1f}% below dynamic threshold {min_gap_required*100:.1f}%",
            'confidence_breakdown': breakdown
        }


# FACTORY FUNCTION
def get_predictor(symbol):
    """Get the stock-specific predictor"""
    predictors = {
        'AMD': AMDPredictor,
        'NVDA': NVDAPredictor,
        'META': METAPredictor,
        'AVGO': AVGOPredictor,
        'SNOW': SNOWPredictor,
        'PLTR': PLTRPredictor
    }

    if symbol not in predictors:
        raise ValueError(f"No predictor for {symbol}")

    return predictors[symbol]()


if __name__ == "__main__":
    print("\n" + "="*80)
    print("🎯 STOCK-SPECIFIC PREDICTORS - DEMONSTRATION")
    print("="*80)

    # Example data
    test_data = {
        'gap_pct': 2.0,
        'volume': 5000000,
        'min_volume': 1000000,
        'trap_signals': False,
        'social_sentiment': 0.05,
        'ai_news': True,
        'sector_pct': 1.2
    }

    print("\n📊 TEST SCENARIO: 2% gap up, high volume, AI news, sector aligned\n")

    # Test each stock with SAME data
    for symbol in ['AMD', 'NVDA', 'META', 'AVGO']:
        predictor = get_predictor(symbol)
        result = predictor.predict(test_data)

        print(f"\n{symbol}:")
        print(f"   Direction: {result.get('direction', 'N/A')}")
        print(f"   Confidence: {result.get('confidence', 0)*100:.0f}%")
        print(f"   Reason: {result.get('reason', 'N/A')}")
        if 'warning' in result:
            print(f"   Warning: {result['warning']}")

    print("\n" + "="*80)
    print("✅ NOTICE: SAME DATA → DIFFERENT PREDICTIONS!")
    print("="*80)
    print("""
Each stock analyzed INDEPENDENTLY:
- AMD: Trusts gaps (57% follow-through)
- NVDA: Cautious (47% follow-through, 53% traps)
- META: Good gaps but weak momentum
- AVGO: Very skeptical (43% follow-through, 57% traps!)

This is CORRECT - each stock has unique behavior!
    """)
