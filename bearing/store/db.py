"""Bearing's SQLite store: opening it, applying its migrations, and saving one ingest into it."""

import sqlite3
from importlib.resources import files
from pathlib import Path

from bearing.ingest.history import parse_merge_subject


def open_store(data_dir) -> sqlite3.Connection:
    Path(data_dir).mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(Path(data_dir) / "bearing.db")
    conn.execute("CREATE TABLE IF NOT EXISTS schema_migrations (name TEXT PRIMARY KEY)")
    applied = {row[0] for row in conn.execute("SELECT name FROM schema_migrations")}
    migrations = files("bearing") / "migrations"
    names = sorted(
        entry.name for entry in migrations.iterdir() if entry.name.endswith(".sql")
    )
    for name in names:
        if name in applied:
            continue
        conn.executescript((migrations / name).read_text(encoding="utf-8"))
        conn.execute("INSERT INTO schema_migrations (name) VALUES (?)", (name,))
        conn.commit()
    return conn


def save(conn, commits, records, result) -> None:
    # Both tables are replaced whole, in one transaction, so a second ingest does not double the rows.
    commit_rows = []
    for position, commit in enumerate(commits):
        subject = parse_merge_subject(commit.subject)
        if subject is None:
            subject_columns = (None, None, None)
        else:
            subject_columns = (subject.number, subject.owner, subject.branch)
        parent_count = len(commit.parents)
        kind = (
            "merge" if commit.sha in result.pr_by_sha or parent_count == 2 else "direct"
        )
        commit_rows.append(
            (
                commit.sha,
                position,
                parent_count,
                commit.subject,
                commit.committed_at,
                kind,
                result.pr_by_sha.get(commit.sha),
                *subject_columns,
            )
        )
    pr_rows = [
        (
            record["number"],
            record["title"],
            record.get("body") or "",
            record["headRefName"],
            record["baseRefName"],
            (record.get("mergeCommit") or {}).get("oid") or None,
            record.get("mergedAt"),
        )
        for record in records
    ]
    with conn:
        conn.execute("DELETE FROM commits")
        conn.execute("DELETE FROM prs")
        conn.executemany(
            "INSERT INTO commits (sha, position, parent_count, subject, committed_at, kind,"
            " pr_number, subject_number, subject_owner, subject_branch)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            commit_rows,
        )
        conn.executemany(
            "INSERT INTO prs (number, title, body, head_ref, base_ref, merge_oid, merged_at)"
            " VALUES (?, ?, ?, ?, ?, ?, ?)",
            pr_rows,
        )
