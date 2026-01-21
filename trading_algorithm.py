#!/usr/bin/env python3
"""
Trading Algorithm for Overnight Swing Trades
Converts predictions into actionable trading decisions with:
- Entry strategy (optimal entry price)
- Position sizing (based on confidence and volatility)
- Stop loss placement (risk management)
- Take profit targets (reward optimization)
- Risk-reward validation (minimum 2:1 ratio)
"""

import sys
from pathlib import Path
from typing import Dict, Optional
sys.path.insert(0, str(Path(__file__).parent))

class TradingAlgorithm:
    """
    Converts prediction signals into specific trade parameters
    Optimized for overnight swing trades (3:50 PM → next morning)
    """
    
    def __init__(self, account_size: float = 10000, max_risk_per_trade: float = 0.02):
        """
        Args:
            account_size: Total account size in dollars
            max_risk_per_trade: Maximum risk per trade as percentage (default 2%)
        """
        self.account_size = account_size
        self.max_risk_per_trade = max_risk_per_trade
        self.min_confidence = 60  # Minimum confidence to take trade
        self.min_risk_reward = 1.5  # Minimum 1.5:1 risk-reward ratio (realistic for overnight swings)
    
    def generate_trade_plan(self, 
                           symbol: str,
                           prediction: Dict,
                           current_price: float,
                           typical_volatility: float) -> Optional[Dict]:
        """
        Generate complete trade plan from prediction
        
        Args:
            symbol: Stock ticker
            prediction: Prediction dict from comprehensive_nextday_predictor
            current_price: Current stock price (at 3:50 PM)
            typical_volatility: Stock's typical daily volatility (e.g., 0.0332 = 3.32%)
        
        Returns:
            Trade plan dict or None if no trade should be taken
        """
        direction = prediction['direction']
        confidence = prediction['confidence']
        target_pct = prediction['target_pct']
        
        # Skip if confidence too low
        if confidence < self.min_confidence:
            return {
                'action': 'NO_TRADE',
                'reason': f'Confidence {confidence:.1f}% below minimum {self.min_confidence}%',
                'symbol': symbol
            }
        
        # Skip NEUTRAL predictions
        if direction == 'NEUTRAL':
            return {
                'action': 'NO_TRADE',
                'reason': 'Neutral prediction - no clear direction',
                'symbol': symbol
            }
        
        # Calculate trade parameters
        trade_plan = self._calculate_trade_parameters(
            symbol=symbol,
            direction=direction,
            confidence=confidence,
            current_price=current_price,
            target_pct=target_pct,
            typical_volatility=typical_volatility
        )
        
        # Validate risk-reward ratio
        if trade_plan['risk_reward_ratio'] < self.min_risk_reward:
            return {
                'action': 'NO_TRADE',
                'reason': f'Risk-reward {trade_plan["risk_reward_ratio"]:.2f} below minimum {self.min_risk_reward}',
                'symbol': symbol,
                'attempted_plan': trade_plan
            }
        
        return trade_plan
    
    def _calculate_trade_parameters(self,
                                   symbol: str,
                                   direction: str,
                                   confidence: float,
                                   current_price: float,
                                   target_pct: float,
                                   typical_volatility: float) -> Dict:
        """
        Calculate specific entry, stop, target, and position size
        """
        # 1. Entry Price Strategy
        # For overnight swings, we want to enter near close (3:50-4:00 PM)
        # Use market order or limit at current price with small buffer
        if direction == 'UP':
            # Enter at or slightly below current price
            entry_price = current_price * 0.999  # 0.1% below to ensure fill
        else:  # DOWN
            # For shorts or puts, enter at or slightly above current price
            entry_price = current_price * 1.001  # 0.1% above to ensure fill
        
        # 2. Stop Loss Placement
        # Based on ATR (Average True Range) concept using typical volatility
        # More conservative stops for lower confidence
        # For overnight swings, use wider stops to avoid getting stopped out on normal volatility
        base_stop_pct = typical_volatility * 0.75  # Use 75% of daily volatility as base (wider for overnight)
        
        # Adjust stop based on confidence
        # Higher confidence = tighter stops (we trust the signal more)
        if confidence >= 80:
            stop_multiplier = 0.6  # Tight stop for high confidence
        elif confidence >= 70:
            stop_multiplier = 0.8  # Moderate stop
        elif confidence >= 60:
            stop_multiplier = 1.0  # Standard stop for minimum confidence
        else:
            stop_multiplier = 1.5  # Wider stop for very low confidence
        
        stop_pct = base_stop_pct * stop_multiplier
        
        if direction == 'UP':
            stop_price = entry_price * (1 - stop_pct)
        else:  # DOWN
            stop_price = entry_price * (1 + stop_pct)
        
        # 3. Take Profit Target
        # Use predicted target but apply confidence scaling
        # Lower confidence = take profits earlier (but keep at minimum 80% of target)
        # For overnight swings, we want to capture most of the predicted move
        confidence_factor = max(0.80, confidence / 100.0)  # Minimum 80% of target even for 60% confidence
        adjusted_target_pct = abs(target_pct) * confidence_factor
        
        if direction == 'UP':
            target_price = entry_price * (1 + adjusted_target_pct)
        else:  # DOWN
            target_price = entry_price * (1 - adjusted_target_pct)
        
        # 4. Risk-Reward Calculation
        risk_per_share = abs(entry_price - stop_price)
        reward_per_share = abs(target_price - entry_price)
        risk_reward_ratio = reward_per_share / risk_per_share if risk_per_share > 0 else 0
        
        # 5. Position Sizing
        # Kelly Criterion adapted for trading
        # Position size = (confidence - 50) / 100 * max_risk * account_size / risk_per_share
        # But cap at max_risk_per_trade for safety
        max_risk_dollars = self.account_size * self.max_risk_per_trade
        
        # Adjust position based on confidence
        # High confidence = larger position (up to max)
        # Low confidence = smaller position
        kelly_factor = (confidence - 50) / 50  # 0 to 0.76 for conf 50-88
        adjusted_risk = max_risk_dollars * kelly_factor
        
        shares = int(adjusted_risk / risk_per_share)
        
        # Ensure at least 1 share
        if shares < 1:
            shares = 1
        
        # Calculate actual dollar amounts
        position_value = shares * entry_price
        risk_dollars = shares * risk_per_share
        reward_dollars = shares * reward_per_share
        
        # 6. Timing Strategy for Overnight Swings
        entry_time = "3:50-4:00 PM"  # Before market close
        monitor_time = "6:00 AM next day"  # Check premarket
        exit_time_window = "6:00-10:00 AM"  # Premarket or morning session
        
        return {
            'action': 'TAKE_TRADE',
            'symbol': symbol,
            'direction': direction,
            'confidence': confidence,
            
            # Entry
            'entry_strategy': 'MARKET_ON_CLOSE' if shares * entry_price < 10000 else 'LIMIT',
            'entry_price': round(entry_price, 2),
            'entry_time': entry_time,
            
            # Risk Management
            'stop_loss': round(stop_price, 2),
            'stop_pct': round(stop_pct * 100, 2),
            
            # Profit Target
            'take_profit': round(target_price, 2),
            'target_pct': round(adjusted_target_pct * 100, 2),
            
            # Position Sizing
            'shares': shares,
            'position_value': round(position_value, 2),
            
            # Risk-Reward
            'risk_per_share': round(risk_per_share, 2),
            'reward_per_share': round(reward_per_share, 2),
            'risk_dollars': round(risk_dollars, 2),
            'reward_dollars': round(reward_dollars, 2),
            'risk_reward_ratio': round(risk_reward_ratio, 2),
            
            # Timing
            'monitor_time': monitor_time,
            'exit_window': exit_time_window,
            'max_hold_time': '16 hours (overnight)',
            
            # Risk as % of account
            'risk_pct_of_account': round((risk_dollars / self.account_size) * 100, 2)
        }
    
    def print_trade_plan(self, trade_plan: Dict):
        """Pretty print trade plan"""
        if trade_plan['action'] == 'NO_TRADE':
            print("\n" + "="*80)
            print("🚫 NO TRADE RECOMMENDED")
            print("="*80)
            print(f"Symbol: {trade_plan['symbol']}")
            print(f"Reason: {trade_plan['reason']}")
            print("="*80)
            return
        
        print("\n" + "="*80)
        print("🎯 TRADE PLAN - OVERNIGHT SWING")
        print("="*80)
        
        print(f"\n📊 OVERVIEW:")
        print(f"   Symbol:     {trade_plan['symbol']}")
        print(f"   Direction:  {trade_plan['direction']} {'🟢' if trade_plan['direction'] == 'UP' else '🔴'}")
        print(f"   Confidence: {trade_plan['confidence']:.1f}%")
        
        print(f"\n💰 ENTRY STRATEGY:")
        print(f"   Entry Price:  ${trade_plan['entry_price']:.2f}")
        print(f"   Entry Type:   {trade_plan['entry_strategy']}")
        print(f"   Entry Time:   {trade_plan['entry_time']}")
        print(f"   Shares:       {trade_plan['shares']:,}")
        print(f"   Position:     ${trade_plan['position_value']:,.2f}")
        
        print(f"\n🛡️ RISK MANAGEMENT:")
        print(f"   Stop Loss:    ${trade_plan['stop_loss']:.2f} ({trade_plan['stop_pct']:+.2f}%)")
        print(f"   Risk/Share:   ${trade_plan['risk_per_share']:.2f}")
        print(f"   Total Risk:   ${trade_plan['risk_dollars']:,.2f} ({trade_plan['risk_pct_of_account']:.2f}% of account)")
        
        print(f"\n🎯 PROFIT TARGET:")
        print(f"   Take Profit:  ${trade_plan['take_profit']:.2f} ({trade_plan['target_pct']:+.2f}%)")
        print(f"   Reward/Share: ${trade_plan['reward_per_share']:.2f}")
        print(f"   Total Reward: ${trade_plan['reward_dollars']:,.2f}")
        
        print(f"\n📈 RISK-REWARD:")
        print(f"   Ratio:        {trade_plan['risk_reward_ratio']:.2f}:1 {'✅' if trade_plan['risk_reward_ratio'] >= 1.5 else '⚠️'}")
        
        print(f"\n⏰ TIMING:")
        print(f"   Monitor:      {trade_plan['monitor_time']}")
        print(f"   Exit Window:  {trade_plan['exit_window']}")
        print(f"   Max Hold:     {trade_plan['max_hold_time']}")
        
        print(f"\n📋 EXECUTION CHECKLIST:")
        print(f"   [ ] Place order at 3:50 PM")
        print(f"   [ ] Set stop loss order")
        print(f"   [ ] Set take profit order (or alert)")
        print(f"   [ ] Check premarket at 6:00 AM")
        print(f"   [ ] Exit when target hit or by 10:00 AM")
        
        print("\n" + "="*80)


