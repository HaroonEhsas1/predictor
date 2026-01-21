#!/usr/bin/env python3
"""
UNIFIED PREDICTION MANAGER
Prevents engines from disappearing by running them in continuous mode
Coordinates multiple prediction engines and keeps them alive
"""

import sys
import time
import threading
from datetime import datetime, timedelta
import subprocess
import os

class UnifiedPredictionManager:
    """
    Manages multiple prediction engines to prevent them from disappearing
    Ensures all engines stay running continuously like the Stock Predictor
    """
    
    def __init__(self):
        self.engines = {
            'gap_predictor_pro': {
                'script': 'gap_predictor_pro.py',
                'status': 'stopped',
                'process': None,
                'last_run': None,
                'restart_count': 0,
                'run_once': True  # This engine runs once and exits
            },
            'ultra_gap_detector': {
                'script': 'ultra_gap_detector.py',
                'status': 'stopped',
                'process': None,
                'last_run': None,
                'restart_count': 0,
                'run_once': True  # This engine runs once and exits
            },
            'continuous_gap_predictor': {
                'script': 'continuous_gap_predictor.py',
                'status': 'stopped',
                'process': None,
                'last_run': None,
                'restart_count': 0,
                'run_once': False  # This engine runs continuously
            },
            'stock_predictor': {
                'script': 'stock_predictor.py',
                'status': 'running',  # Already running as workflow
                'process': None,
                'last_run': datetime.now(),
                'restart_count': 0,
                'run_once': False  # Already continuous
            }
        }
        
        self.prediction_schedule = {
            # Run one-shot engines every 30 minutes
            'gap_predictor_pro': 1800,  # 30 minutes
            'ultra_gap_detector': 1800,  # 30 minutes
        }
        
        self.running = False
        self.start_time = None
    
    def start_engine(self, engine_name):
        """Start a specific prediction engine"""
        engine = self.engines.get(engine_name)
        if not engine:
            print(f"❌ Unknown engine: {engine_name}")
            return False
        
        script_path = engine['script']
        if not os.path.exists(script_path):
            print(f"❌ Script not found: {script_path}")
            return False
        
        try:
            print(f"🚀 Starting {engine_name}...")
            
            if engine['run_once']:
                # For one-shot engines, run them and capture output
                result = subprocess.run(
                    [sys.executable, script_path],
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout
                )
                
                if result.returncode == 0:
                    print(f"✅ {engine_name} completed successfully")
                    print("📊 Output:")
                    print(result.stdout)
                    engine['status'] = 'completed'
                    engine['last_run'] = datetime.now()
                    return True
                else:
                    print(f"❌ {engine_name} failed:")
                    print(result.stderr)
                    engine['status'] = 'failed'
                    return False
            else:
                # For continuous engines, start as subprocess
                process = subprocess.Popen(
                    [sys.executable, script_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                engine['process'] = process
                engine['status'] = 'running'
                engine['last_run'] = datetime.now()
                
                print(f"✅ {engine_name} started (PID: {process.pid})")
                return True
                
        except subprocess.TimeoutExpired:
            print(f"⏰ {engine_name} timeout - may be running too long")
            engine['status'] = 'timeout'
            return False
        except Exception as e:
            print(f"❌ Error starting {engine_name}: {e}")
            engine['status'] = 'error'
            return False
    
    def stop_engine(self, engine_name):
        """Stop a specific prediction engine"""
        engine = self.engines.get(engine_name)
        if not engine:
            return False
        
        if engine['process']:
            try:
                engine['process'].terminate()
                engine['process'].wait(timeout=10)
                print(f"⏹️ {engine_name} stopped")
            except:
                engine['process'].kill()
                print(f"🔪 {engine_name} force stopped")
            
            engine['process'] = None
        
        engine['status'] = 'stopped'
        return True
    
    def check_engine_status(self, engine_name):
        """Check if an engine is running properly"""
        engine = self.engines.get(engine_name)
        if not engine:
            return False
        
        if engine['run_once']:
            # For one-shot engines, check if they need to run again
            if engine['last_run'] is None:
                return False  # Never run
            
            time_since_run = (datetime.now() - engine['last_run']).total_seconds()
            schedule_interval = self.prediction_schedule.get(engine_name, 3600)
            
            return time_since_run < schedule_interval
        else:
            # For continuous engines, check if process is alive
            if engine['process'] is None:
                return False
            
            return engine['process'].poll() is None
    
    def restart_engine(self, engine_name):
        """Restart a prediction engine"""
        print(f"🔄 Restarting {engine_name}...")
        self.stop_engine(engine_name)
        time.sleep(2)
        
        engine = self.engines[engine_name]
        engine['restart_count'] += 1
        
        if engine['restart_count'] > 5:
            print(f"❌ {engine_name} failed too many times. Disabling.")
            engine['status'] = 'disabled'
            return False
        
        return self.start_engine(engine_name)
    
    def run_scheduled_engines(self):
        """Run one-shot engines on their schedule"""
        current_time = datetime.now()
        
        for engine_name, interval in self.prediction_schedule.items():
            engine = self.engines[engine_name]
            
            if engine['status'] == 'disabled':
                continue
            
            # Check if engine needs to run
            needs_run = False
            if engine['last_run'] is None:
                needs_run = True
            else:
                time_since_run = (current_time - engine['last_run']).total_seconds()
                needs_run = time_since_run >= interval
            
            if needs_run:
                print(f"⏰ Scheduled run for {engine_name}")
                self.start_engine(engine_name)
    
    def monitor_engines(self):
        """Monitor all engines and restart if needed"""
        while self.running:
            try:
                print(f"\n🔍 Engine Status Check - {datetime.now().strftime('%H:%M:%S')}")
                
                # Check scheduled engines
                self.run_scheduled_engines()
                
                # Check continuous engines
                for engine_name, engine in self.engines.items():
                    if engine['run_once']:
                        continue  # Skip one-shot engines
                    
                    if engine_name == 'stock_predictor':
                        continue  # Skip - managed by workflows
                    
                    if not self.check_engine_status(engine_name):
                        print(f"⚠️ {engine_name} not running - restarting...")
                        self.restart_engine(engine_name)
                
                # Display status summary
                self.display_status_summary()
                
                # Wait 60 seconds before next check
                time.sleep(60)
                
            except Exception as e:
                print(f"❌ Monitor error: {e}")
                time.sleep(10)
    
    def display_status_summary(self):
        """Display a summary of all engine statuses"""
        print("📊 ENGINE STATUS SUMMARY:")
        for engine_name, engine in self.engines.items():
            status = engine['status']
            last_run = engine['last_run'].strftime('%H:%M:%S') if engine['last_run'] else 'Never'
            restart_count = engine['restart_count']
            
            status_emoji = {
                'running': '🟢',
                'stopped': '🔴',
                'completed': '✅',
                'failed': '❌',
                'error': '💥',
                'timeout': '⏰',
                'disabled': '🚫'
            }.get(status, '⚪')
            
            print(f"   {status_emoji} {engine_name}: {status} | Last: {last_run} | Restarts: {restart_count}")
    
    def start_manager(self):
        """Start the unified prediction manager"""
        print("🚀 Starting Unified Prediction Manager...")
        print("🎯 Purpose: Keep all prediction engines running continuously")
        print("📋 Managing engines:")
        
        for engine_name, engine in self.engines.items():
            run_type = "One-shot (scheduled)" if engine['run_once'] else "Continuous"
            print(f"   • {engine_name}: {run_type}")
        
        self.running = True
        self.start_time = datetime.now()
        
        # Start continuous engines immediately
        for engine_name, engine in self.engines.items():
            if not engine['run_once'] and engine_name != 'stock_predictor':
                self.start_engine(engine_name)
        
        # Start monitoring thread
        monitor_thread = threading.Thread(target=self.monitor_engines, daemon=True)
        monitor_thread.start()
        
        print("✅ Unified Prediction Manager started successfully!")
        print("💡 All engines will now stay running and be automatically restarted")
        print("🔄 One-shot engines will run every 30 minutes")
        print("⚡ Continuous engines will run without interruption")
        print("📊 Press Ctrl+C to stop all engines\n")
        
        try:
            # Main thread just displays periodic status
            while self.running:
                time.sleep(300)  # 5 minutes
                uptime = (datetime.now() - self.start_time).total_seconds() / 3600
                print(f"\n⏰ Manager Uptime: {uptime:.1f} hours")
                self.display_status_summary()
                
        except KeyboardInterrupt:
            print("\n\n⏹️ Shutting down Unified Prediction Manager...")
            self.stop_all_engines()
    
    def stop_all_engines(self):
        """Stop all prediction engines"""
        self.running = False
        print("🔄 Stopping all engines...")
        
        for engine_name in self.engines.keys():
            if engine_name != 'stock_predictor':  # Don't stop workflow-managed engines
                self.stop_engine(engine_name)
        
        print("✅ All engines stopped successfully")
        
        # Display final statistics
        uptime = (datetime.now() - self.start_time).total_seconds() / 3600 if self.start_time else 0
        print(f"\n📊 Final Statistics:")
        print(f"   Total Uptime: {uptime:.1f} hours")
        print(f"   Engines Managed: {len(self.engines)}")
        
        for engine_name, engine in self.engines.items():
            print(f"   {engine_name}: {engine['restart_count']} restarts")

def main():
    """Main function to run unified prediction manager"""
    print("="*70)
    print("🔧 UNIFIED PREDICTION MANAGER")
    print("🎯 Solving the 'engines disappearing' problem")
    print("⚡ Keeping all prediction engines alive and running")
    print("="*70)
    
    manager = UnifiedPredictionManager()
    manager.start_manager()

if __name__ == "__main__":
    main()