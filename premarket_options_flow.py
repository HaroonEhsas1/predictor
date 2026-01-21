"""
OPTIONS FLOW ANALYSIS
Analyzes options activity to predict gap continuation

Features:
- Put/Call ratio analysis
- Unusual options activity
- Options volume surge detection
- Gamma exposure estimation
"""

import yfinance as yf
import pandas as pd
import numpy as np
from typing import Dict, Any
from datetime import datetime, timedelta

class OptionsFlowAnalyzer:
    """
    Analyzes options flow for premarket predictions
    """
    
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.stock = yf.Ticker(symbol)
    
    def analyze_options_flow(self, gap_direction: str) -> Dict[str, Any]:
        """
        Complete options flow analysis
        
        Returns:
        - put_call_ratio: ratio
        - options_sentiment: bullish/bearish/neutral
        - unusual_activity: bool
        - confidence_adjustment: ±15%
        """
        
        print(f"\n📊 Options Flow Analysis...")
        
        try:
            # Get available option dates
            options_dates = self.stock.options
            
            if not options_dates or len(options_dates) == 0:
                print("   ⚠️ No options data available")
                return self._no_data_result()
            
            # Use nearest expiration (most liquid)
            nearest_expiry = options_dates[0]
            
            # Get options chain
            chain = self.stock.option_chain(nearest_expiry)
            calls = chain.calls
            puts = chain.puts
            
            # Calculate metrics
            total_call_volume = calls['volume'].sum()
            total_put_volume = puts['volume'].sum()
            
            total_call_oi = calls['openInterest'].sum()
            total_put_oi = puts['openInterest'].sum()
            
            # Put/Call ratios
            pc_volume_ratio = total_put_volume / total_call_volume if total_call_volume > 0 else 1.0
            pc_oi_ratio = total_put_oi / total_call_oi if total_call_oi > 0 else 1.0
            
            # Get current price
            current_price = self.stock.info.get('regularMarketPrice', 0)
            
            # Find ATM strike
            atm_strike = self._find_atm_strike(calls, current_price)
            
            # Analyze unusual activity
            unusual_activity, unusual_details = self._detect_unusual_activity(calls, puts)
            
            # Determine sentiment
            sentiment, confidence_adj = self._determine_options_sentiment(
                pc_volume_ratio, 
                pc_oi_ratio,
                gap_direction,
                unusual_activity
            )
            
            # Estimate gamma exposure
            gamma_estimate = self._estimate_gamma_exposure(calls, puts, current_price)
            
            result = {
                'has_data': True,
                'pc_volume_ratio': pc_volume_ratio,
                'pc_oi_ratio': pc_oi_ratio,
                'call_volume': total_call_volume,
                'put_volume': total_put_volume,
                'sentiment': sentiment,
                'confidence_adjustment': confidence_adj,
                'unusual_activity': unusual_activity,
                'unusual_details': unusual_details,
                'gamma_exposure': gamma_estimate,
                'expiry_date': nearest_expiry
            }
            
            print(f"   P/C Volume Ratio: {pc_volume_ratio:.2f}")
            print(f"   P/C OI Ratio: {pc_oi_ratio:.2f}")
            print(f"   Sentiment: {sentiment}")
            print(f"   Unusual Activity: {'⚠️ YES' if unusual_activity else '✅ NO'}")
            print(f"   Confidence Adjust: {confidence_adj:+.0f}%")
            
            if unusual_details:
                print(f"   Unusual: {unusual_details}")
            
            return result
            
        except Exception as e:
            print(f"   ⚠️ Options analysis error: {e}")
            return self._no_data_result()
    
    def _find_atm_strike(self, calls: pd.DataFrame, current_price: float) -> float:
        """Find at-the-money strike"""
        
        if len(calls) == 0 or current_price == 0:
            return 0
        
        # Find closest strike to current price
        calls['price_diff'] = abs(calls['strike'] - current_price)
        atm_strike = calls.loc[calls['price_diff'].idxmin(), 'strike']
        
        return atm_strike
    
    def _detect_unusual_activity(self, calls: pd.DataFrame, puts: pd.DataFrame) -> tuple:
        """
        Detect unusual options activity
        
        Unusual = volume > 2x open interest (fresh activity)
        """
        
        # Check calls
        calls['vol_oi_ratio'] = calls['volume'] / calls['openInterest'].replace(0, 1)
        unusual_calls = calls[calls['vol_oi_ratio'] > 2.0]
        
        # Check puts
        puts['vol_oi_ratio'] = puts['volume'] / puts['openInterest'].replace(0, 1)
        unusual_puts = puts[puts['vol_oi_ratio'] > 2.0]
        
        has_unusual = len(unusual_calls) > 0 or len(unusual_puts) > 0
        
        details = []
        if len(unusual_calls) > 0:
            details.append(f"{len(unusual_calls)} unusual call strikes")
        if len(unusual_puts) > 0:
            details.append(f"{len(unusual_puts)} unusual put strikes")
        
        return has_unusual, ", ".join(details) if details else None
    
    def _determine_options_sentiment(self, pc_volume: float, pc_oi: float, 
                                     gap_direction: str, unusual: bool) -> tuple:
        """
        Determine options sentiment and confidence adjustment
        
        Logic:
        - P/C > 1.5 = Excessive fear = Contrarian BULLISH
        - P/C < 0.7 = Excessive greed = Contrarian BEARISH
        - P/C 0.8-1.2 = Neutral
        - Unusual activity = +5% if aligned with gap
        """
        
        confidence_adj = 0
        
        # Analyze P/C ratio (contrarian)
        if pc_volume > 1.5:
            # Excessive put buying = fear = contrarian bullish
            sentiment = 'CONTRARIAN_BULLISH'
            if gap_direction == 'up':
                confidence_adj += 12  # Confirms bullish gap
            else:
                confidence_adj -= 8   # Conflicts with bearish gap
        
        elif pc_volume < 0.7:
            # Excessive call buying = greed = contrarian bearish
            sentiment = 'CONTRARIAN_BEARISH'
            if gap_direction == 'down':
                confidence_adj += 12  # Confirms bearish gap
            else:
                confidence_adj -= 8   # Conflicts with bullish gap
        
        elif 0.8 <= pc_volume <= 1.2:
            # Balanced = neutral
            sentiment = 'NEUTRAL'
            confidence_adj = 0
        
        else:
            # Moderate levels
            if pc_volume > 1.0:
                sentiment = 'SLIGHTLY_BEARISH'
                confidence_adj = -3 if gap_direction == 'up' else +3
            else:
                sentiment = 'SLIGHTLY_BULLISH'
                confidence_adj = +3 if gap_direction == 'up' else -3
        
        # Add bonus for unusual activity (smart money)
        if unusual:
            if sentiment in ['CONTRARIAN_BULLISH', 'SLIGHTLY_BULLISH']:
                confidence_adj += 5
            elif sentiment in ['CONTRARIAN_BEARISH', 'SLIGHTLY_BEARISH']:
                confidence_adj += 5
        
        # Cap adjustment
        confidence_adj = max(-15, min(15, confidence_adj))
        
        return sentiment, confidence_adj
    
    def _estimate_gamma_exposure(self, calls: pd.DataFrame, puts: pd.DataFrame, 
                                 current_price: float) -> Dict[str, Any]:
        """
        Estimate gamma exposure (simplified)
        
        Identifies potential pin levels
        """
        
        # Find strikes with highest open interest
        calls_by_strike = calls.groupby('strike')['openInterest'].sum()
        puts_by_strike = puts.groupby('strike')['openInterest'].sum()
        
        # Combine
        total_oi = calls_by_strike.add(puts_by_strike, fill_value=0)
        
        if len(total_oi) == 0:
            return {'regime': 'UNKNOWN', 'pin_levels': []}
        
        # Find top 3 strikes
        top_strikes = total_oi.nlargest(3).index.tolist()
        
        # Determine if near a pin
        nearest_pin = min(top_strikes, key=lambda x: abs(x - current_price))
        distance_to_pin = abs(current_price - nearest_pin) / current_price
        
        if distance_to_pin < 0.02:  # Within 2%
            regime = 'GAMMA_PIN'
        else:
            regime = 'NORMAL'
        
        return {
            'regime': regime,
            'pin_levels': top_strikes,
            'nearest_pin': nearest_pin,
            'distance_pct': distance_to_pin * 100
        }
    
    def _no_data_result(self) -> Dict[str, Any]:
        """Return default result when no options data"""
        
        return {
            'has_data': False,
            'pc_volume_ratio': 1.0,
            'sentiment': 'UNKNOWN',
            'confidence_adjustment': 0,
            'unusual_activity': False
        }


if __name__ == "__main__":
    # Test
    print("\n" + "="*80)
    print("OPTIONS FLOW ANALYZER - TEST")
    print("="*80)
    
    for symbol in ['NVDA', 'META']:
        analyzer = OptionsFlowAnalyzer(symbol)
        result = analyzer.analyze_options_flow('up')
        
        print(f"\n{symbol} Summary:")
        if result['has_data']:
            print(f"   P/C Ratio: {result['pc_volume_ratio']:.2f}")
            print(f"   Sentiment: {result['sentiment']}")
            print(f"   Adjustment: {result['confidence_adjustment']:+.0f}%")
            print(f"   Unusual: {result['unusual_activity']}")
        else:
            print("   No options data available")
        
        print("\n")
