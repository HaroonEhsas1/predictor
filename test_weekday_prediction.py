"""Quick test of weekday prediction"""

from ultra_accurate_gap_predictor import EnhancedUltraAccurateGapPredictor

print("🧪 Testing weekday prediction method...\n")

try:
    predictor = EnhancedUltraAccurateGapPredictor(symbol="AMD")
    
    print("✅ Predictor initialized")
    print("📊 Generating institutional ML prediction...\n")
    
    prediction = predictor.generate_institutional_ml_prediction()
    
    if prediction:
        print("✅ PREDICTION GENERATED!")
        print(f"Direction: {prediction.get('direction', prediction.get('directional_bias', 'N/A'))}")
        print(f"Confidence: {prediction.get('confidence', prediction.get('confidence_score', 0)):.1%}")
        print(f"Target: ${prediction.get('target_price', prediction.get('price_target', 0)):.2f}")
        
        # Check if it's NOT the 50% fallback
        conf = prediction.get('confidence', prediction.get('confidence_score', 0))
        if conf == 0.50:
            print("\n⚠️ WARNING: Got 50% - might be fallback!")
        else:
            print(f"\n✅ REAL PREDICTION: {conf:.1%} confidence")
    else:
        print("❌ No prediction returned")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
