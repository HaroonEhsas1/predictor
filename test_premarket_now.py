"""
TEST PREMARKET PREDICTIONS WITH SAMPLE DATA
Run this to see how the system makes predictions
"""

from stock_specific_predictors import get_predictor

def test_all_stocks():
    """Test all 6 stocks with sample premarket data"""
    
    print("\n" + "="*80)
    print("PREMARKET PREDICTION TEST - SAMPLE DATA")
    print("="*80)
    print("\nTesting with realistic premarket scenarios:\n")
    
    # Test scenarios for each stock
    scenarios = {
        'AMD': {
            'gap_pct': 2.3,
            'volume': 2500000,
            'min_volume': 1000000,
            'reddit_sentiment': 0.05,
            'unusual_options_activity': True,
            'scenario': 'Strong gap up with options activity'
        },
        'NVDA': {
            'gap_pct': 1.8,
            'volume': 6000000,
            'min_volume': 300000,
            'nasdaq_pct': 1.2,
            'smh_pct': 1.5,
            'ai_news': True,
            'scenario': 'Gap up with NASDAQ/SMH confirmation + AI news'
        },
        'META': {
            'gap_pct': -1.2,
            'volume': 1500000,
            'min_volume': 200000,
            'regulatory_news': True,
            'scenario': 'Gap down with regulatory news'
        },
        'AVGO': {
            'gap_pct': 2.5,
            'volume': 250000,
            'min_volume': 150000,
            'smh_pct': 2.0,
            'institutional_buying': True,
            'scenario': 'Strong gap up with sector and institutional support'
        },
        'SNOW': {
            'gap_pct': 3.2,
            'volume': 7000000,
            'min_volume': 5200000,
            'cloud_sector_pct': 2.5,
            'revenue_growth_news': True,
            'scenario': 'Big gap up with cloud sector strength + revenue news'
        },
        'PLTR': {
            'gap_pct': 4.5,
            'volume': 80000000,
            'min_volume': 45000000,
            'reddit_sentiment': 0.28,
            'government_contract_news': False,
            'scenario': 'Huge gap up but extreme Reddit hype, no catalyst'
        }
    }
    
    results = []
    
    for symbol, data in scenarios.items():
        print("="*80)
        print(f"📊 {symbol} PREDICTION")
        print("="*80)
        
        scenario = data.pop('scenario')
        print(f"\n📋 Scenario: {scenario}")
        print(f"   Gap: {data['gap_pct']:+.1f}%")
        print(f"   Volume: {data['volume']:,}")
        
        # Get predictor
        predictor = get_predictor(symbol)
        
        # Make prediction
        result = predictor.predict(data)
        
        # Display results
        direction = result.get('direction', 'NEUTRAL')
        confidence = result.get('confidence', 0) * 100
        
        print(f"\n🎯 PREDICTION:")
        print(f"   Direction: {direction}")
        print(f"   Confidence: {confidence:.0f}%")
        
        if 'reason' in result:
            print(f"   Reason: {result['reason']}")
        
        if 'warning' in result:
            print(f"   ⚠️ Warning: {result['warning']}")
        
        # Trading recommendation
        if confidence >= 75:
            rec = "🟢🟢 STRONG BUY/SELL"
            position = "100%"
        elif confidence >= 65:
            rec = "🟢 TRADE"
            position = "75%"
        elif confidence >= 55:
            rec = "🟡 CAUTIOUS"
            position = "50%"
        else:
            rec = "⚪ SKIP"
            position = "0%"
        
        print(f"\n   Recommendation: {rec}")
        print(f"   Position Size: {position}")
        
        results.append({
            'symbol': symbol,
            'direction': direction,
            'confidence': confidence,
            'rec': rec,
            'scenario': scenario
        })
        
        print()
    
    # Summary
    print("="*80)
    print("📊 TRADING SUMMARY")
    print("="*80)
    
    trades = [r for r in results if r['confidence'] >= 55]
    
    if trades:
        print(f"\n🎯 {len(trades)} TRADING OPPORTUNITIES:")
        for t in trades:
            print(f"\n   {t['symbol']}: {t['direction']} {t['confidence']:.0f}%")
            print(f"   {t['rec']}")
            print(f"   Scenario: {t['scenario']}")
    else:
        print("\n⚪ NO TRADES RECOMMENDED")
        print("   All signals below minimum confidence threshold")
    
    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80)
    print("\nThis demonstrates how the system evaluates premarket data")
    print("At 9:15 AM, use REAL premarket data for actual trading signals!")
    print()


if __name__ == "__main__":
    test_all_stocks()
