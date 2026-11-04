"""The command line: --version, ingest (stores a repository's history and PRs) and changelog (prints it)."""

import argparse
import datetime
import sqlite3
import sys
from pathlib import Path

from bearing import __version__
from bearing.ingest.changelog import format_changelog, read_entries
from bearing.ingest.history import GitError, read_first_parent
from bearing.ingest.mapping import format_report, load_prs, map_history
from bearing.store.db import open_store, save


def _fail(message: str) -> int:
    print(f"bearing: {message}", file=sys.stderr)
    return 1


def _changelog(args) -> int:
    # Never creates the store: a missing file is an error, not an empty changelog.
    db = Path(args.data) / "bearing.db"
    if not db.is_file():
        return _fail(f"no store at {db}: run bearing ingest first")
    conn = sqlite3.connect(db)
    try:
        entries = read_entries(conn)
    except sqlite3.Error as exc:
        return _fail(f"cannot read store at {db}: {exc}")
    finally:
        conn.close()
    for line in format_changelog(entries, since=args.since, until=args.until):
        sys.stdout.write(f"{line}\n")
    return 0


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
    changelog = subparsers.add_parser(
        "changelog", help="print the changelog from a stored history"
    )
    changelog.add_argument("--since", type=datetime.date.fromisoformat, default=None)
    changelog.add_argument("--until", type=datetime.date.fromisoformat, default=None)
    changelog.add_argument("--data", default=".bearing")
    args = parser.parse_args(argv)
    # Output is UTF-8 whatever the console's code page; a stream without reconfigure (a test's
    # StringIO) is left as it is. Parsing comes first, so --version never touches the stream.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if args.command == "changelog":
        return _changelog(args)
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
    try:
        conn = open_store(args.data)
        save(conn, commits, records, result)
        conn.close()
    except (OSError, sqlite3.Error) as exc:
        return _fail(f"cannot open store at {args.data}: {exc}")
    for line in format_report(result):
        sys.stdout.write(f"{line}\n")
    return 0
