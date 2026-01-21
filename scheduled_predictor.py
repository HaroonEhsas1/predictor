"""Scheduled prediction runner for Sunday 6 PM ET.

Run this continuously and it will automatically generate predictions
every Sunday at 6 PM ET for Monday's gap.
"""

import time
from datetime import datetime, timedelta
import pytz
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from ultra_accurate_gap_predictor import EnhancedUltraAccurateGapPredictor
from contrarian_safeguard import safeguard
from prediction_filters import PredictionFilters

def is_trading_day():
    """Check if today is a trading day (Mon-Fri)."""
    et_tz = pytz.timezone('US/Eastern')
    now_et = datetime.now(et_tz)
    return 0 <= now_et.weekday() <= 4  # Mon=0, Fri=4

def is_market_close_time():
    """Check if it's 4:00-4:15 PM ET on a trading day."""
    et_tz = pytz.timezone('US/Eastern')
    now_et = datetime.now(et_tz)
    
    is_weekday = is_trading_day()
    is_close_window = 16 <= now_et.hour < 17  # 4-5 PM
    
    return is_weekday and is_close_window

def is_sunday_prediction_time():
    """Check if it's Sunday after 6 PM ET (extended window until midnight)."""
    et_tz = pytz.timezone('US/Eastern')
    now_et = datetime.now(et_tz)
    
    is_sunday = now_et.weekday() == 6  # Sunday = 6
    is_evening = now_et.hour >= 18  # 6 PM or later (until midnight)
    
    return is_sunday and is_evening

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
                return  # Already ran today
    
    print("🚀 SCHEDULED PREDICTION TRIGGERED")
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S ET')}")
    
    try:
        # Initialize predictor
        predictor = EnhancedUltraAccurateGapPredictor(symbol="AMD")
        
        # Check if it's Sunday (use weekend data) or weekday (use current data)
        from datetime import date
        current_day = datetime.now().weekday()  # 0=Monday, 6=Sunday
        
        if current_day == 6:  # Sunday - predict Monday gap using weekend data
            print("📅 Sunday prediction mode: Using weekend data for Monday gap")
            next_monday = datetime.now() + timedelta(days=1)
            prediction = predictor._generate_sunday_prediction(target_date=next_monday.date())
        else:  # Monday-Friday - predict next day gap using current data
            print("📅 Weekday prediction mode: Using current data for tomorrow's gap")
            # Use the institutional ML prediction method
            prediction = predictor.generate_institutional_ml_prediction()
        
        if prediction:
            # Apply smart filters (confidence, futures, volatility)
            filters = PredictionFilters(min_confidence=0.60)
            prediction = filters.apply_filters(prediction)
            
            if not prediction:
                print("⏸️ Prediction filtered out - skipping trade")
                return
            
            # Apply contrarian safeguard
            prediction = safeguard.apply_safeguard(prediction)
            
            # Log prediction
            safeguard.log_prediction(prediction['direction'])
            
            # Display result
            print("\n" + "="*60)
            print("📊 MONDAY GAP PREDICTION")
            print("="*60)
            print(f"🎯 Direction: {prediction['direction']}")
            print(f"💰 Target Price: ${prediction.get('target_price', 0):.2f}")
            print(f"🎲 Confidence: {prediction.get('confidence', 0):.1%}")
            if prediction.get('contrarian_flip'):
                print(f"🔄 Contrarian Flip: YES ({prediction.get('reason', '')})")
            print(f"📈 Rolling Accuracy: {prediction.get('rolling_accuracy', 0):.1%}")
            print("="*60)
            
            # Mark as complete
            with open(log_file, 'w') as f:
                f.write(today)
        else:
            print("❌ Prediction failed to generate")
            
    except Exception as e:
        print(f"❌ Error during scheduled prediction: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main scheduler loop."""
    print("🕐 AMD Stock Prediction Scheduler")
    print("   Daily: 4:00 PM ET (next-day prediction)")
    print("   Sunday: 6:00 PM ET (Monday gap prediction)")
    print("   Press Ctrl+C to stop\n")
    
    while True:
        try:
            # Check for daily 4 PM prediction
            if is_market_close_time():
                print("📊 Market close detected - running daily prediction...")
                run_scheduled_prediction()
                time.sleep(3600)  # Sleep 1 hour after running
            
            # Check for Sunday 6 PM prediction
            elif is_sunday_prediction_time():
                print("📅 Sunday evening - running Monday prediction...")
                run_scheduled_prediction()
                time.sleep(3600)  # Sleep 1 hour after running
            
            else:
                # Check every 5 minutes
                time.sleep(300)
                
        except KeyboardInterrupt:
            print("\n👋 Scheduler stopped")
            break
        except Exception as e:
            print(f"❌ Scheduler error: {e}")
            time.sleep(60)  # Wait 1 minute on error

if __name__ == "__main__":
    main()
