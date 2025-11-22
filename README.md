# terminalSwap

Swapping and transferring crypto through the terminal - inspired by Primeagen's terminal coffee shop!

## Features

- Multi-chain portfolio tracking (Base, Ethereum, Celo)
- Real-time token prices via CoinGecko
- Beautiful terminal UI with Rich
- Support for major tokens (ETH, USDC, USDT, CELO, G$, DEGEN, BRETT)
- CLI and interactive modes

## Quick Start

```bash
# Setup
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your private key

# Use
python main.py balance              # Check single network
python main.py balance --all        # Check all networks
python main.py swap ETH USDC 0.1    # Swap (coming soon)
```

## Supported Networks

- **Base** - ETH, USDC, USDT, WETH, DEGEN, BRETT
- **Ethereum** - ETH, USDC, USDT, WETH
- **Celo** - CELO, cUSD, cEUR, USDC, USDT, G$

## Security

See [SECURITY.md](SECURITY.md) for important security guidelines.

## Roadmap

- [x] Multi-chain balance checking
- [x] Real-time price fetching
- [ ] DEX integration (Uniswap V3)
- [ ] Token swapping
- [ ] Interactive TUI mode
- [ ] Transaction history
- [ ] Hardware wallet support
