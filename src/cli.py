import click
from rich.console import Console
from rich.table import Table
from .wallet import Wallet

# from .config import BASE_TOKENS  # TODO: Use this later
from .price_fetcher import PriceFetcher

console = Console()


@click.group()
def cli():
    """🚀 terminalSwap - Multi-chain crypto swapping and transfers via terminal

    \b
    Features:
    • Multi-chain portfolio tracking (Base, Ethereum, Celo)
    • Real-time token prices via CoinGecko
    • Token transfers and swapping
    • Testnet support (Base Sepolia)

    \b
    Examples:
      python main.py balance --all
      python main.py send 0.01 ETH to 0x1234...5678 --network base-sepolia
      python main.py swap 0.1 ETH to USDC --preview
    """
    pass


@cli.command()
@click.option(
    "--network", default="base", help="Network: base, ethereum, celo, base-sepolia"
)
@click.option("--all", is_flag=True, help="Check balances on all networks")
def balance(network, all):
    """Check wallet balance across networks"""
    try:
        if all:
            # Check all networks in unified table
            console.print("[yellow]🔍 Checking all networks...[/yellow]")

            # Create unified table
            table = Table(title="Multi-Chain Portfolio")
            table.add_column("Network", style="blue")
            table.add_column("Token", style="cyan")
            table.add_column("Balance", style="green")
            table.add_column("Price (USD)", style="yellow")
            table.add_column("Value (USD)", style="magenta")

            price_fetcher = PriceFetcher()
            total_value = 0.0

            networks_to_check = ["base", "ethereum", "celo"]

            for net in networks_to_check:
                try:
                    wallet = Wallet(net)
                    if not wallet.is_connected():
                        continue

                    tokens_to_check = _get_tokens_for_network(net)

                    for token_name, token_address in tokens_to_check.items():
                        balance = wallet.get_balance(token_address)
                        if balance > 0:
                            price = price_fetcher.get_token_price(token_name)
                            if price:
                                value = float(balance) * price
                                total_value += value
                                price_str = (
                                    f"${price:.6f}" if price < 0.01 else f"${price:.2f}"
                                )
                                table.add_row(
                                    net.upper(),
                                    token_name,
                                    f"{balance:.6f}",
                                    price_str,
                                    f"${value:.2f}",
                                )
                            else:
                                table.add_row(
                                    net.upper(),
                                    token_name,
                                    f"{balance:.6f}",
                                    "N/A",
                                    "N/A",
                                )
                except Exception:
                    continue

            console.print(table)
            console.print(
                f"\n[bold green]💰 Total Portfolio Value: ${total_value:.2f}[/bold green]"
            )
        else:
            # Single network
            wallet = Wallet(network)
            if not wallet.is_connected():
                console.print("[red]❌ Failed to connect to network[/red]")
                return

            _show_network_balance(wallet, network)

    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")


def _get_tokens_for_network(network):
    """Get token list for a specific network"""
    if network == "base":
        return {
            "ETH": "0x0000000000000000000000000000000000000000",
            "USDC": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
            "USDT": "0xfde4C96c8593536E31F229EA8f37b2ADa2699bb2",
            "WETH": "0x4200000000000000000000000000000000000006",
            "DEGEN": "0x4ed4E862860beD51a9570b96d89aF5E1B0Efefed",
            "BRETT": "0x532f27101965dd16442E59d40670FaF5eBB142E4",
        }
    elif network == "base-sepolia":
        return {
            "ETH": "0x0000000000000000000000000000000000000000",
            "WETH": "0x4200000000000000000000000000000000000006",
            "USDC": "0x036CbD53842c5426634e7929541eC2318f3dCF7e",  # Base Sepolia USDC
        }
    elif network == "celo":
        return {
            "CELO": "0x0000000000000000000000000000000000000000",
            "cUSD": "0x765DE816845861e75A25fCA122bb6898B8B1282a",
            "cEUR": "0xD8763CBa276a3738E6DE85b4b3bF5FDed6D6cA73",
            "USDC": "0xcebA9300f2b948710d2653dD7B07f33A8B32118C",
            "USDT": "0x88eeC49252c8cbc039DCdB394c0c2BA2f1637EA0",
            "G$": "0x62B8B11039FcfE5aB0C56E502b1C372A3d2a9c7A",
        }
    else:  # ethereum
        return {
            "ETH": "0x0000000000000000000000000000000000000000",
            "USDC": "0xA0b86a33E6441E6C673C5C9C7C4b4c4b4b4b4b4b",
            "USDT": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
            "WETH": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
        }


