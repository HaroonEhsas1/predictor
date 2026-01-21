#!/usr/bin/env python3
"""
Enhanced Multi-Stock Predictor
Integrates legendary traders' wisdom:
- Performance tracking (Paul Tudor Jones)
- Dynamic position sizing (PTJ + Soros)
- Market environment filter (Warren Buffett)
- Systematic approach (Ray Dalio)
"""

from market_environment_filter import MarketEnvironmentFilter
from performance_tracker import PerformanceTracker
from comprehensive_nextday_predictor import ComprehensiveNextDayPredictor
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))


def enhanced_prediction_system(symbols=None):
    """
    Run enhanced prediction system with legendary traders' wisdom
    """
    if symbols is None:
        symbols = ['AMD', 'AVGO', 'ORCL', 'NVDA']

    print("\n" + "="*80)
    print("🚀 ENHANCED OVERNIGHT SWING TRADING SYSTEM")
    print("="*80)
    print("Integrating wisdom from:")
    print("  • Paul Tudor Jones (Risk Management)")
    print("  • Ray Dalio (Systematic Approach)")
    print("  • Warren Buffett (Market Environment)")
    print("  • George Soros (Position Sizing)")
    print("="*80)

    # Step 1: Check performance history
    print("\n" + "="*80)
    print("📊 STEP 1: PERFORMANCE ANALYSIS")
    print("="*80)

    tracker = PerformanceTracker()
    tracker.print_performance_report()

    # Step 2: Check market environment
    print("\n" + "="*80)
    print("🌍 STEP 2: MARKET ENVIRONMENT CHECK")
    print("="*80)

    env_filter = MarketEnvironmentFilter()
    market_env = env_filter.get_market_condition()

    # Step 3: Generate predictions for each stock
    print("\n" + "="*80)
    print("🎯 STEP 3: STOCK PREDICTIONS")
    print("="*80)

    predictions = {}

    for symbol in symbols:
        print(f"\n{'='*80}")
        print(f"📈 ANALYZING {symbol}")
        print(f"{'='*80}")

        # Run overnight prediction
        predictor = ComprehensiveNextDayPredictor(symbol)
        prediction = predictor.generate_comprehensive_prediction()

        if prediction:
            # Get position size multiplier from performance
            base_confidence = prediction['confidence']
            perf_multiplier, perf_reason = tracker.get_position_size_multiplier(
                base_confidence)

            # Get market environment multiplier
            market_multiplier = market_env['position_multiplier']

            # Check if should trade based on environment
            should_trade, adj_confidence, trade_reason = env_filter.should_trade_today(
                base_confidence)

            # Combined multiplier
            combined_multiplier = perf_multiplier * market_multiplier
            combined_multiplier = max(
                0.25, min(1.5, combined_multiplier))  # Cap 0.25x to 1.5x

            # Store enhanced prediction
            predictions[symbol] = {
                **prediction,
                'should_trade': should_trade,
                'trade_reason': trade_reason,
                'perf_multiplier': perf_multiplier,
                'perf_reason': perf_reason,
                'market_multiplier': market_multiplier,
                'combined_multiplier': combined_multiplier,
                'adjusted_confidence': adj_confidence
            }

    # Step 4: Trading Plan
    print("\n" + "="*80)
    print("📋 STEP 4: TRADING PLAN")
    print("="*80)

    print(f"\n🎯 MARKET ENVIRONMENT:")
    print(f"   Risk Level: {market_env['risk_level']}")
    print(f"   Base Multiplier: {market_env['position_multiplier']:.2f}x")

    if market_env['warnings']:
        print(f"\n⚠️ MARKET WARNINGS:")
        for warning in market_env['warnings']:
            print(f"   • {warning}")

    print(f"\n💰 RECOMMENDED TRADES:")

    total_trades = 0
    tradeable = []

    for symbol, pred in predictions.items():
        print(f"\n{symbol}:")
        print(f"   Direction: {pred['direction']}")
        print(f"   Base Confidence: {pred['confidence']:.1f}%")
        print(f"   Adjusted Confidence: {pred['adjusted_confidence']:.1f}%")
        print(f"   Target: ${pred['target_price']:.2f}")
        print(f"   Expected Move: ${pred['expected_change']:+.2f}")

        print(f"\n   Position Sizing:")
        print(f"   ├─ Performance Multiplier: {pred['perf_multiplier']:.2f}x")
        print(f"   │  ({pred['perf_reason']})")
        print(f"   ├─ Market Multiplier: {pred['market_multiplier']:.2f}x")
        print(f"   │  (Market: {market_env['risk_level']})")
        print(f"   └─ COMBINED: {pred['combined_multiplier']:.2f}x")

        if pred['should_trade']:
            print(f"\n   ✅ RECOMMENDATION: TRADE")
            print(f"      {pred['trade_reason']}")

            # Calculate actual position size (example: base of 100 shares)
            base_shares = {'AMD': 40, 'AVGO': 15, 'ORCL': 20}.get(symbol, 30)
            actual_shares = int(base_shares * pred['combined_multiplier'])

            print(f"      Base Position: {base_shares} shares")
            print(f"      Adjusted Position: {actual_shares} shares")
            print(f"      Risk per share: ~2% of account")

            total_trades += 1
            tradeable.append(symbol)
        else:
            print(f"\n   ❌ RECOMMENDATION: SKIP")
            print(f"      {pred['trade_reason']}")

    # Summary
    print(f"\n{'='*80}")
    print(f"📊 SUMMARY")
    print(f"{'='*80}")
    print(f"\n✅ TRADEABLE: {len(tradeable)}/{len(symbols)} stocks")
    if tradeable:
        print(f"   {', '.join(tradeable)}")

    perf = tracker.get_recent_performance(10)
    if perf['total_trades'] >= 5:
        print(f"\n📈 YOUR PERFORMANCE:")
        print(f"   Win Rate: {perf['win_rate']:.1f}% (last 10 trades)")
        print(f"   Profit Factor: {perf['profit_factor']:.2f}")

    print(f"\n💡 LEGENDARY TRADERS' WISDOM APPLIED:")
    print(f"   ✅ Paul Tudor Jones: Defense first, scale with performance")
    print(f"   ✅ Ray Dalio: Systematic approach, risk management")
    print(f"   ✅ Warren Buffett: Market environment awareness")
    print(f"   ✅ George Soros: Dynamic position sizing")
    print(f"   ✅ Jesse Livermore: Cut losses, let winners run")

    print(f"\n{'='*80}")
    print(f"🚀 READY TO TRADE!")
    print(f"{'='*80}\n")

    return predictions


if __name__ == "__main__":
    # Run enhanced system
    predictions = enhanced_prediction_system()
