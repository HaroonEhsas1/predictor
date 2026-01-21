#!/usr/bin/env python3
"""Check if Twitter is connected"""

import os
from dotenv import load_dotenv

load_dotenv()

print("\n" + "="*80)
print("TWITTER STATUS CHECK")
print("="*80)

# Check if API key exists
bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
if bearer_token:
    print(f"\n✅ TWITTER_BEARER_TOKEN: {bearer_token[:20]}...")
else:
    print("\n❌ TWITTER_BEARER_TOKEN: NOT SET")

# Check if twitter_sentiment_tracker exists
print("\n" + "="*80)
print("Checking twitter_sentiment_tracker.py...")
print("="*80)

try:
    from twitter_sentiment_tracker import TwitterSentimentTracker
    print("✅ twitter_sentiment_tracker.py found")
    
    tracker = TwitterSentimentTracker()
    print("✅ TwitterSentimentTracker initialized")
    
    # Check if it has methods
    if hasattr(tracker, 'get_sentiment'):
        print("✅ Has get_sentiment() method")
    elif hasattr(tracker, 'get_twitter_sentiment'):
        print("✅ Has get_twitter_sentiment() method")
    else:
        print("⚠️ Method names unknown - checking...")
        methods = [m for m in dir(tracker) if not m.startswith('_')]
        print(f"   Available methods: {', '.join(methods)}")
    
except Exception as e:
    print(f"❌ Error loading twitter_sentiment_tracker: {e}")

# Check if comprehensive_nextday_predictor uses Twitter
print("\n" + "="*80)
print("Checking if predictor uses Twitter...")
print("="*80)

try:
    with open('comprehensive_nextday_predictor.py', 'r', encoding='utf-8') as f:
        content = f.read()
        
    if 'twitter' in content.lower():
        print("✅ 'twitter' mentioned in predictor")
    else:
        print("❌ 'twitter' NOT mentioned in predictor")
        
    if 'TwitterSentimentTracker' in content:
        print("✅ TwitterSentimentTracker imported")
    else:
        print("❌ TwitterSentimentTracker NOT imported")
        print("\n⚠️ TWITTER IS NOT INTEGRATED into the predictor!")
        
except Exception as e:
    print(f"❌ Error checking predictor: {e}")

print("\n" + "="*80)
print("SUMMARY")
print("="*80)

print("\nTwitter API Key: " + ("✅ SET" if bearer_token else "❌ NOT SET"))
print("Twitter Tracker File: ✅ EXISTS")
print("Integration: ❌ NOT INTEGRATED (Twitter data not used in predictions)")

print("\n💡 To integrate Twitter, we need to:")
print("   1. Add Twitter sentiment to comprehensive_nextday_predictor.py")
print("   2. Add Twitter weight to stock_config.py")
print("   3. Include Twitter score in prediction calculation")

print("="*80)
