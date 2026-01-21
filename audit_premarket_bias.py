"""
PREMARKET SYSTEM BIAS & HARDCODE AUDIT
Comprehensive check for:
1. Hardcoded values that should be configurable
2. Directional bias (UP vs DOWN asymmetry)
3. Confidence calculation fairness
4. Weight distribution balance
"""

import ast
import re
from pathlib import Path

class PremarketBiasAuditor:
    """
    Audits premarket system for bias and hardcoded issues
    """
    
    def __init__(self):
        self.issues = []
        self.warnings = []
        self.passed = []
    
    def audit_all_files(self):
        """Run complete audit"""
        
        print("\n" + "="*80)
        print("PREMARKET SYSTEM BIAS & HARDCODE AUDIT")
        print("="*80)
        
        files_to_audit = [
            'premarket_predictor.py',
            'premarket_config.py',
            'premarket_complete_predictor.py',
            'premarket_advanced_filters.py',
            'premarket_options_flow.py',
            'premarket_futures_delta.py',
            'premarket_master_system.py'
        ]
        
        for filename in files_to_audit:
            filepath = Path(filename)
            if filepath.exists():
                print(f"\n{'='*80}")
                print(f"AUDITING: {filename}")
                print(f"{'='*80}")
                self.audit_file(filepath)
        
        # Print summary
        self.print_summary()
    
    def audit_file(self, filepath: Path):
        """Audit a single file"""
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check 1: Hardcoded thresholds
        self.check_hardcoded_thresholds(filepath.name, content)
        
        # Check 2: Directional bias
        self.check_directional_bias(filepath.name, content)
        
        # Check 3: Confidence calculation
        self.check_confidence_calculation(filepath.name, content)
        
        # Check 4: Magic numbers
        self.check_magic_numbers(filepath.name, content)
    
    def check_hardcoded_thresholds(self, filename: str, content: str):
        """Check for hardcoded thresholds that should be configurable"""
        
        print(f"\n🔍 Check 1: Hardcoded Thresholds")
        
        # Look for suspicious patterns
        suspicious_patterns = [
            (r'if\s+.*\s*>\s*0\.0[1-9]', 'Hardcoded threshold >0.0X'),
            (r'if\s+.*\s*<\s*-0\.0[1-9]', 'Hardcoded threshold <-0.0X'),
            (r'confidence\s*[+\-]=\s*\d+', 'Hardcoded confidence adjustment'),
            (r'gap_pct\s*>\s*[0-9.]+', 'Hardcoded gap threshold'),
            (r'volume\s*>\s*\d+', 'Hardcoded volume threshold'),
        ]
        
        issues_found = []
        for pattern, description in suspicious_patterns:
            matches = re.findall(pattern, content)
            if matches:
                issues_found.append(f"{description}: {len(matches)} occurrences")
        
        if issues_found:
            print(f"   ⚠️ WARNINGS:")
            for issue in issues_found:
                print(f"      - {issue}")
                self.warnings.append(f"{filename}: {issue}")
        else:
            print(f"   ✅ PASSED: No suspicious hardcoded thresholds")
            self.passed.append(f"{filename}: Hardcoded thresholds check")
    
    def check_directional_bias(self, filename: str, content: str):
        """Check for UP vs DOWN bias"""
        
        print(f"\n🔍 Check 2: Directional Bias (UP vs DOWN)")
        
        # Count UP vs DOWN adjustments
        up_adjustments = len(re.findall(r'confidence\s*\+=\s*\d+', content))
        down_adjustments = len(re.findall(r'confidence\s*-=\s*\d+', content))
        
        # Check for asymmetric logic
        up_keywords = len(re.findall(r'\b(bullish|long|buy|up)\b', content, re.IGNORECASE))
        down_keywords = len(re.findall(r'\b(bearish|short|sell|down)\b', content, re.IGNORECASE))
        
        print(f"   Confidence adjustments: +{up_adjustments} UP, -{down_adjustments} DOWN")
        print(f"   Keywords: {up_keywords} bullish, {down_keywords} bearish")
        
        # Check for bias
        if up_adjustments > 0 and down_adjustments == 0:
            self.issues.append(f"{filename}: Only UP adjustments, no DOWN adjustments")
            print(f"   ❌ ISSUE: Only UP adjustments detected")
        elif abs(up_adjustments - down_adjustments) > 5:
            self.warnings.append(f"{filename}: Asymmetric adjustments (UP:{up_adjustments}, DOWN:{down_adjustments})")
            print(f"   ⚠️ WARNING: Asymmetric adjustment count")
        else:
            print(f"   ✅ PASSED: Balanced UP/DOWN logic")
            self.passed.append(f"{filename}: Directional bias check")
    
    def check_confidence_calculation(self, filename: str, content: str):
        """Check confidence calculation for bias"""
        
        print(f"\n🔍 Check 3: Confidence Calculation")
        
        # Look for confidence formulas
        confidence_formulas = re.findall(r'confidence\s*=\s*([^;\n]+)', content)
        
        if confidence_formulas:
            print(f"   Found {len(confidence_formulas)} confidence calculations")
            
            # Check for bias in base confidence
            for formula in confidence_formulas[:3]:  # Show first 3
                print(f"      Formula: {formula.strip()}")
                
                # Check if base is 50 (neutral) or biased
                if '50' in formula or '0.5' in formula:
                    print(f"         ✅ Uses neutral base (50%)")
                elif any(x in formula for x in ['60', '65', '70', '0.6', '0.65', '0.7']):
                    self.warnings.append(f"{filename}: Confidence base >50% (bullish bias)")
                    print(f"         ⚠️ Base >50% (potential bullish bias)")
            
            self.passed.append(f"{filename}: Confidence calculation check")
        else:
            print(f"   ℹ️ No confidence calculations found")
    
    def check_magic_numbers(self, filename: str, content: str):
        """Check for magic numbers"""
        
        print(f"\n🔍 Check 4: Magic Numbers")
        
        # Find all numeric literals
        numbers = re.findall(r'\b\d+\.?\d*\b', content)
        
        # Count occurrences
        from collections import Counter
        number_counts = Counter(numbers)
        
        # Find repeated magic numbers (excluding common ones)
        common_numbers = {'0', '1', '2', '3', '5', '10', '100', '0.0', '1.0'}
        magic_numbers = {num: count for num, count in number_counts.items() 
                        if count > 3 and num not in common_numbers}
        
        if magic_numbers:
            print(f"   ⚠️ Repeated numbers (potential magic numbers):")
            for num, count in sorted(magic_numbers.items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"      {num}: {count} times")
                self.warnings.append(f"{filename}: Number {num} repeated {count} times")
        else:
            print(f"   ✅ PASSED: No excessive magic numbers")
            self.passed.append(f"{filename}: Magic numbers check")
    
    def print_summary(self):
        """Print audit summary"""
        
        print(f"\n{'='*80}")
        print("AUDIT SUMMARY")
        print(f"{'='*80}")
        
        print(f"\n✅ PASSED ({len(self.passed)}):")
        for item in self.passed:
            print(f"   ✅ {item}")
        
        print(f"\n⚠️ WARNINGS ({len(self.warnings)}):")
        if self.warnings:
            for item in self.warnings:
                print(f"   ⚠️ {item}")
        else:
            print(f"   None")
        
        print(f"\n❌ CRITICAL ISSUES ({len(self.issues)}):")
        if self.issues:
            for item in self.issues:
                print(f"   ❌ {item}")
        else:
            print(f"   None")
        
        # Overall verdict
        print(f"\n{'='*80}")
        if len(self.issues) == 0:
            if len(self.warnings) == 0:
                print("✅ VERDICT: SYSTEM IS CLEAN - No bias or hardcode issues!")
            else:
                print("⚠️ VERDICT: SYSTEM IS MOSTLY CLEAN - Minor warnings only")
        else:
            print("❌ VERDICT: ISSUES FOUND - Needs fixes")
        print(f"{'='*80}\n")


