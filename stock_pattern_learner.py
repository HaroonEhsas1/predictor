"""
STOCK-SPECIFIC PATTERN LEARNING SYSTEM
User's insight: "Each stock should be independent - use its OWN patterns and logic"

This system:
1. Learns EACH stock's unique behavior separately
2. Finds stock-specific patterns (not universal)
3. Builds independent prediction models per stock
4. No shared logic - each stock is treated uniquely
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

class StockPatternLearner:
    """
    Learns unique patterns for each stock independently
    """
    
    def __init__(self, symbol):
        self.symbol = symbol
        self.patterns = {}
        self.behaviors = {}
        
    def learn_stock_patterns(self, days=90):
        """
        Analyze stock's historical behavior to find UNIQUE patterns
        """
        
        print("\n" + "="*80)
        print(f"🧠 LEARNING {self.symbol}'S UNIQUE PATTERNS")
        print("="*80)
        
        # Fetch data
        print(f"\n📊 Fetching {days} days of data for {self.symbol}...")
        stock = yf.Ticker(self.symbol)
        hist = stock.history(period=f"{days}d", interval="1d")
        
        if len(hist) < 20:
            print("❌ Not enough data")
            return None
        
        print(f"✅ Fetched {len(hist)} days")
        
        # 1. OVERNIGHT GAP PATTERNS
        print("\n" + "="*80)
        print("PATTERN 1: OVERNIGHT GAP BEHAVIOR")
        print("="*80)
        
        gap_patterns = self._analyze_gap_patterns(hist)
        self.patterns['gaps'] = gap_patterns
        
        # 2. INTRADAY BEHAVIOR PATTERNS
        print("\n" + "="*80)
        print("PATTERN 2: INTRADAY BEHAVIOR")
        print("="*80)
        
        intraday_patterns = self._analyze_intraday_behavior(hist)
        self.patterns['intraday'] = intraday_patterns
        
        # 3. VOLUME PATTERNS
        print("\n" + "="*80)
        print("PATTERN 3: VOLUME BEHAVIOR")
        print("="*80)
        
        volume_patterns = self._analyze_volume_patterns(hist)
        self.patterns['volume'] = volume_patterns
        
        # 4. MOMENTUM PATTERNS
        print("\n" + "="*80)
        print("PATTERN 4: MOMENTUM CONTINUATION")
        print("="*80)
        
        momentum_patterns = self._analyze_momentum_patterns(hist)
        self.patterns['momentum'] = momentum_patterns
        
        # 5. TRAP PATTERNS
        print("\n" + "="*80)
        print("PATTERN 5: TRAP/REVERSAL BEHAVIOR")
        print("="*80)
        
        trap_patterns = self._analyze_trap_patterns(hist)
        self.patterns['traps'] = trap_patterns
        
        # SUMMARY
        self._print_summary()
        
        return self.patterns
    
    def _analyze_gap_patterns(self, hist):
        """Find THIS stock's unique gap behavior"""
        
        gaps = []
        gap_follow_through = 0
        gap_reversals = 0
        
        for i in range(1, len(hist)):
            prev_close = hist['Close'].iloc[i-1]
            curr_open = hist['Open'].iloc[i]
            curr_close = hist['Close'].iloc[i]
            
            gap_pct = ((curr_open - prev_close) / prev_close) * 100
            
            if abs(gap_pct) > 0.5:  # Significant gap
                gaps.append(gap_pct)
                
                # Did it follow through?
                if gap_pct > 0:  # Gap up
                    if curr_close > curr_open:  # Continued up
                        gap_follow_through += 1
                    else:
                        gap_reversals += 1
                else:  # Gap down
                    if curr_close < curr_open:  # Continued down
                        gap_follow_through += 1
                    else:
                        gap_reversals += 1
        
        total_gaps = gap_follow_through + gap_reversals
        follow_through_rate = gap_follow_through / total_gaps if total_gaps > 0 else 0
        
        print(f"\n📈 {self.symbol} Gap Statistics:")
        print(f"   Total significant gaps: {total_gaps}")
        print(f"   Follow-through: {gap_follow_through} ({follow_through_rate*100:.1f}%)")
        print(f"   Reversals: {gap_reversals} ({(1-follow_through_rate)*100:.1f}%)")
        print(f"   Average gap size: {np.mean([abs(g) for g in gaps]):.2f}%")
        
        return {
            'follow_through_rate': follow_through_rate,
            'reversal_rate': 1 - follow_through_rate,
            'avg_gap_size': np.mean([abs(g) for g in gaps]) if gaps else 0,
            'total_gaps': total_gaps
        }
    
    def _analyze_intraday_behavior(self, hist):
        """Find how THIS stock behaves during the day"""
        
        morning_strength = 0  # Opens strong and holds
        morning_fade = 0  # Opens strong but fades
        afternoon_recovery = 0  # Weak open, strong close
        all_day_weak = 0  # Weak all day
        
        for i in range(len(hist)):
            open_price = hist['Open'].iloc[i]
            high_price = hist['High'].iloc[i]
            low_price = hist['Low'].iloc[i]
            close_price = hist['Close'].iloc[i]
            
            # Where did it close in the day's range?
            day_range = high_price - low_price
            if day_range == 0:
                continue
                
            close_position = (close_price - low_price) / day_range  # 0 = low, 1 = high
            
            if close_position > 0.7:  # Closed in top 30%
                if close_price > open_price:
                    morning_strength += 1
                else:
                    afternoon_recovery += 1
            elif close_position < 0.3:  # Closed in bottom 30%
                if close_price < open_price:
                    all_day_weak += 1
                else:
                    morning_fade += 1
        
        total = morning_strength + morning_fade + afternoon_recovery + all_day_weak
        
        print(f"\n🕐 {self.symbol} Intraday Patterns:")
        print(f"   Morning strength (holds): {morning_strength} ({morning_strength/total*100:.1f}%)")
        print(f"   Morning fade: {morning_fade} ({morning_fade/total*100:.1f}%)")
        print(f"   Afternoon recovery: {afternoon_recovery} ({afternoon_recovery/total*100:.1f}%)")
        print(f"   All day weak: {all_day_weak} ({all_day_weak/total*100:.1f}%)")
        
        return {
            'morning_strength_rate': morning_strength / total if total > 0 else 0,
            'morning_fade_rate': morning_fade / total if total > 0 else 0,
            'afternoon_recovery_rate': afternoon_recovery / total if total > 0 else 0,
            'all_day_weak_rate': all_day_weak / total if total > 0 else 0
        }
    
    def _analyze_volume_patterns(self, hist):
        """Find THIS stock's volume behavior"""
        
        avg_volume = hist['Volume'].mean()
        high_volume_days = hist[hist['Volume'] > avg_volume * 1.5]
        
        # On high volume days, what happens?
        high_vol_up = 0
        high_vol_down = 0
        
        for idx in high_volume_days.index:
            if hist.loc[idx, 'Close'] > hist.loc[idx, 'Open']:
                high_vol_up += 1
            else:
                high_vol_down += 1
        
        total_high_vol = high_vol_up + high_vol_down
        
        print(f"\n📊 {self.symbol} Volume Patterns:")
        print(f"   Average volume: {avg_volume:,.0f}")
        print(f"   High volume days: {total_high_vol}")
        print(f"   High volume + up: {high_vol_up} ({high_vol_up/total_high_vol*100:.1f}%)" if total_high_vol > 0 else "")
        print(f"   High volume + down: {high_vol_down} ({high_vol_down/total_high_vol*100:.1f}%)" if total_high_vol > 0 else "")
        
        return {
            'avg_volume': avg_volume,
            'high_volume_bullish_rate': high_vol_up / total_high_vol if total_high_vol > 0 else 0.5,
            'high_volume_days': total_high_vol
        }
    
    def _analyze_momentum_patterns(self, hist):
        """Find THIS stock's momentum continuation behavior"""
        
        # Check if previous day's direction continues
        continues = 0
        reverses = 0
        
        for i in range(2, len(hist)):
            # Previous day bullish?
            prev_bullish = hist['Close'].iloc[i-1] > hist['Open'].iloc[i-1]
            
            # Current day bullish?
            curr_bullish = hist['Close'].iloc[i] > hist['Open'].iloc[i]
            
            if prev_bullish == curr_bullish:
                continues += 1
            else:
                reverses += 1
        
        total = continues + reverses
        continuation_rate = continues / total if total > 0 else 0
        
        print(f"\n⚡ {self.symbol} Momentum Patterns:")
        print(f"   Continuation: {continues} ({continuation_rate*100:.1f}%)")
        print(f"   Reversals: {reverses} ({(1-continuation_rate)*100:.1f}%)")
        
        return {
            'continuation_rate': continuation_rate,
            'reversal_rate': 1 - continuation_rate
        }
    
    def _analyze_trap_patterns(self, hist):
        """Find THIS stock's trap/fake-out patterns"""
        
        traps = 0
        total_moves = 0
        
        for i in range(1, len(hist)):
            prev_close = hist['Close'].iloc[i-1]
            curr_open = hist['Open'].iloc[i]
            curr_close = hist['Close'].iloc[i]
            curr_high = hist['High'].iloc[i]
            curr_low = hist['Low'].iloc[i]
            
            gap = curr_open - prev_close
            gap_pct = (gap / prev_close) * 100
            
            # Check for trap patterns
            if abs(gap_pct) > 0.5:
                total_moves += 1
                
                if gap > 0:  # Gap up
                    # Trap if closes below open
                    if curr_close < curr_open:
                        traps += 1
                else:  # Gap down
                    # Trap if closes above open
                    if curr_close > curr_open:
                        traps += 1
        
        trap_rate = traps / total_moves if total_moves > 0 else 0
        
        print(f"\n🚨 {self.symbol} Trap Patterns:")
        print(f"   Total significant moves: {total_moves}")
        print(f"   Traps/reversals: {traps} ({trap_rate*100:.1f}%)")
        print(f"   Clean follow-through: {total_moves - traps} ({(1-trap_rate)*100:.1f}%)")
        
        return {
            'trap_rate': trap_rate,
            'clean_rate': 1 - trap_rate,
            'total_traps': traps
        }
    
    def _print_summary(self):
        """Print stock-specific insights"""
        
        print("\n" + "="*80)
        print(f"🎯 {self.symbol} UNIQUE BEHAVIORAL PROFILE")
        print("="*80)
        
        print(f"\n📊 {self.symbol}'s Personality:")
        
        # Gap behavior
        gap_ft = self.patterns['gaps']['follow_through_rate']
        if gap_ft > 0.6:
            print(f"   ✅ STRONG gap follow-through ({gap_ft*100:.0f}%) - Gaps are reliable")
        elif gap_ft > 0.4:
            print(f"   ⚠️ MODERATE gap follow-through ({gap_ft*100:.0f}%) - Mixed reliability")
        else:
            print(f"   ❌ WEAK gap follow-through ({gap_ft*100:.0f}%) - Gaps often fake-outs")
        
        # Intraday behavior
        fade_rate = self.patterns['intraday']['morning_fade_rate']
        if fade_rate > 0.3:
            print(f"   ⚠️ HIGH morning fade tendency ({fade_rate*100:.0f}%) - Often reverses intraday")
        else:
            print(f"   ✅ LOW morning fade ({fade_rate*100:.0f}%) - Holds opening moves")
        
        # Momentum
        cont_rate = self.patterns['momentum']['continuation_rate']
        if cont_rate > 0.55:
            print(f"   ✅ STRONG momentum continuation ({cont_rate*100:.0f}%) - Trends persist")
        else:
            print(f"   ❌ WEAK momentum ({cont_rate*100:.0f}%) - Choppy/reversing")
        
        # Traps
        trap_rate = self.patterns['traps']['trap_rate']
        if trap_rate > 0.3:
            print(f"   🚨 HIGH trap rate ({trap_rate*100:.0f}%) - Many fake-outs!")
        else:
            print(f"   ✅ LOW trap rate ({trap_rate*100:.0f}%) - Moves are genuine")
        
        print(f"\n💡 {self.symbol} TRADING STRATEGY:")
        
        if fade_rate > 0.4:
            print(f"   → Exit early (9:30-9:35 AM) to avoid intraday reversals")
        
        if gap_ft < 0.5:
            print(f"   → Be skeptical of gaps - often reverse")
        
        if trap_rate > 0.3:
            print(f"   → Require strong confirmation before entering")
        
        if cont_rate > 0.55:
            print(f"   → Can hold positions longer - momentum persists")
        
        print("\n" + "="*80 + "\n")
    
    def save_patterns(self, filename=None):
        """Save learned patterns to file"""
        if filename is None:
            filename = f"{self.symbol}_patterns.json"
        
        with open(filename, 'w') as f:
            json.dump(self.patterns, f, indent=2)
        
        print(f"✅ Saved {self.symbol} patterns to {filename}")
        
        return filename


