"""The timeline: for each stored merge, the structure events between its first parent and itself."""

from bearing.snapshot.diff import structure_events
from bearing.snapshot.tree import renamed_paths, snapshot


def timeline(repo, conn, cache):
    rows = conn.execute(
        "SELECT sha, pr_number FROM commits WHERE kind = 'merge' ORDER BY position"
    ).fetchall()
    lines = []
    for sha, pr_number in rows:
        # The merge before its parent, so a store from another repository fails on the merge's SHA.
        new = snapshot(repo, sha, cache)
        old = snapshot(repo, sha + "^1", cache)
        events = structure_events(old, new, renamed_paths(repo, old["ref"], new["ref"]))
        number = "-" if pr_number is None else pr_number
        lines += [f"{sha[:7]} #{number} {event}" for event in events]
    return lines
