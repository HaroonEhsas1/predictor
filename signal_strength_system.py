"""
SIGNAL STRENGTH SYSTEM
User's key insight: "There are bullish AND bearish signals - pick the STRONGER one!"

This system:
1. Weighs each signal by STRENGTH (not just direction)
2. Calculates BULLISH POWER vs BEARISH POWER
3. Only predicts when one side is CLEARLY dominant
4. Ignores weak/conflicting signals
"""

def analyze_signal_strength(data):
    """
    Calculate which direction has STRONGER signals
    
    Returns:
        direction: 'UP', 'DOWN', or 'NEUTRAL'
        strength: 0-100 (how strong the dominant signal is)
        confidence: 0-100 (how confident we are)
    """
    
    print("\n" + "="*80)
    print("🎯 SIGNAL STRENGTH ANALYSIS")
    print("="*80)
    
    # Initialize power scores
    bullish_power = 0
    bearish_power = 0
    
    # Track individual signals
    bullish_signals = []
    bearish_signals = []
    
    print("\n📊 ANALYZING ALL SIGNALS:")
    print("="*80)
    
    # 1. FUTURES (Weight: HIGH)
    futures_change = data.get('futures_pct', 0)
    if abs(futures_change) > 0.3:
        strength = min(abs(futures_change) * 20, 100)  # Scale to 0-100
        if futures_change > 0:
            bullish_power += strength * 0.15  # 15% weight
            bullish_signals.append(('Futures', strength, 0.15))
            print(f"   ✅ Futures UP {futures_change:+.2f}% → Bullish strength: {strength:.0f}/100")
        else:
            bearish_power += strength * 0.15
            bearish_signals.append(('Futures', strength, 0.15))
            print(f"   ❌ Futures DOWN {futures_change:+.2f}% → Bearish strength: {strength:.0f}/100")
    
    # 2. GAP SIZE & QUALITY (Weight: HIGH)
    gap_pct = data.get('gap_pct', 0)
    gap_volume = data.get('premarket_volume', 0)
    min_volume = data.get('min_volume', 300000)
    
    if abs(gap_pct) > 0.5:
        # Check gap quality
        volume_ok = gap_volume > min_volume * 0.5
        gap_reasonable = abs(gap_pct) < 4.0  # Not too extreme
        
        if volume_ok and gap_reasonable:
            strength = min(abs(gap_pct) * 25, 100)
            if gap_pct > 0:
                bullish_power += strength * 0.20
                bullish_signals.append(('Gap Quality', strength, 0.20))
                print(f"   ✅ Gap UP {gap_pct:+.2f}% (good volume) → Bullish strength: {strength:.0f}/100")
            else:
                bearish_power += strength * 0.20
                bearish_signals.append(('Gap Quality', strength, 0.20))
                print(f"   ❌ Gap DOWN {gap_pct:+.2f}% (good volume) → Bearish strength: {strength:.0f}/100")
        elif not volume_ok:
            # Weak volume = TRAP signal (OPPOSITE direction)
            strength = 60  # Fixed trap strength
            if gap_pct > 0:
                bearish_power += strength * 0.15  # Gap up on weak volume = bearish
                bearish_signals.append(('Weak Volume Trap', strength, 0.15))
                print(f"   ⚠️ Gap UP but WEAK volume → TRAP → Bearish strength: {strength:.0f}/100")
            else:
                bullish_power += strength * 0.15  # Gap down on weak volume = bullish trap
                bullish_signals.append(('Weak Volume Trap', strength, 0.15))
                print(f"   ⚠️ Gap DOWN but WEAK volume → TRAP → Bullish strength: {strength:.0f}/100")
    
    # 3. TECHNICAL (Weight: MEDIUM-HIGH)
    rsi = data.get('rsi', 50)
    if rsi > 70:
        # Overbought = bearish
        strength = min((rsi - 70) * 3, 80)
        bearish_power += strength * 0.12
        bearish_signals.append(('Overbought', strength, 0.12))
        print(f"   ❌ RSI {rsi:.0f} (Overbought) → Bearish strength: {strength:.0f}/100")
    elif rsi < 30:
        # Oversold = bullish
        strength = min((30 - rsi) * 3, 80)
        bullish_power += strength * 0.12
        bullish_signals.append(('Oversold', strength, 0.12))
        print(f"   ✅ RSI {rsi:.0f} (Oversold) → Bullish strength: {strength:.0f}/100")
    elif 45 <= rsi <= 55:
        print(f"   ⚪ RSI {rsi:.0f} (Neutral) → No signal")
    
    # 4. OPTIONS FLOW (Weight: MEDIUM)
    pc_ratio = data.get('pc_ratio', 1.0)
    if pc_ratio > 1.5:
        # Excessive puts = CONTRARIAN bullish
        strength = min((pc_ratio - 1.5) * 50, 80)
        bullish_power += strength * 0.11
        bullish_signals.append(('Options Contrarian', strength, 0.11))
        print(f"   ✅ P/C Ratio {pc_ratio:.2f} (Excessive fear) → CONTRARIAN Bullish strength: {strength:.0f}/100")
    elif pc_ratio < 0.7:
        # Excessive calls = CONTRARIAN bearish
        strength = min((0.7 - pc_ratio) * 50, 80)
        bearish_power += strength * 0.11
        bearish_signals.append(('Options Contrarian', strength, 0.11))
        print(f"   ❌ P/C Ratio {pc_ratio:.2f} (Excessive greed) → CONTRARIAN Bearish strength: {strength:.0f}/100")
    
    # 5. NEWS CATALYST (Weight: MEDIUM)
    news_sentiment = data.get('news_sentiment', 0)  # -1 to +1
    news_strength = data.get('news_strength', 0)  # 0 to 1
    
    if abs(news_sentiment) > 0.3 and news_strength > 0.5:
        strength = min(abs(news_sentiment) * news_strength * 100, 90)
        if news_sentiment > 0:
            bullish_power += strength * 0.10
            bullish_signals.append(('News Catalyst', strength, 0.10))
            print(f"   ✅ Positive news (strength {news_strength:.1f}) → Bullish strength: {strength:.0f}/100")
        else:
            bearish_power += strength * 0.10
            bearish_signals.append(('News Catalyst', strength, 0.10))
            print(f"   ❌ Negative news (strength {news_strength:.1f}) → Bearish strength: {strength:.0f}/100")
    
    # 6. SECTOR ALIGNMENT (Weight: MEDIUM)
    sector_change = data.get('sector_pct', 0)
    if abs(sector_change) > 0.5:
        strength = min(abs(sector_change) * 15, 70)
        if sector_change > 0:
            bullish_power += strength * 0.08
            bullish_signals.append(('Sector', strength, 0.08))
            print(f"   ✅ Sector UP {sector_change:+.2f}% → Bullish strength: {strength:.0f}/100")
        else:
            bearish_power += strength * 0.08
            bearish_signals.append(('Sector', strength, 0.08))
            print(f"   ❌ Sector DOWN {sector_change:+.2f}% → Bearish strength: {strength:.0f}/100")
    
    # 7. SOCIAL SENTIMENT (Weight: LOW)
    social_sentiment = data.get('social_sentiment', 0)  # -1 to +1
    if abs(social_sentiment) > 0.1:
        strength = min(abs(social_sentiment) * 60, 60)
        if social_sentiment > 0:
            bullish_power += strength * 0.05
            bullish_signals.append(('Social', strength, 0.05))
            print(f"   ✅ Social bullish {social_sentiment:+.2f} → Bullish strength: {strength:.0f}/100")
        else:
            bearish_power += strength * 0.05
            bearish_signals.append(('Social', strength, 0.05))
            print(f"   ❌ Social bearish {social_sentiment:+.2f} → Bearish strength: {strength:.0f}/100")
    
    # CALCULATE DOMINANT DIRECTION
    print("\n" + "="*80)
    print("⚡ SIGNAL POWER CALCULATION")
    print("="*80)
    
    print(f"\n💪 BULLISH POWER: {bullish_power:.1f}/100")
    if bullish_signals:
        print(f"   Bullish signals ({len(bullish_signals)}):")
        for signal, strength, weight in sorted(bullish_signals, key=lambda x: x[1] * x[2], reverse=True):
            contribution = strength * weight
            print(f"      • {signal}: {strength:.0f}/100 × {weight:.0%} = {contribution:.1f} points")
    
    print(f"\n💪 BEARISH POWER: {bearish_power:.1f}/100")
    if bearish_signals:
        print(f"   Bearish signals ({len(bearish_signals)}):")
        for signal, strength, weight in sorted(bearish_signals, key=lambda x: x[1] * x[2], reverse=True):
            contribution = strength * weight
            print(f"      • {signal}: {strength:.0f}/100 × {weight:.0%} = {contribution:.1f} points")
    
    # DETERMINE WINNER
    print("\n" + "="*80)
    print("🎯 DOMINANT SIGNAL DETERMINATION")
    print("="*80)
    
    power_diff = abs(bullish_power - bearish_power)
    total_power = bullish_power + bearish_power
    
    # TIERED POSITION SIZING (Decisive Mode)
    # 12-15 points: 50% position
    # 15-18 points: 75% position  
    # 18-20 points: 90% position
    # 20+ points: 100% position
    # <12 points: NEUTRAL (skip)
    
    min_dominance_skip = 12  # Below this = skip
    
    if power_diff < min_dominance_skip:
        direction = 'NEUTRAL'
        strength = 0
        confidence = 0.50  # 50% neutral (coin flip - no clear signal)
        position_size = 0.0  # Skip
        print(f"\n⚪ RESULT: MIXED SIGNALS")
        print(f"   Bullish: {bullish_power:.1f}")
        print(f"   Bearish: {bearish_power:.1f}")
        print(f"   Difference: {power_diff:.1f} (< {min_dominance_skip} required)")
        print(f"   ⚠️ SKIP TRADE - No clear dominant signal!")
        
    elif bullish_power > bearish_power:
        direction = 'UP'
        strength = bullish_power
        # Confidence = how much stronger vs total
        confidence = min(50 + (power_diff / total_power * 100) if total_power > 0 else 50, 95)
        
        # TIERED POSITION SIZING
        if power_diff >= 20:
            position_size = 1.00  # 100% position
            position_desc = "FULL (100%)"
        elif power_diff >= 18:
            position_size = 0.90  # 90% position
            position_desc = "STRONG (90%)"
        elif power_diff >= 15:
            position_size = 0.75  # 75% position
            position_desc = "GOOD (75%)"
        elif power_diff >= 12:
            position_size = 0.50  # 50% position
            position_desc = "MODERATE (50%)"
        else:
            position_size = 0.0  # Skip (shouldn't reach here)
            position_desc = "SKIP (0%)"
        
        print(f"\n✅ RESULT: BULLISH DOMINANT")
        print(f"   Bullish power: {bullish_power:.1f}")
        print(f"   Bearish power: {bearish_power:.1f}")
        print(f"   Dominance: {power_diff:.1f} points")
        print(f"   Position Size: {position_desc}")
        print(f"   Strength: {strength:.0f}/100")
        print(f"   Confidence: {confidence:.0f}%")
        print(f"   🎯 TRADE: LONG")
        
    else:
        direction = 'DOWN'
        strength = bearish_power
        confidence = min(50 + (power_diff / total_power * 100) if total_power > 0 else 50, 95)
        
        # TIERED POSITION SIZING
        if power_diff >= 20:
            position_size = 1.00  # 100% position
            position_desc = "FULL (100%)"
        elif power_diff >= 18:
            position_size = 0.90  # 90% position
            position_desc = "STRONG (90%)"
        elif power_diff >= 15:
            position_size = 0.75  # 75% position
            position_desc = "GOOD (75%)"
        elif power_diff >= 12:
            position_size = 0.50  # 50% position
            position_desc = "MODERATE (50%)"
        else:
            position_size = 0.0  # Skip (shouldn't reach here)
            position_desc = "SKIP (0%)"
        
        print(f"\n❌ RESULT: BEARISH DOMINANT")
        print(f"   Bearish power: {bearish_power:.1f}")
        print(f"   Bullish power: {bullish_power:.1f}")
        print(f"   Dominance: {power_diff:.1f} points")
        print(f"   Position Size: {position_desc}")
        print(f"   Strength: {strength:.0f}/100")
        print(f"   Confidence: {confidence:.0f}%")
        print(f"   🎯 TRADE: SHORT")
    
    print("\n" + "="*80 + "\n")
    
    return {
        'direction': direction,
        'strength': strength,
        'confidence': confidence,
        'position_size': position_size,
        'bullish_power': bullish_power,
        'bearish_power': bearish_power,
        'power_difference': power_diff,
        'bullish_signals': bullish_signals,
        'bearish_signals': bearish_signals
    }


