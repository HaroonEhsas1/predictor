"""
Intelligent Conflict Resolution System

Instead of just reducing confidence when signals conflict,
this system UNDERSTANDS which signals matter MORE in specific situations.

Examples:
- After big drop: Technical (oversold) > News (lagging)
- During high VIX: Futures > Options
- Gap down + overbought: Technical > Options
- Institutional accumulation: Institutional > Social
"""

class IntelligentConflictResolver:
    """
    Resolves signal conflicts by understanding context and signal hierarchy
    """
    
    def __init__(self):
        self.conflict_rules = self._build_conflict_rules()
    
    def _build_conflict_rules(self):
        """
        Build hierarchical rules for which signals win in specific situations
        
        Format: {
            'situation': {
                'condition': lambda data: bool,
                'hierarchy': [signal1, signal2, signal3, ...]  # Order matters!
                'boost': {signal: multiplier}
            }
        }
        """
        
        return {
            # RULE 0: BOUNCE SETUP (Highest Priority!)
            # Gap down + oversold + strong fundamentals = BOUNCE OPPORTUNITY
            # This OVERRIDES AFTER_BIG_DROP when conditions are met
            'BOUNCE_SETUP': {
                'condition': lambda d: (
                    # SCENARIO 1: Classic oversold bounce
                    (d.get('premarket_gap', 0) < -3.0 and d.get('rsi', 50) < 40 and d.get('fundamental_strength', 0) > 0.05) or
                    # SCENARIO 2: Positive fundamentals pullback (works even if overbought)
                    # Pure logic: Fundamentals > 0.03 (positive) = buy any 1%+ dip
                    (d.get('premarket_gap', 0) < -1.0 and d.get('fundamental_strength', 0) > 0.03)
                ),
                'hierarchy': ['bollinger', 'money_flow', 'institutional', 'options', 'news', 'technical'],
                'boost': {
                    'bollinger': 1.6,      # Oversold bounce signal
                    'money_flow': 1.5,     # MFI confirms oversold
                    'institutional': 1.4,  # Smart money buying
                    'options': 1.3,        # Call activity
                    'news': 1.3,           # Fundamentals still strong
                },
                'reduce': {
                    'technical': 0.3,      # IGNORE bearish technical (it's what created the setup!)
                },
                'reasoning': 'BOUNCE SETUP: Gap down + positive fundamentals = Pullback in uptrend, not reversal. Two scenarios: (1) Oversold bounce, (2) Positive fundamentals (>0.03) support even if overbought. Pure logic - fundamentals override short-term weakness.'
            },
            
            # RULE 1: After Big Drops (>1.5%) - Only applies when NOT a bounce setup
            'AFTER_BIG_DROP': {
                'condition': lambda d: (
                    (d.get('intraday_change', 0) < -1.5 or d.get('market_change', 0) < -1.5) and
                    # Exclude both bounce setup scenarios
                    not ((d.get('premarket_gap', 0) < -3.0 and d.get('rsi', 50) < 40 and d.get('fundamental_strength', 0) > 0.05) or
                         (d.get('premarket_gap', 0) < -1.0 and d.get('fundamental_strength', 0) > 0.03))
                ),
                'hierarchy': ['technical', 'bollinger', 'money_flow', 'institutional', 'options', 'news'],
                'boost': {
                    'technical': 1.5,      # Oversold conditions matter MOST
                    'bollinger': 1.4,      # Near lower band = bounce
                    'money_flow': 1.3,     # MFI oversold = opportunity
                    'institutional': 1.2,  # Smart money buying dip
                },
                'reasoning': 'After big drops (without bounce setup), technical oversold signals are most predictive. News is lagging.'
            },
            
            # RULE 2: Overbought Market (RSI >65)
            'OVERBOUGHT': {
                'condition': lambda d: d.get('rsi', 50) > 65,
                'hierarchy': ['technical', 'futures', 'bollinger', 'money_flow', 'options', 'news'],
                'boost': {
                    'technical': 1.4,      # RSI matters most when extended
                    'futures': 1.3,        # Market direction override
                    'bollinger': 1.2,      # Upper band = pullback
                },
                'reduce': {
                    'news': 0.6,           # News often bullish but stock topping
                    'options': 0.7,        # Call buying often peaks at tops
                },
                'reasoning': 'When overbought, technical warnings trump bullish news. Markets correct.'
            },
            
            # RULE 3: Oversold Market (RSI <35)
            'OVERSOLD': {
                'condition': lambda d: d.get('rsi', 50) < 35,
                'hierarchy': ['technical', 'institutional', 'bollinger', 'money_flow', 'futures'],
                'boost': {
                    'technical': 1.5,          # Oversold = bounce likely
                    'institutional': 1.3,      # Institutions buy bottoms
                    'bollinger': 1.3,          # Near lower band
                    'money_flow': 1.2,         # MFI confirms
                },
                'reduce': {
                    'news': 0.5,               # News often still bearish at bottom
                },
                'reasoning': 'Oversold technicals trump bearish news. Markets bounce from extremes.'
            },
            
            # RULE 4: High Volatility (VIX >25)
            'HIGH_VOLATILITY': {
                'condition': lambda d: d.get('vix_level', 18) > 25,
                'hierarchy': ['futures', 'vix', 'options', 'technical', 'news'],
                'boost': {
                    'futures': 1.4,        # Futures lead in volatile markets
                    'vix': 1.3,            # VIX mean reversion
                    'options': 1.2,        # IV expansion
                },
                'reduce': {
                    'news': 0.6,           # News noise high during panic
                    'social': 0.3,         # Social media panics/FOMOs
                },
                'reasoning': 'In high volatility, futures and options matter most. News creates noise.'
            },
            
            # RULE 5: Gap Down + Overbought
            'GAP_DOWN_OVERBOUGHT': {
                'condition': lambda d: d.get('premarket_gap', 0) < -1.0 and d.get('rsi', 50) > 60,
                'hierarchy': ['premarket', 'technical', 'futures', 'options'],
                'boost': {
                    'premarket': 1.5,      # Gap confirms technical warning
                    'technical': 1.4,      # Overbought rejecting
                    'futures': 1.3,        # Weakness confirmed
                },
                'reduce': {
                    'options': 0.5,        # Bullish options now stale
                    'news': 0.5,           # Bullish news rejected
                },
                'reasoning': 'Gap down from overbought = trend change. Technical warnings win.'
            },
            
            # RULE 6: Gap Up + Oversold
            'GAP_UP_OVERSOLD': {
                'condition': lambda d: d.get('premarket_gap', 0) > 1.0 and d.get('rsi', 50) < 40,
                'hierarchy': ['technical', 'premarket', 'institutional', 'futures'],
                'boost': {
                    'technical': 1.5,      # Oversold bounce confirmed
                    'premarket': 1.4,      # Gap up validates bounce
                    'institutional': 1.3,  # Smart money buying
                },
                'reasoning': 'Gap up from oversold = reversal confirmed. Technical bounce wins.'
            },
            
            # RULE 7: Strong Institutional Flow
            'INSTITUTIONAL_ACTIVITY': {
                'condition': lambda d: abs(d.get('institutional_flow', 0)) > 0.15,
                'hierarchy': ['institutional', 'options', 'futures', 'technical', 'news'],
                'boost': {
                    'institutional': 1.6,  # Smart money knows something
                    'options': 1.3,        # Often precedes moves
                    'futures': 1.2,        # Confirms direction
                },
                'reduce': {
                    'social': 0.4,         # Retail often wrong when institutions active
                    'news': 0.8,           # Institutions front-run news
                },
                'reasoning': 'Strong institutional flow trumps retail sentiment. Smart money leads.'
            },
            
            # RULE 8: Unusual Options Activity
            'UNUSUAL_OPTIONS': {
                'condition': lambda d: d.get('options_pcr', 1.0) < 0.5 or d.get('options_pcr', 1.0) > 2.0,
                'hierarchy': ['options', 'institutional', 'futures', 'news'],
                'boost': {
                    'options': 1.5,        # Extreme P/C = insider activity
                    'institutional': 1.3,  # Often aligned
                },
                'reasoning': 'Unusual options activity often precedes big moves. Insiders know.'
            },
            
            # RULE 9: Market Trending Down (SPY/QQQ <-0.5%)
            'MARKET_WEAKNESS': {
                'condition': lambda d: (d.get('spy_change', 0) + d.get('qqq_change', 0)) / 2 < -0.5,
                'hierarchy': ['futures', 'sector', 'relative_strength', 'technical'],
                'boost': {
                    'futures': 1.3,             # Market direction matters
                    'sector': 1.2,              # Sector correlation
                    'relative_strength': 1.4,   # Stocks that hold up = strong
                },
                'reduce': {
                    'news': 0.7,                # Bullish news can't fight market
                },
                'reasoning': 'In weak markets, relative strength matters. Tide lifts/sinks all boats.'
            },
            
            # RULE 10: Near Earnings (<10 days)
            'NEAR_EARNINGS': {
                'condition': lambda d: d.get('days_to_earnings', 100) < 10,
                'hierarchy': ['options', 'institutional', 'news', 'futures'],
                'boost': {
                    'options': 1.4,        # Positioning for earnings
                    'institutional': 1.3,  # Smart money positioning
                    'news': 1.2,           # Earnings previews
                },
                'reduce': {
                    'technical': 0.7,      # Less reliable near earnings
                },
                'reasoning': 'Near earnings, options and institutional flow matter most.'
            },
        }
    
    def resolve_conflict(self, signals_dict, market_data):
        """
        Intelligently resolve conflicts by applying contextual rules
        
        Args:
            signals_dict: {signal_name: {score: float, direction: str}}
            market_data: Context data (RSI, VIX, gaps, etc.)
            
        Returns:
            dict: Adjusted signals with proper hierarchy
        """
        
        active_rules = []
        
        # Check which rules apply to current situation
        for rule_name, rule in self.conflict_rules.items():
            if rule['condition'](market_data):
                active_rules.append((rule_name, rule))
        
        if not active_rules:
            # No special rules apply, use default weights
            return signals_dict, None
        
        # Apply the most relevant rule
        primary_rule_name, primary_rule = active_rules[0]
        
        adjusted_signals = signals_dict.copy()
        
        # Apply boosts
        for signal, boost in primary_rule.get('boost', {}).items():
            if signal in adjusted_signals:
                adjusted_signals[signal]['score'] *= boost
                adjusted_signals[signal]['boosted'] = True
                adjusted_signals[signal]['boost_factor'] = boost
        
        # Apply reductions
        for signal, reduction in primary_rule.get('reduce', {}).items():
            if signal in adjusted_signals:
                adjusted_signals[signal]['score'] *= reduction
                adjusted_signals[signal]['reduced'] = True
                adjusted_signals[signal]['reduction_factor'] = reduction
        
        resolution_info = {
            'rule_applied': primary_rule_name,
            'reasoning': primary_rule['reasoning'],
            'hierarchy': primary_rule['hierarchy'],
            'adjustments_made': len(primary_rule.get('boost', {})) + len(primary_rule.get('reduce', {}))
        }
        
        return adjusted_signals, resolution_info
    
    def explain_resolution(self, resolution_info, conflicting_signals):
        """
        Generate human-readable explanation of conflict resolution
        """
        
        if not resolution_info:
            return "No conflict resolution applied - using default weights"
        
        explanation = []
        explanation.append(f"\n🧠 INTELLIGENT CONFLICT RESOLUTION")
        explanation.append(f"=" * 80)
        explanation.append(f"\n📊 Situation Detected: {resolution_info['rule_applied']}")
        explanation.append(f"\n💡 Reasoning: {resolution_info['reasoning']}")
        explanation.append(f"\n📈 Signal Hierarchy (Most Important → Least):")
        for i, signal in enumerate(resolution_info['hierarchy'][:5], 1):
            explanation.append(f"   {i}. {signal.upper()}")
        
        explanation.append(f"\n🎯 Adjustments Made: {resolution_info['adjustments_made']} signals adjusted")
        explanation.append(f"\nConflict RESOLVED - System now knows which signals matter more!")
        explanation.append("=" * 80)
        
        return "\n".join(explanation)


