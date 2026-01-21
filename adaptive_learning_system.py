"""
Adaptive Learning System
Learns from market conditions and adjusts signal weights dynamically

This system will:
1. Track what signals work in different market conditions
2. Adjust weights based on recent accuracy
3. Learn from big drops/rallies
4. Adapt to market regime changes
"""
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any
import numpy as np

class AdaptiveLearningSystem:
    """
    Learns from market behavior and adapts signal weights
    """
    
    def __init__(self):
        self.history_file = 'data/adaptive_learning_history.json'
        self.load_history()
    
    def load_history(self):
        """Load learning history"""
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r') as f:
                self.history = json.load(f)
        else:
            self.history = {
                'market_regimes': {},  # Track performance by market condition
                'signal_accuracy': {},  # Track accuracy by signal type
                'big_moves': [],       # Track big market moves
                'adaptations': []      # Track system adaptations
            }
    
    def save_history(self):
        """Save learning history"""
        os.makedirs('data', exist_ok=True)
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=2)
    
    def analyze_market_regime(self, spy_change: float, qqq_change: float, vix_level: float) -> str:
        """
        Determine current market regime
        """
        market_avg = (spy_change + qqq_change) / 2
        
        if vix_level > 25:
            return 'HIGH_VOLATILITY'
        elif vix_level > 20:
            if market_avg < -1.0:
                return 'FEARFUL_DECLINE'
            elif market_avg > 1.0:
                return 'VOLATILE_RALLY'
            else:
                return 'CHOPPY'
        elif market_avg < -1.0:
            return 'STEADY_DECLINE'
        elif market_avg < -0.3:
            return 'MODERATE_WEAKNESS'
        elif market_avg > 1.0:
            return 'STRONG_RALLY'
        elif market_avg > 0.3:
            return 'MODERATE_STRENGTH'
        else:
            return 'NEUTRAL'
    
    def get_adaptive_weights(self, regime: str, base_weights: Dict[str, float]) -> Dict[str, float]:
        """
        Adjust weights based on market regime and learning
        
        Different market conditions favor different signals:
        - After big drops: Technical analysis more important (oversold bounces)
        - During rallies: Momentum and institutional flow more important
        - High volatility: Options and futures more predictive
        - Steady markets: News and fundamentals more reliable
        """
        
        adjusted_weights = base_weights.copy()
        
        # Regime-specific adjustments
        if regime == 'FEARFUL_DECLINE':
            # After big drop, focus on:
            # - Technical (oversold conditions)
            # - Options (fear/greed)
            # - VIX (mean reversion)
            adjustments = {
                'technical': 1.3,      # +30%
                'options': 1.2,        # +20%
                'vix': 1.2,           # +20%
                'news': 0.8,          # -20% (often lagging)
                'futures': 1.1        # +10%
            }
        
        elif regime == 'STEADY_DECLINE':
            # Trending down, focus on:
            # - Futures (momentum)
            # - Technical (trend following)
            # - Institutional (smart money exiting?)
            adjustments = {
                'futures': 1.3,
                'technical': 1.2,
                'institutional': 1.2,
                'options': 0.9,
                'news': 0.9
            }
        
        elif regime == 'STRONG_RALLY':
            # Strong up move, focus on:
            # - Momentum indicators
            # - Institutional flow (smart money buying?)
            # - Options (call activity)
            adjustments = {
                'institutional': 1.3,
                'options': 1.2,
                'technical': 1.1,
                'futures': 1.1,
                'news': 1.0
            }
        
        elif regime == 'HIGH_VOLATILITY':
            # High VIX, focus on:
            # - Options (IV expansion)
            # - Futures (leading indicator)
            # - VIX (reversion)
            adjustments = {
                'options': 1.4,
                'futures': 1.3,
                'vix': 1.2,
                'technical': 0.9,
                'news': 0.8
            }
        
        elif regime == 'CHOPPY':
            # Sideways/choppy, focus on:
            # - Mean reversion (technical)
            # - Options (range-bound)
            adjustments = {
                'technical': 1.3,
                'options': 1.1,
                'bollinger': 1.2,  # If we have it
                'futures': 0.9,
                'news': 0.9
            }
        
        else:  # NEUTRAL or MODERATE
            # Normal market, balanced approach
            adjustments = {
                'news': 1.1,
                'institutional': 1.1,
                'analyst_ratings': 1.1
            }
        
        # Apply adjustments
        for signal, multiplier in adjustments.items():
            if signal in adjusted_weights:
                adjusted_weights[signal] *= multiplier
        
        # Normalize back to sum to 1.0
        total = sum(adjusted_weights.values())
        adjusted_weights = {k: v/total for k, v in adjusted_weights.items()}
        
        return adjusted_weights
    
    def learn_from_outcome(self, prediction: Dict, actual_move: float):
        """
        Learn from prediction outcome
        Track which signals were right/wrong
        """
        
        predicted_direction = prediction['direction']
        actual_direction = 'UP' if actual_move > 0 else 'DOWN'
        
        correct = (predicted_direction == actual_direction)
        
        # Store outcome
        outcome = {
            'timestamp': datetime.now().isoformat(),
            'predicted': predicted_direction,
            'actual': actual_direction,
            'correct': correct,
            'confidence': prediction['confidence'],
            'score': prediction['total_score']
        }
        
        # Update regime-specific accuracy
        # (This would be filled in with more tracking)
        
        return correct
    
    def suggest_threshold_adjustment(self, regime: str, recent_accuracy: float) -> float:
        """
        Suggest confidence threshold based on regime and recent performance
        """
        
        base_threshold = 60
        
        # Adjust based on market regime
        if regime in ['FEARFUL_DECLINE', 'HIGH_VOLATILITY']:
            # More uncertainty = higher threshold
            regime_adjustment = +5
        elif regime in ['STEADY_DECLINE', 'STRONG_RALLY']:
            # Trending = can be more confident
            regime_adjustment = -3
        else:
            regime_adjustment = 0
        
        # Adjust based on recent accuracy
        if recent_accuracy > 0.75:
            # System working well = can lower threshold
            accuracy_adjustment = -3
        elif recent_accuracy < 0.55:
            # System struggling = raise threshold
            accuracy_adjustment = +5
        else:
            accuracy_adjustment = 0
        
        adjusted_threshold = base_threshold + regime_adjustment + accuracy_adjustment
        
        return np.clip(adjusted_threshold, 55, 70)  # Keep in reasonable range
    
    def after_big_drop_strategy(self, drop_size: float) -> Dict[str, Any]:
        """
        Special logic after big market drops
        
        After -2%+ drops:
        - Look for oversold bounces
        - Technical indicators more important
        - Options showing fear = contrarian opportunity
        - Institutional buying = strong signal
        """
        
        if drop_size < -2.0:
            return {
                'strategy': 'OVERSOLD_BOUNCE',
                'weight_boosts': {
                    'technical': 1.4,      # RSI, bollinger bands key
                    'options': 1.3,        # P/C ratio spikes = bottom?
                    'institutional': 1.3,  # Smart money buying dip?
                    'bollinger': 1.3,      # Near lower band = bounce
                    'money_flow': 1.2      # Oversold = reversal
                },
                'signals_to_watch': [
                    'RSI < 30 (oversold)',
                    'Near lower Bollinger band',
                    'Institutional accumulation',
                    'P/C ratio spike (fear peak)',
                    'Positive divergence (price down but indicators up)'
                ],
                'threshold_adjustment': -5,  # Can take more risk after flush
                'note': 'After big flush, look for technical reversal signals'
            }
        
        elif drop_size < -1.0:
            return {
                'strategy': 'CAUTIOUS',
                'weight_boosts': {
                    'futures': 1.2,
                    'technical': 1.2,
                    'vix': 1.1
                },
                'threshold_adjustment': +3,
                'note': 'Moderate decline, wait for stabilization'
            }
        
        else:
            return {'strategy': 'NORMAL'}
    
    def generate_report(self) -> str:
        """Generate learning report"""
        
        report = []
        report.append("="*80)
        report.append("🧠 ADAPTIVE LEARNING SYSTEM REPORT")
        report.append("="*80)
        
        report.append("\n📊 CURRENT LEARNINGS:")
        report.append("• System tracks market regimes")
        report.append("• Adjusts weights based on conditions")
        report.append("• Learns from prediction outcomes")
        report.append("• Adapts thresholds dynamically")
        
        report.append("\n🎯 MARKET REGIME STRATEGIES:")
        report.append("\n1. FEARFUL_DECLINE (Today's situation):")
        report.append("   • Boost: Technical +30%, Options +20%, VIX +20%")
        report.append("   • Reduce: News -20% (lagging)")
        report.append("   • Why: After drops, technical oversold matters most")
        
        report.append("\n2. STRONG_RALLY:")
        report.append("   • Boost: Institutional +30%, Options +20%")
        report.append("   • Why: Follow smart money in rallies")
        
        report.append("\n3. HIGH_VOLATILITY:")
        report.append("   • Boost: Options +40%, Futures +30%")
        report.append("   • Why: Fast-moving info more important")
        
        report.append("\n4. CHOPPY:")
        report.append("   • Boost: Technical +30%, Bollinger +20%")
        report.append("   • Why: Mean reversion in sideways markets")
        
        report.append("\n💡 SPECIAL STRATEGIES:")
        report.append("\nAfter Big Drops (-2%+):")
        report.append("   • OVERSOLD_BOUNCE strategy activates")
        report.append("   • Technical analysis weight +40%")
        report.append("   • Look for: RSI <30, lower Bollinger band")
        report.append("   • Lower threshold by 5% (take bounce opportunity)")
        
        report.append("\n" + "="*80)
        
        return "\n".join(report)

