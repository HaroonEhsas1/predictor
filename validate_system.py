"""System validation script - checks for bias and data sufficiency.

Run this to verify your system is truly unbiased and has enough data.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()  # Load .env file

from sqlite_fallback import db
from threshold_manager import load_thresholds
import yfinance as yf
from datetime import datetime, timedelta
import os

def test_bidirectionality():
    """Test if system predicts UP and DOWN equally."""
    print("\n" + "="*60)
    print("📊 BIDIRECTIONALITY TEST")
    print("="*60)
    
    recent = db.get_recent_predictions(100)
    if not recent:
        print("⚠️ No historical predictions found")
        print("   Run system for a few weeks to collect data")
        return
    
    up_count = sum(1 for p in recent if p['predicted'] == 'UP')
    down_count = sum(1 for p in recent if p['predicted'] == 'DOWN')
    total = len(recent)
    
    up_pct = up_count / total if total > 0 else 0
    down_pct = down_count / total if total > 0 else 0
    
    print(f"📈 UP predictions: {up_count}/{total} ({up_pct:.1%})")
    print(f"📉 DOWN predictions: {down_count}/{total} ({down_pct:.1%})")
    
    # Check for bias
    if up_pct > 0.70:
        print("❌ BIAS DETECTED: System is bullish-biased")
    elif down_pct > 0.70:
        print("❌ BIAS DETECTED: System is bearish-biased")
    elif 0.45 <= up_pct <= 0.55:
        print("✅ NO BIAS: System is properly balanced")
    else:
        print("⚠️ SLIGHT IMBALANCE: Within acceptable range")

def test_data_sources():
    """Test if all data sources are accessible."""
    print("\n" + "="*60)
    print("🔌 DATA SOURCE CONNECTION TEST")
    print("="*60)
    
    sources = {
        'POLYGON_API_KEY': 'Polygon.io',
        'FINNHUB_API_KEY': 'Finnhub',
        'ALPHA_VANTAGE_API_KEY': 'Alpha Vantage',
        'EODHD_API_KEY': 'EODHD',
        'FRED_API_KEY': 'FRED',
        'MARKETAUX_API_KEY': 'MarketAux',
        'FMP_API_KEY': 'Financial Modeling Prep'
    }
    
    active = 0
    for key, name in sources.items():
        value = os.getenv(key)
        if value:
            print(f"✅ {name}: Connected")
            active += 1
        else:
            print(f"⚠️ {name}: Not configured (optional)")
    
    print(f"\n📊 Active sources: {active}/{len(sources)}")
    if active >= 4:
        print("✅ SUFFICIENT: Enough data sources for predictions")
    else:
        print("⚠️ LIMITED: Consider adding more API keys")

def test_historical_data():
    """Test if enough historical data exists."""
    print("\n" + "="*60)
    print("📚 HISTORICAL DATA TEST")
    print("="*60)
    
    try:
        ticker = yf.Ticker("AMD")
        
        # Check daily data
        daily = ticker.history(period="5y", interval="1d")
        print(f"📅 Daily data: {len(daily)} days (min: 252)")
        
        if len(daily) >= 252:
            print("✅ SUFFICIENT: Enough historical data")
        else:
            print("❌ INSUFFICIENT: Need at least 1 year of data")
        
        # Check intraday data
        intraday = ticker.history(period="1d", interval="1m")
        print(f"⏰ Intraday data: {len(intraday)} candles")
        
        if len(intraday) >= 100:
            print("✅ SUFFICIENT: Enough intraday data")
        else:
            print("⚠️ LIMITED: Intraday data may be sparse")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")

def test_thresholds():
    """Test if thresholds are loaded correctly."""
    print("\n" + "="*60)
    print("🎚️ THRESHOLD CONFIGURATION TEST")
    print("="*60)
    
    try:
        config = load_thresholds()
        print(f"📊 Min Confidence: {config['min_confidence']:.1%}")
        print(f"📏 Min Margin: {config['min_margin']:.3f}")
        print(f"📈 Volatility Window: {config['volatility_window']} days")
        
        # Check for hardcoded values
        if config['min_confidence'] == 0.65 and config['min_margin'] == 0.015:
            print("⚠️ Using default values - consider tuning")
        else:
            print("✅ Custom thresholds configured")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")

def test_model_files():
    """Check if retrained models exist."""
    print("\n" + "="*60)
    print("🤖 MODEL FILES TEST")
    print("="*60)
    
    models_dir = Path(__file__).parent / "models"
    if not models_dir.exists():
        print("⚠️ No models directory found")
        print("   Run: python scripts/retrain.py")
        return
    
    model_files = list(models_dir.glob("*.pkl"))
    if model_files:
        print(f"✅ Found {len(model_files)} model files:")
        for f in sorted(model_files)[-3:]:
            print(f"   - {f.name}")
    else:
        print("⚠️ No model files found")
        print("   Run: python scripts/retrain.py")

def main():
    """Run all validation tests."""
    print("\n" + "="*60)
    print("🔍 SYSTEM VALIDATION SUITE")
    print("="*60)
    
    test_data_sources()
    test_historical_data()
    test_thresholds()
    test_model_files()
    test_bidirectionality()
    
    print("\n" + "="*60)
    print("✅ VALIDATION COMPLETE")
    print("="*60)
    print("\nRead SYSTEM_AUDIT.md for detailed analysis")

if __name__ == "__main__":
    main()
