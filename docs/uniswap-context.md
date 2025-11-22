# Uniswap Documentation - LLM Context File

This file provides structured context for Large Language Models about the Uniswap Protocol documentation.

## Base Network Uniswap V3 Deployments

### Contract Addresses (Base Mainnet)
- **Factory**: `0x33128a8fC17869897dcE68Ed026d694621f6FDfD`
- **SwapRouter02**: `0x2626664c2603336E57B271c5C0b26F421741e481`
- **QuoterV2**: `0x3d4e44Eb1374240CE5F1B871ab261CD16335B76a`
- **NFTDescriptor**: `0x4f225937EDc33EFD6109c4ceF7b560B2D6401009`
- **NonfungiblePositionManager**: `0x03a520b32C04BF3bEEf7BF5d56E39E959aeD2142`

### Common Token Addresses (Base)
- **WETH**: `0x4200000000000000000000000000000000000006`
- **USDC**: `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913`
- **USDT**: `0xfde4C96c8593536E31F229EA8f37b2ADa2699bb2`

### Fee Tiers
- **0.05%**: 500 (stablecoin pairs)
- **0.30%**: 3000 (most pairs)
- **1.00%**: 10000 (exotic pairs)

## Integration Notes

### QuoterV2 Usage
- Use `quoteExactInputSingle` for single-hop swaps
- Try multiple fee tiers if pool doesn't exist
- Handle "execution reverted" errors gracefully

### Common Issues
- ETH must be converted to WETH for Uniswap V3
- Different tokens use different decimals (USDC=6, ETH=18)
- Pool may not exist for all token pairs/fee combinations