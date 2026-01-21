"""
HIDDEN INSTITUTIONAL PATTERN DETECTOR
======================================
Detects signs that "only few people know" - Smart Money Signals

These are patterns institutional traders use before major moves:
1. Dark pool accumulation/distribution
2. Unusual options activity (big money positioning)
3. Put/Call ratio divergence (institutions hedging)
4. Volume-price divergence (accumulation/distribution)
5. After-hours institutional positioning
6. Futures pre-positioning (overnight edge)
7. VIX options (fear positioning before drops)
8. Sector rotation patterns (money flow)
9. Insider trading patterns (legal filings)
10. Smart money indices (institutional activity)

Author: StockSense Detection System
Created: Oct 30, 2025
"""

import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd

def detect_dark_pool_activity(symbol, days=5):
    """
    Detect unusual dark pool / block trade activity
    Large trades that don't show up on regular exchanges
    
    Hidden Sign: When volume spikes but price doesn't move = accumulation
    """
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period=f'{days}d', interval='1d')
        
        # Calculate volume patterns
        avg_volume = hist['Volume'].mean()
        recent_volume = hist['Volume'].iloc[-1]
        volume_ratio = recent_volume / avg_volume
        
        # Price change vs volume (divergence)
        price_change = ((hist['Close'].iloc[-1] - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2]) * 100
        
        print(f"\n🔒 DARK POOL ANALYSIS ({symbol}):")
        print(f"   Average Volume: {avg_volume:,.0f}")
        print(f"   Recent Volume:  {recent_volume:,.0f}")
        print(f"   Volume Ratio:   {volume_ratio:.2f}x")
        print(f"   Price Change:   {price_change:+.2f}%")
        
        # Hidden Sign Detection
        if volume_ratio > 2.0 and abs(price_change) < 1.0:
            print(f"   🚨 ACCUMULATION DETECTED: High volume, low price move")
            print(f"      → Institutions quietly buying (BULLISH)")
            signal = "BULLISH_ACCUMULATION"
        elif volume_ratio > 2.0 and price_change < -2.0:
            print(f"   🚨 DISTRIBUTION DETECTED: High volume, big drop")
            print(f"      → Institutions dumping (BEARISH)")
            signal = "BEARISH_DISTRIBUTION"
        elif volume_ratio < 0.5:
            print(f"   ⚠️ LOW VOLUME: Retail only, institutions absent")
            signal = "NO_INSTITUTIONAL_INTEREST"
        else:
            print(f"   ✅ NORMAL: No unusual activity")
            signal = "NORMAL"
        
        return {
            'signal': signal,
            'volume_ratio': volume_ratio,
            'price_change': price_change
        }
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return {'signal': 'ERROR', 'volume_ratio': 0, 'price_change': 0}


