"""Fast scheduled predictor - skips heavy data collection"""

import pytz
from datetime import datetime, timedelta
from pathlib import Path
from contrarian_safeguard import safeguard
from prediction_filters import PredictionFilters
import yfinance as yf

def is_trading_day():
    """Check if today is a trading day (Mon-Fri)."""
    return datetime.now().weekday() < 5

def is_market_close_time():
    """Check if it's 4:00-4:15 PM ET on a trading day."""
    et_tz = pytz.timezone('US/Eastern')
    now_et = datetime.now(et_tz)
    return (is_trading_day() and 
            now_et.hour == 16 and 
            now_et.minute < 15)

def generate_fast_prediction():
    """Generate a quick prediction without heavy data collection."""
    print("🚀 FAST PREDICTION MODE")
    print("📊 Using lightweight data collection...\n")
    
    try:
        # Get current AMD price
        amd = yf.Ticker("AMD")
        amd_data = amd.history(period="5d")
        current_price = float(amd_data['Close'].iloc[-1])
        
        # Get futures
        es = yf.Ticker("ES=F")
        nq = yf.Ticker("NQ=F")
        es_data = es.history(period="1d")
        nq_data = nq.history(period="1d")
        
        es_change = 0
        nq_change = 0
        if not es_data.empty and len(es_data) > 0:
            es_change = ((es_data['Close'].iloc[-1] - es_data['Open'].iloc[0]) / es_data['Open'].iloc[0]) * 100
        if not nq_data.empty and len(nq_data) > 0:
            nq_change = ((nq_data['Close'].iloc[-1] - nq_data['Open'].iloc[0]) / nq_data['Open'].iloc[0]) * 100
        
        # Get VIX
        vix = yf.Ticker("^VIX")
        vix_data = vix.history(period="1d")
        current_vix = float(vix_data['Close'].iloc[-1]) if not vix_data.empty else 20
        
        # Simple prediction logic based on futures
        avg_futures = (es_change + nq_change) / 2
        
        if avg_futures > 0.3:
            direction = "UP"
            confidence = min(0.65 + (avg_futures * 0.02), 0.85)
        elif avg_futures < -0.3:
            direction = "DOWN"
            confidence = min(0.65 + (abs(avg_futures) * 0.02), 0.85)
        else:
            # Neutral - use momentum
            momentum = ((amd_data['Close'].iloc[-1] - amd_data['Close'].iloc[-2]) / amd_data['Close'].iloc[-2]) * 100
            direction = "UP" if momentum > 0 else "DOWN"
            confidence = 0.62
        
        # Calculate target
        expected_move = 0.015 if confidence > 0.70 else 0.010
        target_price = current_price * (1 + expected_move) if direction == "UP" else current_price * (1 - expected_move)
        
        prediction = {
            'direction': direction,
            'confidence': confidence,
            'target_price': target_price,
            'current_price': current_price,
            'futures_es': es_change,
            'futures_nq': nq_change,
            'vix': current_vix
        }
        
        print(f"✅ FAST PREDICTION GENERATED:")
        print(f"   Direction: {direction}")
        print(f"   Confidence: {confidence:.1%}")
        print(f"   Current: ${current_price:.2f}")
        print(f"   Target: ${target_price:.2f}")
        print(f"   Futures: ES {es_change:+.2f}%, NQ {nq_change:+.2f}%")
        print(f"   VIX: {current_vix:.1f}\n")
        
        return prediction
        
    except Exception as e:
        print(f"❌ Error generating prediction: {e}")
        return None

def run_scheduled_prediction():
    """Run prediction if it's the right time."""
    log_file = Path(__file__).parent / "data" / "last_prediction_date.txt"
    log_file.parent.mkdir(exist_ok=True)
    
    # Check if already ran today
    today = datetime.now().date().isoformat()
    if log_file.exists():
        with open(log_file, 'r') as f:
            last_run = f.read().strip()
            if last_run == today:
                return
    
    print("🚀 SCHEDULED PREDICTION TRIGGERED")
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S ET')}\n")
    
    try:
        # Generate fast prediction
        prediction = generate_fast_prediction()
        
        if prediction:
            # Apply filters
            filters = PredictionFilters(min_confidence=0.60, enable_sentiment=False)
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
            print("📊 TUESDAY GAP PREDICTION")
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
    import time
    
    print("🚀 FAST AMD Stock Prediction Scheduler")
    print("   Daily: 4:00 PM ET (next-day prediction)")
    print("   Mode: FAST (lightweight data collection)")
    print("   Press Ctrl+C to stop\n")
    
    while True:
        try:
            if is_market_close_time():
                run_scheduled_prediction()
            
            # Check every 5 minutes
            time.sleep(300)
            
        except KeyboardInterrupt:
            print("\n👋 Scheduler stopped")
            break
        except Exception as e:
            print(f"❌ Error in main loop: {e}")
            time.sleep(300)

if __name__ == "__main__":
    main()