def _show_network_balance(wallet, network):
    """Helper function to show balance for a specific network"""
    console.print(f"[green]✅ Connected to {wallet.network_config.name}[/green]")
    console.print(f"[blue]Address: {wallet.address}[/blue]")

    # Create balance table with prices
    table = Table(title=f"{wallet.network_config.name} Balances")
    table.add_column("Token", style="cyan")
    table.add_column("Balance", style="green")
    table.add_column("Price (USD)", style="yellow")
    table.add_column("Value (USD)", style="magenta")

    # Get prices
    price_fetcher = PriceFetcher()

    # Get tokens for this network
    tokens_to_check = _get_tokens_for_network(network)

    for token_name, token_address in tokens_to_check.items():
        balance = wallet.get_balance(token_address)
        if balance > 0:  # Only show tokens with balance
            price = price_fetcher.get_token_price(token_name)
            if price:
                value = float(balance) * price
                price_str = f"${price:.6f}" if price < 0.01 else f"${price:.2f}"
                table.add_row(token_name, f"{balance:.6f}", price_str, f"${value:.2f}")
            else:
                table.add_row(token_name, f"{balance:.6f}", "N/A", "N/A")

    console.print(table)


@cli.command()
@click.argument("amount", type=float)
@click.argument("token")
@click.argument("to_keyword")
@click.argument("address")
@click.option(
    "--network", default="base", help="Network: base, ethereum, celo, base-sepolia"
)
@click.option("--preview", is_flag=True, help="Show transfer preview only")
def send(amount, token, to_keyword, address, network, preview):
    """Send tokens to an address\n\n    \b\n    Examples:\n      send 0.01 ETH to 0x1234...5678 --network base-sepolia --preview\n      send 10 USDC to 0x1234...5678 --network base\n"""

    # Validate 'to' keyword
    if to_keyword.lower() != "to":
        console.print(
            "[red]❌ Invalid syntax. Use: send <amount> <token> to <address>[/red]"
        )
        console.print("[yellow]Example: send 0.01 ETH to 0x1234...5678[/yellow]")
        return

    # Validate address format
    if not address.startswith("0x") or len(address) != 42:
        console.print(
            "[red]❌ Invalid address format. Must be 42 characters starting with 0x[/red]"
        )
        return

    addr_short = f"{address[:6]}...{address[-4:]}"
    console.print(
        f"[yellow]📤 Sending {amount} {token} to {addr_short} on {network.upper()}[/yellow]"
    )

    # Check if token exists on network
    token_addresses = _get_tokens_for_network(network)
    if token.upper() not in token_addresses:
        console.print(f"[red]❌ {token} not available on {network.upper()}[/red]")
        available = ", ".join(token_addresses.keys())
        console.print(f"[yellow]Available tokens: {available}[/yellow]")
        return

    # Check balance
    wallet = Wallet(network)
    if not wallet.is_connected():
        console.print("[red]❌ Failed to connect to network[/red]")
        return

    token_address = token_addresses[token.upper()]
    current_balance = wallet.get_balance(token_address)

    if float(current_balance) < amount:
        msg = f"[red]❌ Insufficient balance! You have {current_balance:.6f} {token}, need {amount}[/red]"
        console.print(msg)
        return

    # Show preview
    console.print(
        f"\n[green]✅ Balance check passed: {current_balance:.6f} {token}[/green]"
    )
    console.print(f"[yellow]Sending: {amount} {token}[/yellow]")
    console.print(f"[yellow]To: {address}[/yellow]")
    console.print(f"[yellow]Network: {network.upper()}[/yellow]")

    if preview:
        console.print(
            "[blue]💡 This was a preview only. Remove --preview to execute.[/blue]"
        )
        return

    # Confirm before sending
    console.print("\n[bold red]⚠️  You are about to send real tokens![/bold red]")
    confirm = input("\nProceed with transfer? (yes/no): ").lower().strip()

    if confirm not in ["yes", "y"]:
        console.print("[yellow]Transfer cancelled.[/yellow]")
        return

    # Execute transfer
    console.print("[yellow]📤 Executing transfer...[/yellow]")

    try:
        if token.upper() == "ETH":
            # Send native ETH
            tx_hash = wallet.send_eth(address, amount)
        else:
            # Send ERC20 token
            tx_hash = wallet.send_token(token_address, address, amount)

        if tx_hash:
            explorer_urls = {
                "base": "https://basescan.org/tx/",
                "base-sepolia": "https://sepolia.basescan.org/tx/",
                "ethereum": "https://etherscan.io/tx/",
            }
            explorer_url = explorer_urls.get(network, "")
            console.print(f"[green]✅ Transfer sent! Transaction: {tx_hash}[/green]")
            if explorer_url:
                console.print(
                    f"[blue]🔗 View on explorer: {explorer_url}{tx_hash}[/blue]"
                )
        else:
            console.print("[red]❌ Transfer failed![/red]")

    except Exception as e:
        console.print(f"[red]❌ Transfer error: {e}[/red]")


