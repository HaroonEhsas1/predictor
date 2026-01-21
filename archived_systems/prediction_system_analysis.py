#!/usr/bin/env python3
"""
PREDICTION SYSTEM PERFORMANCE ANALYSIS
Analyze all prediction systems to identify the most accurate one
"""

import time
import yfinance as yf
from datetime import datetime, timezone, timedelta

class PredictionSystemAnalyzer:
    def __init__(self):
        self.systems = {
            "Continuous Gap Predictor": {
                "accuracy": 84.8,
                "model": "Random Forest",
                "update_frequency": "30 seconds",
                "focus": "$2+ gaps",
                "predictions_made": 15,
                "consistency": "High - consistent 84.8%",
                "gap_threshold_met": False,
                "current_gap_prediction": -0.39
            },
            "Stock Predictor": {
                "accuracy": 63.1,
                "model": "Enhanced ML Ensemble", 
                "update_frequency": "10 seconds",
                "focus": "Next-day direction",
                "predictions_made": 19,
                "consistency": "Medium - varies 62-63%",
                "gap_threshold_met": False,
                "current_gap_prediction": 0.53
            },
            "Reliable Predictor": {
                "accuracy": 97.5,
                "model": "LinearRegression",
                "update_frequency": "One-shot",
                "focus": "High confidence signals",
                "predictions_made": 1,
                "consistency": "Extremely High - 97.5%",
                "gap_threshold_met": False,
                "current_gap_prediction": 0.84
            },
            "Comprehensive Data Collector": {
                "accuracy": "Unknown",
                "model": "ML Ensemble + Daily Context",
                "update_frequency": "3 minutes data collection",
                "focus": "Full day analysis → 3:30 PM signal",
                "predictions_made": "Data collection phase",
                "consistency": "Pending - new system",
                "gap_threshold_met": "TBD",
                "current_gap_prediction": "Pending analysis"
            },
            "Immediate Trading Signals": {
                "accuracy": "Unknown",
                "model": "RF + GB + LR trained on daily data",
                "update_frequency": "Signal at 3:30 PM",
                "focus": "$2+ gaps with execution plan", 
                "predictions_made": "Pending first signal",
                "consistency": "Unknown - new system",
                "gap_threshold_met": "TBD",
                "current_gap_prediction": "Pending"
            }
        }
    
    def analyze_performance(self):
        """Analyze which system performs best"""
        print("🔍 PREDICTION SYSTEM PERFORMANCE ANALYSIS")
        print("="*80)
        
        # Current market data for reference
        ticker = yf.Ticker("AMD")
        current_price = ticker.history(period="1d")['Close'][-1]
        
        print(f"📊 Current AMD Price: ${current_price:.2f}")
        print(f"⏰ Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S ET')}")
        print()
        
        rankings = []
        
        for name, data in self.systems.items():
            print(f"🤖 {name}")
            print(f"   Accuracy:          {data['accuracy']}%")
            print(f"   Model:             {data['model']}")
            print(f"   Update Frequency:  {data['update_frequency']}")
            print(f"   Focus:             {data['focus']}")
            print(f"   Predictions Made:  {data['predictions_made']}")
            print(f"   Consistency:       {data['consistency']}")
            print(f"   Gap Prediction:    ${data['current_gap_prediction']}")
            print()
            
            # Calculate ranking score
            if isinstance(data['accuracy'], (int, float)):
                accuracy_score = data['accuracy']
            else:
                accuracy_score = 0  # Unknown systems get 0 for now
                
            consistency_score = 100 if "High" in str(data['consistency']) else 50
            focus_score = 100 if "$2+" in data['focus'] else 75
            
            total_score = (accuracy_score * 0.5) + (consistency_score * 0.3) + (focus_score * 0.2)
            
            rankings.append((name, total_score, data))
        
        # Sort by score
        rankings.sort(key=lambda x: x[1], reverse=True)
        
        print("🏆 SYSTEM RANKINGS (Best to Worst)")
        print("="*80)
        
        for i, (name, score, data) in enumerate(rankings, 1):
            print(f"{i}. {name}")
            print(f"   Overall Score: {score:.1f}/100")
            print(f"   Key Strength: {self.get_key_strength(name, data)}")
            print(f"   Recommendation: {self.get_recommendation(name, data)}")
            print()
        
        # Best system recommendation
        best_system = rankings[0]
        print("🎯 RECOMMENDATION")
        print("="*50)
        print(f"Best System: {best_system[0]}")
        print(f"Score: {best_system[1]:.1f}/100")
        print(f"Why: {self.get_detailed_recommendation(best_system[0], best_system[2])}")
        
        return best_system[0]
    
    def get_key_strength(self, name, data):
        """Get key strength of each system"""
        strengths = {
            "Continuous Gap Predictor": "Highest proven accuracy (84.8%) with consistent performance",
            "Stock Predictor": "Most comprehensive features and frequent updates", 
            "Reliable Predictor": "Exceptional accuracy (97.5%) but limited sample size",
            "Comprehensive Data Collector": "Most comprehensive data sources and contextual analysis",
            "Immediate Trading Signals": "Clear execution timing and practical trading focus"
        }
        return strengths.get(name, "Unknown")
    
    def get_recommendation(self, name, data):
        """Get recommendation for each system"""
        recommendations = {
            "Continuous Gap Predictor": "✅ Use for reliable gap predictions",
            "Stock Predictor": "🔄 Good for continuous monitoring but lower accuracy", 
            "Reliable Predictor": "⚠️ Promising but needs more data points",
            "Comprehensive Data Collector": "🚀 Potential best - needs first results",
            "Immediate Trading Signals": "⏰ Wait for 3:30 PM results to evaluate"
        }
        return recommendations.get(name, "Unknown")
    
    def get_detailed_recommendation(self, name, data):
        """Get detailed recommendation for best system"""
        if name == "Continuous Gap Predictor":
            return "84.8% accuracy with 15 consistent predictions. Proven track record for $2+ gap detection."
        elif name == "Reliable Predictor":
            return "97.5% accuracy is exceptional but only 1 prediction sample. Needs validation."
        elif name == "Comprehensive Data Collector":
            return "Most comprehensive approach - 28 data points, daily context analysis. Wait for first signal."
        else:
            return "System shows promise but needs more evaluation data."

if __name__ == "__main__":
    analyzer = PredictionSystemAnalyzer()
    best_system = analyzer.analyze_performance()
    print(f"\n🎯 FOCUS RECOMMENDATION: Work on enhancing '{best_system}' system")