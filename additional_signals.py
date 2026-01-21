"""
Additional Signal Sources - Phase 1 (FREE)
Adds 3 high-quality signals to break ties and get clearer predictions
"""
import yfinance as yf
import pandas as pd
from typing import Dict, Any

class AdditionalSignals:
    """Additional high-quality signals for better prediction confidence"""
    
    def __init__(self, symbol: str):
        self.symbol = symbol
        
        # Map stocks to their sector ETFs
        self.sector_etfs = {
            'AMD': 'SMH',      # Semiconductors
            'NVDA': 'SMH',
            'AVGO': 'SMH',
            'QCOM': 'SMH',
            'ORCL': 'XLK',     # Technology
            'MSFT': 'XLK',
            'GOOGL': 'XLK'
        }
    
    def get_relative_strength(self) -> Dict[str, Any]:
        """
        Signal #1: Relative Strength vs Sector
        If stock outperforms sector → Bullish
        If stock underperforms sector → Bearish
        """
        print("\n📊 Relative Strength Analysis...")
        
        result = {'score': 0.0, 'outperformance': 0.0, 'sector_etf': '', 'has_data': False}
        
        try:
            # Get sector ETF
            sector_etf = self.sector_etfs.get(self.symbol, 'SPY')
            result['sector_etf'] = sector_etf
            
            # Get stock and sector data (last 5 days)
            stock = yf.Ticker(self.symbol)
            sector = yf.Ticker(sector_etf)
            
            stock_hist = stock.history(period='5d')
            sector_hist = sector.history(period='5d')
            
            if len(stock_hist) >= 2 and len(sector_hist) >= 2:
                # Calculate 1-day performance
                stock_change = ((stock_hist['Close'].iloc[-1] - stock_hist['Close'].iloc[-2]) 
                               / stock_hist['Close'].iloc[-2]) * 100
                sector_change = ((sector_hist['Close'].iloc[-1] - sector_hist['Close'].iloc[-2]) 
                                / sector_hist['Close'].iloc[-2]) * 100
                
                # Calculate outperformance
                outperformance = stock_change - sector_change
                result['outperformance'] = outperformance
                result['has_data'] = True
                
                # Score based on relative strength
                if outperformance > 1.0:
                    result['score'] = 0.06  # Strong outperformance
                    print(f"   ✅ {self.symbol} OUTPERFORMING {sector_etf} by {outperformance:+.2f}%")
                    print(f"      {self.symbol}: {stock_change:+.2f}% vs {sector_etf}: {sector_change:+.2f}%")
                    print(f"      → Bullish (relative strength)")
                elif outperformance > 0.3:
                    result['score'] = 0.03  # Moderate outperformance
                    print(f"   ✅ {self.symbol} slightly outperforming {sector_etf} by {outperformance:+.2f}%")
                elif outperformance < -1.0:
                    result['score'] = -0.06  # Strong underperformance
                    print(f"   ⚠️ {self.symbol} UNDERPERFORMING {sector_etf} by {outperformance:.2f}%")
                    print(f"      {self.symbol}: {stock_change:+.2f}% vs {sector_etf}: {sector_change:+.2f}%")
                    print(f"      → Bearish (relative weakness)")
                elif outperformance < -0.3:
                    result['score'] = -0.03  # Moderate underperformance
                    print(f"   ⚠️ {self.symbol} slightly underperforming {sector_etf} by {outperformance:.2f}%")
                else:
                    result['score'] = 0.0  # In-line with sector
                    print(f"   ➡️ {self.symbol} performing in-line with {sector_etf} ({outperformance:+.2f}%)")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)[:50]}")
        
        return result
    
    def get_money_flow_index(self) -> Dict[str, Any]:
        """
        Signal #2: Money Flow Index (MFI)
        Like RSI but includes volume
        MFI > 80 = Overbought (bearish)
        MFI < 20 = Oversold (bullish)
        """
        print("\n💰 Money Flow Index Analysis...")
        
        result = {'score': 0.0, 'mfi': 50, 'signal': 'neutral', 'has_data': False}
        
        try:
            stock = yf.Ticker(self.symbol)
            hist = stock.history(period='30d')
            
            if len(hist) >= 14:
                # Calculate Money Flow Index
                typical_price = (hist['High'] + hist['Low'] + hist['Close']) / 3
                money_flow = typical_price * hist['Volume']
                
                # Positive and negative money flow
                positive_flow = []
                negative_flow = []
                
                for i in range(1, len(typical_price)):
                    if typical_price.iloc[i] > typical_price.iloc[i-1]:
                        positive_flow.append(money_flow.iloc[i])
                        negative_flow.append(0)
                    else:
                        positive_flow.append(0)
                        negative_flow.append(money_flow.iloc[i])
                
                # Calculate MFI (14-period)
                positive_mf = pd.Series(positive_flow).rolling(14).sum().iloc[-1]
                negative_mf = pd.Series(negative_flow).rolling(14).sum().iloc[-1]
                
                if negative_mf != 0:
                    mfi_ratio = positive_mf / negative_mf
                    mfi = 100 - (100 / (1 + mfi_ratio))
                    result['mfi'] = mfi
                    result['has_data'] = True
                    
                    # Score based on MFI
                    if mfi > 80:
                        result['score'] = -0.05  # Overbought - bearish
                        result['signal'] = 'overbought'
                        print(f"   ⚠️ MFI: {mfi:.1f} - OVERBOUGHT")
                        print(f"      Too much buying pressure → Reversal likely")
                    elif mfi > 70:
                        result['score'] = -0.02  # Getting overbought
                        result['signal'] = 'high'
                        print(f"   ⚠️ MFI: {mfi:.1f} - High (approaching overbought)")
                    elif mfi < 20:
                        result['score'] = +0.05  # Oversold - bullish
                        result['signal'] = 'oversold'
                        print(f"   💡 MFI: {mfi:.1f} - OVERSOLD")
                        print(f"      Too much selling pressure → Bounce likely")
                    elif mfi < 30:
                        result['score'] = +0.02  # Getting oversold
                        result['signal'] = 'low'
                        print(f"   💡 MFI: {mfi:.1f} - Low (approaching oversold)")
                    else:
                        result['score'] = 0.0  # Neutral
                        result['signal'] = 'neutral'
                        print(f"   ➡️ MFI: {mfi:.1f} - Neutral")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)[:50]}")
        
        return result
    
    def get_bollinger_bands(self) -> Dict[str, Any]:
        """
        Signal #3: Bollinger Band Position
        Price near upper band = Overbought (mean revert down)
        Price near lower band = Oversold (mean revert up)
        """
        print("\n📉 Bollinger Bands Analysis...")
        
        result = {'score': 0.0, 'position': 'middle', 'percent_b': 0.5, 'has_data': False}
        
        try:
            stock = yf.Ticker(self.symbol)
            hist = stock.history(period='30d')
            
            if len(hist) >= 20:
                # Calculate Bollinger Bands (20-day, 2 std dev)
                sma = hist['Close'].rolling(20).mean()
                std = hist['Close'].rolling(20).std()
                
                upper_band = sma + (2 * std)
                lower_band = sma - (2 * std)
                
                current_price = hist['Close'].iloc[-1]
                current_upper = upper_band.iloc[-1]
                current_lower = lower_band.iloc[-1]
                current_sma = sma.iloc[-1]
                
                # Calculate %B (position within bands)
                band_width = current_upper - current_lower
                if band_width > 0:
                    percent_b = (current_price - current_lower) / band_width
                    result['percent_b'] = percent_b
                    result['has_data'] = True
                    
                    print(f"   Current Price: ${current_price:.2f}")
                    print(f"   Upper Band: ${current_upper:.2f}")
                    print(f"   Middle (SMA): ${current_sma:.2f}")
                    print(f"   Lower Band: ${current_lower:.2f}")
                    print(f"   Position: {percent_b*100:.1f}% of band width")
                    
                    # Score based on position
                    if percent_b > 0.95:
                        result['score'] = -0.04  # Very near upper band
                        result['position'] = 'upper_extreme'
                        print(f"   ⚠️ NEAR UPPER BAND - Overbought, pullback likely")
                    elif percent_b > 0.80:
                        result['score'] = -0.02  # Approaching upper band
                        result['position'] = 'upper'
                        print(f"   ⚠️ Approaching upper band - Getting extended")
                    elif percent_b < 0.05:
                        result['score'] = +0.04  # Very near lower band
                        result['position'] = 'lower_extreme'
                        print(f"   💡 NEAR LOWER BAND - Oversold, bounce likely")
                    elif percent_b < 0.20:
                        result['score'] = +0.02  # Approaching lower band
                        result['position'] = 'lower'
                        print(f"   💡 Approaching lower band - Getting oversold")
                    else:
                        result['score'] = 0.0  # Middle of bands
                        result['position'] = 'middle'
                        print(f"   ➡️ In middle of bands - No extreme")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)[:50]}")
        
        return result
    
    def get_all_signals(self) -> Dict[str, Any]:
        """Get all additional signals"""
        return {
            'relative_strength': self.get_relative_strength(),
            'money_flow_index': self.get_money_flow_index(),
            'bollinger_bands': self.get_bollinger_bands()
        }

# Test the signals
if __name__ == "__main__":
    import sys
    
    symbol = sys.argv[1] if len(sys.argv) > 1 else 'ORCL'
    
    print("="*80)
    print(f"TESTING ADDITIONAL SIGNALS - {symbol}")
    print("="*80)
    
    signals = AdditionalSignals(symbol)
    results = signals.get_all_signals()
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    total_score = 0
    for name, data in results.items():
        score = data.get('score', 0)
        total_score += score
        print(f"\n{name.replace('_', ' ').title()}: {score:+.3f}")
    
    print(f"\n{'='*80}")
    print(f"TOTAL ADDITIONAL SCORE: {total_score:+.3f}")
    print(f"{'='*80}")
    
    if total_score > 0.05:
        print(f"\n✅ Additional signals are BULLISH (+{total_score:.3f})")
    elif total_score < -0.05:
        print(f"\n⚠️ Additional signals are BEARISH ({total_score:.3f})")
    else:
        print(f"\n➡️ Additional signals are NEUTRAL ({total_score:+.3f})")
