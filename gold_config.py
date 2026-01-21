#!/usr/bin/env python3
"""
Gold Configuration for XAUUSD

This module defines configuration parameters for the gold prediction system.
We trade spot gold against USD (XAUUSD), but we can also map signals to
futures or CFDs at the broker level.
"""

GOLD_CONFIG = {
    # Yahoo Finance symbol used for pricing. We use COMEX gold futures
    # (GC=F) as a liquid proxy for XAUUSD, then apply signals to your
    # XAUUSD/CFD instrument at the broker.
    "symbol": "GC=F",
    "name": "Gold / US Dollar (XAUUSD via GC futures)",

    # Approximate typical daily range in USD per ounce.
    # This is only a fallback; the predictor uses ATR from live data for
    # targets and stops.
    "typical_daily_range": 25.0,

    # Minimum confidence threshold where trades become interesting.
    # Below this, the system will usually recommend NEUTRAL / skip.
    "min_confidence": 60,
}


def get_gold_config():
    """Return a copy of the base gold configuration."""
    return GOLD_CONFIG.copy()
