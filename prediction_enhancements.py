#!/usr/bin/env python3
"""
Prediction Enhancements - Fixes for Improved Accuracy
Implements 4 critical fixes identified from AMD prediction error

Created: October 23, 2025
Target: Improve accuracy from 66.7% to 75%+
"""

def enhanced_options_analysis(p_c_ratio, call_volume=None, put_volume=None):
    """
    Enhanced options P/C ratio interpretation with CONTRARIAN logic
    
    Fix #1: Add contrarian interpretation for excessive hedging
    
    Args:
        p_c_ratio: Put/Call ratio
        call_volume: Optional call volume for additional context
        put_volume: Optional put volume for additional context
    
    Returns:
        tuple: (score, interpretation, signal_type)
    """
    
    print(f"\n🔍 ENHANCED OPTIONS ANALYSIS:")
    print(f"   P/C Ratio: {p_c_ratio:.2f}")
    
    # CONTRARIAN LOGIC
    if p_c_ratio < 0.7:
        # Strong call buying = Bullish
        score = +1.00
        interpretation = "BULLISH"
        signal_type = "Strong call buying (institutions bullish)"
        confidence = "HIGH"
        
    elif 0.7 <= p_c_ratio < 1.0:
        # Moderate call bias = Bullish
        score = +0.50
        interpretation = "MODERATELY BULLISH"
        signal_type = "Call bias (mild bullish positioning)"
        confidence = "MODERATE"
        
    elif 1.0 <= p_c_ratio <= 1.3:
        # Normal hedging = Neutral
        score = 0.00
        interpretation = "NEUTRAL"
        signal_type = "Normal hedging activity (no edge)"
        confidence = "LOW"
        
    elif 1.3 < p_c_ratio <= 1.5:
        # Elevated hedging = Slight contrarian bullish
        score = +0.20
        interpretation = "SLIGHT CONTRARIAN BULLISH"
        signal_type = "Elevated hedging (mild fear, potential bottom)"
        confidence = "MODERATE"
        
    elif p_c_ratio > 1.5:
        # CRITICAL FIX: Excessive hedging = CONTRARIAN BULLISH!
        score = +0.50
        interpretation = "CONTRARIAN BULLISH"
        signal_type = "EXCESSIVE hedging (max fear = bottom signal)"
        confidence = "HIGH"
        
    else:
        score = 0.00
        interpretation = "NEUTRAL"
        signal_type = "Unknown"
        confidence = "LOW"
    
    print(f"   Interpretation: {interpretation}")
    print(f"   Signal: {signal_type}")
    print(f"   Score: {score:+.2f}")
    print(f"   Confidence: {confidence}")
    
    # Additional context from volume if available
    if call_volume and put_volume:
        volume_ratio = call_volume / put_volume if put_volume > 0 else 0
        print(f"   Call Volume: {call_volume:,.0f}")
        print(f"   Put Volume: {put_volume:,.0f}")
        print(f"   Volume Ratio: {volume_ratio:.2f}")
    
    return score, interpretation, signal_type


def enhanced_rsi_analysis(rsi):
    """
    Enhanced RSI interpretation with NUANCED ZONES
    
    Fix #2: More sophisticated RSI thresholds
    
    Args:
        rsi: RSI value (0-100)
    
    Returns:
        tuple: (score, interpretation, zone)
    """
    
    print(f"\n🔍 ENHANCED RSI ANALYSIS:")
    print(f"   RSI: {rsi:.1f}")
    
    if rsi < 25:
        # Extremely oversold = Strong bounce potential
        score = +1.00
        interpretation = "STRONG BULLISH"
        zone = "Extremely oversold (panic selling)"
        
    elif 25 <= rsi < 35:
        # Oversold = Bounce likely
        score = +0.60
        interpretation = "BULLISH"
        zone = "Oversold (bounce zone)"
        
    elif 35 <= rsi < 45:
        # Approaching neutral from below = Slight bullish bias
        score = +0.20
        interpretation = "SLIGHT BULLISH"
        zone = "Below neutral (approaching oversold)"
        
    elif 45 <= rsi <= 55:
        # CRITICAL FIX: Neutral zone = No edge
        score = 0.00
        interpretation = "NEUTRAL"
        zone = "Neutral zone (no directional edge)"
        
    elif 55 < rsi <= 65:
        # Approaching overbought = Slight bearish bias
        score = -0.20
        interpretation = "SLIGHT BEARISH"
        zone = "Above neutral (approaching overbought)"
        
    elif 65 < rsi <= 75:
        # Overbought = Reversal likely
        score = -0.60
        interpretation = "BEARISH"
        zone = "Overbought (reversal zone)"
        
    else:  # rsi > 75
        # Extremely overbought = Strong reversal potential
        score = -1.00
        interpretation = "STRONG BEARISH"
        zone = "Extremely overbought (euphoria)"
    
    print(f"   Zone: {zone}")
    print(f"   Interpretation: {interpretation}")
    print(f"   Score: {score:+.2f}")
    
    return score, interpretation, zone


