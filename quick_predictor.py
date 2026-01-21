"""Quick prediction without heavy initialization"""

import yfinance as yf
from prediction_filters import PredictionFilters
from contrarian_safeguard import safeguard

def generate_quick_prediction():
    """Generate prediction using lightweight data collection."""
    print("🚀 QUICK PREDICTION MODE (No heavy initialization)")
    print("📊 Collecting essential data only...\n")
    
    try:
        # Get AMD price
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
        if not es_data.empty:
            es_change = ((es_data['Close'].iloc[-1] - es_data['Open'].iloc[0]) / es_data['Open'].iloc[0]) * 100
        if not nq_data.empty:
            nq_change = ((nq_data['Close'].iloc[-1] - nq_data['Open'].iloc[0]) / nq_data['Open'].iloc[0]) * 100
        
        # Get VIX
        vix = yf.Ticker("^VIX")
        vix_data = vix.history(period="1d")
        current_vix = float(vix_data['Close'].iloc[-1]) if not vix_data.empty else 20
        
        # Calculate momentum
        momentum = ((amd_data['Close'].iloc[-1] - amd_data['Close'].iloc[-2]) / amd_data['Close'].iloc[-2]) * 100
        
        # Prediction logic
        avg_futures = (es_change + nq_change) / 2
        
        # Strong futures signal
        if avg_futures > 0.5:
            direction = "UP"
            confidence = min(0.68 + (avg_futures * 0.03), 0.88)
        elif avg_futures < -0.5:
            direction = "DOWN"
            confidence = min(0.68 + (abs(avg_futures) * 0.03), 0.88)
        # Moderate futures + momentum
        elif avg_futures > 0.2 and momentum > 0:
            direction = "UP"
            confidence = 0.65
        elif avg_futures < -0.2 and momentum < 0:
            direction = "DOWN"
            confidence = 0.65
        # Use momentum
        elif momentum > 1:
            direction = "UP"
            confidence = 0.62
        elif momentum < -1:
            direction = "DOWN"
            confidence = 0.62
        # Weak signal
        else:
            direction = "UP" if momentum > 0 else "DOWN"
            confidence = 0.58
        
        # VIX adjustment
        if current_vix > 25:
            confidence *= 0.85
        elif current_vix < 15:
            confidence *= 1.05
        
        # Calculate target
        expected_move = 0.015 if confidence > 0.70 else 0.012
        target_price = current_price * (1 + expected_move) if direction == "UP" else current_price * (1 - expected_move)
        
        prediction = {
            'direction': direction,
            'directional_bias': direction,
            'confidence': confidence,
            'confidence_score': confidence,
            'target_price': target_price,
            'current_price': current_price,
            'futures_es': es_change,
            'futures_nq': nq_change,
            'vix': current_vix,
            'momentum': momentum
        }
        
        print(f"✅ PREDICTION GENERATED:")
        print(f"   Direction: {direction}")
        print(f"   Confidence: {confidence:.1%}")
        print(f"   Current: ${current_price:.2f}")
        print(f"   Target: ${target_price:.2f}")
        print(f"   Futures: ES {es_change:+.2f}%, NQ {nq_change:+.2f}%")
        print(f"   VIX: {current_vix:.1f}")
        print(f"   Momentum: {momentum:+.2f}%\n")
        
        return prediction
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    prediction = generate_quick_prediction()
    
    if prediction:
        print("\n📊 Applying filters...")
        filters = PredictionFilters(min_confidence=0.60, enable_sentiment=False)
        filtered = filters.apply_filters(prediction)
        
        if filtered:
            print("\n✅ FINAL PREDICTION:")
            print(f"   Direction: {filtered['direction']}")
            print(f"   Confidence: {filtered['confidence']:.1%}")
            print(f"   Target: ${filtered['target_price']:.2f}")
            
            # Apply contrarian
            filtered = safeguard.apply_safeguard(filtered)
            safeguard.log_prediction(filtered['direction'])
            
            if filtered.get('contrarian_flip'):
                print(f"   🔄 Contrarian Flip: {filtered.get('reason')}")
        else:
            print("\n⏸️ Prediction filtered out")
