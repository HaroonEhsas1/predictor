#!/usr/bin/env python3
"""
Multi-Stock Prediction Runner
Generates predictions for all active stocks (AMD, AVGO, etc.)
"""

import sys
from pathlib import Path
from datetime import datetime
import pytz
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from comprehensive_nextday_predictor import ComprehensiveNextDayPredictor
from stock_config import get_active_stocks, get_stock_config

# Import filters and safeguards (optional)
try:
    from prediction_filters import PredictionFilters
    FILTERS_AVAILABLE = True
except:
    FILTERS_AVAILABLE = False

try:
    from contrarian_safeguard import safeguard
    SAFEGUARD_AVAILABLE = True
except:
    SAFEGUARD_AVAILABLE = False


def run_prediction_for_stock(symbol: str, apply_filters: bool = True, apply_safeguard: bool = False):
    """
    Run prediction for a single stock
    
    Args:
        symbol: Stock ticker (e.g., 'AMD', 'AVGO')
        apply_filters: Whether to apply prediction filters
        apply_safeguard: Whether to apply contrarian safeguard
        
    Returns:
        dict: Prediction results
    """
    try:
        print(f"\n{'='*80}")
        print(f" PREDICTING: {symbol}")
        print(f"{'='*80}")
        
        # Initialize predictor for this stock
        predictor = ComprehensiveNextDayPredictor(symbol=symbol)
        
        # Generate prediction
        prediction = predictor.generate_comprehensive_prediction()
        
        if prediction is None:
            print(f" Error predicting {symbol}: Unable to generate prediction due to missing data")
            return None
        
        if not prediction:
            print(f"\n Failed to generate prediction for {symbol}")
            return None
        
        # Apply filters if available and enabled
        if apply_filters and FILTERS_AVAILABLE:
            try:
                stock_config = get_stock_config(symbol)
                min_conf = stock_config.get('min_confidence_threshold', 0.55)
                print(f"\n DEBUG: Using min_confidence={min_conf} for {symbol}")
                
                filters = PredictionFilters(min_confidence=min_conf, enable_sentiment=False)
                
                filter_input = {
                    'direction': prediction['direction'],
                    'directional_bias': prediction['direction'],
                    'confidence': prediction['confidence'] / 100,
                    'confidence_score': prediction['confidence'] / 100,
                    'target_price': prediction['target_price'],
                    'current_price': prediction['current_price']
                }
                
                filtered = filters.apply_filters(filter_input)
                
                if not filtered:
                    print(f"\n {symbol} prediction filtered out (confidence too low)")
                    prediction['filtered'] = True
                    prediction['recommendation'] = 'HOLD'
                else:
                    prediction['filtered'] = False
                    prediction['direction'] = filtered['direction']
                    prediction['confidence'] = filtered['confidence'] * 100
                    
            except Exception as e:
                print(f"\n Filter error for {symbol}: {e}")
                prediction['filtered'] = False
        
        # Apply contrarian safeguard if enabled (NOT recommended)
        if apply_safeguard and SAFEGUARD_AVAILABLE:
            try:
                safeguard_input = {
                    'direction': prediction['direction'],
                    'confidence': prediction['confidence'] / 100,
                    'target_price': prediction['target_price']
                }
                
                safeguarded = safeguard.apply_safeguard(safeguard_input)
                
                if safeguarded and safeguarded.get('contrarian_flip'):
                    prediction['direction'] = safeguarded['direction']
                    prediction['contrarian_flip'] = True
                    prediction['flip_reason'] = safeguarded.get('reason', '')
                    print(f"\n Contrarian flip applied to {symbol}")
                    
            except Exception as e:
                print(f"\n Safeguard error for {symbol}: {e}")
        
        # Add symbol to prediction
        prediction['symbol'] = symbol
        
        return {
            'symbol': symbol,
            'direction': prediction.get('direction'),
            'confidence': prediction.get('confidence'),
            'target_price': prediction.get('target_price'),
            'expected_move_percent': prediction.get('expected_move_percent'),
            'current_price': prediction.get('current_price'),
            'explanation': prediction.get('explanation'),
            'recommendation': prediction.get('recommendation'),
            'status': prediction.get('status', 'PASSED'),
            'reason': prediction.get('reason', 'N/A')
        }
        
    except Exception as e:
        print(f"\n Error predicting {symbol}: {e}")
        import traceback
        traceback.print_exc()
        return None


