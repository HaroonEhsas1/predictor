"""
PREMARKET STOCK CONFIGURATIONS
Stock-specific settings for NVDA and META
"""

STOCK_CONFIGS = {
    'NVDA': {
        'name': 'NVIDIA Corporation',
        'sector': 'Technology - Semiconductors',
        'sector_etf': 'SMH',  # Semiconductor ETF
        
        # Historical follow-through patterns
        'follow_through_rate': 0.78,  # 78% of gaps follow through
        'trap_rate': 0.15,  # 15% are fake-outs
        'reversal_rate': 0.07,  # 7% full reversal
        
        # Gap characteristics
        'typical_gap': 0.02,  # 2% typical gap
        'small_gap': 0.01,  # <1% considered noise
        'large_gap': 0.04,  # >4% considered extreme
        'extreme_gap': 0.06,  # >6% exhaustion risk
        
        # Volume requirements
        'min_premarket_volume': 300000,  # Minimum for confidence
        'strong_volume': 800000,  # Strong conviction
        'typical_daily_volume': 50000000,  # Average daily
        
        # Price levels (update regularly)
        'current_price_range': (140, 150),  # Typical range
        'support_levels': [135, 130, 125],
        'resistance_levels': [150, 155, 160],
        
        # Key catalysts
        'primary_catalysts': [
            'earnings', 'guidance', 'data center', 'AI', 
            'gaming', 'automotive', 'chip shortage'
        ],
        'positive_keywords': [
            'beat', 'raised', 'strong', 'growth', 'demand',
            'AI boom', 'record', 'outperform', 'upgrade'
        ],
        'negative_keywords': [
            'miss', 'cut', 'weak', 'concern', 'slowdown',
            'competition', 'inventory', 'downgrade', 'warning'
        ],
        
        # Correlation factors
        'sector_correlation': 0.75,  # High correlation with semiconductors
        'btc_correlation': 0.45,  # Moderate crypto correlation
        'market_correlation': 0.70,  # High market correlation
        
        # Trading characteristics
        'avg_true_range': 0.028,  # 2.8% daily ATR
        'volatility_high': True,
        'premarket_liquidity': 'EXCELLENT',
        
        # Trap patterns (NVDA-specific)
        'common_traps': [
            'Earnings whisper miss - gaps down, then recovers',
            'After-hours pop - fades at open',
            'Small tech sell-off - overreaction, bounces',
        ],
        
        # Weights for prediction algorithm
        'weights': {
            'gap_size': 0.15,
            'volume': 0.20,
            'news_quality': 0.25,
            'futures': 0.15,
            'sector': 0.15,
            'technical': 0.10,
        }
    },
    
    'META': {
        'name': 'Meta Platforms Inc',
        'sector': 'Technology - Social Media',
        'sector_etf': 'XLC',  # Communication Services ETF
        
        # Historical follow-through patterns
        'follow_through_rate': 0.77,  # 77% of gaps follow through
        'trap_rate': 0.18,  # 18% are fake-outs
        'reversal_rate': 0.05,  # 5% full reversal
        
        # Gap characteristics
        'typical_gap': 0.018,  # 1.8% typical gap
        'small_gap': 0.008,  # <0.8% considered noise
        'large_gap': 0.035,  # >3.5% considered extreme
        'extreme_gap': 0.05,  # >5% exhaustion risk
        
        # Volume requirements
        'min_premarket_volume': 200000,
        'strong_volume': 600000,
        'typical_daily_volume': 20000000,
        
        # Price levels (update regularly)
        'current_price_range': (450, 550),
        'support_levels': [450, 430, 400],
        'resistance_levels': [550, 580, 600],
        
        # Key catalysts
        'primary_catalysts': [
            'earnings', 'user growth', 'revenue', 'ARPU',
            'metaverse', 'regulation', 'advertising', 'Reality Labs'
        ],
        'positive_keywords': [
            'beat', 'users up', 'revenue growth', 'ad strength',
            'metaverse progress', 'engagement', 'margin expansion'
        ],
        'negative_keywords': [
            'miss', 'users down', 'regulation', 'privacy',
            'competition', 'TikTok', 'ad weakness', 'fine'
        ],
        
        # Correlation factors
        'sector_correlation': 0.65,  # Moderate sector correlation
        'market_correlation': 0.75,  # High market correlation
        'ad_market_correlation': 0.80,  # High ad market correlation
        
        # Trading characteristics
        'avg_true_range': 0.025,  # 2.5% daily ATR
        'volatility_high': True,
        'premarket_liquidity': 'EXCELLENT',
        
        # Trap patterns (META-specific)
        'common_traps': [
            'Regulatory news - overreaction, recovers',
            'User count concerns - priced in quickly',
            'Competition fears - temporary weakness',
        ],
        
        # Weights for prediction algorithm
        'weights': {
            'gap_size': 0.15,
            'volume': 0.20,
            'news_quality': 0.25,
            'futures': 0.15,
            'sector': 0.10,
            'technical': 0.15,
        }
    },
    
    'AVGO': {
        'name': 'Broadcom Inc',
        'sector': 'Technology - Semiconductors',
        'sector_etf': 'SMH',  # Semiconductor ETF (same as NVDA)
        
        # Historical follow-through patterns
        'follow_through_rate': 0.76,  # 76% of gaps follow through
        'trap_rate': 0.17,  # 17% are fake-outs
        'reversal_rate': 0.07,  # 7% full reversal
        
        # Gap characteristics
        'typical_gap': 0.022,  # 2.2% typical gap
        'small_gap': 0.01,  # <1% considered noise
        'large_gap': 0.045,  # >4.5% considered extreme
        'extreme_gap': 0.06,  # >6% exhaustion risk
        
        # Volume requirements
        'min_premarket_volume': 150000,  # Lower than NVDA (less liquid)
        'strong_volume': 400000,  # Strong conviction
        'typical_daily_volume': 15000000,  # Average daily
        
        # Price levels (update regularly)
        'current_price_range': (160, 180),  # Typical range
        'support_levels': [155, 150, 145],
        'resistance_levels': [180, 185, 190],
        
        # Key catalysts
        'primary_catalysts': [
            'earnings', 'guidance', 'acquisitions', 'M&A', 'VMware',
            'enterprise software', 'data center', 'networking', '5G'
        ],
        'positive_keywords': [
            'beat', 'raised', 'acquisition', 'synergy', 'growth',
            'data center strength', 'record', 'margin expansion', 'upgrade'
        ],
        'negative_keywords': [
            'miss', 'cut', 'integration issues', 'debt', 'concern',
            'competition', 'regulatory', 'downgrade', 'warning'
        ],
        
        # Correlation factors
        'sector_correlation': 0.72,  # High correlation with semiconductors
        'market_correlation': 0.68,  # Moderate-high market correlation
        'ma_driven': True,  # M&A activity affects price
        
        # Trading characteristics
        'avg_true_range': 0.026,  # 2.6% daily ATR
        'volatility_high': True,
        'premarket_liquidity': 'GOOD',  # Not as liquid as NVDA
        
        # Trap patterns (AVGO-specific)
        'common_traps': [
            'M&A rumors - often priced in quickly',
            'Earnings beat - sells off if guidance weak',
            'Sector rotation - can reverse intraday',
        ],
        
        # Weights for prediction algorithm
        'weights': {
            'gap_size': 0.15,
            'volume': 0.18,  # Slightly lower (less liquid)
            'news_quality': 0.27,  # Higher (M&A driven)
            'futures': 0.15,
            'sector': 0.15,
            'technical': 0.10,
        }
    },
    
    'AMD': {
        'name': 'Advanced Micro Devices',
        'sector': 'Technology - Semiconductors',
        'sector_etf': 'SMH',  # Semiconductor ETF (same as NVDA)
        
        # Historical follow-through patterns
        'follow_through_rate': 0.56,  # 56% momentum continuation - BEST!
        'trap_rate': 0.15,  # 15% are fake-outs
        'reversal_rate': 0.29,  # 29% intraday reversals (HIGH!)
        
        # Gap characteristics  
        'typical_gap': 0.0136,  # 1.36% typical gap
        'small_gap': 0.005,  # <0.5% considered noise
        'large_gap': 0.03,  # >3% considered extreme
        'extreme_gap': 0.05,  # >5% exhaustion risk
        
        # Volume requirements
        'min_premarket_volume': 1000000,  # 1M minimum (very liquid)
        'strong_volume': 3000000,  # 3M strong conviction
        'typical_daily_volume': 50000000,  # 50M average daily
        
        # Price levels (update regularly)
        'current_price_range': (135, 150),  # Typical range
        'support_levels': [135, 130, 125],
        'resistance_levels': [150, 155, 160],
        
        # Key catalysts
        'primary_catalysts': [
            'earnings', 'Ryzen', 'EPYC', 'Radeon', 'MI300', 'AI chips',
            'data center', 'gaming GPU', 'Lisa Su', 'TSMC', 'Intel competition'
        ],
        'positive_keywords': [
            'beat', 'strong', 'AI demand', 'data center growth', 'market share',
            'Ryzen success', 'EPYC adoption', 'MI300 ramp', 'upgrade'
        ],
        'negative_keywords': [
            'miss', 'weak', 'competition', 'Intel', 'inventory', 'margin pressure',
            'downgrade', 'guidance cut', 'demand concerns'
        ],
        
        # Correlation factors
        'sector_correlation': 0.70,  # High correlation with semiconductors
        'market_correlation': 0.70,  # High market correlation
        'retail_driven': True,  # Very retail-driven
        
        # Trading characteristics
        'avg_true_range': 0.0332,  # 3.32% daily ATR
        'volatility_high': True,
        'premarket_liquidity': 'EXCELLENT',
        
        # CRITICAL: AMD intraday reversal issue
        'intraday_reversal_rate': 0.455,  # 45.5% reverse intraday!
        'trade_recommendation': 'EXIT_AT_OPEN',  # Take gap profit at 9:30-9:35 AM
        
        # Trap patterns (AMD-specific)
        'common_traps': [
            'Gaps up then sells off intraday (45.5% of time)',
            'Retail FOMO - fades quickly',
            'Social media hype - often reverses',
        ],
        
        # Weights for prediction algorithm
        'weights': {
            'gap_size': 0.15,
            'volume': 0.20,
            'news_quality': 0.25,
            'futures': 0.12,  # Reduced (universal)
            'sector': 0.12,
            'technical': 0.12,  # Increased (stock-specific)
            'options': 0.04,  # Watch for contrarian signals
        }
    }
}


