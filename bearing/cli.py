"""The command line. For now it only answers --version; there are no subcommands yet."""

import argparse

from bearing import __version__


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="bearing")
    parser.add_argument("--version", action="version", version=f"bearing {__version__}")
    parser.parse_args(argv)
    return 0
