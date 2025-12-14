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

    # Get pre-configured tokens for this network
    tokens_to_check = _get_tokens_for_network(network)

    # Discover additional tokens from transaction history
    discovered_tokens = {}
    try:
        from .transaction_history import TransactionHistory

        tx_history = TransactionHistory(network)
        discovered_tokens = tx_history.discover_user_tokens(wallet.address)
        if len(discovered_tokens) > 0:
            console.print(
                f"[dim]🔍 Discovered {len(discovered_tokens)} additional tokens from transaction history[/dim]"
            )
    except Exception as e:
        console.print(f"[dim]⚠️ Token discovery failed: {e}[/dim]")

    # Combine pre-configured and discovered tokens (pre-configured takes priority)
    all_tokens = {**discovered_tokens, **tokens_to_check}

    # Track which tokens are discovered vs pre-configured
    total_value = 0.0

    for token_name, token_address in all_tokens.items():
        balance = wallet.get_balance(token_address)
        # Show tokens with balance > 0, or discovered tokens (to show full discovery results)
        show_token = balance > 0 or (
            token_name in discovered_tokens and token_name not in tokens_to_check
        )
        if show_token:
            price = price_fetcher.get_token_price(token_name)

            # Mark discovered tokens with an asterisk
            display_name = token_name
            if token_name in discovered_tokens and token_name not in tokens_to_check:
                display_name = f"{token_name}*"

            if price:
                value = float(balance) * price
                total_value += value
                price_str = f"${price:.6f}" if price < 0.01 else f"${price:.2f}"
                value_str = f"${value:.2f}" if balance > 0 else "N/A"
                table.add_row(display_name, f"{balance:.6f}", price_str, value_str)
            else:
                # Show N/A for price but still show balance
                price_str = "N/A"
                value_str = "N/A"
                table.add_row(display_name, f"{balance:.6f}", price_str, value_str)

    console.print(table)

    # Show total value if we have any
    if total_value > 0:
        console.print(f"\n[bold green]💰 Total Value: ${total_value:.2f}[/bold green]")

    # Show legend for discovered tokens
    has_discovered = any(
        token in discovered_tokens and token not in tokens_to_check
        for token in all_tokens.keys()
    )
    if has_discovered:
        console.print("\n[dim]* = Discovered from transaction history[/dim]")

    # Show helpful tips
    if len(discovered_tokens) > 0:
        console.print(
            f"\n[green]✅ Automatically discovered {len(discovered_tokens)} tokens from your transaction history![/green]"
        )
    else:
        if network in ["base", "base-sepolia"]:
            console.print(
                f"\n[yellow]💡 Token discovery limited on {network.upper()} (requires paid Etherscan plan)[/yellow]"
            )
            console.print(
                f"[dim]   Use 'python main.py history --network {network}' to see all your tokens[/dim]"
            )
        else:
            console.print(
                "\n[yellow]💡 Tip: Make some transactions to enable automatic token discovery[/yellow]"
            )


@cli.command()
@click.option(
    "--network", default="base", help="Network: base, ethereum, celo, base-sepolia"
)
@click.option(
    "--limit", default=20, help="Number of transactions to show (default: 20)"
)
@click.option(
    "--type", "tx_type", help="Filter by type: send, receive, all (default: all)"
)
@click.option("--summary", is_flag=True, help="Show transaction summary statistics")
def history(network, limit, tx_type, summary):
    """View transaction history for your wallet

    Supported networks (with Etherscan API key):
      • ethereum, celo - Free tier supported
      • base, base-sepolia - Requires paid Etherscan plan

    Examples:
      history --network ethereum --limit 10
      history --network celo --type send
      history --summary
    """
    from .transaction_history import TransactionHistory

    try:
        # Initialize wallet to get address
        wallet = Wallet(network)
        if not wallet.is_connected():
            console.print("[red]❌ Failed to connect to network[/red]")
            return

        console.print(
            f"[yellow]📜 Fetching transaction history for {network.upper()}...[/yellow]"
        )
        console.print(f"[blue]Address: {wallet.address}[/blue]")

        # Get transaction history
        tx_history = TransactionHistory(network)

        if summary:
            # Show summary statistics
            stats = tx_history.get_transaction_summary(wallet.address)
            _show_transaction_summary(stats, network)

            # Check for significant discrepancy between balance and transaction history
            try:
                from .price_fetcher import PriceFetcher
                from .config import NETWORKS

                price_fetcher = PriceFetcher()

                # Get current native token balance and price
                native_token = NETWORKS[network].native_token
                current_balance = wallet.get_balance()  # Native token balance
                token_price = price_fetcher.get_token_price(native_token)

                if current_balance > 0 and token_price:
                    # Convert balance to float for calculations (it's returned as Decimal)
                    current_value = float(current_balance) * token_price
                    tx_net_value = stats["net_flow_usd"]

                    # If current balance is significantly higher than transaction net flow
                    missing_value = current_value - tx_net_value
                    missing_percentage = (
                        (missing_value / current_value) * 100
                        if current_value > 0
                        else 0
                    )

                    # Show warning if either: large dollar amount ($1+) OR high percentage (50%+) missing
                    significant_amount = missing_value > 1.0
                    high_percentage = missing_percentage > 50.0

                    if (
                        significant_amount or high_percentage
                    ) and current_value > 0.10:  # Min $0.10 balance
                        console.print("\n[yellow]⚠️  Historical Data Notice:[/yellow]")
                        console.print(
                            f"[yellow]   Current {native_token} balance: ${current_value:.2f}[/yellow]"
                        )
                        console.print(
                            f"[yellow]   Transaction history net: ${tx_net_value:.2f}[/yellow]"
                        )
                        console.print(
                            f"[yellow]   Missing from history: ~${missing_value:.2f} ({missing_percentage:.0f}%)[/yellow]"
                        )
                        console.print(
                            "[dim]   This suggests older transactions are not included in the API response[/dim]"
                        )
            except Exception:
                pass  # Don't fail if balance check fails
        else:
            # Show transaction list
            transactions = tx_history.get_transaction_history(wallet.address, limit)

            # Filter by type if specified
            if tx_type and tx_type.lower() in ["send", "receive"]:
                filter_type = tx_type.capitalize()
                transactions = [tx for tx in transactions if tx["type"] == filter_type]

            if not transactions:
                console.print("[yellow]No transactions found.[/yellow]")
                return

            _show_transaction_history(transactions, network)

    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")