def enhanced_sector_analysis(stock_change, sector_change, stock_symbol):
    """
    Enhanced sector correlation with RELATIVE STRENGTH check
    
    Fix #3: Account for stock-specific beta and divergence
    
    Args:
        stock_change: Stock's % change
        sector_change: Sector ETF % change
        stock_symbol: Stock ticker for beta lookup
    
    Returns:
        tuple: (score, interpretation, relative_strength)
    """
    
    print(f"\n🔍 ENHANCED SECTOR ANALYSIS:")
    print(f"   Stock: {stock_change:+.2f}%")
    print(f"   Sector: {sector_change:+.2f}%")
    
    # Calculate relative strength
    relative_strength = stock_change - sector_change
    
    print(f"   Relative Strength: {relative_strength:+.2f}%")
    
    # Stock-specific beta (approximate)
    beta_map = {
        'AMD': 1.5,   # High beta
        'NVDA': 1.4,
        'AVGO': 1.1,  # Moderate beta
        'ORCL': 0.9,  # Lower beta
    }
    
    beta = beta_map.get(stock_symbol, 1.0)
    print(f"   Beta (vs sector): {beta:.1f}x")
    
    # CRITICAL FIX: Check if stock is diverging from sector
    if sector_change < -1.0:  # Sector weak
        if relative_strength > 0.5:
            # Stock outperforming weak sector = BULLISH
            score = +0.30
            interpretation = "BULLISH (Relative Strength)"
            signal = f"Outperforming sector by {relative_strength:+.2f}%"
            
        elif relative_strength > -0.5:
            # Stock holding up = Neutral
            score = 0.00
            interpretation = "NEUTRAL (Holding Up)"
            signal = "Not following sector weakness"
            
        else:
            # Stock following sector down = Bearish (but reduced weight)
            score = -0.10  # REDUCED from -0.20
            interpretation = "SLIGHT BEARISH"
            signal = "Following sector weakness (reduced impact)"
    
    elif sector_change > 1.0:  # Sector strong
        if relative_strength > 0.5:
            # Stock outperforming strong sector = Very bullish
            score = +0.40
            interpretation = "VERY BULLISH (Leadership)"
            signal = f"Leading sector higher by {relative_strength:+.2f}%"
            
        elif relative_strength > -0.5:
            # Stock following sector up = Bullish
            score = +0.20
            interpretation = "BULLISH"
            signal = "Following sector strength"
            
        else:
            # Stock underperforming = Neutral/weak
            score = 0.00
            interpretation = "NEUTRAL (Underperforming)"
            signal = "Lagging sector strength"
    
    else:  # Sector neutral
        if abs(relative_strength) > 0.5:
            score = +0.15 if relative_strength > 0 else -0.15
            interpretation = "BULLISH" if relative_strength > 0 else "BEARISH"
            signal = "Stock diverging from neutral sector"
        else:
            score = 0.00
            interpretation = "NEUTRAL"
            signal = "Moving with sector"
    
    print(f"   Interpretation: {interpretation}")
    print(f"   Signal: {signal}")
    print(f"   Score: {score:+.2f}")
    
    return score, interpretation, relative_strength


def enhanced_reddit_analysis(reddit_score, mention_count):
    """
    Enhanced Reddit sentiment with THRESHOLD for extremes
    
    Fix #4: Only fade when extremely euphoric
    
    Args:
        reddit_score: Reddit sentiment score (0.0 to 1.0)
        mention_count: Number of mentions
    
    Returns:
        tuple: (score, interpretation, signal_type)
    """
    
    print(f"\n🔍 ENHANCED REDDIT ANALYSIS:")
    print(f"   Reddit Score: {reddit_score:.3f}")
    print(f"   Mentions: {mention_count}")
    
    # CRITICAL FIX: Only use contrarian when EXTREME
    if reddit_score > 0.15:
        # EXTREME euphoria = Contrarian bearish (top signal)
        score = -0.50
        interpretation = "CONTRARIAN BEARISH"
        signal_type = "EXTREME euphoria (WSB mania = top)"
        
    elif 0.10 < reddit_score <= 0.15:
        # High euphoria = Slight contrarian bearish
        score = -0.20
        interpretation = "SLIGHT CONTRARIAN BEARISH"
        signal_type = "High euphoria (approaching mania)"
        
    elif 0.02 <= reddit_score <= 0.10:
        # CRITICAL FIX: Modest positive = Take at face value!
        score = +0.30
        interpretation = "BULLISH (Confirming)"
        signal_type = "MODEST interest (take at face value)"
        
    elif -0.10 <= reddit_score < 0.02:
        # Neutral to slight negative
        score = 0.00
        interpretation = "NEUTRAL"
        signal_type = "Low/no interest (no edge)"
        
    elif -0.15 <= reddit_score < -0.10:
        # Negative sentiment = Contrarian bullish
        score = +0.20
        interpretation = "SLIGHT CONTRARIAN BULLISH"
        signal_type = "Negative sentiment (potential bottom)"
        
    else:  # reddit_score < -0.15
        # Extreme bearishness = Strong contrarian bullish
        score = +0.50
        interpretation = "CONTRARIAN BULLISH"
        signal_type = "EXTREME bearishness (panic = bottom)"
    
    print(f"   Interpretation: {interpretation}")
    print(f"   Signal: {signal_type}")
    print(f"   Score: {score:+.2f}")
    
    return score, interpretation, signal_type


