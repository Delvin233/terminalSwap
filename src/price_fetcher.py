import requests
from typing import Dict, Optional


class PriceFetcher:
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"

    def get_token_price(self, token_symbol: str) -> Optional[float]:
        """Get USD price for a token"""
        try:
            # Map common symbols to CoinGecko IDs
            token_map = {
                "ETH": "ethereum",
                "WETH": "ethereum",
                "USDC": "usd-coin",
                "USDT": "tether",
                "CELO": "celo",
                "CUSD": "celo-dollar",
                "cUSD": "celo-dollar",  # Support mixed case
                "CEUR": "celo-euro",
                "cEUR": "celo-euro",   # Support mixed case
                "DEGEN": "degen-base",
                "BRETT": "brett",
                "G$": "gooddollar",
            }

            # Try exact match first, then uppercase
            token_id = token_map.get(token_symbol) or token_map.get(token_symbol.upper())
            if not token_id:
                return None

            response = requests.get(
                f"{self.base_url}/simple/price",
                params={"ids": token_id, "vs_currencies": "usd"},
                timeout=5,
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get(token_id, {}).get("usd")

        except Exception:
            pass

        return None

    def get_multiple_prices(self, symbols: list) -> Dict[str, float]:
        """Get prices for multiple tokens at once"""
        prices = {}
        for symbol in symbols:
            price = self.get_token_price(symbol)
            if price:
                prices[symbol] = price
        return prices
