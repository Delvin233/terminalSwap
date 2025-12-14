# Supported Chains

The [**Get Contract ABI**](https://docs.etherscan.io/api-reference/endpoint/getabi), [**Get Contract Source Code**](https://docs.etherscan.io/api-reference/endpoint/getsourcecode), and [**Verify Source Code**](https://docs.etherscan.io/api-reference/endpoint/verifysourcecode) endpoints are available on all chains for every API plan, including the Free Tier.

For Solana(SOL) data, we're also working on the [**Solscan APIs**](https://solscan.io/apis), available separately.

| Chain Name                | Chain ID  | Free Tier     |
| ------------------------- | --------- | ------------- |
| Ethereum Mainnet          | 1         | Available     |
| Sepolia Testnet           | 11155111  | Available     |
| Holesky Testnet           | 17000     | Available     |
| Hoodi Testnet             | 560048    | Available     |
| Abstract Mainnet          | 2741      | Available     |
| Abstract Sepolia Testnet  | 11124     | Available     |
| ApeChain Curtis Testnet   | 33111     | Available     |
| ApeChain Mainnet          | 33139     | Available     |
| Arbitrum Nova Mainnet     | 42170     | Available     |
| Arbitrum One Mainnet      | 42161     | Available     |
| Arbitrum Sepolia Testnet  | 421614    | Available     |
| Avalanche C-Chain         | 43114     | Not Available |
| Avalanche Fuji Testnet    | 43113     | Not Available |
| Base Mainnet              | 8453      | Not Available |
| Base Sepolia Testnet      | 84532     | Not Available |
| Berachain Bepolia Testnet | 80069     | Available     |
| Berachain Mainnet         | 80094     | Available     |
| BitTorrent Chain Mainnet  | 199       | Available     |
| BitTorrent Chain Testnet  | 1029      | Available     |
| Blast Mainnet             | 81457     | Available     |
| Blast Sepolia Testnet     | 168587773 | Available     |
| BNB Smart Chain Mainnet   | 56        | Not Available |
| BNB Smart Chain Testnet   | 97        | Not Available |
| Celo Mainnet              | 42220     | Available     |
| Celo Sepolia Testnet      | 11142220  | Available     |
| Fraxtal Mainnet           | 252       | Available     |
| Fraxtal Hoodi Testnet     | 2523      | Available     |
| Gnosis                    | 100       | Available     |
| HyperEVM Mainnet          | 999       | Available     |
| Katana Bokuto             | 737373    | Available     |
| Katana Mainnet            | 747474    | Available     |
| Linea Mainnet             | 59144     | Available     |
| Linea Sepolia Testnet     | 59141     | Available     |
| Mantle Mainnet            | 5000      | Available     |
| Mantle Sepolia Testnet    | 5003      | Available     |
| Memecore Testnet          | 43521     | Available     |
| Monad Mainnet             | 143       | Available     |
| Monad Testnet             | 10143     | Available     |
| Moonbase Alpha Testnet    | 1287      | Available     |
| Moonbeam Mainnet          | 1284      | Available     |
| Moonriver Mainnet         | 1285      | Available     |
| OP Mainnet                | 10        | Not Available |
| OP Sepolia Testnet        | 11155420  | Not Available |
| opBNB Mainnet             | 204       | Available     |
| opBNB Testnet             | 5611      | Available     |
| Polygon Amoy Testnet      | 80002     | Available     |
| Polygon Mainnet           | 137       | Available     |
| Scroll Mainnet            | 534352    | Available     |
| Scroll Sepolia Testnet    | 534351    | Available     |
| Sei Mainnet               | 1329      | Available     |
| Sei Testnet               | 1328      | Available     |
| Sonic Mainnet             | 146       | Available     |
| Sonic Testnet             | 14601     | Available     |
| Stable Mainnet            | 988       | Available     |
| Stable Testnet            | 2201      | Available     |
| Swellchain Mainnet        | 1923      | Available     |
| Swellchain Testnet        | 1924      | Available     |
| Taiko Hoodi               | 167013    | Available     |
| Taiko Mainnet             | 167000    | Available     |
| Unichain Mainnet          | 130       | Available     |
| Unichain Sepolia Testnet  | 1301      | Available     |
| World Mainnet             | 480       | Available     |
| World Sepolia Testnet     | 4801      | Available     |
| XDC Apothem Testnet       | 51        | Available     |
| XDC Mainnet               | 50        | Available     |
| zkSync Mainnet            | 324       | Available     |
| zkSync Sepolia Testnet    | 300       | Available     |

---

> To find navigation and other pages in this documentation, fetch the llms.txt file at: https://docs.etherscan.io/llms.txt

# V2 Migration

<Tip>
  [Contract verification](/contract-verification/verify-with-foundry) using Hardhat/Remix/Foundry also support using a single Etherscan API key for all chains
</Tip>

As of **August 15th, 2025**, the legacy **Etherscan API V1 endpoints have been deprecated** in favor of the new **Etherscan API V2**, which introduces a unified multichain experience across 60+ supported networks 🌈.

You’ll see a deprecation error message like this if you’re still using V1:

```json theme={null}
{
  "status": "0",
  "message": "NOTOK",
  "result": "You are using a deprecated V1 endpoint, switch to Etherscan API V2."
}
```

All existing endpoints remain compatible once you update them to the **V2 format**.

### How to Migrate

<Steps>
  <Step title="Create an Etherscan account">
    [**Sign up**](https://etherscan.io/register) if you don't have an account or if you're using other explorers like BaseScan, BscScan, Polygonscan, etc.
  </Step>

  <Step title="Create an Etherscan API Key">
    Under your Etherscan [**API dashboard**](https://etherscan.io/apidashboard), create a new key. This key can be used to access all [supported chains](/supported-chains) under API V2.
  </Step>

  <Step title="Migrating Endpoints from Etherscan API V1">
    Use `https://api.etherscan.io/v2/api` as your **base path**, and include a `chainid` for your target network (e.g., 1 for Ethereum).

    Before (V1):

    ```text  theme={null}
    https://api.etherscan.io/api?&action=balance&apikey=YourEtherscanApiKey
    ```

    After (V2):

    ```text  theme={null}
    https://api.etherscan.io/v2/api?chainid=1&action=balance&apikey=YourEtherscanApiKey
    ```

  </Step>

  <Step title="Migrating Endpoints from Other Explorers">
    Use the same base path (`https://api.etherscan.io/v2/api`) and include a `chainid` for the relevant chain from [this list](/supported-chains), in this case `137` for Polygon.

    Pass in your **Etherscan API key** instead of the old explorer-specific one.

    Before (PolygonScan V1):

    ```text  theme={null}
    https://api.polygonscan.com/api?&action=balance&apikey=YourPolygonscanApiKey
    ```

    After (V2):

    ```text  theme={null}
    https://api.etherscan.io/v2/api?chainid=137&action=balance&apikey=YourEtherscanApiKey
    ```

  </Step>
</Steps>

---

> To find navigation and other pages in this documentation, fetch the llms.txt file at: https://docs.etherscan.io/llms.txt
