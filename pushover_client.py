"""
Pushover notification client for sending trading alerts
"""

import requests
from typing import Optional
from datetime import datetime
import config


class PushoverClient:
    """Handle Pushover notifications with priority levels"""

    def __init__(self, user_key: str, api_token: str):
        self.user_key = user_key
        self.api_token = api_token
        self.base_url = "https://api.pushover.net/1/messages.json"
        self.last_notification = {}

    def send_notification(
        self,
        message: str,
        title: str = "Trading Alert",
        priority: int = 0,
        sound: Optional[str] = None,
        url: Optional[str] = None
    ) -> bool:
        """
        Send a Pushover notification

        Args:
            message: The notification message
            title: Notification title
            priority: -2 (silent), -1 (quiet), 0 (normal), 1 (high), 2 (emergency)
            sound: Custom sound (e.g., 'cashregister', 'classical', 'cosmic')
            url: Optional URL to include

        Returns:
            bool: True if successful, False otherwise
        """
        payload = {
            "token": self.api_token,
            "user": self.user_key,
            "message": message,
            "title": title,
            "priority": priority,
            "timestamp": int(datetime.now().timestamp())
        }

        if sound:
            payload["sound"] = sound
        if url:
            payload["url"] = url

        try:
            response = requests.post(self.base_url, data=payload, timeout=10)

            if response.status_code == 200:
                print(f"[PUSHOVER] Sent: {title} - {message}")
                return True
            else:
                print(f"[PUSHOVER ERROR] {response.status_code}: {response.text}")
                return False

        except Exception as e:
            print(f"[PUSHOVER ERROR] Failed to send notification: {e}")
            return False

    def send_bias_alert(self, symbol: str, bias: str, score: int, details: str = ""):
        """Send a bias update alert with appropriate priority"""

        # Determine priority and sound based on bias type
        if "FLIP" in bias.upper():
            priority = 2  # Emergency - requires acknowledgment
            sound = "siren"
            title = f"🚨 {symbol} BIAS FLIP"
        elif "STRONG" in bias.upper():
            priority = 1  # High priority
            sound = "cashregister"
            title = f"⚡ {symbol} STRONG BIAS"
        elif "WEAK" in bias.upper():
            priority = 0  # Normal
            sound = "cosmic"
            title = f"📊 {symbol} Weak Bias"
        else:  # Neutral
            priority = -1  # Quiet
            sound = "none"
            title = f"➖ {symbol} Neutral"

        message = f"{bias} (Score: {score})"
        if details:
            message += f"\n{details}"

        # Prevent duplicate notifications within 2 minutes
        cache_key = f"{symbol}_{bias}"
        now = datetime.now()
        if cache_key in self.last_notification:
            time_diff = (now - self.last_notification[cache_key]).total_seconds()
            if time_diff < 120:  # 2 minutes
                print(f"[SKIP] Duplicate notification for {cache_key}")
                return False

        self.last_notification[cache_key] = now
        return self.send_notification(message, title, priority, sound)

    def send_test_notification(self):
        """Send a test notification to verify setup"""
        return self.send_notification(
            "Bias tracker is online and ready!",
            "Test Alert",
            priority=0,
            sound="cosmic"
        )


if __name__ == "__main__":
    # Test the Pushover client
    client = PushoverClient(
        user_key=config.PUSHOVER_USER_KEY,
        api_token=config.PUSHOVER_API_TOKEN
    )

    print("Testing Pushover notifications...")
    client.send_test_notification()
