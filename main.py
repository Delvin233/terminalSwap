#!/usr/bin/env python3
import warnings
import sys
from src.cli import cli

warnings.filterwarnings("ignore", category=UserWarning, module="web3")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        # No arguments - launch interactive TUI (coming soon)
        print(" terminalSwap - Multi-chain crypto swapping tool")
        print("\n📊 Portfolio tracking:")
        print("  python main.py balance                     # Check Base network")
        print("  python main.py balance --all               # Check all networks")
        print("  python main.py balance --network celo      # Check other networks")
        print("\n🔄 Swap preview:")
        print("  python main.py swap 0.1 ETH to USDC --preview")
        print("  python main.py swap 10 CELO to G$ --network celo --preview")
        print("\n📜 Transaction history:")
        print("  python main.py history --network base --limit 10")
        print("  python main.py history --summary")
        print("\n📚 More help: python main.py --help")
        print("\n⚠️  Interactive TUI mode coming soon!")
    else:
        # CLI mode
        cli()
