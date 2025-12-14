"""Tests for transaction history functionality"""

from unittest.mock import Mock, patch
from src.transaction_history import TransactionHistory


def test_transaction_history_init():
    """Test TransactionHistory initialization"""
    tx_history = TransactionHistory("base")
    assert tx_history.network == "base"
    assert "base" in tx_history.explorer_apis
    assert "USDC" in tx_history.token_addresses


def test_get_network_tokens():
    """Test token address mapping for different networks"""
    # Test Base network
    base_history = TransactionHistory("base")
    base_tokens = base_history.token_addresses
    assert "USDC" in base_tokens
    assert "DEGEN" in base_tokens

    # Test Celo network
    celo_history = TransactionHistory("celo")
    celo_tokens = celo_history.token_addresses
    assert "cUSD" in celo_tokens
    assert "G$" in celo_tokens


@patch("requests.get")
def test_get_transaction_history_empty(mock_get):
    """Test transaction history with empty response"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "1", "result": []}
    mock_get.return_value = mock_response

    tx_history = TransactionHistory("base")
    transactions = tx_history.get_transaction_history(
        "0x1234567890123456789012345678901234567890"
    )

    assert isinstance(transactions, list)
    assert len(transactions) == 0


def test_transaction_summary_empty():
    """Test transaction summary with no transactions"""
    tx_history = TransactionHistory("base")

    # Mock empty transaction history
    with patch.object(tx_history, "get_transaction_history", return_value=[]):
        summary = tx_history.get_transaction_summary(
            "0x1234567890123456789012345678901234567890"
        )

        assert summary["total_transactions"] == 0
        assert summary["total_sent_usd"] == 0
        assert summary["total_received_usd"] == 0
        assert summary["net_flow_usd"] == 0


def test_parse_eth_transactions():
    """Test parsing ETH transactions"""
    tx_history = TransactionHistory("base")

    raw_tx = {
        "hash": "0xabc123",
        "from": "0x1111111111111111111111111111111111111111",
        "to": "0x2222222222222222222222222222222222222222",
        "value": "1000000000000000000",  # 1 ETH in wei
        "timeStamp": "1640995200",  # Jan 1, 2022
        "gasUsed": "21000",
        "gasPrice": "20000000000",  # 20 gwei
        "txreceipt_status": "1",
    }

    user_address = "0x2222222222222222222222222222222222222222"
    parsed = tx_history._parse_eth_transactions([raw_tx], user_address)

    assert len(parsed) == 1
    tx = parsed[0]
    assert tx["type"] == "Receive"
    assert tx["token"] == "ETH"
    assert tx["amount"] == 1.0
    assert tx["status"] == "Success"
