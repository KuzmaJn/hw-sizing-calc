import argparse
import sys

from rich.console import Console
from rich.table import Table

from sizing.config_loader import load_config
from sizing.calculator import calculate_hardware


def parse_args():
    parser = argparse.ArgumentParser(
        description="Estimate CPU / RAM / disk requirements for a given transaction load."
    )
    parser.add_argument(
        "--transactions", "-n", type=int, required=True,
        help="Number of transactions PER DAY."
    )
    parser.add_argument(
        "--type", "-t", type=str, required=True,
        help="Transaction type (must exist in the chosen profile config)."
    )
    parser.add_argument(
        "--profile", "-p", type=str, default="config/generic.yaml",
        help="Path to a profile config file (default: config/generic.yaml)."
    )
    return parser.parse_args()


def main():
    args = parse_args()
    console = Console()

    profiles, defaults = load_config(args.profile)

    if args.type not in profiles:
        console.print(f"[red]Unknown transaction type '{args.type}'.[/red]")
        console.print(f"Available types in {args.profile}: {', '.join(profiles.keys())}")
        sys.exit(1)

    result = calculate_hardware(
        num_transactions=args.transactions,
        tx_profile=profiles[args.type],
        defaults=defaults,
    )

    table = Table(title="Hardware Sizing Estimate")
    table.add_column("Resource")
    table.add_column("Requirement", justify="right")
    table.add_row("CPU cores", str(result.cpu_cores))
    table.add_row("RAM", f"{result.ram_gb} GB")
    table.add_row("Disk", f"{result.disk_gb} GB")
    console.print(table)

    console.print("\n[bold]Assumptions used:[/bold]")
    for key, value in result.assumptions.items():
        console.print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