def apply_all_enhancements(prediction_data):
    """
    Apply all enhancements to a prediction
    
    Args:
        prediction_data: Dictionary with raw signals
    
    Returns:
        dict: Enhanced scores
    """
    
    print("\n" + "="*80)
    print("🔧 APPLYING PREDICTION ENHANCEMENTS")
    print("="*80)
    
    enhanced = {}
    
    # Apply options enhancement
    if 'p_c_ratio' in prediction_data:
        score, interp, signal = enhanced_options_analysis(
            prediction_data['p_c_ratio'],
            prediction_data.get('call_volume'),
            prediction_data.get('put_volume')
        )
        enhanced['options_score'] = score
        enhanced['options_interpretation'] = interp
    
    # Apply RSI enhancement
    if 'rsi' in prediction_data:
        score, interp, zone = enhanced_rsi_analysis(prediction_data['rsi'])
        enhanced['rsi_score'] = score
        enhanced['rsi_interpretation'] = interp
    
    # Apply sector enhancement
    if 'stock_change' in prediction_data and 'sector_change' in prediction_data:
        score, interp, rel_str = enhanced_sector_analysis(
            prediction_data['stock_change'],
            prediction_data['sector_change'],
            prediction_data.get('symbol', 'UNKNOWN')
        )
        enhanced['sector_score'] = score
        enhanced['sector_interpretation'] = interp
    
    # Apply Reddit enhancement
    if 'reddit_score' in prediction_data:
        score, interp, signal = enhanced_reddit_analysis(
            prediction_data['reddit_score'],
            prediction_data.get('reddit_mentions', 0)
        )
        enhanced['reddit_score'] = score
        enhanced['reddit_interpretation'] = interp
    
    print("\n" + "="*80)
    print("✅ ENHANCEMENTS APPLIED")
    print("="*80)
    
    return enhanced


# Test function
if __name__ == "__main__":
    print("\n" + "="*80)
    print("🧪 TESTING PREDICTION ENHANCEMENTS")
    print("="*80)
    
    # Test AMD scenario (what went wrong)
    print("\n📊 TEST CASE: AMD (Oct 23, 2025)")
    print("─"*80)
    
    amd_data = {
        'symbol': 'AMD',
        'p_c_ratio': 1.2,
        'rsi': 45,
        'stock_change': -0.5,
        'sector_change': -2.36,
        'reddit_score': 0.040,
        'reddit_mentions': 50
    }
    
    print("\nRAW DATA:")
    for key, value in amd_data.items():
        print(f"   {key}: {value}")
    
    enhanced = apply_all_enhancements(amd_data)
    
    print("\n📊 ENHANCED SCORES:")
    for key, value in enhanced.items():
        if 'score' in key:
            print(f"   {key}: {value:+.2f}")
        else:
            print(f"   {key}: {value}")
    
    # Calculate corrected prediction
    total_enhanced = (
        enhanced.get('options_score', 0) * 0.11 +
        enhanced.get('rsi_score', 0) * 0.08 +
        enhanced.get('sector_score', 0) * 0.06 +
        enhanced.get('reddit_score', 0) * 0.08
    )
    
    print(f"\n🎯 CORRECTED PREDICTION:")
    print(f"   Original Score: -0.087 (DOWN)")
    print(f"   Enhanced Score: {total_enhanced:+.3f}")
    print(f"   Direction: {'UP' if total_enhanced > 0.02 else 'DOWN' if total_enhanced < -0.02 else 'NEUTRAL'}")
    print(f"   Result: {'✅ CORRECT (AMD went UP)' if total_enhanced > 0 else '❌ STILL WRONG'}")
    
    print("\n" + "="*80)
