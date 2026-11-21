"""The direction report: churn by area and week, the files that change together, and what the pull requests said against what they changed."""

from bearing.direction.changes import commit_changes
from bearing.direction.churn import churn
from bearing.direction.coupling import coupling, latest_names
from bearing.direction.said_vs_done import said_vs_done


def direction_report(repo, conn, areas, min_prs, rules):
    # Each commit is read once: the churn rows, the merges' paths and the renames all use it.
    changes_by_sha = {}

    def changes_of(sha):
        if sha not in changes_by_sha:
            changes_by_sha[sha] = commit_changes(repo, sha)
        return changes_by_sha[sha]

    commits = list(
        conn.execute(
            "SELECT sha, committed_at FROM commits WHERE parent_count > 0 ORDER BY position"
        )
    )
    churn_commits = [
        (committed_at, changes_of(sha)[0]) for sha, committed_at in commits
    ]
    # Coupling pairs files by their last names, so a renamed file is one file.
    # Churn and said vs done keep the paths as changed.
    names = latest_names(
        [
            ([path for path, _, _ in changes_of(sha)[0]], changes_of(sha)[1])
            for sha, _ in commits
        ]
    )
    last_names = {sha: names[i] for i, (sha, _) in enumerate(commits)}
    # The PR's text comes from the same row as its number: a merge whose PR was not fetched has no text.
    merges = [
        (sha, number, branch, body, [path for path, _, _ in changes_of(sha)[0]])
        for sha, number, branch, body in conn.execute(
            "SELECT commits.sha, COALESCE(commits.pr_number, commits.subject_number),"
            " COALESCE(prs.head_ref, commits.subject_branch), prs.body"
            " FROM commits"
            " LEFT JOIN prs ON prs.number = COALESCE(commits.pr_number, commits.subject_number)"
            " WHERE commits.kind = 'merge'"
            " AND COALESCE(commits.pr_number, commits.subject_number) IS NOT NULL"
            " ORDER BY commits.position"
        )
    ]
    prs = [(number, last_names[sha]) for sha, number, _, _, _ in merges]
    said = said_vs_done(
        [(number, branch, body, paths) for _, number, branch, body, paths in merges],
        areas,
        rules,
    )

    lines = [
        "## Churn",
        "",
        "| Week | Area | Added | Deleted |",
        "|---|---|---|---|",
    ]
    for week, area, added, deleted in churn(churn_commits, areas):
        lines.append(f"| {week} | {area} | {added} | {deleted} |")
    lines += [
        "",
        "## Coupling",
        "",
        "| File | File | PRs | Hidden dependency |",
        "|---|---|---|---|",
    ]
    for a, b, numbers, area_a, area_b in coupling(prs, areas, min_prs):
        hidden = "no" if area_a == area_b else f"{area_a}, {area_b}"
        pr_list = ", ".join(f"#{number}" for number in numbers)
        lines.append(f"| {a} | {b} | {pr_list} | {hidden} |")
    lines += ["", "## Said vs done", ""]
    for number, rule_id, claim, files in said:
        lines.append(f"- #{number} {rule_id}: {claim} | {', '.join(files)}")
    if not said:
        lines.append("No flags.")
    return lines
