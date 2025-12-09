"""CLI entry point for igcheck."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import click
from dotenv import load_dotenv
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from igcheck.instagram import InstagramClient
from igcheck.output import export_to_csv, export_to_json, print_to_console

load_dotenv()

console = Console()


def get_2fa_code() -> str:
    """Prompt user for 2FA verification code."""
    return click.prompt("Enter your 2FA verification code", type=str)


@click.command()
@click.option(
    "--username",
    "-u",
    envvar="IG_USERNAME",
    help="Instagram username (or set IG_USERNAME env var)",
)
@click.option(
    "--password",
    "-p",
    envvar="IG_PASSWORD",
    help="Instagram password (or set IG_PASSWORD env var)",
)
@click.option(
    "--json",
    "output_json",
    is_flag=True,
    help="Output results as JSON",
)
@click.option(
    "--csv",
    "output_csv",
    is_flag=True,
    help="Output results as CSV",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output file path (defaults to non-followers.json or non-followers.csv)",
)
def main(
    username: str | None,
    password: str | None,
    output_json: bool,
    output_csv: bool,
    output: str | None,
) -> None:
    """Find Instagram accounts you follow that don't follow you back."""
    if not username:
        username = click.prompt("Instagram username")
    if not password:
        password = click.prompt("Instagram password", hide_input=True)

    client = InstagramClient()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        progress.add_task(description="Logging in to Instagram...", total=None)
        try:
            client.login(username, password, verification_code_callback=get_2fa_code)
        except RuntimeError as e:
            console.print(f"[red]Login failed: {e}[/red]")
            sys.exit(1)

        console.print("[green]Logged in successfully![/green]")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        progress.add_task(description="Fetching followers and following...", total=None)
        try:
            non_followers = client.get_non_followers()
        except Exception as e:
            console.print(f"[red]Error fetching data: {e}[/red]")
            sys.exit(1)

    if output_json:
        output_path = Path(output) if output else Path("non-followers.json")
        export_to_json(non_followers, output_path)
        console.print(f"[green]Results exported to {output_path}[/green]")
        print_to_console(non_followers, console)
    elif output_csv:
        output_path = Path(output) if output else Path("non-followers.csv")
        export_to_csv(non_followers, output_path)
        console.print(f"[green]Results exported to {output_path}[/green]")
        print_to_console(non_followers, console)
    else:
        print_to_console(non_followers, console)


if __name__ == "__main__":
    main()
