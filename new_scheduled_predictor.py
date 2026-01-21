#!/usr/bin/env python3
"""
New Scheduled Prediction Runner
Uses comprehensive predictor (no TensorFlow) with filters and safeguards
Runs at 4 PM ET on weekdays
"""

import time
from datetime import datetime, timedelta
import pytz
from pathlib import Path
import sys
import os

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import our new comprehensive predictor
from comprehensive_nextday_predictor import ComprehensiveNextDayPredictor

# Import stock configuration
try:
    from stock_config import get_active_stocks, get_stock_config
    MULTI_STOCK_MODE = True
except:
    MULTI_STOCK_MODE = False
    print("⚠️ Stock config not found, using single-stock mode (AMD)")

# Import filters and safeguards
try:
    from prediction_filters import PredictionFilters
    FILTERS_AVAILABLE = True
except:
    FILTERS_AVAILABLE = False
    print("Warning: PredictionFilters not available")

try:
    from contrarian_safeguard import safeguard
    SAFEGUARD_AVAILABLE = True
except:
    SAFEGUARD_AVAILABLE = False
    print("Warning: Contrarian safeguard not available")

def is_trading_day():
    """Check if today is a trading day (Mon-Fri)."""
    et_tz = pytz.timezone('US/Eastern')
    now_et = datetime.now(et_tz)
    return 0 <= now_et.weekday() <= 4  # Mon=0, Fri=4

def is_market_close_time():
    """Check if it's 3:50-4:00 PM ET on a trading day (10 min before close)."""
    et_tz = pytz.timezone('US/Eastern')
    now_et = datetime.now(et_tz)
    
    is_weekday = is_trading_day()
    # 3:50 PM = 15 hours + 50/60 minutes = 15.833 hours
    # 4:00 PM = 16 hours
    current_time = now_et.hour + now_et.minute / 60.0
    is_close_window = 15.833 <= current_time < 16.0  # 3:50-4:00 PM (10 min window)
    
    return is_weekday and is_close_window

