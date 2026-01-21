#!/usr/bin/env python3
"""
Stock Configuration for Multi-Symbol Prediction System
Supports AMD, AVGO, ORCL, NVDA, PTLR and easy addition of new stocks
"""

# Stock-specific configurations
STOCK_CONFIGS = {
    'AMD': {
        'name': 'Advanced Micro Devices',
        'sector_etf': 'XLK',  # Technology sector
        'competitors': ['NVDA', 'INTC', 'TSM', 'QCOM'],
        # 3.32% intraday range (high-low) from 90d analysis
        'typical_volatility': 0.0332,
        # 1.36% realistic move (avg of 1.34% overnight + 1.38% regular hours)
        'historical_avg_gap': 0.0136,
        # 55% confidence minimum (lowered to capture more bounces)
        'min_confidence_threshold': 0.55,
        'weight_adjustments': {
            # AMD is heavily retail-driven and social media sensitive
            # FIX OCT 24: Rebalanced to prioritize stock-specific over universal signals
            # Stock-specific increased, universal reduced to prevent herd behavior
            'technical': 0.12,        # INCREASED: Stock-specific (was 8%)
            'institutional': 0.10,    # INCREASED: Stock-specific (was 6%)
            'futures': 0.11,          # REDUCED: Universal signal (was 15%)
            'premarket': 0.10,        # Same-day momentum (situational)
            'hidden_edge': 0.10,      # Phase 3: 8 alt sources (mixed)
            'options': 0.11,          # Real-time sentiment (often similar)
            'news': 0.08,             # Stock-specific news (6h recent)
            'reddit': 0.08,           # AMD popular on WSB (stock-specific)
            'vix': 0.06,              # REDUCED: Universal fear gauge (was 8%)
            'sector': 0.06,           # Universal sector trend
            'twitter': 0.05,          # Social sentiment (stock-specific)
            'analyst_ratings': 0.02,  # Lagging indicator
            'earnings_proximity': 0.02,  # Event risk factor
            'short_interest': 0.01,   # Monthly stale data
            'dxy': 0.00,              # Minimal impact
        },
        'news_keywords': [
            'Ryzen', 'EPYC', 'Radeon', 'Instinct', 'MI300', 'AI chips',
            'data center', 'gaming GPU', 'Lisa Su', 'Xilinx', 'TSMC'
        ],
        'momentum_continuation_rate': 0.56,  # Historical data shows 56% continuation
        'description': 'High-beta semiconductor stock with strong retail following',
        # Optional: Technical indicator thresholds (uses defaults if not specified)
        'technical_thresholds': {
            'rsi_overbought': 65,  # RSI > 65 = overbought (reversal risk)
            'rsi_oversold': 35,    # RSI < 35 = oversold (bounce opportunity)
            'score_threshold': 0.04,  # Minimum score for UP/DOWN signal
            'gap_threshold': 1.5,  # % gap that triggers override logic
        }
    },

    'AVGO': {
        'name': 'Broadcom Inc',
        'sector_etf': 'XLK',  # Technology sector
        'competitors': ['QCOM', 'MRVL', 'TXN', 'NVDA'],
        # 2.81% intraday range (high-low) from 90d analysis
        'typical_volatility': 0.0281,
        # 1.03% realistic move (avg of 0.82% overnight + 1.24% regular hours)
        'historical_avg_gap': 0.0103,
        # 55% confidence minimum (lowered to capture more bounces) (aligned with AMD)
        'min_confidence_threshold': 0.55,
        'weight_adjustments': {
            # AVGO is institution-heavy and news-driven (M&A, deals)
            # FIX OCT 24: Rebalanced to prioritize stock-specific over universal signals
            'institutional': 0.14,    # INCREASED: Stock-specific (was 10%)
            'news': 0.11,             # Stock-specific M&A news
            'technical': 0.10,        # INCREASED: Stock-specific (was 6%)
            'futures': 0.11,          # REDUCED: Universal signal (was 15%)
            'options': 0.11,          # Institutional flow (often similar)
            'premarket': 0.10,        # Same-day momentum (situational)
            'hidden_edge': 0.10,      # Phase 3: 8 alt sources (mixed)
            'sector': 0.08,           # Universal sector trend
            'vix': 0.06,              # REDUCED: Universal fear gauge (was 8%)
            'earnings_proximity': 0.06,  # Event risk factor
            'analyst_ratings': 0.02,  # Lagging indicator
            'reddit': 0.02,           # Less retail
            'twitter': 0.01,          # Lower coverage
            'dxy': 0.00,              # Minimal impact
            'short_interest': 0.00    # Not applicable
        },
        'news_keywords': [
            'OpenAI', 'custom chips', 'VMware', 'AI accelerator', 'Hock Tan',
            'acquisition', 'M&A', 'enterprise software', 'networking chips',
            'infrastructure', 'data center', 'Wi-Fi', 'broadband'
        ],
        'momentum_continuation_rate': 0.41,  # Historical data shows 41% continuation
        'description': 'Large-cap institutional stock driven by M&A and AI deals',
        # Optional: Technical indicator thresholds (uses defaults if not specified)
        'technical_thresholds': {
            'rsi_overbought': 65,  # RSI > 65 = overbought
            'rsi_oversold': 35,    # RSI < 35 = oversold
            'score_threshold': 0.04,  # Minimum score for UP/DOWN signal
            'gap_threshold': 1.5,  # % gap that triggers override logic
        }
    },

    'ORCL': {
        'name': 'Oracle Corporation',
        'sector_etf': 'XLK',  # Technology sector
        'competitors': ['MSFT', 'GOOGL', 'AMZN', 'CRM'],
        'typical_volatility': 0.0306,  # 3.06% intraday range from 90d analysis
        # 1.24% realistic move (avg of 1.08% overnight + 1.39% regular hours)
        'historical_avg_gap': 0.0124,
        # 55% confidence minimum (lowered to capture more bounces)
        'min_confidence_threshold': 0.55,
        'weight_adjustments': {
            # ORCL is enterprise software - institutional heavy, news-driven (cloud deals, earnings)
            # FIX OCT 24: Rebalanced to prioritize stock-specific over universal signals
            'institutional': 0.18,    # INCREASED: Stock-specific (was 16%)
            'news': 0.14,             # Stock-specific enterprise deals
            'technical': 0.12,        # INCREASED: Stock-specific (was 6%)
            'futures': 0.12,          # REDUCED: Universal signal (was 16%)
            'options': 0.11,          # Institutional flow (often similar)
            'premarket': 0.10,        # Same-day momentum (situational)
            'hidden_edge': 0.10,      # Alternative signals (mixed)
            'vix': 0.06,              # REDUCED: Universal fear gauge (was 8%)
            'sector': 0.05,           # Universal sector trend
            'analyst_ratings': 0.02,  # Lagging indicator
            'earnings_proximity': 0.02,  # Event risk factor
            'reddit': 0.00,           # Very low retail interest
            'twitter': 0.00,          # Minimal social buzz
            'dxy': 0.00,              # Minimal FX exposure
            'short_interest': 0.00,   # Not applicable
        },
        'news_keywords': [
            'Oracle Cloud', 'OCI', 'database', 'enterprise software', 'Safra Catz',
            'cloud infrastructure', 'AWS competition', 'Azure', 'ERP', 'NetSuite',
            'Java', 'MySQL', 'enterprise contract', 'cloud deal', 'data center'
        ],
        'momentum_continuation_rate': 0.48,  # Estimate: stable enterprise stock
        'description': 'Large-cap enterprise software - institutional heavy, cloud/deal driven',
        # Optional: Technical indicator thresholds (uses defaults if not specified)
        'technical_thresholds': {
            'rsi_overbought': 65,  # RSI > 65 = overbought
            'rsi_oversold': 35,    # RSI < 35 = oversold
            'score_threshold': 0.04,  # Minimum score for UP/DOWN signal
            'gap_threshold': 1.5,  # % gap that triggers override logic
        }
    },

    'NVDA': {
        'name': 'NVIDIA Corporation',
        'sector_etf': 'XLK',  # Technology sector (also SMH for semiconductors)
        'competitors': ['AMD', 'INTC', 'QCOM', 'AVGO', 'TSM'],
        # 3.99% intraday range - HIGHEST volatility (from 90d analysis)
        'typical_volatility': 0.0399,
        # 0.95% average overnight gap (from 3-month analysis)
        'historical_avg_gap': 0.0095,
        # 60% confidence minimum (higher due to volatility)
        'min_confidence_threshold': 0.60,
        'weight_adjustments': {
            # NVDA is AI chip leader - retail-driven, social media sensitive, news-driven
            # High momentum continuation (54%) - when bullish stays bullish
            # FIX OCT 24: Rebalanced to prioritize stock-specific over universal signals
            # INCREASED: Stock-specific (volatile, responds to technicals)
            'technical': 0.12,
            'news': 0.10,            # AI partnerships, product launches, data center deals
            # INCREASED: Stock-specific (smart money follows AI trends)
            'institutional': 0.10,
            'futures': 0.11,         # REDUCED: Universal signal (was 15%)
            # Real-time sentiment (high options volume)
            'options': 0.11,
            'premarket': 0.10,       # Same-day momentum (situational)
            'hidden_edge': 0.10,     # Phase 3: 8 alt sources (mixed)
            # NVDA very popular on WSB (stock-specific)
            'reddit': 0.08,
            'vix': 0.06,             # REDUCED: Universal fear gauge (was 8%)
            'sector': 0.06,          # Universal sector trend
            # Social sentiment (stock-specific, AI buzz)
            'twitter': 0.05,
            'analyst_ratings': 0.02,  # Lagging indicator
            'earnings_proximity': 0.02,  # Event risk factor
            'short_interest': 0.01,  # Monthly stale data
            'dxy': 0.00,             # Minimal impact
        },
        'news_keywords': [
            'NVIDIA', 'Jensen Huang', 'AI chips', 'data center', 'H100', 'A100', 'Hopper',
            'Grace', 'Blackwell', 'CUDA', 'GPU', 'gaming', 'automotive', 'Omniverse',
            'DGX', 'AI infrastructure', 'machine learning', 'deep learning', 'autonomous vehicles',
            'chip shortage', 'supply chain', 'TSMC', 'partnership', 'enterprise AI'
        ],
        # 54% continuation - 2nd best (from 3-month analysis)
        'momentum_continuation_rate': 0.54,
        'description': 'AI chip leader - high volatility, retail-driven, strong momentum continuation',
        # Optional: Technical indicator thresholds (uses defaults if not specified)
        'technical_thresholds': {
            # RSI > 70 = overbought (higher threshold for momentum stock)
            'rsi_overbought': 70,
            # RSI < 30 = oversold (lower threshold for momentum stock)
            'rsi_oversold': 30,
            'score_threshold': 0.04,  # Minimum score for UP/DOWN signal
            # % gap that triggers override logic (higher for volatile stock)
            'gap_threshold': 2.0,
        }
    },

    'PTLR': {
        'name': 'Piedmont Lithium Inc',
        'sector_etf': 'XLB',  # Materials sector (also LIT for lithium ETF)
        'competitors': ['ALB', 'SQM', 'LTHM', 'LAC', 'LPI'],
        # 4.50% intraday range - VERY HIGH (commodity/mining stock)
        'typical_volatility': 0.0450,
        # 1.50% realistic move (commodity stocks have larger gaps)
        'historical_avg_gap': 0.0150,
        # 58% confidence minimum (higher due to volatility)
        'min_confidence_threshold': 0.58,
        'weight_adjustments': {
            # PTLR is lithium mining - commodity-driven, news-sensitive, less retail
            # Price driven by lithium prices, EV demand, mining permits, supply/demand
            'news': 0.16,            # INCREASED: Commodity stocks are very news-driven
            'technical': 0.13,       # INCREASED: Commodity stocks respond to technicals
            'futures': 0.12,         # Commodity futures correlation
            'institutional': 0.11,    # Mining stocks are institution-heavy
            'options': 0.10,         # Options flow (moderate volume)
            'premarket': 0.10,       # Same-day momentum (situational)
            'hidden_edge': 0.09,     # Alternative signals (commodity-specific)
            'sector': 0.08,          # Materials sector trend (XLB, LIT)
            'vix': 0.05,             # REDUCED: Universal fear gauge
            # Event risk factor (mining permits, production updates)
            'earnings_proximity': 0.04,
            'analyst_ratings': 0.02,  # Lagging indicator
            # Very low retail interest (not WSB popular)
            'reddit': 0.00,
            'twitter': 0.00,         # Minimal social buzz
            'dxy': 0.00,             # Minimal FX exposure
            'short_interest': 0.00,  # Not applicable
        },
        'news_keywords': [
            'Piedmont Lithium', 'lithium', 'mining', 'EV', 'electric vehicle', 'battery',
            'Tesla', 'supply agreement', 'mining permit', 'production', 'spodumene',
            'North Carolina', 'Tennessee', 'lithium hydroxide', 'lithium carbonate',
            'demand', 'supply chain', 'battery metals', 'clean energy', 'renewable',
            'mining operations', 'resource', 'reserve', 'exploration', 'development'
        ],
        # Estimate: commodity stocks have moderate continuation
        'momentum_continuation_rate': 0.45,
        'description': 'Lithium mining stock - commodity-driven, high volatility, news-sensitive',
        # Optional: Technical indicator thresholds (uses defaults if not specified)
        'technical_thresholds': {
            # RSI > 70 = overbought (higher for volatile commodity)
            'rsi_overbought': 70,
            # RSI < 30 = oversold (lower for volatile commodity)
            'rsi_oversold': 30,
            # Minimum score for UP/DOWN signal (higher threshold)
            'score_threshold': 0.05,
            # % gap that triggers override logic (higher for volatile stock)
            'gap_threshold': 2.5,
        }
    }
}

