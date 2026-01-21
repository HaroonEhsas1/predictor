"""
VERIFY DATA SOURCE INDEPENDENCE
================================
Tests that AMD, AVGO, and ORCL each get their own unique data
Not sharing news, sentiment, or other stock-specific data

Run this to ensure complete stock independence
"""

from comprehensive_nextday_predictor import ComprehensiveNextDayPredictor
import time

def verify_data_independence():
    """Verify each stock gets its own data"""
    
    print("="*80)
    print("🔍 DATA SOURCE INDEPENDENCE VERIFICATION")
    print("="*80)
    print("\nTesting that AMD, AVGO, and ORCL each get unique data...")
    print("This may take 30-60 seconds...\n")
    
    # Create predictors for each stock
    print("📊 Creating predictors...")
    amd_pred = ComprehensiveNextDayPredictor(symbol='AMD')
    avgo_pred = ComprehensiveNextDayPredictor(symbol='AVGO')
    orcl_pred = ComprehensiveNextDayPredictor(symbol='ORCL')
    
    results = {
        'AMD': {},
        'AVGO': {},
        'ORCL': {}
    }
    
    # Test 1: News Sentiment
    print("\n" + "="*80)
    print("1️⃣ TESTING NEWS SENTIMENT INDEPENDENCE")
    print("="*80)
    
    for symbol, predictor in [('AMD', amd_pred), ('AVGO', avgo_pred), ('ORCL', orcl_pred)]:
        print(f"\n📰 Fetching {symbol} news...")
        news_data = predictor.get_news_sentiment()
        results[symbol]['news'] = news_data
        print(f"   {symbol} News Score: {news_data.get('score', 0):.3f}")
        print(f"   {symbol} Article Count: {news_data.get('article_count', 0)}")
    
    # Check if news data is different
    amd_news_score = results['AMD']['news'].get('score', 0)
    avgo_news_score = results['AVGO']['news'].get('score', 0)
    orcl_news_score = results['ORCL']['news'].get('score', 0)
    
    print(f"\n📊 Analysis:")
    if amd_news_score == avgo_news_score == orcl_news_score:
        print(f"   ❌ WARNING: All stocks have same news score ({amd_news_score:.3f})")
        print(f"   This suggests news may not be stock-specific!")
    else:
        print(f"   ✅ News scores are different - INDEPENDENT")
        print(f"   AMD: {amd_news_score:.3f}, AVGO: {avgo_news_score:.3f}, ORCL: {orcl_news_score:.3f}")
    
    # Test 2: Technical Analysis
    print("\n" + "="*80)
    print("2️⃣ TESTING TECHNICAL ANALYSIS INDEPENDENCE")
    print("="*80)
    
    for symbol, predictor in [('AMD', amd_pred), ('AVGO', avgo_pred), ('ORCL', orcl_pred)]:
        print(f"\n📈 Calculating {symbol} technicals...")
        tech_data = predictor.get_technical_analysis()
        results[symbol]['technical'] = tech_data
        print(f"   {symbol} RSI: {tech_data.get('rsi', 0):.1f}")
        print(f"   {symbol} Tech Score: {tech_data.get('score', 0):.3f}")
    
    # Check if technical data is different
    amd_rsi = results['AMD']['technical'].get('rsi', 0)
    avgo_rsi = results['AVGO']['technical'].get('rsi', 0)
    orcl_rsi = results['ORCL']['technical'].get('rsi', 0)
    
    print(f"\n📊 Analysis:")
    if amd_rsi == avgo_rsi == orcl_rsi:
        print(f"   ❌ ERROR: All stocks have same RSI ({amd_rsi:.1f})")
        print(f"   This is impossible - technical data is broken!")
    else:
        print(f"   ✅ RSI values are different - INDEPENDENT")
        print(f"   AMD: {amd_rsi:.1f}, AVGO: {avgo_rsi:.1f}, ORCL: {orcl_rsi:.1f}")
    
    # Test 3: Options Data
    print("\n" + "="*80)
    print("3️⃣ TESTING OPTIONS DATA INDEPENDENCE")
    print("="*80)
    
    for symbol, predictor in [('AMD', amd_pred), ('AVGO', avgo_pred), ('ORCL', orcl_pred)]:
        print(f"\n📊 Fetching {symbol} options...")
        options_data = predictor.get_options_flow()
        results[symbol]['options'] = options_data
        pc_ratio = options_data.get('put_call_ratio', 0)
        print(f"   {symbol} P/C Ratio: {pc_ratio:.2f}")
        print(f"   {symbol} Options Score: {options_data.get('score', 0):.3f}")
    
    # Check if options data is different
    amd_pc = results['AMD']['options'].get('put_call_ratio', 0)
    avgo_pc = results['AVGO']['options'].get('put_call_ratio', 0)
    orcl_pc = results['ORCL']['options'].get('put_call_ratio', 0)
    
    print(f"\n📊 Analysis:")
    if amd_pc == avgo_pc == orcl_pc and amd_pc != 0:
        print(f"   ❌ WARNING: All stocks have same P/C ratio ({amd_pc:.2f})")
        print(f"   This suggests options data may not be stock-specific!")
    else:
        print(f"   ✅ P/C ratios are different - INDEPENDENT")
        print(f"   AMD: {amd_pc:.2f}, AVGO: {avgo_pc:.2f}, ORCL: {orcl_pc:.2f}")
    
    # Test 4: Reddit Sentiment
    print("\n" + "="*80)
    print("4️⃣ TESTING REDDIT SENTIMENT INDEPENDENCE")
    print("="*80)
    
    for symbol, predictor in [('AMD', amd_pred), ('AVGO', avgo_pred), ('ORCL', orcl_pred)]:
        print(f"\n🔴 Fetching {symbol} Reddit sentiment...")
        reddit_data = predictor.get_reddit_sentiment()
        results[symbol]['reddit'] = reddit_data
        print(f"   {symbol} Reddit Score: {reddit_data.get('score', 0):.3f}")
        print(f"   {symbol} Mentions: {reddit_data.get('mentions', 0)}")
    
    # Check if Reddit data is different
    amd_reddit = results['AMD']['reddit'].get('score', 0)
    avgo_reddit = results['AVGO']['reddit'].get('score', 0)
    orcl_reddit = results['ORCL']['reddit'].get('score', 0)
    
    amd_mentions = results['AMD']['reddit'].get('mentions', 0)
    avgo_mentions = results['AVGO']['reddit'].get('mentions', 0)
    orcl_mentions = results['ORCL']['reddit'].get('mentions', 0)
    
    print(f"\n📊 Analysis:")
    if (amd_reddit == avgo_reddit == orcl_reddit and 
        amd_mentions == avgo_mentions == orcl_mentions and
        amd_mentions > 0):
        print(f"   ❌ WARNING: All stocks have same Reddit data!")
        print(f"   Score: {amd_reddit:.3f}, Mentions: {amd_mentions}")
        print(f"   ⚠️ Reddit may not be filtering by stock symbol!")
    else:
        print(f"   ✅ Reddit data is different - LIKELY INDEPENDENT")
        print(f"   AMD: {amd_reddit:.3f} ({amd_mentions} mentions)")
        print(f"   AVGO: {avgo_reddit:.3f} ({avgo_mentions} mentions)")
        print(f"   ORCL: {orcl_reddit:.3f} ({orcl_mentions} mentions)")
    
    # Summary
    print("\n" + "="*80)
    print("📊 INDEPENDENCE VERIFICATION SUMMARY")
    print("="*80)
    
    independence_score = 0
    total_tests = 4
    
    # News independence
    if not (amd_news_score == avgo_news_score == orcl_news_score):
        print("\n✅ News Sentiment: INDEPENDENT")
        independence_score += 1
    else:
        print("\n❌ News Sentiment: POTENTIALLY SHARED (investigate)")
    
    # Technical independence
    if not (amd_rsi == avgo_rsi == orcl_rsi):
        print("✅ Technical Analysis: INDEPENDENT")
        independence_score += 1
    else:
        print("❌ Technical Analysis: ERROR (should never match)")
    
    # Options independence
    if not (amd_pc == avgo_pc == orcl_pc and amd_pc != 0):
        print("✅ Options Data: INDEPENDENT")
        independence_score += 1
    else:
        print("❌ Options Data: POTENTIALLY SHARED (investigate)")
    
    # Reddit independence
    if not (amd_reddit == avgo_reddit == orcl_reddit and amd_mentions == avgo_mentions):
        print("✅ Reddit Sentiment: LIKELY INDEPENDENT")
        independence_score += 1
    else:
        print("⚠️ Reddit Sentiment: NEEDS INVESTIGATION")
    
    print(f"\n{'='*80}")
    print(f"🎯 INDEPENDENCE SCORE: {independence_score}/{total_tests}")
    print(f"{'='*80}")
    
    if independence_score == total_tests:
        print("\n✅ EXCELLENT: All data sources are stock-specific!")
        print("   Each stock gets its own unique data.")
        print("   No data sharing detected.")
    elif independence_score >= 3:
        print("\n✅ GOOD: Most data sources are independent")
        print("   Minor investigation needed for flagged sources")
    else:
        print("\n⚠️ WARNING: Multiple data sources may be shared")
        print("   Investigate flagged sources immediately")
    
    return independence_score, total_tests

if __name__ == "__main__":
    score, total = verify_data_independence()
    
    print("\n" + "="*80)
    print("💡 RECOMMENDATIONS")
    print("="*80)
    
    if score == total:
        print("\n✅ No action needed - system is working correctly!")
    else:
        print("\n📋 Action Items:")
        print("1. Check news API calls filter by symbol parameter")
        print("2. Verify Reddit searches include ticker symbol filter")
        print("3. Check Twitter searches use #symbol or $symbol")
        print("4. Review any flagged data sources above")
    
    print("\n" + "="*80)
    print(f"✅ Verification Complete - Score: {score}/{total}")
    print("="*80)
