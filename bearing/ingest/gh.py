"""Reads a repository's merged PRs from the gh CLI, in the records a --prs file holds."""

import json
import subprocess

PR_LIST = [
    "gh",
    "pr",
    "list",
    "--state",
    "merged",
    "--limit",
    "1000",
    "--json",
    "number,title,body,headRefName,baseRefName,mergeCommit,mergedAt",
]


class GhError(Exception):
    """A gh call that failed; the message is what the CLI prints after "bearing: "."""


def fetch_prs(repo) -> list[dict]:
    # gh writes UTF-8 whatever the console's code page; the locale's would garble the titles.
    # check is left out on purpose: a failed exit is read below, into the GhError message.
    try:
        result = subprocess.run(  # noqa: PLW1510
            PR_LIST, cwd=repo, capture_output=True, encoding="utf-8"
        )
    except FileNotFoundError:
        raise GhError("gh not found: install GitHub's CLI or pass --prs FILE")
    if result.returncode != 0:
        detail = (result.stderr or "").strip() or f"exit {result.returncode}"
        raise GhError(f"gh pr list failed: {detail}")
    try:
        return json.loads(result.stdout)
    except ValueError as exc:
        raise GhError(f"gh pr list printed no JSON: {exc}")
