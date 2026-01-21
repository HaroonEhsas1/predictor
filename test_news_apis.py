#!/usr/bin/env python3
"""Test if news APIs are working now"""

from comprehensive_nextday_predictor import ComprehensiveNextDayPredictor

print("\n" + "="*80)
print("TESTING NEWS APIs WITH .ENV FILE")
print("="*80)

print("\nInitializing predictor for AMD...")
predictor = ComprehensiveNextDayPredictor('AMD')

print("\nAPI Keys loaded in predictor:")
for key, value in predictor.api_keys.items():
    if value:
        print(f"   ✅ {key}: {value[:10]}...")
    else:
        print(f"   ❌ {key}: NOT LOADED")

print("\n" + "="*80)
print("Testing news sentiment collection...")
print("="*80)

news_data = predictor.get_news_sentiment()

print("\n" + "="*80)
print("RESULTS:")
print("="*80)
print(f"Overall Score: {news_data['overall_score']:+.3f}")
print(f"Bullish Count: {news_data['bullish_count']}")
print(f"Bearish Count: {news_data['bearish_count']}")
print(f"Sources: {', '.join(news_data['sources']) if news_data['sources'] else 'None'}")
print(f"Has Data: {news_data.get('has_data', False)}")

if news_data.get('has_data'):
    print("\n✅ NEWS APIs ARE WORKING!")
else:
    print("\n❌ NEWS APIs NOT RETURNING DATA")
    print("This could mean:")
    print("   - API rate limits reached")
    print("   - API keys invalid/expired")
    print("   - Network issues")

print("="*80)
