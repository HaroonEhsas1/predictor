"""
COMPLETE PREMARKET PREDICTION SYSTEM
Integrates all components for professional premarket analysis

Components:
1. Gap Quality Analysis
2. Trap Detection
3. News Catalyst Detection
4. Futures & Sector Alignment
5. Technical Analysis
6. Follow-Through Prediction

Entry: 9:25-9:30 AM
Strategy: PREDICTIVE with multi-source confirmation
"""

from premarket_predictor import PremarketPredictor
from premarket_news_analyzer import PremarketNewsAnalyzer
from premarket_market_data import PremarketMarketData
from premarket_technical import PremarketTechnical
from typing import Dict, Any, List

class CompletePremarketPredictor:
    """
    COMPLETE premarket prediction with all data sources
    """
    
    def __init__(self, symbol: str):
        self.symbol = symbol
        
        # Initialize all components
        self.base_predictor = PremarketPredictor(symbol)
        self.news_analyzer = PremarketNewsAnalyzer(symbol)
        self.market_data = PremarketMarketData(symbol)
        self.technical = PremarketTechnical(symbol)
        
        print(f"\n{'='*80}")
        print(f"🌅 COMPLETE PREMARKET PREDICTOR - {symbol}")
        print(f"{'='*80}")
    
    def get_complete_analysis(self) -> Dict[str, Any]:
        """
        RUN COMPLETE PREMARKET ANALYSIS
        
        Returns comprehensive prediction with all sources
        """
        
        print(f"\nStarting complete analysis...")
        
        # STEP 1: Get base analysis (gap, volume, timing)
        print(f"\n{'='*80}")
        print("STEP 1: BASE ANALYSIS")
        print(f"{'='*80}")
        
        base_analysis = self.base_predictor.analyze_premarket()
        
        if not base_analysis.get('analysis_complete'):
            return base_analysis  # Return error if base fails
        
        premarket_data = base_analysis['premarket_data']
        gap_quality = base_analysis['gap_quality']
        trap_detection = base_analysis['trap_detection']
        base_prediction = base_analysis['prediction']
        
        gap_pct = premarket_data['gap_pct']
        gap_direction = 'up' if gap_pct > 0 else 'down'
        premarket_price = premarket_data['premarket_price']
        prev_close = premarket_data['prev_close']
        
        # STEP 2: Analyze news catalyst
        print(f"\n{'='*80}")
        print("STEP 2: NEWS CATALYST ANALYSIS")
        print(f"{'='*80}")
        
        news_analysis = self.news_analyzer.analyze_overnight_catalyst()
        catalyst = news_analysis['catalyst']
        
        # Get news boost
        news_boost = self.news_analyzer.get_news_boost(catalyst, gap_direction)
        
        # STEP 3: Get market context (futures, sector)
        print(f"\n{'='*80}")
        print("STEP 3: MARKET CONTEXT")
        print(f"{'='*80}")
        
        market_context = self.market_data.get_complete_market_context(gap_direction)
        alignment = market_context['alignment']
        
        # STEP 4: Technical analysis
        print(f"\n{'='*80}")
        print("STEP 4: TECHNICAL ANALYSIS")
        print(f"{'='*80}")
        
        technical_analysis = self.technical.analyze_technical(premarket_price, prev_close)
        
        # STEP 5: INTEGRATE ALL SOURCES
        print(f"\n{'='*80}")
        print("STEP 5: INTEGRATED PREDICTION")
        print(f"{'='*80}")
        
        # Start with base confidence
        final_confidence = base_prediction['confidence']
        
        print(f"\n🎯 Confidence Calculation:")
        print(f"   Base: {final_confidence:.1f}%")
        
        # Add adjustments
        adjustments = []
        
        # News catalyst
        final_confidence += news_boost
        adjustments.append(f"News: {news_boost:+.0f}%")
        print(f"   + News: {news_boost:+.0f}% → {final_confidence:.1f}%")
        
        # Futures & sector alignment
        alignment_boost = alignment['confidence_boost']
        final_confidence += alignment_boost
        adjustments.append(f"Market Alignment: {alignment_boost:+.0f}%")
        print(f"   + Alignment: {alignment_boost:+.0f}% → {final_confidence:.1f}%")
        
        # Technical
        technical_boost = technical_analysis['score_adjustment']
        final_confidence += technical_boost
        adjustments.append(f"Technical: {technical_boost:+.0f}%")
        print(f"   + Technical: {technical_boost:+.0f}% → {final_confidence:.1f}%")
        
        # Cap confidence
        final_confidence = max(40.0, min(95.0, final_confidence))
        
        # Determine final recommendation
        if final_confidence >= 75 and trap_detection['trap_risk'] in ['MINIMAL', 'LOW']:
            recommendation = 'STRONG_TRADE'
        elif final_confidence >= 65 and trap_detection['trap_risk'] != 'HIGH':
            recommendation = 'TRADE'
        elif final_confidence >= 55:
            recommendation = 'CAUTIOUS'
        else:
            recommendation = 'SKIP'
        
        # Calculate target prices
        targets = self._calculate_targets(premarket_price, prev_close, gap_pct, final_confidence)
        
        print(f"\n🎯 Target Prices:")
        print(f"   Entry: ${targets['entry']:.2f} (premarket/open)")
        print(f"   Conservative: ${targets['conservative']:.2f} ({targets['conservative_pct']:+.2f}%)")
        print(f"   Moderate: ${targets['moderate']:.2f} ({targets['moderate_pct']:+.2f}%)")
        print(f"   Aggressive: ${targets['aggressive']:.2f} ({targets['aggressive_pct']:+.2f}%)")
        print(f"   Stop Loss: ${targets['stop_loss']:.2f} ({targets['stop_loss_pct']:+.2f}%)")
        
        # Compile complete analysis
        complete_analysis = {
            'symbol': self.symbol,
            'timestamp': premarket_data['current_time_et'],
            
            # Premarket data
            'premarket_data': premarket_data,
            
            # Quality & Traps
            'gap_quality': gap_quality,
            'trap_detection': trap_detection,
            
            # Additional sources
            'news': news_analysis,
            'market_context': market_context,
            'technical': technical_analysis,
            
            # Final prediction
            'prediction': {
                'direction': 'UP' if gap_pct > 0 else 'DOWN',
                'base_confidence': base_prediction['confidence'],
                'final_confidence': final_confidence,
                'recommendation': recommendation,
                'adjustments': adjustments
            },
            
            # Target prices
            'targets': targets
        }
        
        # Print final summary
        self._print_final_summary(complete_analysis)
        
        return complete_analysis
    
    def _calculate_targets(self, premarket_price: float, prev_close: float, 
                          gap_pct: float, confidence: float) -> Dict[str, Any]:
        """
        Calculate target prices and stop loss
        
        Logic:
        - Conservative: 50% gap fill
        - Moderate: 75% gap fill
        - Aggressive: 100% gap fill + momentum
        - Stop: Below entry based on confidence
        """
        
        gap_dollars = premarket_price - prev_close
        direction = 1 if gap_pct > 0 else -1
        
        # Entry price (use premarket or expect open near premarket)
        entry = premarket_price
        
        # Conservative target: 50% of gap
        if direction > 0:
            conservative = prev_close + (gap_dollars * 0.50)
        else:
            conservative = prev_close + (gap_dollars * 0.50)
        
        # Moderate target: 75% of gap
        if direction > 0:
            moderate = prev_close + (gap_dollars * 0.75)
        else:
            moderate = prev_close + (gap_dollars * 0.75)
        
        # Aggressive target: 100% gap + 25% more momentum
        if direction > 0:
            aggressive = prev_close + (gap_dollars * 1.25)
        else:
            aggressive = prev_close + (gap_dollars * 1.25)
        
        # Stop loss: Based on confidence and gap size
        # Higher confidence = tighter stop
        # Larger gap = wider stop
        if confidence >= 75:
            stop_multiplier = 0.015  # 1.5% stop
        elif confidence >= 65:
            stop_multiplier = 0.020  # 2.0% stop
        else:
            stop_multiplier = 0.025  # 2.5% stop
        
        # Adjust for gap size (larger gap = slightly wider stop)
        gap_size = abs(gap_pct)
        if gap_size > 3.0:
            stop_multiplier *= 1.2
        
        if direction > 0:
            stop_loss = entry * (1 - stop_multiplier)
        else:
            stop_loss = entry * (1 + stop_multiplier)
        
        # Calculate percentages from entry
        conservative_pct = ((conservative - entry) / entry) * 100
        moderate_pct = ((moderate - entry) / entry) * 100
        aggressive_pct = ((aggressive - entry) / entry) * 100
        stop_loss_pct = ((stop_loss - entry) / entry) * 100
        
        return {
            'entry': entry,
            'conservative': conservative,
            'conservative_pct': conservative_pct,
            'moderate': moderate,
            'moderate_pct': moderate_pct,
            'aggressive': aggressive,
            'aggressive_pct': aggressive_pct,
            'stop_loss': stop_loss,
            'stop_loss_pct': stop_loss_pct,
            'risk_reward': abs(conservative_pct / stop_loss_pct) if stop_loss_pct != 0 else 0
        }
    
    def _print_final_summary(self, analysis: Dict[str, Any]):
        """Print comprehensive summary"""
        
        print(f"\n{'='*80}")
        print(f"📋 COMPLETE PREMARKET ANALYSIS - {analysis['symbol']}")
        print(f"{'='*80}")
        
        pm = analysis['premarket_data']
        pred = analysis['prediction']
        news = analysis['news']['catalyst']
        market = analysis['market_context']
        tech = analysis['technical']
        traps = analysis['trap_detection']
        
        print(f"\n💰 PREMARKET DATA:")
        print(f"   Gap: {pm['gap_pct']:+.2f}% (${pm['gap_dollars']:+.2f})")
        print(f"   Volume: {pm['premarket_volume']:,}")
        print(f"   Quality: {analysis['gap_quality']['quality']}")
        
        print(f"\n📰 NEWS CATALYST:")
        print(f"   Catalyst: {news['catalyst_type'].upper()} ({news['catalyst_strength']})")
        print(f"   Sentiment: {news['sentiment'].upper()}")
        
        print(f"\n📈 MARKET CONTEXT:")
        print(f"   Futures: {market['futures']['direction']}")
        print(f"   Sector: {market['sector']['direction']}")
        print(f"   Alignment: {market['alignment']['alignment']}")
        
        print(f"\n📐 TECHNICAL:")
        print(f"   RSI: {tech['rsi']:.1f} ({tech['rsi_state']})")
        print(f"   Trend: {tech['trend'].upper()}")
        
        print(f"\n🚨 TRAP RISK: {traps['trap_risk']}")
        print(f"   Traps Detected: {traps['trap_count']}")
        
        print(f"\n🎯 FINAL PREDICTION:")
        print(f"   Direction: {pred['direction']}")
        print(f"   Confidence: {pred['final_confidence']:.1f}%")
        print(f"   Recommendation: {pred['recommendation']}")
        
        print(f"\n📊 Confidence Breakdown:")
        for adj in pred['adjustments']:
            print(f"      • {adj}")
        
        # Target prices
        targets = analysis.get('targets', {})
        if targets:
            print(f"\n🎯 TARGET PRICES:")
            print(f"   Entry: ${targets['entry']:.2f}")
            print(f"   Conservative: ${targets['conservative']:.2f} ({targets['conservative_pct']:+.2f}%)")
            print(f"   Moderate: ${targets['moderate']:.2f} ({targets['moderate_pct']:+.2f}%)")
            print(f"   Aggressive: ${targets['aggressive']:.2f} ({targets['aggressive_pct']:+.2f}%)")
            print(f"   Stop Loss: ${targets['stop_loss']:.2f} ({targets['stop_loss_pct']:+.2f}%)")
            print(f"   Risk/Reward: {targets['risk_reward']:.2f}:1")
        
        print(f"\n{'='*80}")
        
        # Trading recommendation
        if pred['recommendation'] == 'STRONG_TRADE':
            print(f"✅ STRONG TRADE SIGNAL")
            print(f"   Entry: 9:25-9:30 AM @ ${targets.get('entry', 0):.2f}")
            print(f"   Direction: {'LONG' if pred['direction'] == 'UP' else 'SHORT'}")
            print(f"   Position Size: 100% (2% account risk)")
            if targets:
                print(f"   Target: ${targets['moderate']:.2f} (moderate)")
                print(f"   Stop: ${targets['stop_loss']:.2f}")
        elif pred['recommendation'] == 'TRADE':
            print(f"✅ TRADE SIGNAL")
            print(f"   Entry: 9:28-9:30 AM @ ${targets.get('entry', 0):.2f}")
            print(f"   Direction: {'LONG' if pred['direction'] == 'UP' else 'SHORT'}")
            print(f"   Position Size: 75% (1.5% account risk)")
            if targets:
                print(f"   Target: ${targets['conservative']:.2f} (conservative)")
                print(f"   Stop: ${targets['stop_loss']:.2f}")
        elif pred['recommendation'] == 'CAUTIOUS':
            print(f"⚠️ CAUTIOUS - Consider smaller position")
        else:
            print(f"🚫 SKIP - Not enough confidence or high trap risk")
        
        print(f"{'='*80}\n")


def analyze_multiple_stocks_complete(symbols: List[str]):
    """Analyze multiple stocks with complete system"""
    
    print("\n" + "="*80)
    print("🌅 MULTI-STOCK COMPLETE PREMARKET ANALYSIS")
    print("="*80)
    
    results = {}
    
    for symbol in symbols:
        predictor = CompletePremarketPredictor(symbol)
        analysis = predictor.get_complete_analysis()
        results[symbol] = analysis
        print("\n\n")
    
    # Comparison
    print("="*80)
    print("📊 TRADING RECOMMENDATIONS")
    print("="*80)
    
    for symbol, analysis in results.items():
        if analysis.get('prediction'):
            pred = analysis['prediction']
            pm = analysis['premarket_data']
            
            print(f"\n{symbol}:")
            print(f"   Gap: {pm['gap_pct']:+.2f}%")
            print(f"   Prediction: {pred['direction']} ({pred['final_confidence']:.0f}%)")
            print(f"   📌 {pred['recommendation']}")
    
    print("\n" + "="*80)
    
    return results


if __name__ == "__main__":
    # Analyze NVDA and META
    symbols = ['NVDA', 'META']
    results = analyze_multiple_stocks_complete(symbols)
