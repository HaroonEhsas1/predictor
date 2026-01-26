#!/usr/bin/env python3
"""
INTRADAY 1-HOUR MULTI-STOCK RUNNER
Runs the 1-hour momentum predictor for all supported stocks
Designed to run during market hours (9:30 AM - 4:00 PM ET)

Usage:
    python intraday_multi_stock_runner.py                # Run once
    python intraday_multi_stock_runner.py --continuous   # Run every 5 minutes
    python intraday_multi_stock_runner.py --interval 15  # Run every N minutes
"""

import sys
import argparse
from datetime import datetime, timedelta
import pytz
import json
import time
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from intraday_1hour_predictor import IntraDay1HourPredictor


def is_market_open():
    """Check if US market is currently open"""
    et_tz = pytz.timezone('America/New_York')
    now_et = datetime.now(et_tz)
    
    # Market open: 9:30 AM - 4:00 PM ET, Mon-Fri
    market_open_time = now_et.replace(hour=9, minute=30, second=0, microsecond=0)
    market_close_time = now_et.replace(hour=16, minute=0, second=0, microsecond=0)
    
    is_weekday = now_et.weekday() < 5
    is_market_hours = market_open_time <= now_et <= market_close_time
    
    return is_weekday and is_market_hours


def run_intraday_analysis(stocks=None, mode='standard', model_blend=0.6):
    """Run intraday analysis for all stocks"""
    
    if stocks is None:
        stocks = ['AMD', 'NVDA', 'META', 'AVGO', 'SNOW', 'PLTR']
    
    et_tz = pytz.timezone('America/New_York')
    now_et = datetime.now(et_tz)
    
    print(f"\n{'='*80}")
    print(f"🚀 INTRADAY 1-HOUR MOMENTUM ANALYSIS")
    print(f"{'='*80}")
    print(f"⏰ {now_et.strftime('%Y-%m-%d %H:%M:%S %p ET')}")
    print(f"📊 Analyzing {len(stocks)} stocks: {', '.join(stocks)}")
    
    results = {}
    trades = []
    
    for symbol in stocks:
        try:
            print(f"\n{'─'*80}")
            predictor = IntraDay1HourPredictor(symbol, model_blend_weight=model_blend)
            prediction = predictor.predict_next_hour()
            
            results[symbol] = prediction
            
            # Track tradeable signals
            if prediction.get('position_size', 0) > 0:
                trades.append(prediction)
        
        except Exception as e:
            print(f"\n❌ Error analyzing {symbol}: {str(e)[:100]}")
            results[symbol] = {'error': str(e), 'symbol': symbol}
    
    # Generate summary
    print(f"\n{'='*80}")
    print(f"📊 INTRADAY TRADING SUMMARY")
    print(f"{'='*80}")
    
    if trades:
        print(f"\n🎯 {len(trades)} TRADING SIGNALS GENERATED:\n")
        
        # Sort by confidence (highest first)
        trades_sorted = sorted(trades, key=lambda x: x.get('confidence', 0), reverse=True)
        
        for trade in trades_sorted:
            print(f"\n{trade['symbol']} - {trade['direction']} Signal")
            print(f"   Confidence: {trade['confidence']*100:.1f}%")
            print(f"   Recommendation: {trade['recommendation']}")
            print(f"   Current Price: ${trade['current_price']:.2f}")
            print(f"   Entry: ${trade['entry']:.2f}")
            print(f"   Target: ${trade['target']:.2f} ({(trade['target']/trade['entry']-1)*100:+.2f}%)")
            print(f"   Stop: ${trade['stop']:.2f} ({(trade['stop']/trade['entry']-1)*100:+.2f}%)")
            print(f"   Position Size: {trade['position_size']*100:.0f}%")
            
            # Show momentum components
            components = trade.get('components', {})
            print(f"   📊 Momentum Drivers:")
            print(f"      • RSI: {components.get('rsi', 'N/A'):.1f}")
            print(f"      • MACD: {components.get('macd_signal', 'N/A')}")
            print(f"      • Trend: {components.get('trend', 'N/A')}")
            print(f"      • Volume: {components.get('volume_ratio', 0):.2f}x avg")
            print(f"      • News: {components.get('news_sentiment', 0):+.2f}")
            
            if trade['warning'] != 'None':
                print(f"   ⚠️ WARNING: {trade['warning']}")
    else:
        print(f"\n⚪ No trading signals at this time")
        print(f"   All stocks below confidence threshold")
    
    # Market context
    print(f"\n{'='*80}")
    print(f"📈 MARKET CONTEXT")
    print(f"{'='*80}")
    print(f"✅ Market Status: {'OPEN' if is_market_open() else 'CLOSED'}")
    print(f"⏰ Next session: Tomorrow 9:30 AM ET")
    
    # Save results
    os.makedirs('data/intraday', exist_ok=True)
    timestamp = now_et.strftime('%Y%m%d_%H%M%S')
    
    with open(f'data/intraday/intraday_{timestamp}.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Results saved to: data/intraday/intraday_{timestamp}.json")
    
    return results, trades


def continuous_monitoring(interval_minutes=5, stocks=None, model_blend=0.6):
    """Continuously monitor intraday signals"""
    
    print(f"\n🔄 CONTINUOUS INTRADAY MONITORING")
    print(f"   Interval: Every {interval_minutes} minutes")
    print(f"   Press Ctrl+C to stop\n")
    
    iteration = 0
    
    while True:
        iteration += 1
        
        if not is_market_open():
            print(f"\n⏰ {datetime.now(pytz.timezone('America/New_York')).strftime('%H:%M:%S')} - Market Closed")
            print(f"   Next session: Tomorrow 9:30 AM ET")
            break
        
        print(f"\n{'='*80}")
        print(f"Scan #{iteration} at {datetime.now(pytz.timezone('America/New_York')).strftime('%H:%M:%S ET')}")
        print(f"{'='*80}")
        
        try:
            results, trades = run_intraday_analysis(stocks=stocks, model_blend=model_blend)
            
            if trades:
                print(f"\n🔔 ALERT: {len(trades)} trading signal(s) generated!")
                # Could add sound alert, email notification, etc here
        
        except Exception as e:
            print(f"\n❌ Error in monitoring loop: {str(e)}")
        
        # Wait for next interval
        print(f"\n⏳ Next scan in {interval_minutes} minutes...")
        try:
            time.sleep(interval_minutes * 60)
        except KeyboardInterrupt:
            print(f"\n\n✅ Monitoring stopped by user")
            break


def main():
    """Main entry point"""
    
    parser = argparse.ArgumentParser(description='Intraday 1-Hour Momentum Predictor')
    parser.add_argument('--continuous', action='store_true', help='Run continuously during market hours')
    parser.add_argument('--interval', type=int, default=5, help='Interval between scans (minutes)')
    parser.add_argument('--allow-offhours', action='store_true', help='Allow running outside market hours')
    parser.add_argument('--stocks', type=str, default='AMD,NVDA,META,AVGO,SNOW,PLTR', 
                       help='Comma-separated list of stocks to analyze')
    parser.add_argument('--model-blend', type=float, default=0.6,
                       help='Model blending weight (0.0-1.0): 1.0=full model, 0.0=raw sentiment')
    
    args = parser.parse_args()
    
    stocks = args.stocks.split(',') if args.stocks else None
    
    if args.continuous:
        continuous_monitoring(interval_minutes=args.interval, stocks=stocks, model_blend=args.model_blend)
    else:
        # Prevent accidental runs outside market hours unless user explicitly allows it
        if not args.allow_offhours and not is_market_open():
            et_tz = pytz.timezone('America/New_York')
            now_et = datetime.now(et_tz)
            print(f"\n⏰ Market is CLOSED (ET: {now_et.strftime('%Y-%m-%d %H:%M:%S')}).")
            print("   To run anyway, pass --allow-offhours. Exiting without generating predictions.")
            return

        run_intraday_analysis(stocks=stocks, model_blend=args.model_blend)


if __name__ == '__main__':
    main()
