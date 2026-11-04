"""Lets `python -m bearing` run the command line."""

import sys

from bearing.cli import main

if __name__ == "__main__":
    sys.exit(main())
