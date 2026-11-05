"""The page's data: one step per merge, with its changelog entry, its structure events and its flags."""

from bearing.direction.changes import changed_files
from bearing.direction.said_vs_done import said_vs_done
from bearing.ingest.changelog import read_entries
from bearing.snapshot.diff import structure_events
from bearing.snapshot.tree import renamed_paths, snapshot


def page_data(repo, conn, cache, areas, rules):
    entries = read_entries(conn)
    # The same merges, in the same order, as read_entries; direction's join, without its filter.
    rows = conn.execute(
        "SELECT commits.sha, COALESCE(commits.pr_number, commits.subject_number),"
        " COALESCE(prs.head_ref, commits.subject_branch), prs.body"
        " FROM commits"
        " LEFT JOIN prs ON prs.number = COALESCE(commits.pr_number, commits.subject_number)"
        " WHERE commits.kind = 'merge'"
        " ORDER BY commits.position"
    ).fetchall()
    steps = []
    for entry, (sha, number, branch, body) in zip(entries, rows, strict=True):
        # The merge's snapshots first, as timeline reads them, so a foreign store fails on the SHA.
        new = snapshot(repo, sha, cache)
        old = snapshot(repo, sha + "^1", cache)
        events = structure_events(old, new, renamed_paths(repo, old["ref"], new["ref"]))
        paths = [path for path, _, _ in changed_files(repo, sha)]
        # A merge with no number has no flags, whatever its branch says.
        flags = []
        if number is not None:
            flags = [
                {"rule": rule_id, "claim": claim, "files": list(files)}
                for _, rule_id, claim, files in said_vs_done(
                    [(number, branch, body, paths)], areas, rules
                )
            ]
        steps.append(
            {
                "sha": sha,
                "date": entry.date,
                "number": entry.number,
                "title": entry.title,
                "paragraph": entry.paragraph,
                "events": list(events),
                "flags": flags,
            }
        )
    return {"version": "page-v1", "steps": steps}
