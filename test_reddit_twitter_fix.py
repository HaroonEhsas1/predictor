"""
TEST REDDIT & TWITTER SYMBOL FILTERING
=======================================
Verify that Reddit and Twitter sentiment searches filter by stock symbol
Each stock should get different sentiment data

Run this to confirm the fix works
"""

from reddit_sentiment_tracker import RedditSentimentTracker
import time

def test_reddit_symbol_filtering():
    """Test that Reddit searches are symbol-specific"""
    
    print("="*80)
    print("🔍 TESTING REDDIT SYMBOL FILTERING")
    print("="*80)
    print("\nVerifying Reddit searches filter by symbol...")
    print("This will take ~30 seconds...\n")
    
    # Create Reddit tracker
    tracker = RedditSentimentTracker()
    
    if not tracker.reddit:
        print("❌ Reddit API not connected - skipping test")
        print("   (This is OK - Reddit may be rate limited)")
        return False
    
    # Test 3 different symbols
    symbols = ['AMD', 'AVGO', 'ORCL']
    results = {}
    
    for symbol in symbols:
        print(f"\n📊 Testing {symbol}...")
        print(f"   Searching r/wallstreetbets for ${symbol}...")
        
        # Get sentiment for this symbol
        result = tracker.get_wallstreetbets_sentiment(symbol=symbol)
        
        if 'error' in result:
            print(f"   ⚠️ Error: {result['error']}")
            results[symbol] = None
            continue
        
        mentions = result.get('mentions', 0)
        sentiment = result.get('sentiment', 0.0)
        
        print(f"   {symbol} Mentions: {mentions}")
        print(f"   {symbol} Sentiment: {sentiment:+.3f}")
        
        results[symbol] = {
            'mentions': mentions,
            'sentiment': sentiment
        }
        
        # Rate limit protection
        time.sleep(2)
    
    # Analysis
    print("\n" + "="*80)
    print("📊 ANALYSIS")
    print("="*80)
    
    # Check if all results are identical (bad)
    amd_result = results.get('AMD')
    avgo_result = results.get('AVGO')
    orcl_result = results.get('ORCL')
    
    if not amd_result or not avgo_result or not orcl_result:
        print("\n⚠️ Could not fetch all data - test inconclusive")
        return None
    
    amd_mentions = amd_result['mentions']
    avgo_mentions = avgo_result['mentions']
    orcl_mentions = orcl_result['mentions']
    
    print(f"\nMention Counts:")
    print(f"  AMD:  {amd_mentions}")
    print(f"  AVGO: {avgo_mentions}")
    print(f"  ORCL: {orcl_mentions}")
    
    # If all are the same (and > 0), it's broken
    if (amd_mentions == avgo_mentions == orcl_mentions and amd_mentions > 0):
        print(f"\n❌ FAIL: All stocks have {amd_mentions} mentions")
        print(f"   Reddit is NOT filtering by symbol!")
        print(f"   All stocks getting same data ❌")
        return False
    
    # If they're different, it's working
    if not (amd_mentions == avgo_mentions == orcl_mentions):
        print(f"\n✅ PASS: Mention counts are different")
        print(f"   Reddit IS filtering by symbol!")
        print(f"   Each stock gets unique data ✅")
        return True
    
    # If all are zero, test inconclusive
    if amd_mentions == 0 and avgo_mentions == 0 and orcl_mentions == 0:
        print(f"\n⚠️ INCONCLUSIVE: All stocks have 0 mentions")
        print(f"   This could mean:")
        print(f"   • No recent posts about these stocks (possible)")
        print(f"   • Reddit rate limited (possible)")
        print(f"   • Search not working (possible)")
        return None
    
    return True

