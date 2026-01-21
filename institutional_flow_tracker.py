"""FREE Institutional Flow Tracker - No Premium Data Needed

Tracks smart money activity using free data sources:
1. After-hours volume spikes (institutions trade AH)
2. Block trades (unusual large volume bars)
3. Dark pool proxies (3x ETF sentiment)
4. Insider transactions (SEC EDGAR)
5. Unusual options activity
6. FINRA short interest (delayed but free)
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
from typing import Dict, Optional

class InstitutionalFlowTracker:
    """Track institutional activity using free data sources."""
    
    def __init__(self, symbol="AMD"):
        self.symbol = symbol
    
    def detect_after_hours_activity(self) -> Dict:
        """Detect institutional after-hours trading (they dominate AH)."""
        try:
            ticker = yf.Ticker(self.symbol)
            
            # Get extended hours data (includes pre-market and after-hours)
            data = ticker.history(period="5d", interval="1m", prepost=True)
            
            if len(data) == 0:
                return {'score': 0, 'activity': 'UNKNOWN'}
            
            # Identify after-hours periods (4 PM - 8 PM ET)
            data['hour'] = data.index.hour
            ah_data = data[(data['hour'] >= 16) & (data['hour'] < 20)]
            
            if len(ah_data) == 0:
                return {'score': 0, 'activity': 'NO_DATA'}
            
            # Calculate AH volume vs regular hours
            regular_vol = data[(data['hour'] >= 9) & (data['hour'] < 16)]['Volume'].mean()
            ah_vol = ah_data['Volume'].mean()
            
            if regular_vol == 0:
                return {'score': 0, 'activity': 'NO_DATA'}
            
            ah_ratio = ah_vol / regular_vol
            
            # High AH volume = institutional positioning
            if ah_ratio > 0.5:  # AH volume > 50% of regular hours
                activity = 'HIGH_INSTITUTIONAL'
                score = min(ah_ratio * 2, 10)
            elif ah_ratio > 0.3:
                activity = 'MODERATE_INSTITUTIONAL'
                score = ah_ratio * 5
            else:
                activity = 'LOW_INSTITUTIONAL'
                score = ah_ratio * 2
            
            # Get AH price direction
            if len(ah_data) >= 2:
                ah_start = ah_data.iloc[0]['Close']
                ah_end = ah_data.iloc[-1]['Close']
                ah_change = ((ah_end - ah_start) / ah_start) * 100
            else:
                ah_change = 0
            
            return {
                'score': round(score, 2),
                'activity': activity,
                'ah_volume_ratio': round(ah_ratio, 3),
                'ah_price_change': round(ah_change, 3),
                'direction': 'UP' if ah_change > 0 else 'DOWN',
                'signal_strength': 'STRONG' if abs(ah_change) > 0.5 else 'WEAK'
            }
            
        except Exception as e:
            print(f"⚠️ After-hours detection error: {e}")
            return {'score': 0, 'activity': 'ERROR'}
    
    def detect_block_trades(self) -> Dict:
        """Detect block trades (large institutional orders)."""
        try:
            ticker = yf.Ticker(self.symbol)
            data = ticker.history(period="5d", interval="5m")
            
            if len(data) < 20:
                return {'score': 0, 'blocks_detected': 0}
            
            # Calculate average volume
            avg_volume = data['Volume'].rolling(window=20).mean()
            
            # Block trade = volume > 10x average
            blocks = data[data['Volume'] > avg_volume * 10]
            
            if len(blocks) == 0:
                return {'score': 0, 'blocks_detected': 0, 'direction': 'NEUTRAL'}
            
            # Analyze block trade direction
            block_directions = []
            for idx, block in blocks.iterrows():
                # If close > open → buying pressure
                if block['Close'] > block['Open']:
                    block_directions.append('BUY')
                else:
                    block_directions.append('SELL')
            
            buy_blocks = sum(1 for d in block_directions if d == 'BUY')
            sell_blocks = sum(1 for d in block_directions if d == 'SELL')
            
            # Net institutional sentiment
            if buy_blocks > sell_blocks:
                direction = 'BULLISH'
                score = (buy_blocks / len(blocks)) * 10
            elif sell_blocks > buy_blocks:
                direction = 'BEARISH'
                score = (sell_blocks / len(blocks)) * 10
            else:
                direction = 'NEUTRAL'
                score = 5
            
            return {
                'score': round(score, 2),
                'blocks_detected': len(blocks),
                'buy_blocks': buy_blocks,
                'sell_blocks': sell_blocks,
                'direction': direction,
                'net_sentiment': buy_blocks - sell_blocks
            }
            
        except Exception as e:
            print(f"⚠️ Block trade detection error: {e}")
            return {'score': 0, 'blocks_detected': 0}
    
    def analyze_dark_pool_proxies(self) -> Dict:
        """Analyze 3x leveraged ETFs as dark pool sentiment proxies."""
        try:
            # 3x ETFs are often used by institutions for hedging
            # SOXL = 3x bull semiconductor
            # SOXS = 3x bear semiconductor
            
            soxl = yf.Ticker("SOXL").history(period="5d")
            soxs = yf.Ticker("SOXS").history(period="5d")
            
            if len(soxl) < 2 or len(soxs) < 2:
                return {'score': 0, 'sentiment': 'UNKNOWN'}
            
            # Calculate momentum
            soxl_change = (soxl['Close'].iloc[-1] / soxl['Close'].iloc[-2] - 1) * 100
            soxs_change = (soxs['Close'].iloc[-1] / soxs['Close'].iloc[-2] - 1) * 100
            
            # Volume analysis (institutions leave footprints)
            soxl_vol_ratio = soxl['Volume'].iloc[-1] / soxl['Volume'].mean()
            soxs_vol_ratio = soxs['Volume'].iloc[-1] / soxs['Volume'].mean()
            
            # Interpret signals
            if soxl_change > 1 and soxl_vol_ratio > 1.2:
                sentiment = 'BULLISH_INSTITUTIONAL'
                score = min(soxl_change * 2, 10)
            elif soxs_change > 1 and soxs_vol_ratio > 1.2:
                sentiment = 'BEARISH_INSTITUTIONAL'
                score = min(soxs_change * 2, 10)
            else:
                sentiment = 'NEUTRAL'
                score = 5
            
            return {
                'score': round(score, 2),
                'sentiment': sentiment,
                'soxl_change': round(soxl_change, 2),
                'soxs_change': round(soxs_change, 2),
                'soxl_volume_ratio': round(soxl_vol_ratio, 2),
                'soxs_volume_ratio': round(soxs_vol_ratio, 2)
            }
            
        except Exception as e:
            print(f"⚠️ Dark pool proxy error: {e}")
            return {'score': 0, 'sentiment': 'ERROR'}
    
    def check_insider_activity(self) -> Dict:
        """Check recent insider transactions from Yahoo Finance."""
        try:
            ticker = yf.Ticker(self.symbol)
            insiders = ticker.insider_transactions
            
            if insiders is None or len(insiders) == 0:
                return {'score': 0, 'transactions': 0, 'sentiment': 'NO_DATA'}
            
            # Analyze recent transactions (last 30 days)
            cutoff_date = datetime.now() - timedelta(days=30)
            recent = insiders[insiders['Start Date'] > cutoff_date] if 'Start Date' in insiders.columns else insiders.head(10)
            
            if len(recent) == 0:
                return {'score': 0, 'transactions': 0, 'sentiment': 'NO_RECENT'}
            
            # Count buys vs sells
            buys = recent[recent['Transaction'] == 'Buy']
            sells = recent[recent['Transaction'] == 'Sale']
            
            buy_value = buys['Value'].sum() if len(buys) > 0 else 0
            sell_value = sells['Value'].sum() if len(sells) > 0 else 0
            
            # Net insider sentiment
            if buy_value > sell_value * 2:
                sentiment = 'BULLISH'
                score = min((buy_value / (sell_value + 1)) * 2, 10)
            elif sell_value > buy_value * 2:
                sentiment = 'BEARISH'
                score = min((sell_value / (buy_value + 1)) * 2, 10)
            else:
                sentiment = 'NEUTRAL'
                score = 5
            
            return {
                'score': round(score, 2),
                'transactions': len(recent),
                'buy_count': len(buys),
                'sell_count': len(sells),
                'net_value': buy_value - sell_value,
                'sentiment': sentiment
            }
            
        except Exception as e:
            print(f"⚠️ Insider activity error: {e}")
            return {'score': 0, 'transactions': 0, 'sentiment': 'ERROR'}
    
    def detect_unusual_options_activity(self) -> Dict:
        """Detect unusual options volume (institutions use options)."""
        try:
            ticker = yf.Ticker(self.symbol)
            options = ticker.option_chain()
            
            if options is None:
                return {'score': 0, 'unusual': False}
            
            calls = options.calls
            puts = options.puts
            
            # Calculate average volume
            avg_call_vol = calls['volume'].mean()
            avg_put_vol = puts['volume'].mean()
            
            # Find unusual volume (> 3x average)
            unusual_calls = calls[calls['volume'] > avg_call_vol * 3]
            unusual_puts = puts[puts['volume'] > avg_put_vol * 3]
            
            unusual_count = len(unusual_calls) + len(unusual_puts)
            
            if unusual_count == 0:
                return {'score': 0, 'unusual': False, 'sentiment': 'NORMAL'}
            
            # Determine sentiment
            total_call_vol = unusual_calls['volume'].sum()
            total_put_vol = unusual_puts['volume'].sum()
            
            if total_call_vol > total_put_vol * 1.5:
                sentiment = 'BULLISH'
                score = min((total_call_vol / (total_put_vol + 1)), 10)
            elif total_put_vol > total_call_vol * 1.5:
                sentiment = 'BEARISH'
                score = min((total_put_vol / (total_call_vol + 1)), 10)
            else:
                sentiment = 'NEUTRAL'
                score = 5
            
            return {
                'score': round(score, 2),
                'unusual': True,
                'unusual_count': unusual_count,
                'unusual_calls': len(unusual_calls),
                'unusual_puts': len(unusual_puts),
                'sentiment': sentiment
            }
            
        except Exception as e:
            print(f"⚠️ Options activity error: {e}")
            return {'score': 0, 'unusual': False}
    
    def get_institutional_flow_score(self) -> Dict:
        """Aggregate all institutional signals into single score."""
        print(f"\n🏦 Analyzing Institutional Flow for {self.symbol}...")
        
        # Collect all signals
        ah_signal = self.detect_after_hours_activity()
        block_signal = self.detect_block_trades()
        dark_pool_signal = self.analyze_dark_pool_proxies()
        insider_signal = self.check_insider_activity()
        options_signal = self.detect_unusual_options_activity()
        
        # Weight each signal
        weights = {
            'after_hours': 0.30,      # Strong indicator
            'block_trades': 0.25,     # Direct institutional activity
            'dark_pool': 0.20,        # Proxy signal
            'insider': 0.15,          # Leading indicator
            'options': 0.10           # Supportive signal
        }
        
        # Calculate weighted score
        total_score = (
            ah_signal['score'] * weights['after_hours'] +
            block_signal['score'] * weights['block_trades'] +
            dark_pool_signal['score'] * weights['dark_pool'] +
            insider_signal['score'] * weights['insider'] +
            options_signal['score'] * weights['options']
        )
        
        # Determine overall sentiment
        signals = [
            ah_signal.get('direction', 'NEUTRAL'),
            block_signal.get('direction', 'NEUTRAL'),
            dark_pool_signal.get('sentiment', 'NEUTRAL'),
            insider_signal.get('sentiment', 'NEUTRAL'),
            options_signal.get('sentiment', 'NEUTRAL')
        ]
        
        bullish = sum(1 for s in signals if 'BULL' in s or 'UP' in s)
        bearish = sum(1 for s in signals if 'BEAR' in s or 'DOWN' in s)
        
        if bullish > bearish:
            overall_sentiment = 'BULLISH'
        elif bearish > bullish:
            overall_sentiment = 'BEARISH'
        else:
            overall_sentiment = 'NEUTRAL'
        
        # Print results
        print(f"   After-Hours: {ah_signal['activity']} (score: {ah_signal['score']})")
        print(f"   Block Trades: {block_signal['blocks_detected']} detected ({block_signal.get('direction', 'N/A')})")
        print(f"   Dark Pool: {dark_pool_signal['sentiment']}")
        print(f"   Insider: {insider_signal['transactions']} transactions ({insider_signal['sentiment']})")
        print(f"   Options: {'Unusual' if options_signal['unusual'] else 'Normal'} ({options_signal.get('sentiment', 'N/A')})")
        print(f"\n   📊 Total Institutional Score: {total_score:.1f}/10")
        print(f"   📈 Overall Sentiment: {overall_sentiment}")
        
        return {
            'total_score': round(total_score, 2),
            'overall_sentiment': overall_sentiment,
            'signals': {
                'after_hours': ah_signal,
                'block_trades': block_signal,
                'dark_pool': dark_pool_signal,
                'insider': insider_signal,
                'options': options_signal
            },
            'bullish_signals': bullish,
            'bearish_signals': bearish
        }

if __name__ == "__main__":
    tracker = InstitutionalFlowTracker("AMD")
    result = tracker.get_institutional_flow_score()
    
    print(f"\n{'='*60}")
    print(f"🎯 INSTITUTIONAL FLOW ANALYSIS COMPLETE")
    print(f"{'='*60}")
    print(f"Final Score: {result['total_score']}/10")
    print(f"Sentiment: {result['overall_sentiment']}")
    print(f"Bullish Signals: {result['bullish_signals']}")
    print(f"Bearish Signals: {result['bearish_signals']}")
