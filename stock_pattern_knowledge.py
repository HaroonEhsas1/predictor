"""
STOCK PATTERN KNOWLEDGE SYSTEM
Tracks what's normal, abnormal, capacity limits, pump/dump patterns for each stock
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
from pathlib import Path
from typing import Dict, Any, List, Tuple


class StockPatternKnowledge:
    """
    Comprehensive pattern knowledge system for each stock
    Knows: normal behavior, abnormal behavior, capacity limits, pump/dump patterns
    """

    def __init__(self, symbol: str):
        self.symbol = symbol.upper()
        self.patterns_file = Path(f"{self.symbol}_patterns.json")
        self.knowledge_file = Path(f"{self.symbol}_knowledge.json")
        self.patterns = {}
        self.knowledge = {}

    def build_comprehensive_knowledge(self, days=180):
        """
        Build comprehensive knowledge base for this stock
        Analyzes: normal behavior, capacity, pump/dump patterns, abnormal signals
        """
        print("\n" + "="*80)
        print(f"🧠 BUILDING COMPREHENSIVE KNOWLEDGE BASE: {self.symbol}")
        print("="*80)

        # Fetch historical data
        ticker = yf.Ticker(self.symbol)
        hist = ticker.history(period=f"{days}d", interval="1d")

        if len(hist) < 30:
            print("❌ Not enough data")
            return None

        print(f"✅ Analyzing {len(hist)} days of data")

        # 1. NORMAL BEHAVIOR ANALYSIS
        print("\n" + "="*80)
        print("📊 1. NORMAL BEHAVIOR ANALYSIS")
        print("="*80)
        normal_behavior = self._analyze_normal_behavior(hist)
        self.knowledge['normal_behavior'] = normal_behavior

        # 2. CAPACITY LIMITS (Max moves)
        print("\n" + "="*80)
        print("📈 2. CAPACITY LIMITS (Max Up/Down Moves)")
        print("="*80)
        capacity = self._analyze_capacity_limits(hist)
        self.knowledge['capacity'] = capacity

        # 3. PUMP PATTERNS
        print("\n" + "="*80)
        print("🚀 3. PUMP PATTERNS (When stock pumps)")
        print("="*80)
        pump_patterns = self._analyze_pump_patterns(hist)
        self.knowledge['pump_patterns'] = pump_patterns

        # 4. DUMP PATTERNS
        print("\n" + "="*80)
        print("📉 4. DUMP PATTERNS (When stock dumps)")
        print("="*80)
        dump_patterns = self._analyze_dump_patterns(hist)
        self.knowledge['dump_patterns'] = dump_patterns

        # 5. ABNORMAL BEHAVIOR DETECTION
        print("\n" + "="*80)
        print("⚠️ 5. ABNORMAL BEHAVIOR DETECTION")
        print("="*80)
        abnormal_signals = self._analyze_abnormal_behavior(hist)
        self.knowledge['abnormal_signals'] = abnormal_signals

        # 6. VOLATILITY REGIMES
        print("\n" + "="*80)
        print("📊 6. VOLATILITY REGIMES")
        print("="*80)
        volatility_regimes = self._analyze_volatility_regimes(hist)
        self.knowledge['volatility_regimes'] = volatility_regimes

        # Save knowledge
        self.save_knowledge()

        # Print summary
        self._print_knowledge_summary()

        return self.knowledge

    def _analyze_normal_behavior(self, hist) -> Dict[str, Any]:
        """Define what's NORMAL for this stock"""

        # Daily moves
        daily_returns = hist['Close'].pct_change().dropna()

        normal = {
            'avg_daily_move': daily_returns.abs().mean() * 100,
            'median_daily_move': daily_returns.abs().median() * 100,
            'std_daily_move': daily_returns.std() * 100,
            'normal_range': {
                'min': daily_returns.quantile(0.25) * 100,  # 25th percentile
                'max': daily_returns.quantile(0.75) * 100,  # 75th percentile
            },
            'typical_up_day': daily_returns[daily_returns > 0].mean() * 100,
            'typical_down_day': daily_returns[daily_returns < 0].mean() * 100,
        }

        # Volume
        normal['avg_volume'] = hist['Volume'].mean()
        normal['normal_volume_range'] = {
            'min': hist['Volume'].quantile(0.25),
            'max': hist['Volume'].quantile(0.75),
        }

        # Intraday range
        intraday_ranges = ((hist['High'] - hist['Low']) / hist['Close']) * 100
        normal['avg_intraday_range'] = intraday_ranges.mean()
        normal['normal_intraday_range'] = {
            'min': intraday_ranges.quantile(0.25),
            'max': intraday_ranges.quantile(0.75),
        }

        print(f"\n✅ {self.symbol} NORMAL BEHAVIOR:")
        print(f"   Average Daily Move: {normal['avg_daily_move']:.2f}%")
        print(
            f"   Normal Range: {normal['normal_range']['min']:.2f}% to {normal['normal_range']['max']:.2f}%")
        print(f"   Typical Up Day: +{normal['typical_up_day']:.2f}%")
        print(f"   Typical Down Day: {normal['typical_down_day']:.2f}%")
        print(
            f"   Average Intraday Range: {normal['avg_intraday_range']:.2f}%")
        print(
            f"   Normal Volume: {normal['normal_volume_range']['min']/1e6:.1f}M to {normal['normal_volume_range']['max']/1e6:.1f}M")

        return normal

    def _analyze_capacity_limits(self, hist) -> Dict[str, Any]:
        """Find MAX capacity for up/down moves"""

        daily_returns = hist['Close'].pct_change().dropna() * 100

        capacity = {
            'max_up_move': daily_returns.max(),
            'max_down_move': daily_returns.min(),
            'p95_up_move': daily_returns.quantile(0.95),  # 95th percentile
            'p95_down_move': daily_returns.quantile(0.05),  # 5th percentile
            # 99th percentile (extreme)
            'p99_up_move': daily_returns.quantile(0.99),
            # 1st percentile (extreme)
            'p99_down_move': daily_returns.quantile(0.01),
            'typical_max_up': daily_returns[daily_returns > 0].quantile(0.90),
            'typical_max_down': daily_returns[daily_returns < 0].quantile(0.10),
        }

        # Overnight gaps
        gaps = []
        for i in range(1, len(hist)):
            gap = ((hist['Open'].iloc[i] - hist['Close'].iloc[i-1]
                    ) / hist['Close'].iloc[i-1]) * 100
            gaps.append(gap)

        gaps = pd.Series(gaps)
        capacity['max_overnight_gap_up'] = gaps.max()
        capacity['max_overnight_gap_down'] = gaps.min()
        capacity['p95_gap_up'] = gaps.quantile(0.95)
        capacity['p95_gap_down'] = gaps.quantile(0.05)

        print(f"\n📈 {self.symbol} CAPACITY LIMITS:")
        print(f"   Max Up Move (Historical): +{capacity['max_up_move']:.2f}%")
        print(
            f"   Max Down Move (Historical): {capacity['max_down_move']:.2f}%")
        print(f"   95th Percentile Up: +{capacity['p95_up_move']:.2f}%")
        print(f"   95th Percentile Down: {capacity['p95_down_move']:.2f}%")
        print(f"   Typical Max Up: +{capacity['typical_max_up']:.2f}%")
        print(f"   Typical Max Down: {capacity['typical_max_down']:.2f}%")
        print(
            f"   Max Overnight Gap Up: +{capacity['max_overnight_gap_up']:.2f}%")
        print(
            f"   Max Overnight Gap Down: {capacity['max_overnight_gap_down']:.2f}%")

        return capacity

    def _analyze_pump_patterns(self, hist) -> Dict[str, Any]:
        """Find when and why this stock PUMPS"""

        pumps = []
        pump_conditions = []

        for i in range(5, len(hist)):
            # Look for 3+ day runs
            recent_returns = hist['Close'].iloc[i-3:i+1].pct_change().dropna()

            if len(recent_returns) >= 3 and all(recent_returns > 0):
                total_move = (
                    (hist['Close'].iloc[i] - hist['Close'].iloc[i-3]) / hist['Close'].iloc[i-3]) * 100

                if total_move > 5.0:  # Significant pump (5%+ in 3 days)
                    pumps.append({
                        'date': hist.index[i].strftime('%Y-%m-%d'),
                        'total_move': total_move,
                        'volume_ratio': hist['Volume'].iloc[i] / hist['Volume'].iloc[i-10:i].mean(),
                        'rsi': self._calculate_rsi(hist['Close'].iloc[i-14:i+1]) if i >= 14 else 50,
                    })

        pump_patterns = {
            'total_pumps': len(pumps),
            'avg_pump_size': np.mean([p['total_move'] for p in pumps]) if pumps else 0,
            'max_pump_size': max([p['total_move'] for p in pumps]) if pumps else 0,
            'pump_volume_ratio': np.mean([p['volume_ratio'] for p in pumps]) if pumps else 1.0,
            'pump_rsi_avg': np.mean([p['rsi'] for p in pumps]) if pumps else 50,
        }

        # Analyze pump conditions
        if pumps:
            high_volume_pumps = [p for p in pumps if p['volume_ratio'] > 1.5]
            low_rsi_pumps = [p for p in pumps if p['rsi'] < 50]

            pump_patterns['high_volume_pump_rate'] = len(
                high_volume_pumps) / len(pumps)
            pump_patterns['low_rsi_pump_rate'] = len(
                low_rsi_pumps) / len(pumps)
            pump_patterns['pump_triggers'] = {
                'high_volume': len(high_volume_pumps) / len(pumps) > 0.6,
                'oversold_bounce': len(low_rsi_pumps) / len(pumps) > 0.5,
            }

        print(f"\n🚀 {self.symbol} PUMP PATTERNS:")
        print(
            f"   Total Pumps (5%+ in 3 days): {pump_patterns['total_pumps']}")
        if pumps:
            print(
                f"   Average Pump Size: +{pump_patterns['avg_pump_size']:.2f}%")
            print(f"   Max Pump Size: +{pump_patterns['max_pump_size']:.2f}%")
            print(
                f"   Average Volume Ratio: {pump_patterns['pump_volume_ratio']:.2f}x")
            if pump_patterns.get('high_volume_pump_rate', 0) > 0.6:
                print(
                    f"   ✅ Pumps usually have HIGH VOLUME ({pump_patterns['high_volume_pump_rate']*100:.0f}%)")
            if pump_patterns.get('low_rsi_pump_rate', 0) > 0.5:
                print(
                    f"   ✅ Pumps often start from OVERSOLD ({pump_patterns['low_rsi_pump_rate']*100:.0f}%)")

        return pump_patterns

    def _analyze_dump_patterns(self, hist) -> Dict[str, Any]:
        """Find when and why this stock DUMPS"""

        dumps = []

        for i in range(5, len(hist)):
            # Look for 3+ day drops
            recent_returns = hist['Close'].iloc[i-3:i+1].pct_change().dropna()

            if len(recent_returns) >= 3 and all(recent_returns < 0):
                total_move = (
                    (hist['Close'].iloc[i] - hist['Close'].iloc[i-3]) / hist['Close'].iloc[i-3]) * 100

                if total_move < -5.0:  # Significant dump (-5%+ in 3 days)
                    dumps.append({
                        'date': hist.index[i].strftime('%Y-%m-%d'),
                        'total_move': total_move,
                        'volume_ratio': hist['Volume'].iloc[i] / hist['Volume'].iloc[i-10:i].mean(),
                        'rsi': self._calculate_rsi(hist['Close'].iloc[i-14:i+1]) if i >= 14 else 50,
                    })

        dump_patterns = {
            'total_dumps': len(dumps),
            'avg_dump_size': np.mean([abs(d['total_move']) for d in dumps]) if dumps else 0,
            'max_dump_size': abs(min([d['total_move'] for d in dumps])) if dumps else 0,
            'dump_volume_ratio': np.mean([d['volume_ratio'] for d in dumps]) if dumps else 1.0,
            'dump_rsi_avg': np.mean([d['rsi'] for d in dumps]) if dumps else 50,
        }

        # Analyze dump conditions
        if dumps:
            high_volume_dumps = [d for d in dumps if d['volume_ratio'] > 1.5]
            high_rsi_dumps = [d for d in dumps if d['rsi'] > 60]

            dump_patterns['high_volume_dump_rate'] = len(
                high_volume_dumps) / len(dumps)
            dump_patterns['high_rsi_dump_rate'] = len(
                high_rsi_dumps) / len(dumps)
            dump_patterns['dump_triggers'] = {
                'high_volume': len(high_volume_dumps) / len(dumps) > 0.6,
                'overbought_reversal': len(high_rsi_dumps) / len(dumps) > 0.5,
            }

        print(f"\n📉 {self.symbol} DUMP PATTERNS:")
        print(
            f"   Total Dumps (-5%+ in 3 days): {dump_patterns['total_dumps']}")
        if dumps:
            print(
                f"   Average Dump Size: {dump_patterns['avg_dump_size']:.2f}%")
            print(f"   Max Dump Size: {dump_patterns['max_dump_size']:.2f}%")
            print(
                f"   Average Volume Ratio: {dump_patterns['dump_volume_ratio']:.2f}x")
            if dump_patterns.get('high_volume_dump_rate', 0) > 0.6:
                print(
                    f"   ⚠️ Dumps usually have HIGH VOLUME ({dump_patterns['high_volume_dump_rate']*100:.0f}%)")
            if dump_patterns.get('high_rsi_dump_rate', 0) > 0.5:
                print(
                    f"   ⚠️ Dumps often start from OVERBOUGHT ({dump_patterns['high_rsi_dump_rate']*100:.0f}%)")

        return dump_patterns

    def _analyze_abnormal_behavior(self, hist) -> Dict[str, Any]:
        """Detect what's ABNORMAL for this stock"""

        daily_returns = hist['Close'].pct_change().dropna() * 100
        volumes = hist['Volume']

        # Define abnormal thresholds (2 standard deviations)
        abnormal = {
            'abnormal_up_threshold': daily_returns.mean() + (2 * daily_returns.std()),
            'abnormal_down_threshold': daily_returns.mean() - (2 * daily_returns.std()),
            'abnormal_volume_threshold': volumes.mean() + (2 * volumes.std()),
            'abnormal_low_volume_threshold': volumes.mean() - (2 * volumes.std()),
        }

        # Count abnormal events
        abnormal_up_days = len(
            daily_returns[daily_returns > abnormal['abnormal_up_threshold']])
        abnormal_down_days = len(
            daily_returns[daily_returns < abnormal['abnormal_down_threshold']])
        abnormal_volume_days = len(
            volumes[volumes > abnormal['abnormal_volume_threshold']])

        abnormal['abnormal_up_frequency'] = abnormal_up_days / \
            len(daily_returns)
        abnormal['abnormal_down_frequency'] = abnormal_down_days / \
            len(daily_returns)
        abnormal['abnormal_volume_frequency'] = abnormal_volume_days / \
            len(volumes)

        print(f"\n⚠️ {self.symbol} ABNORMAL BEHAVIOR THRESHOLDS:")
        print(
            f"   Abnormal Up Move: >+{abnormal['abnormal_up_threshold']:.2f}%")
        print(
            f"   Abnormal Down Move: <{abnormal['abnormal_down_threshold']:.2f}%")
        print(
            f"   Abnormal Volume: >{abnormal['abnormal_volume_threshold']/1e6:.1f}M")
        print(
            f"   Abnormal Low Volume: <{abnormal['abnormal_low_volume_threshold']/1e6:.1f}M")
        print(
            f"   Frequency of Abnormal Up: {abnormal['abnormal_up_frequency']*100:.1f}%")
        print(
            f"   Frequency of Abnormal Down: {abnormal['abnormal_down_frequency']*100:.1f}%")

        return abnormal

    def _analyze_volatility_regimes(self, hist) -> Dict[str, Any]:
        """Identify different volatility regimes"""

        daily_returns = hist['Close'].pct_change().dropna() * 100

        # Calculate rolling volatility (20-day)
        rolling_vol = daily_returns.rolling(20).std()

        low_vol_threshold = rolling_vol.quantile(0.33)
        high_vol_threshold = rolling_vol.quantile(0.67)

        regimes = {
            'low_volatility_threshold': low_vol_threshold,
            'high_volatility_threshold': high_vol_threshold,
            'current_regime': 'medium',
        }

        if len(rolling_vol) > 0:
            current_vol = rolling_vol.iloc[-1]
            if current_vol < low_vol_threshold:
                regimes['current_regime'] = 'low'
            elif current_vol > high_vol_threshold:
                regimes['current_regime'] = 'high'

        print(f"\n📊 {self.symbol} VOLATILITY REGIMES:")
        print(
            f"   Low Volatility: <{regimes['low_volatility_threshold']:.2f}%")
        print(
            f"   High Volatility: >{regimes['high_volatility_threshold']:.2f}%")
        print(f"   Current Regime: {regimes['current_regime'].upper()}")

        return regimes

    def _calculate_rsi(self, prices, period=14):
        """Calculate RSI"""
        if len(prices) < period + 1:
            return 50

        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50

    def _print_knowledge_summary(self):
        """Print comprehensive knowledge summary"""

        print("\n" + "="*80)
        print(f"🎯 {self.symbol} COMPREHENSIVE KNOWLEDGE SUMMARY")
        print("="*80)

        normal = self.knowledge.get('normal_behavior', {})
        capacity = self.knowledge.get('capacity', {})
        pumps = self.knowledge.get('pump_patterns', {})
        dumps = self.knowledge.get('dump_patterns', {})
        abnormal = self.knowledge.get('abnormal_signals', {})

        print(f"\n📊 WHAT'S NORMAL:")
        print(
            f"   Daily Move: {normal.get('avg_daily_move', 0):.2f}% (typical)")
        print(
            f"   Normal Range: {normal.get('normal_range', {}).get('min', 0):.2f}% to {normal.get('normal_range', {}).get('max', 0):.2f}%")

        print(f"\n📈 CAPACITY LIMITS:")
        print(f"   Max Realistic Up: +{capacity.get('p95_up_move', 0):.2f}%")
        print(
            f"   Max Realistic Down: {capacity.get('p95_down_move', 0):.2f}%")
        print(f"   Extreme Up: +{capacity.get('p99_up_move', 0):.2f}%")
        print(f"   Extreme Down: {capacity.get('p99_down_move', 0):.2f}%")

        print(f"\n🚀 WHEN IT PUMPS:")
        if pumps.get('total_pumps', 0) > 0:
            print(f"   Average Pump: +{pumps.get('avg_pump_size', 0):.2f}%")
            print(f"   Max Pump: +{pumps.get('max_pump_size', 0):.2f}%")
            if pumps.get('pump_triggers', {}).get('high_volume', False):
                print(f"   ✅ Usually pumps on HIGH VOLUME")
            if pumps.get('pump_triggers', {}).get('oversold_bounce', False):
                print(f"   ✅ Often pumps from OVERSOLD (RSI < 50)")

        print(f"\n📉 WHEN IT DUMPS:")
        if dumps.get('total_dumps', 0) > 0:
            print(f"   Average Dump: {dumps.get('avg_dump_size', 0):.2f}%")
            print(f"   Max Dump: {dumps.get('max_dump_size', 0):.2f}%")
            if dumps.get('dump_triggers', {}).get('high_volume', False):
                print(f"   ⚠️ Usually dumps on HIGH VOLUME")
            if dumps.get('dump_triggers', {}).get('overbought_reversal', False):
                print(f"   ⚠️ Often dumps from OVERBOUGHT (RSI > 60)")

        print(f"\n⚠️ WHAT'S ABNORMAL:")
        print(
            f"   Abnormal Up: >+{abnormal.get('abnormal_up_threshold', 0):.2f}%")
        print(
            f"   Abnormal Down: <{abnormal.get('abnormal_down_threshold', 0):.2f}%")
        print(
            f"   Abnormal Volume: >{abnormal.get('abnormal_volume_threshold', 0)/1e6:.1f}M")

        print("\n" + "="*80 + "\n")

    def save_knowledge(self):
        """Save knowledge to JSON file"""
        with open(self.knowledge_file, 'w') as f:
            json.dump(self.knowledge, f, indent=2, default=str)
        print(f"\n✅ Saved {self.symbol} knowledge to {self.knowledge_file}")

    def load_knowledge(self) -> Dict[str, Any]:
        """Load knowledge from JSON file"""
        if self.knowledge_file.exists():
            with open(self.knowledge_file, 'r') as f:
                self.knowledge = json.load(f)
            return self.knowledge
        return None

    def is_abnormal_move(self, move_pct: float) -> Tuple[bool, str]:
        """Check if a move is abnormal for this stock"""
        if not self.knowledge:
            self.load_knowledge()

        if not self.knowledge:
            return False, "No knowledge available"

        abnormal = self.knowledge.get('abnormal_signals', {})
        up_threshold = abnormal.get('abnormal_up_threshold', 999)
        down_threshold = abnormal.get('abnormal_down_threshold', -999)

        if move_pct > up_threshold:
            return True, f"ABNORMAL UP: {move_pct:.2f}% > {up_threshold:.2f}%"
        elif move_pct < down_threshold:
            return True, f"ABNORMAL DOWN: {move_pct:.2f}% < {down_threshold:.2f}%"

        return False, "NORMAL"

    def get_capacity_estimate(self, direction: str = 'up') -> float:
        """Get realistic capacity estimate for move"""
        if not self.knowledge:
            self.load_knowledge()

        if not self.knowledge:
            return 0.0

        capacity = self.knowledge.get('capacity', {})
        if direction.lower() == 'up':
            return capacity.get('p95_up_move', 0.0)
        else:
            return capacity.get('p95_down_move', 0.0)

    def is_pump_likely(self, current_conditions: Dict[str, Any]) -> Tuple[bool, float]:
        """Check if pump is likely based on current conditions"""
        if not self.knowledge:
            self.load_knowledge()

        if not self.knowledge:
            return False, 0.0

        pumps = self.knowledge.get('pump_patterns', {})
        triggers = pumps.get('pump_triggers', {})

        score = 0.0

        # Check volume
        if current_conditions.get('volume_ratio', 1.0) > 1.5 and triggers.get('high_volume', False):
            score += 0.4

        # Check RSI
        if current_conditions.get('rsi', 50) < 50 and triggers.get('oversold_bounce', False):
            score += 0.4

        # Check if in normal range (not already pumped)
        normal = self.knowledge.get('normal_behavior', {})
        recent_move = current_conditions.get('recent_move_pct', 0)
        if abs(recent_move) < normal.get('avg_daily_move', 2.0):
            score += 0.2

        return score > 0.5, score

    def is_dump_likely(self, current_conditions: Dict[str, Any]) -> Tuple[bool, float]:
        """Check if dump is likely based on current conditions"""
        if not self.knowledge:
            self.load_knowledge()

        if not self.knowledge:
            return False, 0.0

        dumps = self.knowledge.get('dump_patterns', {})
        triggers = dumps.get('dump_triggers', {})

        score = 0.0

        # Check volume
        if current_conditions.get('volume_ratio', 1.0) > 1.5 and triggers.get('high_volume', False):
            score += 0.4

        # Check RSI
        if current_conditions.get('rsi', 50) > 60 and triggers.get('overbought_reversal', False):
            score += 0.4

        # Check if extended up
        normal = self.knowledge.get('normal_behavior', {})
        recent_move = current_conditions.get('recent_move_pct', 0)
        if recent_move > normal.get('avg_daily_move', 2.0) * 2:
            score += 0.2

        return score > 0.5, score


if __name__ == "__main__":
    # Build knowledge for AMD and NVDA
    symbols = ['AMD', 'NVDA']

    for symbol in symbols:
        knowledge_system = StockPatternKnowledge(symbol)
        knowledge_system.build_comprehensive_knowledge(days=180)
        print(f"\n✅ {symbol} knowledge complete!\n")
