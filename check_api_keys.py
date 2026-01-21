#!/usr/bin/env python3
"""Check if API keys are loaded from .env file"""

import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

print("\n" + "="*80)
print("API KEYS STATUS")
print("="*80)

keys_to_check = {
    'News APIs': {
        'FINNHUB_API_KEY': os.getenv('FINNHUB_API_KEY'),
        'ALPHA_VANTAGE_API_KEY': os.getenv('ALPHA_VANTAGE_API_KEY'),
        'FMP_API_KEY': os.getenv('FMP_API_KEY'),
    },
    'Social Media': {
        'REDDIT_CLIENT_ID': os.getenv('REDDIT_CLIENT_ID'),
        'REDDIT_CLIENT_SECRET': os.getenv('REDDIT_CLIENT_SECRET'),
        'TWITTER_BEARER_TOKEN': os.getenv('TWITTER_BEARER_TOKEN'),
    },
    'Other': {
        'TWILIO_ACCOUNT_SID': os.getenv('TWILIO_ACCOUNT_SID'),
        'POLYGON_API_KEY': os.getenv('POLYGON_API_KEY'),
    }
}

for category, keys in keys_to_check.items():
    print(f"\n{category}:")
    for key_name, key_value in keys.items():
        if key_value:
            # Show first 10 chars for verification
            masked = key_value[:10] + "..." if len(key_value) > 10 else key_value
            print(f"   ✅ {key_name}: {masked}")
        else:
            print(f"   ❌ {key_name}: NOT SET")

print("\n" + "="*80)

# Check if comprehensive_nextday_predictor loads them
print("\nChecking if predictor loads API keys...")
from comprehensive_nextday_predictor import ComprehensiveNextDayPredictor

predictor = ComprehensiveNextDayPredictor('AMD')
print(f"\nPredictor API keys:")
for key, value in predictor.api_keys.items():
    if value:
        masked = value[:10] + "..." if len(value) > 10 else value
        print(f"   ✅ {key}: {masked}")
    else:
        print(f"   ❌ {key}: NOT LOADED")

print("\n" + "="*80)
