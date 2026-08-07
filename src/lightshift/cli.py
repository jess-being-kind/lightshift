# src/lightshift/cli.py

from __future__ import annotations

import argparse
from collections.abc import Sequence

# parse CLI

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="lumenctl",
        description="Discover & control Lightshift-compatible devices"
    )

    parser.add_argument(
        "--version",
        action="version",
        version="lumenctl 0.1.0"
    )

    return parser

def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    parser.parse_args(argv)

    print("Lumen control online.")
    return 0