def run_scheduled_prediction():
    """Run prediction if it's the right time and hasn't run yet today."""
    log_file = Path(__file__).parent / "data" / "last_prediction_date.txt"
    log_file.parent.mkdir(exist_ok=True)
    
    # Check if already ran today
    today = datetime.now().date().isoformat()
    if log_file.exists():
        with open(log_file, 'r') as f:
            last_run = f.read().strip()
            if last_run == today:
                print(f"Already ran prediction today ({today})")
                return  # Already ran today
    
    et_tz = pytz.timezone('US/Eastern')
    now_et = datetime.now(et_tz)
    
    print("\n" + "="*80)
    print("SCHEDULED PREDICTION TRIGGERED")
    print("="*80)
    print(f"Time: {now_et.strftime('%Y-%m-%d %I:%M %p ET')}")
    print(f"Day: {now_et.strftime('%A')}")
    print("="*80)
    
    # Get stocks to predict
    if MULTI_STOCK_MODE:
        stocks_to_predict = get_active_stocks()
        print(f"\n📊 Multi-Stock Mode: Predicting {', '.join(stocks_to_predict)}")
    else:
        stocks_to_predict = ['AMD']
        print(f"\n📊 Single-Stock Mode: Predicting AMD")
    
    all_predictions = {}
    
    for symbol in stocks_to_predict:
        try:
            print(f"\n\n{'='*80}")
            print(f"🎯 PREDICTING: {symbol}")
            print(f"{'='*80}")
            
            # Initialize comprehensive predictor
            predictor = ComprehensiveNextDayPredictor(symbol=symbol)
        
            # Generate comprehensive prediction
            prediction = predictor.generate_comprehensive_prediction()
        
            if not prediction:
                print(f"\n❌ Failed to generate prediction for {symbol}")
                continue
            
            # Apply filters if available
            if FILTERS_AVAILABLE:
                try:
                    # Get stock-specific min confidence
                    if MULTI_STOCK_MODE:
                        stock_config = get_stock_config(symbol)
                        min_conf = stock_config.get('min_confidence_threshold', 0.60)
                    else:
                        min_conf = 0.60
                    
                    filters = PredictionFilters(min_confidence=min_conf, enable_sentiment=False)
                    
                    # Convert to expected format
                    filter_input = {
                        'direction': prediction['direction'],
                        'directional_bias': prediction['direction'],
                        'confidence': prediction['confidence'] / 100,  # Convert to 0-1
                        'confidence_score': prediction['confidence'] / 100,
                        'target_price': prediction['target_price'],
                        'current_price': prediction['current_price']
                    }
                    
                    filtered = filters.apply_filters(filter_input)
                    
                    if not filtered:
                        print(f"\n" + "="*80)
                        print(f"{symbol} PREDICTION FILTERED OUT")
                        print("="*80)
                        print("Reason: Did not meet confidence/volatility thresholds")
                        print("Recommendation: HOLD - Wait for clearer signals")
                        print("="*80)
                        all_predictions[symbol] = {'filtered': True, 'direction': 'HOLD'}
                        continue
                    
                    # Update prediction with filtered results
                    prediction['direction'] = filtered['direction']
                    prediction['confidence'] = filtered['confidence'] * 100  # Convert back
                    
                    print("\nFilters applied - prediction passed all gates")
                    
                except Exception as e:
                    print(f"\nWarning: Filter error for {symbol}: {e}")
                    print("Continuing with unfiltered prediction...")
            
            # Apply contrarian safeguard if available (disabled by default)
            # NOTE: Contrarian safeguard flips predictions - not recommended for overnight predictions
            if False and SAFEGUARD_AVAILABLE:  # Disabled
                try:
                    # Convert to expected format
                    safeguard_input = {
                        'direction': prediction['direction'],
                        'confidence': prediction['confidence'] / 100,
                        'target_price': prediction['target_price']
                    }
                    
                    safeguarded = safeguard.apply_safeguard(safeguard_input)
                    
                    if safeguarded:
                        prediction['direction'] = safeguarded['direction']
                        if safeguarded.get('contrarian_flip'):
                            prediction['contrarian_flip'] = True
                            prediction['flip_reason'] = safeguarded.get('reason', '')
                            print(f"\nContrarian flip applied: {prediction['flip_reason']}")
                        
                        # Log prediction
                        safeguard.log_prediction(prediction['direction'])
                    
                except Exception as e:
                    print(f"\nWarning: Safeguard error for {symbol}: {e}")
                    print("Continuing without safeguard...")
            
            # Add symbol to prediction
            prediction['symbol'] = symbol
            all_predictions[symbol] = prediction
            
            # Determine next trading day (BEFORE using it)
            next_day = now_et + timedelta(days=1)
            while next_day.weekday() > 4:  # Skip weekends
                next_day += timedelta(days=1)
            
            # Display final prediction
            print("\n" + "="*80)
            print(f"📊 {symbol} PREDICTION FOR NEXT TRADING DAY ({next_day.strftime('%A, %B %d')})")
            print("="*80)
            
            print(f"\nFor: {next_day.strftime('%A, %B %d, %Y')}")
            print(f"\nDirection: {prediction['direction']}")
            print(f"Confidence: {prediction['confidence']:.1f}%")
            print(f"Current Price: ${prediction['current_price']:.2f}")
            print(f"Target Price: ${prediction['target_price']:.2f}")
            print(f"Expected Move: ${prediction['expected_change']:+.2f} ({(prediction['expected_change']/prediction['current_price']*100):+.2f}%)")
            print(f"Total Score: {prediction['total_score']:+.3f}")
            
            if prediction.get('contrarian_flip'):
                print(f"\nContrarian Flip: YES")
                print(f"Reason: {prediction.get('flip_reason', 'Unknown')}")
            
            # Trading recommendation
            print(f"\n" + "-"*80)
            print("TRADING RECOMMENDATION:")
            
            if prediction['confidence'] >= 75:
                print(f"  HIGH CONFIDENCE - Strong {prediction['direction']} signal")
                if prediction['direction'] == "UP":
                    print(f"  Consider LONG position")
                    print(f"  Entry: ${prediction['current_price']:.2f}")
                    print(f"  Target: ${prediction['target_price']:.2f}")
                    print(f"  Stop Loss: ${prediction['current_price'] * 0.98:.2f} (-2%)")
                elif prediction['direction'] == "DOWN":
                    print(f"  Consider staying out or SHORT position")
                    print(f"  Target: ${prediction['target_price']:.2f}")
            elif prediction['confidence'] >= 60:
                print(f"  MODERATE CONFIDENCE - Proceed with caution")
                print(f"  Consider smaller position size (50% normal)")
            else:
                print(f"  LOW CONFIDENCE - Stay on sidelines")
                print(f"  Wait for clearer signals")
            
            print("="*80)
            
            # Save prediction to file
            output_file = Path(__file__).parent / "data" / "nextday" / "latest_prediction.json"
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            import json
            with open(output_file, 'w') as f:
                json.dump({
                    'timestamp': now_et.isoformat(),
                    'target_date': next_day.strftime('%Y-%m-%d'),
                    'prediction': prediction
                }, f, indent=2)
            
            print(f"\nPrediction saved to: {output_file}")
            
            print(f"\n{symbol} prediction completed successfully at {now_et.strftime('%I:%M %p ET')}")
            
        except Exception as e:
            print(f"\n" + "="*80)
            print(f"ERROR DURING {symbol} PREDICTION")
            print("="*80)
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            print("="*80)
    
    # Mark all predictions as complete
    with open(log_file, 'w') as f:
        f.write(today)
    
    # Summary
    if all_predictions:
        print("\n" + "="*80)
        print("📊 ALL PREDICTIONS SUMMARY")
        print("="*80)
        for symbol, pred in all_predictions.items():
            if pred.get('filtered'):
                print(f"\n{symbol}: HOLD (Filtered)")
            else:
                print(f"\n{symbol}: {pred['direction']} @ {pred['confidence']:.1f}% confidence")
        print("\n" + "="*80)

