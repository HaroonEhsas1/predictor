"""
IMPROVED 1-MINUTE PREDICTION FUNCTION FOR AMD STOCK SYSTEM
==========================================================

This function provides a clean, modular replacement for your current 1-minute prediction logic.
It focuses on realistic $0.20 profit moves with proper risk management.

Key Features:
- Market closed detection (returns "MARKET CLOSED" with 0% confidence)
- Realistic $0.20 profit targets (±$0.40 stop-loss)
- Clean integration with existing system structure
- All values rounded to 2 decimals for consistency
- Maintains existing ML model integration and historical data usage
"""

import numpy as np
from typing import Dict, Any
from datetime import datetime

def enhanced_1minute_prediction(self, stock_data, market_mode: str = "live") -> Dict[str, Any]:
    """
    Enhanced 1-minute AMD stock prediction focusing on realistic $0.20 profit moves.
    
    Args:
        stock_data: StockData object with current market information
        market_mode: "live" for trading hours, "collect-only" for market closed
        
    Returns:
        Dictionary with prediction results including direction, confidence, prices, and risk management
    """
    
    # === MARKET CLOSED DETECTION ===
    if market_mode == "collect-only":
        return {
            'predicted_price': round(stock_data.current_price, 2),
            'price_change': 0.00,
            'price_change_pct': 0.00,
            'direction': 'MARKET CLOSED',
            'signal': 'DATA COLLECTION',
            'confidence': 0.00,
            'method': 'Market Closed - Data Collection Mode',
            'stop_loss': 0.00,
            'take_profit': 0.00,
            'target_profit': 0.00,
            'target_stop_loss': 0.00,
            'risk_reward_ratio': 0.00,
            'momentum_score': 0,
            'signal_strength': 0,
            'market_status': 'Market closed – analyzing data for tomorrow'
        }
    
    # === PROFIT TARGET CONFIGURATION ===
    profit_target = 0.20  # $0.20 profit target
    stop_loss_amount = 0.40  # $0.40 stop loss (2x profit target)
    
    current_price = stock_data.current_price
    
    # === MOMENTUM ANALYSIS ===
    momentum_score = 0
    signal_strength = 0
    confidence_boost = 0
    
    # Multi-timeframe momentum analysis
    momentum_15m = getattr(stock_data, 'price_change_15m', 0)
    momentum_30m = getattr(stock_data, 'price_change_30m', 0) 
    momentum_1h = getattr(stock_data, 'price_change_1h', 0)
    
    # Weighted momentum calculation (favor recent data)
    weighted_momentum = momentum_15m * 0.6 + momentum_30m * 0.3 + momentum_1h * 0.1
    
    # Momentum acceleration detection
    momentum_acceleration = momentum_15m - momentum_30m
    
    # === MOMENTUM SCORING ===
    if weighted_momentum > 0.3:  # Strong bullish
        momentum_score += 3
        signal_strength += 2
        confidence_boost += 15
    elif weighted_momentum > 0.15:  # Moderate bullish
        momentum_score += 2
        signal_strength += 1
        confidence_boost += 10
    elif weighted_momentum > 0.05:  # Weak bullish
        momentum_score += 1
        confidence_boost += 5
    elif weighted_momentum < -0.3:  # Strong bearish
        momentum_score -= 3
        signal_strength += 2
        confidence_boost += 15
    elif weighted_momentum < -0.15:  # Moderate bearish
        momentum_score -= 2
        signal_strength += 1
        confidence_boost += 10
    elif weighted_momentum < -0.05:  # Weak bearish
        momentum_score -= 1
        confidence_boost += 5
    
    # Acceleration bonus
    if abs(momentum_acceleration) > 0.2:
        signal_strength += 1
        confidence_boost += 8
        if momentum_acceleration > 0:
            momentum_score += 1
        else:
            momentum_score -= 1
    
    # === VOLUME ANALYSIS ===
    avg_volume = 35000000  # AMD typical daily volume
    volume_ratio = stock_data.volume / avg_volume
    
    if volume_ratio > 1.5:  # High volume confirmation
        signal_strength += 2
        confidence_boost += 12
        if weighted_momentum > 0:
            momentum_score += 1
        else:
            momentum_score -= 1
    elif volume_ratio > 1.2:  # Above average volume
        signal_strength += 1
        confidence_boost += 8
    elif volume_ratio < 0.8:  # Low volume - reduce confidence
        confidence_boost -= 5
    
    # === RSI ANALYSIS ===
    rsi = stock_data.rsi_14
    
    if rsi < 30 and momentum_score > 0:  # Oversold + bullish momentum
        momentum_score += 2
        signal_strength += 1
        confidence_boost += 12
    elif rsi > 70 and momentum_score < 0:  # Overbought + bearish momentum
        momentum_score -= 2
        signal_strength += 1
        confidence_boost += 12
    elif rsi < 35 and momentum_score > 0:  # Mildly oversold + bullish
        momentum_score += 1
        confidence_boost += 8
    elif rsi > 65 and momentum_score < 0:  # Mildly overbought + bearish
        momentum_score -= 1
        confidence_boost += 8
    
    # === SIGNAL GENERATION ===
    base_confidence = 55 + signal_strength * 5 + confidence_boost
    
    # Determine direction and target prices
    if momentum_score >= 3 and signal_strength >= 2:
        direction = "UP"
        signal = "BUY"
        target_price = current_price + profit_target
        stop_loss_price = current_price - stop_loss_amount
        confidence = min(85.00, base_confidence + 10)
        
    elif momentum_score <= -3 and signal_strength >= 2:
        direction = "DOWN" 
        signal = "SELL"
        target_price = current_price - profit_target
        stop_loss_price = current_price + stop_loss_amount
        confidence = min(85.00, base_confidence + 10)
        
    elif momentum_score >= 2 and signal_strength >= 1:
        direction = "UP"
        signal = "WEAK BUY"
        target_price = current_price + (profit_target * 0.75)  # $0.15 target
        stop_loss_price = current_price - stop_loss_amount
        confidence = min(75.00, base_confidence)
        
    elif momentum_score <= -2 and signal_strength >= 1:
        direction = "DOWN"
        signal = "WEAK SELL" 
        target_price = current_price - (profit_target * 0.75)  # $0.15 target
        stop_loss_price = current_price + stop_loss_amount
        confidence = min(75.00, base_confidence)
        
    elif momentum_score >= 1:
        direction = "UP"
        signal = "WAIT"  # Conservative - wait for stronger signal
        target_price = current_price + (profit_target * 0.5)  # $0.10 target
        stop_loss_price = current_price - (stop_loss_amount * 0.5)  # $0.20 stop
        confidence = min(65.00, base_confidence - 5)
        
    elif momentum_score <= -1:
        direction = "DOWN"
        signal = "WAIT"  # Conservative - wait for stronger signal
        target_price = current_price - (profit_target * 0.5)  # $0.10 target
        stop_loss_price = current_price + (stop_loss_amount * 0.5)  # $0.20 stop
        confidence = min(65.00, base_confidence - 5)
        
    else:
        direction = "NEUTRAL"
        signal = "WAIT"
        target_price = current_price
        stop_loss_price = current_price
        confidence = max(50.00, min(60.00, base_confidence - 10))
    
    # === RISK/REWARD CALCULATION ===
    profit_potential = abs(target_price - current_price)
    loss_risk = abs(stop_loss_price - current_price)
    risk_reward_ratio = round(loss_risk / profit_potential if profit_potential > 0 else 1.0, 2)
    
    # === FINAL VALIDATION ===
    # Ensure minimum confidence
    confidence = max(50.00, confidence)
    
    # Price change calculations
    price_change = target_price - current_price
    price_change_pct = (price_change / current_price) * 100 if current_price > 0 else 0
    
    # === RETURN RESULTS ===
    return {
        'predicted_price': round(target_price, 2),
        'price_change': round(price_change, 2),
        'price_change_pct': round(price_change_pct, 2),
        'direction': direction,
        'signal': signal,
        'confidence': round(confidence, 2),
        'method': 'Enhanced 1-Minute v3.0 - Realistic $0.20 Targets',
        'stop_loss': round(stop_loss_price, 2),
        'take_profit': round(target_price, 2),
        'target_profit': round(profit_potential, 2),
        'target_stop_loss': round(loss_risk, 2),
        'risk_reward_ratio': risk_reward_ratio,
        'momentum_score': momentum_score,
        'signal_strength': signal_strength,
        'volume_ratio': round(volume_ratio, 2),
        'weighted_momentum': round(weighted_momentum, 2),
        'momentum_acceleration': round(momentum_acceleration, 2),
        'market_status': 'Market open - live trading signals'
    }


