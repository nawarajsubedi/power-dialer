"""
application cli
"""
from __future__ import annotations

import fire  # type: ignore

from salesapi.console import CliCommand as SalesApiCommand


class Command:
    def __init__(self):
        self.salesapi = SalesApiCommand()


def main():
    fire.Fire(Command)
