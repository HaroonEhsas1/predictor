"""
TEST PREMARKET DATA FETCHING
Verifies that the system correctly fetches premarket-specific data
"""

import yfinance as yf
from datetime import datetime
import pytz

def test_premarket_data_sources(symbol: str):
    """
    Test all data sources for premarket information
    """
    
    print(f"\n{'='*80}")
    print(f"TESTING PREMARKET DATA SOURCES - {symbol}")
    print(f"{'='*80}")
    
    stock = yf.Ticker(symbol)
    info = stock.info
    hist = stock.history(period='5d')
    
    # Get time
    et_tz = pytz.timezone('US/Eastern')
    now_et = datetime.now(et_tz)
    is_premarket = 4 <= now_et.hour < 9 or (now_et.hour == 9 and now_et.minute < 30)
    
    print(f"\n🕒 Current Time: {now_et.strftime('%I:%M %p ET')}")
    print(f"📊 Premarket Hours: {'✅ YES' if is_premarket else '❌ NO (outside 4-9:30 AM ET)'}")
    
    # Test all data sources
    print(f"\n📊 DATA SOURCES AVAILABLE:")
    
    prev_close = hist['Close'].iloc[-1] if len(hist) > 0 else None
    print(f"\n1. Previous Close: ${prev_close:.2f}" if prev_close else "   ❌ Not available")
    
    premarket_price = info.get('preMarketPrice', None)
    if premarket_price:
        print(f"2. preMarketPrice: ${premarket_price:.2f} ✅ PREMARKET DATA")
        gap = ((premarket_price - prev_close) / prev_close) * 100 if prev_close else 0
        print(f"   Gap: {gap:+.2f}%")
    else:
        print(f"2. preMarketPrice: ❌ Not available")
    
    premarket_volume = info.get('preMarketVolume', 0)
    if premarket_volume > 0:
        print(f"3. preMarketVolume: {premarket_volume:,} ✅ PREMARKET VOLUME")
    else:
        print(f"3. preMarketVolume: ❌ Not available or 0")
    
    current_price = info.get('currentPrice', None)
    if current_price:
        print(f"4. currentPrice: ${current_price:.2f}")
    else:
        print(f"4. currentPrice: ❌ Not available")
    
    regular_price = info.get('regularMarketPrice', None)
    if regular_price:
        print(f"5. regularMarketPrice: ${regular_price:.2f}")
    else:
        print(f"5. regularMarketPrice: ❌ Not available")
    
    # Determine best data source
    print(f"\n🎯 BEST DATA SOURCE:")
    if premarket_price:
        print(f"   ✅ Using preMarketPrice: ${premarket_price:.2f}")
        print(f"   ✅ This is PREMARKET-SPECIFIC data")
        data_quality = "EXCELLENT"
    elif current_price and is_premarket:
        print(f"   ⚠️ Using currentPrice: ${current_price:.2f}")
        print(f"   ⚠️ Estimated premarket (no explicit preMarketPrice)")
        data_quality = "GOOD"
    elif regular_price:
        print(f"   ⚠️ Using regularMarketPrice: ${regular_price:.2f}")
        print(f"   ⚠️ May not reflect premarket movement")
        data_quality = "FAIR"
    else:
        print(f"   ❌ No price data available")
        data_quality = "POOR"
    
    print(f"\n📊 DATA QUALITY: {data_quality}")
    
    # Additional premarket info
    print(f"\n📋 ADDITIONAL INFO:")
    premarket_change = info.get('preMarketChange', None)
    if premarket_change:
        print(f"   preMarketChange: ${premarket_change:+.2f}")
    
    premarket_change_pct = info.get('preMarketChangePercent', None)
    if premarket_change_pct:
        print(f"   preMarketChangePercent: {premarket_change_pct:+.2f}%")
    
    premarket_time = info.get('preMarketTime', None)
    if premarket_time:
        pm_time = datetime.fromtimestamp(premarket_time)
        print(f"   preMarketTime: {pm_time.strftime('%I:%M %p')}")
    
    return {
        'has_premarket_price': premarket_price is not None,
        'has_premarket_volume': premarket_volume > 0,
        'data_quality': data_quality,
        'is_premarket_hours': is_premarket
    }


def test_system_integration():
    """
    Test the actual system's premarket data fetching
    """
    
    print(f"\n{'='*80}")
    print(f"TESTING SYSTEM INTEGRATION")
    print(f"{'='*80}")
    
    from premarket_predictor import PremarketPredictor
    
    for symbol in ['NVDA', 'META']:
        print(f"\n{'-'*80}")
        predictor = PremarketPredictor(symbol)
        data = predictor.get_premarket_data()
        
        if data.get('has_data'):
            print(f"\n✅ System successfully fetched premarket data")
            print(f"   Data Source: {data.get('data_source', 'UNKNOWN')}")
            print(f"   Gap: {data['gap_pct']:+.2f}%")
            print(f"   Volume: {data['premarket_volume']:,}")
        else:
            print(f"\n❌ System failed to fetch data")
            print(f"   Error: {data.get('error')}")


if __name__ == "__main__":
    print("\n" + "="*80)
    print("PREMARKET DATA FETCHING TEST")
    print("="*80)
    
    # Test raw data sources
    for symbol in ['NVDA', 'META']:
        result = test_premarket_data_sources(symbol)
        print(f"\n{'='*80}\n")
    
    # Test system integration
    test_system_integration()
    
    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80)
    print("""
INTERPRETATION:
- If preMarketPrice is available: ✅ EXCELLENT - Real premarket data
- If currentPrice during premarket hours: ⚠️ GOOD - Estimated
- If regularMarketPrice only: ⚠️ FAIR - May be stale
- If no data: ❌ POOR - System cannot predict

BEST TIME TO RUN: 9:15 AM ET (15 minutes before open)
    """)