# Default stock symbol (if none specified)
DEFAULT_STOCK = 'AMD'

# Active stocks for prediction (can enable/disable)
ACTIVE_STOCKS = ['AMD', 'AVGO', 'ORCL', 'NVDA']


def get_stock_config(symbol: str) -> dict:
    """
    Get configuration for a specific stock symbol

    Args:
        symbol: Stock ticker (e.g., 'AMD', 'AVGO')

    Returns:
        dict: Stock-specific configuration
    """
    symbol = symbol.upper()

    if symbol not in STOCK_CONFIGS:
        print(f"⚠️ Warning: No config for {symbol}, using default AMD config")
        return STOCK_CONFIGS['AMD'].copy()

    return STOCK_CONFIGS[symbol].copy()


def get_active_stocks() -> list:
    """Get list of stocks currently enabled for prediction"""
    return ACTIVE_STOCKS.copy()


def add_stock_config(symbol: str, config: dict):
    """
    Add a new stock configuration

    Args:
        symbol: Stock ticker
        config: Configuration dictionary
    """
    symbol = symbol.upper()
    STOCK_CONFIGS[symbol] = config

    if symbol not in ACTIVE_STOCKS:
        ACTIVE_STOCKS.append(symbol)

    print(f"✅ Added configuration for {symbol}")


