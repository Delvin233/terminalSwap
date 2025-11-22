from typing import Optional, Dict
from .price_fetcher import PriceFetcher
from .wallet import Wallet


class SwapPreview:
    def __init__(self):
        self.price_fetcher = PriceFetcher()

    def get_swap_quote(
        self, from_token: str, to_token: str, amount: float, network: str = "base"
    ) -> Optional[Dict]:
        """Get swap quote using simple price calculation"""
        try:
            # Validate tokens exist on network
            if not self._validate_tokens_on_network(from_token, to_token, network):
                return None

            from_price = self.price_fetcher.get_token_price(from_token)
            to_price = self.price_fetcher.get_token_price(to_token)

            if not from_price or not to_price:
                return None

            # Simple calculation: (amount * from_price) / to_price
            estimated_output = (amount * from_price) / to_price

            # Simulate 0.3% DEX fee
            fee_percentage = 0.003
            output_after_fee = estimated_output * (1 - fee_percentage)

            # Simulate slippage (0.5% for this example)
            slippage = 0.005
            min_output = output_after_fee * (1 - slippage)

            # Get gas estimation
            gas_info = self._estimate_gas(network)

            return {
                "from_token": from_token,
                "to_token": to_token,
                "from_amount": amount,
                "estimated_output": output_after_fee,
                "min_output": min_output,
                "from_price": from_price,
                "to_price": to_price,
                "fee_percentage": fee_percentage * 100,
                "slippage_percentage": slippage * 100,
                "rate": output_after_fee / amount if amount > 0 else 0,
                "network": network,
                "gas_estimate": gas_info["gas_limit"],
                "gas_price_gwei": gas_info["gas_price_gwei"],
                "gas_cost_usd": gas_info["gas_cost_usd"],
            }

        except Exception:
            return None

    def _estimate_gas(self, network: str) -> Dict:
        """Estimate gas costs for swap transaction"""
        try:
            wallet = Wallet(network)
            if not wallet.is_connected():
                return self._get_fallback_gas(network)

            # Get current gas price
            gas_price_wei = wallet.w3.eth.gas_price
            gas_price_gwei = wallet.w3.from_wei(gas_price_wei, "gwei")

            # Estimate gas limit for swap (typical Uniswap V3 swap)
            gas_limit = self._get_swap_gas_limit(network)

            # Calculate gas cost in ETH
            gas_cost_wei = gas_price_wei * gas_limit
            gas_cost_eth = wallet.w3.from_wei(gas_cost_wei, "ether")

            # Convert to USD
            eth_price = self.price_fetcher.get_token_price("ETH")
            gas_cost_usd = float(gas_cost_eth) * eth_price if eth_price else 0

            return {
                "gas_limit": gas_limit,
                "gas_price_gwei": float(gas_price_gwei),
                "gas_cost_usd": gas_cost_usd,
            }

        except Exception:
            return self._get_fallback_gas(network)

    def _get_swap_gas_limit(self, network: str) -> int:
        """Get typical gas limit for swaps on different networks"""
        gas_limits = {
            "ethereum": 200000,  # Higher gas on mainnet
            "base": 150000,  # Lower gas on L2
            "celo": 120000,  # Even lower on Celo
        }
        return gas_limits.get(network, 150000)

    def _get_fallback_gas(self, network: str) -> Dict:
        """Fallback gas estimates when RPC fails"""
        fallback_data = {
            "ethereum": {
                "gas_limit": 200000,
                "gas_price_gwei": 20.0,
                "gas_cost_usd": 11.0,
            },
            "base": {"gas_limit": 150000, "gas_price_gwei": 0.1, "gas_cost_usd": 0.08},
            "celo": {"gas_limit": 120000, "gas_price_gwei": 0.5, "gas_cost_usd": 0.02},
        }
        return fallback_data.get(network, fallback_data["base"])

    def _validate_tokens_on_network(
        self, from_token: str, to_token: str, network: str
    ) -> bool:
        """Validate that tokens exist on the specified network"""
        from .cli import _get_tokens_for_network

        available_tokens = _get_tokens_for_network(network)
        available_symbols = [t.upper() for t in available_tokens.keys()]

        if from_token.upper() not in available_symbols:
            return False
        if to_token.upper() not in available_symbols:
            return False

        return True
