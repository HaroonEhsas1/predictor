"""
REAL-TIME PATTERN DETECTOR
Uses stock pattern knowledge to detect normal/abnormal behavior, pump/dump signals in real-time
"""

import yfinance as yf
import pandas as pd
from stock_pattern_knowledge import StockPatternKnowledge
from typing import Dict, Any, Tuple


class RealTimePatternDetector:
    """
    Real-time pattern detection using stock knowledge base
    Detects: normal vs abnormal, capacity limits, pump/dump signals
    """

    def __init__(self, symbol: str):
        self.symbol = symbol.upper()
        self.knowledge_system = StockPatternKnowledge(self.symbol)
        self.knowledge_system.load_knowledge()

    def analyze_current_conditions(self) -> Dict[str, Any]:
        """
        Analyze current market conditions and detect patterns
        Returns: Normal/abnormal status, capacity estimates, pump/dump signals
        """
        try:
            ticker = yf.Ticker(self.symbol)
            hist = ticker.history(period="20d")

            if len(hist) < 5:
                return {'has_data': False}

            # Current metrics
            current_price = hist['Close'].iloc[-1]
            current_volume = hist['Volume'].iloc[-1]

            # Recent moves
            recent_1d = (
                (hist['Close'].iloc[-1] - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2]) * 100
            recent_3d = ((hist['Close'].iloc[-1] - hist['Close'].iloc[-4]) /
                         hist['Close'].iloc[-4]) * 100 if len(hist) >= 5 else 0
            recent_5d = ((hist['Close'].iloc[-1] - hist['Close'].iloc[-6]) /
                         hist['Close'].iloc[-6]) * 100 if len(hist) >= 7 else 0

            # Volume ratio
            avg_volume = hist['Volume'].iloc[-10:].mean()
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0

            # RSI
            rsi = self._calculate_rsi(hist['Close'])

            # Current conditions
            current_conditions = {
                'recent_move_pct': recent_1d,
                'recent_3d_move': recent_3d,
                'recent_5d_move': recent_5d,
                'volume_ratio': volume_ratio,
                'rsi': rsi,
                'current_price': current_price,
            }

            # Analyze patterns
            analysis = {
                'has_data': True,
                'current_conditions': current_conditions,
                'normal_behavior': self._check_normal_behavior(recent_1d, volume_ratio),
                'capacity_analysis': self._analyze_capacity(recent_1d, recent_3d),
                'pump_dump_signals': self._detect_pump_dump_signals(current_conditions),
                'abnormal_detection': self._detect_abnormal(recent_1d, volume_ratio),
            }

            return analysis

        except Exception as e:
            return {'has_data': False, 'error': str(e)}

    def _check_normal_behavior(self, move_pct: float, volume_ratio: float) -> Dict[str, Any]:
        """Check if current behavior is normal"""
        knowledge = self.knowledge_system.knowledge
        if not knowledge:
            return {'status': 'unknown', 'reason': 'No knowledge available'}

        normal = knowledge.get('normal_behavior', {})
        normal_range = normal.get('normal_range', {})

        is_normal_move = normal_range.get(
            'min', -999) <= move_pct <= normal_range.get('max', 999)
        is_normal_volume = 0.5 <= volume_ratio <= 2.0

        status = 'normal'
        reasons = []

        if not is_normal_move:
            status = 'abnormal'
            if move_pct > normal_range.get('max', 999):
                reasons.append(
                    f"Move {move_pct:.2f}% exceeds normal max {normal_range.get('max', 0):.2f}%")
            elif move_pct < normal_range.get('min', -999):
                reasons.append(
                    f"Move {move_pct:.2f}% below normal min {normal_range.get('min', 0):.2f}%")

        if not is_normal_volume:
            if volume_ratio > 2.0:
                reasons.append(
                    f"Volume {volume_ratio:.2f}x is abnormally high")
            elif volume_ratio < 0.5:
                reasons.append(f"Volume {volume_ratio:.2f}x is abnormally low")

        return {
            'status': status,
            'is_normal_move': is_normal_move,
            'is_normal_volume': is_normal_volume,
            'reasons': reasons,
            'normal_range': normal_range,
        }

    def _analyze_capacity(self, recent_1d: float, recent_3d: float) -> Dict[str, Any]:
        """Analyze if move is approaching capacity limits"""
        knowledge = self.knowledge_system.knowledge
        if not knowledge:
            return {'status': 'unknown'}

        capacity = knowledge.get('capacity', {})
        p95_up = capacity.get('p95_up_move', 0)
        p95_down = capacity.get('p95_down_move', 0)

        # Check if approaching capacity
        capacity_warning = None
        remaining_capacity = None

        if recent_1d > 0:
            remaining_capacity = p95_up - recent_1d
            if recent_1d > p95_up * 0.8:
                capacity_warning = f"Approaching max capacity (+{p95_up:.2f}%)"
            elif recent_1d > p95_up:
                capacity_warning = f"EXCEEDED normal capacity (+{p95_up:.2f}%)"
        else:
            remaining_capacity = abs(p95_down) - abs(recent_1d)
            if abs(recent_1d) > abs(p95_down) * 0.8:
                capacity_warning = f"Approaching max capacity ({p95_down:.2f}%)"
            elif abs(recent_1d) > abs(p95_down):
                capacity_warning = f"EXCEEDED normal capacity ({p95_down:.2f}%)"

        return {
            'max_capacity_up': p95_up,
            'max_capacity_down': p95_down,
            'current_move': recent_1d,
            'remaining_capacity': remaining_capacity,
            'capacity_warning': capacity_warning,
            'is_near_capacity': capacity_warning is not None,
        }

    def _detect_pump_dump_signals(self, conditions: Dict[str, Any]) -> Dict[str, Any]:
        """Detect pump/dump signals"""
        knowledge = self.knowledge_system.knowledge
        if not knowledge:
            return {'pump_likely': False, 'dump_likely': False}

        # Check pump likelihood
        pump_likely, pump_score = self.knowledge_system.is_pump_likely(
            conditions)

        # Check dump likelihood
        dump_likely, dump_score = self.knowledge_system.is_dump_likely(
            conditions)

        signals = {
            'pump_likely': pump_likely,
            'pump_score': pump_score,
            'dump_likely': dump_likely,
            'dump_score': dump_score,
        }

        # Add specific triggers
        if pump_likely:
            triggers = []
            if conditions.get('volume_ratio', 1.0) > 1.5:
                triggers.append('High volume')
            if conditions.get('rsi', 50) < 50:
                triggers.append('Oversold bounce')
            signals['pump_triggers'] = triggers

        if dump_likely:
            triggers = []
            if conditions.get('volume_ratio', 1.0) > 1.5:
                triggers.append('High volume')
            if conditions.get('rsi', 50) > 60:
                triggers.append('Overbought reversal')
            signals['dump_triggers'] = triggers

        return signals

    def _detect_abnormal(self, move_pct: float, volume_ratio: float) -> Dict[str, Any]:
        """Detect abnormal behavior"""
        is_abnormal, reason = self.knowledge_system.is_abnormal_move(move_pct)

        abnormal_volume = volume_ratio > 2.5 or volume_ratio < 0.3

        return {
            'is_abnormal_move': is_abnormal,
            'abnormal_reason': reason,
            'is_abnormal_volume': abnormal_volume,
            'overall_abnormal': is_abnormal or abnormal_volume,
        }

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

    def get_prediction_adjustment(self, base_prediction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get prediction adjustment based on pattern knowledge
        Returns: Adjusted confidence, warnings, capacity limits
        """
        analysis = self.analyze_current_conditions()

        if not analysis.get('has_data', False):
            return {'adjustment': 0.0, 'warnings': []}

        adjustment = 0.0
        warnings = []

        # Check for abnormal behavior
        abnormal = analysis.get('abnormal_detection', {})
        if abnormal.get('overall_abnormal', False):
            warnings.append(
                "⚠️ ABNORMAL BEHAVIOR DETECTED - Reduce confidence")
            adjustment -= 0.10  # Reduce confidence by 10%

        # Check capacity limits
        capacity = analysis.get('capacity_analysis', {})
        if capacity.get('is_near_capacity', False):
            warnings.append(
                f"⚠️ {capacity.get('capacity_warning', 'Near capacity')}")
            if capacity.get('current_move', 0) > 0:
                adjustment -= 0.05  # Reduce bullish confidence near capacity

        # Check pump/dump signals
        pump_dump = analysis.get('pump_dump_signals', {})
        if pump_dump.get('dump_likely', False):
            warnings.append("📉 DUMP SIGNAL - High probability of reversal")
            adjustment -= 0.15  # Strong bearish adjustment
        elif pump_dump.get('pump_likely', False):
            warnings.append("🚀 PUMP SIGNAL - Momentum building")
            adjustment += 0.10  # Bullish boost

        return {
            'adjustment': adjustment,
            'warnings': warnings,
            'capacity_limits': {
                'max_up': capacity.get('max_capacity_up', 0),
                'max_down': capacity.get('max_capacity_down', 0),
            },
            'pattern_signals': pump_dump,
        }


if __name__ == "__main__":
    # Test pattern detection
    for symbol in ['AMD', 'NVDA']:
        print(f"\n{'='*80}")
        print(f"🔍 REAL-TIME PATTERN DETECTION: {symbol}")
        print(f"{'='*80}")

        detector = RealTimePatternDetector(symbol)
        analysis = detector.analyze_current_conditions()

        if analysis.get('has_data', False):
            print(f"\n📊 Current Conditions:")
            cond = analysis['current_conditions']
            print(f"   1-Day Move: {cond['recent_move_pct']:+.2f}%")
            print(f"   3-Day Move: {cond['recent_3d_move']:+.2f}%")
            print(f"   Volume Ratio: {cond['volume_ratio']:.2f}x")
            print(f"   RSI: {cond['rsi']:.1f}")

            print(f"\n✅ Normal Behavior Check:")
            normal = analysis['normal_behavior']
            print(f"   Status: {normal['status'].upper()}")
            if normal.get('reasons'):
                for reason in normal['reasons']:
                    print(f"   • {reason}")

            print(f"\n📈 Capacity Analysis:")
            capacity = analysis['capacity_analysis']
            print(
                f"   Max Capacity Up: +{capacity.get('max_capacity_up', 0):.2f}%")
            print(
                f"   Max Capacity Down: {capacity.get('max_capacity_down', 0):.2f}%")
            print(f"   Current Move: {capacity.get('current_move', 0):+.2f}%")
            if capacity.get('capacity_warning'):
                print(f"   ⚠️ {capacity['capacity_warning']}")

            print(f"\n🚀 Pump/Dump Signals:")
            pump_dump = analysis['pump_dump_signals']
            if pump_dump.get('pump_likely', False):
                print(
                    f"   ✅ PUMP LIKELY (Score: {pump_dump.get('pump_score', 0):.2f})")
                if pump_dump.get('pump_triggers'):
                    print(
                        f"      Triggers: {', '.join(pump_dump['pump_triggers'])}")
            if pump_dump.get('dump_likely', False):
                print(
                    f"   ⚠️ DUMP LIKELY (Score: {pump_dump.get('dump_score', 0):.2f})")
                if pump_dump.get('dump_triggers'):
                    print(
                        f"      Triggers: {', '.join(pump_dump['dump_triggers'])}")
            if not pump_dump.get('pump_likely', False) and not pump_dump.get('dump_likely', False):
                print(f"   ➡️ No strong pump/dump signals")

        print(f"\n{'='*80}\n")
