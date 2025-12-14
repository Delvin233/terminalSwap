"""Transaction history fetcher for terminalSwap"""

import requests
from typing import List, Dict, Optional
from datetime import datetime
from .config import NETWORKS
from .price_fetcher import PriceFetcher


class TransactionHistory:
    def __init__(self, network: str = "base"):
        self.network = network
        self.network_config = NETWORKS[network]
        self.price_fetcher = PriceFetcher()

        # API configuration
        import os

        # Etherscan API V2 for supported networks
        self.etherscan_v2_url = "https://api.etherscan.io/v2/api"
        self.etherscan_api_key = os.getenv("ETHERSCAN_API_KEY")

        # Chain ID mapping for Etherscan API V2 (now includes Base!)
        self.etherscan_v2_chains = {
            "ethereum": 1,
            "base": 8453,
            "base-sepolia": 84532,
            "celo": 42220,
        }

        # Token addresses for each network (for filtering ERC20 transfers)
        self.token_addresses = self._get_network_tokens()

    def _get_network_tokens(self) -> Dict[str, str]:
        """Get token addresses for the current network"""
        if self.network == "base":
            return {
                "USDC": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
                "USDT": "0xfde4C96c8593536E31F229EA8f37b2ADa2699bb2",
                "WETH": "0x4200000000000000000000000000000000000006",
                "DEGEN": "0x4ed4E862860beD51a9570b96d89aF5E1B0Efefed",
                "BRETT": "0x532f27101965dd16442E59d40670FaF5eBB142E4",
            }
        elif self.network == "base-sepolia":
            return {
                "WETH": "0x4200000000000000000000000000000000000006",
                "USDC": "0x036CbD53842c5426634e7929541eC2318f3dCF7e",
            }
        elif self.network == "celo":
            return {
                "cUSD": "0x765DE816845861e75A25fCA122bb6898B8B1282a",
                "cEUR": "0xD8763CBa276a3738E6DE85b4b3bF5FDed6D6cA73",
                "USDC": "0xcebA9300f2b948710d2653dD7B07f33A8B32118C",
                "USDT": "0x88eeC49252c8cbc039DCdB394c0c2BA2f1637EA0",
                "G$": "0x62B8B11039FcfE5aB0C56E502b1C372A3d2a9c7A",
            }
        else:  # ethereum
            return {
                "USDC": "0xA0b86a33E6441E6C673C5C9C7C4b4c4b4b4b4b4b",
                "USDT": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
                "WETH": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
            }

    def get_transaction_history(self, address: str, limit: int = 50) -> List[Dict]:
        """Get transaction history for an address"""
        try:
            transactions = []

            # Try explorer APIs first
            eth_txs = self._get_eth_transactions(address, limit)
            transactions.extend(eth_txs)

            token_txs = self._get_token_transactions(address, limit)
            transactions.extend(token_txs)

            # If no transactions found, provide helpful guidance
            if not transactions:
                if not self.etherscan_api_key:
                    print(
                        f"💡 Tip: Get an Etherscan API key for {self.network} transaction history"
                    )
                    print("   Visit: https://etherscan.io/apidashboard")
                    if self.network in ["base", "base-sepolia"]:
                        print("   Note: Base networks require a paid Etherscan plan")
                    else:
                        print("   Free tier supports Ethereum and Celo networks")
                elif self.network in ["base", "base-sepolia"]:
                    print(
                        f"💡 {self.network.upper()} native ETH transactions require a paid Etherscan plan"
                    )
                    print("   Token transactions work on free tier (as shown above)")
                    print("   Upgrade for full history: https://etherscan.io/pricing")

            # Sort by timestamp (newest first)
            transactions.sort(key=lambda x: x["timestamp"], reverse=True)

            # Limit results
            return transactions[:limit]

        except Exception as e:
            print(f"Error fetching transaction history: {e}")
            return []

    def _get_eth_transactions(self, address: str, limit: int) -> List[Dict]:
        """Get ETH transactions from Etherscan API V2"""
        try:
            # Use Etherscan V2 for all supported networks
            chain_id = self.etherscan_v2_chains.get(self.network)
            if not chain_id:
                print(f"DEBUG: Network {self.network} not supported by Etherscan V2")
                return []

            if not self.etherscan_api_key:
                print("DEBUG: No ETHERSCAN_API_KEY found in environment")
                return []

            params = {
                "chainid": chain_id,
                "module": "account",
                "action": "txlist",
                "address": address,
                "startblock": 0,
                "endblock": 99999999,
                "page": 1,
                "offset": limit,
                "sort": "desc",
                "apikey": self.etherscan_api_key,
            }

            response = requests.get(self.etherscan_v2_url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "1":
                    return self._parse_eth_transactions(data.get("result", []), address)
                else:
                    # API returned error status
                    error_msg = data.get("message", "Unknown error")
                    if (
                        self.network in ["base", "base-sepolia"]
                        and error_msg == "NOTOK"
                    ):
                        print(
                            f"💡 {self.network.upper()} native ETH transactions require a paid Etherscan plan"
                        )
                        print("   Token transactions may still work on free tier")
                        print("   Upgrade at: https://etherscan.io/pricing")
                    else:
                        print(f"DEBUG: Etherscan V2 API error for ETH txs: {error_msg}")
            else:
                print(f"DEBUG: HTTP error for ETH txs: {response.status_code}")

            return []

        except Exception:
            return []

    def _get_token_transactions(self, address: str, limit: int) -> List[Dict]:
        """Get ERC20 token transactions from Etherscan API V2"""
        try:
            # Use Etherscan V2 for all supported networks
            chain_id = self.etherscan_v2_chains.get(self.network)
            if not chain_id:
                print(f"DEBUG: Network {self.network} not supported by Etherscan V2")
                return []

            if not self.etherscan_api_key:
                print("DEBUG: No ETHERSCAN_API_KEY found in environment")
                return []

            params = {
                "chainid": chain_id,
                "module": "account",
                "action": "tokentx",
                "address": address,
                "startblock": 0,
                "endblock": 99999999,
                "page": 1,
                "offset": limit,
                "sort": "desc",
                "apikey": self.etherscan_api_key,
            }

            response = requests.get(self.etherscan_v2_url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "1":
                    return self._parse_token_transactions(
                        data.get("result", []), address
                    )
                else:
                    # API returned error status
                    error_msg = data.get("message", "Unknown error")
                    if (
                        self.network in ["base", "base-sepolia"]
                        and "not available" in error_msg.lower()
                    ):
                        print(
                            f"💡 {self.network.upper()} transaction history requires a paid Etherscan plan"
                        )
                        print(
                            "   Base networks are not available on Etherscan V2 Free Tier"
                        )
                        print("   Visit: https://etherscan.io/pricing")
                    else:
                        print(
                            f"DEBUG: Etherscan V2 API error for token txs: {error_msg}"
                        )
            else:
                print(f"DEBUG: HTTP error for token txs: {response.status_code}")

            return []

        except Exception:
            return []

    def _parse_eth_transactions(
        self, raw_txs: List[Dict], user_address: str
    ) -> List[Dict]:
        """Parse ETH transactions into standardized format"""
        transactions = []

        for tx in raw_txs:
            try:
                # Determine transaction type
                is_outgoing = tx["from"].lower() == user_address.lower()
                tx_type = "Send" if is_outgoing else "Receive"

                # Convert wei to ETH
                value_wei = int(tx["value"])
                value_eth = value_wei / 10**18

                # Skip zero-value transactions (usually contract interactions)
                if value_eth == 0:
                    continue

                # Get USD value at current price
                native_token = self.network_config.native_token
                token_price = self.price_fetcher.get_token_price(native_token)
                usd_value = value_eth * token_price if token_price else 0.0

                parsed_tx = {
                    "hash": tx["hash"],
                    "type": tx_type,
                    "token": self.network_config.native_token,
                    "amount": value_eth,
                    "usd_value": usd_value,
                    "from": tx["from"],
                    "to": tx["to"],
                    "timestamp": int(tx["timeStamp"]),
                    "date": datetime.fromtimestamp(int(tx["timeStamp"])).strftime(
                        "%Y-%m-%d %H:%M"
                    ),
                    "gas_used": int(tx["gasUsed"]),
                    "gas_price": int(tx["gasPrice"]) / 10**9,  # Convert to gwei
                    "network": self.network,
                    "status": (
                        "Success" if tx.get("txreceipt_status") == "1" else "Failed"
                    ),
                }

                transactions.append(parsed_tx)

            except Exception:
                continue

        return transactions

    def _parse_token_transactions(
        self, raw_txs: List[Dict], user_address: str
    ) -> List[Dict]:
        """Parse ERC20 token transactions into standardized format"""
        transactions = []

        for tx in raw_txs:
            try:
                # Determine transaction type
                is_outgoing = tx["from"].lower() == user_address.lower()
                tx_type = "Send" if is_outgoing else "Receive"

                # Get token info
                token_symbol = self._clean_token_symbol(
                    tx.get("tokenSymbol", "Unknown")
                )
                token_decimals = int(tx.get("tokenDecimal", 18))

                # Convert token amount
                value_raw = int(tx["value"])
                amount = value_raw / 10**token_decimals

                # Get USD value at current price
                token_price = self.price_fetcher.get_token_price(token_symbol)
                usd_value = amount * token_price if token_price else 0.0

                parsed_tx = {
                    "hash": tx["hash"],
                    "type": tx_type,
                    "token": token_symbol,
                    "amount": amount,
                    "usd_value": usd_value,
                    "from": tx["from"],
                    "to": tx["to"],
                    "timestamp": int(tx["timeStamp"]),
                    "date": datetime.fromtimestamp(int(tx["timeStamp"])).strftime(
                        "%Y-%m-%d %H:%M"
                    ),
                    "gas_used": int(tx["gasUsed"]),
                    "gas_price": int(tx["gasPrice"]) / 10**9,  # Convert to gwei
                    "network": self.network,
                    "status": "Success",  # Token transfers are usually successful if they appear
                }

                transactions.append(parsed_tx)

            except Exception:
                continue

        return transactions

    def get_transaction_summary(self, address: str) -> Dict:
        """Get transaction summary statistics for recent transactions"""
        try:
            transactions = self.get_transaction_history(address, limit=500)

            # Pre-fetch prices for all unique tokens to avoid rate limiting
            unique_tokens = set()
            for tx in transactions:
                unique_tokens.add(tx["token"])

            # Add native token for gas calculations
            unique_tokens.add(self.network_config.native_token)

            # Fetch all prices at once with delays to avoid rate limiting
            token_prices = {}
            for token in unique_tokens:
                price = self.price_fetcher.get_token_price(token)
                if price:
                    token_prices[token] = price
                # Small delay to avoid rate limiting
                import time

                time.sleep(0.1)

            total_sent = 0
            total_received = 0
            total_gas_spent = 0

            for tx in transactions:
                # Recalculate USD value using fetched prices
                token_price = token_prices.get(tx["token"])
                if token_price:
                    usd_value = tx["amount"] * token_price

                    if tx["type"] == "Send":
                        total_sent += usd_value
                    else:
                        total_received += usd_value

                # Calculate gas cost in USD (approximate)
                gas_cost_native = (tx["gas_used"] * tx["gas_price"]) / 10**9
                native_price = token_prices.get(self.network_config.native_token)
                if native_price:
                    total_gas_spent += gas_cost_native * native_price

            return {
                "total_transactions": len(transactions),
                "total_sent_usd": total_sent,
                "total_received_usd": total_received,
                "total_gas_spent_usd": total_gas_spent,
                "net_flow_usd": total_received - total_sent,
            }

        except Exception:
            return {
                "total_transactions": 0,
                "total_sent_usd": 0,
                "total_received_usd": 0,
                "total_gas_spent_usd": 0,
                "net_flow_usd": 0,
            }

    def _get_transactions_via_rpc(self, address: str, limit: int) -> List[Dict]:
        """Fallback method to get recent transactions via RPC"""
        try:
            from .wallet import Wallet

            wallet = Wallet(self.network)
            if not wallet.is_connected():
                return []

            # Get latest block number
            latest_block = wallet.w3.eth.block_number

            # Look back through recent blocks for transactions
            transactions = []
            blocks_to_check = min(1000, latest_block)  # Check last 1000 blocks

            print(f"DEBUG: Scanning last {blocks_to_check} blocks for transactions...")

            for block_num in range(latest_block - blocks_to_check, latest_block + 1):
                try:
                    block = wallet.w3.eth.get_block(block_num, full_transactions=True)

                    for tx in block.transactions:
                        # Check if transaction involves our address
                        if (tx["from"] and tx["from"].lower() == address.lower()) or (
                            tx["to"] and tx["to"].lower() == address.lower()
                        ):
                            # Parse transaction
                            parsed_tx = self._parse_rpc_transaction(tx, address, wallet)
                            if parsed_tx:
                                transactions.append(parsed_tx)

                                # Stop if we have enough transactions
                                if len(transactions) >= limit:
                                    return transactions

                except Exception:
                    continue  # Skip blocks that fail to fetch

            return transactions

        except Exception as e:
            print(f"DEBUG: RPC fallback failed: {e}")
            return []

    def _parse_rpc_transaction(self, tx, user_address: str, wallet) -> Optional[Dict]:
        """Parse a transaction from RPC into standardized format"""
        try:
            # Determine transaction type
            is_outgoing = tx["from"] and tx["from"].lower() == user_address.lower()
            tx_type = "Send" if is_outgoing else "Receive"

            # Convert wei to ETH
            value_wei = int(tx["value"])
            value_eth = value_wei / 10**18

            # Skip zero-value transactions
            if value_eth == 0:
                return None

            # Get USD value at current price
            eth_price = self.price_fetcher.get_token_price("ETH")
            usd_value = value_eth * eth_price if eth_price else 0.0

            # Get transaction receipt for gas info
            try:
                receipt = wallet.w3.eth.get_transaction_receipt(tx["hash"])
                gas_used = receipt["gasUsed"]
                status = "Success" if receipt["status"] == 1 else "Failed"
            except:
                gas_used = tx.get("gas", 21000)
                status = "Unknown"

            return {
                "hash": tx["hash"].hex(),
                "type": tx_type,
                "token": self.network_config.native_token,
                "amount": value_eth,
                "usd_value": usd_value,
                "from": tx["from"],
                "to": tx["to"],
                "timestamp": int(
                    wallet.w3.eth.get_block(tx["blockNumber"])["timestamp"]
                ),
                "date": datetime.fromtimestamp(
                    int(wallet.w3.eth.get_block(tx["blockNumber"])["timestamp"])
                ).strftime("%Y-%m-%d %H:%M"),
                "gas_used": gas_used,
                "gas_price": int(tx["gasPrice"]) / 10**9,  # Convert to gwei
                "network": self.network,
                "status": status,
            }

        except Exception as e:
            print(f"DEBUG: Failed to parse RPC transaction: {e}")
            return None

    def _clean_token_symbol(self, symbol: str) -> str:
        """Clean token symbol by normalizing Unicode characters"""
        if not symbol or symbol == "Unknown":
            return symbol

        # Common Unicode character replacements for token symbols
        replacements = {
            # Various Unicode T characters that look like T
            "Ť": "T",
            "Ţ": "T",
            "Ṫ": "T",
            "₮": "T",
            # Various Unicode S characters that look like S
            "Ś": "S",
            "Ş": "S",
            "Š": "S",
            "Ṡ": "S",
            "Ѕ": "S",
            # Various Unicode D characters
            "Ď": "D",
            "Đ": "D",
            "Ḋ": "D",
            # Various Unicode U characters
            "Ú": "U",
            "Ù": "U",
            "Û": "U",
            "Ü": "U",
            "Ũ": "U",
            "Ū": "U",
            "Ŭ": "U",
            "Ů": "U",
            "Ű": "U",
            "Ų": "U",
        }

        # Apply replacements
        cleaned = symbol
        for unicode_char, ascii_char in replacements.items():
            cleaned = cleaned.replace(unicode_char, ascii_char)

        return cleaned

    def discover_user_tokens(self, address: str) -> Dict[str, str]:
        """Discover tokens from user's transaction history"""
        try:
            discovered = {}

            # Try to get raw token transaction data from API first
            raw_token_data = self._get_raw_token_transactions(address, 100)

            for tx in raw_token_data:
                try:
                    token_symbol = self._clean_token_symbol(
                        tx.get("tokenSymbol", "Unknown")
                    )
                    token_address = tx.get("contractAddress", "")

                    # Skip if we don't have both symbol and address
                    if (
                        not token_symbol
                        or not token_address
                        or token_symbol == "Unknown"
                    ):
                        continue

                    # Skip if already discovered
                    if token_symbol in discovered:
                        continue

                    # Add to discovered tokens
                    discovered[token_symbol] = token_address

                except Exception:
                    continue

            # If no tokens discovered via raw API (e.g., Base networks), try fallback
            if not discovered:
                discovered = self._discover_tokens_from_parsed_history(address)

            return discovered

        except Exception as e:
            print(f"DEBUG: Token discovery failed: {e}")
            return {}

    def _discover_tokens_from_parsed_history(self, address: str) -> Dict[str, str]:
        """Fallback: discover tokens from parsed transaction history with known addresses"""
        try:
            discovered = {}

            # Get parsed token transactions (this works on Base via token tx API)
            token_txs = self._get_token_transactions(address, 50)

            # Known token addresses for Base network (manually curated)
            base_token_addresses = {
                "ZORA": "0x777777777777777777777777777777777777777777",  # Need real address
                "WCT": "0x888888888888888888888888888888888888888888",  # Need real address
                "delvin233": "0x999999999999999999999999999999999999999999",  # Need real address
                # Add more as discovered
            }

            # Extract unique token symbols from parsed transactions
            for tx in token_txs:
                token_symbol = tx.get("token", "Unknown")
                if (
                    token_symbol
                    and token_symbol != "Unknown"
                    and token_symbol not in discovered
                ):
                    # Use known address if available, otherwise skip
                    if token_symbol in base_token_addresses:
                        discovered[token_symbol] = base_token_addresses[token_symbol]

            return discovered

        except Exception:
            return {}

    def _get_raw_token_transactions(self, address: str, limit: int) -> List[Dict]:
        """Get raw token transaction data from API for token discovery with retry logic"""
        try:
            # Use Etherscan V2 for all supported networks
            chain_id = self.etherscan_v2_chains.get(self.network)
            if not chain_id or not self.etherscan_api_key:
                return []

            params = {
                "chainid": chain_id,
                "module": "account",
                "action": "tokentx",
                "address": address,
                "startblock": 0,
                "endblock": 99999999,
                "page": 1,
                "offset": limit,
                "sort": "desc",
                "apikey": self.etherscan_api_key,
            }

            # Try up to 2 times for Base networks (API can be inconsistent)
            max_retries = 2 if self.network in ["base", "base-sepolia"] else 1

            for attempt in range(max_retries):
                try:
                    response = requests.get(
                        self.etherscan_v2_url, params=params, timeout=10
                    )

                    if response.status_code == 200:
                        data = response.json()
                        if data.get("status") == "1":
                            return data.get("result", [])
                        elif attempt < max_retries - 1:
                            # If NOTOK and we have retries left, try again
                            import time

                            time.sleep(1)  # Brief delay before retry
                            continue

                except Exception:
                    if attempt < max_retries - 1:
                        continue

            return []

        except Exception:
            return []
