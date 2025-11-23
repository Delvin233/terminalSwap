from typing import Optional, Dict
from .wallet import Wallet


class SwapExecutor:
    def __init__(self, network: str = "base"):
        self.network = network
        self.wallet = Wallet(network)

        # Uniswap V3 SwapRouter02 addresses
        self.router_addresses = {
            "base": "0x2626664c2603336E57B271c5C0b26F421741e481",
            "base-sepolia": "0x94cC0AaC535CCDB3C01d6787D6413C739ae12bc4",  # Base Sepolia SwapRouter
            "ethereum": "0x68b3465833fb72A70ecDF485E0e4C7bD8665Fc45",
        }

        # Networks that support swapping
        self.supported_networks = ["base", "base-sepolia", "ethereum"]

    def execute_swap(
        self,
        from_token: str,
        to_token: str,
        amount: float,
        min_amount_out: float,
        slippage: float = 0.5,
    ) -> Optional[str]:
        """Execute a token swap transaction"""
        try:
            # Check if network supports swapping
            if self.network not in self.supported_networks:
                print(f"Swap execution not supported on {self.network} network")
                return None
            # Get token addresses
            from .cli import _get_tokens_for_network

            token_addresses = _get_tokens_for_network(self.network)

            from_address = token_addresses.get(from_token.upper())
            to_address = token_addresses.get(to_token.upper())

            if not from_address or not to_address:
                return None

            # For ETH swaps, we'll use exactInputSingle with ETH value
            # No need to approve when sending ETH directly
            is_eth_input = from_token.upper() == "ETH"

            # Convert ETH to WETH address for the swap parameters
            if from_address == "0x0000000000000000000000000000000000000000":
                from_address = token_addresses.get("WETH")
            if to_address == "0x0000000000000000000000000000000000000000":
                to_address = token_addresses.get("WETH")

            # Prepare swap transaction
            tx_data = self._prepare_swap_transaction(
                from_address,
                to_address,
                amount,
                min_amount_out,
                from_token,
                is_eth_input,
            )

            if not tx_data:
                return None

            # Sign and send transaction
            signed_tx = self.wallet.w3.eth.account.sign_transaction(
                tx_data, self.wallet.account.key
            )
            tx_hash = self.wallet.w3.eth.send_raw_transaction(signed_tx.rawTransaction)

            return tx_hash.hex()

        except Exception as e:
            print(f"Swap execution error: {e}")
            return None

    def _prepare_swap_transaction(
        self,
        token_in: str,
        token_out: str,
        amount: float,
        min_amount_out: float,
        from_token: str,
        is_eth_input: bool = False,
    ) -> Optional[Dict]:
        """Prepare swap transaction using SwapRouter02"""
        try:
            router_address = self.router_addresses[self.network]

            # SwapRouter02 exactInputSingle ABI
            router_abi = [
                {
                    "inputs": [
                        {
                            "components": [
                                {"name": "tokenIn", "type": "address"},
                                {"name": "tokenOut", "type": "address"},
                                {"name": "fee", "type": "uint24"},
                                {"name": "recipient", "type": "address"},
                                {"name": "amountIn", "type": "uint256"},
                                {"name": "amountOutMinimum", "type": "uint256"},
                                {"name": "sqrtPriceLimitX96", "type": "uint160"},
                            ],
                            "name": "params",
                            "type": "tuple",
                        }
                    ],
                    "name": "exactInputSingle",
                    "outputs": [{"name": "amountOut", "type": "uint256"}],
                    "type": "function",
                }
            ]

            router = self.wallet.w3.eth.contract(address=router_address, abi=router_abi)

            # Get token decimals
            from_decimals = 18  # Default to 18 for ETH/WETH
            to_decimals = (
                6 if "usdt" in token_out.lower() or "usdc" in token_out.lower() else 18
            )

            # Convert amounts to wei with proper decimals
            amount_in_wei = int(amount * 10**from_decimals)
            min_amount_out_wei = int(min_amount_out * 10**to_decimals)

            # Check minimum swap amount (0.001 ETH minimum)
            if amount < 0.001:
                print("Amount too small. Minimum: 0.001 ETH")
                return None

            # Check if user has enough balance
            # For ETH swaps, check native ETH balance, not WETH
            balance_address = (
                "0x0000000000000000000000000000000000000000"
                if from_token.upper() == "ETH"
                else token_in
            )
            current_balance = self.wallet.get_balance(balance_address)
            if float(current_balance) < amount:
                print(
                    f"Insufficient balance. You have {current_balance:.6f} {from_token}, need {amount}"
                )
                return None

            # Try different fee tiers for Base Sepolia
            fee_tiers = [3000, 500, 10000] if self.network == "base-sepolia" else [3000]

            # Swap parameters - try 0.3% fee first, then 0.05%, then 1%
            swap_params = {
                "tokenIn": token_in,
                "tokenOut": token_out,
                "fee": fee_tiers[0],  # Start with 0.3% fee tier
                "recipient": self.wallet.address,
                "amountIn": amount_in_wei,
                "amountOutMinimum": min_amount_out_wei,
                "sqrtPriceLimitX96": 0,  # No price limit
            }

            # Build transaction with fresh nonce
            nonce = self.wallet.w3.eth.get_transaction_count(
                self.wallet.address, "pending"
            )

            # Set value to amount_in_wei if swapping ETH, otherwise 0
            tx_value = amount_in_wei if is_eth_input else 0

            transaction = router.functions.exactInputSingle(
                swap_params
            ).build_transaction(
                {
                    "from": self.wallet.address,
                    "gas": 200000,
                    "gasPrice": self.wallet.w3.eth.gas_price,
                    "nonce": nonce,
                    "value": tx_value,
                }
            )

            return transaction

        except Exception as e:
            print(f"Transaction preparation error: {e}")
            return None

    def approve_token(
        self, token_address: str, spender: str, amount: int
    ) -> Optional[str]:
        """Approve token spending for SwapRouter"""
        try:
            # ERC20 approve ABI
            erc20_abi = [
                {
                    "inputs": [
                        {"name": "spender", "type": "address"},
                        {"name": "amount", "type": "uint256"},
                    ],
                    "name": "approve",
                    "outputs": [{"name": "", "type": "bool"}],
                    "type": "function",
                }
            ]

            token_contract = self.wallet.w3.eth.contract(
                address=token_address, abi=erc20_abi
            )

            # Build approval transaction with fresh nonce
            nonce = self.wallet.w3.eth.get_transaction_count(
                self.wallet.address, "pending"
            )
            tx = token_contract.functions.approve(spender, amount).build_transaction(
                {
                    "from": self.wallet.address,
                    "gas": 100000,
                    "gasPrice": self.wallet.w3.eth.gas_price,
                    "nonce": nonce,
                }
            )

            # Sign and send
            signed_tx = self.wallet.w3.eth.account.sign_transaction(
                tx, self.wallet.account.key
            )
            tx_hash = self.wallet.w3.eth.send_raw_transaction(signed_tx.rawTransaction)

            return tx_hash.hex()

        except Exception as e:
            print(f"Token approval error: {e}")
            return None