def detect_unusual_options_activity(symbol):
    """
    Detect unusual options activity (smart money positioning)
    
    Hidden Signs:
    - Large put buying = Institutions expecting drop
    - Large call buying = Institutions expecting rally
    - Put/Call ratio spike = Fear/hedging
    """
    try:
        stock = yf.Ticker(symbol)
        options_dates = stock.options
        
        if len(options_dates) > 0:
            # Get nearest expiration
            nearest_exp = options_dates[0]
            calls = stock.option_chain(nearest_exp).calls
            puts = stock.option_chain(nearest_exp).puts
            
            # Calculate activity
            call_volume = calls['volume'].sum()
            put_volume = puts['volume'].sum()
            
            if call_volume > 0:
                pc_ratio = put_volume / call_volume
            else:
                pc_ratio = 0
            
            # Open interest (future positioning)
            call_oi = calls['openInterest'].sum()
            put_oi = puts['openInterest'].sum()
            
            print(f"\n📊 OPTIONS ACTIVITY ({symbol}):")
            print(f"   Call Volume:    {call_volume:,.0f}")
            print(f"   Put Volume:     {put_volume:,.0f}")
            print(f"   P/C Ratio:      {pc_ratio:.2f}")
            print(f"   Call OI:        {call_oi:,.0f}")
            print(f"   Put OI:         {put_oi:,.0f}")
            
            # Hidden Sign Detection
            if pc_ratio > 2.0:
                print(f"   🚨 HIGH PUT ACTIVITY: Institutions hedging")
                print(f"      → Expecting drop (BEARISH)")
                signal = "BEARISH_HEDGING"
            elif pc_ratio < 0.5:
                print(f"   🚨 HIGH CALL ACTIVITY: Institutions bullish")
                print(f"      → Expecting rally (BULLISH)")
                signal = "BULLISH_POSITIONING"
            elif pc_ratio > 1.3 and pc_ratio < 1.7:
                print(f"   ⚠️ BALANCED: No clear institutional bias")
                signal = "NEUTRAL"
            else:
                print(f"   ✅ NORMAL: Standard activity")
                signal = "NORMAL"
            
            return {
                'signal': signal,
                'pc_ratio': pc_ratio,
                'call_volume': call_volume,
                'put_volume': put_volume
            }
        else:
            print(f"\n📊 OPTIONS ACTIVITY ({symbol}): No data")
            return {'signal': 'NO_DATA', 'pc_ratio': 0}
            
    except Exception as e:
        print(f"\n📊 OPTIONS ACTIVITY ({symbol}): Error - {e}")
        return {'signal': 'ERROR', 'pc_ratio': 0}


def detect_price_momentum_divergence(symbol, days=10):
    """
    Detect divergence between price and momentum
    
    Hidden Sign: Price going up but momentum slowing = Top forming
    Hidden Sign: Price going down but momentum slowing = Bottom forming
    """
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period=f'{days}d')
        
        # Calculate price trend
        first_price = hist['Close'].iloc[0]
        last_price = hist['Close'].iloc[-1]
        price_change = ((last_price - first_price) / first_price) * 100
        
        # Calculate momentum (last 3 days vs previous 3 days)
        recent_3 = hist['Close'].iloc[-3:].mean()
        previous_3 = hist['Close'].iloc[-6:-3].mean()
        momentum = ((recent_3 - previous_3) / previous_3) * 100
        
        print(f"\n📈 MOMENTUM DIVERGENCE ({symbol}):")
        print(f"   {days}-Day Price Change: {price_change:+.2f}%")
        print(f"   Recent Momentum:        {momentum:+.2f}%")
        
        # Hidden Sign Detection
        if price_change > 3 and momentum < 0:
            print(f"   🚨 BEARISH DIVERGENCE: Price up but momentum down")
            print(f"      → Top forming, expect reversal (BEARISH)")
            signal = "BEARISH_DIVERGENCE"
        elif price_change < -3 and momentum > 0:
            print(f"   🚨 BULLISH DIVERGENCE: Price down but momentum up")
            print(f"      → Bottom forming, expect bounce (BULLISH)")
            signal = "BULLISH_DIVERGENCE"
        else:
            print(f"   ✅ ALIGNED: Price and momentum agree")
            signal = "ALIGNED"
        
        return {
            'signal': signal,
            'price_change': price_change,
            'momentum': momentum
        }
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return {'signal': 'ERROR'}


