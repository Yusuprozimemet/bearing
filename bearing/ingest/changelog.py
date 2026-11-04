"""The changelog: one entry per merge on the line, grouped by the area its branch names."""

import datetime
from typing import NamedTuple

from bearing.ingest.text import area, what_i_built


class Entry(NamedTuple):
    number: int | None
    title: str
    date: str
    area: str
    paragraph: str


def read_entries(conn):
    # The LEFT JOIN keeps an unmatched merge, which has no prs row, as an entry made from its subject.
    rows = conn.execute(
        "SELECT commits.pr_number, commits.subject, commits.committed_at,"
        " commits.subject_number, commits.subject_branch,"
        " prs.number, prs.title, prs.head_ref, prs.body"
        " FROM commits LEFT JOIN prs ON prs.number = commits.pr_number"
        " WHERE commits.kind = 'merge' ORDER BY commits.position"
    ).fetchall()
    entries = []
    for (
        pr_number,
        subject,
        committed_at,
        subject_number,
        subject_branch,
        number,
        title,
        head_ref,
        body,
    ) in rows:
        # The date is the merge commit's, never the PR record's: a record's mergedAt can differ.
        date = committed_at[:10]
        if pr_number is not None:
            entries.append(
                Entry(number, title, date, area(head_ref), what_i_built(body))
            )
        else:
            entries.append(
                Entry(subject_number, subject, date, area(subject_branch), "")
            )
    return entries


def format_changelog(entries, since=None, until=None):
    kept = []
    for entry in entries:
        date = datetime.date.fromisoformat(entry.date)
        if since is not None and date < since:
            continue
        if until is not None and date > until:
            continue
        kept.append(entry)

    lines = ["# Changelog"]
    for name in sorted({entry.area for entry in kept}):
        lines += ["", f"## {name}", ""]
        # Entries keep the order they were given in: no sort by number or date here.
        for entry in kept:
            if entry.area != name:
                continue
            number = "-" if entry.number is None else str(entry.number)
            lines.append(f"- #{number} {entry.title} ({entry.date})")
            if entry.paragraph:
                lines += [f"  {line}" for line in entry.paragraph.split("\n")]
    return lines