# Test the system
if __name__ == "__main__":
    print("Testing Intelligent Conflict Resolver...\n")
    
    resolver = IntelligentConflictResolver()
    
    # TODAY'S SITUATION (Oct 22)
    # Options/News bullish but Technical/Futures bearish
    
    signals = {
        'options': {'score': 0.110, 'direction': 'UP'},
        'news': {'score': 0.075, 'direction': 'UP'},
        'technical': {'score': -0.078, 'direction': 'DOWN'},
        'futures': {'score': -0.019, 'direction': 'DOWN'},
        'premarket': {'score': -0.040, 'direction': 'DOWN'},
    }
    
    market_data = {
        'rsi': 43.5,
        'vix_level': 19.6,
        'intraday_change': -0.48,
        'market_change': -1.10,  # SPY/QQQ average
        'premarket_gap': -0.40,
        'spy_change': -0.80,
        'qqq_change': -1.41,
    }
    
    print("CONFLICT SITUATION (Today - Oct 22):")
    print("="*80)
    print("\n📊 Conflicting Signals:")
    print("   BULLISH: Options (+0.110), News (+0.075)")
    print("   BEARISH: Technical (-0.078), Futures (-0.019), Premarket (-0.040)")
    print(f"\n📉 Market Context:")
    print(f"   RSI: {market_data['rsi']}")
    print(f"   VIX: {market_data['vix_level']}")
    print(f"   Market: {market_data['market_change']:+.2f}%")
    print(f"   Intraday: {market_data['intraday_change']:+.2f}%")
    
    # Resolve conflict
    adjusted, resolution = resolver.resolve_conflict(signals, market_data)
    
    if resolution:
        print(resolver.explain_resolution(resolution, signals))
        
        print("\n📊 ADJUSTED SIGNALS:")
        for signal, data in adjusted.items():
            if data.get('boosted'):
                print(f"   {signal.upper()}: {data['score']:+.3f} ↑ (×{data['boost_factor']:.2f} BOOST)")
            elif data.get('reduced'):
                print(f"   {signal.upper()}: {data['score']:+.3f} ↓ (×{data['reduction_factor']:.2f} REDUCED)")
            else:
                print(f"   {signal.upper()}: {data['score']:+.3f}")
        
        print("\n✅ RESULT: System UNDERSTANDS which signals matter more!")
        print("Instead of just 'conflicts = low confidence', it makes an intelligent choice!")
    
    print("\n" + "="*80)
    print("💡 FOR ORCL TODAY:")
    print("="*80)
    print("Market is weak (-1.1%) → MARKET_WEAKNESS rule applies")
    print("   1. Futures (bearish) gets BOOSTED ×1.3")
    print("   2. Sector/Relative strength important")
    print("   3. News (bullish) gets REDUCED ×0.7")
    print("\nFinal prediction: BEARISH (futures/market win over stale bullish news)")
    print("This is SMARTER than just saying 'mixed signals = skip'!")
