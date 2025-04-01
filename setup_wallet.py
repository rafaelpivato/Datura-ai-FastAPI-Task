#!/usr/bin/env python3

import argparse
import sys
from typing import Optional

import bittensor
from rich.console import Console

# Default values
DEFAULT_HOTKEY = "5FFApaS75bv5pJHfAp2FVLBj9ZaXuFDjEypsaBNc1wCfe52v"
DEFAULT_NETUID = 18
DEFAULT_MNEMONIC = (
    "diamond like interest affair safe clarify lawsuit innocent beef van grief color"
)

console = Console()


def check_wallet(wallet_name: str) -> bool:
    """Check if specified wallet exists with both coldkey and hotkey."""
    try:
        console.print(f"[green]Checking {wallet_name} wallet[/green]")
        if wallet_name == "default":
            console.print("[yellow]You may be asked for your wallet password.[/yellow]")
        wallet = bittensor.wallet(name=wallet_name)
        has_coldkey = wallet.coldkeypub_file.exists_on_device()
        has_hotkey = wallet.hotkey_file.exists_on_device()

        if not has_coldkey:
            console.print(f"[yellow]{wallet_name} wallet missing coldkey[/yellow]")
            return False
        if not has_hotkey:
            console.print(f"[yellow]{wallet_name} wallet missing hotkey[/yellow]")
            return False

        return True
    except Exception as e:
        console.print(f"[red]Error checking {wallet_name} wallet: {e}[/red]")
        return False


def get_wallet_address(wallet_name: str) -> Optional[str]:
    """Get wallet SS58 address."""
    try:
        wallet = bittensor.wallet(name=wallet_name)
        if wallet.coldkeypub_file.exists_on_device():
            return wallet.coldkeypub.ss58_address
        return None
    except Exception as e:
        console.print(f"[red]Error getting {wallet_name} wallet address: {e}[/red]")
        return None


def create_default_wallet() -> bool:
    """Create new default wallet with coldkey and hotkey."""
    try:
        wallet = bittensor.wallet(name="default")

        # Create coldkey
        wallet.create_new_coldkey(use_password=False)
        console.print("[green]Created new coldkey for default wallet[/green]")

        # Create hotkey
        wallet.create_new_hotkey(use_password=False)
        console.print("[green]Created new hotkey for default wallet[/green]")

        return True
    except Exception as e:
        console.print(f"[red]Error creating default wallet: {e}[/red]")
        return False


def setup_datura_wallet() -> bool:
    """Create datura wallet using predefined mnemonic for coldkey."""
    try:
        wallet = bittensor.wallet(name="datura")

        # Regenerate coldkey with mnemonic
        wallet.regenerate_coldkey(mnemonic=DEFAULT_MNEMONIC, use_password=False)
        console.print("[green]Created datura wallet with predefined coldkey[/green]")

        # Create hotkey
        wallet.create_new_hotkey(use_password=False)
        console.print("[green]Added new hotkey to datura wallet[/green]")

        return True
    except Exception as e:
        console.print(f"[red]Error setting up datura wallet: {e}[/red]")
        return False


def transfer_tao(dest_address: str, amount: float) -> bool:
    """Transfer TAO from default wallet to destination address."""
    try:
        wallet = bittensor.wallet(name="datura")
        subtensor = bittensor.subtensor(network="test")

        # Check balance before transfer
        balance = subtensor.get_balance(wallet.coldkeypub.ss58_address)
        if balance < amount:
            console.print(
                f"[red]Insufficient balance in default wallet: {balance} TAO[/red]"
            )
            return False

        # Perform transfer
        success = subtensor.transfer(
            wallet=wallet,
            dest=dest_address,
            amount=bittensor.Balance.from_float(amount),
        )

        if success:
            console.print(
                f"[green]Successfully transferred {amount} TAO to {dest_address}[/green]"
            )
            return True
        else:
            console.print("[red]Transfer failed[/red]")
            return False

    except Exception as e:
        console.print(f"[red]Error during transfer: {e}[/red]")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Setup wallet with shared hotkey and optional TAO transfer"
    )
    parser.add_argument("--transfer", type=float, help="Amount of TAO to transfer")
    parser.add_argument("--dest", type=str, help="Destination address for transfer")
    args = parser.parse_args()

    # Create default wallet if it doesn't exist
    if not check_wallet("default"):
        console.print("Creating new default wallet...")
        if not create_default_wallet():
            console.print("[red]Failed to create default wallet[/red]")
            sys.exit(1)

    # Setup datura wallet if it doesn't exist
    if not check_wallet("datura"):
        console.print("Creating new datura wallet...")
        if not setup_datura_wallet():
            console.print("[red]Failed to setup datura wallet[/red]")
            sys.exit(1)
    else:
        console.print("[green]Datura wallet already exists[/green]")

    # Handle optional transfer
    if args.transfer is not None:
        if args.dest is None:
            console.print("[red]Destination address required for transfer[/red]")
            sys.exit(1)
        if not transfer_tao(args.dest, args.transfer):
            sys.exit(1)

    console.print(
        "\n[green]Setup complete! Check your wallet with: btcli wallet overview --wallet.name default[/green]"
    )


if __name__ == "__main__":
    main()
