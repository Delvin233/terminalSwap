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
            connected = self.w3.is_connected()
            if not connected:
                print(f"DEBUG: Failed to connect to {self.network_config.rpc_url}")
            return connected
        except Exception as e:
            print(f"DEBUG: Connection error: {e}")
            return False

    def send_eth(self, to_address: str, amount: float) -> str:
        """Send native ETH to an address"""
        try:
            # Convert amount to wei
            amount_wei = self.w3.to_wei(amount, "ether")

            # Convert to checksum address
            to_address = self.w3.to_checksum_address(to_address)

            # Build transaction
            transaction = {
                "to": to_address,
                "value": amount_wei,
                "gas": 21000,  # Standard ETH transfer gas
                "gasPrice": self.w3.eth.gas_price,
                "nonce": self.w3.eth.get_transaction_count(self.address, "pending"),
            }

            # Sign and send transaction
            signed_tx = self.w3.eth.account.sign_transaction(
                transaction, self.account.key
            )
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)

            return tx_hash.hex()

        except Exception as e:
            print(f"ETH transfer error: {e}")
            return None

    def send_token(self, token_address: str, to_address: str, amount: float) -> str:
        """Send ERC20 token to an address"""
        try:
            # Convert addresses to checksum format
            token_address = self.w3.to_checksum_address(token_address)
            to_address = self.w3.to_checksum_address(to_address)

            # ERC20 transfer ABI
            erc20_abi = [
                {
                    "inputs": [
                        {"name": "to", "type": "address"},
                        {"name": "amount", "type": "uint256"},
                    ],
                    "name": "transfer",
                    "outputs": [{"name": "", "type": "bool"}],
                    "type": "function",
                }
            ]

            # Get token decimals (assume 6 for USDC, 18 for others)
            decimals = 6 if "usdc" in token_address.lower() else 18
            amount_wei = int(amount * 10**decimals)

            # Create contract instance
            token_contract = self.w3.eth.contract(address=token_address, abi=erc20_abi)

            # Build transaction
            transaction = token_contract.functions.transfer(
                to_address, amount_wei
            ).build_transaction(
                {
                    "from": self.address,
                    "gas": 100000,  # Standard ERC20 transfer gas
                    "gasPrice": self.w3.eth.gas_price,
                    "nonce": self.w3.eth.get_transaction_count(self.address, "pending"),
                }
            )

            # Sign and send transaction
            signed_tx = self.w3.eth.account.sign_transaction(
                transaction, self.account.key
            )
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)

            return tx_hash.hex()

        except Exception as e:
            print(f"Token transfer error: {e}")
            return None