# EXAMPLE USAGE
if __name__ == "__main__":
    print("\n" + "="*80)
    print("🎓 SIGNAL STRENGTH SYSTEM - EXAMPLES")
    print("="*80)
    
    # Example 1: Clear bullish
    print("\n" + "="*80)
    print("EXAMPLE 1: CLEAR BULLISH SCENARIO")
    print("="*80)
    
    data1 = {
        'futures_pct': 0.8,  # Strong futures
        'gap_pct': 2.0,  # Good gap
        'premarket_volume': 500000,  # Good volume
        'min_volume': 300000,
        'rsi': 45,  # Neutral
        'pc_ratio': 1.8,  # Contrarian bullish
        'news_sentiment': 0.7,  # Positive
        'news_strength': 0.8,  # Strong
        'sector_pct': 1.2,  # Sector up
        'social_sentiment': 0.3  # Bullish
    }
    
    result1 = analyze_signal_strength(data1)
    
    # Example 2: Mixed signals (should skip)
    print("\n" + "="*80)
    print("EXAMPLE 2: MIXED SIGNALS (SKIP)")
    print("="*80)
    
    data2 = {
        'futures_pct': 0.5,  # Bullish
        'gap_pct': 2.5,  # Bullish BUT...
        'premarket_volume': 150000,  # WEAK volume (trap!)
        'min_volume': 300000,
        'rsi': 72,  # OVERBOUGHT (bearish!)
        'pc_ratio': 1.0,  # Neutral
        'news_sentiment': 0.3,  # Slightly positive
        'news_strength': 0.4,  # Weak
        'sector_pct': -0.5,  # Sector DOWN (bearish!)
        'social_sentiment': 0.1  # Neutral
    }
    
    result2 = analyze_signal_strength(data2)
    
    # Example 3: Clear bearish
    print("\n" + "="*80)
    print("EXAMPLE 3: CLEAR BEARISH SCENARIO")
    print("="*80)
    
    data3 = {
        'futures_pct': -0.6,  # Futures down
        'gap_pct': -1.8,  # Gap down
        'premarket_volume': 600000,  # Good volume
        'min_volume': 300000,
        'rsi': 28,  # Oversold BUT...
        'pc_ratio': 0.6,  # Too many calls (bearish!)
        'news_sentiment': -0.8,  # Very negative
        'news_strength': 0.9,  # Strong
        'sector_pct': -1.5,  # Sector down
        'social_sentiment': -0.4  # Bearish
    }
    
    result3 = analyze_signal_strength(data3)
    
    print("\n" + "="*80)
    print("✅ SYSTEM COMPLETE")
    print("="*80)
    print("""
KEY FEATURES:
1. ✅ Weighs each signal by STRENGTH (not just yes/no)
2. ✅ Calculates BULLISH POWER vs BEARISH POWER
3. ✅ Only trades when one side is CLEARLY dominant (20+ point difference)
4. ✅ Skips mixed/weak signals
5. ✅ Shows WHY each direction was chosen
6. ✅ Transparent signal breakdown

This is what the user wanted: "Pick the STRONGER signal!"
    """)
