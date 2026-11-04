# Lab notebook

## Results to date

### Day 01: Skeleton (Phase 0), closed in #8

- **Delivered:** `bearing --version`, as a module and as a console script (#2); the ignore and
  line-ending rules (#2); `tests/fixtures/make_repo.py`, which builds a 12-step history with its
  `prs.json` (#3) and the contents of its structure and PR-text cases (#6); and the fixture's
  HEAD SHA pinned in `tests/contract/test_fixture.py`, the same on Linux CI and on Windows.
  `pytest -q`: 9 passed.
- **Criteria:** 11 of 11 ticked: 9 `new` and 2 `hold`. C01.11 was checked by a reader, from
  `gh variable list`.
- **Breaks on purpose:** 13 recorded across #1, #2, #3 and #6, and each one failed its check.
  12 are in `specs/breaks/day-01.json`. The 13th bites only where the environment sets
  `GIT_AUTHOR_NAME`, so a local Windows run guards it, not the replay.
- **PRs:** 5 at the day-spec rung (#1, #2, #3, #6, #8) and 3 area branches (#4, #5, #7). The
  three area branches fixed kit tooling: seen-red copied the code under test into the base
  (#4), the evidence workflow's install test (#5), and the replay compared pytest's run time
  (#7).
- **Defects:** 23 in the Notes.

  | Field | Count |
  | --- | --- |
  | found: auditor | 17 |
  | found: Track A | 1 |
  | found: Track C | 1 |
  | found: close | 2 |
  | found: self | 1 |
  | found: review | 1 |
  | cause: spec | 15 |
  | cause: process | 5 |
  | cause: environment | 3 |

  The spec-auditor found 11 of the 17 auditor defects (D01.7–D01.17) in the draft spec, before
  any code was written. Two defects were found only after merge, at the close (D01.20, D01.21).
- **The workflow's own gap (D01.23):** after a "merged", the session carried on into the next
  step in the same context. CLAUDE.md states the rule, and it was skipped anyway. The
  maintainer rejected a fix in the session's private memory: other users of the kit would never
  see it, and it would hide the gap from the measurement. The fix goes in the repository as a
  hook (H01.7).
- **Tokens:** `docs/dashboard/token-usage.json` tags two rows with Day 1, both on 2026-11-04:
  the main session (92 replies, $5.15) and the implementer on Haiku (31 replies, $0.08). The
  folder's total from 2026-10-28 to 2026-11-04 is $168.85. Most of it was spent setting up the
  repository before the spec, and the script tags none of that to a day.

## What is being measured

| Question | Evidence it will be judged on |
| --- | --- |
| What does a merged PR cost, by rung? | `docs/dashboard/token-usage.json`; at the Day 4 and Day 10 stops, `scripts/token-usage.py --compare --split`, and per-rung counts by hand from the merged branches (plan.md, "Measurement") |
| Where are defects found, and what causes them? | Each day's `Defect` lines (`found:`, `cause:`, `made:`), the dashboard's defect-tag table, and the blind relabel at each close |
| Can each criterion's check fail? | The `broken:` lines under the ticked criteria, `specs/breaks/day-NN.json`, and the post-merge evidence replay (`evidence.yml`) |
| Does the work stay reviewable? | The PR diff stays under 400 changed lines; uses of `Oversized:` so far: none |

## Retrospective
