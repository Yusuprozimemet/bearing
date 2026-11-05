"""The direction report: churn by area and week, the files that change together, and what the pull requests said against what they changed."""

from bearing.direction.changes import changed_files
from bearing.direction.churn import churn
from bearing.direction.coupling import coupling
from bearing.direction.said_vs_done import said_vs_done


def direction_report(repo, conn, areas, min_prs, rules):
    # Each commit's files are read once: the churn rows and the merges' coupling both use them.
    files_by_sha = {}

    def files_of(sha):
        if sha not in files_by_sha:
            files_by_sha[sha] = changed_files(repo, sha)
        return files_by_sha[sha]

    churn_commits = [
        (committed_at, files_of(sha))
        for sha, committed_at in conn.execute(
            "SELECT sha, committed_at FROM commits WHERE parent_count > 0 ORDER BY position"
        )
    ]
    # The PR's text comes from the same row as its number: a merge whose PR was not fetched has no text.
    merges = [
        (sha, number, branch, body, [path for path, _, _ in files_of(sha)])
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
    prs = [(number, paths) for _, number, _, _, paths in merges]
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