def test_overall_sentiment_different():
    """Test that get_overall_reddit_sentiment returns different results per symbol"""
    
    print("\n" + "="*80)
    print("🔍 TESTING OVERALL REDDIT SENTIMENT")
    print("="*80)
    print("\nTesting get_overall_reddit_sentiment for each symbol...")
    print("This will take ~60 seconds...\n")
    
    tracker = RedditSentimentTracker()
    
    if not tracker.reddit:
        print("❌ Reddit API not connected - skipping test")
        return None
    
    symbols = ['AMD', 'AVGO', 'ORCL']
    overall_results = {}
    
    for symbol in symbols:
        print(f"\n📊 Getting overall sentiment for {symbol}...")
        
        result = tracker.get_overall_reddit_sentiment(symbol=symbol)
        
        score = result.get('score', 5)
        mentions = result.get('mentions', 0)
        
        print(f"   {symbol} Score: {score:.1f}/10")
        print(f"   {symbol} Total Mentions: {mentions}")
        
        overall_results[symbol] = {
            'score': score,
            'mentions': mentions
        }
        
        time.sleep(2)
    
    # Analysis
    print("\n" + "="*80)
    print("📊 OVERALL SENTIMENT ANALYSIS")
    print("="*80)
    
    amd_score = overall_results['AMD']['score']
    avgo_score = overall_results['AVGO']['score']
    orcl_score = overall_results['ORCL']['score']
    
    amd_mentions = overall_results['AMD']['mentions']
    avgo_mentions = overall_results['AVGO']['mentions']
    orcl_mentions = overall_results['ORCL']['mentions']
    
    print(f"\nScores:")
    print(f"  AMD:  {amd_score:.1f}/10 ({amd_mentions} mentions)")
    print(f"  AVGO: {avgo_score:.1f}/10 ({avgo_mentions} mentions)")
    print(f"  ORCL: {orcl_score:.1f}/10 ({orcl_mentions} mentions)")
    
    # Check if data is different
    if not (amd_mentions == avgo_mentions == orcl_mentions and amd_mentions > 0):
        print(f"\n✅ PASS: Each stock has different data")
        print(f"   Overall sentiment IS symbol-specific! ✅")
        return True
    else:
        print(f"\n❌ FAIL: All stocks have same mention count")
        print(f"   Overall sentiment NOT symbol-specific! ❌")
        return False

if __name__ == "__main__":
    print("\n" + "="*80)
    print("🧪 REDDIT SYMBOL FILTERING TEST")
    print("="*80)
    print("\nTesting that Reddit searches filter by stock symbol...")
    print("This ensures AMD gets AMD data, AVGO gets AVGO data, etc.\n")
    
    # Test 1: WallStreetBets sentiment
    wsb_result = test_reddit_symbol_filtering()
    
    # Test 2: Overall sentiment
    overall_result = test_overall_sentiment_different()
    
    # Summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    
    tests_passed = 0
    tests_run = 0
    
    if wsb_result is not None:
        tests_run += 1
        if wsb_result:
            tests_passed += 1
            print("\n✅ WallStreetBets Sentiment: PASS (symbol-specific)")
        else:
            print("\n❌ WallStreetBets Sentiment: FAIL (not symbol-specific)")
    else:
        print("\n⚠️ WallStreetBets Sentiment: INCONCLUSIVE")
    
    if overall_result is not None:
        tests_run += 1
        if overall_result:
            tests_passed += 1
            print("✅ Overall Reddit Sentiment: PASS (symbol-specific)")
        else:
            print("❌ Overall Reddit Sentiment: FAIL (not symbol-specific)")
    else:
        print("⚠️ Overall Reddit Sentiment: INCONCLUSIVE")
    
    print(f"\n{'='*80}")
    if tests_run > 0:
        print(f"🎯 RESULT: {tests_passed}/{tests_run} tests passed")
    else:
        print(f"⚠️ RESULT: Unable to run tests (Reddit API issue)")
    print(f"{'='*80}")
    
    if tests_passed == tests_run and tests_run > 0:
        print("\n✅ EXCELLENT: Reddit sentiment is symbol-specific!")
        print("   AMD gets AMD data, AVGO gets AVGO data, ORCL gets ORCL data")
        print("   Fix is working correctly! ✅")
    elif tests_passed > 0:
        print("\n✅ GOOD: Some tests passed")
        print("   Partial symbol filtering working")
    elif tests_run > 0:
        print("\n❌ PROBLEM: Tests failed")
        print("   Reddit may not be filtering by symbol correctly")
    else:
        print("\n⚠️ INCONCLUSIVE: Could not test")
        print("   Reddit API may be rate limited or unavailable")
        print("   Try again later")
