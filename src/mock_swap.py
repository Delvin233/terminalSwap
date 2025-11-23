"""
Mock swap functionality for testing - simulates swaps without using DEX
This is useful for testing the swap flow on testnets where DEX pools might not exist
"""

from typing import Optional
from .wallet import Wallet


class MockSwapExecutor:
    def __init__(self, network: str = "base"):
        self.network = network
        self.wallet = Wallet(network)

        # Mock exchange rates (for simulation only)
        self.mock_rates = {
            "ETH_TO_USDC": 2800.0,
            "USDC_TO_ETH": 1 / 2800.0,
        }

    def execute_mock_swap(
        self, from_token: str, to_token: str, amount: float, min_amount_out: float
    ) -> Optional[str]:
        """Execute a mock swap by just sending the equivalent value"""
        try:
            print(f"🧪 Mock swap: {amount} {from_token} → {to_token}")

            # Calculate mock output amount
            if from_token.upper() == "ETH" and to_token.upper() == "USDC":
                output_amount = (
                    amount * self.mock_rates["ETH_TO_USDC"] * 0.997
                )  # 0.3% fee
            elif from_token.upper() == "USDC" and to_token.upper() == "ETH":
                output_amount = (
                    amount * self.mock_rates["USDC_TO_ETH"] * 0.997
                )  # 0.3% fee
            else:
                print(f"Mock swap not supported for {from_token} → {to_token}")
                return None

            print(
                f"📊 Mock rate: {amount} {from_token} = {output_amount:.6f} {to_token}"
            )

            # For now, just return a mock transaction hash
            # In a real implementation, you might:
            # 1. Send the input tokens to a burn address
            # 2. Mint/send the output tokens from a treasury
            mock_tx_hash = f"0xmock{hash(f'{from_token}{to_token}{amount}'):x}"[
                :42
            ].ljust(66, "0")

            print(f"✅ Mock swap completed! Mock TX: {mock_tx_hash}")

            # Send notification for mock swap
            try:
                from .notifications import NotificationManager

                notifier = NotificationManager()
                notifier.notify_swap_success(
                    f"{amount}",
                    from_token,
                    f"{output_amount:.6f}",
                    to_token,
                    mock_tx_hash,
                )
            except Exception:
                pass  # Don't fail mock swap if notification fails

            return mock_tx_hash

        except Exception as e:
            print(f"Mock swap error: {e}")
            return None
