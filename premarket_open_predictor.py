#!/usr/bin/env python3
"""
Premarket-to-Open Prediction Engine
Run at 8:30 AM ET (1 hour before market open)
Predicts: Premarket Price → 9:30 AM Open Move

Key Differences from Overnight System:
1. Uses PREMARKET price as current price (not yesterday's close)
2. Predicts 1-hour move (premarket → open) vs overnight
3. Different weight distribution (more futures, premarket momentum, less social)
4. Gap fill psychology (large gaps often partially fill)
5. Premarket volume analysis (institutional activity)

Author: Overnight Swing Trading System
Created: October 18, 2025
"""

import os
import sys
from pathlib import Path
from datetime import datetime, time
import pytz

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import the base predictor and modify for premarket
from comprehensive_nextday_predictor import ComprehensiveNextDayPredictor
from stock_config import get_stock_config, get_stock_weight_adjustments

class PremarketOpenPredictor(ComprehensiveNextDayPredictor):
    """
    Premarket-to-Open predictor
    
    Runs: 8:30 AM ET (1 hour before open)
    Predicts: Premarket price → 9:30 AM opening move
    Time Horizon: ~1 hour
    """
    
    def __init__(self, symbol: str = None):
        super().__init__(symbol)
        print("\n" + "="*80)
        print("🌅 PREMARKET-TO-OPEN PREDICTION ENGINE")
        print("="*80)
        print(f"⏰ Run Time: 8:30 AM ET (1 hour before market open)")
        print(f"🎯 Prediction: Premarket → 9:30 AM Open")
        print(f"📊 Time Horizon: ~1 hour")
        print("="*80)
        
    def get_premarket_weights(self):
        """
        Get adjusted weights for premarket-to-open predictions
        
        Key Changes from Overnight:
        1. Futures weight UP (20%) - drives opening direction
        2. Premarket momentum UP (15%) - critical for opening
        3. Options weight DOWN (5%) - less relevant for 1-hour move
        4. Social media DOWN (0%) - not active at 8:30 AM
        5. Gap psychology NEW (10%) - large gaps often fill
        6. Overnight news UP (12%) - breaking news overnight
        """
        
        # Start with base weights
        base_weights = self.weight_adjustments.copy()
        
        # PREMARKET ADJUSTMENTS (Optimized for 1-hour prediction)
        # Key changes from overnight: Futures UP, Gap Fill NEW, Social ZERO
        premarket_weights = {
            'futures': 0.25,          # UP from 15% to 25% - drives opening direction
            'premarket': 0.20,        # UP from 10% to 20% - momentum critical for open
            'gap_psychology': 0.15,   # NEW - large gaps often fill (70-90%)
            'vix': 0.10,              # UP from 8% - fear drives open
            'hidden_edge': 0.08,      # DOWN from 10% - less time for edge to work
            'news': 0.08,             # DOWN from 11-14% - already priced into PM
            'technical': 0.07,        # SAME - support/resistance at open
            'options': 0.05,          # DOWN from 11% - less relevant for 1hr
            'sector': 0.02,           # DOWN - less impact on open
            'analyst_ratings': 0.00,  # ZERO - not relevant for 1hr move
            'institutional': 0.00,    # ZERO - not active at 8:30 AM
            'earnings_proximity': 0.00,  # ZERO - not relevant for open
            'dxy': 0.00,              # ZERO - not relevant for 1hr
            'short_interest': 0.00,   # ZERO - not relevant for open
            'reddit': 0.00,           # ZERO - not active at 8:30 AM
            'twitter': 0.00,          # ZERO - not active at 8:30 AM
        }
        
        print("\n🔧 PREMARKET-OPTIMIZED WEIGHTS:")
        print("   Futures: 25% (drives open direction)")
        print("   PM Momentum: 20% (critical for continuation)")
        print("   Gap Fill: 15% (large gaps often partially fill)")
        print("   Social Media: 0% (not active at 8:30 AM)")
        
        return premarket_weights
    
    def analyze_premarket_momentum(self, symbol: str):
        """
        Analyze premarket price momentum
        
        Critical for opening prediction:
        - Is premarket price trending UP or DOWN?
        - Is momentum accelerating or decelerating?
        - Volume confirmation?
        
        Returns:
            dict: Premarket momentum analysis
        """
        import yfinance as yf
        
        print(f"\n📊 Premarket Momentum Analysis...")
        
        try:
            ticker = yf.Ticker(symbol)
            
            # Get premarket data if available
            hist = ticker.history(period='1d', interval='1m', prepost=True)
            
            if len(hist) > 0:
                # Get premarket bars (before 9:30 AM)
                premarket_bars = hist[hist.index.hour < 9.5]
                
                if len(premarket_bars) >= 5:
                    # Calculate momentum
                    recent_5 = premarket_bars.tail(5)
                    momentum_change = ((recent_5['Close'].iloc[-1] - recent_5['Close'].iloc[0]) / 
                                     recent_5['Close'].iloc[0]) * 100
                    
                    # Volume trend
                    avg_volume = recent_5['Volume'].mean()
                    last_volume = recent_5['Volume'].iloc[-1]
                    volume_trend = "INCREASING" if last_volume > avg_volume * 1.2 else "DECREASING" if last_volume < avg_volume * 0.8 else "NEUTRAL"
                    
                    # Momentum direction
                    if momentum_change > 0.3:
                        momentum_dir = "BULLISH"
                        momentum_score = 0.50
                    elif momentum_change > 0.1:
                        momentum_dir = "SLIGHTLY_BULLISH"
                        momentum_score = 0.25
                    elif momentum_change < -0.3:
                        momentum_dir = "BEARISH"
                        momentum_score = -0.50
                    elif momentum_change < -0.1:
                        momentum_dir = "SLIGHTLY_BEARISH"
                        momentum_score = -0.25
                    else:
                        momentum_dir = "NEUTRAL"
                        momentum_score = 0.0
                    
                    print(f"   5-Min Momentum: {momentum_change:+.2f}% ({momentum_dir})")
                    print(f"   Volume Trend: {volume_trend}")
                    print(f"   Momentum Score: {momentum_score:+.2f}")
                    
                    return {
                        'momentum_change': momentum_change,
                        'momentum_dir': momentum_dir,
                        'momentum_score': momentum_score,
                        'volume_trend': volume_trend,
                        'has_data': True
                    }
        except Exception as e:
            print(f"   ⚠️ Could not fetch premarket momentum: {str(e)[:50]}")
        
        # No data available
        print(f"   ℹ️ Premarket momentum data not available")
        return {
            'momentum_change': 0,
            'momentum_dir': 'UNKNOWN',
            'momentum_score': 0.0,
            'volume_trend': 'UNKNOWN',
            'has_data': False
        }
    
    def analyze_gap_psychology(self, yesterday_close: float, premarket_price: float, 
                               premarket_volume: float = 0):
        """
        Analyze gap fill psychology
        
        Large gaps (>3%) often partially fill on open
        Small gaps (<1%) often extend
        
        Args:
            yesterday_close: Yesterday's closing price
            premarket_price: Current premarket price
            premarket_volume: Premarket volume (if available)
            
        Returns:
            dict: Gap psychology analysis
        """
        
        gap_pct = ((premarket_price - yesterday_close) / yesterday_close) * 100
        gap_size = abs(gap_pct)
        
        print(f"\n📊 Gap Psychology Analysis...")
        print(f"   Yesterday Close: ${yesterday_close:.2f}")
        print(f"   Premarket Price: ${premarket_price:.2f}")
        print(f"   Gap: {gap_pct:+.2f}%")
        
        # Gap fill tendency based on size
        if gap_size > 5.0:
            # Huge gap (>5%) - Very likely to partially fill
            fill_tendency = -0.70 if gap_pct > 0 else 0.70  # 70% fill tendency
            strength = "VERY_HIGH"
            print(f"   🔥 HUGE GAP >5% - Very likely to partially fill")
        elif gap_size > 3.0:
            # Large gap (3-5%) - Likely to partially fill
            fill_tendency = -0.50 if gap_pct > 0 else 0.50  # 50% fill tendency
            strength = "HIGH"
            print(f"   ⚠️ LARGE GAP 3-5% - Likely to partially fill")
        elif gap_size > 1.5:
            # Moderate gap (1.5-3%) - May partially fill
            fill_tendency = -0.30 if gap_pct > 0 else 0.30  # 30% fill tendency
            strength = "MODERATE"
            print(f"   📈 MODERATE GAP 1.5-3% - May partially fill")
        elif gap_size > 0.5:
            # Small gap (0.5-1.5%) - Tends to extend
            fill_tendency = 0.20 if gap_pct > 0 else -0.20  # 20% extension tendency
            strength = "LOW"
            print(f"   ➡️ SMALL GAP 0.5-1.5% - Tends to extend")
        else:
            # Tiny gap (<0.5%) - Neutral
            fill_tendency = 0.0
            strength = "NONE"
            print(f"   ⚪ TINY GAP <0.5% - Neutral")
        
        # Premarket volume confirmation (if available)
        volume_confirmation = 0
        if premarket_volume > 100000:  # Significant volume
            volume_confirmation = 0.10  # Adds conviction
            print(f"   ✅ Premarket Volume: {premarket_volume:,.0f} (significant)")
        
        score = fill_tendency + volume_confirmation
        
        return {
            'gap_pct': gap_pct,
            'gap_size': gap_size,
            'fill_tendency': fill_tendency,
            'strength': strength,
            'score': score,
            'has_data': True
        }
    
    def generate_premarket_prediction(self):
        """
        Generate premarket-to-open prediction
        
        Key Differences:
        1. Current price = PREMARKET price
        2. Target = Expected 9:30 AM open price
        3. Uses premarket-specific weights
        4. Includes gap psychology
        5. Shorter time horizon (1 hour)
        """
        
        # Check if we're in premarket hours (6:00 AM - 9:30 AM ET)
        et_tz = pytz.timezone('US/Eastern')
        now_et = datetime.now(et_tz)
        current_time = now_et.time()
        
        premarket_start = time(6, 0)   # 6:00 AM
        premarket_end = time(9, 30)     # 9:30 AM
        
        if not (premarket_start <= current_time < premarket_end):
            print(f"\n⚠️ WARNING: Not in premarket hours!")
            print(f"   Current time: {now_et.strftime('%I:%M %p ET')}")
            print(f"   Premarket hours: 6:00 AM - 9:30 AM ET")
            print(f"   Proceeding anyway for testing...")
        
        print(f"\n⏰ {now_et.strftime('%Y-%m-%d %I:%M %p ET')}")
        
        # Get yesterday's close and premarket price
        import yfinance as yf
        ticker = yf.Ticker(self.symbol)
        
        try:
            # Get yesterday's close
            hist = ticker.history(period='5d')
            if len(hist) >= 2:
                yesterday_close = float(hist['Close'].iloc[-2])
                print(f"📊 Yesterday's Close: ${yesterday_close:.2f}")
            else:
                yesterday_close = float(hist['Close'].iloc[-1])
                print(f"📊 Last Close: ${yesterday_close:.2f}")
            
            # Get premarket price
            info = ticker.info
            premarket_price = info.get('preMarketPrice', None)
            premarket_volume = info.get('preMarketVolume', 0)
            
            if premarket_price:
                premarket_price = float(premarket_price)
                gap_pct = ((premarket_price - yesterday_close) / yesterday_close) * 100
                print(f"🌅 Premarket Price: ${premarket_price:.2f} ({gap_pct:+.2f}%)")
                print(f"📊 Premarket Volume: {premarket_volume:,.0f}")
                current_price = premarket_price  # USE PREMARKET AS CURRENT
            else:
                print(f"⚠️ Premarket price not available, using last close")
                current_price = yesterday_close
                premarket_price = yesterday_close
                
        except Exception as e:
            print(f"❌ Error fetching prices: {e}")
            return None
        
        # Collect data sources (similar to overnight but different weights)
        print(f"\n📰 Analyzing Overnight News...")
        news = self.get_news_sentiment()
        
        print(f"\n📈 Analyzing Futures...")
        futures = self.get_futures_sentiment()
        
        print(f"\n📊 Analyzing Options...")
        options = self.get_options_flow()
        
        print(f"\n📊 VIX Fear Gauge...")
        vix = self.get_vix_fear_gauge()
        
        print(f"\n🏭 Sector Analysis...")
        sector = self.get_sector_analysis()
        
        # Gap psychology analysis
        gap_psych = self.analyze_gap_psychology(
            yesterday_close, 
            premarket_price,
            premarket_volume
        )
        
        # Premarket momentum analysis (CRITICAL for opening prediction)
        premarket_momentum = self.analyze_premarket_momentum(self.symbol)
        
        # Technical (less important for 1-hour move)
        technical = self.get_technical_analysis()
        
        # Get premarket weights
        weights = self.get_premarket_weights()
        
        print("\n" + "="*80)
        print("🎯 PREMARKET PREDICTION CALCULATION")
        print("="*80)
        
        print(f"\n⚖️ Using PREMARKET-specific weights for {self.symbol}:")
        for factor, weight in sorted(weights.items(), key=lambda x: x[1], reverse=True):
            if weight > 0:
                print(f"   {factor.capitalize():20s} {weight:.2f} ({weight*100:.0f}%)")
        
        # Calculate scores
        news_score = news['overall_score'] * weights['news']
        futures_score = (futures['overall_sentiment'] / 10) * weights['futures']
        options_score = weights['options'] if options['sentiment'] == 'bullish' else -weights['options'] if options['sentiment'] == 'bearish' else 0
        
        # VIX sentiment (negative VIX change = bullish, positive = bearish)
        vix_change = vix.get('vix_change', 0)
        if vix_change > 15:
            vix_sentiment = -0.50  # Big VIX spike = bearish
        elif vix_change > 5:
            vix_sentiment = -0.30  # VIX up = bearish
        elif vix_change < -15:
            vix_sentiment = 0.30  # Big VIX drop = bullish
        elif vix_change < -5:
            vix_sentiment = 0.10  # VIX down = bullish
        else:
            vix_sentiment = 0  # Neutral
        vix_score = vix_sentiment * weights['vix']
        
        gap_score = gap_psych['score'] * weights['gap_psychology']
        
        # PREMARKET MOMENTUM (VERY IMPORTANT - can override everything!)
        # If premarket is moving strongly in one direction, that matters more than overnight prediction
        premarket_momentum_score = 0
        if premarket_momentum['has_data']:
            # Use premarket momentum with HIGH weight (15%)
            premarket_momentum_score = premarket_momentum['momentum_score'] * weights['premarket']
            
            # Strong premarket momentum can override other signals
            if abs(premarket_momentum['momentum_change']) > 0.5:
                print(f"\n   ⚠️ STRONG PREMARKET MOMENTUM DETECTED!")
                print(f"   This can override overnight signals if direction differs")
        
        # Technical (simplified for short-term)
        if technical.get('trend') == 'uptrend':
            tech_score = weights['technical']
        elif technical.get('trend') == 'downtrend':
            tech_score = -weights['technical']
        else:
            tech_score = 0
        
        # Sector
        sector_score = 0
        if sector.get('has_data'):
            sector_change = sector.get('sector_change', 0)
            if sector_change > 0.3:
                sector_score = weights['sector']
            elif sector_change < -0.3:
                sector_score = -weights['sector']
        
        # Calculate total (INDEPENDENT from overnight system)
        total_score = (
            news_score +
            futures_score +
            options_score +
            vix_score +
            gap_score +
            premarket_momentum_score +  # NEW: Premarket momentum
            tech_score +
            sector_score
        )
        
        print(f"\n📊 Scores:")
        print(f"   News (overnight):     {news_score:+.3f}")
        print(f"   Futures:              {futures_score:+.3f}")
        print(f"   Options:              {options_score:+.3f}")
        print(f"   VIX:                  {vix_score:+.3f}")
        print(f"   Gap Psychology:       {gap_score:+.3f}")
        print(f"   Premarket Momentum:   {premarket_momentum_score:+.3f} ⭐ (CRITICAL)")
        print(f"   Technical:            {tech_score:+.3f}")
        print(f"   Sector:               {sector_score:+.3f}")
        print(f"   " + "-"*40)
        print(f"   TOTAL (raw):          {total_score:+.3f}")
        
        # 🆕 BIAS FIXES FROM OVERNIGHT SYSTEM (Applied to premarket too!)
        print(f"\n🔧 APPLYING BIAS FIXES:")
        
        # FIX #1: RSI OVERBOUGHT PENALTY (Same as overnight)
        rsi = technical.get('rsi', 50)
        if rsi > 65 and total_score > 0:
            overbought_penalty = -0.013
            total_score += overbought_penalty
            print(f"   ⚠️ RSI {rsi:.1f} OVERBOUGHT - Bearish penalty: {overbought_penalty:.3f}")
        
        # FIX #2: MEAN REVERSION (Multiple up days + overbought)
        consecutive_days = technical.get('consecutive_days', 0)
        if consecutive_days >= 3 and rsi > 60 and total_score > 0:
            reversion_penalty = -0.025
            total_score += reversion_penalty
            print(f"   ⚠️ Mean Reversion: {consecutive_days} up days + RSI {rsi:.1f} - Penalty: {reversion_penalty:.3f}")
        elif consecutive_days <= -3 and rsi < 40 and total_score < 0:
            reversion_boost = 0.025
            total_score += reversion_boost
            print(f"   💡 Mean Reversion: {abs(consecutive_days)} down days + RSI {rsi:.1f} - Boost: {reversion_boost:+.3f}")
        
        # FIX #3: GAP EXTENSION CHECK (Already gapped up/down significantly)
        gap_pct = gap_psych['gap_pct']
        if abs(gap_pct) > 1.5:  # Significant gap
            if gap_pct > 1.5 and rsi > 65:  # Gap up + overbought
                extension_penalty = -0.020
                total_score += extension_penalty
                print(f"   ⚠️ Gap Extension: +{gap_pct:.2f}% gap + RSI {rsi:.1f} - Penalty: {extension_penalty:.3f}")
            elif gap_pct < -1.5 and rsi < 35:  # Gap down + oversold
                extension_boost = 0.020
                total_score += extension_boost
                print(f"   💡 Gap Bounce: {gap_pct:.2f}% gap + RSI {rsi:.1f} - Boost: {extension_boost:+.3f}")
        
        # FIX #4: EXTREME SCORE DAMPENER (Prevent over-optimism)
        original_score = total_score
        if total_score > 0.25:
            excess = total_score - 0.25
            dampened = excess * 0.50
            total_score = 0.25 + dampened
            print(f"   📉 Extreme Bullish: {original_score:+.3f} → {total_score:+.3f} (dampened)")
        elif total_score < -0.25:
            excess = abs(total_score) - 0.25
            dampened = excess * 0.50
            total_score = -0.25 - dampened
            print(f"   📈 Extreme Bearish: {original_score:+.3f} → {total_score:+.3f} (dampened)")
        
        if total_score != original_score:
            print(f"   TOTAL (after fixes):  {total_score:+.3f}")
        else:
            print(f"   ✅ No bias fixes needed")
        
        # 🆕 ENHANCEMENT: Check if overnight prediction suggests gap continuation
        # If huge gap AND weak premarket momentum, gap likely continues
        gap_pct = gap_psych['gap_pct']
        premarket_mom_change = premarket_momentum.get('momentum_change', 0)
        
        gap_continuation_override = False
        
        # Check for GAP CONTINUATION pattern
        if abs(gap_pct) > 5.0:  # Huge gap (>5%)
            # If gap DOWN and weak/no bounce momentum
            if gap_pct < -5.0 and premarket_mom_change < 0.3:
                # Bearish gap with weak/negative momentum = continuation likely
                if tech_score < 0:  # Technical also bearish
                    print(f"\n   🚨 GAP CONTINUATION DETECTED:")
                    print(f"      Huge gap DOWN: {gap_pct:.2f}%")
                    print(f"      Weak premarket momentum: {premarket_mom_change:+.2f}%")
                    print(f"      Bearish technical trend")
                    print(f"      → Predicting CONTINUATION, not bounce!")
                    
                    # Override score to predict continuation
                    gap_continuation_override = True
                    continuation_penalty = -0.15  # Force bearish
                    total_score += continuation_penalty
                    
                    print(f"      Continuation Penalty: {continuation_penalty:.3f}")
                    print(f"      Adjusted Total: {total_score:+.3f}")
            
            # If gap UP and weak/no momentum
            elif gap_pct > 5.0 and premarket_mom_change > -0.3:
                # Bullish gap with weak/positive momentum = continuation likely
                if tech_score > 0:  # Technical also bullish
                    print(f"\n   🚀 GAP CONTINUATION DETECTED:")
                    print(f"      Huge gap UP: {gap_pct:.2f}%")
                    print(f"      Positive premarket momentum: {premarket_mom_change:+.2f}%")
                    print(f"      Bullish technical trend")
                    print(f"      → Predicting CONTINUATION, not pullback!")
                    
                    gap_continuation_override = True
                    continuation_boost = 0.15  # Force bullish
                    total_score += continuation_boost
                    
                    print(f"      Continuation Boost: {continuation_boost:.3f}")
                    print(f"      Adjusted Total: {total_score:+.3f}")
        
        # Standard momentum note
        if not gap_continuation_override and abs(premarket_momentum.get('momentum_change', 0)) > 0.3:
            print(f"\n   💡 NOTE: Premarket conditions may differ from overnight prediction!")
            if premarket_momentum['momentum_direction'] == 'bullish':
                print(f"      Bullish premarket momentum detected")
            elif premarket_momentum['momentum_direction'] == 'bearish':
                print(f"      Bearish premarket momentum detected")
            if abs(premarket_momentum['momentum_change']) > 0.5:
                print(f"      Strong premarket momentum - may override overnight signals")
            else:
                print(f"      Large gap detected - gap fill psychology active")
        
        # Determine direction and confidence
        if total_score >= 0.04:
            direction = "UP"
            if abs(total_score) <= 0.10:
                confidence = 55 + abs(total_score) * 125
            else:
                confidence = 67.5 + (abs(total_score) - 0.10) * 115
            confidence = min(confidence, 88)
        elif total_score <= -0.04:
            direction = "DOWN"
            if abs(total_score) <= 0.10:
                confidence = 55 + abs(total_score) * 125
            else:
                confidence = 67.5 + (abs(total_score) - 0.10) * 115
            confidence = min(confidence, 88)
        else:
            direction = "NEUTRAL"
            confidence = 50
        
        # Calculate target for OPENING MOVE (1 hour horizon)
        # Opening moves are MUCH smaller than overnight moves
        base_vol = self.stock_config.get('typical_volatility', 0.015)
        
        # Opening moves are typically 20-40% of overnight moves
        # Start conservative
        opening_volatility = base_vol * 0.25  # 25% of overnight volatility as base
        
        # Adjust based on gap size (larger gaps = more volatile opens)
        gap_size = gap_psych['gap_size']
        if gap_size > 4:
            gap_mult = 1.4  # Large gaps = volatile opens
        elif gap_size > 2:
            gap_mult = 1.2  # Moderate gaps = somewhat volatile
        elif gap_size > 1:
            gap_mult = 1.1  # Small gaps = slightly more
        else:
            gap_mult = 1.0  # Tiny gaps = normal
        
        # Confidence adjustment (modest)
        if confidence >= 80:
            conf_mult = 1.15  # Very high confidence = 15% larger
        elif confidence >= 70:
            conf_mult = 1.08  # High confidence = 8% larger
        else:
            conf_mult = 1.0
        
        # Score magnitude (only for strong signals)
        score_mag = abs(total_score)
        if score_mag > 0.30:
            score_mult = 1.20  # Very strong signal = 20% larger
        elif score_mag > 0.20:
            score_mult = 1.10  # Strong signal = 10% larger
        else:
            score_mult = 1.0
        
        # Premarket momentum boost (strong momentum = larger opening move)
        if premarket_momentum['has_data']:
            momentum_mag = abs(premarket_momentum['momentum_change'])
            if momentum_mag > 0.5:
                momentum_mult = 1.25  # Strong momentum
            elif momentum_mag > 0.3:
                momentum_mult = 1.12  # Moderate momentum
            else:
                momentum_mult = 1.0
        else:
            momentum_mult = 1.0
        
        # Calculate dynamic volatility
        dynamic_volatility = opening_volatility * gap_mult * conf_mult * score_mult * momentum_mult
        
        # Cap at reasonable opening move
        # Typical opening moves: AMD $1-3, AVGO $2-4, ORCL $2-5
        max_opening_move = base_vol * 0.45  # Max 45% of overnight vol
        min_opening_move = base_vol * 0.15  # Min 15% of overnight vol (avoid tiny targets)
        
        dynamic_volatility = max(min_opening_move, min(dynamic_volatility, max_opening_move))
        
        print(f"\n🎯 Opening Move Calculation:")
        print(f"   Base Opening Volatility: {opening_volatility*100:.2f}%")
        print(f"   Gap Multiplier: {gap_mult:.2f}x (gap: {gap_size:.1f}%)")
        print(f"   Confidence Multiplier: {conf_mult:.2f}x")
        print(f"   Score Multiplier: {score_mult:.2f}x")
        print(f"   Momentum Multiplier: {momentum_mult:.2f}x")
        print(f"   Final Opening Move: {dynamic_volatility*100:.2f}%")
        
        # Calculate target
        if direction == "UP":
            target_price = current_price * (1 + dynamic_volatility)
        elif direction == "DOWN":
            target_price = current_price * (1 - dynamic_volatility)
        else:
            target_price = current_price
        
        expected_change = target_price - current_price
        expected_change_pct = (expected_change / current_price) * 100
        
        # Display results
        print("\n" + "="*80)
        print("🎯 PREMARKET-TO-OPEN PREDICTION")
        print("="*80)
        print(f"\n{'📈' if direction=='UP' else '📉' if direction=='DOWN' else '➡️'} DIRECTION: {direction}")
        print(f"🎲 CONFIDENCE: {confidence:.1f}%")
        print(f"🌅 PREMARKET PRICE: ${current_price:.2f} (current)")
        print(f"🎯 EXPECTED OPEN (9:30 AM): ${target_price:.2f}")
        print(f"📊 EXPECTED MOVE: ${expected_change:+.2f} ({expected_change_pct:+.2f}%)")
        print(f"⏱️ TIME HORIZON: ~1 hour (premarket → open)")
        print(f"📈 SCORE: {total_score:+.3f}")
        
        print(f"\n" + "-"*80)
        print(f"💡 TRADING DECISION:")
        if direction == "NEUTRAL":
            print(f"   ⏸️ WAIT - Conflicting signals, stay on sidelines")
        elif confidence >= 70:
            action = "BUY" if direction == "UP" else "SELL/SHORT"
            print(f"   ✅ {action} at premarket")
            print(f"   🎯 Target: ${target_price:.2f} at 9:30 AM open")
            print(f"   ⏰ Hold for ~1 hour (premarket → open)")
        else:
            print(f"   ⚠️ MODERATE CONFIDENCE - Smaller position or wait")
        
        print("="*80)
        
        return {
            'direction': direction,
            'confidence': confidence,
            'premarket_price': current_price,
            'yesterday_close': yesterday_close,
            'gap_pct': gap_psych['gap_pct'],
            'target_price': target_price,
            'expected_change': expected_change,
            'expected_move_pct': expected_change_pct,
            'total_score': total_score,
            'gap_psychology': gap_psych,
            'time_horizon': '1 hour (premarket → open)'
        }


if __name__ == "__main__":
    import sys
    
    # Get symbol from command line argument or use default
    symbol = sys.argv[1] if len(sys.argv) > 1 else None
    
    try:
        predictor = PremarketOpenPredictor(symbol=symbol)
        prediction = predictor.generate_premarket_prediction()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
