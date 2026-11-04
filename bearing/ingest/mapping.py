"""Mapping the first-parent history onto the PRs gh listed, and the report of what did not match."""

import json
from pathlib import Path
from typing import NamedTuple

from bearing.ingest.history import Commit, parse_merge_subject


class MappingResult(NamedTuple):
    pr_by_sha: dict[str, int]
    merges: int
    matched: int
    unmatched_merges: list[Commit]
    unmatched_prs: list[dict]
    direct: int


def load_prs(path) -> list[dict]:
    # gh writes UTF-8; the system's code page would turn a title's non-ASCII text into noise.
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _oid(record):
    merge_commit = record.get("mergeCommit")
    if isinstance(merge_commit, dict) and merge_commit.get("oid"):
        return merge_commit["oid"]
    return None


def _pick(commit, candidates):
    # Several records can share one merge commit, a squashed PR and the PR it came from.
    # The commit's subject names the one it merged; without a name, the lowest number wins,
    # so the answer does not depend on the order gh listed the records in.
    subject = parse_merge_subject(commit.subject)
    if subject is not None:
        for index, record in candidates:
            if record["number"] == subject.number:
                return index
    return min(candidates, key=lambda item: item[1]["number"])[0]


def map_history(commits, records) -> MappingResult:
    pr_by_sha: dict[str, int] = {}
    matched_records: set[int] = set()
    matched_commits: set[str] = set()

    # Pass 1: a record whose mergeCommit oid is a commit on the line.
    for commit in commits:
        candidates = [
            (index, record)
            for index, record in enumerate(records)
            if index not in matched_records and _oid(record) == commit.sha
        ]
        if not candidates:
            continue
        index = _pick(commit, candidates)
        pr_by_sha[commit.sha] = records[index]["number"]
        matched_records.add(index)
        matched_commits.add(commit.sha)

    # Pass 2: a two-parent merge whose subject names a record that has no oid. A record
    # with an oid is never matched by its subject, even when that oid is off the line.
    for commit in commits:
        if commit.sha in matched_commits or len(commit.parents) != 2:
            continue
        subject = parse_merge_subject(commit.subject)
        if subject is None:
            continue
        for index, record in enumerate(records):
            if (
                record["number"] == subject.number
                and index not in matched_records
                and _oid(record) is None
            ):
                pr_by_sha[commit.sha] = record["number"]
                matched_records.add(index)
                matched_commits.add(commit.sha)
                break

    unmatched_merges = [
        commit
        for commit in commits
        if commit.sha not in matched_commits and len(commit.parents) == 2
    ]
    unmatched_prs = sorted(
        (
            record
            for index, record in enumerate(records)
            if index not in matched_records
        ),
        key=lambda record: record["number"],
    )
    direct = sum(
        1
        for commit in commits
        if commit.sha not in matched_commits and len(commit.parents) < 2
    )
    matched = len(matched_commits)
    return MappingResult(
        pr_by_sha=pr_by_sha,
        merges=matched + len(unmatched_merges),
        matched=matched,
        unmatched_merges=unmatched_merges,
        unmatched_prs=unmatched_prs,
        direct=direct,
    )


def format_report(result: MappingResult) -> list[str]:
    summary = (
        f"merges {result.merges}  matched {result.matched}"
        f"  unmatched merges {len(result.unmatched_merges)}"
        f"  unmatched PRs {len(result.unmatched_prs)}  direct {result.direct}"
    )
    lines = [summary]
    for commit in result.unmatched_merges:
        lines.append(f"unmatched merge {commit.sha[:7]} {commit.subject}")
    for record in result.unmatched_prs:
        oid = _oid(record)
        short = oid[:7] if oid else "-"
        lines.append(f"unmatched PR #{record['number']} {short} {record['title']}")
    return lines
