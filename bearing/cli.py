"""The command line: --version, ingest (stores a repository's history and PRs), changelog (prints it), snapshot (prints a repository's modules and imports at one commit), timeline (prints what each merge changed in the structure) and direction (prints churn by area and week, the files that change together, and said vs done)."""

import argparse
import datetime
import json
import sqlite3
import sys
from pathlib import Path

from bearing import __version__
from bearing.direction.config import ConfigError, load_config, load_rules
from bearing.direction.report import direction_report
from bearing.ingest.changelog import format_changelog, read_entries
from bearing.ingest.gh import GhError, fetch_prs
from bearing.ingest.history import GitError, read_first_parent
from bearing.ingest.mapping import format_report, load_prs, map_history
from bearing.snapshot.cache import BlobCache
from bearing.snapshot.timeline import timeline
from bearing.snapshot.tree import SnapshotError, snapshot
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


def _snapshot(args) -> int:
    try:
        snap = snapshot(args.repo, args.ref)
    except SnapshotError as exc:
        return _fail(str(exc))
    sys.stdout.write(json.dumps(snap, sort_keys=True, indent=2) + "\n")
    return 0


def _timeline(args) -> int:
    # Never creates the store, as changelog: a missing file is an error.
    db = Path(args.data) / "bearing.db"
    if not db.is_file():
        return _fail(f"no store at {db}: run bearing ingest first")
    conn = None
    try:
        conn = open_store(args.data)  # applies 002_blobs.sql to a Day 5 store
        cache = BlobCache(conn)
        # All lines are computed before any is printed, so an error prints nothing on stdout.
        lines = timeline(args.repo, conn, cache)
        for line in lines:
            sys.stdout.write(f"{line}\n")
        conn.commit()
    except SnapshotError as exc:
        return _fail(str(exc))
    except sqlite3.Error as exc:
        return _fail(f"cannot read store at {db}: {exc}")
    finally:
        if conn is not None:
            conn.close()
    if args.stats:
        print(f"blobs parsed {cache.parsed}  cache hits {cache.hits}", file=sys.stderr)
    return 0


def _direction(args) -> int:
    # The config is read first, so a missing or broken one is an error whatever the store holds.
    # Its rules are read too, so a misspelt rule fails here and not after the report starts.
    try:
        areas, min_prs = load_config(args.config)
        rules = load_rules(args.config)
    except ConfigError as exc:
        return _fail(str(exc))
    # Never creates the store, as timeline: a missing file is an error.
    db = Path(args.data) / "bearing.db"
    if not db.is_file():
        return _fail(f"no store at {db}: run bearing ingest first")
    conn = None
    try:
        conn = sqlite3.connect(db)
        # All lines are computed before any is printed, so an error prints nothing on stdout.
        lines = direction_report(args.repo, conn, areas, min_prs, rules)
    except SnapshotError as exc:
        return _fail(str(exc))
    except sqlite3.Error as exc:
        return _fail(f"cannot read store at {db}: {exc}")
    finally:
        if conn is not None:
            conn.close()
    for line in lines:
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
    ingest.add_argument("--prs", default=None)
    ingest.add_argument("--data", default=".bearing")
    changelog = subparsers.add_parser(
        "changelog", help="print the changelog from a stored history"
    )
    changelog.add_argument("--since", type=datetime.date.fromisoformat, default=None)
    changelog.add_argument("--until", type=datetime.date.fromisoformat, default=None)
    changelog.add_argument("--data", default=".bearing")
    snap = subparsers.add_parser(
        "snapshot", help="print the modules and imports of a repository at one commit"
    )
    snap.add_argument("repo")
    snap.add_argument("ref")
    tl = subparsers.add_parser(
        "timeline", help="print what each merge changed in the structure"
    )
    tl.add_argument("repo")
    tl.add_argument("--data", default=".bearing")
    tl.add_argument("--stats", action="store_true")
    direction = subparsers.add_parser(
        "direction",
        help="print churn by area and week and the files that change together",
    )
    direction.add_argument("repo")
    direction.add_argument("--data", default=".bearing")
    direction.add_argument("--config", default="bearing.toml")
    args = parser.parse_args(argv)
    # Output is UTF-8 whatever the console's code page; a stream without reconfigure (a test's
    # StringIO) is left as it is. Parsing comes first, so --version never touches the stream.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if args.command == "changelog":
        return _changelog(args)
    if args.command == "snapshot":
        return _snapshot(args)
    if args.command == "timeline":
        return _timeline(args)
    if args.command == "direction":
        return _direction(args)
    if args.command != "ingest":
        return 0

    # Read git and the PR records (file or gh) before the store is opened, so an error leaves
    # no store behind.
    try:
        commits = read_first_parent(args.repo)
    except GitError as exc:
        return _fail(str(exc) or f"not a git repository: {args.repo}")
    except OSError as exc:
        return _fail(f"cannot run git in {args.repo}: {exc.strerror or exc}")
    if args.prs is None:
        try:
            records = fetch_prs(args.repo)
        except GhError as exc:
            return _fail(str(exc))
    else:
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
