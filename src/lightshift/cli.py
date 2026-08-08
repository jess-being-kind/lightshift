# src/lightshift/cli.py


from __future__ import annotations

import argparse
from collections.abc import Sequence
from enum import IntEnum
import logging
import datetime
from dataclasses import dataclass
import time
from typing import
from pathlib import Path

# ======================================================================================
# ▶▶▶ S0. Dependency utilities, globals, logger
# ======================================================================================

log = logging.getLogger(__name__)
separator = "\u27E1"

def utc_now() -> str:
    time_now = datetime.datetime.now(datetime.UTC).strftime("%d_%m_%y__%H_%M_%S_UTC")
    return time_now

def ensure_directory(path: Path) -> int:
    if path.exists():
        log.info(f"Path {path} already exists - skipping mkdir")
        return 1
    else:
        log.info(f"Path {path} does not exist - creating directory")
        path.mkdir(parents=True, exist_ok=True)
        return 0

def ensure_file(file: Path, config: Config) -> Path:

    ensure_directory(file.parent)

    if file.exists():
        log.info(f"File {file} already exists")
        if config.force:
            log.info(f"--force selected - overwriting file {file}")
            file.rename(file.name + ".bak" + RUN_ID)
            file.touch(exist_ok=False)
            return file
        else:
            log.info("skipping create file - use --force to backup & overwrite")
    else:
        log.info(f"Creating file {file}:")
        file.touch(exist_ok=True)
    return file

# ======================================================================================
# ▶▶▶ S1. Metadata, classes
# ======================================================================================

# script metadata
TIME_START_S = str(time.time())
RUN_ID = utc_now()
AUTHOR = "V Halcyon"
VERSION = "v0_1_0"
DIR_OUTPUT = Path("output")

@dataclass(frozen=True)
class Metadata:
    start_time: str = TIME_START_S
    run_id: str = RUN_ID
    author: str = AUTHOR
    version: str = VERSION
    dir_output: Path = DIR_OUTPUT

@dataclass(frozen=True)
class Config:
    version: str
    verbose: bool | None
    quiet: bool | None
    apply: bool = False
    force: bool = False

class ConsoleLevel(IntEnum):
    QUIET = logging.CRITICAL
    VERBOSE = logging.DEBUG
    NOMINAL = logging.INFO
    ERROR = logging.ERROR

# ======================================================================================
# ▶▶▶ S2. Parse CLI
# ======================================================================================

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

    parser.add_argument(
            "--force",
            action="store_true",
            default=False,
        )

    parser.add_argument(
            "--verbose",
            action="store_true",
            default=False,
        )

    parser.add_argument(
            "--quiet",
            action="store_true",
            default=False
        )

    parser.add_argument(
        "--apply",
        action="store_true",
        default=False,
    )

    return parser

# ======================================================================================
# ▶▶▶ S3. Setup logging
# ======================================================================================

def setup_logging(config: Config) -> logging.Logger:
    if config.verbose:
        console_level = ConsoleLevel.VERBOSE
    elif config.quiet:
        console_level = ConsoleLevel.QUIET
    else:
        console_level = ConsoleLevel.NOMINAL

    ensure_directory(DIR_OUTPUT)

    log_file = DIR_OUTPUT / f"lightshift_{VERSION}_{RUN_ID}.log"

    log_format = (
        "%(asctime)s ⟡ "
        "%(levelname)-7s ⟡ "
        "%(name)s ⟡ "
        "%(message)s"
    )

    formatter = logging.Formatter(
        log_format,
        datefmt="%H:%M:%S",
    )

    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_handler.setFormatter(formatter)

    file_handler = logging.FileHandler(
        log_file,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    root_log = logging.getLogger()
    root_log.setLevel(logging.DEBUG)

    root_log.addHandler(console_handler)
    root_log.addHandler(file_handler)

    log.debug(f"Logging initialized @ level: {console_level.name}")

    return root_log

# ======================================================================================
# ▶▶▶ S4. Build run-time config
# ======================================================================================

def build_config(args: argparse.Namespace) -> Config:
    print("building config")
    built_config = Config(
        version=VERSION,
        verbose=args.verbose,
        quiet=args.quiet,
        apply=args.apply,
        force=args.force,
        )
    return built_config

# ======================================================================================
# ▶▶▶ S5. Main - lumenctl entry-point
# ======================================================================================

def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    config = build_config(args)
    log = setup_logging(config)

    log.info("Lumen control online @: " + utc_now())


    # lumenctl entry point

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
