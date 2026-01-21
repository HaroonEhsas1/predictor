"""
Prediction System Improvements
Based on October 22, 2025 failure analysis
Critical fixes to improve accuracy from 0/3 to 2/3+
"""

import yfinance as yf
from datetime import datetime, timedelta

class PredictionImprovements:
    """Critical improvements to fix Oct 22 failures"""
    
    @staticmethod
    def get_market_regime():
        """
        FIX #1: Market Regime Detection
        Check SPY/QQQ trend to set market bias
        Prevents bullish predictions when market is weak
        """
        try:
            spy = yf.Ticker('SPY')
            spy_hist = spy.history(period='2d')
            
            if len(spy_hist) >= 2:
                spy_yesterday = spy_hist['Close'].iloc[-2]
                spy_today = spy_hist['Close'].iloc[-1]
                spy_change_pct = ((spy_today - spy_yesterday) / spy_yesterday) * 100
                
                # Also check QQQ for tech stocks
                qqq = yf.Ticker('QQQ')
                qqq_hist = qqq.history(period='2d')
                
                if len(qqq_hist) >= 2:
                    qqq_yesterday = qqq_hist['Close'].iloc[-2]
                    qqq_today = qqq_hist['Close'].iloc[-1]
                    qqq_change_pct = ((qqq_today - qqq_yesterday) / qqq_yesterday) * 100
                    
                    # Average for overall market sentiment
                    market_change = (spy_change_pct + qqq_change_pct) / 2
                    
                    # Determine regime
                    if market_change < -0.5:
                        return {
                            'regime': 'BEARISH',
                            'bias': -0.05,  # Reduce bullish scores
                            'spy_change': spy_change_pct,
                            'qqq_change': qqq_change_pct,
                            'market_change': market_change,
                            'message': f"Market WEAK (SPY {spy_change_pct:+.2f}%, QQQ {qqq_change_pct:+.2f}%)"
                        }
                    elif market_change > 0.5:
                        return {
                            'regime': 'BULLISH',
                            'bias': +0.05,  # Boost bullish scores
                            'spy_change': spy_change_pct,
                            'qqq_change': qqq_change_pct,
                            'market_change': market_change,
                            'message': f"Market STRONG (SPY {spy_change_pct:+.2f}%, QQQ {qqq_change_pct:+.2f}%)"
                        }
                    else:
                        return {
                            'regime': 'NEUTRAL',
                            'bias': 0.0,
                            'spy_change': spy_change_pct,
                            'qqq_change': qqq_change_pct,
                            'market_change': market_change,
                            'message': f"Market NEUTRAL (SPY {spy_change_pct:+.2f}%, QQQ {qqq_change_pct:+.2f}%)"
                        }
            
        except Exception as e:
            print(f"   ⚠️ Market regime detection error: {e}")
        
        # Default to neutral if can't determine
        return {
            'regime': 'NEUTRAL',
            'bias': 0.0,
            'spy_change': 0,
            'qqq_change': 0,
            'market_change': 0,
            'message': 'Market data unavailable'
        }
    
    @staticmethod
    def apply_technical_veto(technical_score, total_score, confidence):
        """
        FIX #2: Technical Signal Veto Power
        When technical conflicts with other signals, investigate deeper
        ORCL case study: Technical -0.078 was CORRECT but got overridden
        """
        # Check if technical conflicts with total direction
        if technical_score * total_score < 0:  # Opposite signs = conflict
            # Technical says one thing, everything else says another
            technical_strength = abs(technical_score)
            total_strength = abs(total_score)
            
            if technical_strength > 0.05:  # Significant technical signal
                # This is a warning sign - reduce confidence
                conflict_penalty = 0.7  # Reduce confidence by 30%
                
                # If technical is strong relative to total, dampen the total
                if technical_strength > total_strength * 0.3:
                    # Technical warning is strong - listen to it
                    dampening = 0.6  # Reduce total score by 40%
                    new_total_score = total_score * dampening
                    
                    return {
                        'applied': True,
                        'new_total_score': new_total_score,
                        'new_confidence': confidence * conflict_penalty,
                        'message': f"⚠️ TECHNICAL CONFLICT: Technical {technical_score:+.3f} vs Total {total_score:+.3f}",
                        'warning': "Technical analysis disagrees strongly - reducing conviction"
                    }
        
        return {'applied': False}
    
    @staticmethod
    def adjust_options_on_conflict(options_score, news_score, technical_score):
        """
        FIX #3: Reduce Options Weight When Conflicting
        AVGO case study: Options -0.110 was WRONG, but News +0.084 and Technical +0.042 were RIGHT
        Options can be unreliable - reduce weight when other signals conflict
        """
        # Check if options conflicts with news + technical
        combined_other = news_score + technical_score
        
        if options_score * combined_other < 0:  # Conflict
            # Options says one thing, news+technical say another
            if abs(combined_other) > abs(options_score) * 0.5:
                # News+Technical are strong enough to challenge options
                # Reduce options influence
                adjusted_options_score = options_score * 0.5
                
                return {
                    'applied': True,
                    'original_options_score': options_score,
                    'adjusted_options_score': adjusted_options_score,
                    'reduction': options_score - adjusted_options_score,
                    'message': f"⚠️ OPTIONS CONFLICT: Options {options_score:+.3f} vs News+Tech {combined_other:+.3f}",
                    'warning': "Options contradicts news and technical - reducing options weight by 50%"
                }
        
        return {'applied': False, 'adjusted_options_score': options_score}
    
    @staticmethod
    def calculate_signal_conflicts(scores_dict):
        """
        FIX #4: Confidence Penalty for Conflicting Signals
        AVGO had 81% confidence but had conflicting signals - should have been lower
        Count how many signals conflict with main direction
        """
        # Determine main direction from total
        total_score = sum(scores_dict.values())
        main_direction = 1 if total_score > 0 else -1
        
        # Count conflicts
        conflicting_signals = []
        aligned_signals = []
        
        for name, score in scores_dict.items():
            if abs(score) > 0.01:  # Only count significant signals
                if score * main_direction < 0:  # Conflicts
                    conflicting_signals.append((name, score))
                else:
                    aligned_signals.append((name, score))
        
        conflict_count = len(conflicting_signals)
        aligned_count = len(aligned_signals)
        
        # Calculate confidence penalty
        if conflict_count == 0:
            penalty_multiplier = 1.0  # No penalty
        elif conflict_count == 1:
            penalty_multiplier = 0.95  # Small penalty
        elif conflict_count == 2:
            penalty_multiplier = 0.85  # Medium penalty (AVGO case)
        elif conflict_count >= 3:
            penalty_multiplier = 0.75  # Large penalty
        else:
            penalty_multiplier = 0.9
        
        return {
            'conflict_count': conflict_count,
            'aligned_count': aligned_count,
            'conflicting_signals': conflicting_signals,
            'aligned_signals': aligned_signals,
            'penalty_multiplier': penalty_multiplier,
            'message': f"Signal Alignment: {aligned_count} aligned, {conflict_count} conflicting"
        }
    
    @staticmethod
    def apply_news_freshness_decay(news_score, news_age_hours):
        """
        FIX #5: News Freshness Decay
        News that's >4 hours old at prediction time (3:50 PM) is less reliable
        AMD/ORCL case: News was misleading, may have been stale
        """
        if news_age_hours > 4:
            # Stale news - apply decay
            if news_age_hours > 8:
                decay_factor = 0.3  # Very stale - keep only 30%
            else:
                decay_factor = 0.5  # Somewhat stale - keep only 50%
            
            adjusted_news_score = news_score * decay_factor
            
            return {
                'applied': True,
                'original_news_score': news_score,
                'adjusted_news_score': adjusted_news_score,
                'news_age_hours': news_age_hours,
                'decay_factor': decay_factor,
                'message': f"⏰ NEWS DECAY: News {news_age_hours:.1f}h old - applying {decay_factor*100:.0f}% decay"
            }
        
        return {'applied': False, 'adjusted_news_score': news_score}
    
    @staticmethod
    def check_afterhours_futures(time_of_prediction=None):
        """
        FIX #6: After-Hours Futures Trend Check
        At 3:50 PM, check what futures are doing for after-hours guidance
        If futures trending down in last 30 mins, reduce bullish bias
        """
        try:
            # Get ES and NQ futures
            es_futures = yf.Ticker('ES=F')
            nq_futures = yf.Ticker('NQ=F')
            
            # Get last 1 hour of data
            es_hist = es_futures.history(period='1d', interval='5m')
            nq_hist = nq_futures.history(period='1d', interval='5m')
            
            if len(es_hist) >= 6 and len(nq_hist) >= 6:  # At least 30 mins of data
                # Compare last 30 mins trend
                es_30min_ago = es_hist['Close'].iloc[-6]
                es_now = es_hist['Close'].iloc[-1]
                es_trend = ((es_now - es_30min_ago) / es_30min_ago) * 100
                
                nq_30min_ago = nq_hist['Close'].iloc[-6]
                nq_now = nq_hist['Close'].iloc[-1]
                nq_trend = ((nq_now - nq_30min_ago) / nq_30min_ago) * 100
                
                avg_trend = (es_trend + nq_trend) / 2
                
                if avg_trend < -0.2:
                    return {
                        'trend': 'BEARISH',
                        'adjustment': -0.03,
                        'es_trend': es_trend,
                        'nq_trend': nq_trend,
                        'message': f"⚠️ FUTURES WEAKENING: ES {es_trend:+.2f}%, NQ {nq_trend:+.2f}% (last 30min)"
                    }
                elif avg_trend > 0.2:
                    return {
                        'trend': 'BULLISH',
                        'adjustment': +0.03,
                        'es_trend': es_trend,
                        'nq_trend': nq_trend,
                        'message': f"✅ FUTURES STRENGTHENING: ES {es_trend:+.2f}%, NQ {nq_trend:+.2f}% (last 30min)"
                    }
        
        except Exception as e:
            pass
        
        return {'trend': 'NEUTRAL', 'adjustment': 0.0}
    
    @staticmethod
    def generate_improvement_report(fixes_applied):
        """Generate a report of all improvements applied"""
        report_lines = []
        report_lines.append("\n" + "="*80)
        report_lines.append("🔧 PREDICTION IMPROVEMENTS APPLIED")
        report_lines.append("="*80)
        
        for fix_name, fix_data in fixes_applied.items():
            if fix_data.get('applied', False):
                report_lines.append(f"\n✅ {fix_name}:")
                if 'message' in fix_data:
                    report_lines.append(f"   {fix_data['message']}")
                if 'warning' in fix_data:
                    report_lines.append(f"   {fix_data['warning']}")
        
        report_lines.append("="*80)
        return "\n".join(report_lines)


