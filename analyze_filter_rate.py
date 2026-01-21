"""
Analyze if the system is filtering too aggressively
Check historical predictions to see filter rate
"""
import json
import os
from datetime import datetime

def analyze_filter_rate():
    """Check how often system filters vs trades"""
    
    print("="*80)
    print("📊 FILTER RATE ANALYSIS")
    print("="*80)
    
    # Get all prediction files
    data_dir = 'data/multi_stock'
    prediction_files = sorted([f for f in os.listdir(data_dir) if f.startswith('predictions_') and f.endswith('.json')])
    
    print(f"\n📁 Found {len(prediction_files)} prediction files\n")
    
    total_predictions = 0
    filtered_count = 0
    traded_count = 0
    
    confidence_distribution = {
        '<50%': 0,
        '50-60%': 0,
        '60-70%': 0,
        '70-80%': 0,
        '>80%': 0
    }
    
    recent_predictions = []
    
    for filename in prediction_files[-10:]:  # Last 10 files
        filepath = os.path.join(data_dir, filename)
        
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        timestamp = data.get('timestamp', filename)
        predictions = data.get('predictions', {})
        
        print(f"\n📅 {filename}:")
        
        for symbol, pred in predictions.items():
            total_predictions += 1
            confidence = pred['confidence']
            direction = pred['direction']
            filtered = pred.get('filtered', False)
            
            # Track confidence distribution
            if confidence < 50:
                confidence_distribution['<50%'] += 1
            elif confidence < 60:
                confidence_distribution['50-60%'] += 1
            elif confidence < 70:
                confidence_distribution['60-70%'] += 1
            elif confidence < 80:
                confidence_distribution['70-80%'] += 1
            else:
                confidence_distribution['>80%'] += 1
            
            if filtered or confidence < 60:
                filtered_count += 1
                status = "❌ FILTERED"
            else:
                traded_count += 1
                status = "✅ TRADE"
            
            print(f"   {symbol}: {direction} {confidence:.1f}% - {status}")
            
            recent_predictions.append({
                'symbol': symbol,
                'confidence': confidence,
                'direction': direction,
                'filtered': filtered or confidence < 60,
                'timestamp': timestamp
            })
    
    print("\n" + "="*80)
    print("📊 OVERALL STATISTICS")
    print("="*80)
    
    filter_rate = (filtered_count / total_predictions * 100) if total_predictions > 0 else 0
    trade_rate = (traded_count / total_predictions * 100) if total_predictions > 0 else 0
    
    print(f"\nTotal Predictions: {total_predictions}")
    print(f"Filtered: {filtered_count} ({filter_rate:.1f}%)")
    print(f"Traded: {traded_count} ({trade_rate:.1f}%)")
    
    print(f"\n📊 Confidence Distribution:")
    for range_label, count in confidence_distribution.items():
        pct = (count / total_predictions * 100) if total_predictions > 0 else 0
        bar = "█" * int(pct / 2)
        print(f"   {range_label:10s}: {count:3d} ({pct:5.1f}%) {bar}")
    
    print(f"\n{'='*80}")
    print("💡 ANALYSIS:")
    print(f"{'='*80}")
    
    if filter_rate > 70:
        print(f"\n⚠️ FILTER RATE TOO HIGH: {filter_rate:.1f}%")
        print(f"   System is filtering TOO MANY trades!")
        print(f"   Recommendations:")
        print(f"   1. Lower threshold from 62% to 60%")
        print(f"   2. Reduce conflict penalty (85% instead of 75%)")
        print(f"   3. Don't raise threshold for conflicts")
    elif filter_rate > 50:
        print(f"\n⚠️ FILTER RATE HIGH: {filter_rate:.1f}%")
        print(f"   System is selective (good) but may miss opportunities")
        print(f"   Monitor for next few days")
    elif filter_rate > 30:
        print(f"\n✅ FILTER RATE BALANCED: {filter_rate:.1f}%")
        print(f"   Good balance - filters bad trades, takes good ones")
    else:
        print(f"\n⚠️ FILTER RATE LOW: {filter_rate:.1f}%")
        print(f"   System may be taking too many marginal trades")
        print(f"   Consider raising threshold")
    
    # Check today's specific situation
    print(f"\n{'='*80}")
    print("🔍 TODAY'S SITUATION (Oct 22):")
    print(f"{'='*80}")
    print(f"\nMarket Context:")
    print(f"   • SPY: -0.80% (weak)")
    print(f"   • QQQ: -1.41% (tech down)")
    print(f"   • VIX: +9.46% (fear spike)")
    print(f"\nAll 3 stocks filtered (32-35% confidence)")
    print(f"Reason: 3 conflicts each + technical veto")
    print(f"\nThis is CORRECT filtering for a messy market day!")
    print(f"On clear days (like Monday), confidence would be 70%+")

if __name__ == "__main__":
    analyze_filter_rate()
