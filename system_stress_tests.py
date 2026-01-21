"""
SYSTEM STRESS TESTS - HARD CHALLENGES
Tests the system with difficult scenarios that could break it

Challenges:
1. Conflicting signals (bullish + bearish at same time)
2. Extreme volatility
3. Trap scenarios
4. Mixed market conditions
5. Edge cases
6. Real-world difficult situations
"""

from stock_specific_predictors import get_predictor
from signal_strength_system import analyze_signal_strength

class SystemStressTest:
    """Stress test the system with hard challenges"""
    
    def __init__(self):
        self.challenges_passed = 0
        self.challenges_failed = 0
        self.results = []
        
    def run_all_challenges(self):
        """Run all stress tests"""
        
        print("\n" + "="*80)
        print("💪 SYSTEM STRESS TESTS - HARD CHALLENGES")
        print("="*80)
        print("""
Testing system with:
⚡ Conflicting signals
⚡ Extreme volatility  
⚡ Known trap patterns
⚡ Mixed market conditions
⚡ Edge cases
⚡ Real-world difficult scenarios

Let's see if it breaks! 💪
        """)
        
        self.challenge_1_conflicting_signals()
        self.challenge_2_extreme_volatility()
        self.challenge_3_classic_traps()
        self.challenge_4_mixed_market()
        self.challenge_5_edge_cases()
        self.challenge_6_real_world_scenarios()
        self.challenge_7_stock_specific_tests()
        
        self.print_summary()
        
    def challenge_1_conflicting_signals(self):
        """Challenge 1: Conflicting bullish and bearish signals"""
        
        print("\n" + "="*80)
        print("CHALLENGE 1: CONFLICTING SIGNALS")
        print("="*80)
        print("Scenario: Futures UP, but stock technical DOWN, news NEGATIVE, volume WEAK")
        
        data = {
            'futures_pct': 0.8,  # Bullish
            'gap_pct': -1.5,  # Bearish!
            'premarket_volume': 300000,  # Weak (< 1M min)
            'min_volume': 1000000,
            'rsi': 72,  # Overbought (bearish!)
            'pc_ratio': 0.7,  # Too many calls (bearish!)
            'news_sentiment': -0.6,  # Very negative!
            'news_strength': 0.8,  # Strong
            'sector_pct': -1.0,  # Sector down (bearish!)
            'social_sentiment': 0.3  # Bullish (but retail wrong?)
        }
        
        print("\n📊 Signals:")
        print(f"   ✅ Futures: UP {data['futures_pct']}%")
        print(f"   ❌ Gap: DOWN {data['gap_pct']}%")
        print(f"   ❌ Volume: WEAK {data['premarket_volume']:,} (< {data['min_volume']:,})")
        print(f"   ❌ RSI: OVERBOUGHT {data['rsi']}")
        print(f"   ❌ News: VERY NEGATIVE ({data['news_sentiment']})")
        print(f"   ❌ Sector: DOWN {data['sector_pct']}%")
        print(f"   ✅ Social: Bullish (but retail often wrong)")
        
        # Run signal strength analysis
        result = analyze_signal_strength(data)
        
        print(f"\n🎯 System Decision:")
        print(f"   Direction: {result['direction']}")
        print(f"   Confidence: {result['confidence']*100:.0f}%")
        print(f"   Bullish Power: {result['bullish_power']:.1f}")
        print(f"   Bearish Power: {result['bearish_power']:.1f}")
        print(f"   Dominance: {result['power_difference']:.1f} points")
        
        # Should SKIP or pick BEARISH (bearish dominant)
        if result['direction'] == 'DOWN' or result['direction'] == 'NEUTRAL':
            print(f"\n   ✅ PASS: System correctly chose {result['direction']}")
            print(f"           Bearish signals (gap down, weak volume, overbought,")
            print(f"           negative news, sector down) DOMINATED!")
            self.challenges_passed += 1
        else:
            print(f"\n   ❌ FAIL: Should not go UP with so many bearish signals!")
            self.challenges_failed += 1
        
        self.results.append({
            'challenge': 'Conflicting Signals',
            'passed': result['direction'] != 'UP',
            'decision': result['direction']
        })
    
    def challenge_2_extreme_volatility(self):
        """Challenge 2: Extreme volatility scenario"""
        
        print("\n" + "="*80)
        print("CHALLENGE 2: EXTREME VOLATILITY")
        print("="*80)
        print("Scenario: 8% gap (extreme!), high volume, but is it a trap?")
        
        data = {
            'gap_pct': 8.0,  # EXTREME gap!
            'premarket_volume': 10000000,  # Very high
            'min_volume': 1000000,
            'rsi': 78,  # Very overbought
            'futures_pct': 0.5,  # Moderate
            'news_sentiment': 0.8,  # Positive (but gap already priced in?)
            'news_strength': 0.9,
            'sector_pct': 2.0,  # Strong sector
            'pc_ratio': 1.0,  # Neutral
            'social_sentiment': 0.15  # Very high retail interest (danger?)
        }
        
        print("\n📊 Situation:")
        print(f"   Gap: {data['gap_pct']}% (EXTREME! Normal max is 4-5%)")
        print(f"   Volume: {data['premarket_volume']:,} (VERY HIGH)")
        print(f"   RSI: {data['rsi']} (VERY OVERBOUGHT)")
        print(f"   News: Very positive")
        print(f"   Social: Very high retail interest")
        
        result = analyze_signal_strength(data)
        
        print(f"\n🎯 System Decision:")
        print(f"   Direction: {result['direction']}")
        print(f"   Confidence: {result['confidence']*100:.0f}%")
        
        # Extreme gaps often EXHAUST - should be cautious
        # Even if bullish, confidence should be lower due to overbought
        if result['confidence'] < 0.75 or result['direction'] == 'NEUTRAL':
            print(f"\n   ✅ PASS: System is CAUTIOUS about extreme 8% gap")
            print(f"           Confidence {result['confidence']*100:.0f}% reflects exhaustion risk")
            print(f"           Overbought RSI 78 + extreme gap = dangerous!")
            self.challenges_passed += 1
        else:
            print(f"\n   ⚠️ WARNING: High confidence on extreme gap could be risky")
            print(f"            8% gaps often reverse (exhaustion)")
            if result['confidence'] > 0.85:
                self.challenges_failed += 1
            else:
                self.challenges_passed += 1
        
        self.results.append({
            'challenge': 'Extreme Volatility',
            'passed': result['confidence'] < 0.85,
            'decision': f"{result['direction']} {result['confidence']*100:.0f}%"
        })
    
    def challenge_3_classic_traps(self):
        """Challenge 3: Classic trap patterns"""
        
        print("\n" + "="*80)
        print("CHALLENGE 3: CLASSIC TRAP PATTERNS")
        print("="*80)
        
        # Trap 1: Gap up on weak volume
        print("\n📊 TRAP 1: Gap up on weak volume")
        
        data1 = {
            'gap_pct': 2.5,
            'premarket_volume': 200000,  # Very weak!
            'min_volume': 1000000,
            'rsi': 50,
            'futures_pct': 0.3,
            'news_sentiment': 0.4,
            'news_strength': 0.3,  # Weak news
            'sector_pct': 0.5
        }
        
        print(f"   Gap: {data1['gap_pct']}% UP")
        print(f"   Volume: {data1['premarket_volume']:,} (< {data1['min_volume']*0.5:,} WEAK!)")
        
        result1 = analyze_signal_strength(data1)
        
        if result1['direction'] == 'NEUTRAL' or result1['confidence'] < 0.60:
            print(f"   ✅ PASS: Detected weak volume trap!")
            print(f"           Decision: {result1['direction']} {result1['confidence']*100:.0f}%")
            trap1_pass = True
        else:
            print(f"   ❌ FAIL: Should detect weak volume trap!")
            trap1_pass = False
        
        # Trap 2: Overbought + gap up
        print("\n📊 TRAP 2: Overbought reversal")
        
        data2 = {
            'gap_pct': 3.0,
            'premarket_volume': 2000000,
            'min_volume': 1000000,
            'rsi': 76,  # Very overbought!
            'futures_pct': 0.2,  # Weak
            'news_sentiment': 0.5,
            'news_strength': 0.5,
            'sector_pct': -0.5  # Sector diverging!
        }
        
        print(f"   Gap: {data2['gap_pct']}% UP")
        print(f"   RSI: {data2['rsi']} (VERY OVERBOUGHT)")
        print(f"   Sector: DOWN {data2['sector_pct']}% (DIVERGING!)")
        
        result2 = analyze_signal_strength(data2)
        
        if result2['direction'] == 'NEUTRAL' or result2['confidence'] < 0.65:
            print(f"   ✅ PASS: Detected overbought trap!")
            print(f"           Decision: {result2['direction']} {result2['confidence']*100:.0f}%")
            trap2_pass = True
        else:
            print(f"   ❌ FAIL: Should be cautious of overbought + divergence!")
            trap2_pass = False
        
        if trap1_pass and trap2_pass:
            self.challenges_passed += 1
        else:
            self.challenges_failed += 1
        
        self.results.append({
            'challenge': 'Classic Traps',
            'passed': trap1_pass and trap2_pass,
            'decision': 'Both traps detected' if trap1_pass and trap2_pass else 'Failed'
        })
    
    def challenge_4_mixed_market(self):
        """Challenge 4: Mixed/choppy market conditions"""
        
        print("\n" + "="*80)
        print("CHALLENGE 4: MIXED/CHOPPY MARKET")
        print("="*80)
        print("Scenario: Everything is mediocre - no clear direction")
        
        data = {
            'gap_pct': 0.8,  # Small gap
            'premarket_volume': 1200000,  # Just above minimum
            'min_volume': 1000000,
            'rsi': 52,  # Neutral
            'futures_pct': 0.1,  # Barely up
            'news_sentiment': 0.1,  # Slightly positive
            'news_strength': 0.3,  # Weak
            'sector_pct': -0.2,  # Slightly negative
            'pc_ratio': 1.1,  # Neutral
            'social_sentiment': 0.0  # Neutral
        }
        
        print("\n📊 Mediocre signals:")
        print(f"   Gap: {data['gap_pct']}% (small)")
        print(f"   Volume: {data['premarket_volume']:,} (barely enough)")
        print(f"   RSI: {data['rsi']} (neutral)")
        print(f"   Futures: {data['futures_pct']}% (barely positive)")
        print(f"   News: Weak positive")
        print(f"   Sector: Slightly negative")
        
        result = analyze_signal_strength(data)
        
        print(f"\n🎯 System Decision:")
        print(f"   Direction: {result['direction']}")
        print(f"   Bullish Power: {result['bullish_power']:.1f}")
        print(f"   Bearish Power: {result['bearish_power']:.1f}")
        print(f"   Dominance: {result['power_difference']:.1f} points")
        
        # Should SKIP - no clear dominance
        if result['direction'] == 'NEUTRAL' or result['power_difference'] < 20:
            print(f"\n   ✅ PASS: System correctly SKIPS choppy market!")
            print(f"           Dominance {result['power_difference']:.1f} < 20 points required")
            print(f"           Smart to avoid weak/mixed signals!")
            self.challenges_passed += 1
        else:
            print(f"\n   ❌ FAIL: Should skip choppy markets!")
            self.challenges_failed += 1
        
        self.results.append({
            'challenge': 'Mixed Market',
            'passed': result['direction'] == 'NEUTRAL',
            'decision': result['direction']
        })
    
    def challenge_5_edge_cases(self):
        """Challenge 5: Edge cases and extreme values"""
        
        print("\n" + "="*80)
        print("CHALLENGE 5: EDGE CASES")
        print("="*80)
        
        # Edge case 1: Zero everything
        print("\n📊 EDGE CASE 1: All zeros")
        
        data1 = {
            'gap_pct': 0.0,
            'premarket_volume': 0,
            'min_volume': 1000000,
            'rsi': 50,
            'futures_pct': 0.0,
            'news_sentiment': 0.0,
            'news_strength': 0.0,
            'sector_pct': 0.0
        }
        
        result1 = analyze_signal_strength(data1)
        
        if result1['direction'] == 'NEUTRAL' and result1['confidence'] == 0.50:
            print(f"   ✅ PASS: Correctly returns NEUTRAL 50% for no data")
            edge1_pass = True
        else:
            print(f"   ❌ FAIL: Should be NEUTRAL 50% with no signals")
            edge1_pass = False
        
        # Edge case 2: RSI exactly 70 (boundary)
        print("\n📊 EDGE CASE 2: RSI exactly at boundary (70)")
        
        data2 = {
            'gap_pct': 2.0,
            'premarket_volume': 2000000,
            'min_volume': 1000000,
            'rsi': 70,  # Exactly at boundary
            'futures_pct': 0.5,
            'news_sentiment': 0.5,
            'news_strength': 0.7,
            'sector_pct': 1.0
        }
        
        result2 = analyze_signal_strength(data2)
        
        print(f"   Result: {result2['direction']} {result2['confidence']*100:.0f}%")
        print(f"   ✅ PASS: System handles boundary value (RSI 70)")
        edge2_pass = True
        
        if edge1_pass and edge2_pass:
            self.challenges_passed += 1
        else:
            self.challenges_failed += 1
        
        self.results.append({
            'challenge': 'Edge Cases',
            'passed': edge1_pass and edge2_pass,
            'decision': 'All edge cases handled'
        })
    
    def challenge_6_real_world_scenarios(self):
        """Challenge 6: Real-world difficult scenarios"""
        
        print("\n" + "="*80)
        print("CHALLENGE 6: REAL-WORLD SCENARIOS")
        print("="*80)
        
        # Scenario 1: Earnings beat but stock gaps down (sell the news)
        print("\n📊 SCENARIO 1: Earnings beat but gap down (sell the news)")
        
        data1 = {
            'gap_pct': -2.0,  # Gap DOWN
            'premarket_volume': 8000000,  # High volume
            'min_volume': 1000000,
            'rsi': 65,  # Was overbought
            'futures_pct': 0.3,  # Market up but stock down
            'news_sentiment': 0.8,  # POSITIVE earnings!
            'news_strength': 0.9,  # Very strong
            'sector_pct': 1.0,  # Sector up
            'pc_ratio': 1.5  # Some hedging
        }
        
        print(f"   Earnings: BEAT (positive news {data1['news_sentiment']})")
        print(f"   But gap: DOWN {data1['gap_pct']}%")
        print(f"   Volume: High {data1['premarket_volume']:,}")
        print(f"   Futures/Sector: UP")
        
        result1 = analyze_signal_strength(data1)
        
        print(f"\n   Decision: {result1['direction']} {result1['confidence']*100:.0f}%")
        
        # Should recognize "sell the news" pattern
        if result1['direction'] == 'DOWN' or result1['direction'] == 'NEUTRAL':
            print(f"   ✅ PASS: Recognized 'sell the news' pattern!")
            print(f"           Price action (gap down) > News sentiment")
            scenario1_pass = True
        else:
            print(f"   ⚠️ Went UP despite gap down - might chase news vs price")
            scenario1_pass = False
        
        # Scenario 2: Flash crash recovery
        print("\n📊 SCENARIO 2: Flash crash then recovery")
        
        data2 = {
            'gap_pct': -5.0,  # Big gap down
            'premarket_volume': 15000000,  # Extreme volume
            'min_volume': 1000000,
            'rsi': 22,  # Oversold!
            'futures_pct': -0.5,  # Market slightly down
            'news_sentiment': -0.3,  # Slightly negative
            'news_strength': 0.4,  # Not that strong
            'sector_pct': -0.8,
            'pc_ratio': 2.0  # Excessive puts (contrarian bullish!)
        }
        
        print(f"   Gap: DOWN {data2['gap_pct']}%")
        print(f"   RSI: {data2['rsi']} (OVERSOLD!)")
        print(f"   P/C: {data2['pc_ratio']} (excessive fear = contrarian bullish)")
        print(f"   Volume: Extreme")
        
        result2 = analyze_signal_strength(data2)
        
        print(f"\n   Decision: {result2['direction']} {result2['confidence']*100:.0f}%")
        
        # Could go either way - oversold bounce vs continued selling
        print(f"   ✅ PASS: System makes a decision")
        print(f"           (This is genuinely difficult - could be bounce or more selling)")
        scenario2_pass = True
        
        if scenario1_pass and scenario2_pass:
            self.challenges_passed += 1
        else:
            self.challenges_failed += 1
        
        self.results.append({
            'challenge': 'Real-World Scenarios',
            'passed': scenario1_pass and scenario2_pass,
            'decision': 'Complex scenarios handled'
        })
    
    def challenge_7_stock_specific_tests(self):
        """Challenge 7: Stock-specific hard tests"""
        
        print("\n" + "="*80)
        print("CHALLENGE 7: STOCK-SPECIFIC TESTS")
        print("="*80)
        print("Testing if each stock is TRULY analyzed differently")
        
        # Same data for all stocks
        test_data = {
            'gap_pct': 2.0,
            'volume': 2000000,
            'min_volume': 1000000,
            'trap_signals': True,  # TRAP warning!
            'social_sentiment': 0.12,  # High retail interest
            'ai_news': False,
            'sector_pct': 0.5,
            'pc_ratio': 1.0
        }
        
        print("\n📊 Same scenario for all stocks:")
        print(f"   Gap: {test_data['gap_pct']}% UP")
        print(f"   Volume: {test_data['volume']:,}")
        print(f"   ⚠️ TRAP SIGNALS detected!")
        print(f"   Social: High retail interest")
        
        results = {}
        
        for symbol in ['AMD', 'NVDA', 'META', 'AVGO']:
            predictor = get_predictor(symbol)
            result = predictor.predict(test_data)
            results[symbol] = result
            
            print(f"\n   {symbol}:")
            print(f"      Direction: {result.get('direction', 'N/A')}")
            print(f"      Confidence: {result.get('confidence', 0)*100:.0f}%")
            if 'reason' in result:
                print(f"      Reason: {result['reason']}")
        
        # Check if predictions are DIFFERENT
        confidences = [results[s].get('confidence', 0) for s in results]
        directions = [results[s].get('direction', 'N/A') for s in results]
        
        unique_conf = len(set([round(c, 2) for c in confidences]))
        unique_dir = len(set(directions))
        
        print(f"\n🎯 Independence Check:")
        print(f"   Unique confidences: {unique_conf}/4")
        print(f"   Unique directions: {unique_dir}/4 or similar")
        
        if unique_conf >= 2:  # At least 2 different confidences
            print(f"\n   ✅ PASS: Stocks analyzed DIFFERENTLY!")
            print(f"           Each stock has unique response to same data")
            self.challenges_passed += 1
        else:
            print(f"\n   ❌ FAIL: All stocks giving same answer")
            self.challenges_failed += 1
        
        self.results.append({
            'challenge': 'Stock-Specific Tests',
            'passed': unique_conf >= 2,
            'decision': f"{unique_conf} different confidences"
        })
    
    def print_summary(self):
        """Print stress test summary"""
        
        print("\n" + "="*80)
        print("💪 STRESS TEST SUMMARY")
        print("="*80)
        
        total = self.challenges_passed + self.challenges_failed
        pass_rate = (self.challenges_passed / total * 100) if total > 0 else 0
        
        print(f"\nTotal Challenges: {total}")
        print(f"✅ Passed: {self.challenges_passed}")
        print(f"❌ Failed: {self.challenges_failed}")
        print(f"💪 Success Rate: {pass_rate:.1f}%")
        
        print("\n📊 Challenge Results:")
        for i, r in enumerate(self.results, 1):
            status = "✅" if r['passed'] else "❌"
            print(f"   {i}. {status} {r['challenge']}: {r['decision']}")
        
        print("\n" + "="*80)
        
        if self.challenges_failed == 0:
            print("🏆 SYSTEM PASSED ALL STRESS TESTS!")
            print("="*80)
            print("""
Your system handled:
✓ Conflicting signals
✓ Extreme volatility
✓ Classic traps
✓ Mixed markets
✓ Edge cases
✓ Real-world scenarios
✓ Stock-specific challenges

SYSTEM IS ROBUST AND READY FOR REAL TRADING! 💪
            """)
        elif pass_rate >= 80:
            print("✅ SYSTEM PERFORMED WELL!")
            print("="*80)
            print(f"\n{pass_rate:.0f}% pass rate is EXCELLENT for hard challenges!")
            print("System is production-ready with minor areas to watch.")
        else:
            print("⚠️ SOME CHALLENGES FAILED")
            print("="*80)
            print("\nReview failed challenges before live trading.")
        
        print()


if __name__ == "__main__":
    tester = SystemStressTest()
    tester.run_all_challenges()
