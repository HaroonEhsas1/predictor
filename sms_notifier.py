#!/usr/bin/env python3
"""
SMS Notification Module for Ultra Accurate Gap Predictor
Integrates with Twilio to send alerts for high-confidence predictions and significant market events
"""

import os
import json
import logging
from datetime import datetime, date, timedelta
from typing import Optional, Dict, Any
from twilio.rest import Client

# Create logger without setting basicConfig
logger = logging.getLogger(__name__)

class SMSNotifier:
    """
    Professional SMS notification system for stock prediction alerts
    Uses Twilio integration for reliable message delivery
    """
    
    def __init__(self):
        """Initialize SMS notifier with Twilio credentials from environment"""
        self.account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
        self.auth_token = os.environ.get("TWILIO_AUTH_TOKEN") 
        self.from_phone = os.environ.get("TWILIO_PHONE_NUMBER")
        
        # Validate credentials
        if not all([self.account_sid, self.auth_token, self.from_phone]):
            raise ValueError("Missing required Twilio credentials. Please check environment variables.")
            
        # Initialize Twilio client
        try:
            self.client = Client(self.account_sid, self.auth_token)
            self.enabled = True
            logger.info("✅ SMS Notifier initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Twilio client: {e}")
            self.enabled = False
            
        # Message rate limiting and persistence (avoid spam)
        self.last_alert_time = {}
        self.min_alert_interval = 300  # 5 minutes between similar alerts
        self.sent_predictions_file = 'sent_predictions.json'
        self.daily_sent_count = 0
        self.max_daily_alerts = 10  # Maximum alerts per day
        self.sent_predictions = self._load_sent_predictions()
        
    def send_message(self, to_phone: str, message: str, alert_type: str = "general") -> bool:
        """
        Send SMS message with rate limiting and error handling
        
        Args:
            to_phone: Destination phone number (include country code)
            message: Message content
            alert_type: Type of alert for rate limiting
            
        Returns:
            bool: True if message sent successfully, False otherwise
        """
        if not self.enabled:
            logger.warning("SMS notifier disabled - message not sent")
            return False
            
        # Rate limiting check
        current_time = datetime.now().timestamp()
        last_alert = self.last_alert_time.get(alert_type, 0)
        
        if current_time - last_alert < self.min_alert_interval:
            logger.info(f"Rate limit: Skipping {alert_type} alert (sent recently)")
            return False
            
        try:
            # Send the SMS message
            message_obj = self.client.messages.create(
                body=message,
                from_=self.from_phone,
                to=to_phone
            )
            
            # Update rate limiting tracker
            self.last_alert_time[alert_type] = current_time
            
            logger.info(f"✅ SMS sent successfully - SID: {message_obj.sid}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send SMS: {e}")
            return False
    
    def _load_sent_predictions(self) -> Dict:
        """Load sent predictions from persistent storage"""
        try:
            with open(self.sent_predictions_file, 'r') as f:
                data = json.load(f)
                # Clean old entries (older than 7 days)
                cutoff_date = (datetime.now().date() - timedelta(days=7)).isoformat()
                cleaned_data = {k: v for k, v in data.items() if k >= cutoff_date}
                if len(cleaned_data) != len(data):
                    self._save_sent_predictions(cleaned_data)
                return cleaned_data
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_sent_predictions(self, data: Dict) -> None:
        """Save sent predictions to persistent storage"""
        try:
            with open(self.sent_predictions_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save sent predictions: {e}")
    
    def _generate_prediction_id(self, prediction_data: Dict[str, Any]) -> str:
        """Generate stable prediction ID for deduplication"""
        symbol = prediction_data.get('symbol', 'AMD')
        direction = prediction_data.get('direction', 'UNKNOWN')
        confidence = prediction_data.get('confidence', 0)
        target = prediction_data.get('target_price') or prediction_data.get('expected_move', 0)
        today = date.today().isoformat()
        
        # Create stable hash from key prediction components
        prediction_str = f"{today}_{symbol}_{direction}_{confidence:.1f}_{target:.2f}"
        return prediction_str
    
    def _is_prediction_already_sent(self, prediction_data: Dict[str, Any]) -> bool:
        """Check if this exact prediction was already sent today"""
        prediction_id = self._generate_prediction_id(prediction_data)
        today = date.today().isoformat()
        
        today_sent = self.sent_predictions.get(today, [])
        return prediction_id in today_sent
    
    def _mark_prediction_sent(self, prediction_data: Dict[str, Any]) -> None:
        """Mark this prediction as sent to prevent duplicates"""
        prediction_id = self._generate_prediction_id(prediction_data)
        today = date.today().isoformat()
        
        if today not in self.sent_predictions:
            self.sent_predictions[today] = []
        
        if prediction_id not in self.sent_predictions[today]:
            self.sent_predictions[today].append(prediction_id)
            self._save_sent_predictions(self.sent_predictions)
    
    def _normalize_prediction_data(self, prediction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize prediction data to consistent format"""
        # Handle different key names from various prediction sources
        direction = (prediction_data.get('direction') or 
                    prediction_data.get('directional_bias', 'UNKNOWN'))
        
        # Normalize confidence to 0-100 scale
        confidence = (prediction_data.get('confidence') or 
                     prediction_data.get('confidence_score', 0))
        if confidence <= 1.0:
            confidence = confidence * 100
        
        # Normalize expected move to dollars
        expected_move = prediction_data.get('expected_move', 0)
        if expected_move == 0:
            # Try to calculate from price targets
            current_price = prediction_data.get('current_price', 0)
            target_price = (prediction_data.get('target_price') or 
                           prediction_data.get('price_target', 0))
            if current_price and target_price:
                expected_move = abs(target_price - current_price)
            else:
                # Fallback to percentage move (but convert to approximate dollars)
                expected_move_pct = prediction_data.get('expected_move_pct', 0)
                if expected_move_pct and current_price:
                    expected_move = (expected_move_pct / 100) * current_price
        
        return {
            'symbol': prediction_data.get('symbol', 'AMD'),
            'direction': direction,
            'confidence': confidence,
            'expected_move': expected_move,
            'current_price': prediction_data.get('current_price', 0),
            'target_price': (prediction_data.get('target_price') or 
                           prediction_data.get('price_target', 0))
        }
    
    def send_prediction_alert(self, to_phone: str, prediction_data: Dict[str, Any]) -> bool:
        """
        Send formatted prediction alert with key market data
        
        Args:
            to_phone: Destination phone number
            prediction_data: Dictionary containing prediction details
            
        Returns:
            bool: Success status
        """
        try:
            # Normalize prediction data first
            normalized_data = self._normalize_prediction_data(prediction_data)
            
            # Check if this prediction was already sent
            if self._is_prediction_already_sent(normalized_data):
                logger.info("Prediction already sent today - skipping duplicate")
                return True
            
            # Check daily limit
            today = date.today().isoformat()
            today_count = len(self.sent_predictions.get(today, []))
            if today_count >= self.max_daily_alerts:
                logger.warning(f"Daily SMS limit reached ({self.max_daily_alerts}) - skipping alert")
                return False
            
            symbol = normalized_data['symbol']
            direction = normalized_data['direction']
            confidence = normalized_data['confidence']
            expected_move = normalized_data['expected_move']
            current_price = normalized_data['current_price']
            
            # Create formatted alert message
            message = f"""🚨 {symbol} PREDICTION ALERT
            
Direction: {direction}
Confidence: {confidence:.1f}%
Expected Move: ${expected_move:.2f}
Current Price: ${current_price:.2f}

Time: {datetime.now().strftime('%H:%M ET')}

⚡ Ultra Accurate Gap Predictor"""

            success = self.send_message(to_phone, message, f"prediction_{symbol}")
            
            # Mark as sent if successful
            if success:
                self._mark_prediction_sent(normalized_data)
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to format prediction alert: {e}")
            return False
    
    def send_high_confidence_alert(self, to_phone: str, symbol: str, direction: str, 
                                 confidence: float, expected_move: float) -> bool:
        """
        Send high-confidence prediction alert (80%+ confidence)
        
        Args:
            to_phone: Destination phone number
            symbol: Stock symbol
            direction: Predicted direction (UP/DOWN)
            confidence: Confidence percentage
            expected_move: Expected price movement in dollars
            
        Returns:
            bool: Success status
        """
        confidence_pct = confidence * 100 if confidence <= 1 else confidence
        
        message = f"""🔥 HIGH CONFIDENCE ALERT
        
{symbol}: {direction} {confidence_pct:.1f}%
Expected: ${expected_move:.2f} move
        
This is a HIGH CONFIDENCE signal from the Ultra Accurate Gap Predictor system.

Time: {datetime.now().strftime('%H:%M ET')}"""

        return self.send_message(to_phone, message, f"high_conf_{symbol}")
    
    def send_market_close_summary(self, to_phone: str, summary_data: Dict[str, Any]) -> bool:
        """
        Send market close summary with next-day predictions
        
        Args:
            to_phone: Destination phone number  
            summary_data: Dictionary with market summary data
            
        Returns:
            bool: Success status
        """
        try:
            symbol = summary_data.get('symbol', 'AMD')
            close_price = summary_data.get('close_price', 0)
            daily_change = summary_data.get('daily_change', 0)
            next_day_direction = summary_data.get('next_day_direction', 'UNKNOWN')
            next_day_confidence = summary_data.get('next_day_confidence', 0)
            
            change_sign = "+" if daily_change >= 0 else ""
            confidence_pct = next_day_confidence * 100 if next_day_confidence <= 1 else next_day_confidence
            
            message = f"""📊 MARKET CLOSE SUMMARY
            
{symbol}: ${close_price:.2f} ({change_sign}{daily_change:.2f})

NEXT DAY PREDICTION:
Direction: {next_day_direction}
Confidence: {confidence_pct:.1f}%

Analysis completed at market close.

⚡ Ultra Accurate Gap Predictor"""

            return self.send_message(to_phone, message, f"daily_summary_{symbol}")
            
        except Exception as e:
            logger.error(f"Failed to format market close summary: {e}")
            return False
            
    def test_connection(self, to_phone: str) -> bool:
        """
        Test SMS functionality with a simple test message
        
        Args:
            to_phone: Phone number to test
            
        Returns:
            bool: True if test successful
        """
        test_message = f"""✅ SMS Test Message

Ultra Accurate Gap Predictor SMS system is working correctly.

Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S ET')}

This is a test - no action required."""

        return self.send_message(to_phone, test_message, "test")


# Create global SMS notifier instance
try:
    sms_notifier = SMSNotifier()
    SMS_AVAILABLE = True
except Exception as e:
    logger.error(f"Failed to initialize SMS notifier: {e}")
    sms_notifier = None
    SMS_AVAILABLE = False


def send_prediction_sms(to_phone: str, prediction_data: Dict[str, Any]) -> bool:
    """
    Convenience function to send prediction alerts
    
    Args:
        to_phone: Destination phone number
        prediction_data: Prediction details
        
    Returns:
        bool: Success status
    """
    if not SMS_AVAILABLE or not sms_notifier:
        logger.warning("SMS not available - alert not sent")
        return False
        
    return sms_notifier.send_prediction_alert(to_phone, prediction_data)


def send_high_confidence_sms(to_phone: str, symbol: str, direction: str, 
                           confidence: float, expected_move: float) -> bool:
    """
    Convenience function to send high-confidence alerts
    
    Args:
        to_phone: Destination phone number
        symbol: Stock symbol
        direction: Predicted direction
        confidence: Confidence level
        expected_move: Expected move in dollars
        
    Returns:
        bool: Success status
    """
    if not SMS_AVAILABLE or not sms_notifier:
        logger.warning("SMS not available - alert not sent") 
        return False
        
    return sms_notifier.send_high_confidence_alert(to_phone, symbol, direction, confidence, expected_move)


def test_sms(to_phone: str) -> bool:
    """
    Test SMS functionality
    
    Args:
        to_phone: Phone number to test
        
    Returns:
        bool: Success status
    """
    if not SMS_AVAILABLE or not sms_notifier:
        logger.warning("SMS not available - test failed")
        return False
        
    return sms_notifier.test_connection(to_phone)


if __name__ == "__main__":
    # Quick test when run directly
    print("SMS Notifier Module")
    print(f"Status: {'✅ Available' if SMS_AVAILABLE else '❌ Not Available'}")
    
    if SMS_AVAILABLE:
        print("\nTo test SMS functionality, call:")
        print("python sms_notifier.py test +1234567890")
    else:
        print("Check Twilio credentials in environment variables")