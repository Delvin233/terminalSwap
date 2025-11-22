import os
from web3 import Web3
from web3.middleware import geth_poa_middleware
from dotenv import load_dotenv
from .config import NETWORKS

load_dotenv()


class Wallet:
    def __init__(self, network: str = "base"):
        self.network_config = NETWORKS[network]
        self.w3 = Web3(Web3.HTTPProvider(self.network_config.rpc_url))
        self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)

        private_key = os.getenv("PRIVATE_KEY")
        if not private_key:
            raise ValueError("PRIVATE_KEY not found in environment")

        self.account = self.w3.eth.account.from_key(private_key)
        self.address = self.account.address

    def get_balance(self, token_address: str = None) -> float:
        """Get ETH balance or ERC20 token balance"""
        if (
            not token_address
            or token_address == "0x0000000000000000000000000000000000000000"
        ):
            # Native ETH balance
            balance_wei = self.w3.eth.get_balance(self.address)
            return self.w3.from_wei(balance_wei, "ether")
        else:
            # ERC20 token balance
            try:
                # ERC20 balanceOf function signature
                balance_data = self.w3.eth.call(
                    {
                        "to": token_address,
                        "data": "0x70a08231" + self.address[2:].zfill(64),
                    }
                )
                balance = int(balance_data.hex(), 16)
                # Most tokens use 6 decimals (USDC) or 18 decimals
                decimals = 6 if "usdc" in token_address.lower() else 18
                return balance / (10**decimals)
            except Exception:
                return 0.0

    def is_connected(self) -> bool:
        """Check if connected to network"""
        try:
            return self.w3.is_connected()
        except Exception:
            return False
