#!/usr/bin/env python3
"""
Performance Tracker - Track Win Rate & Adjust Position Sizing
Based on legendary traders' wisdom (Paul Tudor Jones, Ray Dalio)
"""

import json
from datetime import datetime
from pathlib import Path

class PerformanceTracker:
    """Track trading performance and adjust position sizing"""
    
    def __init__(self, trades_file='trades_history.json'):
        self.trades_file = Path(__file__).parent / trades_file
        self.trades = self.load_trades()
    
    def load_trades(self):
        """Load trade history"""
        if self.trades_file.exists():
            with open(self.trades_file, 'r') as f:
                return json.load(f)
        return []
    
    def save_trades(self):
        """Save trade history"""
        with open(self.trades_file, 'w') as f:
            json.dump(self.trades, f, indent=2)
    
    def add_trade(self, symbol, direction, entry, exit, profit_loss, 
                  target_hit, confidence, date=None):
        """Add a trade to history"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        trade = {
            'date': date,
            'symbol': symbol,
            'direction': direction,
            'entry': entry,
            'exit': exit,
            'profit_loss': profit_loss,
            'profit_pct': (profit_loss / entry) * 100 if direction == 'LONG' else -(profit_loss / entry) * 100,
            'target_hit': target_hit,
            'confidence': confidence,
            'win': profit_loss > 0
        }
        
        self.trades.append(trade)
        self.save_trades()
        
        print(f"✅ Trade logged: {symbol} {direction} P/L: ${profit_loss:+.2f}")
    
    def get_recent_performance(self, last_n=10):
        """Get performance stats for last N trades"""
        if not self.trades:
            return {
                'total_trades': 0,
                'wins': 0,
                'losses': 0,
                'win_rate': 0,
                'avg_profit': 0,
                'avg_loss': 0,
                'profit_factor': 0,
                'consecutive_wins': 0,
                'consecutive_losses': 0
            }
        
        recent = self.trades[-last_n:]
        
        wins = [t for t in recent if t['win']]
        losses = [t for t in recent if not t['win']]
        
        total_profit = sum(t['profit_loss'] for t in wins)
        total_loss = abs(sum(t['profit_loss'] for t in losses))
        
        # Calculate consecutive wins/losses
        consecutive_wins = 0
        consecutive_losses = 0
        for trade in reversed(self.trades):
            if trade['win']:
                consecutive_wins += 1
                if consecutive_losses > 0:
                    break
            else:
                consecutive_losses += 1
                if consecutive_wins > 0:
                    break
        
        return {
            'total_trades': len(recent),
            'wins': len(wins),
            'losses': len(losses),
            'win_rate': (len(wins) / len(recent)) * 100 if recent else 0,
            'avg_profit': total_profit / len(wins) if wins else 0,
            'avg_loss': total_loss / len(losses) if losses else 0,
            'profit_factor': total_profit / total_loss if total_loss > 0 else 0,
            'consecutive_wins': consecutive_wins,
            'consecutive_losses': consecutive_losses,
            'total_pl': sum(t['profit_loss'] for t in recent)
        }
    
    def get_position_size_multiplier(self, base_confidence):
        """
        Calculate position size multiplier based on performance
        Following Paul Tudor Jones: "Reduce size when losing, increase when winning"
        """
        perf = self.get_recent_performance(10)
        
        multiplier = 1.0
        
        # Based on win rate (last 10 trades)
        if perf['total_trades'] >= 5:  # Need at least 5 trades
            win_rate = perf['win_rate']
            
            if win_rate >= 70:
                # Trading well - can increase slightly
                multiplier = 1.2
                reason = "HIGH win rate (70%+)"
            elif win_rate >= 60:
                # Good performance - normal size
                multiplier = 1.0
                reason = "GOOD win rate (60-70%)"
            elif win_rate >= 50:
                # Moderate - slightly reduce
                multiplier = 0.8
                reason = "MODERATE win rate (50-60%)"
            else:
                # Poor performance - significantly reduce
                multiplier = 0.5
                reason = "LOW win rate (<50%)"
        else:
            multiplier = 1.0
            reason = "Not enough trades yet"
        
        # Based on consecutive wins/losses
        if perf['consecutive_wins'] >= 3:
            # Hot streak - bonus multiplier
            multiplier *= 1.1
            reason += " + Hot streak (3+ wins)"
        elif perf['consecutive_losses'] >= 2:
            # Cold streak - reduce more
            multiplier *= 0.7
            reason += " + Cold streak (2+ losses)"
        
        # Based on confidence level
        if base_confidence >= 85:
            # Very high confidence - increase
            multiplier *= 1.1
            reason += " + High confidence (85%+)"
        elif base_confidence < 70:
            # Lower confidence - reduce
            multiplier *= 0.8
            reason += " + Lower confidence (<70%)"
        
        # Cap multiplier between 0.25x and 1.5x
        multiplier = max(0.25, min(1.5, multiplier))
        
        return multiplier, reason
    
    def get_trading_status(self):
        """Get current trading status and recommendations"""
        perf = self.get_recent_performance(10)
        
        if perf['total_trades'] < 5:
            return {
                'status': 'BUILDING_TRACK_RECORD',
                'recommendation': 'Normal position sizes',
                'action': 'Continue trading normally to build history'
            }
        
        win_rate = perf['win_rate']
        
        if win_rate >= 70:
            return {
                'status': 'TRADING_WELL',
                'recommendation': 'Can increase sizes by 20%',
                'action': 'Capitalize on hot streak'
            }
        elif win_rate >= 60:
            return {
                'status': 'NORMAL_PERFORMANCE',
                'recommendation': 'Normal position sizes',
                'action': 'Continue current approach'
            }
        elif win_rate >= 50:
            return {
                'status': 'MODERATE_PERFORMANCE',
                'recommendation': 'Reduce sizes by 20%',
                'action': 'Be more selective with trades'
            }
        else:
            return {
                'status': 'POOR_PERFORMANCE',
                'recommendation': 'Reduce sizes by 50%',
                'action': 'Review system, take break if needed'
            }
    
    def print_performance_report(self):
        """Print detailed performance report"""
        perf = self.get_recent_performance(10)
        status = self.get_trading_status()
        
        print("\n" + "="*80)
        print("📊 PERFORMANCE TRACKER - Last 10 Trades")
        print("="*80)
        
        print(f"\n📈 STATISTICS:")
        print(f"   Total Trades: {perf['total_trades']}")
        print(f"   Wins: {perf['wins']} | Losses: {perf['losses']}")
        print(f"   Win Rate: {perf['win_rate']:.1f}%")
        
        if perf['total_trades'] > 0:
            print(f"   Avg Profit: ${perf['avg_profit']:+.2f}")
            print(f"   Avg Loss: ${perf['avg_loss']:+.2f}")
            print(f"   Profit Factor: {perf['profit_factor']:.2f}")
            print(f"   Total P/L: ${perf['total_pl']:+.2f}")
        
        print(f"\n🔥 CURRENT STREAK:")
        if perf['consecutive_wins'] > 0:
            print(f"   ✅ {perf['consecutive_wins']} consecutive WINS")
        elif perf['consecutive_losses'] > 0:
            print(f"   ❌ {perf['consecutive_losses']} consecutive LOSSES")
        else:
            print(f"   ➡️ No active streak")
        
        print(f"\n🎯 TRADING STATUS:")
        print(f"   Status: {status['status']}")
        print(f"   Recommendation: {status['recommendation']}")
        print(f"   Action: {status['action']}")
        
        # Show last 5 trades
        if self.trades:
            print(f"\n📋 LAST 5 TRADES:")
            for trade in self.trades[-5:]:
                result = "✅ WIN" if trade['win'] else "❌ LOSS"
                print(f"   {trade['date']} | {trade['symbol']} {trade['direction']} | "
                      f"${trade['profit_loss']:+.2f} ({trade['profit_pct']:+.1f}%) | {result}")
        
        print("="*80)

# Example usage
if __name__ == "__main__":
    tracker = PerformanceTracker()
    
    # Example: Add Monday's trades
    tracker.add_trade('AMD', 'LONG', 233.08, 238.60, 5.52, True, 84.3, '2025-10-20')
    tracker.add_trade('AVGO', 'LONG', 349.33, 356.34, 7.01, True, 83.3, '2025-10-20')
    tracker.add_trade('ORCL', 'SHORT', 291.31, 285.27, 6.04, True, 79.7, '2025-10-20')
    
    # Show report
    tracker.print_performance_report()
    
    # Get position size multiplier
    multiplier, reason = tracker.get_position_size_multiplier(85)
    print(f"\n💰 Position Size Multiplier: {multiplier:.2f}x")
    print(f"   Reason: {reason}")