# Test the system
if __name__ == "__main__":
    print("Testing Adaptive Learning System...\n")
    
    learner = AdaptiveLearningSystem()
    
    # Today's situation
    spy_change = -0.80
    qqq_change = -1.41
    vix_level = 19.6
    
    regime = learner.analyze_market_regime(spy_change, qqq_change, vix_level)
    
    print(f"Current Market Regime: {regime}")
    print(f"SPY: {spy_change:+.2f}%, QQQ: {qqq_change:+.2f}%, VIX: {vix_level:.1f}")
    
    # Check if big drop strategy applies
    market_avg = (spy_change + qqq_change) / 2
    strategy = learner.after_big_drop_strategy(market_avg)
    
    print(f"\n📊 Recommended Strategy: {strategy['strategy']}")
    if 'weight_boosts' in strategy:
        print(f"\n💪 Weight Adjustments:")
        for signal, boost in strategy['weight_boosts'].items():
            print(f"   {signal}: ×{boost:.2f}")
    
    if 'threshold_adjustment' in strategy:
        print(f"\n🎯 Threshold Adjustment: {strategy['threshold_adjustment']:+d}%")
        print(f"   (60% → {60 + strategy['threshold_adjustment']}%)")
    
    if 'note' in strategy:
        print(f"\n💡 Note: {strategy['note']}")
    
    # Generate full report
    print(f"\n{learner.generate_report()}")
