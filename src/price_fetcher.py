import requests
from typing import Dict, Optional
import time


class PriceFetcher:
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.cache = {}
        self.cache_duration = 60  # Cache for 60 seconds

    def get_token_price(self, token_symbol: str) -> Optional[float]:
        """Get USD price for a token with caching"""
        # Check cache first
        cache_key = token_symbol.upper()
        current_time = time.time()
        
        if cache_key in self.cache:
            cached_price, cached_time = self.cache[cache_key]
            if current_time - cached_time < self.cache_duration:
                return cached_price
        
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
                "ZORA": "zora",
                "WCT": "connect-token-wct",
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
                price = data.get(token_id, {}).get("usd")
                
                # Cache the result
                if price is not None:
                    self.cache[cache_key] = (price, current_time)
                
                return price
            else:
                # If rate limited, return cached value if available
                if response.status_code == 429 and cache_key in self.cache:
                    cached_price, _ = self.cache[cache_key]
                    return cached_price

        except Exception as e:
            # Return cached value on exception if available
            if cache_key in self.cache:
                cached_price, _ = self.cache[cache_key]
                return cached_price

        return None

    def get_multiple_prices(self, symbols: list) -> Dict[str, float]:
        """Get prices for multiple tokens at once"""
        prices = {}
        for symbol in symbols:
            price = self.get_token_price(symbol)
            if price:
                prices[symbol] = price
        return prices
