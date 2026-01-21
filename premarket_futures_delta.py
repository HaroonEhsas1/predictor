"""
FUTURES DELTA ANALYSIS
Analyzes recent futures momentum for gap prediction

Features:
- ES/NQ delta last 30-60 minutes
- Momentum building/fading detection
- Acceleration scoring
"""

import yfinance as yf
import pandas as pd
from typing import Dict, Any
from datetime import datetime, timedelta
import pytz

class FuturesDeltaAnalyzer:
    """
    Analyzes futures momentum in last 30-60 minutes
    """
    
    def __init__(self):
        self.es = yf.Ticker('ES=F')
        self.nq = yf.Ticker('NQ=F')
    
    def analyze_futures_delta(self, gap_direction: str) -> Dict[str, Any]:
        """
        Analyze futures delta in last 30-60 minutes
        
        Returns:
        - delta_30min: change in last 30 mins
        - delta_60min: change in last 60 mins
        - momentum: building/fading/stable
        - confidence_adjustment: ±10%
        """
        
        print(f"\n📈 Futures Delta Analysis...")
        
        try:
            # Get intraday data (1 day, 5-min intervals)
            es_hist = self.es.history(period='1d', interval='5m')
            nq_hist = self.nq.history(period='1d', interval='5m')
            
            if len(es_hist) < 12 or len(nq_hist) < 12:
                print("   ⚠️ Insufficient futures data")
                return self._no_data_result()
            
            # Get recent prices
            es_current = es_hist['Close'].iloc[-1]
            es_30min = es_hist['Close'].iloc[-7] if len(es_hist) >= 7 else es_hist['Close'].iloc[0]  # 6x5min = 30min
            es_60min = es_hist['Close'].iloc[-13] if len(es_hist) >= 13 else es_hist['Close'].iloc[0]  # 12x5min = 60min
            
            nq_current = nq_hist['Close'].iloc[-1]
            nq_30min = nq_hist['Close'].iloc[-7] if len(nq_hist) >= 7 else nq_hist['Close'].iloc[0]
            nq_60min = nq_hist['Close'].iloc[-13] if len(nq_hist) >= 13 else nq_hist['Close'].iloc[0]
            
            # Calculate deltas
            es_delta_30 = ((es_current - es_30min) / es_30min) * 100
            es_delta_60 = ((es_current - es_60min) / es_60min) * 100
            
            nq_delta_30 = ((nq_current - nq_30min) / nq_30min) * 100
            nq_delta_60 = ((nq_current - nq_60min) / nq_60min) * 100
            
            # Average for overall futures momentum
            avg_delta_30 = (es_delta_30 + nq_delta_30) / 2
            avg_delta_60 = (es_delta_60 + nq_delta_60) / 2
            
            # Determine momentum pattern
            momentum, confidence_adj = self._analyze_momentum_pattern(
                avg_delta_30,
                avg_delta_60,
                gap_direction
            )
            
            # Check acceleration
            acceleration = avg_delta_30 - (avg_delta_60 / 2)  # Is 30min faster than 60min pace?
            
            if abs(acceleration) > 0.1:
                accelerating = acceleration > 0
            else:
                accelerating = None
            
            result = {
                'has_data': True,
                'es_delta_30': es_delta_30,
                'es_delta_60': es_delta_60,
                'nq_delta_30': nq_delta_30,
                'nq_delta_60': nq_delta_60,
                'avg_delta_30': avg_delta_30,
                'avg_delta_60': avg_delta_60,
                'momentum': momentum,
                'accelerating': accelerating,
                'confidence_adjustment': confidence_adj
            }
            
            print(f"   ES 30min: {es_delta_30:+.2f}%")
            print(f"   NQ 30min: {nq_delta_30:+.2f}%")
            print(f"   Momentum: {momentum}")
            print(f"   Accelerating: {'✅ YES' if accelerating else '❌ NO' if accelerating is False else '➖ STABLE'}")
            print(f"   Confidence Adjust: {confidence_adj:+.0f}%")
            
            return result
            
        except Exception as e:
            print(f"   ⚠️ Futures delta error: {e}")
            return self._no_data_result()
    
    def _analyze_momentum_pattern(self, delta_30: float, delta_60: float, 
                                  gap_direction: str) -> tuple:
        """
        Analyze momentum pattern and calculate confidence adjustment
        
        Patterns:
        - Building: 30min > 60min, aligned with gap
        - Fading: 30min < 60min, against gap
        - Strong: Both 30 and 60 aligned with gap
        - Weak: Both against gap
        """
        
        confidence_adj = 0
        
        # Determine futures direction
        if delta_30 > 0.2:
            futures_direction_30 = 'up'
        elif delta_30 < -0.2:
            futures_direction_30 = 'down'
        else:
            futures_direction_30 = 'neutral'
        
        if delta_60 > 0.2:
            futures_direction_60 = 'up'
        elif delta_60 < -0.2:
            futures_direction_60 = 'down'
        else:
            futures_direction_60 = 'neutral'
        
        # Check momentum building/fading
        if abs(delta_30) > abs(delta_60) * 1.2:
            # Momentum building
            momentum = 'BUILDING'
            
            # Check alignment with gap
            if gap_direction == futures_direction_30:
                confidence_adj += 10  # Strong confirmation
            else:
                confidence_adj -= 8   # Conflict
        
        elif abs(delta_30) < abs(delta_60) * 0.8:
            # Momentum fading
            momentum = 'FADING'
            
            # Check alignment
            if gap_direction == futures_direction_60:
                confidence_adj -= 5   # Was strong, now fading
            else:
                confidence_adj += 5   # Was against, now fading (good)
        
        else:
            # Stable momentum
            momentum = 'STABLE'
            
            # Check alignment
            if gap_direction == futures_direction_30:
                confidence_adj += 5   # Steady support
            else:
                confidence_adj -= 5   # Steady resistance
        
        # Cap adjustment
        confidence_adj = max(-10, min(10, confidence_adj))
        
        return momentum, confidence_adj
    
    def _no_data_result(self) -> Dict[str, Any]:
        """Return default when no data"""
        
        return {
            'has_data': False,
            'avg_delta_30': 0,
            'momentum': 'UNKNOWN',
            'confidence_adjustment': 0
        }


if __name__ == "__main__":
    # Test
    print("\n" + "="*80)
    print("FUTURES DELTA ANALYZER - TEST")
    print("="*80)
    
    analyzer = FuturesDeltaAnalyzer()
    result = analyzer.analyze_futures_delta('up')
    
    print(f"\nSummary:")
    if result['has_data']:
        print(f"   30min Delta: {result['avg_delta_30']:+.2f}%")
        print(f"   60min Delta: {result['avg_delta_60']:+.2f}%")
        print(f"   Momentum: {result['momentum']}")
        print(f"   Adjustment: {result['confidence_adjustment']:+.0f}%")
    else:
        print("   No futures delta data")
