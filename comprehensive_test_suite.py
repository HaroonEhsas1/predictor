"""
COMPREHENSIVE TEST SUITE - ALL DIFFICULTY LEVELS
Tests each stock at Easy, Medium, Hard, and Extreme difficulty levels

Tests:
- Easy: Clear signals, obvious patterns
- Medium: Some conflicts, moderate complexity
- Hard: Mixed signals, trap patterns
- Extreme: Worst-case scenarios, edge cases

Each stock gets tested with scenarios matching its unique patterns
"""

from stock_specific_predictors import get_predictor
from signal_strength_system import analyze_signal_strength
import json

class ComprehensiveTestSuite:
    """Test system at all difficulty levels for each stock"""
    
    def __init__(self):
        self.stocks = ['AMD', 'NVDA', 'META', 'AVGO']
        self.results = {
            'easy': {'passed': 0, 'failed': 0, 'tests': []},
            'medium': {'passed': 0, 'failed': 0, 'tests': []},
            'hard': {'passed': 0, 'failed': 0, 'tests': []},
            'extreme': {'passed': 0, 'failed': 0, 'tests': []}
        }
        
    def run_all_tests(self):
        """Run complete test suite"""
        
        print("\n" + "="*80)
        print("🧪 COMPREHENSIVE TEST SUITE - ALL DIFFICULTY LEVELS")
        print("="*80)
        print("""
Testing 4 stocks × 4 difficulty levels = 16+ scenarios

Difficulty Levels:
✓ EASY: Clear signals, obvious trades
✓ MEDIUM: Some complexity, moderate confidence
✓ HARD: Mixed signals, trap detection needed
✓ EXTREME: Worst-case, edge cases, stress scenarios

Each stock tested with its UNIQUE patterns!
        """)
        
        # Run tests for each difficulty level
        self.test_easy_scenarios()
        self.test_medium_scenarios()
        self.test_hard_scenarios()
        self.test_extreme_scenarios()
        
        # Print comprehensive summary
        self.print_final_summary()
        
    def test_easy_scenarios(self):
        """EASY tests - Clear signals, should easily pass"""
        
        print("\n" + "="*80)
        print("✅ LEVEL 1: EASY TESTS")
        print("="*80)
        print("Clear signals, obvious patterns - System should EASILY handle these\n")
        
        # AMD EASY: Strong gap with good volume
        print("📊 AMD EASY TEST: Strong gap + good volume")
        amd_easy = {
            'gap_pct': 2.5,
            'volume': 5000000,  # Excellent
            'min_volume': 1000000,
            'trap_signals': False,
            'social_sentiment': 0.05,  # Moderate (not extreme)
        }
        
        predictor = get_predictor('AMD')
        result = predictor.predict(amd_easy)
        
        # Should be bullish with good confidence
        if result['direction'] == 'UP' and result['confidence'] > 0.60:
            print(f"   ✅ PASS: AMD {result['direction']} {result['confidence']*100:.0f}%")
            print(f"           {result['reason']}")
            self.results['easy']['passed'] += 1
            self.results['easy']['tests'].append(('AMD Easy', True, result['confidence']))
        else:
            print(f"   ❌ FAIL: Should be bullish with strong gap + volume")
            self.results['easy']['failed'] += 1
            self.results['easy']['tests'].append(('AMD Easy', False, result.get('confidence', 0)))
        
        # NVDA EASY: Strong gap + AI news + sector aligned
        print("\n📊 NVDA EASY TEST: AI news + strong sector alignment")
        nvda_easy = {
            'gap_pct': 2.0,
            'volume': 5000000,
            'min_volume': 300000,
            'trap_signals': False,
            'ai_news': True,  # NVDA responds to AI news!
            'sector_pct': 1.5,  # Sector strong
        }
        
        predictor = get_predictor('NVDA')
        result = predictor.predict(nvda_easy)
        
        if result['direction'] == 'UP' and result['confidence'] > 0.70:
            print(f"   ✅ PASS: NVDA {result['direction']} {result['confidence']*100:.0f}%")
            print(f"           {result['reason']}")
            self.results['easy']['passed'] += 1
            self.results['easy']['tests'].append(('NVDA Easy', True, result['confidence']))
        else:
            print(f"   ❌ FAIL: Should be very bullish with AI news + sector")
            self.results['easy']['failed'] += 1
            self.results['easy']['tests'].append(('NVDA Easy', False, result.get('confidence', 0)))
        
        # META EASY: Good gap + user growth news
        print("\n📊 META EASY TEST: Strong gap + positive user news")
        meta_easy = {
            'gap_pct': 2.0,
            'volume': 3000000,
            'min_volume': 200000,
            'trap_signals': False,
            'user_news': True,  # META-specific catalyst
            'regulatory_news': False,
        }
        
        predictor = get_predictor('META')
        result = predictor.predict(meta_easy)
        
        if result['direction'] == 'UP' and result['confidence'] > 0.65:
            print(f"   ✅ PASS: META {result['direction']} {result['confidence']*100:.0f}%")
            print(f"           {result['reason']}")
            self.results['easy']['passed'] += 1
            self.results['easy']['tests'].append(('META Easy', True, result['confidence']))
        else:
            print(f"   ❌ FAIL: Should be bullish with user news")
            self.results['easy']['failed'] += 1
            self.results['easy']['tests'].append(('META Easy', False, result.get('confidence', 0)))
        
        # AVGO EASY: Large gap + institutional confirmation
        print("\n📊 AVGO EASY TEST: Gap + institutional confirmation (rare!)")
        avgo_easy = {
            'gap_pct': 3.0,
            'volume': 5000000,  # Very high (2x minimum)
            'min_volume': 150000,
            'trap_signals': False,
            'ma_rumors': True,
            'institutional_confirmation': True,  # CRITICAL for AVGO!
            'institutional_buying': True,
        }
        
        predictor = get_predictor('AVGO')
        result = predictor.predict(avgo_easy)
        
        if result['direction'] == 'UP' and result['confidence'] > 0.65:
            print(f"   ✅ PASS: AVGO {result['direction']} {result['confidence']*100:.0f}%")
            print(f"           {result['reason']}")
            self.results['easy']['passed'] += 1
            self.results['easy']['tests'].append(('AVGO Easy', True, result['confidence']))
        else:
            print(f"   ❌ FAIL: Should be bullish with institutional backing")
            self.results['easy']['failed'] += 1
            self.results['easy']['tests'].append(('AVGO Easy', False, result.get('confidence', 0)))
    
    def test_medium_scenarios(self):
        """MEDIUM tests - Moderate complexity"""
        
        print("\n" + "="*80)
        print("⚡ LEVEL 2: MEDIUM TESTS")
        print("="*80)
        print("Moderate complexity - Some conflicts but manageable\n")
        
        # AMD MEDIUM: Gap up but high social sentiment (danger!)
        print("📊 AMD MEDIUM TEST: Gap up but social hype risk")
        amd_medium = {
            'gap_pct': 2.0,
            'volume': 2500000,
            'min_volume': 1000000,
            'trap_signals': False,
            'social_sentiment': 0.12,  # HIGH retail interest (AMD trap pattern!)
        }
        
        predictor = get_predictor('AMD')
        result = predictor.predict(amd_medium)
        
        # AMD should reduce confidence due to social hype
        if result['confidence'] < 0.65:  # Lower than easy test
            print(f"   ✅ PASS: AMD {result['direction']} {result['confidence']*100:.0f}%")
            print(f"           Correctly penalized for social hype!")
            self.results['medium']['passed'] += 1
            self.results['medium']['tests'].append(('AMD Medium', True, result['confidence']))
        else:
            print(f"   ⚠️ Confidence {result['confidence']*100:.0f}% - should be lower for hype risk")
            self.results['medium']['failed'] += 1
            self.results['medium']['tests'].append(('AMD Medium', False, result['confidence']))
        
        # NVDA MEDIUM: Good signals but no AI news
        print("\n📊 NVDA MEDIUM TEST: Gap without AI catalyst")
        nvda_medium = {
            'gap_pct': 2.0,
            'volume': 3000000,
            'min_volume': 300000,
            'trap_signals': False,
            'ai_news': False,  # No AI news - less boost
            'sector_pct': 0.5,  # Moderate sector
        }
        
        predictor = get_predictor('NVDA')
        result = predictor.predict(nvda_medium)
        
        # Should be moderate confidence (no AI boost)
        if 0.50 < result.get('confidence', 0) < 0.75:
            print(f"   ✅ PASS: NVDA {result['direction']} {result['confidence']*100:.0f}%")
            print(f"           Moderate confidence without AI news")
            self.results['medium']['passed'] += 1
            self.results['medium']['tests'].append(('NVDA Medium', True, result['confidence']))
        else:
            print(f"   ⚠️ Should have moderate confidence without catalysts")
            self.results['medium']['failed'] += 1
            self.results['medium']['tests'].append(('NVDA Medium', False, result.get('confidence', 0)))
        
        # META MEDIUM: Gap up but some regulatory concerns
        print("\n📊 META MEDIUM TEST: Gap up but regulatory headwinds")
        meta_medium = {
            'gap_pct': 1.8,
            'volume': 2000000,
            'min_volume': 200000,
            'trap_signals': False,
            'regulatory_news': True,  # META-specific risk!
            'user_news': False,
        }
        
        predictor = get_predictor('META')
        result = predictor.predict(meta_medium)
        
        # Should be cautious due to regulatory news
        if result.get('confidence', 0) < 0.70:
            print(f"   ✅ PASS: META {result['direction']} {result.get('confidence', 0)*100:.0f}%")
            print(f"           Correctly cautious about regulatory risk")
            self.results['medium']['passed'] += 1
            self.results['medium']['tests'].append(('META Medium', True, result.get('confidence', 0)))
        else:
            print(f"   ⚠️ Should be more cautious with regulatory news")
            self.results['medium']['failed'] += 1
            self.results['medium']['tests'].append(('META Medium', False, result.get('confidence', 0)))
        
        # AVGO MEDIUM: Gap up with M&A rumors but no confirmation
        print("\n📊 AVGO MEDIUM TEST: M&A rumors without confirmation")
        avgo_medium = {
            'gap_pct': 2.5,
            'volume': 2000000,
            'min_volume': 150000,
            'trap_signals': False,
            'ma_rumors': True,
            'institutional_confirmation': False,  # DANGER for AVGO!
        }
        
        predictor = get_predictor('AVGO')
        result = predictor.predict(avgo_medium)
        
        # AVGO should be very cautious - unconfirmed M&A often trap
        if result.get('confidence', 1) < 0.60 or result['direction'] == 'NEUTRAL':
            print(f"   ✅ PASS: AVGO {result['direction']} {result.get('confidence', 0)*100:.0f}%")
            print(f"           Correctly skeptical of unconfirmed M&A")
            self.results['medium']['passed'] += 1
            self.results['medium']['tests'].append(('AVGO Medium', True, result.get('confidence', 0)))
        else:
            print(f"   ⚠️ Should be very cautious with unconfirmed M&A rumors")
            self.results['medium']['failed'] += 1
            self.results['medium']['tests'].append(('AVGO Medium', False, result.get('confidence', 0)))
    
    def test_hard_scenarios(self):
        """HARD tests - Mixed signals, trap detection critical"""
        
        print("\n" + "="*80)
        print("🔥 LEVEL 3: HARD TESTS")
        print("="*80)
        print("Mixed signals and trap patterns - Real decision-making needed\n")
        
        # AMD HARD: Gap up on weak volume (classic AMD trap!)
        print("📊 AMD HARD TEST: Classic weak volume trap")
        amd_hard = {
            'gap_pct': 2.5,
            'volume': 800000,  # WEAK! (< 1M minimum)
            'min_volume': 1000000,
            'trap_signals': True,
            'social_sentiment': 0.15,  # Very high hype
        }
        
        predictor = get_predictor('AMD')
        result = predictor.predict(amd_hard)
        
        # Should skip or very low confidence
        if result['direction'] == 'NEUTRAL' or result.get('confidence', 1) < 0.50:
            print(f"   ✅ PASS: AMD {result['direction']} {result.get('confidence', 0)*100:.0f}%")
            print(f"           Correctly detected AMD's weak volume trap!")
            self.results['hard']['passed'] += 1
            self.results['hard']['tests'].append(('AMD Hard', True, result.get('confidence', 0)))
        else:
            print(f"   ❌ FAIL: Should detect weak volume + hype trap!")
            self.results['hard']['failed'] += 1
            self.results['hard']['tests'].append(('AMD Hard', False, result.get('confidence', 0)))
        
        # NVDA HARD: Gap up but very overbought + high traps
        print("\n📊 NVDA HARD TEST: Gap up but high trap rate scenario")
        nvda_hard = {
            'gap_pct': 2.5,
            'volume': 2000000,
            'min_volume': 300000,
            'trap_signals': True,  # NVDA has 53% trap rate!
            'ai_news': False,
            'sector_pct': -0.5,  # Sector diverging!
        }
        
        predictor = get_predictor('NVDA')
        result = predictor.predict(nvda_hard)
        
        # Should be cautious - NVDA trap rate is 53%
        if result['direction'] == 'NEUTRAL' or result.get('confidence', 1) < 0.60:
            print(f"   ✅ PASS: NVDA {result['direction']} {result.get('confidence', 0)*100:.0f}%")
            print(f"           Recognized high trap risk + sector divergence")
            self.results['hard']['passed'] += 1
            self.results['hard']['tests'].append(('NVDA Hard', True, result.get('confidence', 0)))
        else:
            print(f"   ❌ FAIL: Should be cautious given NVDA's 53% trap rate")
            self.results['hard']['failed'] += 1
            self.results['hard']['tests'].append(('NVDA Hard', False, result.get('confidence', 0)))
        
        # META HARD: Choppy momentum (META's weakness!)
        print("\n📊 META HARD TEST: Weak momentum scenario")
        meta_hard = {
            'gap_pct': 1.5,
            'volume': 1500000,
            'min_volume': 200000,
            'trap_signals': False,
            'prev_day_momentum': True,  # But META only 41% continuation!
            'regulatory_news': True,
        }
        
        predictor = get_predictor('META')
        result = predictor.predict(meta_hard)
        
        # META weak momentum (41%) should result in caution
        if result.get('confidence', 1) < 0.65:
            print(f"   ✅ PASS: META {result['direction']} {result.get('confidence', 0)*100:.0f}%")
            print(f"           Accounts for META's weak momentum (41%)")
            self.results['hard']['passed'] += 1
            self.results['hard']['tests'].append(('META Hard', True, result.get('confidence', 0)))
        else:
            print(f"   ⚠️ Should have lower confidence given weak momentum")
            self.results['hard']['failed'] += 1
            self.results['hard']['tests'].append(('META Hard', False, result.get('confidence', 0)))
        
        # AVGO HARD: Gap up with all AVGO trap patterns!
        print("\n📊 AVGO HARD TEST: Multiple AVGO-specific traps")
        avgo_hard = {
            'gap_pct': 2.8,
            'volume': 1800000,  # Just above 1x minimum, not 2x
            'min_volume': 150000,
            'trap_signals': True,
            'ma_rumors': True,
            'institutional_confirmation': False,  # No confirmation
            'institutional_buying': False,  # No buying
        }
        
        predictor = get_predictor('AVGO')
        result = predictor.predict(avgo_hard)
        
        # AVGO should strongly reject this (57% trap rate + no confirmation)
        if result['direction'] == 'NEUTRAL' or result.get('confidence', 1) < 0.50:
            print(f"   ✅ PASS: AVGO {result['direction']} {result.get('confidence', 0)*100:.0f}%")
            print(f"           Correctly rejected AVGO trap (57% trap rate!)")
            self.results['hard']['passed'] += 1
            self.results['hard']['tests'].append(('AVGO Hard', True, result.get('confidence', 0)))
        else:
            print(f"   ❌ FAIL: Should strongly reject (AVGO has 57% trap rate!)")
            self.results['hard']['failed'] += 1
            self.results['hard']['tests'].append(('AVGO Hard', False, result.get('confidence', 0)))
    
    def test_extreme_scenarios(self):
        """EXTREME tests - Worst-case scenarios"""
        
        print("\n" + "="*80)
        print("💀 LEVEL 4: EXTREME TESTS")
        print("="*80)
        print("Worst-case scenarios - System must protect capital!\n")
        
        # AMD EXTREME: Extreme gap with reversal pattern
        print("📊 AMD EXTREME TEST: 7% gap (exhaustion) + reversal risk")
        amd_extreme = {
            'gap_pct': 7.0,  # EXTREME!
            'volume': 10000000,
            'min_volume': 1000000,
            'trap_signals': True,
            'social_sentiment': 0.20,  # Extreme hype
        }
        
        predictor = get_predictor('AMD')
        result = predictor.predict(amd_extreme)
        
        # Should skip - extreme gaps often reverse + 45.5% intraday reversal rate!
        if result['direction'] == 'NEUTRAL' or result.get('confidence', 1) < 0.50:
            print(f"   ✅ PASS: AMD {result['direction']} {result.get('confidence', 0)*100:.0f}%")
            print(f"           Correctly avoided exhaustion + reversal risk")
            print(f"           (AMD has 45.5% intraday reversal rate!)")
            self.results['extreme']['passed'] += 1
            self.results['extreme']['tests'].append(('AMD Extreme', True, result.get('confidence', 0)))
        else:
            print(f"   ❌ FAIL: Should skip 7% gap with extreme hype!")
            self.results['extreme']['failed'] += 1
            self.results['extreme']['tests'].append(('AMD Extreme', False, result.get('confidence', 0)))
        
        # NVDA EXTREME: Gap down despite AI news (sell the news)
        print("\n📊 NVDA EXTREME TEST: Gap DOWN despite positive AI news")
        nvda_extreme = {
            'gap_pct': -2.5,  # Gap DOWN
            'volume': 8000000,
            'min_volume': 300000,
            'trap_signals': False,
            'ai_news': True,  # Positive but stock down = sell the news!
            'sector_pct': 1.0,  # Sector up but stock down
        }
        
        predictor = get_predictor('NVDA')
        result = predictor.predict(nvda_extreme)
        
        # Should recognize price action > news
        if result['direction'] == 'DOWN' or result['direction'] == 'NEUTRAL':
            print(f"   ✅ PASS: NVDA {result['direction']} {result.get('confidence', 0)*100:.0f}%")
            print(f"           Price action overrode positive news!")
            self.results['extreme']['passed'] += 1
            self.results['extreme']['tests'].append(('NVDA Extreme', True, result.get('confidence', 0)))
        else:
            print(f"   ❌ FAIL: Should follow price action, not news!")
            self.results['extreme']['failed'] += 1
            self.results['extreme']['tests'].append(('NVDA Extreme', False, result.get('confidence', 0)))
        
        # META EXTREME: All signals mediocre (choppy)
        print("\n📊 META EXTREME TEST: Choppy market (META's weakness)")
        meta_extreme = {
            'gap_pct': 0.8,  # Small
            'volume': 1200000,  # Barely above min
            'min_volume': 200000,
            'trap_signals': False,
            'user_news': False,
            'regulatory_news': False,
            'prev_day_momentum': False,
        }
        
        predictor = get_predictor('META')
        result = predictor.predict(meta_extreme)
        
        # META weak momentum (41%) + no clear signals = skip
        if result['direction'] == 'NEUTRAL' or result.get('confidence', 1) < 0.55:
            print(f"   ✅ PASS: META {result['direction']} {result.get('confidence', 0)*100:.0f}%")
            print(f"           Correctly skipped choppy scenario")
            print(f"           (META has weakest momentum: 41%)")
            self.results['extreme']['passed'] += 1
            self.results['extreme']['tests'].append(('META Extreme', True, result.get('confidence', 0)))
        else:
            print(f"   ❌ FAIL: Should skip unclear/choppy market!")
            self.results['extreme']['failed'] += 1
            self.results['extreme']['tests'].append(('META Extreme', False, result.get('confidence', 0)))
        
        # AVGO EXTREME: Perfect trap scenario
        print("\n📊 AVGO EXTREME TEST: Perfect AVGO trap (all red flags)")
        avgo_extreme = {
            'gap_pct': 4.0,  # Large gap
            'volume': 800000,  # Weak for gap size
            'min_volume': 150000,
            'trap_signals': True,
            'ma_rumors': True,
            'institutional_confirmation': False,
            'institutional_buying': False,
        }
        
        predictor = get_predictor('AVGO')
        result = predictor.predict(avgo_extreme)
        
        # AVGO should STRONGLY reject (57% trap rate + all red flags!)
        if result['direction'] == 'NEUTRAL' or result.get('confidence', 1) < 0.40:
            print(f"   ✅ PASS: AVGO {result['direction']} {result.get('confidence', 0)*100:.0f}%")
            print(f"           STRONGLY rejected AVGO trap!")
            print(f"           (AVGO: 57% trap rate, 43% gap follow-through)")
            self.results['extreme']['passed'] += 1
            self.results['extreme']['tests'].append(('AVGO Extreme', True, result.get('confidence', 0)))
        else:
            print(f"   ❌ FAIL: Should STRONGLY reject all AVGO red flags!")
            self.results['extreme']['failed'] += 1
            self.results['extreme']['tests'].append(('AVGO Extreme', False, result.get('confidence', 0)))
    
    def print_final_summary(self):
        """Print comprehensive test summary"""
        
        print("\n" + "="*80)
        print("📊 COMPREHENSIVE TEST SUMMARY")
        print("="*80)
        
        total_passed = sum(r['passed'] for r in self.results.values())
        total_failed = sum(r['failed'] for r in self.results.values())
        total_tests = total_passed + total_failed
        pass_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n🎯 OVERALL RESULTS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   ✅ Passed: {total_passed}")
        print(f"   ❌ Failed: {total_failed}")
        print(f"   📊 Pass Rate: {pass_rate:.1f}%")
        
        print(f"\n📈 BY DIFFICULTY LEVEL:")
        for level in ['easy', 'medium', 'hard', 'extreme']:
            data = self.results[level]
            total = data['passed'] + data['failed']
            rate = (data['passed'] / total * 100) if total > 0 else 0
            
            if level == 'easy':
                icon = "✅"
            elif level == 'medium':
                icon = "⚡"
            elif level == 'hard':
                icon = "🔥"
            else:
                icon = "💀"
            
            print(f"   {icon} {level.upper():8s}: {data['passed']}/{total} ({rate:.0f}%)")
        
        print(f"\n📋 DETAILED RESULTS:")
        for level in ['easy', 'medium', 'hard', 'extreme']:
            print(f"\n   {level.upper()}:")
            for test_name, passed, conf in self.results[level]['tests']:
                status = "✅" if passed else "❌"
                print(f"      {status} {test_name:20s} ({conf*100:.0f}% conf)")
        
        print("\n" + "="*80)
        
        if pass_rate >= 90:
            print("🏆 EXCELLENT! System handles ALL difficulty levels!")
            print("="*80)
            print("""
✓ EASY scenarios: Handled perfectly
✓ MEDIUM complexity: Managed well
✓ HARD mixed signals: Intelligent decisions
✓ EXTREME cases: Protected capital

SYSTEM IS PRODUCTION READY FOR ALL SCENARIOS! 💪
            """)
        elif pass_rate >= 75:
            print("✅ VERY GOOD! System is robust across difficulty levels")
            print("="*80)
            print(f"\n{pass_rate:.0f}% pass rate is STRONG!")
            print("System is ready for live trading.")
        else:
            print("⚠️ NEEDS IMPROVEMENT")
            print("="*80)
            print("\nReview failed tests before live trading.")
        
        print()


if __name__ == "__main__":
    suite = ComprehensiveTestSuite()
    suite.run_all_tests()
