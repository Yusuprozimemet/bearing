"""Build the fixture history the tests read: a repository, and prs.json beside it.

Run as `python tests/fixtures/make_repo.py <dir>`. The steps table below drives the build;
the contents are placeholders for now, so the history shape can be checked on its own.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

# Pinned identity and config, so the commit SHAs do not depend on the machine running the build.
GIT_CONFIG = [
    "-c",
    "user.name=Fixture",
    "-c",
    "user.email=fixture@example.com",
    "-c",
    "core.autocrlf=false",
    "-c",
    "commit.gpgsign=false",
    "-c",
    "init.defaultBranch=main",
    "-c",
    f"core.attributesFile={os.devnull}",
]


def merged(pr, head):
    return f"Merge pull request #{pr} from acme/{head}"


# One row per commit on the first-parent line of main, oldest first:
# (day, kind, PR number, head branch, whether the PR has a record in prs.json).
STEPS = [
    ("05", "root", None, None, False),
    ("07", "merge", 1, "day-01/track-a-core", True),
    ("09", "merge", 2, "tooling/scripts", True),
    ("12", "merge", 4, "docs/guide", True),
    ("14", "merge", 3, "day-02/track-a-cycle", True),
    ("16", "direct", None, None, False),
    ("19", "merge", 5, "docs/typo-fix", True),
    ("21", "squash", 6, "day-02/track-b-grow", True),
    ("23", "merge", 8, "day-03/track-a-rename", True),
    ("26", "merge", 9, "day-03/track-b-break-cycle", True),
    ("28", "merge", 10, "release", True),
    ("30", "merge", 11, "tooling/ci", False),
]
SUBJECTS = {"root": "Initial commit", "direct": "Fix README typo"}
# A PR merged into another PR's branch before that branch lands on main, so its merge is
# reachable from main but off the first-parent line: {outer PR: (day, PR, head branch)}.
# The outer branch's own commit takes the side PR's day.
SIDES = {10: ("27", 7, "docs/notes")}


README = "# Fixture\n"
README_FIXED = "# Fixture\n\nTypo fixed.\n"


def git(repo, day, *args):
    # Every call gets the commit date, so each commit and merge carries the step's date.
    env = dict(os.environ)
    env.update(
        GIT_CONFIG_NOSYSTEM="1",
        GIT_ATTR_NOSYSTEM="1",
        GIT_CONFIG_GLOBAL=os.devnull,
        GIT_AUTHOR_DATE=f"2026-01-{day}T12:00:00+0000",
        GIT_COMMITTER_DATE=f"2026-01-{day}T12:00:00+0000",
    )
    result = subprocess.run(
        ["git", *GIT_CONFIG, *args],
        cwd=repo,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def write_and_commit(repo, day, files, message):
    for rel, text in files.items():
        path = repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(text.encode("utf-8"))
    git(repo, day, "add", "--", *files)
    git(repo, day, "commit", "-m", message)


def open_branch(repo, head, start, pr, day):
    # The PR's branch holds one commit, the PR's own change file.
    git(repo, day, "checkout", "-q", "-b", head, start)
    write_and_commit(
        repo, day, {f"changes/{pr}.txt": f"PR {pr}\n"}, f"Add changes/{pr}.txt"
    )


def merge_into(repo, base, head, subject, day):
    git(repo, day, "checkout", "-q", base)
    git(repo, day, "merge", "--no-ff", "-m", subject, head)
    return git(repo, day, "rev-parse", "HEAD")


def squash_into(repo, base, head, subject, day):
    git(repo, day, "checkout", "-q", base)
    git(repo, day, "merge", "--squash", head)
    git(repo, day, "commit", "-m", subject)
    return git(repo, day, "rev-parse", "HEAD")


def record(number, head, base, day, sha):
    return {
        "baseRefName": base,
        "body": "",
        "headRefName": head,
        "mergeCommit": {"oid": sha},
        "mergedAt": f"2026-01-{day}T12:00:00Z",
        "number": number,
        "title": head,
    }


def build(out):
    repo = out / "repo"
    repo.mkdir()
    records = []
    for day, kind, pr, head, recorded in STEPS:
        if kind == "root":
            git(repo, day, "init", "-q")
            write_and_commit(repo, day, {"README.md": README}, SUBJECTS[kind])
        elif kind == "direct":
            write_and_commit(repo, day, {"README.md": README_FIXED}, SUBJECTS[kind])
        elif kind == "squash":
            open_branch(repo, head, "main", pr, day)
            subject = f"Grow the core module (#{pr})"
            sha = squash_into(repo, "main", head, subject, day)
            records.append(record(pr, head, "main", day, sha))
        else:
            side = SIDES.get(pr)
            open_branch(repo, head, "main", pr, side[0] if side else day)
            if side:
                side_day, side_pr, side_head = side
                open_branch(repo, side_head, head, side_pr, side_day)
                subject = merged(side_pr, side_head)
                side_sha = merge_into(repo, head, side_head, subject, side_day)
                records.append(record(side_pr, side_head, head, side_day, side_sha))
            sha = merge_into(repo, "main", head, merged(pr, head), day)
            if recorded:
                records.append(record(pr, head, "main", day, sha))
    records.sort(key=lambda r: r["number"])
    text = json.dumps(records, sort_keys=True, indent=2) + "\n"
    (out / "prs.json").write_bytes(text.encode("utf-8"))


def main(argv):
    if len(argv) != 2:
        print("usage: make_repo.py <dir>", file=sys.stderr)
        return 2
    out = Path(argv[1])
    if out.exists() and (not out.is_dir() or any(out.iterdir())):
        print(f"make_repo.py: {out} is not an empty directory", file=sys.stderr)
        return 1
    out.mkdir(parents=True, exist_ok=True)
    build(out)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
