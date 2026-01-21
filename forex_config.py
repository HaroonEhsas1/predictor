#!/usr/bin/env python3
"""
Forex Configuration - Similar to stock_config.py
For Daily Swing Trading (24-48 hour predictions)
"""

# Forex pairs configuration
FOREX_PAIRS = {
    'EUR/USD': {
        'symbol': 'EURUSD=X',  # Yahoo Finance format
        'name': 'Euro / US Dollar',
        'typical_daily_pips': 70,  # Average daily range
        'typical_volatility': 0.007,  # 0.7% daily
        'spread_pips': 0.5,  # Typical spread
        'pip_value': 0.0001,  # 1 pip = 0.0001
        'min_confidence': 65,  # Higher than stocks (forex harder)
        'session_strength': {
            'asian': 0.3,
            'london': 1.0,
            'ny': 0.9,
            'overlap': 1.0
        }
    },
    'GBP/USD': {
        'symbol': 'GBPUSD=X',
        'name': 'British Pound / US Dollar',
        'typical_daily_pips': 110,
        'typical_volatility': 0.009,  # 0.9% daily
        'spread_pips': 0.8,
        'pip_value': 0.0001,
        'min_confidence': 68,  # More volatile, need higher confidence
        'session_strength': {
            'asian': 0.2,
            'london': 1.0,
            'ny': 0.7,
            'overlap': 0.9
        }
    },
    'USD/JPY': {
        'symbol': 'USDJPY=X',
        'name': 'US Dollar / Japanese Yen',
        'typical_daily_pips': 60,
        'typical_volatility': 0.006,  # 0.6% daily
        'spread_pips': 0.4,
        'pip_value': 0.01,  # JPY pairs: 1 pip = 0.01
        'min_confidence': 65,
        'session_strength': {
            'asian': 0.8,
            'london': 0.7,
            'ny': 0.9,
            'overlap': 1.0
        }
    }
}

# Weight adjustments for forex (daily swing focus)
def get_forex_weight_adjustments(pair):
    """Get weight adjustments for specific forex pair"""
    
    # EUR/USD: Most balanced, fundamentals-driven
    if pair == 'EUR/USD':
        return {
            'interest_rates': 0.20,      # Most important for forex!
            'economic_data': 0.15,        # GDP, CPI, NFP
            'central_bank': 0.10,         # Fed/ECB statements
            'technical': 0.15,            # RSI, MACD, MA
            'dxy': 0.10,                  # Dollar Index
            'risk_sentiment': 0.10,       # VIX, S&P 500
            'cot_positioning': 0.08,      # COT report
            'correlations': 0.07,         # Gold, oil
            'session_time': 0.05          # Time of day
        }
    
    # GBP/USD: More volatile, technical matters more
    elif pair == 'GBP/USD':
        return {
            'interest_rates': 0.18,
            'economic_data': 0.15,
            'central_bank': 0.10,
            'technical': 0.18,            # Higher weight (more volatile)
            'dxy': 0.10,
            'risk_sentiment': 0.10,
            'cot_positioning': 0.07,
            'correlations': 0.07,
            'session_time': 0.05
        }
    
    # USD/JPY: Risk sentiment heavy
    elif pair == 'USD/JPY':
        return {
            'interest_rates': 0.20,
            'economic_data': 0.12,
            'central_bank': 0.10,
            'technical': 0.13,
            'dxy': 0.12,
            'risk_sentiment': 0.15,       # Higher (safe haven pair)
            'cot_positioning': 0.07,
            'correlations': 0.06,
            'session_time': 0.05
        }
    
    # Default
    return {
        'interest_rates': 0.20,
        'economic_data': 0.15,
        'central_bank': 0.10,
        'technical': 0.15,
        'dxy': 0.10,
        'risk_sentiment': 0.10,
        'cot_positioning': 0.08,
        'correlations': 0.07,
        'session_time': 0.05
    }

# Interest rate data (approximate - would need real-time API)
INTEREST_RATES = {
    'USD': 5.50,  # Fed Funds Rate (as of Oct 2025)
    'EUR': 4.00,  # ECB Rate
    'GBP': 5.00,  # BoE Rate
    'JPY': 0.10   # BoJ Rate
}

# Economic calendar (major events - would integrate API)
MAJOR_EVENTS = {
    'NFP': 'High',           # Non-Farm Payrolls (first Friday)
    'CPI': 'High',           # Inflation data
    'GDP': 'High',           # Growth data
    'FOMC': 'Very High',     # Fed meeting
    'ECB': 'Very High',      # ECB meeting
    'BoE': 'Very High',      # BoE meeting
    'PMI': 'Medium',         # Manufacturing data
    'Retail_Sales': 'Medium'
}

def get_forex_config(pair):
    """Get complete configuration for forex pair"""
    if pair not in FOREX_PAIRS:
        raise ValueError(f"Forex pair {pair} not configured")
    
    config = FOREX_PAIRS[pair].copy()
    config['weights'] = get_forex_weight_adjustments(pair)
    
    return config

# Risk management (similar to stocks but adjusted)
FOREX_RISK_MANAGEMENT = {
    'max_risk_per_trade': 0.01,      # 1% max risk (lower than stocks)
    'max_open_positions': 2,          # Max 2 forex pairs at once
    'max_correlation': 0.7,           # Don't trade correlated pairs
    'risk_reward_min': 2.0,           # Higher R:R for forex (2:1)
    'stop_loss_pips': {               # Based on pair
        'EUR/USD': 40,
        'GBP/USD': 60,
        'USD/JPY': 35
    },
    'take_profit_pips': {
        'EUR/USD': 80,                # 2:1 R:R
        'GBP/USD': 120,
        'USD/JPY': 70
    }
}

# Session times (EST)
SESSION_TIMES = {
    'asian': {'start': 19, 'end': 4},      # 7 PM - 4 AM
    'london': {'start': 3, 'end': 12},     # 3 AM - 12 PM
    'ny': {'start': 8, 'end': 17},         # 8 AM - 5 PM
    'overlap': {'start': 8, 'end': 12}     # 8 AM - 12 PM (best time)
}

# Correlation matrix (approximate)
CORRELATIONS = {
    'EUR/USD': {
        'GBP/USD': 0.85,   # High positive
        'USD/JPY': -0.75,  # High negative
        'Gold': 0.70       # Positive
    },
    'GBP/USD': {
        'EUR/USD': 0.85,
        'USD/JPY': -0.65,
        'Gold': 0.60
    },
    'USD/JPY': {
        'EUR/USD': -0.75,
        'GBP/USD': -0.65,
        'SPX': 0.80        # Risk-on correlation
    }
}

if __name__ == "__main__":
    # Test configuration
    print("\n" + "="*80)
    print("FOREX CONFIGURATION TEST")
    print("="*80)
    
    for pair in FOREX_PAIRS.keys():
        print(f"\n{pair}:")
        config = get_forex_config(pair)
        print(f"  Daily Range: {config['typical_daily_pips']} pips")
        print(f"  Volatility: {config['typical_volatility']*100:.2f}%")
        print(f"  Min Confidence: {config['min_confidence']}%")
        print(f"  Top Weights:")
        weights = sorted(config['weights'].items(), key=lambda x: x[1], reverse=True)
        for factor, weight in weights[:3]:
            print(f"    {factor}: {weight*100:.0f}%")
    
    print("\n" + "="*80)
    print("Forex configuration loaded successfully!")
    print("="*80 + "\n")