def run_multi_stock_prediction(stocks: list = None, apply_filters: bool = True, apply_safeguard: bool = False):
    """
    Run predictions for multiple stocks
    
    Args:
        stocks: List of stock symbols (if None, uses all active stocks)
        apply_filters: Whether to apply prediction filters
        apply_safeguard: Whether to apply contrarian safeguard
        
    Returns:
        dict: Predictions for all stocks
    """
    et_tz = pytz.timezone('US/Eastern')
    now_et = datetime.now(et_tz)
    
    print("\n" + "="*80)
    print(" MULTI-STOCK PREDICTION ENGINE")
    print("="*80)
    print(f" {now_et.strftime('%Y-%m-%d %I:%M %p ET')}")
    print(f" {now_et.strftime('%A')}")
    print("="*80)
    
    # Get stocks to predict
    if stocks is None:
        stocks = get_active_stocks()
    
    print(f"\n Predicting {len(stocks)} stocks: {', '.join(stocks)}")
    print(f" Filters: {'ON' if apply_filters else 'OFF'}")
    print(f" Contrarian Safeguard: {'ON' if apply_safeguard else 'OFF (Recommended)'}")
    
    # Run predictions
    results = {}
    
    for symbol in stocks:
        prediction = run_prediction_for_stock(symbol, apply_filters, apply_safeguard)
        if prediction:
            results[symbol] = prediction
    
    # Summary
    print("\n" + "="*80)
    print(" PREDICTION SUMMARY")
    print("="*80)
    
    for symbol, pred in results.items():
        if pred and pred.get('direction'):
            print(f"\n{symbol}:")
            if pred.get('status') == 'FILTERED':
                print(f"   Status: FILTERED OUT (Hold)")
                print(f"   Reason: Confidence below threshold")
            else:
                print(f"   Direction: {pred['direction']}")
                print(f"   Confidence: {pred['confidence']:.1f}%")
                print(f"   Today's Close: ${pred['current_price']:.2f}")
                print(f"   Target (Tomorrow): ${pred['target_price']:.2f}")
                expected_move = pred.get('expected_move_percent', 0.0) if pred.get('expected_move_percent') is not None else ((pred['target_price'] - pred['current_price']) / pred['current_price'] * 100 if pred['current_price'] > 0 else 0.0)
                print(f"   Expected Move: {expected_move:.2f}%")
                
                if pred.get('contrarian_flip'):
                    print(f"   Contrarian Flip: YES")
    
    print("\n" + "="*80)
    
    # OCT 24 FIX: Check for universal bias (all stocks agreeing with high confidence)
    non_filtered_predictions = [p for p in results.values() if not p.get('filtered', False)]
    
    if len(non_filtered_predictions) >= 3:
        directions = [p['direction'] for p in non_filtered_predictions]
        confidences = [p['confidence'] for p in non_filtered_predictions]
        
        # Check if all stocks have same direction
        all_same_direction = len(set(directions)) == 1 and directions[0] != 'NEUTRAL'
        
        # Check if all have high confidence (>85%)
        all_high_confidence = all(c > 85 for c in confidences)
        
        if all_same_direction and all_high_confidence:
            avg_confidence = sum(confidences) / len(confidences)
            print("\n" + "!"*80)
            print(" CORRELATION ALERT: UNIVERSAL BIAS DETECTED")
            print("!"*80)
            print(f"\n All {len(non_filtered_predictions)} stocks predicting {directions[0]} at {avg_confidence:.1f}% average confidence")
            print(f"\n POSSIBLE CAUSES:")
            print(f"   • Strong market trend (SPY/QQQ) overwhelming stock-specific signals")
            print(f"   • Universal factors (futures, VIX, gaps) drowning out fundamentals")
            print(f"   • Genuine market-wide move (all stocks moving together)")
            print(f"\n RECOMMENDATION:")
            print(f"   • Check if stock-specific signals (technical, institutional) are weak")
            print(f"   • Consider reducing position sizes (unusual agreement)")
            print(f"   • Verify each stock has unique reasoning (not just 'market up')")
            print(f"   • Look for the strongest signal (highest confidence may be most reliable)")
            print(f"\n When all stocks agree, diversification benefit is REDUCED.")
            print("!"*80 + "\n")
        elif all_same_direction:
            print(f"\n Note: All stocks predicting {directions[0]} (avg confidence: {sum(confidences)/len(confidences):.1f}%)")
            print(f"   This may indicate a strong market trend.")
    
    # Save results
    output_dir = Path(__file__).parent / "data" / "multi_stock"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / f"predictions_{now_et.strftime('%Y%m%d_%H%M')}.json"
    
    with open(output_file, 'w') as f:
        json.dump({
            'timestamp': now_et.isoformat(),
            'predictions': results
        }, f, indent=2)
    
    print(f"\n Saved to: {output_file}")
    
    return results


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Multi-Stock Prediction Engine')
    parser.add_argument('--stocks', nargs='+', help='Stock symbols to predict (default: all active)')
    parser.add_argument('--no-filters', action='store_true', help='Disable prediction filters')
    parser.add_argument('--safeguard', action='store_true', help='Enable contrarian safeguard (not recommended)')
    
    args = parser.parse_args()
    
    # Run predictions
    run_multi_stock_prediction(
        stocks=args.stocks,
        apply_filters=not args.no_filters,
        apply_safeguard=args.safeguard
    )
