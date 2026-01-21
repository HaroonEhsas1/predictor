#!/usr/bin/env python3
"""
DECISIVE Stock Predictor - Simple Wrapper
Takes standard predictions and applies decisive logic

Key Changes:
1. Lower score threshold: 0.02 (vs 0.04 standard)
2. Lower confidence minimum: 45% (vs 60% standard)
3. Position sizing by confidence level
4. Makes calls instead of filtering everything out

Author: Decisive Trading System
Created: October 23, 2025
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from comprehensive_nextday_predictor import ComprehensiveNextDayPredictor
from stock_config import get_stock_config

def apply_decisive_thresholds(prediction, symbol):
    """
    Apply decisive thresholds to a standard prediction
    
    Standard Mode:
    - Score threshold: ±0.04
    - Confidence minimum: 60%
    - Filters aggressively
    
    Decisive Mode:
    - Score threshold: ±0.02 (LOWER)
    - Confidence minimum: 45% (LOWER)
    - Position sizing by confidence
    
    Args:
        prediction: Prediction dict from ComprehensiveNextDayPredictor
        symbol: Stock symbol (e.g. 'AMD', 'AVGO', 'ORCL')
    """
    
    if not prediction:
        return None
    
    # Extract fields
    direction = prediction.get('direction', 'NEUTRAL')
    confidence = prediction.get('confidence', 0)
    current_price = prediction.get('current_price', 0)
    config = get_stock_config(symbol)
    
    # DEBUG: Show what fields are available
    available_fields = list(prediction.keys())
    
    # Try to get score from various possible fields
    score = None
    for score_field in ['score', 'raw_score', 'total_score', 'final_score']:
        if score_field in prediction:
            score = prediction[score_field]
            break
    
    # If no score found, calculate proxy based on direction/confidence
    if score is None or score == 0:
        if direction == 'UP':
            score = (confidence - 50) / 1000  # Scale to ~0.01-0.04 range
        elif direction == 'DOWN':
            score = -(confidence - 50) / 1000
        else:
            score = 0.0
        score_is_proxy = True
    else:
        score_is_proxy = False
    
    print(f"\n{'='*80}")
    print(f"\ud83d\udd25 DECISIVE ANALYSIS FOR {symbol}")
    print(f"{'='*80}\n")
    
    print(f"\ud83d\udcca STANDARD PREDICTION:")
    print(f"   Direction: {direction}")
    print(f"   Score: {score:+.3f}" + (" (proxy)" if score_is_proxy else ""))
    print(f"   Confidence: {confidence:.1f}%")
    print(f"   Filtered: {prediction.get('filtered', False)}")
    print(f"   Available fields: {', '.join(available_fields[:5])}..." if len(available_fields) > 5 else f"   Available fields: {', '.join(available_fields)}")
    
    # DECISIVE LOGIC with LOWER thresholds
    decisive_threshold = 0.02  # Was 0.04!
    min_confidence = 45  # Was 60%!
    
    print(f"\n\ud83d\udcc8 DECISIVE LOGIC:")
    print(f"\n💪 DECISIVE LOGIC:")
    print(f"   Threshold: ±{decisive_threshold} (standard: ±0.04)")
    print(f"   Min Confidence: {min_confidence}% (standard: 60%)")
    
    # Determine decisive direction
    if abs(score) >= decisive_threshold:
        decisive_direction = direction
        decisive_confidence = confidence
        
        # Check if originally filtered
        if prediction.get('filtered', False):
            print(f"   ✅ UNFILTERED: Score {score:+.3f} exceeds decisive threshold")
            decisive_confidence = max(confidence, min_confidence + 5)  # Boost if filtered
        else:
            print(f"   ✅ QUALIFIED: Passes decisive threshold")
    
    elif abs(score) >= 0.01:  # Very weak but not zero
        decisive_direction = "UP" if score > 0 else "DOWN"
        decisive_confidence = 45 + abs(score) * 500  # Scale 45-55%
        print(f"   ⚠️ WEAK SIGNAL: Score {score:+.3f} near threshold")
        print(f"   → Making cautious call: {decisive_direction} at {decisive_confidence:.1f}%")
    
    else:
        decisive_direction = "NEUTRAL"
        decisive_confidence = 40
        print(f"   ❌ TOO WEAK: Score {score:+.3f} below minimum")
    
    # Position sizing
    if decisive_confidence >= 70:
        position_size = 100
        size_desc = "FULL (100%)"
    elif decisive_confidence >= 60:
        position_size = 75
        size_desc = "LARGE (75%)"
    elif decisive_confidence >= 50:
        position_size = 50
        size_desc = "HALF (50%)"
    elif decisive_confidence >= 45:
        position_size = 25
        size_desc = "SMALL (25% test)"
    else:
        position_size = 0
        size_desc = "SKIP"
    
    print(f"\n📏 POSITION SIZING:")
    print(f"   Confidence: {decisive_confidence:.1f}%")
    print(f"   Position: {size_desc}")
    
    # Calculate targets
    volatility_pct = config['typical_volatility'] * 100  # Convert to percentage
    
    if decisive_confidence >= 70:
        target_pct = volatility_pct * 0.8
    elif decisive_confidence >= 60:
        target_pct = volatility_pct * 0.6
    elif decisive_confidence >= 50:
        target_pct = volatility_pct * 0.5
    else:
        target_pct = volatility_pct * 0.3
    
    stop_pct = target_pct * 0.6  # 1:1.67 R:R
    
    if decisive_direction == "UP":
        target_price = current_price * (1 + target_pct / 100)
        stop_price = current_price * (1 - stop_pct / 100)
    elif decisive_direction == "DOWN":
        target_price = current_price * (1 - target_pct / 100)
        stop_price = current_price * (1 + stop_pct / 100)
    else:
        target_price = current_price
        stop_price = current_price
        target_pct = 0
        stop_pct = 0
    
    risk_reward = target_pct / stop_pct if stop_pct > 0 else 0
    
    # Output
    print(f"\n{'='*80}")
    print(f"🎯 DECISIVE RESULT FOR {symbol}")
    print(f"{'='*80}\n")
    
    print(f"📍 Direction: {decisive_direction}")
    print(f"🎲 Confidence: {decisive_confidence:.1f}%")
    print(f"💰 Current: ${current_price:.2f}")
    
    if decisive_direction != "NEUTRAL" and position_size > 0:
        print(f"🎯 Target: ${target_price:.2f} ({target_pct:+.2f}%)")
        print(f"🛑 Stop: ${stop_price:.2f} ({stop_pct:+.2f}%)")
        print(f"📊 R:R: 1:{risk_reward:.2f}")
        print(f"📏 Position: {size_desc}")
        
        print(f"\n💡 OVERNIGHT TRADE PLAN:")
        print(f"   ⏰ Enter: Today 3:55 PM (market on close)")
        print(f"   📊 Direction: {decisive_direction}")
        print(f"   💰 Entry: ${current_price:.2f}")
        print(f"   🎯 Target: ${target_price:.2f}")
        print(f"   🛑 Stop: ${stop_price:.2f}")
        print(f"   🌅 Check: Tomorrow 6:00 AM premarket")
        print(f"   📤 Exit: When target hit or 9:30 AM open")
        
        tradeable = True
    else:
        print(f"\n⏸️ NO TRADE - Signal too weak or neutral")
        tradeable = False
    
    print(f"\n{'='*80}\n")
    
    return {
        'symbol': symbol,
        'decisive_direction': decisive_direction,
        'decisive_confidence': decisive_confidence,
        'current_price': current_price,
        'target': target_price,
        'stop': stop_price,
        'target_pct': target_pct,
        'stop_pct': stop_pct,
        'risk_reward': risk_reward,
        'position_size': position_size,
        'tradeable': tradeable,
        'original_direction': direction,
        'original_confidence': confidence,
        'original_filtered': prediction.get('filtered', False)
    }

def run_decisive_multi_stock(symbols=['AMD', 'AVGO', 'ORCL']):
    """Run decisive predictions for multiple stocks"""
    
    print("\n" + "="*80)
    print("🚀 DECISIVE MODE - OVERNIGHT SWING TRADING")
    print("="*80)
    print(f"📊 Stocks: {', '.join(symbols)}")
    print(f"⏰ Strategy: 3:50 PM entry → Exit next morning")
    print(f"🔥 Decisive Thresholds: Score ≥0.02, Confidence ≥45%")
    print("="*80)
    
    results = []
    trades = []
    
    for symbol in symbols:
        try:
            # Run standard prediction
            predictor = ComprehensiveNextDayPredictor(symbol=symbol)
            prediction = predictor.generate_comprehensive_prediction()
            
            if prediction:
                # Apply decisive logic - pass symbol explicitly
                decisive_result = apply_decisive_thresholds(prediction, symbol)
                
                if decisive_result:
                    results.append(decisive_result)
                    
                    if decisive_result['tradeable']:
                        trades.append(decisive_result)
        
        except Exception as e:
            print(f"❌ Error analyzing {symbol}: {e}")
            continue
    
    # Summary
    print("\n" + "="*80)
    print("📊 DECISIVE TRADE SUMMARY")
    print("="*80)
    
    if trades:
        print(f"\n✅ {len(trades)} ACTIONABLE TRADES FOUND:\n")
        
        for i, trade in enumerate(trades, 1):
            print(f"{'─'*80}")
            print(f"{i}. {trade['symbol']}: {trade['decisive_direction']}")
            print(f"   📊 Confidence: {trade['decisive_confidence']:.1f}%")
            print(f"   💰 Entry: ${trade['current_price']:.2f}")
            print(f"   🎯 Target: ${trade['target']:.2f} ({trade['target_pct']:+.2f}%)")
            print(f"   🛑 Stop: ${trade['stop']:.2f} ({trade['stop_pct']:+.2f}%)")
            print(f"   📊 R:R: 1:{trade['risk_reward']:.2f}")
            print(f"   📏 Position: {trade['position_size']}%")
            
            if trade['original_filtered']:
                print(f"   ⚡ UNFILTERED by decisive mode!")
        
        print(f"{'─'*80}")
        
        # Best trade
        best_trade = max(trades, key=lambda x: x['decisive_confidence'])
        print(f"\n⭐ BEST OPPORTUNITY:")
        print(f"   {best_trade['symbol']}: {best_trade['decisive_direction']}")
        print(f"   Confidence: {best_trade['decisive_confidence']:.1f}%")
        print(f"   Entry: ${best_trade['current_price']:.2f} → Target: ${best_trade['target']:.2f}")
        print(f"   Position Size: {best_trade['position_size']}%")
        
    else:
        print(f"\n⏸️ NO ACTIONABLE TRADES TODAY")
        print(f"\nEven with decisive thresholds, all signals too weak:")
        for result in results:
            print(f"   {result['symbol']}: {result['decisive_direction']} " +
                  f"({result['decisive_confidence']:.1f}% confidence)")
    
    print("\n" + "="*80)
    print("💡 NEXT STEPS:")
    if trades:
        print(f"   1. Review each trade setup above")
        print(f"   2. Enter positions at 3:55 PM (market on close)")
        print(f"   3. Set stop losses and targets")
        print(f"   4. Monitor premarket at 6:00 AM tomorrow")
        print(f"   5. Exit when targets hit or at 9:30 AM open")
    else:
        print(f"   → Wait for tomorrow's opportunities")
        print(f"   → Run again at 3:50 PM ET tomorrow")
    print("="*80 + "\n")
    
    return results

if __name__ == "__main__":
    results = run_decisive_multi_stock(['AMD', 'AVGO', 'ORCL'])
