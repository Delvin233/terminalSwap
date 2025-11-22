#!/usr/bin/env python3
import warnings
import sys
from src.cli import cli

warnings.filterwarnings("ignore", category=UserWarning, module="web3")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        # No arguments - launch interactive TUI (coming soon)
        print("🚀 Interactive mode coming soon! Use CLI commands for now.")
        print("Try: python main.py balance")
    else:
        # CLI mode
        cli()
