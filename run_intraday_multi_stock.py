#!/usr/bin/env python3
"""Intraday (Regular-Hours) Multi-Stock Prediction Runner

Adapts the proven ComprehensiveNextDayPredictor to intraday use and
applies decisive-style thresholds and position sizing similar to the
premarket system.

Usage (examples):
    python run_intraday_multi_stock.py --mode decisive
    python run_intraday_multi_stock.py --mode standard --stocks AMD NVDA AVGO
"""

import sys
from pathlib import Path
from datetime import datetime
import json

import pytz

# Ensure local project imports work when run as a script
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from comprehensive_nextday_predictor import ComprehensiveNextDayPredictor
from stock_config import get_active_stocks, get_stock_config

try:
    from market_intelligence_system import MarketIntelligenceSystem
    INTELLIGENCE_AVAILABLE = True
except Exception:
    MarketIntelligenceSystem = None
    INTELLIGENCE_AVAILABLE = False


def generate_intraday_signal(symbol: str, mode: str = "decisive") -> dict | None:
    """Generate an intraday trading signal for a single stock.

    This reuses ComprehensiveNextDayPredictor (which already includes
    intraday fixes like live price and intraday momentum) and then maps
    its direction + confidence into a decisive-style recommendation and
    position size.
    """

    predictor = ComprehensiveNextDayPredictor(symbol=symbol)
    base = predictor.generate_comprehensive_prediction()

    if not base:
        return None

    direction = base.get("direction", "NEUTRAL") or "NEUTRAL"
    confidence_pct = float(base.get("confidence", 0.0) or 0.0)
    confidence = confidence_pct / 100.0

    # Default recommendation
    recommendation = "SKIP"
    position_size = 0.0

    if direction != "NEUTRAL":
        # Decisive mode: more trades, scaled position size
        if mode == "decisive":
            if confidence >= 0.70:
                recommendation = "STRONG_TRADE"
                position_size = 1.0
            elif confidence >= 0.60:
                recommendation = "TRADE"
                position_size = 0.75
            elif confidence >= 0.50:
                recommendation = "CAUTIOUS"
                position_size = 0.50
            elif confidence >= 0.45:
                recommendation = "CAUTIOUS"
                position_size = 0.25
            else:
                recommendation = "SKIP"
                position_size = 0.0
        else:  # standard (stricter) mode
            if confidence >= 0.75:
                recommendation = "STRONG_TRADE"
                position_size = 1.0
            elif confidence >= 0.65:
                recommendation = "TRADE"
                position_size = 0.75
            elif confidence >= 0.55:
                recommendation = "CAUTIOUS"
                position_size = 0.50
            else:
                recommendation = "SKIP"
                position_size = 0.0

    stock_cfg = get_stock_config(symbol)

    sector_etf = stock_cfg.get("sector_etf", "XLK")
    if INTELLIGENCE_AVAILABLE and position_size > 0.0:
        try:
            intelligence = MarketIntelligenceSystem(symbol)
            intel_result = intelligence.apply_intelligence_to_prediction(
                base_confidence=confidence,
                base_sector_weight=stock_cfg.get("weight_adjustments", {}).get("sector", 0.06),
                base_position_size=position_size,
                stock_sector_etf=sector_etf,
            )
            position_size = float(intel_result.get("adjusted_position_size", position_size) or position_size)
        except Exception:
            pass

    return {
        "symbol": symbol,
        "name": stock_cfg.get("name", symbol),
        "direction": direction,
        "confidence": confidence_pct,
        "recommendation": recommendation,
        "position_size": position_size,
        "current_price": base.get("current_price"),
        "target_price": base.get("target_price"),
        "expected_move_percent": base.get("expected_move_percent"),
        "reason": base.get("reason"),
        "explanation": base.get("explanation"),
    }


def run_intraday_multi_stock(stocks: list[str] | None = None, mode: str = "decisive") -> dict:
    """Run intraday predictions for multiple stocks using decisive-style logic."""

    et_tz = pytz.timezone("US/Eastern")
    now_et = datetime.now(et_tz)

    print("\n" + "=" * 80)
    print(" INTRADAY REGULAR-HOURS PREDICTION SYSTEM")
    print("=" * 80)
    print(f" {now_et.strftime('%Y-%m-%d %I:%M %p ET')}")
    print(f" {now_et.strftime('%A')}")
    print(f" Mode: {mode.upper()}")
    print("=" * 80)

    if stocks is None:
        stocks = get_active_stocks()

    print(f"\n Predicting {len(stocks)} stocks: {', '.join(stocks)}")

    results: dict[str, dict] = {}

    for symbol in stocks:
        print("\n" + "-" * 80)
        print(f" INTRADAY ANALYSIS: {symbol}")
        print("-" * 80)

        try:
            signal = generate_intraday_signal(symbol, mode=mode)
        except Exception as e:  # noqa: BLE001
            print(f" Error generating intraday signal for {symbol}: {e}")
            signal = None

        if not signal:
            print(f" Skipping {symbol}: no signal")
            continue

        results[symbol] = signal

        direction = signal["direction"]
        conf = signal["confidence"]
        rec = signal["recommendation"]
        size = signal["position_size"]
        price = signal.get("current_price")
        target = signal.get("target_price")

        print(f"\n PREDICTION:")
        print(f"   Direction: {direction}")
        print(f"   Confidence: {conf:.1f}%")
        print(f"   Recommendation: {rec}")
        print(f"   Position Size: {size*100:.0f}%")
        if price is not None:
            print(f"   Current Price: ${price:.2f}")
        if target is not None:
            print(f"   Target Price:  ${target:.2f}")

        reason = signal.get("reason")
        if reason:
            print(f"\n Reason: {reason}")

    # Summary
    print("\n" + "=" * 80)
    print(" INTRADAY TRADING SUMMARY")
    print("=" * 80)

    trades = [s for s in results.values() if s.get("position_size", 0) > 0]

    if not trades:
        print("\n No intraday trades recommended under current mode.")
    else:
        print(f"\n 🎯 {len(trades)} INTRADAY OPPORTUNITIES:")
        for sig in trades:
            print(f"\n{sig['symbol']} ({sig.get('name', sig['symbol'])}):")
            print(f"   Direction: {sig['direction']}")
            print(f"   Confidence: {sig['confidence']:.1f}%")
            print(f"   Position: {sig['position_size']*100:.0f}%")
            cp = sig.get("current_price")
            tp = sig.get("target_price")
            if cp is not None:
                print(f"   Current: ${cp:.2f}")
            if tp is not None:
                print(f"   Target:  ${tp:.2f}")

    # Save results
    output_dir = PROJECT_ROOT / "data" / "intraday"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / f"intraday_predictions_{now_et.strftime('%Y%m%d_%H%M')}.json"

    with output_file.open("w", encoding="utf-8") as f:
        json.dump({
            "timestamp": now_et.isoformat(),
            "mode": mode,
            "predictions": results,
        }, f, indent=2)

    print(f"\n Saved to: {output_file}")
    print("\n" + "=" * 80)

    return results


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Intraday (regular-hours) multi-stock prediction")
    parser.add_argument("--stocks", nargs="+", help="Stock symbols to predict (default: all active)")
    parser.add_argument("--mode", choices=["standard", "decisive"], default="decisive",
                        help="Threshold mode: standard (stricter) or decisive (more trades, smaller size)")

    args = parser.parse_args()

    run_intraday_multi_stock(stocks=args.stocks, mode=args.mode)
