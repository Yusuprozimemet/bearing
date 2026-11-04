"""Reading the first-parent history of main, and the merge subjects GitHub writes into it."""

import re
import subprocess
from datetime import UTC, datetime
from typing import NamedTuple

MERGE_SUBJECT = re.compile(r"Merge pull request #(\d+) from ([^/\s]+)/(\S+)")


class Commit(NamedTuple):
    sha: str
    parents: tuple[str, ...]
    committed_at: str
    subject: str


class MergeSubject(NamedTuple):
    number: int
    owner: str
    branch: str


class GitError(Exception):
    """Raised when git fails; the message carries git's stderr."""


def read_first_parent(repo) -> list[Commit]:
    # Read-only: git log writes nothing, so the repository is left as it was.
    result = subprocess.run(
        [
            "git",
            "-C",
            str(repo),
            "log",
            "--first-parent",
            "--reverse",
            "--format=%H%x00%P%x00%ct%x00%s",
            "main",
            "--",
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if result.returncode != 0:
        raise GitError(result.stderr.strip())
    commits = []
    # Split on "\n" only: splitlines() would also break a subject at other line separators.
    for line in result.stdout.split("\n"):
        if not line:
            continue
        # %x00 separates the fields: a subject may hold spaces, never a NUL.
        sha, parents, committed, subject = line.split("\x00", 3)
        commits.append(
            Commit(
                sha=sha,
                parents=tuple(parents.split()),
                committed_at=datetime.fromtimestamp(int(committed), UTC).isoformat(),
                subject=subject,
            )
        )
    return commits


def parse_merge_subject(subject) -> MergeSubject | None:
    match = MERGE_SUBJECT.fullmatch(subject)
    if match is None:
        return None
    number, owner, branch = match.groups()
    return MergeSubject(int(number), owner, branch)
