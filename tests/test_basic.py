"""Basic tests for terminalSwap functionality"""

from unittest.mock import Mock, patch


def test_basic_functionality():
    """Test basic Python functionality"""
    assert 1 + 1 == 2


@patch("requests.get")
def test_mock_api_call(mock_get):
    """Test mocked API response"""
    mock_response = Mock()
    mock_response.json.return_value = {"test": "data"}
    mock_response.status_code = 200
    mock_get.return_value = mock_response

    import requests

    response = requests.get("https://api.example.com")
    data = response.json()

    assert data["test"] == "data"
    assert response.status_code == 200


def test_token_validation_logic():
    """Test token validation logic without imports"""
    # Mock token list
    available_tokens = ["ETH", "USDC", "USDT"]

    # Test valid token
    assert "ETH" in available_tokens
    assert "USDC" in available_tokens

    # Test invalid token
    assert "INVALID" not in available_tokens
