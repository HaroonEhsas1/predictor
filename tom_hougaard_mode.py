"""
TOM HOUGAARD MODE - Ultra-Conservative Trading
==============================================
Based on Tom Hougaard's principles from "Best Loser Wins"

Key Differences from Standard Mode:
1. 1% Risk Per Trade (vs 2%)
2. Price Action Focus (Options, Futures, Technical, S/R only)
3. Higher Confidence Filter (55% min vs 50%)
4. Stricter R:R Ratio (1:2.5 vs 1:1.67)
5. Session-Based Trading (London/NY only)

Philosophy: "Keep it simple, manage risk, let winners run"
"""

import yfinance as yf
from datetime import datetime, time
import pytz

class TomHougaardMode:
    """
    Ultra-conservative trading mode inspired by Tom Hougaard's principles
    """
    
    def __init__(self):
        self.max_risk_percent = 1.0  # Tom's 1% rule
        self.min_confidence = 55  # Higher than standard 50%
        self.min_risk_reward = 2.5  # Stricter than standard 1.67
        
    def should_trade_now(self):
        """
        Tom's rule: Only trade during high-volatility sessions
        - London: 8:00-10:00 GMT
        - NY: 14:30-16:30 GMT (9:30-11:30 EST)
        - Overlap: 13:00-17:00 GMT (best time)
        """
        gmt = pytz.timezone('GMT')
        now = datetime.now(gmt)
        current_time = now.time()
        
        # London session (first 2 hours)
        london_open = time(8, 0)
        london_close = time(10, 0)
        
        # NY session (first 2 hours)
        ny_open = time(14, 30)
        ny_close = time(16, 30)
        
        # Best: London/NY overlap
        overlap_start = time(13, 0)
        overlap_end = time(17, 0)
        
        in_london = london_open <= current_time <= london_close
        in_ny = ny_open <= current_time <= ny_close
        in_overlap = overlap_start <= current_time <= overlap_end
        
        return {
            'should_trade': in_london or in_ny,
            'is_optimal': in_overlap,
            'session': 'London/NY Overlap' if in_overlap else 
                      ('London' if in_london else 'NY' if in_ny else 'Low Volatility')
        }
    
    def calculate_position_size(self, account_balance, stop_loss_percent, confidence):
        """
        Tom's position sizing: 1% risk per trade
        
        Args:
            account_balance: Total account size
            stop_loss_percent: Stop distance (e.g., 2.5 for 2.5%)
            confidence: Prediction confidence (50-95%)
        
        Returns:
            Position size and risk amount
        """
        # Tom's rule: Always 1% risk
        risk_amount = account_balance * (self.max_risk_percent / 100)
        
        # Position size = Risk Amount / Stop Loss Distance
        position_size = risk_amount / (stop_loss_percent / 100)
        
        # Scale by confidence (Tom would do this intuitively)
        confidence_multiplier = self._get_confidence_multiplier(confidence)
        adjusted_position = position_size * confidence_multiplier
        
        return {
            'position_size': adjusted_position,
            'risk_amount': risk_amount,
            'risk_percent': self.max_risk_percent,
            'confidence_multiplier': confidence_multiplier
        }
    
    def _get_confidence_multiplier(self, confidence):
        """
        Tom's conviction-based sizing:
        - 55-60%: 50% position (testing waters)
        - 60-70%: 75% position (good setup)
        - 70-80%: 100% position (high conviction)
        - 80%+: 100% position (don't over-leverage even when confident)
        """
        if confidence < 55:
            return 0  # Don't trade
        elif confidence < 60:
            return 0.50
        elif confidence < 70:
            return 0.75
        elif confidence < 80:
            return 1.00
        else:
            return 1.00  # Tom: Never over-leverage
    
    def filter_signals(self, prediction):
        """
        Apply Tom's filters to standard system predictions
        
        Args:
            prediction: Standard system prediction dict
        
        Returns:
            Filtered prediction with Tom's rules applied
        """
        confidence = prediction.get('confidence', 0)
        score = prediction.get('score', 0)
        direction = prediction.get('direction', 'NEUTRAL')
        
        # Filter 1: Confidence must be 55%+
        if confidence < self.min_confidence:
            return {
                'trade': False,
                'reason': f"Confidence {confidence}% below Tom's 55% minimum",
                'tom_approved': False
            }
        
        # Filter 2: Check if in trading session
        session = self.should_trade_now()
        if not session['should_trade']:
            return {
                'trade': False,
                'reason': f"Outside trading hours (currently {session['session']})",
                'tom_approved': False
            }
        
        # Filter 3: Calculate risk/reward
        target = prediction.get('target', 0)
        stop = prediction.get('stop_loss', 0)
        entry = prediction.get('entry_price', 0)
        
        if entry > 0 and stop > 0:
            if direction == 'UP':
                risk = entry - stop
                reward = target - entry
            else:
                risk = stop - entry
                reward = entry - target
            
            risk_reward_ratio = reward / risk if risk > 0 else 0
            
            if risk_reward_ratio < self.min_risk_reward:
                return {
                    'trade': False,
                    'reason': f"R:R {risk_reward_ratio:.2f} below Tom's 2.5 minimum",
                    'tom_approved': False
                }
        
        # Passed all filters
        return {
            'trade': True,
            'reason': f"Tom-approved: {confidence}% confidence, {session['session']} session",
            'tom_approved': True,
            'session': session['session'],
            'is_optimal': session['is_optimal'],
            'confidence': confidence,
            'direction': direction
        }
    
    def simplify_prediction(self, full_prediction):
        """
        Tom's approach: Focus on PRICE ACTION only
        Remove news, social, sentiment - keep only price-derived signals
        
        Recalculates score using only:
        - Futures (price-derived)
        - Options flow (price-derived)
        - Technical indicators (price-derived)
        - Support/Resistance (price levels)
        """
        # Extract price-action components only
        components = full_prediction.get('components', {})
        
        price_action_sources = [
            'futures', 'options', 'technical', 'support_resistance',
            'premarket', 'volume', 'momentum', 'vwap'
        ]
        
        # Recalculate score with price action only
        simplified_score = 0
        total_weight = 0
        
        for source in price_action_sources:
            if source in components:
                score = components[source].get('score', 0)
                weight = components[source].get('weight', 0)
                simplified_score += score * weight
                total_weight += weight
        
        # Normalize
        if total_weight > 0:
            simplified_score = simplified_score / total_weight
        
        # Recalculate confidence
        simplified_confidence = self._calculate_simple_confidence(simplified_score)
        
        return {
            'score': simplified_score,
            'confidence': simplified_confidence,
            'direction': 'UP' if simplified_score > 0.03 else 'DOWN' if simplified_score < -0.03 else 'NEUTRAL',
            'sources_used': price_action_sources,
            'philosophy': 'Tom Hougaard - Price Action Only'
        }
    
    def _calculate_simple_confidence(self, score):
        """
        Conservative confidence calculation
        Tom wouldn't claim 95% confidence - cap at 80%
        """
        abs_score = abs(score)
        
        if abs_score < 0.01:
            return 50  # Neutral
        elif abs_score < 0.03:
            return 55  # Weak signal
        elif abs_score < 0.05:
            return 62
        elif abs_score < 0.07:
            return 68
        elif abs_score < 0.10:
            return 75
        else:
            return 80  # Tom: Never 95% certain (cap at 80%)
    
    def generate_trade_plan(self, prediction, account_balance):
        """
        Generate Tom-style trade plan
        
        Returns complete trade setup with:
        - Entry price
        - Stop loss (tight)
        - Target (2.5x stop distance minimum)
        - Position size (1% risk)
        - Session timing
        """
        # Apply Tom's filters
        filtered = self.filter_signals(prediction)
        
        if not filtered['tom_approved']:
            return {
                'trade': False,
                'reason': filtered['reason']
            }
        
        # Calculate position sizing
        stop_loss_pct = prediction.get('stop_loss_percent', 2.0)
        position_info = self.calculate_position_size(
            account_balance, 
            stop_loss_pct, 
            prediction['confidence']
        )
        
        # Build trade plan
        trade_plan = {
            'trade': True,
            'symbol': prediction.get('symbol', 'N/A'),
            'direction': prediction['direction'],
            'confidence': prediction['confidence'],
            'entry_price': prediction.get('entry_price', 0),
            'stop_loss': prediction.get('stop_loss', 0),
            'target': prediction.get('target', 0),
            'position_size': position_info['position_size'],
            'risk_amount': position_info['risk_amount'],
            'risk_percent': position_info['risk_percent'],
            'session': filtered['session'],
            'is_optimal_time': filtered['is_optimal'],
            'tom_approved': True,
            'philosophy': "Best Loser Wins - Risk management first"
        }
        
        return trade_plan