def main():
    """Main scheduler loop."""
    import sys
    
    print("="*80)
    print("🚀 MULTI-STOCK PREDICTION SCHEDULER")
    print("="*80)
    print("Schedule: Daily at 3:50 PM ET (10 min before close)")
    print("Predictor: Comprehensive multi-source analysis")
    sys.stdout.flush()  # Force output
    
    if MULTI_STOCK_MODE:
        stocks = get_active_stocks()
        print(f"Symbols: {', '.join(stocks)}")
    else:
        print("Symbol: AMD (single-stock mode)")
    
    print("Press Ctrl+C to stop")
    print("="*80)
    sys.stdout.flush()  # Force output
    
    # Run immediately if it's market close time
    if is_market_close_time():
        print("\nMarket close time detected - running prediction now...")
        run_scheduled_prediction()
    else:
        import sys
        et_tz = pytz.timezone('US/Eastern')
        now_et = datetime.now(et_tz)
        print(f"\nCurrent time: {now_et.strftime('%I:%M %p ET')}")
        print("Waiting for prediction time (3:50 PM ET - 10 min before close)...")
        sys.stdout.flush()  # Force output
    
    print("\nScheduler active. Checking every 2 minutes...\n")
    sys.stdout.flush()  # Force output
    
    while True:
        try:
            # Check for daily 4 PM prediction
            if is_market_close_time():
                print(f"\n[{datetime.now().strftime('%I:%M %p')}] Market close detected - running prediction...")
                run_scheduled_prediction()
                time.sleep(3600)  # Sleep 1 hour after running
            else:
                # Check every 2 minutes (more frequent to catch 3:50 PM window)
                time.sleep(120)
                
        except KeyboardInterrupt:
            print("\n\nScheduler stopped by user")
            break
        except Exception as e:
            print(f"\nScheduler error: {e}")
            time.sleep(60)  # Wait 1 minute on error

if __name__ == "__main__":
    main()
