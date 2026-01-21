#!/usr/bin/env python3
"""
Market Environment Filter
Based on Warren Buffett & Ray Dalio wisdom
Warns when market is extended or dangerous
"""

import yfinance as yf
from datetime import datetime, timedelta

class MarketEnvironmentFilter:
    """Analyze overall market environment and provide warnings"""
    
    def __init__(self):
        self.sp500 = yf.Ticker("^GSPC")
        self.vix = yf.Ticker("^VIX")
        self.nasdaq = yf.Ticker("^IXIC")
    
    def get_market_condition(self):
        """Analyze current market environment"""
        
        print("\n" + "="*80)
        print("🌍 MARKET ENVIRONMENT ANALYSIS")
        print("="*80)
        
        conditions = []
        warnings = []
        
        # Get VIX level
        vix_data = self.vix.history(period='5d')
        if not vix_data.empty:
            current_vix = float(vix_data['Close'].iloc[-1])
            print(f"\n📊 VIX (Fear Gauge): {current_vix:.2f}")
            
            if current_vix < 12:
                conditions.append('COMPLACENCY')
                warnings.append("VIX <12 = Market complacency - Be cautious!")
                print(f"   ⚠️ VERY LOW - Market complacent")
            elif current_vix < 15:
                conditions.append('LOW_FEAR')
                print(f"   ✅ LOW - Market calm")
            elif current_vix < 20:
                conditions.append('NORMAL')
                print(f"   ✅ NORMAL - Healthy fear level")
            elif current_vix < 30:
                conditions.append('ELEVATED')
                print(f"   ⚠️ ELEVATED - Increased volatility")
            else:
                conditions.append('FEAR')
                warnings.append("VIX >30 = High fear - Reduce position sizes!")
                print(f"   🚨 HIGH - Market fear")
        
        # Get S&P 500 position relative to highs
        sp_data = self.sp500.history(period='1y')
        if not sp_data.empty:
            current_sp = float(sp_data['Close'].iloc[-1])
            year_high = float(sp_data['High'].max())
            pct_from_high = ((current_sp - year_high) / year_high) * 100
            
            print(f"\n📈 S&P 500: {current_sp:.2f}")
            print(f"   52-Week High: {year_high:.2f}")
            print(f"   From High: {pct_from_high:+.1f}%")
            
            if pct_from_high > -2:
                conditions.append('AT_HIGHS')
                if current_vix < 15:
                    warnings.append("Market at highs + low VIX = Extended! (Buffett warning)")
                print(f"   ⚠️ NEAR ALL-TIME HIGHS")
            elif pct_from_high > -5:
                conditions.append('NEAR_HIGHS')
                print(f"   ✅ NEAR HIGHS - Normal")
            elif pct_from_high > -10:
                conditions.append('PULLBACK')
                print(f"   ✅ SLIGHT PULLBACK - Healthy")
            elif pct_from_high > -20:
                conditions.append('CORRECTION')
                print(f"   💡 CORRECTION - Opportunity?")
            else:
                conditions.append('BEAR_MARKET')
                print(f"   🐻 BEAR MARKET - High risk")
        
        # Get NASDAQ trend
        nasdaq_data = self.nasdaq.history(period='90d')
        if not nasdaq_data.empty:
            # Calculate 200-day MA
            close_prices = nasdaq_data['Close']
            if len(close_prices) >= 50:
                ma_50 = close_prices.rolling(50).mean().iloc[-1]
                current_nasdaq = float(close_prices.iloc[-1])
                
                print(f"\n📊 NASDAQ: {current_nasdaq:.2f}")
                print(f"   50-day MA: {ma_50:.2f}")
                
                pct_from_ma = ((current_nasdaq - ma_50) / ma_50) * 100
                print(f"   From MA: {pct_from_ma:+.1f}%")
                
                if pct_from_ma > 5:
                    conditions.append('EXTENDED')
                    if 'AT_HIGHS' in conditions:
                        warnings.append("Market extended above MA + at highs = Risky!")
                    print(f"   ⚠️ EXTENDED above moving average")
                elif pct_from_ma > -5:
                    conditions.append('NORMAL_TREND')
                    print(f"   ✅ NORMAL trend")
                else:
                    conditions.append('WEAK_TREND')
                    print(f"   ⚠️ WEAK - Below moving average")
        
        # Overall assessment
        print(f"\n🎯 OVERALL MARKET CONDITION:")
        print(f"   Conditions: {', '.join(conditions)}")
        
        # Determine trading recommendation
        risk_level = self.calculate_risk_level(conditions, current_vix if 'current_vix' in locals() else 20)
        
        print(f"\n💡 TRADING RECOMMENDATION:")
        if risk_level == 'HIGH_RISK':
            print(f"   🚨 HIGH RISK ENVIRONMENT")
            print(f"   → Reduce ALL position sizes by 50%")
            print(f"   → Be very selective (only 80%+ confidence)")
            print(f"   → Consider raising cash")
            position_multiplier = 0.5
        elif risk_level == 'ELEVATED_RISK':
            print(f"   ⚠️ ELEVATED RISK")
            print(f"   → Reduce position sizes by 20-30%")
            print(f"   → Be selective (70%+ confidence)")
            print(f"   → Watch for reversals")
            position_multiplier = 0.75
        elif risk_level == 'NORMAL':
            print(f"   ✅ NORMAL CONDITIONS")
            print(f"   → Trade normally")
            print(f"   → Follow system signals")
            print(f"   → Standard position sizes")
            position_multiplier = 1.0
        else:  # OPPORTUNITY
            print(f"   💡 OPPORTUNITY")
            print(f"   → Market pullback = potential opportunity")
            print(f"   → But use normal or slightly smaller sizes")
            print(f"   → Fear creates opportunities")
            position_multiplier = 1.0
        
        if warnings:
            print(f"\n⚠️ WARNINGS:")
            for warning in warnings:
                print(f"   • {warning}")
        
        print("="*80)
        
        return {
            'conditions': conditions,
            'risk_level': risk_level,
            'position_multiplier': position_multiplier,
            'warnings': warnings,
            'vix': current_vix if 'current_vix' in locals() else None
        }
    
    def calculate_risk_level(self, conditions, vix):
        """Calculate overall risk level"""
        
        # High risk scenarios
        if ('AT_HIGHS' in conditions and 'COMPLACENCY' in conditions):
            # Buffett warning: Market at highs + low VIX
            return 'HIGH_RISK'
        
        if ('EXTENDED' in conditions and 'AT_HIGHS' in conditions):
            # Extended above MA and at all-time highs
            return 'HIGH_RISK'
        
        if ('FEAR' in conditions):
            # VIX >30 = High volatility
            return 'HIGH_RISK'
        
        # Elevated risk
        if ('AT_HIGHS' in conditions or 'EXTENDED' in conditions):
            return 'ELEVATED_RISK'
        
        if ('COMPLACENCY' in conditions):
            return 'ELEVATED_RISK'
        
        # Opportunity
        if ('CORRECTION' in conditions or 'PULLBACK' in conditions):
            return 'OPPORTUNITY'
        
        # Normal
        return 'NORMAL'
    
    def should_trade_today(self, system_confidence):
        """
        Decide if should trade based on market environment
        Returns: (should_trade, adjusted_confidence, reason)
        """
        env = self.get_market_condition()
        
        # Adjust confidence based on environment
        adjusted_conf = system_confidence
        
        if env['risk_level'] == 'HIGH_RISK':
            # High risk - need much higher confidence
            if system_confidence < 80:
                return (False, adjusted_conf, 
                       f"Market too risky (confidence {system_confidence:.0f}% < 80% required)")
            adjusted_conf *= 0.9  # Reduce confidence slightly
            return (True, adjusted_conf, 
                   f"HIGH RISK environment - proceed with caution")
        
        elif env['risk_level'] == 'ELEVATED_RISK':
            # Elevated risk - higher threshold
            if system_confidence < 70:
                return (False, adjusted_conf,
                       f"Elevated risk (confidence {system_confidence:.0f}% < 70% required)")
            return (True, adjusted_conf,
                   f"ELEVATED RISK - be selective")
        
        elif env['risk_level'] == 'NORMAL':
            # Normal - use system threshold
            if system_confidence < 60:
                return (False, adjusted_conf,
                       f"Confidence {system_confidence:.0f}% < 60% minimum")
            return (True, adjusted_conf,
                   f"NORMAL conditions - trade as usual")
        
        else:  # OPPORTUNITY
            # Opportunity - can be slightly more aggressive
            if system_confidence < 55:
                return (False, adjusted_conf,
                       f"Confidence {system_confidence:.0f}% < 55% minimum")
            return (True, adjusted_conf,
                   f"OPPORTUNITY - market pullback")

# Example usage
if __name__ == "__main__":
    filter = MarketEnvironmentFilter()
    env = filter.get_market_condition()
    
    # Test with different confidence levels
    print(f"\n{'='*80}")
    print(f"🎯 TRADING DECISIONS:")
    print(f"{'='*80}\n")
    
    for conf in [85, 75, 65, 55]:
        should_trade, adj_conf, reason = filter.should_trade_today(conf)
        status = "✅ TRADE" if should_trade else "❌ SKIP"
        print(f"System Confidence: {conf}%")
        print(f"   {status}: {reason}")
        if should_trade and adj_conf != conf:
            print(f"   Adjusted Confidence: {adj_conf:.1f}%")
        print()
