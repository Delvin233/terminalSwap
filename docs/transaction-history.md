# Transaction History

terminalSwap provides comprehensive transaction history tracking across multiple networks using Etherscan API V2.

## Features

- **Multi-network support** - Ethereum, Celo, Base (with limitations)
- **Transaction filtering** - By type (send/receive), date, amount
- **USD value calculations** - Real-time pricing for historical transactions
- **Gas fee tracking** - Monitor transaction costs
- **Summary statistics** - Portfolio analytics
- **Explorer integration** - Direct links to block explorers

## Usage

### Basic History

```bash
# Recent transactions (default: 20)
python main.py history --network ethereum

# Limit number of transactions
python main.py history --network celo --limit 10

# Filter by transaction type
python main.py history --network base --type send
python main.py history --network ethereum --type receive
```

### Summary Statistics

```bash
# Get portfolio analytics
python main.py history --network ethereum --summary
```

Example output:

```
📊 Transaction Summary - CELO
┏━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┓
┃ Metric             ┃ Value  ┃
┡━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━┩
│ Total Transactions │ 40     │
│ Total Sent         │ $0.00  │
│ Total Received     │ $0.10  │
│ Gas Fees Paid      │ $98.09 │
│ Net Flow           │ +$0.10 │
└────────────────────┴────────┘
```

**Note**: USD values reflect current prices for tokens with CoinGecko support. Custom tokens and meme coins may show $0.00 if price data is unavailable.

## Supported Networks

### Etherscan API V2 Integration

terminalSwap uses the unified Etherscan API V2 for multi-chain support:

| Network      | Chain ID | Free Tier    | Features                      |
| ------------ | -------- | ------------ | ----------------------------- |
| Ethereum     | 1        | ✅ Available | Full history, token discovery |
| Celo         | 42220    | ✅ Available | Full history, token discovery |
| Base         | 8453     | ❌ Paid only | Limited on free tier          |
| Base Sepolia | 84532    | ❌ Paid only | Limited on free tier          |

### API Endpoint

All networks use the unified endpoint:

```
https://api.etherscan.io/v2/api?chainid={CHAIN_ID}&...
```

## Transaction Types

### Native Token Transfers

- ETH transfers on Ethereum/Base
- CELO transfers on Celo network
- Gas fee calculations
- USD value at current prices

### ERC20 Token Transfers

- All token transfers (USDC, USDT, etc.)
- Custom and discovered tokens
- Token metadata (symbol, decimals)
- Real-time price integration

## Data Fields

Each transaction includes:

- **Hash** - Transaction identifier
- **Type** - Send or Receive
- **Token** - Token symbol (ETH, USDC, ZORA, etc.)
- **Amount** - Token amount with proper decimals
- **USD Value** - Current USD value
- **From/To** - Counterparty address (shortened)
- **Date** - Human-readable timestamp
- **Status** - Success/Failed
- **Gas Info** - Gas used, price, cost

## Price Integration

### Real-time USD Values

Historical transactions show current USD values:

```bash
📜 Transaction History - BASE
┏━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━┓
┃ Date             ┃ Type    ┃ Token     ┃ Amount      ┃ USD Value ┃
┡━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━┩
│ 2025-12-13 09:10 │ Receive │ ZORA      │ 0.0200      │ $0.00     │
│ 2025-12-13 09:02 │ Send    │ WCT       │ 50.0000     │ $3.86     │
│ 2025-12-05 14:15 │ Receive │ WCT       │ 200.0000    │ $15.45    │
└──────────────────┴─────────┴───────────┴─────────────┴───────────┘
```

### Supported Tokens

Price data available for:

- **Major tokens**: ETH, USDC, USDT, CELO
- **DeFi tokens**: DEGEN, BRETT
- **Discovered tokens**: ZORA ($0.05), WCT ($0.08)
- **Stablecoins**: cUSD, cEUR, G$

## Setup

### 1. Get Etherscan API Key

```bash
# Visit https://etherscan.io/register
# Create account and get API key
# Add to .env file
ETHERSCAN_API_KEY=YourApiKeyHere
```

### 2. Network Access

- **Free Tier**: Ethereum, Celo, testnets
- **Paid Plans**: Base networks (full features)
- **Rate Limits**: 5 calls/sec, 100k/day (free)

## Examples

### Ethereum History

```bash
python main.py history --network ethereum --limit 5
```

### Celo Token Transfers

```bash
python main.py history --network celo --type receive
```

### Base Network (Limited)

```bash
# May show limited results on free tier
python main.py history --network base
```

## Error Handling

### Common Issues

1. **No API Key**: Set `ETHERSCAN_API_KEY` in `.env`
2. **Rate Limits**: Built-in retry logic
3. **Base Limitations**: Upgrade to paid plan
4. **No Transactions**: Make some transactions first

### Helpful Messages

The system provides guidance:

```bash
💡 Tip: Get an Etherscan API key for ethereum transaction history
   Visit: https://etherscan.io/apidashboard
   Free tier supports Ethereum and Celo networks

💡 BASE native ETH transactions require a paid Etherscan plan
   Token transactions work on free tier (as shown above)
   Upgrade for full history: https://etherscan.io/pricing
```

## Integration with Other Features

### Token Discovery

Transaction history powers automatic token discovery:

- Scans ERC20 transfers for new tokens
- Extracts contract addresses and symbols
- Integrates with balance checking

### Portfolio Tracking

History data enhances portfolio features:

- Net flow calculations
- Gas fee analytics
- Trading activity insights
- Token interaction patterns

## Explorer Links

Direct links to block explorers:

- **Ethereum**: https://etherscan.io/address/
- **Base**: https://basescan.org/address/
- **Celo**: https://celoscan.io/address/
- **Base Sepolia**: https://sepolia.basescan.org/address/

## Future Enhancements

- Historical price data (not just current prices)
- Advanced filtering (date ranges, amounts)
- Export to CSV/JSON
- Portfolio performance analytics
- DeFi protocol interaction tracking
