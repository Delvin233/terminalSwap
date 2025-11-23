"""System notifications for transaction status"""

from plyer import notification


class NotificationManager:
    def __init__(self):
        self.app_name = "terminalSwap"
        self.app_icon = None  # Could add icon path later

    def notify_transaction_success(
        self, tx_type: str, amount: str, token: str, tx_hash: str
    ):
        """Notify successful transaction"""
        title = f"✅ {tx_type} Successful"
        message = f"{amount} {token}\nTx: {tx_hash[:10]}..."
        self._send_notification(title, message)

    def notify_transaction_failed(
        self, tx_type: str, amount: str, token: str, error: str
    ):
        """Notify failed transaction"""
        title = f"❌ {tx_type} Failed"
        message = f"{amount} {token}\nError: {error[:50]}..."
        self._send_notification(title, message)

    def notify_swap_success(
        self,
        from_amount: str,
        from_token: str,
        to_amount: str,
        to_token: str,
        tx_hash: str,
    ):
        """Notify successful swap"""
        title = "✅ Swap Successful"
        message = f"{from_amount} {from_token} → {to_amount} {to_token}\nTx: {tx_hash[:10]}..."
        self._send_notification(title, message)

    def notify_swap_failed(
        self, from_amount: str, from_token: str, to_token: str, error: str
    ):
        """Notify failed swap"""
        title = "❌ Swap Failed"
        message = f"{from_amount} {from_token} → {to_token}\nError: {error[:50]}..."
        self._send_notification(title, message)

    def _send_notification(self, title: str, message: str):
        """Send system notification"""
        try:
            notification.notify(
                title=title,
                message=message,
                app_name=self.app_name,
                app_icon=self.app_icon,
                timeout=5,  # 5 seconds
            )
        except Exception as e:
            # Fallback - just print if notifications fail
            print(f"📱 {title}: {message}")
            print(f"(Notification error: {e})")
