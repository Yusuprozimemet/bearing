"""The command line: --version, and the ingest subcommand that stores a repository's history and PRs."""

import argparse
import sys

from bearing import __version__
from bearing.ingest.history import GitError, read_first_parent
from bearing.ingest.mapping import format_report, load_prs, map_history
from bearing.store.db import open_store, save


def _fail(message: str) -> int:
    print(f"bearing: {message}", file=sys.stderr)
    return 1


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="bearing")
    parser.add_argument("--version", action="version", version=f"bearing {__version__}")
    subparsers = parser.add_subparsers(dest="command")
    ingest = subparsers.add_parser(
        "ingest", help="store a repository's history and PRs"
    )
    ingest.add_argument("repo")
    ingest.add_argument("--prs", required=True)
    ingest.add_argument("--data", default=".bearing")
    args = parser.parse_args(argv)
    if args.command != "ingest":
        return 0

    # Read git and the PR file before the store is opened, so an error leaves no store behind.
    try:
        commits = read_first_parent(args.repo)
    except GitError as exc:
        return _fail(str(exc) or f"not a git repository: {args.repo}")
    except OSError as exc:
        return _fail(f"cannot run git in {args.repo}: {exc.strerror or exc}")
    try:
        records = load_prs(args.prs)
    except FileNotFoundError as exc:
        return _fail(f"cannot read {args.prs}: {exc.strerror}")
    except (OSError, ValueError) as exc:
        return _fail(str(exc))

    result = map_history(commits, records)
    conn = open_store(args.data)
    save(conn, commits, records, result)
    conn.close()
    for line in format_report(result):
        sys.stdout.write(f"{line}\n")
    return 0
