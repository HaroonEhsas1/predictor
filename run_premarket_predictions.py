"""
DAILY PREMARKET PREDICTIONS
Run this at 9:15 AM before market opens

Gets predictions for all stocks with full enhancements:
- Stock-specific intelligence
- Adaptive thresholds (VIX-based)
- Regime detection
- Correlation management
- VWAP analysis
- All hidden signals

Simple usage: python run_premarket_predictions.py
"""

from stock_specific_predictors import get_predictor
from adaptive_thresholds import get_adaptive_threshold, print_threshold_status
from regime_detector import detect_market_regime, print_regime_status
from correlation_manager import get_stock_correlation, apply_correlation_sizing
from volume_profile import print_vwap_analysis
from datetime import datetime

def run_daily_predictions():
    """
    Run complete daily premarket predictions
    """
    
    print("\n" + "="*80)
    print("🚀 DAILY PREMARKET PREDICTIONS")
    print("="*80)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d')}")
    print(f"Time: {datetime.now().strftime('%H:%M:%S')}")
    print("\nRun this at 9:15 AM for today's trading signals!")
    print("="*80)
    
    symbols = ['AMD', 'NVDA', 'META', 'AVGO']
    
    # STEP 1: Market Context
    print("\n" + "="*80)
    print("📊 STEP 1: MARKET CONTEXT ANALYSIS")
    print("="*80)
    
    # Get adaptive threshold
    threshold_info = get_adaptive_threshold()
    print(f"\n🎯 Adaptive Threshold:")
    print(f"   VIX: {threshold_info.get('vix', 'N/A')}")
    print(f"   Regime: {threshold_info['regime']}")
    print(f"   Threshold: {threshold_info['threshold']} points")
    print(f"   Reasoning: {threshold_info['reasoning']}")
    
    # Get market regime
    regime_info = detect_market_regime()
    print(f"\n📈 Market Regime:")
    print(f"   Regime: {regime_info['regime']}")
    print(f"   Strategy: {regime_info['strategy']}")
    print(f"   Position Size Adjustment: {regime_info['adjustments']['position_size_modifier']:.0%}")
    print(f"   Max Positions: {regime_info['adjustments']['max_positions']}")
    
    # Get correlation
    corr_info = get_stock_correlation(symbols)
    print(f"\n🔗 Correlation Analysis:")
    if corr_info['success']:
        print(f"   Average Correlation: {corr_info['avg_correlation']:.2f}")
        print(f"   Risk Level: {corr_info['risk_level']}")
        print(f"   Max Positions: {corr_info['max_positions']}")
    else:
        print(f"   Using conservative defaults")
    
    # STEP 2: Stock Analysis
    print("\n" + "="*80)
    print("📊 STEP 2: INDIVIDUAL STOCK ANALYSIS")
    print("="*80)
    
    predictions = {}
    
    for symbol in symbols:
        print(f"\n{'='*80}")
        print(f"📊 {symbol} ANALYSIS")
        print('='*80)
        
        # Get predictor
        predictor = get_predictor(symbol)
        
        # NOTE: In real use, you'd fetch actual premarket data here
        # For now, this shows the structure
        print(f"\n⚠️ MANUAL INPUT REQUIRED:")
        print(f"   Please enter current premarket data for {symbol}:")
        print(f"   - Gap % (from yesterday's close)")
        print(f"   - Premarket volume")
        print(f"   - Any news/catalysts")
        
        # Example structure (you'll fill with real data)
        test_data = {
            'gap_pct': 0.0,  # UPDATE WITH REAL GAP
            'volume': 0,      # UPDATE WITH REAL VOLUME
            'min_volume': 1000000,  # Stock-specific
            'trap_signals': False,
            'news': None
        }
        
        print(f"\n📊 Stock-Specific Intelligence:")
        print(f"   Min Gap: {predictor.min_gap:.2f}%")
        print(f"   Gap Trust: {predictor.gap_trust*100:.0f}%")
        print(f"   Trap Risk: {predictor.trap_risk*100:.0f}%")
        
        # Get prediction (with example data)
        pred = predictor.predict(test_data)
        predictions[symbol] = pred
        
        print(f"\n🎯 Prediction:")
        print(f"   Direction: {pred['direction']}")
        print(f"   Confidence: {pred.get('confidence', 0)*100:.0f}%")
        if 'reason' in pred:
            print(f"   Reason: {pred['reason']}")
        if 'warning' in pred:
            print(f"   ⚠️ Warning: {pred['warning']}")
    
    # STEP 3: Apply Enhancements
    print("\n" + "="*80)
    print("📊 STEP 3: APPLY ENHANCEMENTS")
    print("="*80)
    
    # Apply regime adjustments
    for symbol, pred in predictions.items():
        if pred['direction'] != 'NEUTRAL':
            original_conf = pred.get('confidence', 0.5)
            
            # Regime adjustment
            if regime_info['regime'] in ['HIGH_VOLATILITY', 'TRENDING_BEAR']:
                pred['confidence'] = original_conf * 0.95
            elif regime_info['regime'] == 'TRENDING_BULL':
                pred['confidence'] = min(original_conf * 1.05, 0.95)
            
            # Position size from regime
            original_size = 1.0  # Default
            pred['position_size'] = original_size * regime_info['adjustments']['position_size_modifier']
            pred['regime_adjusted'] = True
    
    # Apply correlation limits
    result = apply_correlation_sizing(predictions, symbols)
    predictions = result['predictions']
    
    # STEP 4: Final Recommendations
    print("\n" + "="*80)
    print("🎯 STEP 4: FINAL TRADING RECOMMENDATIONS")
    print("="*80)
    
    print(f"\n📊 Market Context:")
    print(f"   Threshold: {threshold_info['threshold']} points ({threshold_info['regime']})")
    print(f"   Regime: {regime_info['regime']} ({regime_info['strategy']})")
    print(f"   Correlation: {corr_info.get('avg_correlation', 'N/A')} (Max {corr_info['max_positions']} positions)")
    
    print(f"\n🎯 Stock Recommendations:")
    
    tradeable = []
    
    for symbol, pred in predictions.items():
        print(f"\n{symbol}:")
        print(f"  Direction: {pred['direction']}")
        print(f"  Confidence: {pred.get('confidence', 0)*100:.0f}%")
        print(f"  Position Size: {pred.get('position_size', 0)*100:.0f}%")
        
        if pred.get('correlation_skip'):
            print(f"  ⚠️ {pred['skip_reason']}")
        elif pred.get('correlation_adjusted'):
            print(f"  📊 Correlation adjusted")
        
        if pred.get('regime_adjusted'):
            print(f"  📈 Regime adjusted ({regime_info['regime']})")
        
        # Trading decision
        if pred['direction'] != 'NEUTRAL' and pred.get('position_size', 0) > 0:
            confidence = pred.get('confidence', 0)
            
            if confidence >= 0.75:
                action = "STRONG BUY" if pred['direction'] == 'UP' else "STRONG SELL"
                emoji = "🟢🟢🟢"
            elif confidence >= 0.65:
                action = "BUY" if pred['direction'] == 'UP' else "SELL"
                emoji = "🟢🟢"
            elif confidence >= 0.55:
                action = "CAUTIOUS" if pred['direction'] == 'UP' else "CAUTIOUS SHORT"
                emoji = "🟡"
            else:
                action = "SKIP"
                emoji = "⚪"
            
            print(f"  {emoji} RECOMMENDATION: {action}")
            
            if action != "SKIP":
                tradeable.append((symbol, pred, action))
        else:
            print(f"  ⚪ RECOMMENDATION: SKIP")
    
    # Summary
    print("\n" + "="*80)
    print("📋 TRADING SUMMARY")
    print("="*80)
    
    if tradeable:
        print(f"\n✅ {len(tradeable)} Trading Opportunities:")
        for symbol, pred, action in tradeable:
            print(f"\n{symbol}: {action}")
            print(f"  Entry: 9:25-9:30 AM")
            print(f"  Position: {pred.get('position_size', 0)*100:.0f}% of account")
            print(f"  Confidence: {pred.get('confidence', 0)*100:.0f}%")
            
            # Risk management
            if symbol == 'AMD' and pred['direction'] == 'UP':
                print(f"  EXIT: 9:35 AM (AMD reversal risk!)")
            else:
                print(f"  Target: Set based on ATR")
                print(f"  Stop: Set based on ATR × confidence")
    else:
        print("\n⚪ NO TRADES TODAY")
        print("   Market conditions not favorable")
        print("   Wait for better opportunities")
    
    print("\n" + "="*80)
    print("✅ ANALYSIS COMPLETE!")
    print("="*80)
    print("""
Next Steps:
1. Review recommendations above
2. Check actual premarket data (9:15-9:25 AM)
3. Enter positions at 9:25-9:30 AM if recommended
4. Set stops and targets immediately
5. Manage positions according to plan

Good luck trading! 🚀
    """)
    
    return {
        'threshold_info': threshold_info,
        'regime_info': regime_info,
        'correlation_info': corr_info,
        'predictions': predictions,
        'tradeable': tradeable
    }


