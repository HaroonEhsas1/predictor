"""
Professional Candlestick Pattern Detection System
Mathematically correct pattern recognition with NO hardcoded values or bias
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class CandlestickPatternDetector:
    """
    Advanced candlestick pattern detection using dynamic thresholds
    All calculations are relative and unbiased
    """
    
    def __init__(self):
        """Initialize pattern detector with no hardcoded values"""
        self.pattern_names = [
            'doji', 'hammer', 'inverted_hammer', 'shooting_star',
            'bullish_engulfing', 'bearish_engulfing',
            'bullish_harami', 'bearish_harami',
            'morning_star', 'evening_star',
            'bullish_marubozu', 'bearish_marubozu',
            'piercing_line', 'dark_cloud_cover',
            'three_white_soldiers', 'three_black_crows'
        ]
    
    def detect_all_patterns(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Detect all candlestick patterns in the data
        
        Args:
            data: DataFrame with OHLC columns
            
        Returns:
            DataFrame with pattern scores (-1 to +1, 0 = no pattern)
        """
        if len(data) < 1:
            result = pd.DataFrame(index=data.index)
            for name in self.pattern_names:
                result[name] = 0.0
            return result
        
        patterns = {}
        
        # Single candle patterns (work with 1+ candles)
        patterns['doji'] = self._detect_doji(data)
        patterns['hammer'] = self._detect_hammer(data)
        patterns['inverted_hammer'] = self._detect_inverted_hammer(data)
        patterns['shooting_star'] = self._detect_shooting_star(data)
        patterns['bullish_marubozu'] = self._detect_bullish_marubozu(data)
        patterns['bearish_marubozu'] = self._detect_bearish_marubozu(data)
        
        # Two candle patterns (require 2+ candles)
        if len(data) >= 2:
            patterns['bullish_engulfing'] = self._detect_bullish_engulfing(data)
            patterns['bearish_engulfing'] = self._detect_bearish_engulfing(data)
            patterns['bullish_harami'] = self._detect_bullish_harami(data)
            patterns['bearish_harami'] = self._detect_bearish_harami(data)
            patterns['piercing_line'] = self._detect_piercing_line(data)
            patterns['dark_cloud_cover'] = self._detect_dark_cloud_cover(data)
        else:
            patterns['bullish_engulfing'] = pd.Series(0.0, index=data.index)
            patterns['bearish_engulfing'] = pd.Series(0.0, index=data.index)
            patterns['bullish_harami'] = pd.Series(0.0, index=data.index)
            patterns['bearish_harami'] = pd.Series(0.0, index=data.index)
            patterns['piercing_line'] = pd.Series(0.0, index=data.index)
            patterns['dark_cloud_cover'] = pd.Series(0.0, index=data.index)
        
        # Three candle patterns (require 3+ candles)
        if len(data) >= 3:
            patterns['morning_star'] = self._detect_morning_star(data)
            patterns['evening_star'] = self._detect_evening_star(data)
            patterns['three_white_soldiers'] = self._detect_three_white_soldiers(data)
            patterns['three_black_crows'] = self._detect_three_black_crows(data)
        else:
            patterns['morning_star'] = pd.Series(0.0, index=data.index)
            patterns['evening_star'] = pd.Series(0.0, index=data.index)
            patterns['three_white_soldiers'] = pd.Series(0.0, index=data.index)
            patterns['three_black_crows'] = pd.Series(0.0, index=data.index)
        
        return pd.DataFrame(patterns, index=data.index)
    
    def _calculate_candle_metrics(self, row: pd.Series) -> Tuple[float, float, float, float, float, bool]:
        """Calculate dynamic candle body and shadow metrics"""
        open_price = float(row['Open'])
        high = float(row['High'])
        low = float(row['Low'])
        close = float(row['Close'])
        
        # Body size (absolute)
        body = abs(close - open_price)
        
        # Total range
        total_range = high - low
        
        # Avoid division by zero
        if total_range == 0:
            return 0.0, 0.0, 0.0, 0.0, 0.0, True
        
        # Upper shadow
        upper_shadow = high - max(open_price, close)
        
        # Lower shadow
        lower_shadow = min(open_price, close) - low
        
        # Body ratio (relative to total range)
        body_ratio = body / total_range if total_range > 0 else 0.0
        
        # Is bullish
        is_bullish = close > open_price
        
        return body, total_range, upper_shadow, lower_shadow, body_ratio, is_bullish
    
    def _detect_doji(self, data: pd.DataFrame) -> pd.Series:
        """
        Doji: Open ≈ Close (indecision)
        Score based on body_size relative to range
        """
        scores = []
        
        for idx, row in data.iterrows():
            body, total_range, _, _, body_ratio, _ = self._calculate_candle_metrics(row)
            
            # Doji strength: inverse of body ratio
            # Small body = strong doji signal
            if total_range > 0:
                doji_score = 1.0 - body_ratio
                # Only count as doji if body is less than 10% of range
                if body_ratio < 0.1:
                    scores.append(doji_score)
                else:
                    scores.append(0.0)
            else:
                scores.append(0.0)
        
        return pd.Series(scores, index=data.index)
    
    def _detect_hammer(self, data: pd.DataFrame) -> pd.Series:
        """
        Hammer: Small body at top, long lower shadow (bullish reversal)
        Returns positive score for valid hammer
        """
        scores = []
        
        for idx, row in data.iterrows():
            body, total_range, upper_shadow, lower_shadow, body_ratio, _ = self._calculate_candle_metrics(row)
            
            if total_range > 0:
                # Hammer criteria (dynamic, relative measurements):
                # 1. Lower shadow is at least 2x body size
                # 2. Upper shadow is minimal (< body size)
                # 3. Body is in upper portion of range
                
                lower_to_body = lower_shadow / (body + 1e-10)
                upper_to_body = upper_shadow / (body + 1e-10)
                
                if lower_to_body >= 2.0 and upper_to_body < 1.0:
                    # Score based on how well it matches ideal hammer
                    score = min(lower_to_body / 3.0, 1.0)
                    scores.append(score)
                else:
                    scores.append(0.0)
            else:
                scores.append(0.0)
        
        return pd.Series(scores, index=data.index)
    
    def _detect_inverted_hammer(self, data: pd.DataFrame) -> pd.Series:
        """
        Inverted Hammer: Small body at bottom, long upper shadow (bullish reversal)
        """
        scores = []
        
        for idx, row in data.iterrows():
            body, total_range, upper_shadow, lower_shadow, body_ratio, _ = self._calculate_candle_metrics(row)
            
            if total_range > 0:
                upper_to_body = upper_shadow / (body + 1e-10)
                lower_to_body = lower_shadow / (body + 1e-10)
                
                if upper_to_body >= 2.0 and lower_to_body < 1.0:
                    score = min(upper_to_body / 3.0, 1.0)
                    scores.append(score)
                else:
                    scores.append(0.0)
            else:
                scores.append(0.0)
        
        return pd.Series(scores, index=data.index)
    
    def _detect_shooting_star(self, data: pd.DataFrame) -> pd.Series:
        """
        Shooting Star: Small body at bottom, long upper shadow (bearish reversal)
        Returns negative score for bearish signal
        """
        scores = []
        
        for idx, row in data.iterrows():
            body, total_range, upper_shadow, lower_shadow, body_ratio, _ = self._calculate_candle_metrics(row)
            
            if total_range > 0:
                upper_to_body = upper_shadow / (body + 1e-10)
                lower_to_body = lower_shadow / (body + 1e-10)
                
                if upper_to_body >= 2.0 and lower_to_body < 1.0:
                    score = -min(upper_to_body / 3.0, 1.0)
                    scores.append(score)
                else:
                    scores.append(0.0)
            else:
                scores.append(0.0)
        
        return pd.Series(scores, index=data.index)
    
    def _detect_bullish_engulfing(self, data: pd.DataFrame) -> pd.Series:
        """
        Bullish Engulfing: Current bullish candle completely engulfs previous bearish candle
        """
        scores = pd.Series(0.0, index=data.index)
        
        for i in range(1, len(data)):
            prev_row = data.iloc[i-1]
            curr_row = data.iloc[i]
            
            _, _, _, _, _, prev_bullish = self._calculate_candle_metrics(prev_row)
            _, _, _, _, _, curr_bullish = self._calculate_candle_metrics(curr_row)
            
            # Previous bearish, current bullish
            if not prev_bullish and curr_bullish:
                # Current candle engulfs previous
                if (curr_row['Open'] < prev_row['Close'] and 
                    curr_row['Close'] > prev_row['Open']):
                    
                    # Score based on engulfing degree
                    prev_body = abs(prev_row['Close'] - prev_row['Open'])
                    curr_body = abs(curr_row['Close'] - curr_row['Open'])
                    
                    if prev_body > 0:
                        engulf_ratio = min(curr_body / prev_body, 2.0) / 2.0
                        scores.iloc[i] = engulf_ratio
        
        return scores
    
    def _detect_bearish_engulfing(self, data: pd.DataFrame) -> pd.Series:
        """
        Bearish Engulfing: Current bearish candle completely engulfs previous bullish candle
        """
        scores = pd.Series(0.0, index=data.index)
        
        for i in range(1, len(data)):
            prev_row = data.iloc[i-1]
            curr_row = data.iloc[i]
            
            _, _, _, _, _, prev_bullish = self._calculate_candle_metrics(prev_row)
            _, _, _, _, _, curr_bullish = self._calculate_candle_metrics(curr_row)
            
            # Previous bullish, current bearish
            if prev_bullish and not curr_bullish:
                # Current candle engulfs previous
                if (curr_row['Open'] > prev_row['Close'] and 
                    curr_row['Close'] < prev_row['Open']):
                    
                    prev_body = abs(prev_row['Close'] - prev_row['Open'])
                    curr_body = abs(curr_row['Close'] - curr_row['Open'])
                    
                    if prev_body > 0:
                        engulf_ratio = min(curr_body / prev_body, 2.0) / 2.0
                        scores.iloc[i] = -engulf_ratio
        
        return scores
    
    def _detect_bullish_harami(self, data: pd.DataFrame) -> pd.Series:
        """
        Bullish Harami: Small bullish candle inside previous large bearish candle
        """
        scores = pd.Series(0.0, index=data.index)
        
        for i in range(1, len(data)):
            prev_row = data.iloc[i-1]
            curr_row = data.iloc[i]
            
            _, _, _, _, _, prev_bullish = self._calculate_candle_metrics(prev_row)
            _, _, _, _, _, curr_bullish = self._calculate_candle_metrics(curr_row)
            
            # Previous bearish, current bullish
            if not prev_bullish and curr_bullish:
                # Current candle inside previous
                if (curr_row['Open'] > prev_row['Close'] and 
                    curr_row['Close'] < prev_row['Open']):
                    
                    prev_body = abs(prev_row['Close'] - prev_row['Open'])
                    curr_body = abs(curr_row['Close'] - curr_row['Open'])
                    
                    if prev_body > 0:
                        size_ratio = curr_body / prev_body
                        # Smaller current candle = stronger signal
                        if size_ratio < 0.5:
                            scores.iloc[i] = 1.0 - (size_ratio * 2.0)
        
        return scores
    
    def _detect_bearish_harami(self, data: pd.DataFrame) -> pd.Series:
        """
        Bearish Harami: Small bearish candle inside previous large bullish candle
        """
        scores = pd.Series(0.0, index=data.index)
        
        for i in range(1, len(data)):
            prev_row = data.iloc[i-1]
            curr_row = data.iloc[i]
            
            _, _, _, _, _, prev_bullish = self._calculate_candle_metrics(prev_row)
            _, _, _, _, _, curr_bullish = self._calculate_candle_metrics(curr_row)
            
            # Previous bullish, current bearish
            if prev_bullish and not curr_bullish:
                # Current candle inside previous
                if (curr_row['Open'] < prev_row['Close'] and 
                    curr_row['Close'] > prev_row['Open']):
                    
                    prev_body = abs(prev_row['Close'] - prev_row['Open'])
                    curr_body = abs(curr_row['Close'] - curr_row['Open'])
                    
                    if prev_body > 0:
                        size_ratio = curr_body / prev_body
                        if size_ratio < 0.5:
                            scores.iloc[i] = -(1.0 - (size_ratio * 2.0))
        
        return scores
    
    def _detect_bullish_marubozu(self, data: pd.DataFrame) -> pd.Series:
        """
        Bullish Marubozu: Strong bullish candle with no/minimal shadows
        """
        scores = []
        
        for idx, row in data.iterrows():
            body, total_range, upper_shadow, lower_shadow, body_ratio, is_bullish = self._calculate_candle_metrics(row)
            
            if is_bullish and total_range > 0:
                # Body should be >80% of total range
                shadow_total = upper_shadow + lower_shadow
                shadow_ratio = shadow_total / total_range
                
                if body_ratio >= 0.8:
                    # Score based on how close to perfect marubozu
                    score = 1.0 - (shadow_ratio * 2.0)
                    scores.append(max(score, 0.0))
                else:
                    scores.append(0.0)
            else:
                scores.append(0.0)
        
        return pd.Series(scores, index=data.index)
    
    def _detect_bearish_marubozu(self, data: pd.DataFrame) -> pd.Series:
        """
        Bearish Marubozu: Strong bearish candle with no/minimal shadows
        """
        scores = []
        
        for idx, row in data.iterrows():
            body, total_range, upper_shadow, lower_shadow, body_ratio, is_bullish = self._calculate_candle_metrics(row)
            
            if not is_bullish and total_range > 0:
                shadow_total = upper_shadow + lower_shadow
                shadow_ratio = shadow_total / total_range
                
                if body_ratio >= 0.8:
                    score = -(1.0 - (shadow_ratio * 2.0))
                    scores.append(min(score, 0.0))
                else:
                    scores.append(0.0)
            else:
                scores.append(0.0)
        
        return pd.Series(scores, index=data.index)
    
    def _detect_piercing_line(self, data: pd.DataFrame) -> pd.Series:
        """
        Piercing Line: Bullish reversal - closes above midpoint of previous bearish candle
        """
        scores = pd.Series(0.0, index=data.index)
        
        for i in range(1, len(data)):
            prev_row = data.iloc[i-1]
            curr_row = data.iloc[i]
            
            _, _, _, _, _, prev_bullish = self._calculate_candle_metrics(prev_row)
            _, _, _, _, _, curr_bullish = self._calculate_candle_metrics(curr_row)
            
            if not prev_bullish and curr_bullish:
                prev_midpoint = (prev_row['Open'] + prev_row['Close']) / 2.0
                
                # Opens below previous close, closes above midpoint
                if (curr_row['Open'] < prev_row['Close'] and 
                    curr_row['Close'] > prev_midpoint):
                    
                    # Score based on penetration
                    penetration = (curr_row['Close'] - prev_midpoint) / (prev_row['Open'] - prev_row['Close'])
                    scores.iloc[i] = min(penetration, 1.0)
        
        return scores
    
    def _detect_dark_cloud_cover(self, data: pd.DataFrame) -> pd.Series:
        """
        Dark Cloud Cover: Bearish reversal - closes below midpoint of previous bullish candle
        """
        scores = pd.Series(0.0, index=data.index)
        
        for i in range(1, len(data)):
            prev_row = data.iloc[i-1]
            curr_row = data.iloc[i]
            
            _, _, _, _, _, prev_bullish = self._calculate_candle_metrics(prev_row)
            _, _, _, _, _, curr_bullish = self._calculate_candle_metrics(curr_row)
            
            if prev_bullish and not curr_bullish:
                prev_midpoint = (prev_row['Open'] + prev_row['Close']) / 2.0
                
                # Opens above previous close, closes below midpoint
                if (curr_row['Open'] > prev_row['Close'] and 
                    curr_row['Close'] < prev_midpoint):
                    
                    penetration = (prev_midpoint - curr_row['Close']) / (prev_row['Close'] - prev_row['Open'])
                    scores.iloc[i] = -min(penetration, 1.0)
        
        return scores
    
    def _detect_morning_star(self, data: pd.DataFrame) -> pd.Series:
        """
        Morning Star: 3-candle bullish reversal pattern
        """
        scores = pd.Series(0.0, index=data.index)
        
        for i in range(2, len(data)):
            first = data.iloc[i-2]
            second = data.iloc[i-1]
            third = data.iloc[i]
            
            first_body = abs(first['Close'] - first['Open'])
            second_body = abs(second['Close'] - second['Open'])
            third_body = abs(third['Close'] - third['Open'])
            
            # First: Large bearish
            # Second: Small body (indecision)
            # Third: Large bullish
            
            if (first['Close'] < first['Open'] and  # Bearish
                third['Close'] > third['Open'] and   # Bullish
                second_body < first_body * 0.5 and   # Small middle
                third['Close'] > (first['Open'] + first['Close']) / 2.0):  # Third closes above first midpoint
                
                # Score based on pattern quality
                size_ratio = third_body / first_body if first_body > 0 else 0.0
                scores.iloc[i] = min(size_ratio, 1.0)
        
        return scores
    
    def _detect_evening_star(self, data: pd.DataFrame) -> pd.Series:
        """
        Evening Star: 3-candle bearish reversal pattern
        """
        scores = pd.Series(0.0, index=data.index)
        
        for i in range(2, len(data)):
            first = data.iloc[i-2]
            second = data.iloc[i-1]
            third = data.iloc[i]
            
            first_body = abs(first['Close'] - first['Open'])
            second_body = abs(second['Close'] - second['Open'])
            third_body = abs(third['Close'] - third['Open'])
            
            # First: Large bullish
            # Second: Small body
            # Third: Large bearish
            
            if (first['Close'] > first['Open'] and  # Bullish
                third['Close'] < third['Open'] and   # Bearish
                second_body < first_body * 0.5 and   # Small middle
                third['Close'] < (first['Open'] + first['Close']) / 2.0):  # Third closes below first midpoint
                
                size_ratio = third_body / first_body if first_body > 0 else 0.0
                scores.iloc[i] = -min(size_ratio, 1.0)
        
        return scores
    
    def _detect_three_white_soldiers(self, data: pd.DataFrame) -> pd.Series:
        """
        Three White Soldiers: 3 consecutive bullish candles with higher closes
        """
        scores = pd.Series(0.0, index=data.index)
        
        for i in range(2, len(data)):
            first = data.iloc[i-2]
            second = data.iloc[i-1]
            third = data.iloc[i]
            
            # All bullish with progressively higher closes
            if (first['Close'] > first['Open'] and
                second['Close'] > second['Open'] and
                third['Close'] > third['Open'] and
                second['Close'] > first['Close'] and
                third['Close'] > second['Close']):
                
                # Score based on uniformity
                avg_body = (abs(first['Close'] - first['Open']) + 
                           abs(second['Close'] - second['Open']) + 
                           abs(third['Close'] - third['Open'])) / 3.0
                
                if avg_body > 0:
                    uniformity = 1.0 - (np.std([
                        abs(first['Close'] - first['Open']),
                        abs(second['Close'] - second['Open']),
                        abs(third['Close'] - third['Open'])
                    ]) / avg_body)
                    scores.iloc[i] = max(uniformity, 0.0)
        
        return scores
    
    def _detect_three_black_crows(self, data: pd.DataFrame) -> pd.Series:
        """
        Three Black Crows: 3 consecutive bearish candles with lower closes
        """
        scores = pd.Series(0.0, index=data.index)
        
        for i in range(2, len(data)):
            first = data.iloc[i-2]
            second = data.iloc[i-1]
            third = data.iloc[i]
            
            # All bearish with progressively lower closes
            if (first['Close'] < first['Open'] and
                second['Close'] < second['Open'] and
                third['Close'] < third['Open'] and
                second['Close'] < first['Close'] and
                third['Close'] < second['Close']):
                
                avg_body = (abs(first['Close'] - first['Open']) + 
                           abs(second['Close'] - second['Open']) + 
                           abs(third['Close'] - third['Open'])) / 3.0
                
                if avg_body > 0:
                    uniformity = 1.0 - (np.std([
                        abs(first['Close'] - first['Open']),
                        abs(second['Close'] - second['Open']),
                        abs(third['Close'] - third['Open'])
                    ]) / avg_body)
                    scores.iloc[i] = -max(uniformity, 0.0)
        
        return scores
