# API Integration Guide

terminalSwap integrates with multiple APIs to provide comprehensive multi-chain functionality.

## Etherscan API V2

### Overview

Unified API for transaction history and token discovery across 60+ networks.

**Base URL**: `https://api.etherscan.io/v2/api`

### Supported Networks

| Network      | Chain ID | Free Tier    | Status            |
| ------------ | -------- | ------------ | ----------------- |
| Ethereum     | 1        | ✅ Available | Full features     |
| Celo         | 42220    | ✅ Available | Full features     |
| Base         | 8453     | ❌ Paid only | Limited free tier |
| Base Sepolia | 84532    | ❌ Paid only | Limited free tier |

### Setup

1. Create account at [Etherscan](https://etherscan.io/register)
2. Get API key from [dashboard](https://etherscan.io/apidashboard)
3. Add to `.env`: `ETHERSCAN_API_KEY=YourApiKeyHere`

### Rate Limits

- **Free Tier**: 5 calls/second, 100,000 calls/day
- **Paid Plans**: Higher limits, priority access

### Endpoints Used

#### Transaction History

```bash
GET /v2/api?chainid=1&module=account&action=txlist&address=0x...&apikey=...
```

#### Token Transfers

```bash
GET /v2/api?chainid=1&module=account&action=tokentx&address=0x...&apikey=...
```

### Error Handling

- Automatic retry logic for Base network inconsistencies
- Graceful degradation when API limits reached
- Clear user messaging for upgrade requirements

## CoinGecko API

### Overview

Real-time cryptocurrency price data for portfolio valuation.

**Base URL**: `https://api.coingecko.com/api/v3`

### Token Mapping

```python
token_map = {
    "ETH": "ethereum",
    "USDC": "usd-coin",
    "CELO": "celo",
    "ZORA": "zora",
    "WCT": "connect-token-wct",
    "G$": "gooddollar",
    # ... more tokens
}
```

### Endpoint Used

```bash
GET /simple/price?ids=ethereum,zora&vs_currencies=usd
```

### Features

- No API key required
- Rate limits: ~50 calls/minute
- Supports 10,000+ cryptocurrencies
- Real-time price updates

## Alchemy RPC

### Overview

Enhanced Ethereum RPC endpoints for better reliability and performance.

### Supported Networks

- **Ethereum Mainnet**: `eth-mainnet.g.alchemy.com`
- **Base Mainnet**: `base-mainnet.g.alchemy.com`
- **Base Sepolia**: `base-sepolia.g.alchemy.com`

### Setup

1. Create account at [Alchemy](https://alchemy.com)
2. Create apps for each network
3. Add to `.env`:

```bash
ETHEREUM_RPC_URL=https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY
BASE_RPC_URL=https://base-mainnet.g.alchemy.com/v2/YOUR_KEY
BASE_SEPOLIA_RPC_URL=https://base-sepolia.g.alchemy.com/v2/YOUR_KEY
```

### Benefits

- No rate limiting (vs public RPCs)
- Enhanced reliability
- Better for DEX integrations
- Advanced features (traces, NFTs, etc.)

### Fallback Strategy

If Alchemy keys not provided, falls back to public RPCs:

- Ethereum: `https://ethereum-rpc.publicnode.com`
- Base: `https://base-rpc.publicnode.com`
- Celo: `https://forno.celo.org`

## API Integration Architecture

### Layered Approach

1. **Primary**: Alchemy RPC for blockchain interactions
2. **Secondary**: Public RPCs as fallback
3. **History**: Etherscan V2 for transaction data
4. **Pricing**: CoinGecko for USD values

### Error Handling Strategy

```python
try:
    # Try primary API (Alchemy)
    result = alchemy_call()
except:
    try:
        # Fallback to public RPC
        result = public_rpc_call()
    except:
        # Graceful degradation
        return None
```

### Retry Logic

- Exponential backoff for rate limits
- Network-specific retry counts (Base: 2x, others: 1x)
- Clear user messaging for persistent failures

## Configuration Examples

### Complete .env Setup

```bash
# Wallet (Required)
PRIVATE_KEY=0x1234567890abcdef...

# Etherscan V2 (Recommended for history)
ETHERSCAN_API_KEY=YourEtherscanApiKey

# Alchemy RPCs (Optional but recommended)
ETHEREUM_RPC_URL=https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY
BASE_RPC_URL=https://base-mainnet.g.alchemy.com/v2/YOUR_KEY
BASE_SEPOLIA_RPC_URL=https://base-sepolia.g.alchemy.com/v2/YOUR_KEY
```

### Minimal Setup (Free)

```bash
# Only wallet required for basic functionality
PRIVATE_KEY=0x1234567890abcdef...

# Uses public RPCs and no transaction history
```

## API Usage Patterns

### Balance Checking

1. Connect to RPC (Alchemy or public)
2. Query token balances via smart contracts
3. Fetch prices from CoinGecko
4. Calculate USD values

### Transaction History

1. Query Etherscan V2 for transaction list
2. Parse ETH and ERC20 transfers
3. Enrich with current price data
4. Format for terminal display

### Token Discovery

1. Scan transaction history via Etherscan V2
2. Extract unique token contracts
3. Validate contract addresses
4. Integrate with balance checking

## Performance Optimizations

### Caching Strategy

- Price data cached for 60 seconds
- Discovery results cached per session
- RPC connections reused

### Batch Operations

- Multiple token balances in single call
- Bulk price fetching when possible
- Parallel network queries

### Rate Limit Management

- Built-in delays between calls
- Exponential backoff on errors
- User feedback for long operations

## Troubleshooting

### Common Issues

#### No Transaction History

```bash
# Check API key
echo $ETHERSCAN_API_KEY

# Verify network support
python main.py history --network ethereum  # Should work
python main.py history --network base      # May need paid plan
```

#### Price Data Missing

```bash
# Test CoinGecko connection
curl "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd"

# Check token mapping in price_fetcher.py
```

#### RPC Connection Issues

```bash
# Test public RPC
curl -X POST https://ethereum-rpc.publicnode.com \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}'
```

### Debug Mode

Enable debug logging by modifying source:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Future API Integrations

### Planned Additions

- **DeFiLlama**: Enhanced DeFi protocol data
- **Moralis**: NFT and advanced token data
- **The Graph**: Decentralized indexing
- **1inch**: Better DEX aggregation

### Expansion Networks

- Polygon, Arbitrum, Optimism
- Avalanche, Fantom, BSC
- Layer 2 solutions (zkSync, Starknet)

## Security Considerations

### API Key Management

- Store in `.env` file (never commit)
- Use environment variables in production
- Rotate keys regularly

### Rate Limit Compliance

- Respect API terms of service
- Implement proper backoff strategies
- Monitor usage patterns

### Data Validation

- Validate all API responses
- Sanitize user inputs
- Handle malformed data gracefully