@cli.command()
@click.argument("amount", type=float)
@click.argument("from_token")
@click.argument("to_keyword")
@click.argument("to_token")
@click.option(
    "--network", default="base", help="Network: base, ethereum, celo, base-sepolia"
)
@click.option("--preview", is_flag=True, help="Show swap preview only")
def swap(amount, from_token, to_keyword, to_token, network, preview):
    """Swap tokens with natural syntax\n\n    \b\n    Examples:\n      swap 0.1 ETH to USDC --preview\n      swap 10 CELO to G$ --network celo --preview\n      swap 0.01 ETH to USDC --network base-sepolia (mock swap)\n"""
    from .swap_preview import SwapPreview

    # Validate 'to' keyword
    if to_keyword.lower() != "to":
        console.print(
            "[red]❌ Invalid syntax. Use: swap <amount> <from_token> to <to_token>[/red]"
        )
        console.print("[yellow]Example: swap 10 CELO to G$ --network celo[/yellow]")
        return

    console.print(
        f"[yellow]🔄 {amount} {from_token} → {to_token} on {network.upper()}[/yellow]"
    )

    # Get swap quote
    swap_preview = SwapPreview()
    quote = swap_preview.get_swap_quote(from_token, to_token, amount, network)

    if not quote:
        msg = f"[red]❌ Invalid swap: {from_token} or {to_token} not available on {network.upper()}[/red]"
        console.print(msg)
        available_tokens = ", ".join(_get_tokens_for_network(network).keys())
        console.print(
            f"[yellow]Available tokens on {network.upper()}: {available_tokens}[/yellow]"
        )
        return

    # Display swap preview
    _show_swap_preview(quote)

    if preview:
        console.print(
            "[blue]💡 This was a preview only. Remove --preview to execute.[/blue]"
        )
    else:
        # Check balance before confirming
        from .wallet import Wallet

        wallet = Wallet(network)
        token_addresses = _get_tokens_for_network(network)
        from_address = token_addresses.get(from_token.upper())

        if from_address:
            current_balance = wallet.get_balance(from_address)

            # Confirm before executing
            console.print(
                "\n[bold red]⚠️  You are about to execute a real swap![/bold red]"
            )
            console.print(f"Your balance: {current_balance:.6f} {from_token}")
            estimated = quote["estimated_output"]
            console.print(
                f"Swapping: {amount} {from_token} → ~{estimated:.6f} {to_token}"
            )
            console.print(f"Minimum received: {quote['min_output']:.6f} {to_token}")
            console.print(f"Gas cost: ${quote['gas_cost_usd']:.2f}")

            if float(current_balance) < amount:
                needed = amount - float(current_balance)
                console.print(
                    f"[red]❌ Insufficient balance! You need {needed:.6f} more {from_token}[/red]"
                )
                return
        else:
            console.print(
                "\n[bold red]⚠️  You are about to execute a real swap![/bold red]"
            )
            estimated = quote["estimated_output"]
            console.print(
                f"Swapping: {amount} {from_token} → ~{estimated:.6f} {to_token}"
            )
            console.print(f"Minimum received: {quote['min_output']:.6f} {to_token}")
            console.print(f"Gas cost: ${quote['gas_cost_usd']:.2f}")

        confirm = input("\nProceed with swap? (yes/no): ").lower().strip()

        if confirm not in ["yes", "y"]:
            console.print("[yellow]Swap cancelled.[/yellow]")
            return

        # Execute the actual swap
        console.print("[yellow]🔄 Executing swap...[/yellow]")

        # Use mock swap for testnets, real swap for mainnets
        if network == "base-sepolia":
            from .mock_swap import MockSwapExecutor

            executor = MockSwapExecutor(network)
            tx_hash = executor.execute_mock_swap(
                from_token, to_token, amount, quote["min_output"]
            )
        else:
            from .swap_executor import SwapExecutor

            executor = SwapExecutor(network)
            tx_hash = executor.execute_swap(
                from_token, to_token, amount, quote["min_output"]
            )

        if tx_hash:
            explorer_urls = {
                "base": "https://basescan.org/tx/",
                "base-sepolia": "https://sepolia.basescan.org/tx/",
                "ethereum": "https://etherscan.io/tx/",
            }
            explorer_url = explorer_urls.get(network, "")
            console.print(f"[green]✅ Swap executed! Transaction: {tx_hash}[/green]")
            if explorer_url:
                console.print(
                    f"[blue]🔗 View on explorer: {explorer_url}{tx_hash}[/blue]"
                )
        else:
            console.print(
                f"[red]❌ Swap failed! Swapping not supported on {network.upper()} network.[/red]"
            )
            console.print(
                "[yellow]💡 Try Base or Ethereum networks for swapping.[/yellow]"
            )


