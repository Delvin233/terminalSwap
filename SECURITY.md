# Security Guidelines

## Private Key Safety
- **NEVER** commit your `.env` file
- **NEVER** share your private key
- Use a separate wallet for testing
- Consider hardware wallet integration for production

## Environment Setup
1. Copy `.env.example` to `.env`
2. Add your private key to `.env`
3. Ensure `.env` is in `.gitignore`

## Network Security
- Uses HTTPS RPC endpoints
- Validates network connections
- Handles API failures gracefully

## Dependencies
- Keep dependencies updated
- Review `requirements.txt` regularly
- Use virtual environments

## Recommendations
- Test with small amounts first
- Verify transaction details before signing
- Use testnet for development