def get_stock_config(symbol: str) -> dict:
    """Get configuration for a stock"""
    return STOCK_CONFIGS.get(symbol, STOCK_CONFIGS['NVDA'])


# Trap detection rules (generic + stock-specific)
TRAP_DETECTION_RULES = {
    'WEAK_VOLUME': {
        'description': 'Large gap with low volume',
        'check': lambda gap, volume, min_vol: abs(gap) > 1.5 and volume < min_vol * 0.7,
        'severity': 'HIGH',
        'trap_probability': 0.65,
    },
    'EXHAUSTION': {
        'description': 'Extreme gap likely to reverse',
        'check': lambda gap, extreme: abs(gap) > extreme,
        'severity': 'HIGH',
        'trap_probability': 0.60,
    },
    'NOISE': {
        'description': 'Gap too small to be meaningful',
        'check': lambda gap, small: abs(gap) < small,
        'severity': 'MEDIUM',
        'trap_probability': 0.70,
    },
    'COUNTER_FUTURES': {
        'description': 'Gap opposite to futures direction',
        'check': lambda gap, futures: (gap > 0 and futures < -0.5) or (gap < 0 and futures > 0.5),
        'severity': 'HIGH',
        'trap_probability': 0.55,
    },
    'WEAK_NEWS': {
        'description': 'Gap without catalyst',
        'check': lambda has_news: not has_news,
        'severity': 'MEDIUM',
        'trap_probability': 0.50,
    },
    'TOO_EARLY': {
        'description': 'Too early in premarket',
        'check': lambda minutes: minutes > 300,
        'severity': 'MEDIUM',
        'trap_probability': 0.45,
    },
    'OVERBOUGHT_OVERSOLD': {
        'description': 'Stock at extreme technical level',
        'check': lambda rsi: rsi > 70 or rsi < 30,
        'severity': 'MEDIUM',
        'trap_probability': 0.50,
    },
}


