#!/usr/bin/env python3
"""
Premarket Prediction Simulator
Simulates what the premarket system would predict with different scenarios

Use this to test the system logic without waiting for actual premarket hours
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from premarket_open_predictor import PremarketOpenPredictor

def simulate_premarket_scenario(symbol, scenario_name, yesterday_close, premarket_price, 
                                 premarket_momentum, gap_info=""):
    """
    Simulate a premarket scenario
    
    Args:
        symbol: Stock ticker
        scenario_name: Name of scenario
        yesterday_close: Yesterday's closing price
        premarket_price: Simulated premarket price
        premarket_momentum: Simulated momentum (e.g., +0.5 for bullish, -0.5 for bearish)
        gap_info: Description of gap
    """
    
    print("\n" + "="*80)
    print(f"📊 SIMULATION: {scenario_name}")
    print("="*80)
    print(f"Symbol: {symbol}")
    print(f"Yesterday Close: ${yesterday_close:.2f}")
    print(f"Premarket Price: ${premarket_price:.2f}")
    
    gap_pct = ((premarket_price - yesterday_close) / yesterday_close) * 100
    print(f"Gap: {gap_pct:+.2f}% {gap_info}")
    print(f"Premarket Momentum: {premarket_momentum:+.2f}%")
    print("="*80)
    
    # This is just for demonstration - the actual system would fetch real data
    # You would run the actual predictor at 8:30 AM with real premarket data
    
    # Calculate expected direction based on simulation
    gap_score = 0
    if gap_pct > 5:
        gap_score = -0.70 if gap_pct > 0 else 0.70
    elif gap_pct > 3:
        gap_score = -0.50 if gap_pct > 0 else 0.50
    elif gap_pct > 1.5:
        gap_score = -0.30 if gap_pct > 0 else 0.30
    
    momentum_score = 0
    if premarket_momentum > 0.3:
        momentum_score = 0.50
    elif premarket_momentum > 0.1:
        momentum_score = 0.25
    elif premarket_momentum < -0.3:
        momentum_score = -0.50
    elif premarket_momentum < -0.1:
        momentum_score = -0.25
    
    # Simulate total score (simplified)
    simulated_score = gap_score * 0.10 + momentum_score * 0.15
    
    print(f"\n💡 EXPECTED BEHAVIOR:")
    print(f"   Gap Psychology Score: {gap_score:+.2f}")
    print(f"   Momentum Score: {momentum_score:+.2f}")
    print(f"   Combined Effect: {simulated_score:+.2f}")
    
    if simulated_score > 0.04:
        print(f"   → Likely predicts: UP")
    elif simulated_score < -0.04:
        print(f"   → Likely predicts: DOWN")
    else:
        print(f"   → Likely predicts: NEUTRAL (conflicting signals)")
    
    print(f"\n   This simulation shows how the system WOULD behave")
    print(f"   Run at actual 8:30 AM premarket for real predictions!")
    

if __name__ == "__main__":
    print("\n" + "="*80)
    print("🌅 PREMARKET PREDICTION SIMULATOR")
    print("="*80)
    print("Simulating different premarket scenarios...")
    print("(Run actual predictor at 8:30 AM for real-time predictions)")
    
    # Scenario 1: Large gap UP, strong bullish momentum
    simulate_premarket_scenario(
        symbol="AMD",
        scenario_name="Large Gap UP with Bullish Momentum",
        yesterday_close=233.08,
        premarket_price=241.50,
        premarket_momentum=+0.45,
        gap_info="(LARGE gap - may partially fill)"
    )
    
    # Scenario 2: Large gap DOWN, bearish momentum continues
    simulate_premarket_scenario(
        symbol="ORCL",
        scenario_name="Large Gap DOWN with Bearish Momentum",
        yesterday_close=291.31,
        premarket_price=271.50,
        premarket_momentum=-0.62,
        gap_info="(HUGE gap - likely to partially fill)"
    )
    
    # Scenario 3: Small gap UP but momentum turning bearish
    simulate_premarket_scenario(
        symbol="AVGO",
        scenario_name="Small Gap UP but Momentum Reversing",
        yesterday_close=349.33,
        premarket_price=350.80,
        premarket_momentum=-0.28,
        gap_info="(Small gap but bearish momentum = conflict)"
    )
    
    # Scenario 4: Gap UP matches overnight UP prediction
    simulate_premarket_scenario(
        symbol="AMD",
        scenario_name="Gap UP Confirms Overnight UP Prediction",
        yesterday_close=233.08,
        premarket_price=236.20,
        premarket_momentum=+0.32,
        gap_info="(Moderate gap, bullish momentum = confirmation)"
    )
    
    # Scenario 5: Gap DOWN flips overnight UP prediction
    simulate_premarket_scenario(
        symbol="AMD",
        scenario_name="Gap DOWN FLIPS Overnight UP Prediction",
        yesterday_close=233.08,
        premarket_price=229.50,
        premarket_momentum=-0.55,
        gap_info="(Bearish gap + momentum = FLIP signal!)"
    )
    
    print("\n" + "="*80)
    print("✅ SIMULATION COMPLETE")
    print("="*80)
    print("\n📋 HOW TO USE THE REAL SYSTEM:")
    print("\n1. Wait until 8:30 AM ET (premarket hours)")
    print("2. Run: python premarket_open_predictor.py AMD")
    print("3. System will fetch REAL premarket price and momentum")
    print("4. Get actual prediction for 9:30 AM opening move")
    print("\n⏰ Premarket Hours: 6:00 AM - 9:30 AM ET")
    print("📊 Best Time to Run: 8:30 AM ET (1 hour before open)")
    print("\n" + "="*80)
