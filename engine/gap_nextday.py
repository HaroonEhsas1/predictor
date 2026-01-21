#!/usr/bin/env python3
"""
Professional Next-Day / Gap + Context System
Advanced next-day predictions using historical gap analysis and contextual market indicators
"""

import os
import sys
import time
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import warnings
warnings.filterwarnings('ignore')

# Import existing system components
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from manager.scheduler import scheduler

# Try importing existing next-day prediction system
try:
    from professional_next_day_predictor import ProfessionalNextDayPredictor
    EXISTING_NEXTDAY_AVAILABLE = True
except ImportError:
    EXISTING_NEXTDAY_AVAILABLE = False

@dataclass
class GapAnalysis:
    """Container for gap analysis results"""
    expected_gap_pct: float
    gap_direction: str  # 'UP', 'DOWN', 'FLAT'
    confidence: float
    historical_accuracy: float
    contextual_factors: Dict[str, float]
    risk_factors: Dict[str, float]
    
@dataclass
class NextDayPrediction:
    """Container for comprehensive next-day prediction"""
    target_price: float
    expected_gap_pct: float
    direction: str
    confidence: float
    risk_level: str
    position_size: float
    profit_range: Tuple[float, float]
    time_horizon: str  # 'pre-market', 'market-open', 'full-day'
    contextual_analysis: Dict[str, Any]
    execution_details: Dict[str, Any]
    timestamp: str