# Follow-through prediction adjustments
FOLLOW_THROUGH_ADJUSTMENTS = {
    'HIGH_QUALITY_GAP': +0.15,  # Large gap, high volume, good news
    'FUTURES_ALIGNED': +0.10,  # Gap direction matches futures
    'SECTOR_ALIGNED': +0.08,  # Sector moving same direction
    'STRONG_VOLUME': +0.10,  # Volume 2x+ typical
    'GOOD_TIMING': +0.05,  # Last hour before open
    'NEWS_CATALYST': +0.12,  # Strong news catalyst
    
    'WEAK_VOLUME': -0.20,  # Low volume
    'COUNTER_FUTURES': -0.15,  # Against futures
    'EXTREME_GAP': -0.15,  # Too large
    'SMALL_GAP': -0.18,  # Too small
    'TOO_EARLY': -0.10,  # Early premarket
    'NO_CATALYST': -0.12,  # No news
}


# UNIVERSAL THRESHOLDS (Apply to all stocks)
# These replace hardcoded values throughout the system
UNIVERSAL_THRESHOLDS = {
    # Gap thresholds (percentage)
    'min_gap_for_trade': 0.005,  # 0.5% minimum gap to consider
    'ideal_gap_min': 0.015,  # 1.5% ideal minimum
    'ideal_gap_max': 0.04,  # 4% ideal maximum
    'extreme_gap': 0.05,  # 5% extreme (exhaustion risk)
    'very_extreme_gap': 0.07,  # 7% very extreme
    
    # Volume thresholds (multipliers of typical)
    'min_volume_ratio': 0.05,  # 5% of daily volume minimum
    'weak_volume_ratio': 0.03,  # <3% is weak
    'strong_volume_ratio': 0.10,  # >10% is strong
    'very_strong_volume_ratio': 0.15,  # >15% is very strong
    
    # Volatility thresholds
    'normal_volatility_multiplier': 1.0,  # 1x normal
    'high_volatility_multiplier': 2.0,  # 2x normal
    'extreme_volatility_multiplier': 3.0,  # 3x normal (filter out)
    
    # Timing thresholds (minutes before open)
    'too_early_threshold': 300,  # 5 hours (before 4:30 AM)
    'early_threshold': 120,  # 2 hours (before 7:30 AM)
    'ideal_time_min': 15,  # 15 minutes (9:15 AM)
    'ideal_time_max': 60,  # 60 minutes (8:30 AM)
    
    # Confidence thresholds
    'min_confidence': 40.0,  # Minimum confidence %
    'max_confidence': 95.0,  # Maximum confidence %
    'neutral_confidence': 50.0,  # Neutral base
    'strong_trade_threshold': 75.0,  # STRONG_TRADE
    'trade_threshold': 65.0,  # TRADE
    'cautious_threshold': 55.0,  # CAUTIOUS
    
    # Futures alignment thresholds
    'futures_strong_move': 0.5,  # 0.5% strong move
    'futures_moderate_move': 0.2,  # 0.2% moderate move
    'futures_weak_move': 0.1,  # 0.1% weak move
    
    # Technical thresholds
    'rsi_overbought': 70,  # RSI overbought
    'rsi_oversold': 30,  # RSI oversold
    'rsi_very_overbought': 80,  # Very overbought
    'rsi_very_oversold': 20,  # Very oversold
    'rsi_neutral_min': 45,  # Neutral zone min
    'rsi_neutral_max': 55,  # Neutral zone max
    
    # ATR stop multipliers
    'atr_stop_tight': 1.5,  # High confidence
    'atr_stop_standard': 2.0,  # Medium confidence
    'atr_stop_wide': 2.5,  # Low confidence
    'atr_target_conservative': 0.6,  # Conservative target
    'atr_target_moderate': 1.0,  # Moderate target
    'atr_target_aggressive': 1.5,  # Aggressive target
    
    # Options flow thresholds
    'pc_ratio_neutral_min': 0.8,  # P/C neutral min
    'pc_ratio_neutral_max': 1.2,  # P/C neutral max
    'pc_ratio_excessive_puts': 1.5,  # Excessive puts (contrarian bullish)
    'pc_ratio_excessive_calls': 0.7,  # Excessive calls (contrarian bearish)
    'unusual_volume_ratio': 2.0,  # Volume > 2x OI = unusual
    
    # Sector correlation thresholds
    'correlation_strong': 0.7,  # Strong correlation
    'correlation_moderate': 0.4,  # Moderate correlation
    'correlation_weak': 0.2,  # Weak correlation
    'divergence_threshold': 0.5,  # 0.5% divergence significant
    
    # Social sentiment thresholds
    'reddit_spike_threshold': 10,  # >10 mentions = spike
    'reddit_extreme_threshold': 0.10,  # >0.10 sentiment = extreme
    'reddit_modest_threshold': 0.02,  # 0.02-0.10 = modest
    
    # News recency thresholds (hours)
    'news_breaking': 2,  # <2 hours = breaking
    'news_recent': 6,  # <6 hours = recent
    'news_stale': 24,  # >24 hours = stale
    
    # Confidence adjustments (percentage points)
    'news_boost_strong': 15,  # Strong news
    'news_boost_medium': 10,  # Medium news
    'news_boost_weak': 5,  # Weak news
    'news_penalty_none': -12,  # No news
    'futures_boost_aligned': 10,  # Futures aligned
    'futures_penalty_conflict': -15,  # Futures conflict
    'sector_boost_aligned': 8,  # Sector aligned
    'sector_penalty_conflict': -10,  # Sector conflict
    'technical_boost_support': 8,  # Technical support
    'technical_penalty_extreme': -10,  # Technical extreme
    'options_boost_max': 15,  # Max options boost
    'futures_delta_boost_max': 10,  # Max futures delta boost
    'social_boost_max': 10,  # Max social boost
    'sector_corr_boost_max': 12,  # Max sector correlation boost
    
    # Trap penalties
    'trap_penalty_high': 30,  # High severity trap
    'trap_penalty_medium': 20,  # Medium severity trap
    'trap_penalty_low': 10,  # Low severity trap
    
    # Position sizing
    'position_full': 1.0,  # 100% position
    'position_large': 0.75,  # 75% position
    'position_medium': 0.5,  # 50% position
    'position_small': 0.25,  # 25% position
    'max_risk_per_trade': 0.02,  # 2% max risk
    
    # Risk/Reward thresholds
    'min_risk_reward': 1.5,  # Minimum 1.5:1 R:R
    'good_risk_reward': 2.0,  # Good 2:1 R:R
    'excellent_risk_reward': 2.5,  # Excellent 2.5:1 R:R
}


def get_threshold(key: str, default=None):
    """Get a threshold value by key"""
    return UNIVERSAL_THRESHOLDS.get(key, default)