def compare_modes(standard_prediction, account_balance=10000):
    """
    Compare Standard Mode vs Tom Hougaard Mode
    """
    tom_mode = TomHougaardMode()
    
    print("=" * 70)
    print("🎯 STANDARD MODE vs TOM HOUGAARD MODE COMPARISON")
    print("=" * 70)
    
    # Standard mode
    print("\n📊 STANDARD MODE:")
    print(f"   Confidence: {standard_prediction['confidence']}%")
    print(f"   Direction: {standard_prediction['direction']}")
    print(f"   Risk: 2% max")
    print(f"   Min Confidence: 50%")
    
    # Tom mode
    print("\n🎯 TOM HOUGAARD MODE:")
    tom_result = tom_mode.filter_signals(standard_prediction)
    
    if tom_result['tom_approved']:
        trade_plan = tom_mode.generate_trade_plan(standard_prediction, account_balance)
        print(f"   ✅ TOM APPROVED")
        print(f"   Confidence: {trade_plan['confidence']}%")
        print(f"   Direction: {trade_plan['direction']}")
        print(f"   Risk: {trade_plan['risk_percent']}% (${trade_plan['risk_amount']:.2f})")
        print(f"   Position: ${trade_plan['position_size']:.2f}")
        print(f"   Session: {trade_plan['session']}")
        print(f"   Optimal Time: {'Yes' if trade_plan['is_optimal_time'] else 'No'}")
    else:
        print(f"   ❌ TOM REJECTED")
        print(f"   Reason: {tom_result['reason']}")
    
    # Price action mode
    print("\n💡 TOM'S PRICE ACTION MODE:")
    simplified = tom_mode.simplify_prediction(standard_prediction)
    print(f"   Score: {simplified['score']:.4f}")
    print(f"   Confidence: {simplified['confidence']}%")
    print(f"   Direction: {simplified['direction']}")
    print(f"   Sources: {len(simplified['sources_used'])} price-action only")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    # Example usage
    example_prediction = {
        'symbol': 'AMD',
        'confidence': 65,
        'score': 0.045,
        'direction': 'UP',
        'entry_price': 150.00,
        'target': 154.50,
        'stop_loss': 148.50,
        'stop_loss_percent': 1.0,
        'components': {
            'futures': {'score': 0.05, 'weight': 0.15},
            'options': {'score': 0.03, 'weight': 0.11},
            'technical': {'score': 0.02, 'weight': 0.08},
            'news': {'score': 0.06, 'weight': 0.08},
            'reddit': {'score': 0.04, 'weight': 0.08}
        }
    }
    
    compare_modes(example_prediction, account_balance=10000)