# Example usage for integration
if __name__ == "__main__":
    improvements = PredictionImprovements()
    
    # Test market regime detection
    print("Testing Market Regime Detection:")
    regime = improvements.get_market_regime()
    print(f"  {regime['message']}")
    print(f"  Bias adjustment: {regime['bias']:+.3f}")
    
    # Test technical veto
    print("\nTesting Technical Veto (ORCL case):")
    technical_score = -0.078  # ORCL's bearish technical warning
    total_score = +0.133  # Bullish total from options/news/institutional
    confidence = 71.31
    
    veto_result = improvements.apply_technical_veto(technical_score, total_score, confidence)
    if veto_result['applied']:
        print(f"  {veto_result['message']}")
        print(f"  Original score: {total_score:+.3f} → New score: {veto_result['new_total_score']:+.3f}")
        print(f"  Original confidence: {confidence:.2f}% → New confidence: {veto_result['new_confidence']:.2f}%")
    
    # Test options adjustment
    print("\nTesting Options Adjustment (AVGO case):")
    options_score = -0.110  # AVGO's wrong bearish options signal
    news_score = +0.084  # AVGO's correct bullish news
    technical_score = +0.042  # AVGO's correct bullish technical
    
    options_adj = improvements.adjust_options_on_conflict(options_score, news_score, technical_score)
    if options_adj['applied']:
        print(f"  {options_adj['message']}")
        print(f"  Original options: {options_adj['original_options_score']:+.3f} → Adjusted: {options_adj['adjusted_options_score']:+.3f}")
    
    # Test conflict counting
    print("\nTesting Conflict Counting (AVGO case):")
    scores = {
        'options': -0.110,
        'news': +0.084,
        'technical': +0.042,
        'futures': +0.020
    }
    
    conflicts = improvements.calculate_signal_conflicts(scores)
    print(f"  {conflicts['message']}")
    print(f"  Confidence penalty: {conflicts['penalty_multiplier']*100:.0f}%")
    print(f"  Conflicting: {[f'{name}:{score:+.3f}' for name, score in conflicts['conflicting_signals']]}")