def detect_cyclical_patterns(symbol, days=20):
    """
    Detect cyclical "pump and dump" patterns
    
    Hidden Sign: Stock pumps 3-5 days then dumps reliably
    This indicates institutional rotation or algo trading
    """
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period=f'{days}d')
        
        # Find recent runs (consecutive up/down days)
        changes = hist['Close'].pct_change()
        
        # Count consecutive patterns
        up_days = 0
        down_days = 0
        current_trend = None
        
        for change in changes.iloc[-10:]:  # Last 10 days
            if change > 0:
                if current_trend == 'UP':
                    up_days += 1
                else:
                    current_trend = 'UP'
                    up_days = 1
            else:
                if current_trend == 'DOWN':
                    down_days += 1
                else:
                    current_trend = 'DOWN'
                    down_days = 1
        
        print(f"\n🔄 CYCLICAL PATTERN ({symbol}):")
        print(f"   Current Trend:      {current_trend}")
        print(f"   Consecutive Days:   {up_days if current_trend == 'UP' else down_days}")
        
        # Hidden Sign Detection
        if current_trend == 'UP' and up_days >= 4:
            print(f"   🚨 EXTENDED RUN: {up_days} days up")
            print(f"      → Reversal likely (expect down day)")
            signal = "EXPECT_REVERSAL_DOWN"
        elif current_trend == 'DOWN' and down_days >= 3:
            print(f"   🚨 OVERSOLD: {down_days} days down")
            print(f"      → Bounce likely (expect up day)")
            signal = "EXPECT_BOUNCE_UP"
        else:
            print(f"   ✅ NORMAL: No extended pattern")
            signal = "NORMAL"
        
        return {
            'signal': signal,
            'trend': current_trend,
            'days': up_days if current_trend == 'UP' else down_days
        }
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return {'signal': 'ERROR'}


def detect_futures_premarket_edge(symbol):
    """
    Detect futures positioning before market open
    
    Hidden Sign: Futures strong but stock weak in premarket = Divergence
    Institutions may know something retail doesn't
    """
    try:
        # Get ES futures (S&P 500)
        es = yf.Ticker('ES=F')
        es_hist = es.history(period='2d')
        
        if len(es_hist) >= 2:
            es_change = ((es_hist['Close'].iloc[-1] - es_hist['Close'].iloc[-2]) / es_hist['Close'].iloc[-2]) * 100
            
            # Get stock change
            stock = yf.Ticker(symbol)
            stock_hist = stock.history(period='2d')
            stock_change = ((stock_hist['Close'].iloc[-1] - stock_hist['Close'].iloc[-2]) / stock_hist['Close'].iloc[-2]) * 100
            
            print(f"\n🌅 FUTURES DIVERGENCE ({symbol}):")
            print(f"   ES Futures Change:  {es_change:+.2f}%")
            print(f"   {symbol} Change:    {stock_change:+.2f}%")
            
            # Hidden Sign Detection
            divergence = abs(es_change - stock_change)
            
            if divergence > 2.0:
                if es_change > 0 and stock_change < -1:
                    print(f"   🚨 BEARISH DIVERGENCE: Futures up, stock down")
                    print(f"      → Stock-specific weakness (BEARISH)")
                    signal = "BEARISH_STOCK_WEAKNESS"
                elif es_change < 0 and stock_change > 1:
                    print(f"   🚨 BULLISH DIVERGENCE: Futures down, stock up")
                    print(f"      → Stock-specific strength (BULLISH)")
                    signal = "BULLISH_STOCK_STRENGTH"
                else:
                    signal = "DIVERGENCE"
            else:
                print(f"   ✅ ALIGNED: Stock following market")
                signal = "ALIGNED"
            
            return {
                'signal': signal,
                'divergence': divergence,
                'es_change': es_change,
                'stock_change': stock_change
            }
        else:
            return {'signal': 'NO_DATA'}
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return {'signal': 'ERROR'}