def _show_swap_preview(quote: dict):
    """Display swap preview in a nice table"""
    table = Table(title="🔄 Swap Preview", show_header=False)
    table.add_column("Field", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("From", f"{quote['from_amount']:.6f} {quote['from_token']}")
    table.add_row(
        "To (Estimated)", f"{quote['estimated_output']:.6f} {quote['to_token']}"
    )
    table.add_row("Minimum Received", f"{quote['min_output']:.6f} {quote['to_token']}")
    table.add_row(
        "Exchange Rate",
        f"1 {quote['from_token']} = {quote['rate']:.6f} {quote['to_token']}",
    )
    table.add_row("Network", quote["network"].upper())
    table.add_row("DEX Fee", f"{quote['fee_percentage']:.1f}%")
    table.add_row("Slippage Tolerance", f"{quote['slippage_percentage']:.1f}%")
    table.add_row("Gas Limit", f"{quote['gas_estimate']:,}")
    table.add_row("Gas Price", f"{quote['gas_price_gwei']:.1f} gwei")
    table.add_row("Gas Cost", f"${quote['gas_cost_usd']:.2f}")
    table.add_row("Quote Source", quote.get("quote_source", "Price API"))

    # Calculate total cost
    total_cost = quote["from_amount"] * quote["from_price"] + quote["gas_cost_usd"]
    table.add_row("[bold]Total Cost[/bold]", f"[bold]${total_cost:.2f}[/bold]")

    console.print(table)


if __name__ == "__main__":
    cli()