def demonstrate_algorithm():
    """Demonstrate the trading algorithm with example predictions"""
    
    print("="*80)
    print("🤖 TRADING ALGORITHM DEMONSTRATION")
    print("="*80)
    print("\nConverting predictions into actionable trades...")
    
    # Initialize algorithm with $10,000 account and 2% max risk
    algo = TradingAlgorithm(account_size=10000, max_risk_per_trade=0.02)
    
    # Example 1: Strong bullish prediction for AMD
    print("\n\n" + "█"*80)
    print("EXAMPLE 1: Strong Bullish Signal (AMD)")
    print("█"*80)
    
    prediction_bullish = {
        'direction': 'UP',
        'confidence': 85,
        'target_pct': 0.0420  # 4.2% target (realistic for strong overnight signal)
    }
    
    trade_plan = algo.generate_trade_plan(
        symbol='AMD',
        prediction=prediction_bullish,
        current_price=145.50,
        typical_volatility=0.0332  # 3.32% daily volatility
    )
    
    algo.print_trade_plan(trade_plan)
    
    # Example 2: Moderate bearish prediction for AVGO
    print("\n\n" + "█"*80)
    print("EXAMPLE 2: Moderate Bearish Signal (AVGO)")
    print("█"*80)
    
    prediction_bearish = {
        'direction': 'DOWN',
        'confidence': 72,
        'target_pct': -0.0350  # -3.5% target (realistic for moderate overnight signal)
    }
    
    trade_plan = algo.generate_trade_plan(
        symbol='AVGO',
        prediction=prediction_bearish,
        current_price=175.20,
        typical_volatility=0.0281  # 2.81% daily volatility
    )
    
    algo.print_trade_plan(trade_plan)
    
    # Example 3: Low confidence - should reject trade
    print("\n\n" + "█"*80)
    print("EXAMPLE 3: Low Confidence Signal (Should Reject)")
    print("█"*80)
    
    prediction_low_conf = {
        'direction': 'UP',
        'confidence': 55,
        'target_pct': 0.0120
    }
    
    trade_plan = algo.generate_trade_plan(
        symbol='ORCL',
        prediction=prediction_low_conf,
        current_price=132.40,
        typical_volatility=0.0306  # 3.06% daily volatility
    )
    
    algo.print_trade_plan(trade_plan)
    
    # Example 4: Neutral prediction - should reject
    print("\n\n" + "█"*80)
    print("EXAMPLE 4: Neutral Signal (Should Reject)")
    print("█"*80)
    
    prediction_neutral = {
        'direction': 'NEUTRAL',
        'confidence': 50,
        'target_pct': 0.0000
    }
    
    trade_plan = algo.generate_trade_plan(
        symbol='AMD',
        prediction=prediction_neutral,
        current_price=145.50,
        typical_volatility=0.0332
    )
    
    algo.print_trade_plan(trade_plan)
    
    print("\n\n" + "="*80)
    print("✅ ALGORITHM DEMONSTRATION COMPLETE")
    print("="*80)
    print("\nKey Algorithm Features:")
    print("✅ Converts predictions into specific trade parameters")
    print("✅ Calculates optimal position size based on confidence")
    print("✅ Sets appropriate stop loss using volatility-based approach")
    print("✅ Determines take profit targets with confidence scaling")
    print("✅ Validates minimum 1.5:1 risk-reward ratio (realistic for overnight swings)")
    print("✅ Rejects low-confidence or neutral trades")
    print("✅ Manages risk as percentage of account (2% max)")
    print("✅ Optimized for overnight swing trading (3:50 PM → next morning)")
    print("\n" + "="*80)


if __name__ == '__main__':
    demonstrate_algorithm()