def get_stock_weight_adjustments(symbol: str) -> dict:
    """Get weight adjustments for a specific stock"""
    config = get_stock_config(symbol)
    return config.get('weight_adjustments', {
        'news': 0.20,
        'futures': 0.20,
        'options': 0.15,
        'technical': 0.15,
        'sector': 0.10,
        'reddit': 0.10,
        'institutional': 0.10
    })


def get_technical_thresholds(symbol: str) -> dict:
    """
    Get technical indicator thresholds for a specific stock
    Returns stock-specific thresholds or defaults if not configured

    Args:
        symbol: Stock ticker

    Returns:
        dict: Technical thresholds (RSI, score, gap levels)
    """
    config = get_stock_config(symbol)
    return config.get('technical_thresholds', {
        'rsi_overbought': 65,
        'rsi_oversold': 35,
        'score_threshold': 0.04,
        'gap_threshold': 1.5
    })


# Stock symbol for single-stock mode
STOCK_SYMBOL = DEFAULT_STOCK


if __name__ == "__main__":
    print("\n" + "="*80)
    print("📊 STOCK PREDICTION SYSTEM - CONFIGURATION")
    print("="*80)

    print(f"\n🎯 Active Stocks: {', '.join(ACTIVE_STOCKS)}")
    print(f"📌 Default Stock: {DEFAULT_STOCK}")

    for symbol in ACTIVE_STOCKS:
        config = get_stock_config(symbol)
        print(f"\n{'='*80}")
        print(f"📈 {symbol} - {config['name']}")
        print(f"{'='*80}")
        print(f"   Sector ETF: {config['sector_etf']}")
        print(f"   Competitors: {', '.join(config['competitors'])}")
        print(
            f"   Typical Volatility: {config['typical_volatility']*100:.1f}%")
        print(
            f"   Min Confidence: {config['min_confidence_threshold']*100:.0f}%")
        print(
            f"   Momentum Rate: {config['momentum_continuation_rate']*100:.1f}%")
        print(f"   Description: {config['description']}")

        print(f"\n   Weight Adjustments:")
        weights = config['weight_adjustments']
        for factor, weight in sorted(weights.items(), key=lambda x: x[1], reverse=True):
            print(
                f"      {factor.capitalize():15s} {weight:.2f} ({weight*100:.0f}%)")

        print(f"\n   Key News Keywords:")
        print(f"      {', '.join(config['news_keywords'][:5])}...")

    print(f"\n{'='*80}\n")