def _show_transaction_summary(stats: dict, network: str):
    """Display transaction summary statistics"""
    table = Table(title=f"📊 Recent Transaction Summary - {network.upper()}")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Total Transactions", str(stats["total_transactions"]))
    table.add_row("Total Sent", f"${stats['total_sent_usd']:.2f}")
    table.add_row("Total Received", f"${stats['total_received_usd']:.2f}")
    table.add_row("Gas Fees Paid", f"${stats['total_gas_spent_usd']:.2f}")

    net_flow = stats["net_flow_usd"]
    net_color = "green" if net_flow >= 0 else "red"
    net_symbol = "+" if net_flow >= 0 else ""
    table.add_row("Net Flow", f"[{net_color}]{net_symbol}${net_flow:.2f}[/{net_color}]")

    console.print(table)

    # Add important disclaimer about historical data limitations
    console.print(
        f"\n[yellow]💡 Summary shows recent transaction flow (last {stats['total_transactions']} transactions)[/yellow]"
    )
    console.print(
        "[yellow]   Older transactions may not be included due to API limitations[/yellow]"
    )
    console.print("[dim]Use 'balance' command to see current total holdings[/dim]")


def _show_transaction_history(transactions: list, network: str):
    """Display transaction history in a table"""
    table = Table(title=f"📜 Transaction History - {network.upper()}")
    table.add_column("Date", style="blue")
    table.add_column("Type", style="cyan")
    table.add_column("Token", style="yellow")
    table.add_column("Amount", style="green")
    table.add_column("USD Value", style="magenta")
    table.add_column("From/To", style="white")
    table.add_column("Status", style="green")

    for tx in transactions:
        # Format amount
        if tx["amount"] < 0.000001:
            amount_str = f"{tx['amount']:.8f}"
        elif tx["amount"] < 0.01:
            amount_str = f"{tx['amount']:.6f}"
        else:
            amount_str = f"{tx['amount']:.4f}"

        # Format USD value
        usd_str = f"${tx['usd_value']:.2f}" if tx["usd_value"] > 0 else "N/A"

        # Format address (show counterparty)
        if tx["type"] == "Send":
            address_str = f"→ {tx['to'][:6]}...{tx['to'][-4:]}"
            type_color = "red"
        else:
            address_str = f"← {tx['from'][:6]}...{tx['from'][-4:]}"
            type_color = "green"

        # Status color
        status_color = "green" if tx["status"] == "Success" else "red"

        table.add_row(
            tx["date"],
            f"[{type_color}]{tx['type']}[/{type_color}]",
            tx["token"],
            amount_str,
            usd_str,
            address_str,
            f"[{status_color}]{tx['status']}[/{status_color}]",
        )

    console.print(table)

    # Show explorer links
    explorer_urls = {
        "base": "https://basescan.org/address/",
        "base-sepolia": "https://sepolia.basescan.org/address/",
        "ethereum": "https://etherscan.io/address/",
        "celo": "https://celoscan.io/address/",
    }

    if network in explorer_urls:
        wallet = Wallet(network)
        explorer_url = explorer_urls[network] + wallet.address
        console.print(f"\n[blue]🔗 View full history: {explorer_url}[/blue]")