def quick_prediction(symbol, gap_pct, volume, min_volume=1000000, news=None):
    """
    Quick prediction for a single stock
    
    Args:
        symbol: Stock symbol (AMD, NVDA, META, AVGO)
        gap_pct: Gap % from yesterday's close
        volume: Current premarket volume
        min_volume: Minimum volume threshold
        news: Any relevant news (optional)
    
    Returns:
        dict: Prediction result
    """
    
    predictor = get_predictor(symbol)
    
    data = {
        'gap_pct': gap_pct,
        'volume': volume,
        'min_volume': min_volume,
        'trap_signals': False,
        'news': news
    }
    
    result = predictor.predict(data)
    
    print(f"\n{'='*80}")
    print(f"📊 {symbol} QUICK PREDICTION")
    print('='*80)
    print(f"Gap: {gap_pct:+.2f}%")
    print(f"Volume: {volume:,}")
    print(f"\nDirection: {result['direction']}")
    print(f"Confidence: {result.get('confidence', 0)*100:.0f}%")
    if 'reason' in result:
        print(f"Reason: {result['reason']}")
    if 'warning' in result:
        print(f"⚠️ {result['warning']}")
    print('='*80)
    
    return result


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                     DAILY PREMARKET PREDICTION SYSTEM                        ║
║                                                                              ║
║  Run at 9:15 AM for today's trading signals                                 ║
║  Enhanced with ALL intelligent features                                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    # Run daily predictions
    results = run_daily_predictions()
    
    print("\n" + "="*80)
    print("📖 USAGE EXAMPLES")
    print("="*80)
    print("""
# Full daily analysis (run at 9:15 AM):
python run_premarket_predictions.py

# Quick single stock prediction:
from run_premarket_predictions import quick_prediction
quick_prediction('AMD', gap_pct=2.5, volume=3000000)
quick_prediction('NVDA', gap_pct=-1.2, volume=5000000)

# Get raw prediction object:
from stock_specific_predictors import get_predictor
predictor = get_predictor('AMD')
result = predictor.predict({'gap_pct': 2.0, 'volume': 2000000, 'min_volume': 1000000})
    """)
