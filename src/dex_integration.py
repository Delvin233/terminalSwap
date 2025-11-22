from typing import Optional, Dict
from .wallet import Wallet


class UniswapV3Integration:
    def __init__(self, network: str = "base"):
        self.network = network
        self.wallet = Wallet(network)

        # Uniswap V3 contract addresses
        self.contracts = {
            "base": {
                "router": "0x2626664c2603336E57B271c5C0b26F421741e481",  # SwapRouter02
                "factory": "0x33128a8fC17869897dcE68Ed026d694621f6FDfD",
                "quoter": "0x3d4e44Eb1374240CE5F1B871ab261CD16335B76a",  # QuoterV2 on Base
            },
            "ethereum": {
                "router": "0x68b3465833fb72A70ecDF485E0e4C7bD8665Fc45",
                "factory": "0x1F98431c8aD98523631AE4a59f267346ea31F984",
                "quoter": "0xb27308f9F90D607463bb33eA1BeBb41C27CE5AB6",
            },
        }

    def get_quote(
        self, token_in: str, token_out: str, amount_in: int, fee: int = 500
    ) -> Optional[int]:
        """Get exact quote from Uniswap V3 Quoter"""
        try:
            quoter_address = self.contracts[self.network]["quoter"]

            # QuoterV2 ABI (correct signature)
            quoter_abi = [
                {
                    "inputs": [
                        {
                            "components": [
                                {"name": "tokenIn", "type": "address"},
                                {"name": "tokenOut", "type": "address"},
                                {"name": "fee", "type": "uint24"},
                                {"name": "amountIn", "type": "uint256"},
                                {"name": "sqrtPriceLimitX96", "type": "uint160"},
                            ],
                            "name": "params",
                            "type": "tuple",
                        }
                    ],
                    "name": "quoteExactInputSingle",
                    "outputs": [
                        {"name": "amountOut", "type": "uint256"},
                        {"name": "sqrtPriceX96After", "type": "uint160"},
                        {"name": "initializedTicksCrossed", "type": "uint32"},
                        {"name": "gasEstimate", "type": "uint256"},
                    ],
                    "type": "function",
                }
            ]

            quoter = self.wallet.w3.eth.contract(address=quoter_address, abi=quoter_abi)

            # Test if contract exists
            try:
                code = self.wallet.w3.eth.get_code(quoter_address)
                print(f"DEBUG: Quoter contract code length: {len(code)}")
                if len(code) <= 2:  # Just '0x'
                    print("DEBUG: No contract at quoter address!")
                    return None
            except Exception as e:
                print(f"DEBUG: Failed to get contract code: {e}")
                return None

            # First check if pools exist using Factory
            factory_address = self.contracts[self.network]["factory"]
            factory_abi = [
                {
                    "inputs": [
                        {"name": "tokenA", "type": "address"},
                        {"name": "tokenB", "type": "address"},
                        {"name": "fee", "type": "uint24"},
                    ],
                    "name": "getPool",
                    "outputs": [{"name": "pool", "type": "address"}],
                    "type": "function",
                }
            ]

            factory = self.wallet.w3.eth.contract(
                address=factory_address, abi=factory_abi
            )

            # Try different fee tiers and check if pools exist
            fee_tiers = [500, 3000, 10000]

            for fee_tier in fee_tiers:
                try:
                    # Check if pool exists
                    pool_address = factory.functions.getPool(
                        token_in, token_out, fee_tier
                    ).call()
                    print(f"DEBUG: Pool for fee {fee_tier}: {pool_address}")

                    if pool_address == "0x0000000000000000000000000000000000000000":
                        print(f"DEBUG: No pool exists for fee tier {fee_tier}")
                        continue

                    print(f"DEBUG: Trying quoter for fee tier {fee_tier}")

                    # QuoterV2 uses struct parameter
                    quote_params = {
                        "tokenIn": token_in,
                        "tokenOut": token_out,
                        "fee": fee_tier,
                        "amountIn": amount_in,
                        "sqrtPriceLimitX96": 0,
                    }

                    result = quoter.functions.quoteExactInputSingle(quote_params).call()
                    amount_out = result[0]  # First element is amountOut
                    print(
                        f"DEBUG: Success with fee tier {fee_tier}, amount_out: {amount_out}"
                    )
                    return amount_out
                except Exception as e:
                    print(f"DEBUG: Fee tier {fee_tier} failed: {e}")
                    continue

            return None

        except Exception as e:
            print(f"DEBUG: UniswapV3Integration.get_quote error: {e}")
            import traceback

            traceback.print_exc()
            return None

    def prepare_swap_transaction(
        self,
        token_in: str,
        token_out: str,
        amount_in: int,
        amount_out_min: int,
        fee: int = 3000,
    ) -> Optional[Dict]:
        """Prepare swap transaction data"""
        try:
            router_address = self.contracts[self.network]["router"]

            # SwapRouter02 ABI (simplified)
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

            # Prepare transaction parameters
            swap_params = {
                "tokenIn": token_in,
                "tokenOut": token_out,
                "fee": fee,
                "recipient": self.wallet.address,
                "amountIn": amount_in,
                "amountOutMinimum": amount_out_min,
                "sqrtPriceLimitX96": 0,
            }

            # Build transaction
            transaction = router.functions.exactInputSingle(
                swap_params
            ).build_transaction(
                {
                    "from": self.wallet.address,
                    "gas": 200000,  # Will be estimated properly
                    "gasPrice": self.wallet.w3.eth.gas_price,
                    "nonce": self.wallet.w3.eth.get_transaction_count(
                        self.wallet.address
                    ),
                }
            )

            return transaction

        except Exception:
            return None