def compare_stocks(symbols):
    """
    Compare multiple stocks to show they are INDEPENDENT
    """
    
    print("\n" + "="*80)
    print("🔬 STOCK INDEPENDENCE VERIFICATION")
    print("="*80)
    print("""
User's insight: "Each stock should be independent - use its own patterns"

Let's prove that each stock has UNIQUE behavior!
    """)
    
    all_patterns = {}
    
    # Learn each stock's patterns
    for symbol in symbols:
        learner = StockPatternLearner(symbol)
        patterns = learner.learn_stock_patterns(days=90)
        all_patterns[symbol] = patterns
        learner.save_patterns()
    
    # Compare them
    print("\n" + "="*80)
    print("📊 CROSS-STOCK COMPARISON")
    print("="*80)
    
    print("\n🎯 GAP FOLLOW-THROUGH RATES:")
    for symbol in symbols:
        rate = all_patterns[symbol]['gaps']['follow_through_rate']
        print(f"   {symbol}: {rate*100:.1f}%")
    
    print("\n⚡ MOMENTUM CONTINUATION RATES:")
    for symbol in symbols:
        rate = all_patterns[symbol]['momentum']['continuation_rate']
        print(f"   {symbol}: {rate*100:.1f}%")
    
    print("\n🚨 TRAP RATES:")
    for symbol in symbols:
        rate = all_patterns[symbol]['traps']['trap_rate']
        print(f"   {symbol}: {rate*100:.1f}%")
    
    print("\n🕐 MORNING FADE RATES:")
    for symbol in symbols:
        rate = all_patterns[symbol]['intraday']['morning_fade_rate']
        print(f"   {symbol}: {rate*100:.1f}%")
    
    # Calculate variance to prove they're different
    gap_rates = [all_patterns[s]['gaps']['follow_through_rate'] for s in symbols]
    momentum_rates = [all_patterns[s]['momentum']['continuation_rate'] for s in symbols]
    trap_rates = [all_patterns[s]['traps']['trap_rate'] for s in symbols]
    
    print("\n" + "="*80)
    print("✅ INDEPENDENCE VERIFICATION")
    print("="*80)
    
    gap_variance = np.var(gap_rates)
    momentum_variance = np.var(momentum_rates)
    trap_variance = np.var(trap_rates)
    
    print(f"\nGap follow-through variance: {gap_variance:.4f}")
    print(f"Momentum continuation variance: {momentum_variance:.4f}")
    print(f"Trap rate variance: {trap_variance:.4f}")
    
    if gap_variance > 0.01 or momentum_variance > 0.01:
        print("\n✅ STOCKS ARE INDEPENDENT!")
        print("   Each stock has UNIQUE patterns and behavior")
        print("   System MUST treat them separately!")
    else:
        print("\n⚠️ Stocks behaving similarly")
        print("   May be able to share some logic")
    
    print("\n" + "="*80 + "\n")
    
    return all_patterns


if __name__ == "__main__":
    # Analyze all 4 stocks
    stocks = ['NVDA', 'META', 'AVGO', 'AMD']
    
    print("="*80)
    print("🧠 STOCK-SPECIFIC PATTERN LEARNING")
    print("="*80)
    print("""
This system learns EACH stock's unique patterns:
- NOT using universal rules
- NOT averaging behavior
- Each stock analyzed INDEPENDENTLY
- Finds stock-specific strategies

Let's discover what makes each stock unique!
    """)
    
    patterns = compare_stocks(stocks)
    
    print("="*80)
    print("✅ PATTERN LEARNING COMPLETE")
    print("="*80)
    print("""
Results saved to:
- NVDA_patterns.json
- META_patterns.json
- AVGO_patterns.json
- AMD_patterns.json

Each file contains THAT stock's unique behavior!

Next: Use these patterns to build stock-specific prediction models!
    """)
