"""
Database manager for persistent prediction storage
Fixes the issue where predictions were only stored in memory
"""

import os
import json
import logging
from datetime import datetime, date
from decimal import Decimal
from typing import Dict, List, Optional, Any, Union
import psycopg2
from psycopg2.extras import RealDictCursor, Json
from psycopg2 import sql
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class PredictionDatabase:
    """
    Database manager for persistent prediction storage
    Replaces memory-only storage with proper database persistence
    """
    
    def __init__(self):
        """Initialize database connection"""
        self.connection_string = os.getenv('DATABASE_URL')
        if not self.connection_string:
            raise ValueError("DATABASE_URL environment variable is required")
        
        logger.info("✅ PredictionDatabase initialized with persistent storage")
    
    @contextmanager
    def get_connection(self):
        """Get database connection with proper error handling"""
        conn = None
        try:
            conn = psycopg2.connect(self.connection_string)
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database connection error: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def save_prediction(self, 
                       symbol: str,
                       prediction_type: str,
                       prediction_data: Dict[str, Any],
                       prediction_date: Optional[date] = None) -> int:
        """
        Save prediction to database (replaces memory-only storage)
        
        Args:
            symbol: Stock symbol (e.g., 'AMD')
            prediction_type: Type of prediction ('next_day', 'intraday', '1min', 'scalper', 'elite')
            prediction_data: Full prediction data dictionary
            prediction_date: Trading date for this prediction (defaults to today)
        
        Returns:
            prediction_id: ID of the saved prediction
        """
        
        if prediction_date is None:
            prediction_date = date.today()
        
        # Extract core fields from prediction data
        direction = prediction_data.get('direction', 'UNKNOWN')
        confidence = float(prediction_data.get('confidence', 0.0))
        trade_signal = prediction_data.get('trade_signal', 'NO_TRADE')
        
        # Price fields
        current_price = self._safe_decimal(prediction_data.get('current_price'))
        predicted_price = self._safe_decimal(prediction_data.get('predicted_price') or 
                                           prediction_data.get('most_likely_open') or
                                           prediction_data.get('target_price'))
        target_price_up = self._safe_decimal(prediction_data.get('target_price_up') or
                                           prediction_data.get('range_high'))
        target_price_down = self._safe_decimal(prediction_data.get('target_price_down') or
                                             prediction_data.get('range_low'))
        stop_loss = self._safe_decimal(prediction_data.get('stop_loss'))
        take_profit = self._safe_decimal(prediction_data.get('take_profit'))
        
        # Risk and position fields
        risk_level = prediction_data.get('risk_level', 'UNKNOWN')
        position_size = self._safe_decimal(prediction_data.get('position_size', 0.0))
        expected_move_pct = self._safe_decimal(prediction_data.get('expected_move_pct') or
                                             prediction_data.get('price_change_pct'))
        risk_reward_ratio = self._safe_decimal(prediction_data.get('risk_reward_ratio'))
        
        # Model and data quality
        model_version = prediction_data.get('model_version', 'unknown')
        data_quality = prediction_data.get('data_quality', 'UNKNOWN')
        data_sources_count = int(prediction_data.get('data_sources_count', 0))
        feature_count = int(prediction_data.get('feature_count', 0))
        
        # Status
        is_active = prediction_data.get('is_active', True)
        dry_run = prediction_data.get('dry_run', False)
        
        # Clean prediction data for JSON storage (remove None values)
        clean_prediction_data = self._clean_dict_for_json(prediction_data)
        
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    insert_query = """
                    INSERT INTO predictions (
                        symbol, prediction_type, prediction_date,
                        direction, confidence, trade_signal,
                        current_price, predicted_price, target_price_up, target_price_down,
                        stop_loss, take_profit,
                        risk_level, position_size, expected_move_pct, risk_reward_ratio,
                        model_version, data_quality, data_sources_count, feature_count,
                        is_active, dry_run, prediction_data
                    ) VALUES (
                        %s, %s, %s,
                        %s, %s, %s,
                        %s, %s, %s, %s,
                        %s, %s,
                        %s, %s, %s, %s,
                        %s, %s, %s, %s,
                        %s, %s, %s
                    ) RETURNING id
                    """
                    
                    cur.execute(insert_query, (
                        symbol, prediction_type, prediction_date,
                        direction, confidence, trade_signal,
                        current_price, predicted_price, target_price_up, target_price_down,
                        stop_loss, take_profit,
                        risk_level, position_size, expected_move_pct, risk_reward_ratio,
                        model_version, data_quality, data_sources_count, feature_count,
                        is_active, dry_run, Json(clean_prediction_data)
                    ))
                    
                    result = cur.fetchone()
                    if not result:
                        raise ValueError("Failed to get prediction ID")
                    prediction_id = result[0]
                    conn.commit()
                    
                    logger.info(f"✅ Prediction saved to database: ID={prediction_id}, {symbol} {prediction_type} {direction} {confidence:.1f}%")
                    return prediction_id
                    
        except Exception as e:
            logger.error(f"❌ Failed to save prediction to database: {e}")
            logger.debug(f"Prediction data: {prediction_data}")
            raise
    
    def get_predictions(self, 
                       symbol: Optional[str] = None,
                       prediction_type: Optional[str] = None,
                       days_back: int = 7,
                       limit: int = 100) -> List[Dict[str, Any]]:
        """
        Retrieve predictions from database (replaces memory-only access)
        
        Args:
            symbol: Filter by symbol (optional)
            prediction_type: Filter by prediction type (optional) 
            days_back: Number of days to look back
            limit: Maximum number of predictions to return
        
        Returns:
            List of prediction dictionaries
        """
        
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    query = """
                    SELECT * FROM predictions 
                    WHERE created_at >= NOW() - %s::interval
                    """
                    params = [f'{days_back} days']
                    
                    if symbol:
                        query += " AND symbol = %s"
                        params.append(symbol)
                    
                    if prediction_type:
                        query += " AND prediction_type = %s" 
                        params.append(prediction_type)
                    
                    query += " ORDER BY created_at DESC LIMIT %s"
                    params.append(limit)
                    
                    cur.execute(query, params)
                    predictions = cur.fetchall()
                    
                    # Convert to regular dictionaries and handle JSON
                    result = []
                    for pred in predictions:
                        pred_dict = dict(pred)
                        # Convert datetime objects to strings for JSON serialization
                        for key, value in pred_dict.items():
                            if isinstance(value, datetime):
                                pred_dict[key] = value.isoformat()
                            elif isinstance(value, date):
                                pred_dict[key] = value.isoformat()
                            elif isinstance(value, Decimal):
                                pred_dict[key] = float(value)
                        result.append(pred_dict)
                    
                    logger.info(f"📊 Retrieved {len(result)} predictions from database")
                    return result
                    
        except Exception as e:
            logger.error(f"❌ Failed to retrieve predictions from database: {e}")
            return []
    
    def get_recent_prediction(self, 
                             symbol: str, 
                             prediction_type: str) -> Optional[Dict[str, Any]]:
        """
        Get the most recent prediction for a symbol and type
        (replaces memory-only last prediction storage)
        """
        
        predictions = self.get_predictions(
            symbol=symbol, 
            prediction_type=prediction_type, 
            days_back=1, 
            limit=1
        )
        
        return predictions[0] if predictions else None
    
    def update_prediction_outcome(self,
                                prediction_id: int,
                                actual_price: float,
                                actual_direction: str) -> bool:
        """
        Update prediction with actual outcome for accuracy tracking
        
        Args:
            prediction_id: ID of the prediction to update
            actual_price: Actual price that occurred
            actual_direction: Actual direction that occurred
        
        Returns:
            bool: Success status
        """
        
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    # Get the original prediction using named columns to avoid index issues
                    cur.execute("""
                        SELECT predicted_price, direction, target_price_up, target_price_down 
                        FROM predictions WHERE id = %s
                    """, (prediction_id,))
                    pred_data = cur.fetchone()
                    
                    if not pred_data:
                        logger.error(f"Prediction data not found for ID {prediction_id}")
                        return False
                    
                    predicted_price = float(pred_data[0]) if pred_data[0] else None
                    predicted_direction = pred_data[1]
                    target_up = float(pred_data[2]) if pred_data[2] else None
                    target_down = float(pred_data[3]) if pred_data[3] else None
                    
                    # Calculate accuracy metrics
                    price_difference = (actual_price - predicted_price) if predicted_price is not None else None
                    percentage_error = None
                    if predicted_price and predicted_price != 0 and price_difference is not None:
                        percentage_error = (price_difference / predicted_price * 100)
                    direction_correct = (actual_direction.upper() == predicted_direction.upper())
                    
                    # Check if within target range
                    within_target_range = False
                    if target_up and target_down:
                        within_target_range = target_down <= actual_price <= target_up
                    
                    # Insert outcome record
                    outcome_query = """
                    INSERT INTO prediction_outcomes (
                        prediction_id, actual_price, actual_direction, 
                        price_difference, percentage_error, direction_correct, within_target_range
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """
                    
                    cur.execute(outcome_query, (
                        prediction_id, actual_price, actual_direction,
                        price_difference, percentage_error, direction_correct, within_target_range
                    ))
                    
                    conn.commit()
                    logger.info(f"✅ Prediction outcome updated: ID={prediction_id}, correct={direction_correct}")
                    return True
                    
        except Exception as e:
            logger.error(f"❌ Failed to update prediction outcome: {e}")
            return False
    
    def get_prediction_accuracy(self, 
                              symbol: Optional[str] = None,
                              prediction_type: Optional[str] = None,
                              days_back: int = 30) -> Dict[str, Any]:
        """
        Get prediction accuracy statistics
        (replaces memory-only accuracy tracking)
        """
        
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    query = """
                    SELECT 
                        COUNT(*) as total_predictions,
                        COUNT(po.id) as evaluated_predictions,
                        COUNT(CASE WHEN po.direction_correct = true THEN 1 END) as correct_direction,
                        COUNT(CASE WHEN po.within_target_range = true THEN 1 END) as within_range,
                        ROUND(
                            COUNT(CASE WHEN po.direction_correct = true THEN 1 END)::decimal / 
                            NULLIF(COUNT(po.id), 0) * 100, 2
                        ) as direction_accuracy_pct,
                        ROUND(
                            COUNT(CASE WHEN po.within_target_range = true THEN 1 END)::decimal / 
                            NULLIF(COUNT(po.id), 0) * 100, 2
                        ) as target_accuracy_pct,
                        AVG(p.confidence) as avg_confidence,
                        AVG(ABS(po.percentage_error)) as avg_error_pct
                    FROM predictions p
                    LEFT JOIN prediction_outcomes po ON p.id = po.prediction_id
                    WHERE p.created_at >= NOW() - %s::interval
                    """
                    params = [f'{days_back} days']
                    
                    if symbol:
                        query += " AND p.symbol = %s"
                        params.append(symbol)
                    
                    if prediction_type:
                        query += " AND p.prediction_type = %s"
                        params.append(prediction_type)
                    
                    cur.execute(query, params)
                    result = cur.fetchone()
                    
                    # Convert to regular dictionary and handle None/Decimal values
                    accuracy_stats = dict(result) if result else {}
                    for key, value in accuracy_stats.items():
                        if isinstance(value, Decimal):
                            accuracy_stats[key] = float(value)
                        elif value is None:
                            accuracy_stats[key] = 0.0
                    
                    return accuracy_stats
                    
        except Exception as e:
            logger.error(f"❌ Failed to get prediction accuracy: {e}")
            return {}
    
    def cleanup_old_predictions(self, days_to_keep: int = 90) -> int:
        """
        Clean up old predictions (keeps database manageable)
        
        Args:
            days_to_keep: Number of days of predictions to keep
            
        Returns:
            Number of predictions deleted
        """
        
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    # Delete old outcomes first (due to foreign key)
                    cur.execute("""
                        DELETE FROM prediction_outcomes 
                        WHERE prediction_id IN (
                            SELECT id FROM predictions 
                            WHERE created_at < NOW() - %s::interval
                        )
                    """, (f'{days_to_keep} days',))
                    
                    outcomes_deleted = cur.rowcount
                    
                    # Delete old predictions
                    cur.execute("""
                        DELETE FROM predictions 
                        WHERE created_at < NOW() - %s::interval
                    """, (f'{days_to_keep} days',))
                    
                    predictions_deleted = cur.rowcount
                    conn.commit()
                    
                    logger.info(f"🧹 Cleaned up {predictions_deleted} old predictions and {outcomes_deleted} outcomes")
                    return predictions_deleted
                    
        except Exception as e:
            logger.error(f"❌ Failed to cleanup old predictions: {e}")
            return 0
    
    def _safe_decimal(self, value: Any) -> Optional[float]:
        """Convert value to float safely, return None if not convertible"""
        if value is None:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None
    
    def _clean_dict_for_json(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean dictionary for JSON storage (remove None values, convert types)"""
        clean_data = {}
        for key, value in data.items():
            if value is not None:
                if isinstance(value, (datetime, date)):
                    clean_data[key] = value.isoformat()
                elif isinstance(value, Decimal):
                    clean_data[key] = float(value)
                elif isinstance(value, dict):
                    clean_data[key] = self._clean_dict_for_json(value)
                elif isinstance(value, list):
                    clean_data[key] = [self._clean_dict_for_json(item) if isinstance(item, dict) else item for item in value]
                else:
                    clean_data[key] = value
        return clean_data

# Global instance for easy import
prediction_db = PredictionDatabase()