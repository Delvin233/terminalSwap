import click
from rich.console import Console
from rich.table import Table
from .wallet import Wallet

# from .config import BASE_TOKENS  # TODO: Use this later
from .price_fetcher import PriceFetcher

console = Console()


@click.group()
def cli():
    """Terminal-based crypto swapping tool"""
    pass


@cli.command()
@click.option("--network", default="base", help="Network to use (base, ethereum, celo)")
@click.option("--all", is_flag=True, help="Check balances on all networks")
def balance(network, all):
    """Check wallet balance"""
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
@click.argument("from_token")
@click.argument("to_keyword")
@click.argument("to_token")
@click.option("--network", default="base", help="Network to use")
@click.option("--preview", is_flag=True, help="Show swap preview only")
def swap(amount, from_token, to_keyword, to_token, network, preview):
    """Swap tokens with natural syntax\n\n    \b\n    Examples:\n      swap 0.1 ETH to USDC --preview\n      swap 10 CELO to G$ --network celo --preview\n      swap 100 USDC to USDT --network ethereum\n"""
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
        console.print(
            f"[red]❌ Invalid swap: {from_token} or {to_token} not available on {network.upper()}[/red]"
        )
        console.print(
            f"[yellow]Available tokens on {network.upper()}: {', '.join(_get_tokens_for_network(network).keys())}[/yellow]"
        )
        return

    # Display swap preview
    _show_swap_preview(quote)

    if preview:
        console.print(
            "[blue]💡 This was a preview only. Remove --preview to execute.[/blue]"
        )
    else:
        console.print("[red]⚠️  Actual swap execution coming soon![/red]")


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