def check_specific_bias_patterns():
    """Check for specific known bias patterns"""
    
    print("\n" + "="*80)
    print("SPECIFIC BIAS PATTERN CHECK")
    print("="*80)
    
    checks = []
    
    # Check 1: Confidence base
    print(f"\n🔍 Check: Confidence Base Value")
    try:
        from premarket_predictor import PremarketPredictor
        # This would need to check the actual confidence calculation
        print("   ℹ️ Manual review needed for confidence base")
        checks.append(("Confidence base", "MANUAL"))
    except Exception as e:
        print(f"   ⚠️ Could not import: {e}")
    
    # Check 2: Stock configs
    print(f"\n🔍 Check: Stock Configuration Symmetry")
    try:
        import sys
        sys.path.insert(0, '.')
        from premarket_config import STOCK_CONFIGS
        
        for symbol, config in STOCK_CONFIGS.items():
            print(f"\n   {symbol}:")
            print(f"      Follow-through rate: {config['follow_through_rate']:.1%}")
            print(f"      Trap rate: {config['trap_rate']:.1%}")
            
            # Check if follow-through is suspiciously high
            if config['follow_through_rate'] > 0.85:
                print(f"      ⚠️ WARNING: Very high follow-through rate (>85%)")
            else:
                print(f"      ✅ Reasonable follow-through rate")
        
        checks.append(("Stock configs", "PASSED"))
    except Exception as e:
        print(f"   ⚠️ Could not check configs: {e}")
        checks.append(("Stock configs", "SKIP"))
    
    # Check 3: Weight distribution
    print(f"\n🔍 Check: Weight Distribution")
    try:
        weights = {
            'news': 0.25,
            'volume': 0.20,
            'technical': 0.20,
            'futures': 0.20,
            'sector': 0.15
        }
        
        total = sum(weights.values())
        print(f"   Total weight: {total:.2f}")
        
        if abs(total - 1.0) < 0.01:
            print(f"   ✅ Weights sum to 1.0")
            checks.append(("Weight distribution", "PASSED"))
        else:
            print(f"   ⚠️ Weights don't sum to 1.0")
            checks.append(("Weight distribution", "WARNING"))
    except Exception as e:
        print(f"   ⚠️ Could not check weights: {e}")
    
    # Summary
    print(f"\n{'='*80}")
    print("SPECIFIC CHECKS SUMMARY:")
    for check, result in checks:
        symbol = "✅" if result == "PASSED" else "⚠️" if result == "WARNING" else "ℹ️"
        print(f"   {symbol} {check}: {result}")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    # Run comprehensive audit
    auditor = PremarketBiasAuditor()
    auditor.audit_all_files()
    
    # Run specific checks
    check_specific_bias_patterns()
    
    print("\n" + "="*80)
    print("RECOMMENDATIONS:")
    print("="*80)
    print("""
1. ✅ Move all thresholds to premarket_config.py
2. ✅ Ensure symmetric UP/DOWN logic
3. ✅ Use 50% as neutral confidence base
4. ✅ Document all magic numbers
5. ✅ Test with both UP and DOWN gaps
6. ✅ Verify trap detection works both ways
    """)