def integrate_improved_1minute_prediction():
    """
    Integration instructions for your existing StockPredictor class:
    
    1. Replace your current _fallback_1min_prediction method with enhanced_1minute_prediction
    2. Update the method call in predict_1minute_ahead to use the new function
    3. The function maintains all existing return value structures for compatibility
    
    Example integration:
    ```python
    def predict_1minute_ahead(self, stock_data: StockData, market_mode: str = "live") -> dict:
        # ... existing caching logic ...
        
        try:
            # Try LSTM first if available
            if LSTM_AVAILABLE:
                prediction = self._lstm_1minute_prediction(stock_data, comprehensive_data, market_mode)
                if prediction:
                    return prediction
                    
            # Fallback to enhanced prediction
            return self.enhanced_1minute_prediction(stock_data, market_mode)
            
        except Exception as e:
            print(f"1-minute prediction error: {e}")
            return self.enhanced_1minute_prediction(stock_data, market_mode)
    ```
    
    Key benefits:
    - Cleaner, more maintainable code
    - Focused on realistic $0.20 profit targets
    - Proper market closed handling
    - All values rounded to 2 decimals
    - Compatible with existing system structure
    """
    pass

if __name__ == "__main__":
    print("✅ Enhanced 1-minute prediction function ready for integration")
    print("📊 Focuses on realistic $0.20 profit moves with $0.40 stop-loss")
    print("🔒 Safe, modular design that won't break existing codebase")
    print("💼 Market closed detection returns 'MARKET CLOSED' with 0% confidence")
    print("📈 Maintains ML model integration and historical data usage")