class NextDayGapPredictor:
    """
    Professional next-day gap prediction system with contextual analysis
    Runs automatically at market close and pre-market open
    """
    
    def __init__(self):
        """Initialize next-day gap predictor"""
        self.historical_gaps = {}
        self.contextual_weights = {
            'futures_influence': 0.35,
            'global_markets': 0.25, 
            'volatility_regime': 0.20,
            'technical_setup': 0.15,
            'news_sentiment': 0.05
        }
        
        # Gap analysis parameters
        self.min_significant_gap = 1.5  # 1.5% minimum for significant gap
        self.confidence_threshold = 0.65  # 65% minimum confidence for trading
        self.max_position_size = 0.07   # 7% maximum position size
        
        # Historical analysis cache
        self.gap_history_cache = {}
        self.cache_duration = 3600  # 1 hour
        
        print("✅ NextDayGapPredictor initialized")
    
    def predict_preclose(self, dataset: Dict[str, Any], symbol: str) -> NextDayPrediction:
        """
        Pre-close next-day prediction (runs 30 minutes before market close)
        Comprehensive analysis for overnight gap prediction
        """
        print(f"🌙 Generating pre-close next-day prediction for {symbol}...")
        
        try:
            # Analyze historical gap patterns
            gap_analysis = self._analyze_historical_gaps(dataset, symbol)
            
            # Get current market context
            market_context = dataset.get('market_context')
            contextual_analysis = self._analyze_market_context(market_context, gap_analysis)
            
            # Combine technical and contextual factors
            technical_factors = self._analyze_technical_setup(dataset)
            
            # Generate comprehensive prediction
            prediction = self._generate_preclose_prediction(
                gap_analysis, contextual_analysis, technical_factors, symbol
            )
            
            print(f"✅ Pre-close prediction: {prediction.direction} gap of {prediction.expected_gap_pct:.2f}%")
            return prediction
            
        except Exception as e:
            print(f"⚠️  Pre-close prediction error: {str(e)[:50]}")
            return self._create_default_prediction(symbol, "pre-close")
    
    def predict_preopen(self, dataset: Dict[str, Any], symbol: str) -> NextDayPrediction:
        """
        Pre-open prediction (runs 1 hour before market open)
        Incorporates overnight developments and futures movements
        """
        print(f"🌅 Generating pre-open prediction for {symbol}...")
        
        try:
            # Get overnight developments
            overnight_context = self._get_overnight_context(dataset)
            
            # Update gap analysis with overnight information
            updated_gap_analysis = self._update_gap_analysis_with_overnight(dataset, overnight_context, symbol)
            
            # Generate pre-open prediction
            prediction = self._generate_preopen_prediction(
                updated_gap_analysis, overnight_context, symbol
            )
            
            print(f"✅ Pre-open prediction: {prediction.direction} opening at ${prediction.target_price:.2f}")
            return prediction
            
        except Exception as e:
            print(f"⚠️  Pre-open prediction error: {str(e)[:50]}")
            return self._create_default_prediction(symbol, "pre-open")
    
    def get_detailed_gap_report(self, symbol: str, dataset: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate detailed gap analysis report with confidence scores
        Used for comprehensive next-day analysis
        """
        try:
            # Historical gap analysis
            historical_analysis = self._comprehensive_gap_analysis(dataset, symbol)
            
            # Market context analysis
            context_analysis = self._detailed_context_analysis(dataset.get('market_context', {}))
            
            # Risk assessment
            risk_analysis = self._comprehensive_risk_analysis(dataset, historical_analysis)
            
            # Trading recommendations
            trading_recommendations = self._generate_trading_recommendations(
                historical_analysis, context_analysis, risk_analysis
            )
            
            report = {
                'symbol': symbol,
                'analysis_timestamp': datetime.now().isoformat(),
                'historical_analysis': historical_analysis,
                'context_analysis': context_analysis,
                'risk_analysis': risk_analysis,
                'trading_recommendations': trading_recommendations,
                'overall_confidence': self._calculate_overall_confidence(
                    historical_analysis, context_analysis, risk_analysis
                )
            }
            
            return report
            
        except Exception as e:
            print(f"⚠️  Gap report error: {str(e)[:50]}")
            return {'error': str(e), 'symbol': symbol}
    
    def _analyze_historical_gaps(self, dataset: Dict[str, Any], symbol: str) -> GapAnalysis:
        """Analyze historical gap patterns"""
        try:
            base_data = dataset.get('base_data', {})
            daily_data = base_data.get('timeframes', {}).get('1d')
            
            if daily_data is None or len(daily_data) < 20:
                return self._create_default_gap_analysis()
            
            # Calculate historical gaps
            gaps = []
            gap_directions = []
            
            for i in range(1, min(len(daily_data), 60)):  # Last 60 trading days
                prev_close = daily_data['Close'].iloc[-(i+1)]
                current_open = daily_data['Open'].iloc[-i]
                
                if prev_close > 0:
                    gap_pct = ((current_open - prev_close) / prev_close) * 100
                    gaps.append(gap_pct)
                    
                    if abs(gap_pct) >= self.min_significant_gap:
                        gap_directions.append('UP' if gap_pct > 0 else 'DOWN')
                    else:
                        gap_directions.append('FLAT')
            
            if not gaps:
                return self._create_default_gap_analysis()
            
            # Statistical analysis
            avg_gap = np.mean(np.abs(gaps))
            gap_volatility = np.std(gaps)
            significant_gap_freq = len([g for g in gaps if abs(g) >= self.min_significant_gap]) / len(gaps)
            
            # Direction bias
            up_gaps = len([g for g in gaps if g > self.min_significant_gap])
            down_gaps = len([g for g in gaps if g < -self.min_significant_gap])
            
            if up_gaps > down_gaps:
                expected_direction = 'UP'
                direction_confidence = up_gaps / (up_gaps + down_gaps) if (up_gaps + down_gaps) > 0 else 0.5
            elif down_gaps > up_gaps:
                expected_direction = 'DOWN'
                direction_confidence = down_gaps / (up_gaps + down_gaps) if (up_gaps + down_gaps) > 0 else 0.5
            else:
                expected_direction = 'FLAT'
                direction_confidence = 0.6
            
            # Expected gap size
            recent_gaps = gaps[:10]  # Last 10 trading days
            expected_gap_pct = np.mean(np.abs(recent_gaps)) if recent_gaps else avg_gap
            
            return GapAnalysis(
                expected_gap_pct=expected_gap_pct,
                gap_direction=expected_direction,
                confidence=direction_confidence * significant_gap_freq,  # Combined confidence
                historical_accuracy=self._calculate_historical_accuracy(gaps, gap_directions),
                contextual_factors={
                    'avg_gap_size': avg_gap,
                    'gap_volatility': gap_volatility,
                    'significant_gap_frequency': significant_gap_freq,
                    'recent_trend': np.mean(recent_gaps) if recent_gaps else 0.0
                },
                risk_factors={
                    'volatility_risk': min(gap_volatility / 5.0, 1.0),  # Normalize to 0-1
                    'pattern_reliability': significant_gap_freq
                }
            )
            
        except Exception as e:
            print(f"⚠️  Gap analysis error: {str(e)[:50]}")
            return self._create_default_gap_analysis()
    
    def _analyze_market_context(self, market_context: Dict, gap_analysis: GapAnalysis) -> Dict[str, Any]:
        """Analyze market context for gap prediction"""
        context_analysis = {
            'futures_signal': 0.0,
            'global_signal': 0.0,
            'volatility_signal': 0.0,
            'overall_sentiment': 0.0,
            'strength': 'WEAK'
        }
        
        try:
            if not market_context:
                return context_analysis
            
            # Futures analysis
            futures = market_context.get('futures', {})
            if futures:
                # Tech-heavy weighting for AMD
                nq_change = futures.get('NQ', 0.0)
                es_change = futures.get('ES', 0.0)
                
                futures_signal = (nq_change * 0.7) + (es_change * 0.3)
                context_analysis['futures_signal'] = futures_signal
                
                # Signal strength
                if abs(futures_signal) > 1.0:
                    context_analysis['strength'] = 'STRONG' if abs(futures_signal) > 2.0 else 'MEDIUM'
            
            # Global markets
            global_indices = market_context.get('global_indices', {})
            if global_indices:
                # Weight by market relevance to US tech
                global_signal = 0.0
                weights = {'Nikkei': 0.3, 'DAX': 0.4, 'FTSE': 0.3}
                
                for index, weight in weights.items():
                    global_signal += global_indices.get(index, 0.0) * weight
                
                context_analysis['global_signal'] = global_signal
            
            # Volatility indicators
            volatility = market_context.get('volatility', {})
            if volatility:
                vix_change = volatility.get('VIX', 0.0)
                dxy_change = volatility.get('DXY', 0.0)
                
                # VIX up = risk off, DXY up = USD strength (negative for stocks)
                volatility_signal = -vix_change * 0.6 - dxy_change * 0.4
                context_analysis['volatility_signal'] = volatility_signal
            
            # Overall sentiment
            weighted_sentiment = (
                context_analysis['futures_signal'] * self.contextual_weights['futures_influence'] +
                context_analysis['global_signal'] * self.contextual_weights['global_markets'] +
                context_analysis['volatility_signal'] * self.contextual_weights['volatility_regime']
            )
            
            context_analysis['overall_sentiment'] = weighted_sentiment
            
            # Update strength based on overall sentiment
            if abs(weighted_sentiment) > 1.5:
                context_analysis['strength'] = 'STRONG'
            elif abs(weighted_sentiment) > 0.8:
                context_analysis['strength'] = 'MEDIUM'
            else:
                context_analysis['strength'] = 'WEAK'
                
        except Exception as e:
            print(f"⚠️  Context analysis error: {str(e)[:50]}")
        
        return context_analysis
    
    def _analyze_technical_setup(self, dataset: Dict[str, Any]) -> Dict[str, float]:
        """Analyze technical setup for next-day prediction"""
        technical_factors = {
            'trend_alignment': 0.0,
            'support_resistance': 0.0,
            'momentum_divergence': 0.0,
            'volume_confirmation': 0.0,
            'overall_technical_score': 0.0
        }
        
        try:
            base_data = dataset.get('base_data', {})
            daily_data = base_data.get('timeframes', {}).get('1d')
            
            if daily_data is None or len(daily_data) < 20:
                return technical_factors
            
            close = daily_data['Close']
            volume = daily_data.get('Volume', pd.Series([1] * len(daily_data)))
            
            # Trend alignment (price vs moving averages)
            if len(close) >= 20:
                sma_20 = close.rolling(20).mean()
                current_price = close.iloc[-1]
                sma_current = sma_20.iloc[-1]
                
                if sma_current > 0:
                    trend_score = (current_price / sma_current - 1) * 10  # Scale to -1 to 1
                    technical_factors['trend_alignment'] = max(-1, min(1, trend_score))
            
            # Volume analysis
            if len(volume) >= 10:
                avg_volume = volume.rolling(10).mean().iloc[-1]
                current_volume = volume.iloc[-1]
                
                if avg_volume > 0:
                    volume_ratio = current_volume / avg_volume
                    # Higher volume = more confirmation
                    volume_score = min(1.0, (volume_ratio - 1) * 2)  # Scale to 0-1
                    technical_factors['volume_confirmation'] = volume_score
            
            # Momentum (simplified)
            if len(close) >= 5:
                momentum = (close.iloc[-1] / close.iloc[-6] - 1) * 10  # 5-day momentum
                technical_factors['momentum_divergence'] = max(-1, min(1, momentum))
            
            # Support/Resistance (price position in recent range)
            if len(daily_data) >= 20:
                recent_high = daily_data['High'].tail(20).max()
                recent_low = daily_data['Low'].tail(20).min()
                current_price = close.iloc[-1]
                
                if recent_high != recent_low:
                    price_position = (current_price - recent_low) / (recent_high - recent_low)
                    # Convert to signal: 0.5 = neutral, 1 = at resistance, 0 = at support
                    technical_factors['support_resistance'] = (price_position - 0.5) * 2
            
            # Overall technical score
            scores = [
                technical_factors['trend_alignment'] * 0.4,
                technical_factors['momentum_divergence'] * 0.3,
                technical_factors['volume_confirmation'] * 0.2,
                technical_factors['support_resistance'] * 0.1
            ]
            technical_factors['overall_technical_score'] = sum(scores)
            
        except Exception as e:
            print(f"⚠️  Technical analysis error: {str(e)[:50]}")
        
        return technical_factors
    
    def _generate_preclose_prediction(self, gap_analysis: GapAnalysis, context_analysis: Dict, 
                                    technical_factors: Dict, symbol: str) -> NextDayPrediction:
        """Generate comprehensive pre-close prediction"""
        try:
            # Combine all signals
            gap_signal = gap_analysis.expected_gap_pct if gap_analysis.gap_direction == 'UP' else -gap_analysis.expected_gap_pct
            context_signal = context_analysis.get('overall_sentiment', 0.0)
            technical_signal = technical_factors.get('overall_technical_score', 0.0)
            
            # Weighted combination
            combined_signal = (
                gap_signal * 0.4 +           # Historical gap pattern
                context_signal * 0.4 +       # Market context
                technical_signal * 0.2       # Technical setup
            )
            
            # Direction and magnitude
            if abs(combined_signal) < 0.5:
                direction = 'FLAT'
                expected_gap = 0.0
            elif combined_signal > 0:
                direction = 'UP'
                expected_gap = abs(combined_signal)
            else:
                direction = 'DOWN' 
                expected_gap = abs(combined_signal)
            
            # Confidence calculation
            confidence_factors = [
                gap_analysis.confidence * 0.4,
                min(1.0, abs(context_signal) / 2.0) * 0.4,  # Context strength
                (gap_analysis.historical_accuracy / 100.0) * 0.2
            ]
            overall_confidence = sum(confidence_factors)
            
            # Risk level
            volatility_risk = gap_analysis.risk_factors.get('volatility_risk', 0.5)
            if volatility_risk > 0.7 or overall_confidence < 0.5:
                risk_level = 'HIGH'
            elif volatility_risk > 0.4 or overall_confidence < 0.7:
                risk_level = 'MEDIUM'
            else:
                risk_level = 'LOW'
            
            # Position sizing
            if overall_confidence >= self.confidence_threshold and expected_gap >= self.min_significant_gap:
                # Scale position by confidence and expected gap
                base_size = min(overall_confidence, expected_gap / 5.0)  # Cap based on gap size
                position_size = min(base_size * self.max_position_size, self.max_position_size)
            else:
                position_size = 0.0
            
            # Target price (simplified - would need current price)
            target_price = 0.0  # Placeholder - would calculate based on current price
            
            # Profit range
            gap_volatility = gap_analysis.contextual_factors.get('gap_volatility', 2.0)
            profit_range = (
                expected_gap - gap_volatility,
                expected_gap + gap_volatility
            )
            
            return NextDayPrediction(
                target_price=target_price,
                expected_gap_pct=expected_gap,
                direction=direction,
                confidence=overall_confidence,
                risk_level=risk_level,
                position_size=position_size,
                profit_range=profit_range,
                time_horizon='pre-market',
                contextual_analysis={
                    'gap_analysis': gap_analysis.__dict__,
                    'market_context': context_analysis,
                    'technical_factors': technical_factors
                },
                execution_details={
                    'min_gap_for_trade': self.min_significant_gap,
                    'confidence_threshold': self.confidence_threshold,
                    'max_position_size': self.max_position_size
                },
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            print(f"⚠️  Pre-close prediction generation error: {str(e)[:50]}")
            return self._create_default_prediction(symbol, "pre-close")
    
    def _get_overnight_context(self, dataset: Dict[str, Any]) -> Dict[str, Any]:
        """Get overnight market developments"""
        # This would integrate with real-time news and futures data
        # For now, return basic overnight context
        return {
            'futures_overnight_change': 0.0,
            'news_sentiment_overnight': 0.0,
            'global_market_close': 0.0,
            'earnings_announcements': [],
            'major_news_events': []
        }
    
    def _update_gap_analysis_with_overnight(self, dataset: Dict, overnight_context: Dict, symbol: str) -> GapAnalysis:
        """Update gap analysis with overnight developments"""
        # Get original analysis
        gap_analysis = self._analyze_historical_gaps(dataset, symbol)
        
        # Adjust based on overnight context
        overnight_adjustment = overnight_context.get('futures_overnight_change', 0.0)
        
        # Update expected gap
        if abs(overnight_adjustment) > 0.5:  # Significant overnight move
            gap_analysis.expected_gap_pct += abs(overnight_adjustment) * 0.5
            gap_analysis.confidence *= 1.2  # Increase confidence with overnight confirmation
            
        return gap_analysis
    
    def _generate_preopen_prediction(self, gap_analysis: GapAnalysis, overnight_context: Dict, symbol: str) -> NextDayPrediction:
        """Generate pre-open prediction with overnight updates"""
        # Similar to pre-close but with overnight adjustments
        # This is a simplified version
        return NextDayPrediction(
            target_price=0.0,
            expected_gap_pct=gap_analysis.expected_gap_pct,
            direction=gap_analysis.gap_direction,
            confidence=gap_analysis.confidence,
            risk_level='MEDIUM',
            position_size=0.03,
            profit_range=(0.0, gap_analysis.expected_gap_pct * 1.5),
            time_horizon='market-open',
            contextual_analysis={'overnight_context': overnight_context},
            execution_details={},
            timestamp=datetime.now().isoformat()
        )
    
    def _comprehensive_gap_analysis(self, dataset: Dict, symbol: str) -> Dict[str, Any]:
        """Comprehensive historical gap analysis"""
        gap_analysis = self._analyze_historical_gaps(dataset, symbol)
        
        return {
            'expected_gap_pct': gap_analysis.expected_gap_pct,
            'direction': gap_analysis.gap_direction,
            'confidence': gap_analysis.confidence,
            'historical_accuracy': gap_analysis.historical_accuracy,
            'contextual_factors': gap_analysis.contextual_factors,
            'risk_factors': gap_analysis.risk_factors
        }
    
    def _detailed_context_analysis(self, market_context: Dict) -> Dict[str, Any]:
        """Detailed market context analysis"""
        return self._analyze_market_context(market_context, self._create_default_gap_analysis())
    
    def _comprehensive_risk_analysis(self, dataset: Dict, historical_analysis: Dict) -> Dict[str, Any]:
        """Comprehensive risk analysis"""
        return {
            'volatility_risk': historical_analysis.get('risk_factors', {}).get('volatility_risk', 0.5),
            'pattern_reliability': historical_analysis.get('risk_factors', {}).get('pattern_reliability', 0.5),
            'market_regime_risk': 0.3,  # Placeholder
            'execution_risk': 0.2,     # Placeholder
            'overall_risk_score': 0.4  # Placeholder
        }
    
    def _generate_trading_recommendations(self, historical: Dict, context: Dict, risk: Dict) -> Dict[str, Any]:
        """Generate trading recommendations based on analysis"""
        confidence = historical.get('confidence', 0.5)
        expected_gap = historical.get('expected_gap_pct', 0.0)
        overall_risk = risk.get('overall_risk_score', 0.5)
        
        if confidence >= 0.7 and abs(expected_gap) >= 1.5 and overall_risk <= 0.4:
            recommendation = 'STRONG_BUY' if expected_gap > 0 else 'STRONG_SELL'
            position_size = 0.07
        elif confidence >= 0.6 and abs(expected_gap) >= 1.0:
            recommendation = 'BUY' if expected_gap > 0 else 'SELL'
            position_size = 0.04
        else:
            recommendation = 'HOLD'
            position_size = 0.0
        
        return {
            'recommendation': recommendation,
            'position_size': position_size,
            'confidence': confidence,
            'expected_return': expected_gap,
            'stop_loss': expected_gap * -0.5,
            'take_profit': expected_gap * 1.5
        }
    
    def _calculate_overall_confidence(self, historical: Dict, context: Dict, risk: Dict) -> float:
        """Calculate overall prediction confidence"""
        hist_confidence = historical.get('confidence', 0.5)
        context_strength = min(1.0, abs(context.get('overall_sentiment', 0.0)) / 2.0)
        risk_adjustment = 1.0 - risk.get('overall_risk_score', 0.5)
        
        overall_confidence = (hist_confidence * 0.5 + context_strength * 0.3 + risk_adjustment * 0.2)
        return min(1.0, max(0.0, overall_confidence))
    
    def _calculate_historical_accuracy(self, gaps: List[float], directions: List[str]) -> float:
        """Calculate historical prediction accuracy"""
        if not gaps or not directions:
            return 0.0
        
        # Simplified accuracy calculation
        # In production, would compare with actual historical predictions
        correct_predictions = 0
        # Use consistent sample - exclude last 10 for testing, but count only what we evaluate
        evaluation_directions = directions[:-10] if len(directions) > 10 else directions
        total_predictions = len(evaluation_directions)
        
        for i, direction in enumerate(evaluation_directions):
            if i < len(gaps):  # Ensure we have corresponding gap data
                actual_gap = gaps[i]
                if direction == 'UP' and actual_gap > 0:
                    correct_predictions += 1
                elif direction == 'DOWN' and actual_gap < 0:
                    correct_predictions += 1
                elif direction == 'FLAT' and abs(actual_gap) < 1.0:
                    correct_predictions += 1
        
        accuracy = (correct_predictions / total_predictions) * 100 if total_predictions > 0 else 0.0
        return min(100.0, max(0.0, accuracy))
    
    def _create_default_gap_analysis(self) -> GapAnalysis:
        """Create default gap analysis for error cases"""
        return GapAnalysis(
            expected_gap_pct=1.5,
            gap_direction='FLAT',
            confidence=0.5,
            historical_accuracy=0.0,
            contextual_factors={},
            risk_factors={'volatility_risk': 0.5, 'pattern_reliability': 0.5}
        )
    
    def _create_default_prediction(self, symbol: str, horizon: str) -> NextDayPrediction:
        """Create default prediction for error cases"""
        return NextDayPrediction(
            target_price=0.0,
            expected_gap_pct=0.0,
            direction='FLAT',
            confidence=0.3,
            risk_level='HIGH',
            position_size=0.0,
            profit_range=(0.0, 0.0),
            time_horizon=horizon,
            contextual_analysis={},
            execution_details={},
            timestamp=datetime.now().isoformat()
        )

# Create global instance
gap_nextday_predictor = NextDayGapPredictor()