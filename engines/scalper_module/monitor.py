#!/usr/bin/env python3
"""
Scalper Module Monitor - Continuous 5-minute microstructure analysis
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scalper_engine import ScalperModule
import time
import json
from datetime import datetime

def main():
    scalper = ScalperModule(symbol="AMD", target_profit=0.30)
    
    print("🔥 SCALPER MODULE - CONTINUOUS MONITOR")
    print("⚡ 5-Minute $0.30 Target System")
    print("📊 Microstructure + Order Flow Analysis")
    print("⚖️ Confidence Threshold: 75.0%")
    print("🚀 Elite 4-Pillar Intelligence Active")
    print("="*80)
    
    while True:
        try:
            print(f"\n🔄 SCALPER ANALYSIS UPDATE - {datetime.now().strftime('%H:%M:%S')} ET")
            print("="*80)
            
            # Run scalper analysis
            signal = scalper.run_scalper_analysis()
            
            # Save prediction
            os.makedirs("../data/predictions/scalper", exist_ok=True)
            with open("../data/predictions/scalper/latest.json", "w") as f:
                json.dump({
                    **signal,
                    'timestamp': datetime.now().isoformat(),
                    'symbol': 'AMD'
                }, f, indent=2)
            
            print(f"⏰ Next update in 2 minutes")
            
            # Wait 2 minutes (faster updates for scalping)
            time.sleep(120)
            
        except KeyboardInterrupt:
            print("\n🛑 Monitor stopped by user")
            break
        except Exception as e:
            print(f"❌ Monitor error: {e}")
            print("⏰ Retrying in 30 seconds...")
            time.sleep(30)

if __name__ == "__main__":
    main()