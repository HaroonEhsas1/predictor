#!/usr/bin/env python3
"""
CLEAN NEXT-DAY PREDICTION SYSTEM
================================

Simplified, professional next-day prediction without excessive noise.
Focus on actionable insights with minimal verbose output.
"""

import os
import sys
import numpy as np
import pandas as pd
import requests
import json
import time
import warnings
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional, Any

warnings.filterwarnings('ignore')

# Core ML libraries
try:
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
    from sklearn.preprocessing import RobustScaler
    from sklearn.metrics import mean_absolute_error
    import yfinance as yf
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("Warning: ML libraries not available, using fallback mode")

@dataclass
class CleanPrediction:
    """Simplified prediction output"""
    symbol: str
    direction: str  # UP, DOWN, NEUTRAL
    confidence: float  # 0-100
    expected_price: float
    current_price: float
    position_size: str  # SMALL, MEDIUM, LARGE, NONE
    reasoning: str
    timestamp: datetime

class CleanNextDayPredictor:
    """Clean, minimal noise next-day prediction system"""
    
    def __init__(self, symbol: str = "AMD"):
        self.symbol = symbol
        self.scaler = RobustScaler() if ML_AVAILABLE else None
        self.model = None
        self.is_trained = False
        
    def collect_market_data(self) -> Optional[Dict[str, float]]:
        """Collect essential market data without excessive logging"""
        try:
            ticker = yf.Ticker(self.symbol)
            
            # Get current data
            current = ticker.history(period="1d", interval="1m")
            hist_5d = ticker.history(period="5d", interval="1h")
            
            if current.empty or hist_5d.empty:
                return None
                
            current_price = float(current['Close'].iloc[-1])
            prev_close = float(hist_5d['Close'].iloc[-2])
            
            # Calculate essential features
            intraday_change = (current_price - prev_close) / prev_close * 100
            volume_ratio = current['Volume'].iloc[-1] / hist_5d['Volume'].mean()
            volatility = hist_5d['Close'].pct_change().std() * 100
            
            # Simple momentum calculation
            momentum_3h = (current_price - hist_5d['Close'].iloc[-4]) / hist_5d['Close'].iloc[-4] * 100
            
            return {
                'intraday_change': intraday_change,
                'volume_ratio': volume_ratio,
                'volatility': volatility,
                'momentum_3h': momentum_3h,
                'current_price': current_price,
                'prev_close': prev_close
            }
            
        except Exception as e:
            print(f"Data collection error: {e}")
            return None
    
    def calculate_prediction_score(self, data: Dict[str, float]) -> Tuple[str, float, str]:
        """Calculate simple, logical prediction score"""
        score = 0.0
        
        # Intraday momentum component (30% weight)
        if data['intraday_change'] > 1.0:
            score += 0.3  # Strong positive
        elif data['intraday_change'] > 0.2:
            score += 0.15  # Mild positive
        elif data['intraday_change'] < -1.0:
            score -= 0.3  # Strong negative
        elif data['intraday_change'] < -0.2:
            score -= 0.15  # Mild negative
            
        # 3-hour momentum component (40% weight)
        if data['momentum_3h'] > 2.0:
            score += 0.4
        elif data['momentum_3h'] > 0.5:
            score += 0.2
        elif data['momentum_3h'] < -2.0:
            score -= 0.4
        elif data['momentum_3h'] < -0.5:
            score -= 0.2
            
        # Volume component (20% weight)
        if data['volume_ratio'] > 1.5:
            score += 0.15  # High volume supports move
        elif data['volume_ratio'] < 0.7:
            score -= 0.05  # Low volume reduces conviction
            
        # Volatility adjustment (10% weight)
        if data['volatility'] > 3.0:
            score *= 0.9  # High volatility reduces confidence
            
        # Determine direction and confidence
        if score > 0.15:
            direction = "UP"
            confidence = min(abs(score) * 150, 85)  # Cap at 85%
        elif score < -0.15:
            direction = "DOWN"
            confidence = min(abs(score) * 150, 85)
        else:
            direction = "NEUTRAL"
            confidence = 40 + abs(score) * 20
            
        # Position sizing
        if confidence > 75:
            position = "LARGE"
        elif confidence > 60:
            position = "MEDIUM"
        elif confidence > 50:
            position = "SMALL"
        else:
            position = "NONE"
            
        return direction, confidence, position
    
    def make_prediction(self) -> Optional[CleanPrediction]:
        """Make clean next-day prediction"""
        data = self.collect_market_data()
        if not data:
            return None
            
        direction, confidence, position = self.calculate_prediction_score(data)
        
        # Calculate expected price
        if direction == "UP":
            expected_move = 0.5 + (confidence - 50) * 0.03  # Scale with confidence
            expected_price = data['current_price'] * (1 + expected_move / 100)
        elif direction == "DOWN":
            expected_move = -(0.5 + (confidence - 50) * 0.03)
            expected_price = data['current_price'] * (1 + expected_move / 100)
        else:
            expected_price = data['current_price']
            
        # Simple reasoning
        reasoning_parts = []
        if abs(data['intraday_change']) > 1.0:
            reasoning_parts.append(f"Strong intraday move ({data['intraday_change']:+.1f}%)")
        if abs(data['momentum_3h']) > 1.0:
            reasoning_parts.append(f"3h momentum ({data['momentum_3h']:+.1f}%)")
        if data['volume_ratio'] > 1.5:
            reasoning_parts.append("High volume")
        elif data['volume_ratio'] < 0.7:
            reasoning_parts.append("Low volume")
            
        reasoning = "; ".join(reasoning_parts) if reasoning_parts else "Neutral conditions"
        
        return CleanPrediction(
            symbol=self.symbol,
            direction=direction,
            confidence=confidence,
            expected_price=expected_price,
            current_price=data['current_price'],
            position_size=position,
            reasoning=reasoning,
            timestamp=datetime.now()
        )
    
    def display_prediction(self, prediction: CleanPrediction):
        """Clean, minimal display"""
        print(f"\n🎯 NEXT-DAY PREDICTION - {prediction.symbol}")
        print("=" * 50)
        print(f"Direction:      {prediction.direction}")
        print(f"Confidence:     {prediction.confidence:.0f}%")
        print(f"Current Price:  ${prediction.current_price:.2f}")
        print(f"Expected Open:  ${prediction.expected_price:.2f}")
        print(f"Position Size:  {prediction.position_size}")
        print(f"Reasoning:      {prediction.reasoning}")
        print("=" * 50)

def main():
    """Clean main execution"""
    predictor = CleanNextDayPredictor("AMD")
    
    while True:
        try:
            prediction = predictor.make_prediction()
            if prediction:
                predictor.display_prediction(prediction)
            else:
                print("❌ Unable to generate prediction")
                
            time.sleep(30)  # Update every 30 seconds
            
        except KeyboardInterrupt:
            print("\n👋 Stopping prediction system")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    main()