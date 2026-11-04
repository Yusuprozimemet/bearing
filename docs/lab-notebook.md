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
- **Defects:** 24 in the Notes (D01.24 added after the close, in `tooling/step-guard`).

  | Field | Count |
  | --- | --- |
  | found: auditor | 17 |
  | found: Track A | 1 |
  | found: Track C | 1 |
  | found: close | 2 |
  | found: self | 1 |
  | found: review | 2 |
  | cause: spec | 15 |
  | cause: process | 6 |
  | cause: environment | 3 |

  The spec-auditor found 11 of the 17 auditor defects (D01.7–D01.17) in the draft spec, before
  any code was written. Two defects were found only after merge, at the close (D01.20, D01.21).
- **The workflow's own gap (D01.23):** after a "merged", the session carried on into the next
  step in the same context. CLAUDE.md states the rule, and it was skipped anyway. The
  maintainer rejected a fix in the session's private memory: other users of the kit would never
  see it, and it would hide the gap from the measurement. The fix goes in the repository as a
  hook (H01.7). One merge later it happened again (D01.24): after #8's "merged" the session
  launched the end-of-phase auditors in the same context, reading step 6's "after step 5" as
  leave to go on. Prose alone held neither time; `scripts/step-guard.py` now refuses new work
  after a "merged" until a new session.
- **Tokens:** `docs/dashboard/token-usage.json` tags two rows with Day 1, both on 2026-11-04:
  the main session (92 replies, $5.15) and the implementer on Haiku (31 replies, $0.08). The
  folder's total from 2026-10-28 to 2026-11-04 is $168.85. Most of it was spent setting up the
  repository before the spec, and the script tags none of that to a day.

### Day 02: Ingest (Phase 1), closed in the closing PR

- **Delivered:** `bearing ingest <repo> --prs <file> [--data DIR]`. It reads the first-parent
  line of `main` (#13) and maps the `gh` records to it, `mergeCommit` first and the merge subject
  only when there is no `oid` (#14). It stores both in SQLite through migration
  `001_history.sql` (#15). It prints the counts line and each unmatched item against the golden
  file `tests/fixtures/expected/ingest.txt` (#16). On the fixture:
  `merges 10  matched 9  unmatched merges 1  unmatched PRs 1  direct 2`. `pytest -q`: 20 passed,
  4 subtests passed.
- **Criteria:** 11 of 11 ticked: 10 `new` and 1 `hold`.
- **Breaks on purpose:** 11, all in `specs/breaks/day-02.json`: 1 in #11, 2 in #13, 3 in #14, 1
  in #15, 3 in #16, and 1 at the close. No track broke C02.4, so the close ran its first break
  (D02.14). Two `manifest:` lines had lost a level of backslashes in their PR bodies, as on Day 1
  (D02.12, D02.13). The close restored them and replayed all 11 in an LF worktree. Each one
  failed its check.
- **PRs:** 7 at the day-spec rung: the spec (#11), Tracks 0 and A–D (#12–#16), and the close.
  Before them, #10 was a plan-change PR from the Phase 0/1 plan-auditor.
- **Defects:** 15 in the Notes, 2 of them recurrences of D01.21.

  | Field | Count |
  | --- | --- |
  | found: auditor | 6 |
  | found: Track B | 1 |
  | found: Track D | 2 |
  | found: review | 2 |
  | found: close | 3 |
  | found: self | 1 |
  | cause: spec | 9 |
  | cause: implementation | 1 |
  | cause: process | 5 |

  The spec-auditor's six findings (D02.1–D02.6) all landed in the spec before any code. Four of
  them would have produced a criterion that could not be met or a test that could not fail. Two
  spec gaps came up only in Track D, both on the output side: the report crashes on a non-ASCII
  title when stdout is piped on Windows (D02.10), and a bad `--data` gives a traceback (D02.11).
  Both go to Day 3 (H02.2, H02.3).
- **Tokens:** `docs/dashboard/token-usage.json` tags three rows with Day 2, all on 2026-11-04:
  the main session (76 replies, $3.20), the spec-auditor (33 replies, $1.14) and the
  implementer on Haiku (39 replies, $0.04). The folder's total from 2026-10-28 to 2026-11-04 is
  $184.22, counted during the close, so the close's own session is only partly in it.

## What is being measured

| Question | Evidence it will be judged on |
| --- | --- |
| What does a merged PR cost, by rung? | `docs/dashboard/token-usage.json`; at the Day 4 and Day 10 stops, `scripts/token-usage.py --compare --split`, and per-rung counts by hand from the merged branches (plan.md, "Measurement") |
| Where are defects found, and what causes them? | Each day's `Defect` lines (`found:`, `cause:`, `made:`), the dashboard's defect-tag table, and the blind relabel at each close |
| Can each criterion's check fail? | The `broken:` lines under the ticked criteria, `specs/breaks/day-NN.json`, and the post-merge evidence replay (`evidence.yml`) |
| Does the work stay reviewable? | The PR diff stays under 400 changed lines; uses of `Oversized:` so far: none |

## Retrospective
