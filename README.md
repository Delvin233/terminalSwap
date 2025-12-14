# terminalSwap

Swapping and transferring crypto through the terminal - inspired by Primeagen's terminal coffee shop!

## Features

- Multi-chain portfolio tracking (Base, Ethereum, Celo, Base Sepolia)
- Token transfers (ETH and ERC20 tokens)
- Token swapping with safety features
- Real-time token prices via CoinGecko
- Beautiful terminal UI with Rich
- Support for major tokens (ETH, USDC, USDT, CELO, G$, DEGEN, BRETT)
- Testnet support with mock swaps

## Quick Start

### 1. Setup Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Wallet & RPC

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with:
# - Your wallet private key (required)
# - RPC API keys (optional but recommended)
```

### 3. Get API Keys (Optional but Recommended)

1. Visit [Alchemy](https://alchemy.com) and create free account
2. Create apps for:
   - Base Mainnet
   - Base Sepolia (for testing)
   - Ethereum Mainnet
3. Copy API keys to `.env` file

**Benefits of API keys:**

- No rate limiting
- Faster responses
- More reliable connections
- Better for DEX quotes

### 4. Usage

```bash
# Portfolio tracking
python main.py balance              # Check Base network
python main.py balance --all        # Check all networks
python main.py balance --network ethereum

# Token transfers
python main.py send 0.01 ETH to 0x1234...5678 --network base-sepolia --preview
python main.py send 10 USDC to 0x1234...5678 --network base

# Transaction history
python main.py history --network ethereum --limit 10  # Recent transactions
python main.py history --network celo --summary        # Transaction statistics
python main.py history --network ethereum --type send  # Filter by type

# Swap preview (safe)
python main.py swap 0.1 ETH to USDC --preview

# Execute swap (real money!)
python main.py swap 0.1 ETH to USDC

# Test on Sepolia (mock swap - safe for testing)
python main.py swap 0.01 ETH to USDC --network base-sepolia
```

## Supported Networks

- **Base** - ETH, USDC, USDT, WETH, DEGEN, BRETT
- **Base Sepolia** - ETH, WETH, USDC (testnet with mock swaps)
- **Ethereum** - ETH, USDC, USDT, WETH
- **Celo** - CELO, cUSD, cEUR, USDC, USDT, G$

## Security

See [SECURITY.md](SECURITY.md) for important security guidelines.

## Configuration

### Environment Variables

| Variable               | Required | Description                            |
| ---------------------- | -------- | -------------------------------------- |
| `PRIVATE_KEY`          | Yes      | Your wallet private key                |
| `BASE_RPC_URL`         | No       | Alchemy API for Base (recommended)     |
| `BASE_SEPOLIA_RPC_URL` | No       | Alchemy API for Base Sepolia testing   |
| `ETHEREUM_RPC_URL`     | No       | Alchemy API for Ethereum (recommended) |

### Example .env

```bash
PRIVATE_KEY=0x1234567890abcdef...
BASE_RPC_URL=https://base-mainnet.g.alchemy.com/v2/YOUR_API_KEY
BASE_SEPOLIA_RPC_URL=https://base-sepolia.g.alchemy.com/v2/YOUR_API_KEY
ETHEREUM_RPC_URL=https://eth-mainnet.g.alchemy.com/v2/YOUR_API_KEY
```

## Roadmap

- [x] Multi-chain balance checking
- [x] Real-time price fetching
- [x] Token transfers (ETH and ERC20)
- [x] DEX integration (Uniswap V3)
- [x] Token swapping with safety features
- [x] Testnet support (Base Sepolia with mock swaps)
- [x] Transaction history with filtering and statistics
- [ ] Interactive TUI mode
- [ ] Hardware wallet support
- [ ] Real DEX swaps on testnets
