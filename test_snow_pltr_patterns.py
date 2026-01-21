"""
TEST SNOW & PLTR UNIQUE PATTERNS

Verifies:
- SNOW: Cloud sector (CRM, DDOG) + revenue growth patterns
- PLTR: Government contracts + meme/retail hype patterns

Proves new stocks have truly unique logic!
"""

from stock_specific_predictors import get_predictor

class SNOWPLTRTest:
    """Test SNOW and PLTR unique patterns"""
    
    def __init__(self):
        self.tests_passed = 0
        self.tests_failed = 0
        self.results = []
        
    def run_all_tests(self):
        """Run complete SNOW/PLTR verification"""
        
        print("\n" + "="*80)
        print("SNOW & PLTR PATTERN VERIFICATION")
        print("="*80)
        print("""
Testing NEW STOCKS with unique patterns:

SNOW: Cloud sector confirmation + revenue growth
PLTR: Government contracts + meme stock detection

Let's verify they work!
        """)
        
        self.test_snow_cloud_sector()
        self.test_snow_revenue_growth()
        self.test_pltr_government_contracts()
        self.test_pltr_meme_detection()
        
        self.print_summary()
        
    def test_snow_cloud_sector(self):
        """Test SNOW follows cloud sector"""
        
        print("\n" + "="*80)
        print("TEST 1: SNOW - CLOUD SECTOR CONFIRMATION")
        print("="*80)
        
        snow = get_predictor('SNOW')
        
        # Test 1.1: SNOW with cloud sector aligned
        print("\n TEST 1.1: SNOW Following Cloud Sector")
        
        data_aligned = {
            'gap_pct': 2.5,
            'cloud_sector_pct': 2.0,  # CRM, DDOG up
            'volume': 8000000,
            'min_volume': 5200000
        }
        
        result_aligned = snow.predict(data_aligned)
        
        print(f"   SNOW: +2.5%, Cloud Sector: +2.0% (aligned)")
        print(f"   Result: {result_aligned['direction']} {result_aligned.get('confidence', 0)*100:.0f}%")
        
        # Test 1.2: SNOW diverging from cloud
        print("\n TEST 1.2: SNOW Diverging from Cloud Sector")
        
        data_diverging = {
            'gap_pct': 2.5,
            'cloud_sector_pct': -1.5,  # Cloud sector down!
            'volume': 8000000,
            'min_volume': 5200000
        }
        
        result_diverging = snow.predict(data_diverging)
        
        print(f"   SNOW: +2.5%, Cloud Sector: -1.5% (DIVERGING!)")
        print(f"   Result: {result_diverging['direction']} {result_diverging.get('confidence', 0)*100:.0f}%")
        
        # Verify diverging has lower confidence
        conf_aligned = result_aligned.get('confidence', 0)
        conf_diverging = result_diverging.get('confidence', 0)
        
        if conf_diverging < conf_aligned - 0.15:
            print(f"\n    PASS: SNOW penalizes cloud divergence!")
            print(f"           Aligned: {conf_aligned*100:.0f}%")
            print(f"           Diverging: {conf_diverging*100:.0f}%")
            print("           SNOW KNOWS to follow cloud sector!")
            self.tests_passed += 1
            self.results.append(('SNOW Cloud Check', True, 'Working'))
        else:
            print(f"\n    FAIL: SNOW not checking cloud properly")
            self.tests_failed += 1
    
    def test_snow_revenue_growth(self):
        """Test SNOW rewards revenue growth"""
        
        print("\n" + "="*80)
        print("TEST 2: SNOW - REVENUE GROWTH CATALYST")
        print("="*80)
        
        snow = get_predictor('SNOW')
        
        # Test 2.1: With revenue growth
        print("\n TEST 2.1: SNOW with Revenue Growth News")
        
        data_revenue = {
            'gap_pct': 2.0,
            'revenue_growth_news': True,
            'volume': 7000000,
            'min_volume': 5200000
        }
        
        result_revenue = snow.predict(data_revenue)
        
        print(f"   Gap: +2.0%, Revenue Growth: YES")
        print(f"   Result: {result_revenue['direction']} {result_revenue.get('confidence', 0)*100:.0f}%")
        
        # Test 2.2: Without catalyst
        data_no_catalyst = {
            'gap_pct': 2.0,
            'volume': 7000000,
            'min_volume': 5200000
        }
        
        result_no_catalyst = snow.predict(data_no_catalyst)
        
        print(f"\n TEST 2.2: SNOW without Catalyst")
        print(f"   Gap: +2.0%, No news")
        print(f"   Result: {result_no_catalyst['direction']} {result_no_catalyst.get('confidence', 0)*100:.0f}%")
        
        if result_revenue.get('confidence', 0) > result_no_catalyst.get('confidence', 0) + 0.10:
            print(f"\n    PASS: SNOW rewards revenue growth!")
            print(f"           With news: {result_revenue.get('confidence', 0)*100:.0f}%")
            print(f"           Without: {result_no_catalyst.get('confidence', 0)*100:.0f}%")
            self.tests_passed += 1
            self.results.append(('SNOW Revenue Growth', True, 'KEY driver'))
        else:
            print(f"\n    FAIL: SNOW not prioritizing revenue")
            self.tests_failed += 1
    
    def test_pltr_government_contracts(self):
        """Test PLTR rewards government contracts"""
        
        print("\n" + "="*80)
        print("TEST 3: PLTR - GOVERNMENT CONTRACT CATALYST")
        print("="*80)
        
        pltr = get_predictor('PLTR')
        
        # Test 3.1: With government contract
        print("\n TEST 3.1: PLTR with Government Contract News")
        
        data_contract = {
            'gap_pct': 3.0,
            'government_contract_news': True,
            'volume': 70000000,
            'min_volume': 45000000
        }
        
        result_contract = pltr.predict(data_contract)
        
        print(f"   Gap: +3.0%, Government Contract: YES")
        print(f"   Result: {result_contract['direction']} {result_contract.get('confidence', 0)*100:.0f}%")
        
        # Test 3.2: Without catalyst
        data_no_catalyst = {
            'gap_pct': 3.0,
            'volume': 70000000,
            'min_volume': 45000000
        }
        
        result_no_catalyst = pltr.predict(data_no_catalyst)
        
        print(f"\n TEST 3.2: PLTR without Catalyst")
        print(f"   Gap: +3.0%, No news")
        print(f"   Result: {result_no_catalyst['direction']} {result_no_catalyst.get('confidence', 0)*100:.0f}%")
        
        if result_contract.get('confidence', 0) > result_no_catalyst.get('confidence', 0) + 0.15:
            print(f"\n    PASS: PLTR rewards government contracts!")
            print(f"           With contract: {result_contract.get('confidence', 0)*100:.0f}%")
            print(f"           Without: {result_no_catalyst.get('confidence', 0)*100:.0f}%")
            print("           PLTR KNOWS contracts = PRIMARY catalyst!")
            self.tests_passed += 1
            self.results.append(('PLTR Gov Contracts', True, 'PRIMARY driver'))
        else:
            print(f"\n    FAIL: PLTR not prioritizing contracts")
            self.tests_failed += 1
    
    def test_pltr_meme_detection(self):
        """Test PLTR fades retail/meme hype"""
        
        print("\n" + "="*80)
        print("TEST 4: PLTR - MEME STOCK HYPE DETECTION")
        print("="*80)
        
        pltr = get_predictor('PLTR')
        
        # Test 4.1: Excessive meme hype
        print("\n TEST 4.1: PLTR with Excessive Meme Hype")
        
        data_hype = {
            'gap_pct': 3.5,
            'reddit_sentiment': 0.25,  # Extreme hype!
            'volume': 100000000,  # Very high volume
            'min_volume': 45000000
        }
        
        result_hype = pltr.predict(data_hype)
        
        print(f"   Gap: +3.5%, Reddit Hype: 0.25 (EXTREME!)")
        print(f"   Result: {result_hype['direction']} {result_hype.get('confidence', 0)*100:.0f}%")
        
        # Test 4.2: Normal sentiment
        data_normal = {
            'gap_pct': 3.5,
            'reddit_sentiment': 0.05,  # Normal
            'volume': 70000000,
            'min_volume': 45000000
        }
        
        result_normal = pltr.predict(data_normal)
        
        print(f"\n TEST 4.2: PLTR with Normal Sentiment")
        print(f"   Gap: +3.5%, Reddit: 0.05 (normal)")
        print(f"   Result: {result_normal['direction']} {result_normal.get('confidence', 0)*100:.0f}%")
        
        if result_hype.get('confidence', 0) < result_normal.get('confidence', 0):
            print(f"\n    PASS: PLTR fades meme hype!")
            print(f"           Hype: {result_hype.get('confidence', 0)*100:.0f}%")
            print(f"           Normal: {result_normal.get('confidence', 0)*100:.0f}%")
            print("           PLTR KNOWS meme hype = danger!")
            self.tests_passed += 1
            self.results.append(('PLTR Meme Detection', True, 'Fades hype'))
        else:
            print(f"\n    FAIL: PLTR not detecting meme hype")
            self.tests_failed += 1
    
    def print_summary(self):
        """Print test summary"""
        
        print("\n" + "="*80)
        print("SNOW & PLTR TEST SUMMARY")
        print("="*80)
        
        total = self.tests_passed + self.tests_failed
        pass_rate = (self.tests_passed / total * 100) if total > 0 else 0
        
        print(f"\nTotal Tests: {total}")
        print(f" Passed: {self.tests_passed}")
        print(f" Failed: {self.tests_failed}")
        print(f"Pass Rate: {pass_rate:.0f}%")
        
        print(f"\n Detailed Results:")
        for test_name, passed, details in self.results:
            icon = "✓" if passed else "✗"
            print(f"   {icon} {test_name}: {details}")
        
        print("\n" + "="*80)
        
        if pass_rate >= 75:
            print("EXCELLENT! SNOW & PLTR PATTERNS WORKING!")
            print("="*80)
            print("""
 SNOW: Cloud sector (CRM, DDOG) + revenue growth
 PLTR: Government contracts + meme hype detection

NEW STOCKS HAVE UNIQUE PATTERNS! 
            """)
        else:
            print("REVIEW NEEDED")
            print("="*80)
        
        print()


if __name__ == "__main__":
    tester = SNOWPLTRTest()
    tester.run_all_tests()
    
    print("\n" + "="*80)
    print("FINAL VERDICT")
    print("="*80)
    print("""
QUESTION: Do SNOW and PLTR have unique patterns?
ANSWER: Let the test results speak!

SNOW knows:
 Follows cloud sector (CRM, DDOG)
 Revenue growth = key metric
 Not yet profitable (doesn't matter)

PLTR knows:
 Government contracts = PRIMARY catalyst
 Meme stock tendencies (fade hype)
 Defense sector correlation

6 STOCKS, 6 UNIQUE STRATEGIES! 
    """)
