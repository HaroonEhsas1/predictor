#!/usr/bin/env python3
"""
Engine Logger for Professional Stock Prediction Engine
Integrates with existing logging systems
"""

import os
import sys
import csv
import time
from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Optional
import pandas as pd
import pytz
import warnings
warnings.filterwarnings('ignore')

# Define logging configuration directly (config.py doesn't exist)
LOGGING_CONFIG = {
    'predictions_csv': 'logs/predictions.csv',
    'performance_log': 'logs/performance.log'
}

PATHS = {
    'logs': 'logs'
}

class EngineLogger:
    """
    Professional logging system for the engine
    Extends existing logging capabilities
    """
    
    def __init__(self):
        """Initialize engine logger with daily prediction tracking"""
        self.log_paths = {
            'predictions': LOGGING_CONFIG.get('predictions_csv', 'logs/predictions.csv'),
            'daily_predictions': 'logs/daily_predictions.csv',
            'daily_schedule': 'logs/daily_schedule.json',
            'performance': LOGGING_CONFIG.get('performance_log', 'logs/performance.log'),
            'engine': 'logs/engine.log',
            'training': 'logs/training.log'
        }
        
        # Eastern timezone for market hours
        self.et_tz = pytz.timezone('US/Eastern')
        
        # Ensure log directories exist
        for log_path in self.log_paths.values():
            os.makedirs(os.path.dirname(log_path), exist_ok=True)
        
        # Initialize CSV files with headers if they don't exist
        self._initialize_csv_files()
        
        # Initialize daily tracking
        self._initialize_daily_tracking()
        
        print("✅ EngineLogger initialized with daily prediction tracking")
    
    def log_prediction(self, prediction: Dict[str, Any], symbol: str, prediction_type: str):
        """Log prediction results to CSV"""
        try:
            log_entry = {
                'utc_ts': datetime.utcnow().isoformat(),
                'et_ts': datetime.now().isoformat(),
                'symbol': symbol,
                'horizon': prediction_type,
                'price_pred': prediction.get('target_price', 0.0),
                'direction': prediction.get('direction', 'SIDEWAYS'),
                'confidence': prediction.get('confidence', 0.0),
                'expected_return_pct': prediction.get('expected_return_pct', 0.0),
                'position_size': prediction.get('position_size', 0.0),
                'risk_level': prediction.get('risk_level', 'UNKNOWN'),
                'execution_time_ms': prediction.get('execution_details', {}).get('execution_time_ms', 0.0),
                'data_quality': prediction.get('execution_details', {}).get('data_quality', 'unknown')
            }
            
            self._write_csv_entry(self.log_paths['predictions'], log_entry)
            
        except Exception as e:
            print(f"⚠️  Prediction logging error: {str(e)[:50]}")
    
    def log_training_session(self, training_results: Dict[str, Any], symbol: str):
        """Log model training session results"""
        try:
            timestamp = datetime.now().isoformat()
            
            # Log to training log file
            with open(self.log_paths['training'], 'a', encoding='utf-8') as f:
                f.write(f"\n=== TRAINING SESSION {timestamp} ===\n")
                f.write(f"Symbol: {symbol}\n")
                
                session_info = training_results.get('training_session', {})
                f.write(f"Data Points: {session_info.get('data_points', 0)}\n")
                f.write(f"Models Trained: {session_info.get('total_models', 0)}\n")
                f.write(f"Duration: {session_info.get('training_duration', 0.0):.2f}s\n")
                
                # Intraday results
                intraday_results = training_results.get('intraday_results', {})
                if intraday_results:
                    f.write(f"\nIntraday Models:\n")
                    for model_name, result in intraday_results.items():
                        f.write(f"  {model_name}: Accuracy={result.accuracy:.4f}, MAE={result.mae:.4f}\n")
                
                # Next-day results
                nextday_results = training_results.get('nextday_results', {})
                if nextday_results:
                    f.write(f"\nNext-Day Models:\n")
                    for model_name, result in nextday_results.items():
                        f.write(f"  {model_name}: Accuracy={result.accuracy:.4f}\n")
                
                f.write("=" * 50 + "\n")
            
        except Exception as e:
            print(f"⚠️  Training session logging error: {str(e)[:50]}")
    
    def log_performance_metrics(self, metrics: Dict[str, Any], component: str):
        """Log performance metrics"""
        try:
            timestamp = datetime.now().isoformat()
            
            with open(self.log_paths['performance'], 'a', encoding='utf-8') as f:
                f.write(f"{timestamp} [{component}] ")
                
                metric_strs = []
                for key, value in metrics.items():
                    if isinstance(value, float):
                        metric_strs.append(f"{key}={value:.4f}")
                    else:
                        metric_strs.append(f"{key}={value}")
                
                f.write(" ".join(metric_strs) + "\n")
            
        except Exception as e:
            print(f"⚠️  Performance logging error: {str(e)[:50]}")
    
    def log_engine_event(self, event: str, details: Dict[str, Any] = None):
        """Log general engine events"""
        try:
            timestamp = datetime.now().isoformat()
            
            with open(self.log_paths['engine'], 'a', encoding='utf-8') as f:
                f.write(f"{timestamp} - {event}")
                
                if details:
                    detail_strs = []
                    for key, value in details.items():
                        detail_strs.append(f"{key}={value}")
                    f.write(f" ({', '.join(detail_strs)})")
                
                f.write("\n")
            
        except Exception as e:
            print(f"⚠️  Engine event logging error: {str(e)[:50]}")
    
    def get_recent_predictions(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent prediction logs"""
        try:
            predictions = []
            
            if os.path.exists(self.log_paths['predictions']):
                with open(self.log_paths['predictions'], 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    all_predictions = list(reader)
                    
                    # Return most recent predictions
                    predictions = all_predictions[-limit:] if len(all_predictions) > limit else all_predictions
            
            return predictions
            
        except Exception as e:
            print(f"⚠️  Recent predictions retrieval error: {str(e)[:50]}")
            return []
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary from logs"""
        try:
            summary = {
                'total_predictions': 0,
                'prediction_types': {},
                'avg_confidence': 0.0,
                'avg_execution_time_ms': 0.0,
                'data_quality_distribution': {},
                'recent_activity': []
            }
            
            recent_predictions = self.get_recent_predictions(1000)  # Last 1000 predictions
            
            if recent_predictions:
                summary['total_predictions'] = len(recent_predictions)
                
                # Analyze prediction types
                for pred in recent_predictions:
                    pred_type = pred.get('horizon', 'unknown')
                    summary['prediction_types'][pred_type] = summary['prediction_types'].get(pred_type, 0) + 1
                
                # Average confidence
                confidences = [float(pred.get('confidence', 0)) for pred in recent_predictions if pred.get('confidence')]
                if confidences:
                    summary['avg_confidence'] = sum(confidences) / len(confidences)
                
                # Average execution time
                exec_times = [float(pred.get('execution_time_ms', 0)) for pred in recent_predictions if pred.get('execution_time_ms')]
                if exec_times:
                    summary['avg_execution_time_ms'] = sum(exec_times) / len(exec_times)
                
                # Data quality distribution
                for pred in recent_predictions:
                    quality = pred.get('data_quality', 'unknown')
                    summary['data_quality_distribution'][quality] = summary['data_quality_distribution'].get(quality, 0) + 1
                
                # Recent activity (last 10 predictions)
                summary['recent_activity'] = recent_predictions[-10:]
            
            return summary
            
        except Exception as e:
            print(f"⚠️  Performance summary error: {str(e)[:50]}")
            return {}
    
    def cleanup_old_logs(self, days_to_keep: int = 30):
        """Clean up old log entries to prevent excessive disk usage"""
        try:
            cutoff_timestamp = datetime.now().timestamp() - (days_to_keep * 24 * 3600)
            
            for log_type, log_path in self.log_paths.items():
                if not os.path.exists(log_path):
                    continue
                
                if log_path.endswith('.csv'):
                    self._cleanup_csv_log(log_path, cutoff_timestamp)
                else:
                    self._cleanup_text_log(log_path, cutoff_timestamp)
            
            print(f"✅ Cleaned up logs older than {days_to_keep} days")
            
        except Exception as e:
            print(f"⚠️  Log cleanup error: {str(e)[:50]}")
    
    def _initialize_daily_tracking(self):
        """Initialize daily prediction tracking system"""
        try:
            # Check for missing prediction days and create schedule
            self._ensure_daily_schedule()
            
            # Initialize daily predictions CSV if it doesn't exist
            if not os.path.exists(self.log_paths['daily_predictions']):
                with open(self.log_paths['daily_predictions'], 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        'trading_date', 'prediction_date', 'prediction_time_et', 'prediction_time_utc',
                        'symbol', 'direction', 'confidence', 'target_price', 'current_price',
                        'expected_move_pct', 'risk_level', 'data_quality', 'prediction_id',
                        'market_close_price', 'actual_open_price', 'prediction_accuracy',
                        'backtest_performance', 'model_version', 'features_used'
                    ])
            
            print("✅ Daily prediction tracking initialized")
            
        except Exception as e:
            print(f"⚠️ Daily tracking initialization error: {str(e)[:50]}")
    
    def _ensure_daily_schedule(self):
        """Ensure we have a prediction schedule for all trading days"""
        try:
            import json
            
            # Load existing schedule or create new one
            schedule = {}
            if os.path.exists(self.log_paths['daily_schedule']):
                with open(self.log_paths['daily_schedule'], 'r') as f:
                    schedule = json.load(f)
            
            # Get date range for schedule (30 days back, 30 days forward)
            today = datetime.now(self.et_tz).date()
            start_date = today - timedelta(days=30)
            end_date = today + timedelta(days=30)
            
            # Generate schedule for all trading days
            current_date = start_date
            updated = False
            
            while current_date <= end_date:
                if self._is_trading_day(current_date):
                    date_str = current_date.strftime('%Y-%m-%d')
                    if date_str not in schedule:
                        schedule[date_str] = {
                            'scheduled': True,
                            'prediction_generated': False,
                            'prediction_time': None,
                            'market_close_time': '16:00:00',  # 4:00 PM ET
                            'next_trading_day': self._get_next_trading_day(current_date).strftime('%Y-%m-%d')
                        }
                        updated = True
                
                current_date += timedelta(days=1)
            
            # Save updated schedule
            if updated:
                with open(self.log_paths['daily_schedule'], 'w') as f:
                    json.dump(schedule, f, indent=2)
                print(f"✅ Daily schedule updated with {len(schedule)} trading days")
            
        except Exception as e:
            print(f"⚠️ Schedule creation error: {str(e)[:50]}")
    
    def _is_trading_day(self, check_date: date) -> bool:
        """Check if a given date is a trading day (weekday, not holiday)"""
        # Monday = 0, Sunday = 6
        if check_date.weekday() >= 5:  # Saturday or Sunday
            return False
        
        # TODO: Add holiday checking for more accuracy
        # For now, just check weekdays
        return True
    
    def _get_next_trading_day(self, current_date: date) -> date:
        """Get the next trading day after the given date"""
        next_date = current_date + timedelta(days=1)
        while not self._is_trading_day(next_date):
            next_date += timedelta(days=1)
        return next_date
    
    def _initialize_csv_files(self):
        """Initialize CSV files with proper headers"""
        try:
            # Predictions CSV
            predictions_headers = [
                'utc_ts', 'et_ts', 'symbol', 'horizon', 'price_pred', 'direction',
                'confidence', 'expected_return_pct', 'position_size', 'risk_level',
                'execution_time_ms', 'data_quality'
            ]
            
            if not os.path.exists(self.log_paths['predictions']):
                with open(self.log_paths['predictions'], 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=predictions_headers)
                    writer.writeheader()
            
        except Exception as e:
            print(f"⚠️  CSV initialization error: {str(e)[:50]}")
    
    def _write_csv_entry(self, file_path: str, entry: Dict[str, Any]):
        """Write entry to CSV file"""
        try:
            # Check if file exists to determine if we need headers
            file_exists = os.path.exists(file_path) and os.path.getsize(file_path) > 0
            
            with open(file_path, 'a', newline='', encoding='utf-8') as f:
                if entry:
                    writer = csv.DictWriter(f, fieldnames=entry.keys())
                    if not file_exists:
                        writer.writeheader()
                    writer.writerow(entry)
            
        except Exception as e:
            print(f"⚠️  CSV write error: {str(e)[:50]}")
    
    def _cleanup_csv_log(self, file_path: str, cutoff_timestamp: float):
        """Clean up CSV log file"""
        try:
            if not os.path.exists(file_path):
                return
            
            temp_file = file_path + '.tmp'
            
            with open(file_path, 'r', encoding='utf-8') as infile, \
                 open(temp_file, 'w', newline='', encoding='utf-8') as outfile:
                
                reader = csv.DictReader(infile)
                writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames)
                writer.writeheader()
                
                for row in reader:
                    try:
                        # Parse timestamp
                        ts_str = row.get('utc_ts', row.get('et_ts', ''))
                        if ts_str:
                            ts = datetime.fromisoformat(ts_str.replace('Z', '+00:00')).timestamp()
                            if ts >= cutoff_timestamp:
                                writer.writerow(row)
                    except:
                        # Keep row if timestamp parsing fails
                        writer.writerow(row)
            
            # Replace original file with cleaned version
            os.replace(temp_file, file_path)
            
        except Exception as e:
            print(f"⚠️  CSV cleanup error: {str(e)[:50]}")
            # Clean up temp file if it exists
            if os.path.exists(file_path + '.tmp'):
                os.remove(file_path + '.tmp')
    
    def _cleanup_text_log(self, file_path: str, cutoff_timestamp: float):
        """Clean up text log file"""
        try:
            if not os.path.exists(file_path):
                return
            
            temp_file = file_path + '.tmp'
            
            with open(file_path, 'r', encoding='utf-8') as infile, \
                 open(temp_file, 'w', encoding='utf-8') as outfile:
                
                for line in infile:
                    try:
                        # Extract timestamp from line (assuming ISO format at start)
                        if line.strip():
                            ts_str = line.split(' ')[0]
                            ts = datetime.fromisoformat(ts_str).timestamp()
                            if ts >= cutoff_timestamp:
                                outfile.write(line)
                    except:
                        # Keep line if timestamp parsing fails
                        outfile.write(line)
            
            os.replace(temp_file, file_path)
            
        except Exception as e:
            print(f"⚠️  Text log cleanup error: {str(e)[:50]}")
            if os.path.exists(file_path + '.tmp'):
                os.remove(file_path + '.tmp')
    
    def log_daily_prediction(self, prediction: Dict[str, Any], symbol: str, 
                           prediction_date: date, target_trading_date: date) -> str:
        """Log daily prediction with comprehensive tracking"""
        try:
            # Generate unique prediction ID
            prediction_id = f"{symbol}_{prediction_date.strftime('%Y%m%d')}_{target_trading_date.strftime('%Y%m%d')}"
            
            # Get current times
            current_time_et = datetime.now(self.et_tz)
            current_time_utc = datetime.utcnow()
            
            # Prepare daily prediction entry
            daily_entry = {
                'trading_date': target_trading_date.strftime('%Y-%m-%d'),
                'prediction_date': prediction_date.strftime('%Y-%m-%d'),
                'prediction_time_et': current_time_et.strftime('%Y-%m-%d %H:%M:%S'),
                'prediction_time_utc': current_time_utc.strftime('%Y-%m-%d %H:%M:%S'),
                'symbol': symbol,
                'direction': prediction.get('direction', 'UNKNOWN'),
                'confidence': prediction.get('confidence', 0.0),
                'target_price': prediction.get('target_price', 0.0),
                'current_price': prediction.get('current_price', 0.0),
                'expected_move_pct': prediction.get('expected_move_pct', 0.0),
                'risk_level': prediction.get('risk_level', 'UNKNOWN'),
                'data_quality': prediction.get('data_quality', 'unknown'),
                'prediction_id': prediction_id,
                'market_close_price': prediction.get('market_close_price', 0.0),
                'actual_open_price': '',  # To be filled later
                'prediction_accuracy': '',  # To be calculated later
                'backtest_performance': prediction.get('backtest_performance', ''),
                'model_version': prediction.get('model_version', '1.0'),
                'features_used': str(prediction.get('features_used', []))[:200]  # Truncate if too long
            }
            
            # Write to daily predictions CSV
            self._write_csv_entry(self.log_paths['daily_predictions'], daily_entry)
            
            # Update daily schedule
            self._update_daily_schedule(prediction_date, current_time_et)
            
            # Also log to regular predictions log for backwards compatibility
            self.log_prediction(prediction, symbol, 'next_day')
            
            print(f"✅ Daily prediction logged: {prediction_id}")
            return prediction_id
            
        except Exception as e:
            print(f"⚠️ Daily prediction logging error: {str(e)[:50]}")
            return ""
    
    def save_daily_prediction(self, prediction_data: Dict, symbol: str = "AMD") -> Optional[str]:
        """
        Save a daily prediction at market close with proper scheduling and deduplication
        This is the main method called at 4:00 PM ET market close
        """
        try:
            # Get current ET time and dates
            current_et = datetime.now(self.et_tz)
            prediction_date = current_et.date()
            target_trading_date = self._get_next_trading_day(prediction_date)
            
            # Check if prediction already exists for today (prevent duplicates)
            if self._has_prediction_for_date(prediction_date):
                print(f"✅ Daily prediction already exists for {prediction_date}")
                return None
            
            # Log the daily prediction
            prediction_id = self.log_daily_prediction(prediction_data, symbol, prediction_date, target_trading_date)
            
            if prediction_id:
                print(f"💾 DAILY PREDICTION SAVED: {prediction_id}")
                print(f"📅 Date: {prediction_date}")
                print(f"⏰ Time: {current_et.strftime('%H:%M:%S')} ET")
                print(f"🎯 Direction: {prediction_data.get('direction', 'UNKNOWN')}")
                print(f"📊 Confidence: {prediction_data.get('confidence', 0):.1f}%")
                
            return prediction_id
            
        except Exception as e:
            print(f"❌ Save daily prediction error: {str(e)[:100]}")
            return None
    
    def _has_prediction_for_date(self, check_date: date) -> bool:
        """Check if a daily prediction already exists for the given date"""
        try:
            if not os.path.exists(self.log_paths['daily_predictions']):
                return False
                
            with open(self.log_paths['daily_predictions'], 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get('prediction_date') == check_date.strftime('%Y-%m-%d'):
                        return True
            return False
            
        except Exception as e:
            print(f"⚠️ Check prediction date error: {str(e)[:30]}")
            return False
    
    def backfill_missing_days(self, days_back: int = 7) -> int:
        """Backfill missing prediction days with placeholder entries"""
        try:
            missing_days = self.get_missing_prediction_days(days_back)
            backfilled_count = 0
            
            for missing_date in missing_days:
                # Create placeholder entry for missed day
                placeholder_data = {
                    'direction': 'MISSED',
                    'confidence': 0.0,
                    'target_price': 0.0,
                    'current_price': 0.0,
                    'expected_move_pct': 0.0,
                    'risk_level': 'MISSED',
                    'data_quality': 'missed_day',
                    'market_close_price': 0.0,
                    'model_version': 'backfill',
                    'features_used': ['backfill'],
                    'backtest_performance': 'missed',
                    'consensus_details': {'backfilled': True, 'reason': 'system_gap'}
                }
                
                # Use log_daily_prediction with the missing date
                target_trading_date = self._get_next_trading_day(missing_date)
                prediction_id = self.log_daily_prediction(placeholder_data, "AMD", missing_date, target_trading_date)
                
                if prediction_id:
                    backfilled_count += 1
                    print(f"🔧 Backfilled missing day: {missing_date}")
            
            if backfilled_count > 0:
                print(f"✅ Backfilled {backfilled_count} missing prediction days")
            
            return backfilled_count
            
        except Exception as e:
            print(f"⚠️ Backfill error: {str(e)[:50]}")
            return 0
    
    def _update_daily_schedule(self, prediction_date: date, prediction_time: datetime):
        """Update the daily schedule when a prediction is made"""
        try:
            import json
            
            # Load current schedule
            schedule = {}
            if os.path.exists(self.log_paths['daily_schedule']):
                with open(self.log_paths['daily_schedule'], 'r') as f:
                    schedule = json.load(f)
            
            # Update schedule entry
            date_str = prediction_date.strftime('%Y-%m-%d')
            if date_str in schedule:
                schedule[date_str]['prediction_generated'] = True
                schedule[date_str]['prediction_time'] = prediction_time.strftime('%Y-%m-%d %H:%M:%S')
            
            # Save updated schedule
            with open(self.log_paths['daily_schedule'], 'w') as f:
                json.dump(schedule, f, indent=2)
                
        except Exception as e:
            print(f"⚠️ Schedule update error: {str(e)[:50]}")
    
    def get_missing_prediction_days(self, days_back: int = 30) -> List[date]:
        """Get list of trading days that are missing predictions"""
        try:
            import json
            
            missing_days = []
            
            # Check if schedule exists
            if not os.path.exists(self.log_paths['daily_schedule']):
                print("⚠️ Daily schedule not found - initializing")
                self._ensure_daily_schedule()
            
            # Load schedule
            with open(self.log_paths['daily_schedule'], 'r') as f:
                schedule = json.load(f)
            
            # Check recent trading days
            today = datetime.now(self.et_tz).date()
            start_date = today - timedelta(days=days_back)
            
            current_date = start_date
            while current_date <= today:
                if self._is_trading_day(current_date):
                    date_str = current_date.strftime('%Y-%m-%d')
                    
                    # Check if prediction exists in schedule
                    if date_str in schedule:
                        if not schedule[date_str].get('prediction_generated', False):
                            missing_days.append(current_date)
                    else:
                        # Date not in schedule, add to missing
                        missing_days.append(current_date)
                
                current_date += timedelta(days=1)
            
            return missing_days
            
        except Exception as e:
            print(f"⚠️ Missing days check error: {str(e)[:50]}")
            return []
    
    def should_generate_daily_prediction(self) -> bool:
        """Check if we should generate a daily prediction now based on market hours"""
        try:
            current_time_et = datetime.now(self.et_tz)
            current_hour = current_time_et.hour
            current_minute = current_time_et.minute
            
            # Market closes at 4:00 PM ET (16:00)
            # Generate prediction in the last 30 minutes (3:30 PM - 4:00 PM)
            if current_hour == 15 and current_minute >= 30:  # 3:30 PM - 3:59 PM
                return True
            elif current_hour == 16 and current_minute <= 30:  # 4:00 PM - 4:30 PM (post-close)
                return True
            
            return False
            
        except Exception as e:
            print(f"⚠️ Daily prediction check error: {str(e)[:50]}")
            return False
    
    def get_daily_prediction_summary(self, days_back: int = 30) -> Dict[str, Any]:
        """Get summary of daily predictions for the specified period"""
        try:
            summary = {
                'total_trading_days': 0,
                'predictions_made': 0,
                'missing_predictions': 0,
                'missing_days': [],
                'recent_predictions': [],
                'avg_confidence': 0.0,
                'direction_distribution': {},
                'accuracy_metrics': {}
            }
            
            # Get missing days
            missing_days = self.get_missing_prediction_days(days_back)
            summary['missing_predictions'] = len(missing_days)
            summary['missing_days'] = [d.strftime('%Y-%m-%d') for d in missing_days]
            
            # Count total trading days
            today = datetime.now(self.et_tz).date()
            start_date = today - timedelta(days=days_back)
            total_trading_days = 0
            
            current_date = start_date
            while current_date <= today:
                if self._is_trading_day(current_date):
                    total_trading_days += 1
                current_date += timedelta(days=1)
            
            summary['total_trading_days'] = total_trading_days
            summary['predictions_made'] = total_trading_days - len(missing_days)
            
            # Analyze recent daily predictions if file exists
            if os.path.exists(self.log_paths['daily_predictions']):
                with open(self.log_paths['daily_predictions'], 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    daily_predictions = list(reader)
                    
                    if daily_predictions:
                        # Filter to recent period
                        cutoff_date = (today - timedelta(days=days_back)).strftime('%Y-%m-%d')
                        recent_predictions = [p for p in daily_predictions if p.get('prediction_date', '') >= cutoff_date]
                        
                        summary['recent_predictions'] = recent_predictions[-10:]  # Last 10
                        
                        # Calculate averages
                        if recent_predictions:
                            confidences = [float(p.get('confidence', 0)) for p in recent_predictions if p.get('confidence')]
                            if confidences:
                                summary['avg_confidence'] = sum(confidences) / len(confidences)
                            
                            # Direction distribution
                            for pred in recent_predictions:
                                direction = pred.get('direction', 'UNKNOWN')
                                summary['direction_distribution'][direction] = summary['direction_distribution'].get(direction, 0) + 1
            
            return summary
            
        except Exception as e:
            print(f"⚠️ Daily summary error: {str(e)[:50]}")
            return summary

# Create global instance
engine_logger = EngineLogger()