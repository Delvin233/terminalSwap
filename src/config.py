from dataclasses import dataclass
from typing import Dict


@dataclass
class NetworkConfig:
    name: str
    rpc_url: str
    chain_id: int
    native_token: str


NETWORKS: Dict[str, NetworkConfig] = {
    "base": NetworkConfig(
        name="Base",
        rpc_url="https://mainnet.base.org",
        chain_id=8453,
        native_token="ETH",
    ),
    "ethereum": NetworkConfig(
        name="Ethereum",
        rpc_url="https://eth.llamarpc.com",
        chain_id=1,
        native_token="ETH",
    ),
    "celo": NetworkConfig(
        name="Celo",
        rpc_url="https://forno.celo.org",
        chain_id=42220,
        native_token="CELO",
    ),
}

# Common token addresses on Base
BASE_TOKENS = {
    "ETH": "0x0000000000000000000000000000000000000000",  # Native ETH
    "USDC": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
    "WETH": "0x4200000000000000000000000000000000000006",
}
