"""The direction report: churn by area and week, and the files that change together."""

from bearing.direction.changes import changed_files
from bearing.direction.churn import churn
from bearing.direction.coupling import coupling


def direction_report(repo, conn, areas, min_prs):
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
    prs = [
        (number, [path for path, _, _ in files_of(sha)])
        for sha, number in conn.execute(
            "SELECT sha, COALESCE(pr_number, subject_number) FROM commits"
            " WHERE kind = 'merge' AND COALESCE(pr_number, subject_number) IS NOT NULL"
            " ORDER BY position"
        )
    ]

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
    return lines
