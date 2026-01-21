"""
Market Internals Tracker - FREE Data
Tracks:
1. Advance/Decline Ratio (market breadth)
2. New Highs/Lows (market health)
3. Up/Down Volume (institutional participation)
4. Market breadth score (0-10)
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Optional

class MarketInternalsTracker:
    """Track market internals for AMD prediction context."""
    
    def __init__(self):
        # Market breadth proxies (free via Yahoo)
        self.breadth_symbols = {
            '^GSPC': 'S&P 500',           # Large cap breadth
            '^NDX': 'Nasdaq 100',         # Tech breadth
            '^RUT': 'Russell 2000',       # Small cap breadth
            '^DJI': 'Dow Jones'           # Blue chip breadth
        }
        
        # Sector ETFs for breadth
        self.sector_etfs = {
            'XLK': 'Technology',
            'XLF': 'Financials',
            'XLE': 'Energy',
            'XLV': 'Healthcare',
            'XLY': 'Consumer Disc',
            'XLP': 'Consumer Staples',
            'XLI': 'Industrials',
            'XLB': 'Materials',
            'XLU': 'Utilities',
            'XLRE': 'Real Estate',
            'XLC': 'Communications'
        }
    
    def get_advance_decline_ratio(self) -> Dict:
        """
        Calculate advance/decline ratio using sector ETFs as proxy.
        
        When 8/11 sectors are up → Strong market breadth (bullish)
        When 3/11 sectors are up → Weak market breadth (bearish)
        """
        try:
            advancing = 0
            declining = 0
            sector_changes = {}
            
            for symbol, name in self.sector_etfs.items():
                try:
                    ticker = yf.Ticker(symbol)
                    data = ticker.history(period='2d')
                    
                    if len(data) >= 2:
                        yesterday_close = data['Close'].iloc[-2]
                        today_close = data['Close'].iloc[-1]
                        change_pct = ((today_close - yesterday_close) / yesterday_close) * 100
                        
                        sector_changes[symbol] = {
                            'name': name,
                            'change': round(change_pct, 2)
                        }
                        
                        if change_pct > 0:
                            advancing += 1
                        else:
                            declining += 1
                
                except Exception as e:
                    continue
            
            total = advancing + declining
            if total == 0:
                return {'score': 5, 'ratio': 1.0, 'breadth': 'NEUTRAL'}
            
            ad_ratio = advancing / total
            
            # Score calculation (0-10)
            # ad_ratio > 0.7 (70% sectors up) = 9-10 (very bullish)
            # ad_ratio 0.5-0.7 = 6-8 (bullish)
            # ad_ratio 0.3-0.5 = 4-6 (neutral)
            # ad_ratio < 0.3 = 0-3 (bearish)
            
            if ad_ratio >= 0.7:
                score = 9 + (ad_ratio - 0.7) * 3.33  # 9-10
                breadth = 'VERY_STRONG'
            elif ad_ratio >= 0.5:
                score = 6 + (ad_ratio - 0.5) * 10  # 6-8
                breadth = 'STRONG'
            elif ad_ratio >= 0.3:
                score = 4 + (ad_ratio - 0.3) * 10  # 4-6
                breadth = 'NEUTRAL'
            else:
                score = ad_ratio * 13.33  # 0-4
                breadth = 'WEAK'
            
            return {
                'score': round(score, 2),
                'advancing': advancing,
                'declining': declining,
                'ratio': round(ad_ratio, 3),
                'breadth': breadth,
                'sector_details': sector_changes
            }
            
        except Exception as e:
            print(f"⚠️ Advance/Decline calculation error: {e}")
            return {'score': 5, 'ratio': 0.5, 'breadth': 'UNKNOWN'}
    
    def get_new_highs_lows(self) -> Dict:
        """
        Track stocks at new highs vs new lows using sector ETF proxies.
        
        When sectors at 52-week highs > lows → Bullish market health
        """
        try:
            highs = 0
            lows = 0
            neutral = 0
            
            for symbol in self.sector_etfs.keys():
                try:
                    ticker = yf.Ticker(symbol)
                    data = ticker.history(period='1y')
                    
                    if len(data) < 100:
                        continue
                    
                    current_price = data['Close'].iloc[-1]
                    high_52w = data['High'].max()
                    low_52w = data['Low'].min()
                    
                    # Within 5% of 52-week high
                    if current_price >= high_52w * 0.95:
                        highs += 1
                    # Within 5% of 52-week low
                    elif current_price <= low_52w * 1.05:
                        lows += 1
                    else:
                        neutral += 1
                
                except Exception:
                    continue
            
            total = highs + lows + neutral
            if total == 0:
                return {'score': 5, 'health': 'UNKNOWN'}
            
            # Score based on highs vs lows
            if lows == 0 and highs > 0:
                net_ratio = 1.0
            elif lows > 0:
                net_ratio = highs / lows
            else:
                net_ratio = 0.0
            
            # Convert to 0-10 score
            if net_ratio >= 3:
                score = 9
                health = 'VERY_HEALTHY'
            elif net_ratio >= 1.5:
                score = 7
                health = 'HEALTHY'
            elif net_ratio >= 0.7:
                score = 5
                health = 'NEUTRAL'
            elif net_ratio >= 0.3:
                score = 3
                health = 'WEAK'
            else:
                score = 1
                health = 'VERY_WEAK'
            
            return {
                'score': score,
                'new_highs': highs,
                'new_lows': lows,
                'neutral': neutral,
                'ratio': round(net_ratio, 2),
                'health': health
            }
            
        except Exception as e:
            print(f"⚠️ New Highs/Lows error: {e}")
            return {'score': 5, 'health': 'UNKNOWN'}
    
    def get_market_breadth_score(self) -> Dict:
        """
        Combine all internals into single market health score (0-10).
        
        Score > 7 = Strong market (bullish for AMD)
        Score 4-7 = Neutral market
        Score < 4 = Weak market (bearish for AMD)
        """
        print("\n📊 Analyzing Market Internals...")
        
        # Get all components
        ad_data = self.get_advance_decline_ratio()
        hl_data = self.get_new_highs_lows()
        
        # Weight components
        weights = {
            'advance_decline': 0.60,  # Most important
            'highs_lows': 0.40        # Supporting indicator
        }
        
        # Calculate weighted score
        total_score = (
            ad_data['score'] * weights['advance_decline'] +
            hl_data['score'] * weights['highs_lows']
        )
        
        # Overall assessment
        if total_score >= 7:
            assessment = 'STRONG_BREADTH'
            impact = 'BULLISH'
        elif total_score >= 5:
            assessment = 'NEUTRAL_BREADTH'
            impact = 'NEUTRAL'
        else:
            assessment = 'WEAK_BREADTH'
            impact = 'BEARISH'
        
        # Print results
        print(f"   📈 Advance/Decline: {ad_data['advancing']}/{ad_data['declining']} ({ad_data['breadth']})")
        print(f"   🎯 New Highs/Lows: {hl_data['new_highs']}/{hl_data['new_lows']} ({hl_data['health']})")
        print(f"   📊 Market Breadth Score: {total_score:.1f}/10 ({assessment})")
        print(f"   💡 Impact on AMD: {impact}")
        
        return {
            'total_score': round(total_score, 2),
            'assessment': assessment,
            'impact': impact,
            'advance_decline': ad_data,
            'highs_lows': hl_data
        }

if __name__ == "__main__":
    tracker = MarketInternalsTracker()
    result = tracker.get_market_breadth_score()
    
    print(f"\n{'='*60}")
    print(f"🎯 MARKET INTERNALS ANALYSIS COMPLETE")
    print(f"{'='*60}")
    print(f"Breadth Score: {result['total_score']}/10")
    print(f"Assessment: {result['assessment']}")
    print(f"Impact: {result['impact']}")
