"""CLI entry point for igcheck."""

from __future__ import annotations

import sys
import time
from pathlib import Path

import click
import questionary
from dotenv import load_dotenv
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from igcheck.instagram import InstagramClient, UserInfo
from igcheck.output import export_to_csv, export_to_json, print_to_console

load_dotenv()

console = Console()


def get_2fa_code() -> str:
    """Prompt user for 2FA verification code."""
    return click.prompt("Enter your 2FA verification code", type=str)


def interactive_unfollow(client: InstagramClient, non_followers: list[UserInfo]) -> None:
    """
    Show interactive checkbox selection for unfollowing users.

    Args:
        client: Authenticated Instagram client
        non_followers: List of users to potentially unfollow
    """
    if not non_followers:
        return

    choices = [
        questionary.Choice(
            title=f"@{user.username} ({user.full_name})" if user.full_name else f"@{user.username}",
            value=user,
        )
        for user in sorted(non_followers, key=lambda u: u.username.lower())
    ]

    console.print("\n[bold]Select accounts to unfollow (Space to select, Enter to confirm):[/bold]")

    selected = questionary.checkbox(
        "Use arrow keys to navigate, Space to select, Enter to confirm:",
        choices=choices,
    ).ask()

    if selected is None:
        console.print("[yellow]Cancelled.[/yellow]")
        return

    if not selected:
        console.print("[yellow]No accounts selected.[/yellow]")
        return

    console.print(f"\n[bold]You selected {len(selected)} account(s) to unfollow:[/bold]")
    for user in selected:
        console.print(f"  - @{user.username}")

    if not questionary.confirm("Are you sure you want to unfollow these accounts?").ask():
        console.print("[yellow]Cancelled.[/yellow]")
        return

    console.print()
    success_count = 0
    fail_count = 0

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        for user in selected:
            progress.add_task(description=f"Unfollowing @{user.username}...", total=None)
            try:
                if client.unfollow_user(user.user_id):
                    console.print(f"[green]Unfollowed @{user.username}[/green]")
                    success_count += 1
                else:
                    console.print(f"[red]Failed to unfollow @{user.username}[/red]")
                    fail_count += 1
            except Exception as e:
                console.print(f"[red]Error unfollowing @{user.username}: {e}[/red]")
                fail_count += 1

            # Rate limiting - wait between unfollows to avoid Instagram blocking
            if user != selected[-1]:
                time.sleep(2)

    console.print(f"\n[bold]Done! Unfollowed {success_count} account(s).[/bold]")
    if fail_count > 0:
        console.print(f"[yellow]Failed to unfollow {fail_count} account(s).[/yellow]")


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
@click.option(
    "--interactive",
    "-i",
    is_flag=True,
    help="Interactively select and unfollow accounts",
)
def main(
    username: str | None,
    password: str | None,
    output_json: bool,
    output_csv: bool,
    output: str | None,
    interactive: bool,
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

    if output_csv:
        output_path = Path(output) if output else Path("non-followers.csv")
        export_to_csv(non_followers, output_path)
        console.print(f"[green]Results exported to {output_path}[/green]")

    print_to_console(non_followers, console)

    if interactive:
        interactive_unfollow(client, non_followers)


if __name__ == "__main__":
    main()