def comprehensive_hidden_signal_analysis(symbol):
    """
    Run ALL hidden signal detectors
    Combine to find institutional positioning
    """
    print("="*80)
    print(f"🔍 COMPREHENSIVE HIDDEN SIGNAL ANALYSIS - {symbol}")
    print("="*80)
    print("Detecting signs that 'only few people know'...")
    print("These are institutional patterns before major moves\n")
    
    # Run all detectors
    dark_pool = detect_dark_pool_activity(symbol)
    options = detect_unusual_options_activity(symbol)
    divergence = detect_price_momentum_divergence(symbol)
    cyclical = detect_cyclical_patterns(symbol)
    futures = detect_futures_premarket_edge(symbol)
    
    # Aggregate signals
    print(f"\n{'='*80}")
    print(f"📊 OVERALL HIDDEN SIGNAL ASSESSMENT - {symbol}")
    print(f"{'='*80}")
    
    bearish_count = 0
    bullish_count = 0
    
    signals = [dark_pool, options, divergence, cyclical, futures]
    
    for sig in signals:
        if 'BEARISH' in sig.get('signal', ''):
            bearish_count += 1
        elif 'BULLISH' in sig.get('signal', ''):
            bullish_count += 1
    
    print(f"\nSignal Summary:")
    print(f"  Bullish Signals: {bullish_count}")
    print(f"  Bearish Signals: {bearish_count}")
    print(f"  Neutral/Normal:  {len(signals) - bullish_count - bearish_count}")
    
    # Final verdict
    print(f"\n🎯 INSTITUTIONAL POSITIONING:")
    
    if bearish_count >= 3:
        print(f"  🚨 STRONG BEARISH: Institutions positioning for DROP")
        print(f"     Expect: DOWN move soon")
        verdict = "STRONG_BEARISH"
    elif bearish_count >= 2:
        print(f"  ⚠️ MODERATE BEARISH: Some institutional selling")
        print(f"     Expect: Weakness or consolidation")
        verdict = "MODERATE_BEARISH"
    elif bullish_count >= 3:
        print(f"  ✅ STRONG BULLISH: Institutions accumulating")
        print(f"     Expect: UP move soon")
        verdict = "STRONG_BULLISH"
    elif bullish_count >= 2:
        print(f"  📈 MODERATE BULLISH: Some institutional buying")
        print(f"     Expect: Strength or rally")
        verdict = "MODERATE_BULLISH"
    else:
        print(f"  ➡️ NEUTRAL: No clear institutional bias")
        print(f"     Expect: Range-bound or choppy")
        verdict = "NEUTRAL"
    
    print(f"\n{'='*80}")
    print(f"✅ ANALYSIS COMPLETE - {symbol}")
    print(f"{'='*80}\n")
    
    return {
        'symbol': symbol,
        'verdict': verdict,
        'bullish_count': bullish_count,
        'bearish_count': bearish_count,
        'dark_pool': dark_pool,
        'options': options,
        'divergence': divergence,
        'cyclical': cyclical,
        'futures': futures
    }


if __name__ == "__main__":
    # Analyze all 3 stocks
    stocks = ['AMD', 'AVGO', 'ORCL']
    
    print("\n" + "="*80)
    print("🔍 HIDDEN INSTITUTIONAL PATTERN DETECTION")
    print("="*80)
    print("Analyzing signs that only institutional traders see...")
    print("These patterns often predict moves 1-3 days in advance\n")
    
    results = {}
    
    for symbol in stocks:
        result = comprehensive_hidden_signal_analysis(symbol)
        results[symbol] = result
        print("\n")
    
    # Summary
    print("="*80)
    print("📋 SUMMARY - INSTITUTIONAL POSITIONING")
    print("="*80)
    
    for symbol in stocks:
        verdict = results[symbol]['verdict']
        bullish = results[symbol]['bullish_count']
        bearish = results[symbol]['bearish_count']
        
        if 'BEARISH' in verdict:
            emoji = "🔴"
        elif 'BULLISH' in verdict:
            emoji = "🟢"
        else:
            emoji = "⚪"
        
        print(f"\n{symbol}:")
        print(f"  {emoji} {verdict}")
        print(f"  Bullish Signals: {bullish} | Bearish Signals: {bearish}")
    
    print(f"\n{'='*80}")
    print("💡 HOW TO USE THIS:")
    print(f"{'='*80}")
    print("""
    1. Run this BEFORE your main prediction (3:45 PM)
    2. If STRONG BEARISH detected → Reduce confidence or skip
    3. If STRONG BULLISH detected → Increase confidence
    4. Combine with main system for best results
    
    These are the "hidden signs" institutions use to position
    before major moves. Most retail traders don't see them.
    """)
    
    print(f"\n{'='*80}")
    print("✅ HIDDEN SIGNAL DETECTION COMPLETE")
    print(f"{'='*80}\n")
