#!/usr/bin/env python3
"""
ACCURACY TRACKER - Validation System
Tracks prediction accuracy to improve signal quality
"""

import json
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, List
import os

class AccuracyTracker:
    def __init__(self, symbol: str = "AMD"):
        self.symbol = symbol
        self.predictions_file = "./data/predictions/scalper/predictions_log.json"
        self.accuracy_file = "./data/predictions/scalper/accuracy_results.json"
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.predictions_file), exist_ok=True)
        
    def log_prediction(self, signal: Dict) -> None:
        """Log a new prediction for later validation"""
        try:
            # Get current price
            current_price = yf.Ticker(self.symbol).history(period="1d", interval="1m")['Close'].iloc[-1]
            
            prediction_record = {
                'timestamp': datetime.now().isoformat(),
                'direction': signal['direction'],
                'confidence': signal['confidence'],
                'entry_price': float(current_price),
                'target_profit': signal.get('target_profit', 0.30),
                'stop_loss': signal.get('stop_loss', 0.20),
                'reason': signal.get('reason', ''),
                'signals': signal.get('signals', {}),
                'validated': False
            }
            
            # Load existing predictions
            predictions = []
            if os.path.exists(self.predictions_file):
                with open(self.predictions_file, 'r') as f:
                    predictions = json.load(f)
            
            predictions.append(prediction_record)
            
            # Keep only last 100 predictions
            if len(predictions) > 100:
                predictions = predictions[-100:]
            
            # Save updated predictions
            with open(self.predictions_file, 'w') as f:
                json.dump(predictions, f, indent=2)
                
        except Exception as e:
            print(f"❌ Error logging prediction: {e}")
    
    def validate_predictions(self) -> Dict:
        """Validate past predictions and calculate accuracy"""
        try:
            if not os.path.exists(self.predictions_file):
                return {'accuracy': 0.0, 'total_predictions': 0}
            
            with open(self.predictions_file, 'r') as f:
                predictions = json.load(f)
            
            # Filter unvalidated predictions older than 10 minutes
            now = datetime.now()
            cutoff_time = now - timedelta(minutes=10)
            
            validation_results = []
            updated_predictions = []
            
            for pred in predictions:
                pred_time = datetime.fromisoformat(pred['timestamp'])
                
                if pred['validated']:
                    updated_predictions.append(pred)
                    continue
                
                if pred_time < cutoff_time and pred['direction'] != 'HOLD':
                    # Validate this prediction
                    result = self._validate_single_prediction(pred, pred_time)
                    pred['validated'] = True
                    pred['validation_result'] = result
                    validation_results.append(result)
                
                updated_predictions.append(pred)
            
            # Save updated predictions
            with open(self.predictions_file, 'w') as f:
                json.dump(updated_predictions, f, indent=2)
            
            # Calculate overall accuracy
            accuracy_stats = self._calculate_accuracy_stats(updated_predictions)
            
            # Save accuracy results
            with open(self.accuracy_file, 'w') as f:
                json.dump(accuracy_stats, f, indent=2)
            
            return accuracy_stats
            
        except Exception as e:
            print(f"❌ Error validating predictions: {e}")
            return {'accuracy': 0.0, 'total_predictions': 0}
    
    def _validate_single_prediction(self, prediction: Dict, pred_time: datetime) -> Dict:
        """Validate a single prediction against actual price movement"""
        try:
            # Get price data for validation period
            end_time = pred_time + timedelta(minutes=10)
            
            # Fetch minute data for the validation period  
            ticker = yf.Ticker(self.symbol)
            data = ticker.history(start=pred_time.date(), end=end_time.date() + timedelta(days=1), interval="1m")
            
            if len(data) < 5:
                return {'success': False, 'reason': 'Insufficient data', 'actual_change': 0.0}
            
            entry_price = prediction['entry_price']
            direction = prediction['direction']
            target_profit = prediction['target_profit']
            stop_loss = prediction['stop_loss']
            
            # Find relevant price range after prediction
            pred_data = data[data.index >= pred_time][:10]  # Next 10 minutes
            
            if len(pred_data) == 0:
                return {'success': False, 'reason': 'No data after prediction', 'actual_change': 0.0}
            
            max_price = float(pred_data['High'].max())
            min_price = float(pred_data['Low'].min())
            final_price = float(pred_data['Close'].iloc[-1])
            
            actual_change = (final_price / entry_price - 1) * 100
            
            # Determine if prediction was correct
            if direction == "UP":
                # Check if target was hit
                target_price = entry_price + target_profit
                stop_price = entry_price - stop_loss
                
                if max_price >= target_price:
                    return {'success': True, 'reason': 'Target hit', 'actual_change': actual_change, 'max_gain': (max_price/entry_price-1)*100}
                elif min_price <= stop_price:
                    return {'success': False, 'reason': 'Stop loss hit', 'actual_change': actual_change, 'max_loss': (min_price/entry_price-1)*100}
                else:
                    # Check directional accuracy
                    success = actual_change > 0.05  # At least 5 cents up
                    return {'success': success, 'reason': 'Direction check', 'actual_change': actual_change}
                    
            elif direction == "DOWN":
                target_price = entry_price - target_profit
                stop_price = entry_price + stop_loss
                
                if min_price <= target_price:
                    return {'success': True, 'reason': 'Target hit', 'actual_change': actual_change, 'max_gain': abs((min_price/entry_price-1)*100)}
                elif max_price >= stop_price:
                    return {'success': False, 'reason': 'Stop loss hit', 'actual_change': actual_change, 'max_loss': (max_price/entry_price-1)*100}
                else:
                    success = actual_change < -0.05  # At least 5 cents down
                    return {'success': success, 'reason': 'Direction check', 'actual_change': actual_change}
            
            return {'success': False, 'reason': 'Unknown direction', 'actual_change': 0.0}
            
        except Exception as e:
            return {'success': False, 'reason': f'Validation error: {e}', 'actual_change': 0.0}
    
    def _calculate_accuracy_stats(self, predictions: List[Dict]) -> Dict:
        """Calculate comprehensive accuracy statistics"""
        validated_predictions = [p for p in predictions if p.get('validated', False)]
        
        if not validated_predictions:
            return {
                'accuracy': 0.0,
                'total_predictions': 0,
                'successful_predictions': 0,
                'by_direction': {'UP': {'total': 0, 'successful': 0, 'accuracy': 0.0},
                               'DOWN': {'total': 0, 'successful': 0, 'accuracy': 0.0}},
                'avg_actual_change': 0.0,
                'last_updated': datetime.now().isoformat()
            }
        
        successful = sum(1 for p in validated_predictions if p.get('validation_result', {}).get('success', False))
        total = len(validated_predictions)
        
        # By direction stats
        by_direction = {}
        for direction in ['UP', 'DOWN']:
            dir_preds = [p for p in validated_predictions if p['direction'] == direction]
            dir_successful = sum(1 for p in dir_preds if p.get('validation_result', {}).get('success', False))
            
            by_direction[direction] = {
                'total': len(dir_preds),
                'successful': dir_successful,
                'accuracy': (dir_successful / len(dir_preds) * 100) if dir_preds else 0.0
            }
        
        # Average actual change
        actual_changes = [p.get('validation_result', {}).get('actual_change', 0.0) for p in validated_predictions]
        avg_actual_change = sum(actual_changes) / len(actual_changes) if actual_changes else 0.0
        
        return {
            'accuracy': (successful / total * 100) if total > 0 else 0.0,
            'total_predictions': total,
            'successful_predictions': successful,
            'by_direction': by_direction,
            'avg_actual_change': avg_actual_change,
            'last_updated': datetime.now().isoformat()
        }
    
    def get_recent_accuracy(self) -> str:
        """Get formatted recent accuracy report"""
        try:
            if os.path.exists(self.accuracy_file):
                with open(self.accuracy_file, 'r') as f:
                    stats = json.load(f)
                    
                if stats['total_predictions'] > 0:
                    return (f"📊 Recent Accuracy: {stats['accuracy']:.1f}% "
                           f"({stats['successful_predictions']}/{stats['total_predictions']}) | "
                           f"UP: {stats['by_direction']['UP']['accuracy']:.1f}% "
                           f"DOWN: {stats['by_direction']['DOWN']['accuracy']:.1f}%")
                           
            return "📊 No accuracy data available yet"
            
        except Exception:
            return "📊 Error reading accuracy data"