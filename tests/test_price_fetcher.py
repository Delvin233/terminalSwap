from src.price_fetcher import PriceFetcher


def test_price_fetcher_init():
    """Test PriceFetcher initialization"""
    fetcher = PriceFetcher()
    assert fetcher.base_url == "https://api.coingecko.com/api/v3"


def test_get_eth_price():
    """Test getting ETH price"""
    fetcher = PriceFetcher()
    price = fetcher.get_token_price("ETH")
    assert price is not None
    assert price > 0


def test_get_invalid_token_price():
    """Test getting price for invalid token"""
    fetcher = PriceFetcher()
    price = fetcher.get_token_price("INVALID_TOKEN")
    assert price is None


def test_get_multiple_prices():
    """Test getting multiple token prices"""
    fetcher = PriceFetcher()
    prices = fetcher.get_multiple_prices(["ETH", "USDC"])
    assert isinstance(prices, dict)
    assert "ETH" in prices or "USDC" in prices