@cli.command()
@click.option(
    "--network", default="base", help="Network: base, ethereum, celo, base-sepolia"
)
def discover(network):
    """Discover tokens from your transaction history

    This command scans your transaction history to find all tokens
    you've interacted with and shows their contract addresses.

    Examples:
      discover --network base
      discover --network ethereum
    """
    from .transaction_history import TransactionHistory

    try:
        # Initialize wallet to get address
        wallet = Wallet(network)
        if not wallet.is_connected():
            console.print("[red]❌ Failed to connect to network[/red]")
            return

        console.print(
            f"[yellow]🔍 Discovering tokens from {network.upper()} transaction history...[/yellow]"
        )
        console.print(f"[blue]Address: {wallet.address}[/blue]")

        # Discover tokens
        tx_history = TransactionHistory(network)
        discovered_tokens = tx_history.discover_user_tokens(wallet.address)

        if not discovered_tokens:
            if network in ["base", "base-sepolia"]:
                console.print(
                    "[yellow]Token discovery temporarily unavailable (API inconsistency).[/yellow]"
                )
                console.print(
                    "[dim]💡 Try running the command again, or use 'history' to see your tokens[/dim]"
                )
            else:
                console.print(
                    "[yellow]No tokens found in transaction history.[/yellow]"
                )
                console.print(
                    "[dim]💡 Make some token transactions to enable discovery[/dim]"
                )
            return

        # Create discovery table
        table = Table(title=f"🔍 Discovered Tokens - {network.upper()}")
        table.add_column("Token Symbol", style="cyan")
        table.add_column("Contract Address", style="green")
        table.add_column("Balance", style="yellow")
        table.add_column("Status", style="magenta")

        for token_symbol, token_address in discovered_tokens.items():
            # Check current balance
            balance = wallet.get_balance(token_address)

            # Check if it's in pre-configured tokens
            preconfigured_tokens = _get_tokens_for_network(network)
            status = (
                "✅ Pre-configured"
                if token_symbol in preconfigured_tokens
                else "🆕 Discovered"
            )

            balance_str = f"{balance:.6f}" if balance > 0 else "0"

            table.add_row(token_symbol, token_address, balance_str, status)

        console.print(table)
        console.print(
            f"\n[green]✅ Found {len(discovered_tokens)} unique tokens in your transaction history![/green]"
        )
        console.print(
            "[dim]💡 These tokens will automatically appear in your balance command[/dim]"
        )

    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")


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
    """Send tokens to an address

    Examples:
      send 0.01 ETH to 0x1234...5678 --network base-sepolia --preview
      send 10 USDC to 0x1234...5678 --network base
    """

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
        msg = (
            f"[red]❌ Insufficient balance! "
            f"You have {current_balance:.6f} {token}, need {amount}[/red]"
        )
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
            from .notifications import NotificationManager

            notifier = NotificationManager()
            notifier.notify_transaction_success("Transfer", f"{amount}", token, tx_hash)

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
            from .notifications import NotificationManager

            notifier = NotificationManager()
            notifier.notify_transaction_failed(
                "Transfer", f"{amount}", token, "Transaction failed"
            )
            console.print("[red]❌ Transfer failed![/red]")

    except Exception as e:
        from .notifications import NotificationManager

        notifier = NotificationManager()
        notifier.notify_transaction_failed("Transfer", f"{amount}", token, str(e))
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
    """Swap tokens with natural syntax

    Examples:
      swap 0.1 ETH to USDC --preview
      swap 10 CELO to G$ --network celo --preview
      swap 0.01 ETH to USDC --network base-sepolia (mock)
    """
    from .swap_preview import SwapPreview

    # Validate 'to' keyword
    if to_keyword.lower() != "to":
        console.print(
            "[red]❌ Invalid syntax. Use: swap <amount> <from_token> to <to_token>[/red]"
        )
        console.print("[yellow]Example: swap 10 CELO to G$[/yellow]")
        return

    console.print(
        f"[yellow]🔄 {amount} {from_token} → {to_token} on {network.upper()}[/yellow]"
    )

    # Get swap quote
    swap_preview = SwapPreview()
    quote = swap_preview.get_swap_quote(from_token, to_token, amount, network)

    if not quote:
        msg = (
            f"[red]❌ Invalid swap: {from_token} or {to_token} "
            f"not available on {network.upper()}[/red]"
        )
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
            from .notifications import NotificationManager

            notifier = NotificationManager()
            estimated = quote["estimated_output"]
            notifier.notify_swap_success(
                f"{amount}", from_token, f"{estimated:.6f}", to_token, tx_hash
            )

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
            from .notifications import NotificationManager

            notifier = NotificationManager()
            notifier.notify_swap_failed(
                f"{amount}", from_token, to_token, "Swapping not supported on network"
            )
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
