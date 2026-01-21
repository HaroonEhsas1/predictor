#!/usr/bin/env python3
"""
After Close Engine - Continuous Monitor
Runs continuous predictions with regular updates, similar to the main gap predictor
"""
import time
import json
import logging
from datetime import datetime, timedelta
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from engine import predict_command, setup_logging

def continuous_monitor():
    """Run continuous after-close predictions with regular updates"""
    
    print("🌙 AFTER CLOSE ENGINE - CONTINUOUS MONITOR")
    print("⚖️ Independent Overnight Gap Prediction System")
    print("📊 Using Real Market Data for Pre-Market Analysis")
    print("🎯 Symbol: AMD | Confidence Threshold: 70%")
    print("🔧 Models: GradientBoosting (Production Ready)")
    print("=" * 80)
    
    setup_logging(debug=False)
    logger = logging.getLogger(__name__)
    
    update_interval = 300  # 5 minutes
    
    while True:
        try:
            current_time = datetime.now()
            print(f"\n🔄 AFTER CLOSE PREDICTION UPDATE - {current_time.strftime('%H:%M:%S ET')}")
            print("=" * 80)
            
            # Run prediction
            result = predict_command(dry_run=False, auto_fit=False)
            
            if result['status'] == 'success':
                prediction = result['prediction']
                
                # Display prediction with nice formatting
                direction_emoji = {
                    'UP': '🟢',
                    'DOWN': '🔴', 
                    'SKIP': '🟡'
                }.get(prediction['direction'], '⚪')
                
                print(f"{direction_emoji} OVERNIGHT GAP PREDICTION: {prediction['direction']}")
                print(f"📊 Confidence: {prediction['confidence']:.1%}")
                print(f"💰 Expected Open: ${prediction['expected_open']:.2f}")
                print(f"📈 Current Price: ${prediction.get('current_price', 0):.2f}")
                
                if prediction['direction'] != 'SKIP':
                    gap_size = abs(prediction['expected_open'] - prediction.get('current_price', 0))
                    print(f"📏 Expected Gap: ${gap_size:.2f}")
                else:
                    threshold = prediction.get('confidence_threshold', 0.7)
                    print(f"📋 Reason: Confidence {prediction['confidence']:.1%} below {threshold:.0%} threshold")
                
                # Show key features
                features = prediction.get('features', {})
                print(f"\n🔍 KEY OVERNIGHT SIGNALS:")
                print(f"    📈 Futures Move: {features.get('overnight_futures_pct', 0):.2f}%")
                print(f"    📊 Options Flow: {features.get('net_options_flow', 0):.2f}")
                print(f"    📰 News Sentiment: {features.get('news_sentiment_score', 0):.2f}")
                print(f"    🌍 Global Impact: {features.get('global_index_impact_score', 0):.2f}")
                
                # Model breakdown
                models = prediction.get('model_predictions', {})
                print(f"\n🤖 MODEL ENSEMBLE:")
                print(f"    ⚡ LightGBM: {models.get('lightgbm', 0):.4f}")
                print(f"    🧠 LSTM: {models.get('lstm', 0):.4f}")
                
            else:
                print(f"❌ Prediction failed: {result.get('error', 'Unknown error')}")
            
            next_update = datetime.now() + timedelta(seconds=update_interval)
            print(f"\n⏰ Next update in {update_interval//60} minutes at {next_update.strftime('%H:%M ET')}")
            
            # Wait for next update
            time.sleep(update_interval)
            
        except KeyboardInterrupt:
            print("\n\n⏹️ Monitor stopped by user")
            break
        except Exception as e:
            logger.error(f"Monitor error: {e}")
            print(f"❌ Error occurred: {e}")
            print(f"⏳ Retrying in 30 seconds...")
            time.sleep(30)

if __name__ == "__main__":
    continuous_monitor()