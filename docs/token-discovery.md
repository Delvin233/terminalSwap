# Dynamic Token Discovery

terminalSwap automatically discovers tokens from your transaction history, providing a comprehensive view of all tokens you've interacted with across supported networks.

## How It Works

The system scans your transaction history using Etherscan API V2 to find:

- ERC20 token transfers (sent and received)
- Token contract addresses
- Token symbols and metadata
- Real-time price data where available

## Supported Networks

### Free Tier (Etherscan V2)

- **Ethereum Mainnet** (Chain ID: 1) - Full discovery
- **Celo Mainnet** (Chain ID: 42220) - Full discovery
- **Sepolia Testnet** (Chain ID: 11155111) - Full discovery

### Paid Plans Required

- **Base Mainnet** (Chain ID: 8453) - Limited on free tier
- **Base Sepolia** (Chain ID: 84532) - Limited on free tier

## Usage

### Discover Tokens

```bash
# Discover tokens from transaction history
python main.py discover --network ethereum
python main.py discover --network celo
python main.py discover --network base
```

### View in Balance

Discovered tokens automatically appear in your balance with an asterisk (\*):

```bash
python main.py balance --network base
```

Example output:

```
Base Balances
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━┓
┃ Token                       ┃ Balance  ┃ Price (USD) ┃ Value (USD) ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━┩
│ ZORA*                       │ 0.000000 │ $0.05       │ $0.00       │
│ WCT*                        │ 0.000000 │ $0.08       │ $0.00       │
│ delvin233*                  │ 0.000000 │ N/A         │ N/A         │
│ ETH                         │ 0.000103 │ $3100.30    │ $0.32       │
└─────────────────────────────┴──────────┴─────────────┴─────────────┘

* = Discovered from transaction history
```

## Features

### Zero Balance Display

- Shows discovered tokens even with 0 balance for visibility
- Helps track tokens you previously held
- Useful for airdrops and forgotten tokens

### Price Integration

Discovered tokens automatically get price data from CoinGecko:

- **ZORA** - $0.05 (Zora Protocol Token)
- **WCT** - $0.08 (WalletConnect Token)
- **Custom tokens** - Prices when available on CoinGecko

### Smart Caching

- Discovery results are cached during session
- Reduces API calls and improves performance
- Graceful handling of API rate limits

## API Requirements

### Setup Etherscan API Key

1. Visit [Etherscan](https://etherscan.io/register)
2. Create free account
3. Go to [API Dashboard](https://etherscan.io/apidashboard)
4. Create new API key
5. Add to `.env`: `ETHERSCAN_API_KEY=YourApiKeyHere`

### Network Limitations

- **Free Tier**: Full discovery on Ethereum, Celo, testnets
- **Base Networks**: Requires paid plan for full transaction history
- **API Inconsistency**: Base APIs may be intermittent (retry logic included)

## Troubleshooting

### No Tokens Found

```bash
# Check if you have transactions on the network
python main.py history --network ethereum

# Verify API key is set
echo $ETHERSCAN_API_KEY
```

### Base Network Issues

Base networks may show "Token discovery temporarily unavailable":

- This is due to API inconsistencies on free tier
- Try running the command again
- Use `history` command to see your tokens
- Consider upgrading to paid Etherscan plan

### API Rate Limits

- Free tier: 5 calls/second, 100,000 calls/day
- Paid plans: Higher limits and priority access
- Built-in retry logic handles temporary failures

## Examples

### Real Discovered Tokens

Based on actual transaction history:

- **ZORA** (0x1111...c69) - Zora Protocol governance token
- **WCT** (0xef44...945) - WalletConnect Token
- **delvin233** (0xbabc...9b2) - Custom project token
- **911** (0x4296...102) - Meme coin
- **Telegram @TronVanity88_bot** - Scam token (shows importance of discovery)

### Integration with Balance Command

```bash
# Pre-configured + discovered tokens
python main.py balance --all

# Shows comprehensive portfolio across all networks
# Includes both standard tokens and discovered tokens
# Real-time USD values where available
```

## Security Notes

- Discovery only reads transaction history (no wallet access)
- Contract addresses are validated before balance checks
- Scam tokens are displayed but clearly marked
- Always verify token contracts before trading
