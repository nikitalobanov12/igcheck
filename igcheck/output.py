"""Output formatting for non-followers data."""

from __future__ import annotations

import csv
import json
from dataclasses import asdict
from pathlib import Path
from typing import TYPE_CHECKING

from rich.console import Console
from rich.table import Table

if TYPE_CHECKING:
    from igcheck.instagram import UserInfo


def print_to_console(users: list[UserInfo], console: Console | None = None) -> None:
    """
    Print non-followers to console with rich formatting.

    Args:
        users: List of UserInfo objects
        console: Optional Rich console instance
    """
    if console is None:
        console = Console()

    if not users:
        console.print("[green]Everyone you follow follows you back![/green]")
        return

    console.print(f"\n[bold]Found {len(users)} account(s) that don't follow you back:[/bold]\n")

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Username", style="yellow")
    table.add_column("Full Name")
    table.add_column("Profile URL", style="blue")

    for user in sorted(users, key=lambda u: u.username.lower()):
        table.add_row(user.username, user.full_name, user.profile_url)

    console.print(table)
    console.print()


def export_to_json(users: list[UserInfo], output_path: Path) -> None:
    """
    Export non-followers to JSON file.

    Args:
        users: List of UserInfo objects
        output_path: Path to output file
    """
    data = [asdict(user) for user in sorted(users, key=lambda u: u.username.lower())]
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def export_to_csv(users: list[UserInfo], output_path: Path) -> None:
    """
    Export non-followers to CSV file.

    Args:
        users: List of UserInfo objects
        output_path: Path to output file
    """
    fieldnames = ["username", "full_name", "profile_url", "user_id"]
    sorted_users = sorted(users, key=lambda u: u.username.lower())

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for user in sorted_users:
            writer.writerow(asdict(user))
