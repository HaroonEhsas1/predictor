#!/usr/bin/env python3
"""
Daily automated news reaction model retraining.

Runs every night at midnight ET, collects last 90 days of data,
retrains models, and auto-deploys to models/ directory.

Usage:
    python scheduled_retraining.py              # Run once immediately
    python scheduled_retraining.py --daemon     # Run continuously (every night)
"""
import os
import sys
import time
import subprocess
from datetime import datetime, time as dtime
import argparse
from pathlib import Path
import pytz

def retrain_models():
    """Execute model retraining for all stocks"""
    et_tz = pytz.timezone('America/New_York')
    now_et = datetime.now(et_tz)
    
    print(f"\n{'='*80}")
    print(f"🔄 SCHEDULED MODEL RETRAINING")
    print(f"{'='*80}")
    print(f"⏰ Starting at {now_et.strftime('%Y-%m-%d %H:%M:%S ET')}")
    
    try:
        # Run trainer with default settings (90 days, all stocks)
        result = subprocess.run(
            [sys.executable, 'news_reaction_trainer.py', '--days', '90'],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode == 0:
            print(f"\n✅ Retraining completed successfully")
            print(f"Output:\n{result.stdout[-500:]}")  # Last 500 chars
        else:
            print(f"\n❌ Retraining failed with return code {result.returncode}")
            print(f"Error:\n{result.stderr[-500:]}")
        
        # Log completion
        log_path = Path('logs') / 'retraining.log'
        log_path.parent.mkdir(exist_ok=True)
        with open(log_path, 'a') as f:
            f.write(f"\n{now_et.isoformat()} - Retraining {'SUCCESS' if result.returncode == 0 else 'FAILED'}")
        
        return result.returncode == 0
    
    except subprocess.TimeoutExpired:
        print("❌ Retraining timed out (5 min limit)")
        return False
    except Exception as e:
        print(f"❌ Retraining error: {e}")
        return False

def schedule_job():
    """Schedule retraining to run every night at midnight ET"""
    et_tz = pytz.timezone('America/New_York')
    
    def should_run():
        now_et = datetime.now(et_tz)
        # Run between midnight and 1 AM ET
        return 0 <= now_et.hour < 1
    
    while True:
        if should_run():
            retrain_models()
            # Wait until after 1 AM to avoid running again same night
            time.sleep(3600)
        else:
            # Check every 10 min if it's time
            time.sleep(600)

def main():
    parser = argparse.ArgumentParser(description='Automated news model retraining scheduler')
    parser.add_argument('--daemon', action='store_true', help='Run as continuous daemon (nightly)')
    args = parser.parse_args()
    
    if args.daemon:
        print("\n🔄 Starting retraining daemon (runs nightly at midnight ET)")
        print("   Press Ctrl+C to stop")
        try:
            schedule_job()
        except KeyboardInterrupt:
            print("\n✅ Daemon stopped")
    else:
        # Run once
        retrain_models()

if __name__ == '__main__':
    main()
