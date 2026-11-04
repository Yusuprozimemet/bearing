"""Build the fixture history the tests read: a repository, and prs.json beside it.

Run as `python tests/fixtures/make_repo.py <dir>`. The steps table below drives the build;
CHANGES says what each step's commit adds, edits, moves or deletes, and BODIES what each record
says about its PR.
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

# The file text is LF, except app/crlf.py, which keeps the Windows line ending on purpose.
CRLF_MODULE = (
    '"""A module saved with Windows line endings."""\n\n\ndef c():\n    return 3\n'
)
# 60 functions of four lines each: app/core.py goes from under 200 lines to over 200 in one squash.
GROWTH = "".join(f"\n\ndef grown_{i}():\n    return {i}\n" for i in range(60))

# What each step's commit changes, keyed by step kind ("root", "direct") or by PR number. Writes
# come first, then appends, moves and deletes; a PR with no entry has no commit of its own.
CHANGES = {
    "root": {
        "write": {
            "README.md": README,
            "app/__init__.py": "from . import core\n",
            "app/core.py": '"""The core module, the one the others build on."""\n\n\ndef f():\n    return 1\n',
            "app/legacy.py": '"""The legacy module, kept until the rename lands."""\n\nOLD = ["alpha", "beta"]\n',
            "app/pkg/__init__.py": '"""The pkg package."""\n\n\ndef h():\n    return 2\n',
            "src/lib/__init__.py": '"""The lib package."""\n',
            "src/lib/util.py": "import app.core\n\n\ndef u():\n    return app.core.f()\n",
            "scripts/helpers.py": '"""Helpers for the scripts folder."""\n\n\ndef help_me():\n    return "help"\n',
            "scripts/config.py": '"""Settings the scripts read."""\n\nDEBUG = False\n',
        },
    },
    "direct": {"write": {"README.md": README_FIXED}},
    1: {
        "write": {
            "app/sub/__init__.py": '"""The sub package."""\n',
            "app/sub/mod.py": '"""Imports from the packages above it."""\n\nfrom ..pkg import h\nfrom ..core import f\n\n\ndef both():\n    return h(), f()\n',
        },
        "append": {
            "app/core.py": "\n\ndef g():\n    return 2\n",
            "src/lib/util.py": "\n\ndef v():\n    return 2\n",
        },
    },
    2: {
        "write": {
            "scripts/run.py": 'import helpers\n\n\ndef main():\n    return "Runing"\n',
            "scripts/helpers.py": '"""Helpers for the scripts folder."""\n\nimport config\n\n\ndef help_me():\n    return "help"\n',
        },
    },
    3: {
        "write": {
            "app/a.py": '"""One half of the cycle."""\n\nimport app.b\n',
            "app/b.py": '"""The other half of the cycle."""\n\nimport app.a\n\n\ndef b():\n    return 1\n',
            "app/crlf.py": CRLF_MODULE.replace("\n", "\r\n"),
        },
        "append": {
            "app/core.py": "\n\ndef k():\n    return 4\n",
            "src/lib/util.py": "\n\ndef w():\n    return 3\n",
        },
    },
    4: {"write": {"docs/guide.md": "# Guide\n\nRun the fixture builder.\n"}},
    5: {
        "write": {
            "scripts/run.py": 'import helpers\n\n\ndef main():\n    return "Running"\n',
        },
    },
    6: {
        "write": {"app/broken.py": "def broken(:\n    return 1\n"},
        "append": {"app/core.py": GROWTH},
    },
    7: {
        "write": {
            "docs/notes.md": "# Notes\n\nA side note, merged into release first.\n"
        }
    },
    8: {
        "move": {"scripts/helpers.py": "scripts/tools.py"},
        "write": {
            "scripts/run.py": 'import tools\n\n\ndef main():\n    return "Running"\n',
            "app/extra.py": '"""Extra helpers, added after the rename."""\n\n\ndef extra():\n    return 5\n',
        },
        "delete": ["app/legacy.py"],
    },
    9: {
        "write": {
            "app/b.py": '"""The other half of the cycle."""\n\n\ndef b():\n    return 1\n',
            "tests/contract/test_api.py": '"""The API the contract tests pin."""\n\n\ndef test_api():\n    assert True\n',
        },
        "append": {
            "app/core.py": "\n\ndef m():\n    return 6\n",
            "src/lib/util.py": "\n\ndef x():\n    return 4\n",
        },
    },
    11: {"write": {"ci.txt": "Run the tests on every push.\n"}},
}

TEMPLATE = (
    "## What I built\n\n"
    "A small change to the fixture, so the tests have a real case to read.\n\n"
    "## Why this approach\n\n"
    "The smallest change that gives the tests something to check.\n\n"
    "## Contract impact\n\n"
    "None\n"
)
BODY_2 = (
    "## What was built\n\n"
    "A script that prints a greeting, and the helper module it imports.\n"
)
BODY_9 = (
    "## What I built\n\n"
    "app/b.py stops importing app.a, so the cycle is gone.\n\n"
    "## Why this approach\n\n"
    "The cycle is what the structure cases look for, so it is removed here.\n\n"
    "Contract impact: None\n"
)
# The bodies that differ from the template: #2 has another heading, #4 is empty, #9 states its
# contract impact in one line. Every other record has the template.
BODIES = {2: BODY_2, 4: "", 9: BODY_9}


def git(repo, day, *args):
    # Every call gets the commit date, so each commit and merge carries the step's date. The
    # identity goes in the environment too: GIT_AUTHOR_NAME and the like override user.name.
    env = dict(os.environ)
    env.update(
        GIT_AUTHOR_NAME="Fixture",
        GIT_AUTHOR_EMAIL="fixture@example.com",
        GIT_COMMITTER_NAME="Fixture",
        GIT_COMMITTER_EMAIL="fixture@example.com",
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


def commit(repo, day, change, message):
    for rel, text in change.get("write", {}).items():
        path = repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(text.encode("utf-8"))
    for rel, text in change.get("append", {}).items():
        path = repo / rel
        path.write_bytes(path.read_bytes() + text.encode("utf-8"))
    for old, new in change.get("move", {}).items():
        git(repo, day, "mv", old, new)
    for rel in change.get("delete", []):
        git(repo, day, "rm", "-q", "--", rel)
    git(repo, day, "add", "-A")
    git(repo, day, "commit", "-m", message)


def open_branch(repo, head, start, pr, day):
    # The PR's branch holds the one commit its CHANGES entry names, if it has one.
    git(repo, day, "checkout", "-q", "-b", head, start)
    if pr in CHANGES:
        commit(repo, day, CHANGES[pr], f"Change for #{pr}")


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
        "body": BODIES.get(number, TEMPLATE),
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
            commit(repo, day, CHANGES["root"], SUBJECTS[kind])
        elif kind == "direct":
            commit(repo, day, CHANGES["direct"], SUBJECTS[kind])
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
