from src.config import NETWORKS, BASE_TOKENS


def test_networks_config():
    """Test network configurations"""
    assert "base" in NETWORKS
    assert "ethereum" in NETWORKS
    assert "celo" in NETWORKS

    # Test Base config
    base_config = NETWORKS["base"]
    assert base_config.name == "Base"
    assert base_config.chain_id == 8453
    assert base_config.native_token == "ETH"


def test_base_tokens():
    """Test Base token addresses"""
    assert "ETH" in BASE_TOKENS
    assert "USDC" in BASE_TOKENS
    assert BASE_TOKENS["ETH"] == "0x0000000000000000000000000000000000000000"
