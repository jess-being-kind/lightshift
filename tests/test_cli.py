# tests/test_cli.py

from lightshift.cli import main

def test_main_returns_success() -> None:
    assert main([]) == 0
