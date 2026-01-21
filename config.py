#!/usr/bin/env python3
"""
Global Configuration File
Contains market hours, trading rules, and system configuration settings
"""

import os
from datetime import time

# Automatically load environment variables from .env so that all
# subsequent os.getenv() calls throughout the codebase can access
# keys that the user places in their local .env file.
try:
    # Only import if package is available – it is declared in requirements.txt
    from dotenv import load_dotenv, find_dotenv
    _env_file = find_dotenv()
    if _env_file:
        load_dotenv(_env_file)
        # Optional: uncomment the next line for troubleshooting missing keys
        # print(f"✅ Loaded environment vars from {_env_file}")
    else:
        # .env not found – rely on system env vars
        pass
except ImportError:
    # python-dotenv might be missing if user installed partial deps; ignore gracefully
    pass

# Market hours configuration (US/Eastern time)
MARKET_HOURS = {
    'open': time(9, 30),    # 9:30 AM ET
    'close': time(16, 0),   # 4:00 PM ET
    'pre_market_start': time(4, 0),  # 4:00 AM ET
    'after_hours_end': time(20, 0),  # 8:00 PM ET
    'pre_close_window': 15,  # Minutes before close for approaching close alerts
    'pre_open_window': 15,   # Minutes before open for pre-open alerts
}

# Display and behavior suppression rules
SUPPRESSION_RULES = {
    'suppress_intraday_when_closed': True,      # Hide intraday data when market is closed
    'suppress_approaching_close_when_invalid': True,  # Hide approaching close when not applicable  
    'suppress_trade_signals_on_fallback': False,     # Whether to hide trade signals during fallback modes
    'suppress_position_text_when_hold': False,       # Whether to hide position text when holding
}

# Trading configuration
TRADING_CONFIG = {
    'timezone': 'US/Eastern',
    'market_timezone': 'US/Eastern', 
    'data_timezone': 'UTC',
    'use_real_time': True,
    'dst_aware': True,
}

# Data cache settings 
CACHE_SETTINGS = {
    'default_ttl_seconds': 30,
    'intraday_ttl_seconds': 30,
    'daily_ttl_seconds': 21600,  # 6 hours
    'realtime_refresh_enabled': True
}