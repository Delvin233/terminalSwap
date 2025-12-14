# terminalSwap

Swapping and transferring crypto through the terminal - inspired by Primeagen's terminal coffee shop!

## Recent Updates

### Transaction History & Gas Fee Fixes (December 2024)

- **Gas Fee Calculation Fix**: Corrected gas fee calculations to use network-native tokens (CELO for Celo, ETH for Ethereum/Base) instead of always using ETH prices
- **Unicode Token Symbol Cleanup**: Added normalization for special Unicode characters in token symbols (e.g., USD₮ → USDT, Ѕ → S)
- **Transaction Summary Improvements**: Enhanced price fetching with rate limiting protection and better error handling
- **Historical Data Warnings**: Added intelligent discrepancy detection that warns users when transaction history appears incomplete due to API limitations
- **Smart Discrepancy Detection**: Warns when either large amounts (>$1) or high percentages (>50%) are missing from transaction history
- **Balance vs History Validation**: Compares current wallet balance with transaction history to identify missing historical data

## Features

- **Multi-chain portfolio tracking** (Base, Ethereum, Celo, Base Sepolia)
- **Dynamic token discovery** - Automatically finds tokens from your transaction history
- **Transaction history** with filtering, statistics, and USD values
- **Token transfers** (ETH and ERC20 tokens)
- **Token swapping** with safety features and previews
- **Real-time token prices** via CoinGecko API
- **Beautiful terminal UI** with Rich tables and color coding
- **Comprehensive token support** - Pre-configured + auto-discovered tokens
- **Testnet support** with mock swaps for safe testing

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

### 4. Get Etherscan API Key (For Transaction History)

1. Visit [Etherscan](https://etherscan.io/register) and create free account
2. Go to [API Dashboard](https://etherscan.io/apidashboard) and create API key
3. Add to `.env` file: `ETHERSCAN_API_KEY=YourApiKeyHere`

**Supported Networks:**

- **Free Tier**: Ethereum, Celo (full transaction history)
- **Paid Plans**: Base networks (requires upgrade for full features)

### 5. Usage

```bash
# Portfolio tracking with auto-discovery
python main.py balance              # Check Base network
python main.py balance --all        # Check all networks
python main.py balance --network ethereum

# Token discovery
python main.py discover --network base      # Find tokens from transaction history
python main.py discover --network ethereum  # Discover your token interactions

# Transaction history
python main.py history --network ethereum --limit 10  # Recent transactions
python main.py history --network celo --summary        # Transaction statistics
python main.py history --network ethereum --type send  # Filter by type

# Token transfers
python main.py send 0.01 ETH to 0x1234...5678 --network base-sepolia --preview
python main.py send 10 USDC to 0x1234...5678 --network base

# Swap preview (safe)
python main.py swap 0.1 ETH to USDC --preview

# Execute swap (real money!)
python main.py swap 0.1 ETH to USDC

# Test on Sepolia (mock swap - safe for testing)
python main.py swap 0.01 ETH to USDC --network base-sepolia
```

## Supported Networks

### Pre-configured Tokens

- **Base** - ETH, USDC, USDT, WETH, DEGEN, BRETT
- **Base Sepolia** - ETH, WETH, USDC (testnet with mock swaps)
- **Ethereum** - ETH, USDC, USDT, WETH
- **Celo** - CELO, cUSD, cEUR, USDC, USDT, G$

### Dynamic Token Discovery

The system automatically discovers additional tokens from your transaction history:

- **Ethereum & Celo** - Full discovery (Etherscan V2 Free Tier)
- **Base Networks** - Limited discovery (requires paid Etherscan plan)

**Example discovered tokens:** ZORA, WCT (WalletConnect Token), custom project tokens, meme coins, etc.

## Documentation

- **[Token Discovery](docs/token-discovery.md)** - Automatic token discovery from transaction history
- **[Transaction History](docs/transaction-history.md)** - Multi-chain transaction tracking and analytics
- **[API Integration](docs/api-integration.md)** - Etherscan V2, CoinGecko, and Alchemy setup
- **[Uniswap Context](docs/uniswap-context.md)** - DEX integration details

## Security

See [SECURITY.md](SECURITY.md) for important security guidelines.

## Configuration

### Environment Variables

| Variable               | Required | Description                                    |
| ---------------------- | -------- | ---------------------------------------------- |
| `PRIVATE_KEY`          | Yes      | Your wallet private key                        |
| `ETHERSCAN_API_KEY`    | No       | Etherscan V2 API key (for transaction history) |
| `BASE_RPC_URL`         | No       | Alchemy API for Base (recommended)             |
| `BASE_SEPOLIA_RPC_URL` | No       | Alchemy API for Base Sepolia testing           |
| `ETHEREUM_RPC_URL`     | No       | Alchemy API for Ethereum (recommended)         |

### Example .env

```bash
PRIVATE_KEY=0x1234567890abcdef...
ETHERSCAN_API_KEY=YourEtherscanApiKeyHere
BASE_RPC_URL=https://base-mainnet.g.alchemy.com/v2/YOUR_API_KEY
BASE_SEPOLIA_RPC_URL=https://base-sepolia.g.alchemy.com/v2/YOUR_API_KEY
ETHEREUM_RPC_URL=https://eth-mainnet.g.alchemy.com/v2/YOUR_API_KEY
```

### API Key Benefits

**Etherscan API Key:**

- Transaction history on all networks
- Automatic token discovery from your transactions
- Free tier: Ethereum, Celo (full features)
- Paid plans: Base networks (full transaction history)

**Alchemy RPC Keys:**

- No rate limiting
- Faster responses
- More reliable connections
- Better for DEX quotes

## Roadmap

- [x] Multi-chain balance checking
- [x] Real-time price fetching via CoinGecko
- [x] Dynamic token discovery from transaction history
- [x] Transaction history with filtering and statistics
- [x] Etherscan API V2 integration (60+ networks)
- [x] Token transfers (ETH and ERC20)
- [x] DEX integration (Uniswap V3)
- [x] Token swapping with safety features
- [x] Testnet support (Base Sepolia with mock swaps)
- [x] Comprehensive price support (ZORA, WCT, major tokens)
- [ ] Interactive TUI mode
- [ ] Hardware wallet support
- [ ] Real DEX swaps on testnets
- [ ] Portfolio analytics and charts
