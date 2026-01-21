#!/usr/bin/env python3\n"""\nPrediction Output Fixes\n"""\n\n
# Configuration for minimal prediction output
PREDICTION_CONFIG = {
    'verbose_mode': False,
    'show_detailed_analysis': False,
    'show_enhanced_sections': False,
    'max_output_lines': 10,
    'show_only_actionable': True,
    'remove_hardcoded_fallbacks': True
}

def should_show_verbose_output():
    """Check if verbose output should be shown"""
    return PREDICTION_CONFIG.get('verbose_mode', False)

def filter_prediction_output(prediction_text):
    """Filter out noise from prediction output"""
    if PREDICTION_CONFIG.get('show_only_actionable', True):
        # Remove lines with hardcoded 50.0% values
        lines = prediction_text.split('\n')
        filtered_lines = []
        
        noise_patterns = [
            r'.*50\.0%.*NEUTRAL.*',  # Remove 50.0% NEUTRAL lines
            r'.*Advanced Historical Accuracy.*',
            r'.*Technical Confluence.*',
            r'.*ENHANCED ANALYSIS.*',
            r'.*Using ALL available data.*',
            r'.*Analyst Coverage: 50\.0%.*',
            r'.*Dollar/VIX Impact: 50\.0%.*'
        ]
        
        for line in lines:
            should_keep = True
            for pattern in noise_patterns:
                if re.match(pattern, line):
                    should_keep = False
                    break
            
            if should_keep:
                filtered_lines.append(line)
        
        return '\n'.join(filtered_lines)
    
    return prediction_text
\n\n
def display_minimal_prediction(prediction_data):
    """Display clean, minimal prediction without noise"""
    print("\n" + "="*60)
    print(f"🎯 NEXT-DAY PREDICTION - {prediction_data.get('symbol', 'AMD')}")
    print("="*60)
    
    # Essential info only
    direction = prediction_data.get('direction', 'NEUTRAL')
    confidence = prediction_data.get('confidence', 50)
    current_price = prediction_data.get('current_price', 0)
    expected_price = prediction_data.get('expected_price', current_price)
    
    print(f"Direction:      {direction}")
    print(f"Confidence:     {confidence:.0f}%")
    print(f"Current Price:  ${current_price:.2f}")
    print(f"Expected Open:  ${expected_price:.2f}")
    
    # Show price change
    if expected_price != current_price:
        change = expected_price - current_price
        change_pct = (change / current_price) * 100
        print(f"Expected Move:  ${change:+.2f} ({change_pct:+.1f}%)")
    
    # Key reasoning (max 2 factors)
    reasoning = prediction_data.get('reasoning', '')
    if reasoning:
        # Truncate reasoning to key points
        short_reasoning = reasoning[:60] + "..." if len(reasoning) > 60 else reasoning
        print(f"Key Factors:    {short_reasoning}")
    
    # Position size
    position = prediction_data.get('position_size', 'NONE')
    if position and position != 'NONE':
        print(f"Position Size:  {position}")
    
    print("="*60)
\n\n# remove_enhanced_analysis\n
# Replace verbose "ENHANCED ANALYSIS" with minimal summary
def create_minimal_analysis_summary(data):
    """Create minimal analysis instead of verbose output"""
    key_factors = []
    
    # Only include significant factors
    momentum = data.get('momentum_3h', 0)
    if abs(momentum) > 1.0:
        key_factors.append(f"3h momentum: {momentum:+.1f}%")
    
    volume_ratio = data.get('volume_ratio', 1.0)
    if volume_ratio > 1.5:
        key_factors.append("High volume")
    elif volume_ratio < 0.7:
        key_factors.append("Low volume")
    
    volatility = data.get('volatility', 0)
    if volatility > 3.0:
        key_factors.append("High volatility")
    
    return "; ".join(key_factors[:3])  # Max 3 factors
\n\n# remove_hardcoded_values\n
# Remove hardcoded 50.0% values and static calculations
def calculate_real_technical_indicators(price_data):
    """Calculate real technical indicators or return None"""
    if not price_data or len(price_data) < 14:
        return None
    
    # Only calculate if we have real data
    try:
        import pandas as pd
        import numpy as np
        
        df = pd.DataFrame(price_data)
        
        # Real RSI calculation
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return {
            'rsi': rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else None,
            'trend': 'UP' if df['close'].iloc[-1] > df['close'].iloc[-5] else 'DOWN'
        }
    except:
        return None
\n\n# simplified_confidence_calc\n
def calculate_simple_confidence(factors):
    """Simple confidence calculation without noise"""
    base_confidence = 50
    
    # Momentum factor
    momentum = factors.get('momentum', 0)
    base_confidence += min(abs(momentum) * 10, 25)
    
    # Volume factor
    volume_ratio = factors.get('volume_ratio', 1.0)
    if volume_ratio > 1.5:
        base_confidence += 10
    elif volume_ratio < 0.7:
        base_confidence -= 5
    
    # Cap confidence
    return min(max(base_confidence, 30), 85)
\n\n