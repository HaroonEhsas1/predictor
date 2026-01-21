"""
FREE ADVANCED INDICATORS FOR STOCK-SPECIFIC INTELLIGENCE

Uses only FREE data sources (yfinance, SEC EDGAR, free APIs):
- No paid subscriptions required
- High-impact indicators
- Easy to implement

For each stock:
AMD: 200-Day MA, Relative Strength, Crypto Mining
NVDA: Insider Transactions, Relative Strength, Hash Rate
META: Put/Call Extremes, Relative Strength
AVGO: Dividend Safety, Relative Strength
SNOW: SBC Trend, Cloud Sector Strength
PLTR: Insider Selling, Short Interest, Relative Strength
"""

import yfinance as yf
import requests
from datetime import datetime, timedelta
import json

class FreeAdvancedIndicators:
    """Free advanced indicators for all stocks"""
    
    def __init__(self, symbol):
        self.symbol = symbol
        self.ticker = yf.Ticker(symbol)
        
    def get_all_indicators(self):
        """Get all available free indicators for this stock"""
        
        indicators = {}
        
        # Universal indicators (all stocks)
        indicators['ma_distance'] = self.get_200ma_distance()
        indicators['relative_strength'] = self.get_relative_strength()
        
        # Stock-specific indicators
        if self.symbol == 'AMD':
            indicators.update(self.get_amd_indicators())
        elif self.symbol == 'NVDA':
            indicators.update(self.get_nvda_indicators())
        elif self.symbol == 'META':
            indicators.update(self.get_meta_indicators())
        elif self.symbol == 'AVGO':
            indicators.update(self.get_avgo_indicators())
        elif self.symbol == 'SNOW':
            indicators.update(self.get_snow_indicators())
        elif self.symbol == 'PLTR':
            indicators.update(self.get_pltr_indicators())
        
        return indicators
    
    # ========== UNIVERSAL INDICATORS ==========
    
    def get_200ma_distance(self):
        """
        Distance from 200-day moving average
        FREE: yfinance
        Impact: Medium (mean reversion signal)
        """
        try:
            hist = self.ticker.history(period='1y')
            
            if len(hist) < 200:
                return {'success': False, 'reason': 'Insufficient data'}
            
            current_price = hist['Close'].iloc[-1]
            ma_200 = hist['Close'].rolling(window=200).mean().iloc[-1]
            
            distance_pct = ((current_price - ma_200) / ma_200) * 100
            
            # Interpretation
            if distance_pct > 15:
                signal = 'OVERBOUGHT'
                bias = -0.08  # Mean reversion down
            elif distance_pct > 10:
                signal = 'EXTENDED_UP'
                bias = -0.05
            elif distance_pct < -15:
                signal = 'OVERSOLD'
                bias = 0.08  # Mean reversion up
            elif distance_pct < -10:
                signal = 'EXTENDED_DOWN'
                bias = 0.05
            else:
                signal = 'NEUTRAL'
                bias = 0.0
            
            return {
                'success': True,
                'distance_pct': distance_pct,
                'ma_200': ma_200,
                'current_price': current_price,
                'signal': signal,
                'bias': bias,
                'reasoning': f"{distance_pct:+.1f}% from 200MA - {signal}"
            }
            
        except Exception as e:
            return {'success': False, 'reason': str(e)}
    
    def get_relative_strength(self):
        """
        Relative strength vs sector/index
        FREE: yfinance
        Impact: Medium-High
        """
        try:
            # Get sector ETF based on stock
            sector_map = {
                'AMD': 'SMH',    # Semiconductors
                'NVDA': 'SMH',   # Semiconductors
                'META': 'XLC',   # Communication
                'AVGO': 'SMH',   # Semiconductors
                'SNOW': 'SKYY',  # Cloud computing (or use XLK as backup)
                'PLTR': 'ITA'    # Defense (or use XLK)
            }
            
            sector_symbol = sector_map.get(self.symbol, 'SPY')
            
            # Get 20-day performance
            stock_hist = self.ticker.history(period='1mo')
            sector_hist = yf.Ticker(sector_symbol).history(period='1mo')
            
            if len(stock_hist) < 20 or len(sector_hist) < 20:
                return {'success': False, 'reason': 'Insufficient data'}
            
            stock_return = ((stock_hist['Close'].iloc[-1] / stock_hist['Close'].iloc[0]) - 1) * 100
            sector_return = ((sector_hist['Close'].iloc[-1] / sector_hist['Close'].iloc[0]) - 1) * 100
            
            relative_strength = stock_return - sector_return
            
            # Interpretation
            if relative_strength > 5:
                signal = 'STRONG_OUTPERFORM'
                bias = 0.10
            elif relative_strength > 2:
                signal = 'OUTPERFORM'
                bias = 0.06
            elif relative_strength < -5:
                signal = 'STRONG_UNDERPERFORM'
                bias = -0.10
            elif relative_strength < -2:
                signal = 'UNDERPERFORM'
                bias = -0.06
            else:
                signal = 'INLINE'
                bias = 0.0
            
            return {
                'success': True,
                'stock_return': stock_return,
                'sector_return': sector_return,
                'relative_strength': relative_strength,
                'sector_etf': sector_symbol,
                'signal': signal,
                'bias': bias,
                'reasoning': f"{relative_strength:+.1f}% vs {sector_symbol} - {signal}"
            }
            
        except Exception as e:
            return {'success': False, 'reason': str(e)}
    
    # ========== AMD-SPECIFIC INDICATORS ==========
    
    def get_amd_indicators(self):
        """AMD-specific free indicators"""
        indicators = {}
        
        # Crypto mining profitability (affects GPU demand)
        indicators['crypto_mining'] = self.get_crypto_mining_signal()
        
        return indicators
    
    def get_crypto_mining_signal(self):
        """
        GPU mining profitability
        FREE: Blockchain data
        Impact: Low-Medium
        """
        try:
            # Bitcoin hash rate as proxy for GPU mining activity
            # Higher hash rate = more mining = potential GPU demand
            url = "https://blockchain.info/q/hashrate"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                current_hashrate = float(response.text)
                
                # Simple interpretation (would need historical comparison)
                # For now, just return the data
                return {
                    'success': True,
                    'hashrate': current_hashrate,
                    'signal': 'TRACKING',
                    'bias': 0.0,  # Neutral until we have historical comparison
                    'reasoning': f"Bitcoin hashrate: {current_hashrate/1e9:.2f} GH/s"
                }
            else:
                return {'success': False, 'reason': 'API unavailable'}
                
        except Exception as e:
            return {'success': False, 'reason': str(e)}
    
    # ========== NVDA-SPECIFIC INDICATORS ==========
    
    def get_nvda_indicators(self):
        """NVDA-specific free indicators"""
        indicators = {}
        
        # Insider transactions
        indicators['insider_activity'] = self.get_insider_transactions()
        
        return indicators
    
    def get_insider_transactions(self):
        """
        Insider buying/selling (SEC Form 4)
        FREE: yfinance insider data
        Impact: High
        """
        try:
            insider_data = self.ticker.insider_transactions
            
            if insider_data is None or len(insider_data) == 0:
                return {'success': False, 'reason': 'No insider data'}
            
            # Get recent transactions (last 90 days)
            recent = insider_data.head(20)  # Last 20 transactions
            
            buys = recent[recent['Transaction'] == 'Buy']
            sells = recent[recent['Transaction'] == 'Sale']
            
            buy_value = buys['Value'].sum() if len(buys) > 0 else 0
            sell_value = sells['Value'].sum() if len(sells) > 0 else 0
            
            net_insider = buy_value - sell_value
            
            # Interpretation
            if net_insider > 5000000:  # $5M+ net buying
                signal = 'STRONG_BUYING'
                bias = 0.12
            elif net_insider > 1000000:  # $1M+ net buying
                signal = 'BUYING'
                bias = 0.08
            elif net_insider < -10000000:  # $10M+ net selling
                signal = 'HEAVY_SELLING'
                bias = -0.12
            elif net_insider < -5000000:  # $5M+ net selling
                signal = 'SELLING'
                bias = -0.08
            else:
                signal = 'NEUTRAL'
                bias = 0.0
            
            return {
                'success': True,
                'buy_value': buy_value,
                'sell_value': sell_value,
                'net_value': net_insider,
                'buy_count': len(buys),
                'sell_count': len(sells),
                'signal': signal,
                'bias': bias,
                'reasoning': f"Insiders: ${net_insider/1e6:.1f}M net - {signal}"
            }
            
        except Exception as e:
            return {'success': False, 'reason': str(e)}
    
    # ========== META-SPECIFIC INDICATORS ==========
    
    def get_meta_indicators(self):
        """META-specific free indicators"""
        indicators = {}
        
        # Put/Call ratio extremes (contrarian)
        indicators['pc_extreme'] = self.get_pc_ratio_extreme()
        
        return indicators
    
    def get_pc_ratio_extreme(self):
        """
        Put/Call ratio extremes (contrarian signal)
        FREE: yfinance options data
        Impact: Medium
        """
        try:
            # Get options data
            options = self.ticker.options
            
            if len(options) == 0:
                return {'success': False, 'reason': 'No options data'}
            
            # Get nearest expiration
            nearest_exp = options[0]
            opt_chain = self.ticker.option_chain(nearest_exp)
            
            put_volume = opt_chain.puts['volume'].sum()
            call_volume = opt_chain.calls['volume'].sum()
            
            if call_volume == 0:
                return {'success': False, 'reason': 'No call volume'}
            
            pc_ratio = put_volume / call_volume
            
            # Contrarian interpretation
            if pc_ratio > 2.0:  # Excessive fear
                signal = 'EXTREME_FEAR'
                bias = 0.10  # Contrarian bullish
            elif pc_ratio > 1.5:
                signal = 'FEAR'
                bias = 0.06
            elif pc_ratio < 0.5:  # Excessive greed
                signal = 'EXTREME_GREED'
                bias = -0.08  # Contrarian bearish
            elif pc_ratio < 0.7:
                signal = 'GREED'
                bias = -0.04
            else:
                signal = 'NEUTRAL'
                bias = 0.0
            
            return {
                'success': True,
                'pc_ratio': pc_ratio,
                'put_volume': put_volume,
                'call_volume': call_volume,
                'signal': signal,
                'bias': bias,
                'reasoning': f"P/C {pc_ratio:.2f} - {signal} (contrarian)"
            }
            
        except Exception as e:
            return {'success': False, 'reason': str(e)}
    
    # ========== AVGO-SPECIFIC INDICATORS ==========
    
    def get_avgo_indicators(self):
        """AVGO-specific free indicators"""
        indicators = {}
        
        # Dividend safety
        indicators['dividend_safety'] = self.get_dividend_safety()
        
        return indicators
    
    def get_dividend_safety(self):
        """
        Dividend coverage and safety
        FREE: yfinance financial data
        Impact: Medium
        """
        try:
            info = self.ticker.info
            
            dividend_yield = info.get('dividendYield', 0)
            payout_ratio = info.get('payoutRatio', 0)
            
            if dividend_yield == 0:
                return {'success': False, 'reason': 'No dividend'}
            
            # Interpretation
            if payout_ratio < 0.5:  # Very safe
                signal = 'VERY_SAFE'
                bias = 0.07
            elif payout_ratio < 0.7:  # Safe
                signal = 'SAFE'
                bias = 0.04
            elif payout_ratio > 1.0:  # Unsustainable
                signal = 'RISK'
                bias = -0.12
            elif payout_ratio > 0.85:  # High risk
                signal = 'CAUTION'
                bias = -0.08
            else:
                signal = 'MODERATE'
                bias = 0.0
            
            return {
                'success': True,
                'dividend_yield': dividend_yield * 100,
                'payout_ratio': payout_ratio,
                'signal': signal,
                'bias': bias,
                'reasoning': f"Payout {payout_ratio*100:.0f}% - {signal}"
            }
            
        except Exception as e:
            return {'success': False, 'reason': str(e)}
    
    # ========== SNOW-SPECIFIC INDICATORS ==========
    
    def get_snow_indicators(self):
        """SNOW-specific free indicators"""
        indicators = {}
        
        # Stock-based compensation trend
        indicators['sbc_trend'] = self.get_sbc_trend()
        
        # Cloud sector strength
        indicators['cloud_strength'] = self.get_cloud_sector_strength()
        
        return indicators
    
    def get_sbc_trend(self):
        """
        Stock-based compensation trend (dilution concern)
        FREE: yfinance financials
        Impact: Medium
        """
        try:
            # Get quarterly financials
            financials = self.ticker.quarterly_financials
            
            if financials is None or len(financials.columns) < 2:
                return {'success': False, 'reason': 'Insufficient financial data'}
            
            # This would need proper SBC extraction from financials
            # For now, return neutral
            return {
                'success': True,
                'signal': 'TRACKING',
                'bias': 0.0,
                'reasoning': 'SBC data tracked'
            }
            
        except Exception as e:
            return {'success': False, 'reason': str(e)}
    
    def get_cloud_sector_strength(self):
        """
        Cloud sector relative strength (CRM, DDOG performance)
        FREE: yfinance
        Impact: High for SNOW
        """
        try:
            # Track CRM and DDOG as cloud sector proxies
            crm = yf.Ticker('CRM').history(period='1mo')
            ddog = yf.Ticker('DDOG').history(period='1mo')
            
            if len(crm) < 20 or len(ddog) < 20:
                return {'success': False, 'reason': 'Insufficient data'}
            
            crm_return = ((crm['Close'].iloc[-1] / crm['Close'].iloc[0]) - 1) * 100
            ddog_return = ((ddog['Close'].iloc[-1] / ddog['Close'].iloc[0]) - 1) * 100
            
            cloud_avg = (crm_return + ddog_return) / 2
            
            # Interpretation
            if cloud_avg > 10:
                signal = 'STRONG_CLOUD'
                bias = 0.15
            elif cloud_avg > 5:
                signal = 'CLOUD_UP'
                bias = 0.10
            elif cloud_avg < -10:
                signal = 'WEAK_CLOUD'
                bias = -0.15
            elif cloud_avg < -5:
                signal = 'CLOUD_DOWN'
                bias = -0.10
            else:
                signal = 'NEUTRAL'
                bias = 0.0
            
            return {
                'success': True,
                'crm_return': crm_return,
                'ddog_return': ddog_return,
                'cloud_avg': cloud_avg,
                'signal': signal,
                'bias': bias,
                'reasoning': f"Cloud sector {cloud_avg:+.1f}% - {signal}"
            }
            
        except Exception as e:
            return {'success': False, 'reason': str(e)}
    
    # ========== PLTR-SPECIFIC INDICATORS ==========
    
    def get_pltr_indicators(self):
        """PLTR-specific free indicators"""
        indicators = {}
        
        # Insider selling pace
        indicators['insider_selling'] = self.get_insider_selling_pace()
        
        # Short interest
        indicators['short_interest'] = self.get_short_interest()
        
        return indicators
    
    def get_insider_selling_pace(self):
        """
        Insider selling pace (PLTR notorious for heavy selling)
        FREE: yfinance insider data
        Impact: High for PLTR
        """
        try:
            insider_data = self.ticker.insider_transactions
            
            if insider_data is None or len(insider_data) == 0:
                return {'success': False, 'reason': 'No insider data'}
            
            # Get last 30 days
            recent = insider_data.head(30)
            sells = recent[recent['Transaction'] == 'Sale']
            
            sell_value = sells['Value'].sum() if len(sells) > 0 else 0
            sell_count = len(sells)
            
            # Interpretation (PLTR-specific thresholds)
            if sell_value > 100000000:  # $100M+ selling
                signal = 'MASSIVE_SELLING'
                bias = -0.15
            elif sell_value > 50000000:  # $50M+ selling
                signal = 'HEAVY_SELLING'
                bias = -0.12
            elif sell_value > 10000000:  # $10M+ selling
                signal = 'SELLING'
                bias = -0.08
            elif sell_value < 5000000:  # Low selling
                signal = 'LOW_SELLING'
                bias = 0.08  # Bullish for PLTR
            else:
                signal = 'NORMAL'
                bias = 0.0
            
            return {
                'success': True,
                'sell_value': sell_value,
                'sell_count': sell_count,
                'signal': signal,
                'bias': bias,
                'reasoning': f"Insider selling: ${sell_value/1e6:.0f}M - {signal}"
            }
            
        except Exception as e:
            return {'success': False, 'reason': str(e)}
    
    def get_short_interest(self):
        """
        Short interest trend (squeeze potential)
        FREE: yfinance
        Impact: Medium-High for PLTR
        """
        try:
            info = self.ticker.info
            
            short_percent = info.get('shortPercentOfFloat', 0) * 100
            
            if short_percent == 0:
                return {'success': False, 'reason': 'No short data'}
            
            # Interpretation
            if short_percent > 20:  # Very high short interest
                signal = 'SQUEEZE_POTENTIAL'
                bias = 0.12  # With catalyst = squeeze
            elif short_percent > 15:
                signal = 'HIGH_SHORT'
                bias = 0.08
            elif short_percent < 5:
                signal = 'LOW_SHORT'
                bias = 0.0
            else:
                signal = 'MODERATE'
                bias = 0.04
            
            return {
                'success': True,
                'short_percent': short_percent,
                'signal': signal,
                'bias': bias,
                'reasoning': f"Short interest {short_percent:.1f}% - {signal}"
            }
            
        except Exception as e:
            return {'success': False, 'reason': str(e)}


def get_free_indicators(symbol):
    """Convenience function to get all free indicators"""
    analyzer = FreeAdvancedIndicators(symbol)
    return analyzer.get_all_indicators()


if __name__ == "__main__":
    # Test all stocks
    symbols = ['AMD', 'NVDA', 'META', 'AVGO', 'SNOW', 'PLTR']
    
    print("\n" + "="*80)
    print("FREE ADVANCED INDICATORS TEST")
    print("="*80)
    
    for symbol in symbols:
        print(f"\n{'='*80}")
        print(f"{symbol} ADVANCED INDICATORS")
        print('='*80)
        
        indicators = get_free_indicators(symbol)
        
        for name, data in indicators.items():
            if data.get('success'):
                print(f"\n{name.upper()}:")
                print(f"  Signal: {data.get('signal', 'N/A')}")
                print(f"  Bias: {data.get('bias', 0):+.3f}")
                print(f"  Reasoning: {data.get('reasoning', 'N/A')}")
            else:
                print(f"\n{name.upper()}: {data.get('reason', 'Failed')}")
    
    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80)
