"""
PREMARKET MARKET DATA ANALYZER
Fetches futures and sector data for premarket analysis

Features:
- ES/NQ futures real-time
- Sector ETF premarket (SMH, XLC)
- Alignment checking
- Correlation scoring
"""

import yfinance as yf
from datetime import datetime
import pytz
from typing import Dict, Any
from premarket_config import get_stock_config

class PremarketMarketData:
    """
    Fetches and analyzes market context for premarket
    """
    
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.config = get_stock_config(symbol)
    
    def get_futures_data(self) -> Dict[str, Any]:
        """
        Get ES and NQ futures data
        """
        
        print(f"\n📈 Fetching Futures Data...")
        
        try:
            # ES (S&P 500 futures)
            es = yf.Ticker('ES=F')
            es_info = es.info
            es_hist = es.history(period='2d')
            
            # NQ (Nasdaq futures)
            nq = yf.Ticker('NQ=F')
            nq_info = nq.info
            nq_hist = nq.history(period='2d')
            
            # Calculate changes
            if len(es_hist) >= 2:
                es_prev = es_hist['Close'].iloc[-2]
                es_current = es_info.get('regularMarketPrice', es_hist['Close'].iloc[-1])
                es_change_pct = ((es_current - es_prev) / es_prev) * 100
            else:
                es_change_pct = 0
            
            if len(nq_hist) >= 2:
                nq_prev = nq_hist['Close'].iloc[-2]
                nq_current = nq_info.get('regularMarketPrice', nq_hist['Close'].iloc[-1])
                nq_change_pct = ((nq_current - nq_prev) / nq_prev) * 100
            else:
                nq_change_pct = 0
            
            # Average for overall futures direction
            avg_futures = (es_change_pct + nq_change_pct) / 2
            
            # Determine direction
            if avg_futures > 0.3:
                direction = 'BULLISH'
            elif avg_futures < -0.3:
                direction = 'BEARISH'
            else:
                direction = 'NEUTRAL'
            
            data = {
                'has_data': True,
                'es_change': es_change_pct,
                'nq_change': nq_change_pct,
                'avg_change': avg_futures,
                'direction': direction
            }
            
            print(f"   ES: {es_change_pct:+.2f}%")
            print(f"   NQ: {nq_change_pct:+.2f}%")
            print(f"   Direction: {direction}")
            
            return data
            
        except Exception as e:
            print(f"   ⚠️ Error: {e}")
            return {
                'has_data': False,
                'direction': 'UNKNOWN',
                'avg_change': 0
            }
    
    def get_sector_data(self) -> Dict[str, Any]:
        """
        Get sector ETF data
        """
        
        print(f"\n📊 Fetching Sector Data...")
        
        sector_etf = self.config.get('sector_etf', 'SPY')
        
        try:
            etf = yf.Ticker(sector_etf)
            etf_info = etf.info
            etf_hist = etf.history(period='2d')
            
            # Calculate change
            if len(etf_hist) >= 2:
                prev_close = etf_hist['Close'].iloc[-2]
                current_price = etf_info.get('regularMarketPrice', etf_hist['Close'].iloc[-1])
                change_pct = ((current_price - prev_close) / prev_close) * 100
            else:
                change_pct = 0
            
            # Get premarket if available
            premarket_price = etf_info.get('preMarketPrice', current_price)
            premarket_change = ((premarket_price - prev_close) / prev_close) * 100
            
            # Determine direction
            if premarket_change > 0.5:
                direction = 'BULLISH'
            elif premarket_change < -0.5:
                direction = 'BEARISH'
            else:
                direction = 'NEUTRAL'
            
            data = {
                'has_data': True,
                'sector_etf': sector_etf,
                'change_pct': change_pct,
                'premarket_change': premarket_change,
                'direction': direction
            }
            
            print(f"   Sector ({sector_etf}): {premarket_change:+.2f}%")
            print(f"   Direction: {direction}")
            
            return data
            
        except Exception as e:
            print(f"   ⚠️ Error: {e}")
            return {
                'has_data': False,
                'sector_etf': sector_etf,
                'direction': 'UNKNOWN',
                'change_pct': 0
            }
    
    def check_alignment(self, stock_gap_direction: str, 
                       futures_data: Dict[str, Any],
                       sector_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check if stock gap aligns with futures and sector
        
        Args:
            stock_gap_direction: 'up' or 'down'
            futures_data: Futures analysis
            sector_data: Sector analysis
        
        Returns:
            Alignment analysis with confidence boost
        """
        
        print(f"\n🔄 Checking Alignment...")
        
        alignments = []
        confidence_boost = 0
        
        # Check futures alignment
        if futures_data.get('has_data'):
            futures_dir = futures_data['direction']
            
            if stock_gap_direction == 'up' and futures_dir == 'BULLISH':
                alignments.append('Futures aligned (bullish)')
                confidence_boost += 10
            elif stock_gap_direction == 'down' and futures_dir == 'BEARISH':
                alignments.append('Futures aligned (bearish)')
                confidence_boost += 10
            elif stock_gap_direction == 'up' and futures_dir == 'BEARISH':
                alignments.append('Futures CONFLICT (bearish)')
                confidence_boost -= 15
            elif stock_gap_direction == 'down' and futures_dir == 'BULLISH':
                alignments.append('Futures CONFLICT (bullish)')
                confidence_boost -= 15
            else:
                alignments.append('Futures neutral')
        
        # Check sector alignment
        if sector_data.get('has_data'):
            sector_dir = sector_data['direction']
            
            if stock_gap_direction == 'up' and sector_dir == 'BULLISH':
                alignments.append('Sector aligned (bullish)')
                confidence_boost += 8
            elif stock_gap_direction == 'down' and sector_dir == 'BEARISH':
                alignments.append('Sector aligned (bearish)')
                confidence_boost += 8
            elif stock_gap_direction == 'up' and sector_dir == 'BEARISH':
                alignments.append('Sector CONFLICT (bearish)')
                confidence_boost -= 10
            elif stock_gap_direction == 'down' and sector_dir == 'BULLISH':
                alignments.append('Sector CONFLICT (bullish)')
                confidence_boost -= 10
            else:
                alignments.append('Sector neutral')
        
        # Overall alignment
        if confidence_boost >= 15:
            alignment = 'STRONG_ALIGNED'
        elif confidence_boost >= 5:
            alignment = 'ALIGNED'
        elif confidence_boost >= -5:
            alignment = 'NEUTRAL'
        elif confidence_boost >= -15:
            alignment = 'WEAK_CONFLICT'
        else:
            alignment = 'STRONG_CONFLICT'
        
        result = {
            'alignment': alignment,
            'confidence_boost': confidence_boost,
            'details': alignments
        }
        
        print(f"   Alignment: {alignment}")
        print(f"   Boost: {confidence_boost:+.0f}%")
        for detail in alignments:
            print(f"      • {detail}")
        
        return result
    
    def get_complete_market_context(self, stock_gap_direction: str) -> Dict[str, Any]:
        """
        Get complete market context analysis
        """
        
        # Fetch data
        futures = self.get_futures_data()
        sector = self.get_sector_data()
        
        # Check alignment
        alignment = self.check_alignment(stock_gap_direction, futures, sector)
        
        return {
            'futures': futures,
            'sector': sector,
            'alignment': alignment
        }


if __name__ == "__main__":
    # Test
    print("\n" + "="*80)
    print("PREMARKET MARKET DATA - TEST")
    print("="*80)
    
    for symbol in ['NVDA', 'META']:
        analyzer = PremarketMarketData(symbol)
        
        # Test with up gap
        result = analyzer.get_complete_market_context('up')
        
        print(f"\n{symbol} (simulated UP gap):")
        print(f"   Futures: {result['futures']['direction']}")
        print(f"   Sector: {result['sector']['direction']}")
        print(f"   Alignment: {result['alignment']['alignment']}")
        print(f"   Boost: {result['alignment']['confidence_boost']:+.0f}%")
        
        print("\n")
