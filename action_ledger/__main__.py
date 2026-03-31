"""Standalone CLI entry point for the action ledger.

Usage:
    python -m action_ledger record --session S42 --verb explored --target fieldwork
    python -m action_ledger show [--session S42] [--verb explored]
    python -m action_ledger sequence show [--session S42]
    python -m action_ledger sequence close --session S42 [--outcome "..."]
    python -m action_ledger sequence intent --session S42 "the intent"
    python -m action_ledger params
"""

from __future__ import annotations

import argparse
import sys

from action_ledger.cli import register_ledger_commands


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="action_ledger",
        description="Action Ledger — system-wide process recording",
    )
    subparsers = parser.add_subparsers(dest="command")

    register_ledger_commands(subparsers, prefix="")

    args = parser.parse_args(argv)
    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
