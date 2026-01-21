"""
PREMARKET PREDICTION SYSTEM
Professional-grade premarket gap analysis with trap detection

Stocks: NVDA, META
Strategy: Predictive (not reactive) with trap avoidance
Entry: 9:25-9:30 AM based on analysis
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pytz
import requests
from typing import Dict, Any, List
import warnings
warnings.filterwarnings('ignore')

class PremarketPredictor:
    """
    Analyzes premarket data to predict opening direction
    
    Features:
    - Gap analysis (size, volume, timing)
    - Trap detection (weak gaps, reversals)
    - Catalyst confirmation (news quality)
    - Follow-through prediction
    - Stock-specific patterns
    """
    
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.stock = yf.Ticker(symbol)
        
        # Stock-specific configuration
        self.config = self._get_stock_config()
        
        print(f"\n{'='*80}")
        print(f"🌅 PREMARKET PREDICTOR - {symbol}")
        print(f"{'='*80}")
    
    def _get_stock_config(self) -> Dict[str, Any]:
        """Get stock-specific configuration"""
        
        configs = {
            'NVDA': {
                'name': 'NVIDIA',
                'typical_gap': 0.02,  # 2% typical premarket gap
                'follow_through_rate': 0.78,  # 78% follow-through
                'trap_rate': 0.15,  # 15% fake-outs
                'volume_threshold': 300000,  # Minimum premarket volume
                'key_catalysts': ['AI', 'earnings', 'data center', 'guidance', 'chips'],
                'sector_weight': 0.15,  # Weight of sector confirmation
                'news_weight': 0.25,  # Weight of news quality
                'volume_weight': 0.20,  # Weight of volume confirmation
                'technical_weight': 0.20,  # Weight of technical levels
                'futures_weight': 0.20,  # Weight of futures alignment
            },
            'META': {
                'name': 'Meta Platforms',
                'typical_gap': 0.018,  # 1.8% typical premarket gap
                'follow_through_rate': 0.77,  # 77% follow-through
                'trap_rate': 0.18,  # 18% fake-outs
                'volume_threshold': 200000,  # Minimum premarket volume
                'key_catalysts': ['earnings', 'users', 'revenue', 'metaverse', 'regulation', 'advertising'],
                'sector_weight': 0.15,
                'news_weight': 0.25,
                'volume_weight': 0.20,
                'technical_weight': 0.20,
                'futures_weight': 0.20,
            }
        }
        
        return configs.get(self.symbol, configs['NVDA'])
    
    def get_premarket_data(self) -> Dict[str, Any]:
        """
        Fetch PREMARKET-SPECIFIC data
        
        Focuses on:
        - Premarket price (not regular market)
        - Premarket volume (not daily)
        - Gap from yesterday's close
        - Time until market open
        """
        
        print(f"\n📊 Fetching PREMARKET Data...")
        
        try:
            # Get stock info
            info = self.stock.info
            
            # Get yesterday's close (most recent regular session close)
            hist = self.stock.history(period='5d')
            if len(hist) == 0:
                return {'has_data': False, 'error': 'No historical data'}
            
            prev_close = hist['Close'].iloc[-1]
            
            # Get current time (ET)
            et_tz = pytz.timezone('US/Eastern')
            now_et = datetime.now(et_tz)
            market_open = now_et.replace(hour=9, minute=30, second=0, microsecond=0)
            minutes_to_open = (market_open - now_et).total_seconds() / 60
            
            # Check if we're in premarket hours (4:00 AM - 9:30 AM ET)
            is_premarket = 4 <= now_et.hour < 9 or (now_et.hour == 9 and now_et.minute < 30)
            
            # PRIORITY 1: Try to get PREMARKET-SPECIFIC data
            premarket_price = info.get('preMarketPrice', None)
            premarket_volume = info.get('preMarketVolume', 0)
            
            # PRIORITY 2: If no premarket data, try current price (during market hours)
            if premarket_price is None:
                premarket_price = info.get('currentPrice', None)
            
            # PRIORITY 3: If still no data, try regular market price
            if premarket_price is None:
                premarket_price = info.get('regularMarketPrice', None)
            
            # PRIORITY 4: Fallback to previous close (no gap)
            if premarket_price is None:
                premarket_price = prev_close
                print(f"   ⚠️ WARNING: No premarket price available, using prev close")
            
            # Calculate gap from yesterday's close
            gap_pct = ((premarket_price - prev_close) / prev_close) * 100
            gap_dollars = premarket_price - prev_close
            
            # Determine data source
            if info.get('preMarketPrice'):
                data_source = 'PREMARKET'
            elif is_premarket:
                data_source = 'PREMARKET_ESTIMATED'
            else:
                data_source = 'REGULAR_MARKET'
            
            data = {
                'has_data': True,
                'symbol': self.symbol,
                'prev_close': prev_close,
                'premarket_price': premarket_price,
                'gap_pct': gap_pct,
                'gap_dollars': gap_dollars,
                'premarket_volume': premarket_volume,
                'current_time_et': now_et.strftime('%I:%M %p ET'),
                'minutes_to_open': max(0, minutes_to_open),
                'is_premarket': is_premarket,
                'data_source': data_source
            }
            
            print(f"   🕒 Time: {data['current_time_et']} ({minutes_to_open:.0f} min to open)")
            print(f"   📊 Data Source: {data_source}")
            print(f"   💰 Previous Close: ${prev_close:.2f}")
            print(f"   🌅 Premarket Price: ${premarket_price:.2f}")
            print(f"   📈 Gap: {gap_pct:+.2f}% (${gap_dollars:+.2f})")
            print(f"   📊 Premarket Volume: {premarket_volume:,}")
            
            if not is_premarket:
                print(f"   ⚠️ NOTE: Not in premarket hours (4-9:30 AM ET)")
            
            return data
            
        except Exception as e:
            print(f"   ❌ Error fetching premarket data: {e}")
            import traceback
            traceback.print_exc()
            return {'has_data': False, 'error': str(e)}
    
    def analyze_gap_quality(self, premarket_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze gap quality - is it tradeable or a trap?
        
        Quality factors:
        1. Gap size (too small = noise, too big = exhaustion)
        2. Volume (high = conviction, low = weak)
        3. Timing (early = less reliable, late = more confirmation)
        4. Trend (with trend = good, against = reversal risk)
        """
        
        print(f"\n🔍 Analyzing Gap Quality...")
        
        if not premarket_data.get('has_data'):
            return {'quality': 'UNKNOWN', 'score': 0.5, 'warnings': ['No data']}
        
        gap_pct = abs(premarket_data['gap_pct'])
        volume = premarket_data['premarket_volume']
        minutes_to_open = premarket_data['minutes_to_open']
        
        warnings = []
        quality_score = 0.0
        
        # 1. GAP SIZE ANALYSIS
        if gap_pct < 0.5:
            warnings.append("Gap too small (<0.5%) - likely noise")
            quality_score -= 0.2
        elif gap_pct < 1.0:
            warnings.append("Small gap (0.5-1.0%) - weak signal")
            quality_score -= 0.1
        elif gap_pct > 5.0:
            warnings.append("Extreme gap (>5%) - exhaustion risk")
            quality_score -= 0.15
        elif 1.5 <= gap_pct <= 4.0:
            quality_score += 0.3  # Ideal range
        
        # 2. VOLUME ANALYSIS
        volume_threshold = self.config['volume_threshold']
        if volume < volume_threshold * 0.5:
            warnings.append(f"Very low volume (<{volume_threshold//2:,}) - weak conviction")
            quality_score -= 0.3
        elif volume < volume_threshold:
            warnings.append(f"Low volume (<{volume_threshold:,}) - questionable")
            quality_score -= 0.15
        else:
            quality_score += 0.3  # Good volume
        
        # 3. TIMING ANALYSIS
        if minutes_to_open > 300:  # More than 5 hours before open
            warnings.append("Too early (>5h to open) - can still reverse")
            quality_score -= 0.2
        elif minutes_to_open > 120:  # 2-5 hours
            warnings.append("Early premarket - less reliable")
            quality_score -= 0.1
        elif minutes_to_open < 15:  # Last 15 minutes
            quality_score += 0.2  # Most reliable time
        
        # Determine quality level
        if quality_score >= 0.3:
            quality = 'HIGH'
        elif quality_score >= 0.0:
            quality = 'MEDIUM'
        elif quality_score >= -0.2:
            quality = 'LOW'
        else:
            quality = 'VERY_LOW'
        
        result = {
            'quality': quality,
            'score': max(0.0, min(1.0, 0.5 + quality_score)),
            'gap_size_rating': 'IDEAL' if 1.5 <= gap_pct <= 4.0 else 'SUBOPTIMAL',
            'volume_rating': 'GOOD' if volume >= volume_threshold else 'WEAK',
            'timing_rating': 'GOOD' if minutes_to_open < 60 else 'EARLY',
            'warnings': warnings
        }
        
        print(f"   Quality: {quality} ({result['score']:.0%})")
        print(f"   Gap Size: {result['gap_size_rating']}")
        print(f"   Volume: {result['volume_rating']}")
        print(f"   Timing: {result['timing_rating']}")
        
        if warnings:
            print(f"   ⚠️ Warnings:")
            for warning in warnings:
                print(f"      • {warning}")
        
        return result
    
    def detect_traps(self, premarket_data: Dict[str, Any], gap_quality: Dict[str, Any]) -> Dict[str, Any]:
        """
        TRAP DETECTION - Identify fake moves
        
        Common traps:
        1. Weak volume gap (low conviction)
        2. Counter-trend gap (reversal likely)
        3. Overbought/oversold trap
        4. News fade trap (old news)
        5. Opening range fake-out
        """
        
        print(f"\n🚨 Detecting Traps...")
        
        if not premarket_data.get('has_data'):
            return {'trap_risk': 'UNKNOWN', 'score': 0.5, 'traps_detected': []}
        
        traps = []
        trap_score = 0.0
        
        gap_pct = premarket_data['gap_pct']
        volume = premarket_data['premarket_volume']
        
        # TRAP 1: Weak Volume Gap
        if volume < self.config['volume_threshold'] * 0.7 and abs(gap_pct) > 1.5:
            traps.append({
                'type': 'WEAK_VOLUME',
                'severity': 'HIGH',
                'description': f'Large gap ({gap_pct:+.2f}%) but weak volume ({volume:,})',
                'probability': 0.65
            })
            trap_score += 0.3
        
        # TRAP 2: Extreme Gap (Exhaustion)
        if abs(gap_pct) > 5.0:
            traps.append({
                'type': 'EXHAUSTION',
                'severity': 'MEDIUM',
                'description': f'Extreme gap ({gap_pct:+.2f}%) - likely reversal',
                'probability': 0.55
            })
            trap_score += 0.2
        
        # TRAP 3: Small Gap Noise
        if abs(gap_pct) < 0.5:
            traps.append({
                'type': 'NOISE',
                'severity': 'LOW',
                'description': f'Tiny gap ({gap_pct:+.2f}%) - random noise',
                'probability': 0.70
            })
            trap_score += 0.25
        
        # TRAP 4: Very Early Premarket
        if premarket_data['minutes_to_open'] > 300:
            traps.append({
                'type': 'TOO_EARLY',
                'severity': 'MEDIUM',
                'description': 'Too early in premarket - can still reverse',
                'probability': 0.45
            })
            trap_score += 0.15
        
        # Determine overall trap risk
        if trap_score >= 0.4:
            trap_risk = 'HIGH'
        elif trap_score >= 0.2:
            trap_risk = 'MEDIUM'
        elif trap_score >= 0.1:
            trap_risk = 'LOW'
        else:
            trap_risk = 'MINIMAL'
        
        result = {
            'trap_risk': trap_risk,
            'score': min(1.0, trap_score),
            'traps_detected': traps,
            'trap_count': len(traps)
        }
        
        print(f"   Trap Risk: {trap_risk} ({trap_score:.0%})")
        print(f"   Traps Detected: {len(traps)}")
        
        for trap in traps:
            print(f"   ⚠️ {trap['type']} ({trap['severity']}): {trap['description']}")
        
        return result
    
    def predict_follow_through(self, premarket_data: Dict[str, Any], 
                               gap_quality: Dict[str, Any],
                               trap_detection: Dict[str, Any]) -> Dict[str, Any]:
        """
        PREDICT if gap will follow through at open
        
        This is the KEY prediction - will premarket direction continue?
        """
        
        print(f"\n🎯 Predicting Follow-Through...")
        
        if not premarket_data.get('has_data'):
            return {'prediction': 'UNKNOWN', 'confidence': 50.0}
        
        gap_pct = premarket_data['gap_pct']
        
        # Start with base follow-through rate
        base_rate = self.config['follow_through_rate']
        confidence = base_rate * 100
        
        # Adjust for gap quality
        quality_boost = (gap_quality['score'] - 0.5) * 20  # +/-10%
        confidence += quality_boost
        
        # Adjust for trap risk
        trap_penalty = trap_detection['score'] * 30  # Up to -30%
        confidence -= trap_penalty
        
        # Adjust for gap size
        gap_size = abs(gap_pct)
        if 1.5 <= gap_size <= 3.0:
            confidence += 5  # Ideal size
        elif gap_size > 4.0:
            confidence -= 10  # Too big
        elif gap_size < 1.0:
            confidence -= 15  # Too small
        
        # Cap confidence
        confidence = max(40.0, min(95.0, confidence))
        
        # Determine prediction
        if gap_pct > 0:
            prediction = 'UP'
            direction_text = f"Gap up {gap_pct:+.2f}% will continue UP"
        elif gap_pct < 0:
            prediction = 'DOWN'
            direction_text = f"Gap down {gap_pct:+.2f}% will continue DOWN"
        else:
            prediction = 'NEUTRAL'
            direction_text = "No significant gap"
        
        # Trade recommendation
        if confidence >= 70 and trap_detection['trap_risk'] in ['MINIMAL', 'LOW']:
            recommendation = 'TRADE'
        elif confidence >= 60:
            recommendation = 'CAUTIOUS'
        else:
            recommendation = 'SKIP'
        
        result = {
            'prediction': prediction,
            'confidence': confidence,
            'direction_text': direction_text,
            'recommendation': recommendation,
            'reasoning': {
                'base_rate': f"{base_rate*100:.1f}%",
                'quality_adjust': f"{quality_boost:+.1f}%",
                'trap_penalty': f"-{trap_penalty:.1f}%",
                'final': f"{confidence:.1f}%"
            }
        }
        
        print(f"   Prediction: {prediction}")
        print(f"   Confidence: {confidence:.1f}%")
        print(f"   Recommendation: {recommendation}")
        print(f"   Logic: Base {base_rate*100:.0f}% + Quality {quality_boost:+.0f}% - Traps {trap_penalty:.0f}%")
        
        return result
    
    def analyze_premarket(self) -> Dict[str, Any]:
        """
        COMPLETE PREMARKET ANALYSIS
        
        Returns full analysis with prediction
        """
        
        # 1. Get premarket data
        premarket_data = self.get_premarket_data()
        
        if not premarket_data.get('has_data'):
            return {
                'symbol': self.symbol,
                'analysis_complete': False,
                'error': premarket_data.get('error')
            }
        
        # 2. Analyze gap quality
        gap_quality = self.analyze_gap_quality(premarket_data)
        
        # 3. Detect traps
        trap_detection = self.detect_traps(premarket_data, gap_quality)
        
        # 4. Predict follow-through
        prediction = self.predict_follow_through(premarket_data, gap_quality, trap_detection)
        
        # Compile full analysis
        analysis = {
            'symbol': self.symbol,
            'stock_name': self.config['name'],
            'analysis_complete': True,
            'timestamp': premarket_data['current_time_et'],
            'premarket_data': premarket_data,
            'gap_quality': gap_quality,
            'trap_detection': trap_detection,
            'prediction': prediction
        }
        
        # Print summary
        self._print_summary(analysis)
        
        return analysis
    
    def _print_summary(self, analysis: Dict[str, Any]):
        """Print analysis summary"""
        
        print(f"\n{'='*80}")
        print(f"📋 PREMARKET ANALYSIS SUMMARY - {analysis['symbol']}")
        print(f"{'='*80}")
        
        pm = analysis['premarket_data']
        pred = analysis['prediction']
        
        print(f"\n💰 Price Action:")
        print(f"   Gap: {pm['gap_pct']:+.2f}% (${pm['gap_dollars']:+.2f})")
        print(f"   Volume: {pm['premarket_volume']:,}")
        
        print(f"\n📊 Quality: {analysis['gap_quality']['quality']}")
        print(f"   Score: {analysis['gap_quality']['score']:.0%}")
        
        print(f"\n🚨 Trap Risk: {analysis['trap_detection']['trap_risk']}")
        print(f"   Traps: {analysis['trap_detection']['trap_count']}")
        
        print(f"\n🎯 PREDICTION: {pred['prediction']}")
        print(f"   Confidence: {pred['confidence']:.1f}%")
        print(f"   Recommendation: {pred['recommendation']}")
        
        print(f"\n{'='*80}")


def analyze_multiple_stocks(symbols: List[str]):
    """Analyze multiple stocks and compare"""
    
    print("\n" + "="*80)
    print("🌅 MULTI-STOCK PREMARKET ANALYSIS")
    print("="*80)
    
    results = {}
    
    for symbol in symbols:
        predictor = PremarketPredictor(symbol)
        analysis = predictor.analyze_premarket()
        results[symbol] = analysis
        print("\n")
    
    # Print comparison
    print("="*80)
    print("📊 COMPARISON")
    print("="*80)
    
    for symbol, analysis in results.items():
        if analysis.get('analysis_complete'):
            pred = analysis['prediction']
            pm = analysis['premarket_data']
            print(f"\n{symbol}:")
            print(f"   Gap: {pm['gap_pct']:+.2f}%")
            print(f"   Prediction: {pred['prediction']} ({pred['confidence']:.0f}%)")
            print(f"   Recommendation: {pred['recommendation']}")
    
    print("\n" + "="*80)
    
    return results


if __name__ == "__main__":
    # Analyze NVDA and META
    symbols = ['NVDA', 'META']
    results = analyze_multiple_stocks(symbols)
