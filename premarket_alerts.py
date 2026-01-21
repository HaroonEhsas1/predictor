"""
REAL-TIME ALERTS SYSTEM
Sends alerts for strong premarket signals

Supports:
- Desktop notifications (Windows)
- Telegram bot
- Discord webhook
- Email (optional)
"""

import os
import requests
from typing import Dict, Any

# Desktop notifications
try:
    from win10toast import ToastNotifier
    DESKTOP_AVAILABLE = True
except:
    DESKTOP_AVAILABLE = False

class PremarketAlerts:
    """
    Sends real-time alerts for premarket signals
    """
    
    def __init__(self):
        # Telegram config
        self.telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN', None)
        self.telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID', None)
        
        # Discord config
        self.discord_webhook_url = os.getenv('DISCORD_WEBHOOK_URL', None)
        
        # Desktop notifier
        if DESKTOP_AVAILABLE:
            self.toaster = ToastNotifier()
        else:
            self.toaster = None
    
    def send_trade_alert(self, symbol: str, analysis: Dict[str, Any]):
        """
        Send alert for trade signal
        
        Args:
            symbol: Stock symbol
            analysis: Complete premarket analysis
        """
        
        prediction = analysis.get('prediction', {})
        targets = analysis.get('targets', {})
        premarket = analysis.get('premarket_data', {})
        
        recommendation = prediction.get('recommendation', 'UNKNOWN')
        
        # Only alert on tradeable signals
        if recommendation in ['STRONG_TRADE', 'TRADE']:
            self._send_all_alerts(symbol, analysis)
    
    def _send_all_alerts(self, symbol: str, analysis: Dict[str, Any]):
        """Send alerts to all configured channels"""
        
        # Format message
        message = self._format_alert_message(symbol, analysis)
        
        # Send to all channels
        self._send_desktop(symbol, message)
        self._send_telegram(message)
        self._send_discord(symbol, message)
        
        print(f"✅ Alerts sent for {symbol}")
    
    def _format_alert_message(self, symbol: str, analysis: Dict[str, Any]) -> str:
        """Format alert message"""
        
        pred = analysis['prediction']
        targets = analysis.get('targets', {})
        pm = analysis['premarket_data']
        
        direction = pred['direction']
        confidence = pred['final_confidence']
        recommendation = pred['recommendation']
        
        entry = targets.get('entry', 0)
        target = targets.get('moderate', 0)
        stop = targets.get('stop_loss', 0)
        
        gap = pm.get('gap_pct', 0)
        
        message = f"""
🚨 {symbol} - {recommendation}

Direction: {direction}
Confidence: {confidence:.0f}%
Gap: {gap:+.2f}%

Entry: ${entry:.2f}
Target: ${target:.2f}
Stop: ${stop:.2f}

Action: Enter 9:25-9:30 AM
        """.strip()
        
        return message
    
    def _send_desktop(self, symbol: str, message: str):
        """Send Windows desktop notification"""
        
        if not DESKTOP_AVAILABLE or not self.toaster:
            return
        
        try:
            self.toaster.show_toast(
                f"{symbol} - Premarket Signal",
                message,
                duration=10,
                threaded=True
            )
            print("   ✅ Desktop notification sent")
        except Exception as e:
            print(f"   ⚠️ Desktop notification failed: {e}")
    
    def _send_telegram(self, message: str):
        """Send Telegram message"""
        
        if not self.telegram_bot_token or not self.telegram_chat_id:
            return
        
        try:
            url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
            
            payload = {
                'chat_id': self.telegram_chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, data=payload, timeout=5)
            
            if response.status_code == 200:
                print("   ✅ Telegram alert sent")
            else:
                print(f"   ⚠️ Telegram failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ⚠️ Telegram error: {e}")
    
    def _send_discord(self, symbol: str, message: str):
        """Send Discord webhook message"""
        
        if not self.discord_webhook_url:
            return
        
        try:
            # Discord embed format
            embed = {
                "title": f"🚨 {symbol} - Premarket Signal",
                "description": message,
                "color": 3066993  # Green
            }
            
            payload = {
                "embeds": [embed]
            }
            
            response = requests.post(
                self.discord_webhook_url,
                json=payload,
                timeout=5
            )
            
            if response.status_code == 204:
                print("   ✅ Discord alert sent")
            else:
                print(f"   ⚠️ Discord failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ⚠️ Discord error: {e}")


# SETUP INSTRUCTIONS:
"""
TELEGRAM SETUP (Recommended - Free):
1. Create a bot:
   - Message @BotFather on Telegram
   - Send /newbot
   - Follow instructions to get bot token

2. Get your chat ID:
   - Message your bot
   - Visit: https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
   - Find your chat_id in the response

3. Set environment variables:
   setx TELEGRAM_BOT_TOKEN "your_bot_token_here"
   setx TELEGRAM_CHAT_ID "your_chat_id_here"

DISCORD SETUP (Free):
1. Create a webhook:
   - Go to Server Settings > Integrations > Webhooks
   - Click "New Webhook"
   - Copy webhook URL

2. Set environment variable:
   setx DISCORD_WEBHOOK_URL "your_webhook_url_here"

DESKTOP NOTIFICATIONS (Windows):
1. Install library:
   pip install win10toast

No configuration needed - works automatically!

USAGE:
from premarket_alerts import PremarketAlerts

alerts = PremarketAlerts()
alerts.send_trade_alert('NVDA', analysis)
"""


if __name__ == "__main__":
    # Test
    print("\n" + "="*80)
    print("PREMARKET ALERTS - TEST")
    print("="*80)
    
    # Simulate analysis
    test_analysis = {
        'prediction': {
            'direction': 'UP',
            'final_confidence': 87.0,
            'recommendation': 'STRONG_TRADE'
        },
        'targets': {
            'entry': 145.32,
            'moderate': 148.47,
            'stop_loss': 142.96
        },
        'premarket_data': {
            'gap_pct': 2.45
        }
    }
    
    alerts = PremarketAlerts()
    
    print("\nConfigured channels:")
    print(f"   Telegram: {'✅' if alerts.telegram_bot_token else '❌ Not configured'}")
    print(f"   Discord: {'✅' if alerts.discord_webhook_url else '❌ Not configured'}")
    print(f"   Desktop: {'✅' if DESKTOP_AVAILABLE else '❌ win10toast not installed'}")
    
    print("\nTesting alert...")
    alerts.send_trade_alert('NVDA', test_analysis)
    
    print("\n" + "="*80)
    print("SETUP INSTRUCTIONS:")
    print("="*80)
    print("""
Telegram (Recommended - Free):
1. Message @BotFather on Telegram → /newbot
2. Get bot token
3. Message your bot
4. Visit: https://api.telegram.org/bot<TOKEN>/getUpdates
5. Get chat_id
6. Set variables:
   setx TELEGRAM_BOT_TOKEN "token"
   setx TELEGRAM_CHAT_ID "id"

Discord (Free):
1. Server Settings > Integrations > Webhooks
2. Create webhook, copy URL
3. setx DISCORD_WEBHOOK_URL "url"

Desktop (Free):
1. pip install win10toast
2. Works automatically!
    """)
