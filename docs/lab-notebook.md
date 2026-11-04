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

### Day 02: Ingest (Phase 1), closed in #17

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

### Day 03: Changelog (Phase 1), closed in #24

- **Delivered:** `bearing changelog [--since DATE] [--until DATE] [--data DIR]`. A merge's area is
  its branch up to the first `/`, and its paragraph is the first one under "What I built" in
  the PR body, or the body's first paragraph (#21). The entries are ingest's `merges`, dated by
  the merge commit, not the record. They print as `# Changelog` and then one `## <area>` section
  per area, against the golden file `tests/fixtures/expected/changelog.md` (#22). The command
  and its contract test came in #23, with two hand-offs from Day 2. Stdout is UTF-8 whatever the
  code page (H02.2), and an unusable `--data` gives "bearing: ..." and exit 1, not a traceback
  (H02.3). On the fixture: 10 entries, the ingest line's `merges 10`. `pytest -q`: 30 passed,
  22 subtests passed.
- **Criteria:** 9 of 9 ticked: 8 `new` and 1 `hold`.
- **Breaks on purpose:** 11, all in `specs/breaks/day-03.json`: 1 in #19, 2 in #21, 3 in #22
  and 5 in #23. Every criterion had one before the close, so the close ran none. All 11
  `manifest:` lines arrived intact. On Days 1 and 2 some had lost backslashes (D01.21, D02.12,
  D02.13). The close replayed all 11 in an LF worktree, and each one failed its check.
- **PRs:** 5 at the day-spec rung: the spec (#19), Tracks A–C (#21–#23) and the close. #20, a
  `tooling/` PR that added the `human:` line, merged between the spec and Track A.
- **Defects:** 12 in the Notes.

  | Field | Count |
  | --- | --- |
  | found: spec-change PR | 1 |
  | found: auditor | 9 |
  | found: Track B | 1 |
  | found: self | 1 |
  | cause: spec | 9 |
  | cause: process | 2 |
  | cause: environment | 1 |

  Ten of the twelve were in the spec and were fixed before any code: the session's own count
  (D03.1) and nine spec-auditor findings (D03.2–D03.10). One finding (D03.3) would have let a
  format that sorted by number pass. Track B's break, which sorts by number, confirmed it: the
  golden file passes with that break in, and only the out-of-order pair catches it. No track
  found a spec gap, and the close found no escape. The two defects after the spec PR are an
  environment one (a corrupt Ruff cache, D03.11) and the close's own (D03.12).
- **Hand-offs:** H02.2 and H02.3 picked up (C03.7, C03.8). Left: H03.1 (stderr's encoding) and
  H03.3 (version strings in the text formats) to the maintainer, H03.2 (a broken `bearing.db`)
  to Day 4, with H02.1 still there.
- **Tokens:** `docs/dashboard/token-usage.json` tags three rows with Day 3, all on 2026-11-04:
  the main session (76 replies, $3.67), the spec-auditor (33 replies, $1.43) and the
  implementer on Haiku (27 replies, $0.04). The folder's total from 2026-10-28 to 2026-11-04 is
  $197.05, counted during the close, so the close's own session is only partly in it.

### Day 04: Live PRs (Phase 1), closed in #29

- **Delivered:** `bearing ingest <repo>` with no `--prs` reads the records from `gh pr list`
  itself, with the same command `--prs` files are recorded with. A missing `gh`, a failed call
  or output that is not JSON gives "bearing: ..." and exit 1, with no store written (#27). Two
  records on one merge commit now go to the one the merge subject names, or else the lowest
  number, whatever `gh`'s order (H02.1, #28). A broken `bearing.db` was already refused, and a
  test now pins it (H03.2, #26). Phase 1's done line holds on the kit at `44d7a55`:
  `merges 91  matched 91  unmatched merges 0  unmatched PRs 0  direct 11`, and 91 changelog
  entries, none of them falling back to its merge subject. `pytest -q`: 38 passed, 33 subtests
  passed.
- **Criteria:** 8 of 8 ticked: 4 `new` and 4 `hold`.
- **Breaks on purpose:** 9, all in `specs/breaks/day-04.json`: 1 in #25, 2 in #26, 5 in #27 and
  1 in #28. C04.6's break needs the kit, so it was run by hand in #25 and is in no manifest.
  The close replayed all 9 in an LF worktree, and each one failed its check.
- **PRs:** 5 at the day-spec rung: the spec (#25), Tracks 0, A and B (#26–#28) and the close.
- **Defects:** 12 in the Notes.

  | Field | Count |
  | --- | --- |
  | found: spec-change PR | 1 |
  | found: auditor | 8 |
  | found: Track A | 1 |
  | found: Track B | 2 |
  | cause: spec | 7 |
  | cause: process | 5 |

  The blind relabel agreed on 11 of 12 stages and causes. It moved D04.7 from `environment` to
  `spec`, and D04.8 stayed `found: auditor` (the spec's Notes give the reasons). Nine were found before any code: the session's own (D04.1, a Day 3 escape: #23 already
  refused a broken store, untested) and eight spec-auditor findings (D04.2–D04.9). Two of
  those would have let wrong code pass: a command check compared with the module's own constant
  (D04.5) and a shared-`oid` case with no subject naming neither record (D04.6). The three
  after the spec PR are process slips around the implementer: an expected count that missed
  Track 0's tests (D04.10), a count taken before formatting (D04.11) and a red value not
  reported (D04.12). The main session caught each before its PR. No escape was found at the close.
- **Hand-offs:** H02.1 and H03.2 picked up (C04.5, C04.1). H04.1, the Phase 1 stop, held in
  #30: the changelog judged useful enough to go on, with three findings; the kit copied in at
  `c12cfe5`; the token comparison, which separates nothing yet (plan.md, "Course correction
  after Phase 1"). Left to the maintainer: H04.2 (`gh`'s 1000-PR cap), with H03.1 and H03.3 still there.
- **Tokens:** `docs/dashboard/token-usage.json` tags two rows with Day 4, on 2026-11-04: the
  main session (51 replies, $2.09) and the implementer on Haiku (9 replies, $0.01). Most of the
  day went to rows with no day: since Day 3's close the untagged main session rose from 349 to
  415 replies and the untagged spec-auditor from 44 to 85. The folder's total from 2026-10-28
  to 2026-11-04 is $206.89, counted during the close, so the close's own session is only
  partly in it.

### Day 05: Snapshot (Phase 2), closed in #37

- **Delivered:** `bearing snapshot <repo> <ref>` prints the `snapshot-v1` JSON of a repository
  at one commit: one module per `.py` file, with its dotted name, path, line count and whether
  it parses, and the import edges between modules in the repository (#36). Names, line counts,
  import parsing and resolution are `bearing.snapshot.modules` (#34), and `snapshot(repo, ref)`
  reads the tree from git without writing to the target (#35). The golden file pins `448fc4d`,
  which holds the fixture's cycle: 15 modules and 8 imports. `main`'s 16 and 7 are pinned
  outside the contract. A bad ref or a directory that is not a repository gives "bearing: ..."
  and exit 1. `pytest -q`: 47 passed, 47 subtests passed.
- **Criteria:** 10 of 10 ticked: 9 `new` and 1 `hold`.
- **Breaks on purpose:** 11, all in `specs/breaks/day-05.json`: 1 in #32, 5 in #34, 2 in #35 and
  3 in #36. Track 0 (#33) had no criterion. The close replayed all 11 in an LF worktree, and
  each one failed its check.
- **PRs:** 6 at the day-spec rung: the spec (#32), Tracks 0, A, B and C (#33–#36) and the close.
- **Defects:** 10 in the Notes.

  | Field | Count |
  | --- | --- |
  | found: spec-change PR | 1 |
  | found: auditor | 7 |
  | found: Track B | 1 |
  | found: close | 1 |
  | cause: spec | 9 |
  | cause: process | 1 |

  The blind relabel agreed on all 10 stages, causes and `made:`; the rater marked D05.2,
  D05.8 and D05.10 as mixed, and no tag changed. Eight were found before any code: one by the session's own
  scratch implementation of the spec's rules (D05.1) and seven by the spec-auditor
  (D05.2–D05.8). Two of those would have let wrong code pass: a golden file checked only
  against the implementation's own output (D05.5), and a resolution case that a wrong rule
  passed too (D05.3). One would have crashed: deep nesting raising past `parse_imports` (D05.6).
  After the spec PR there was one process slip, a wrong expected count in a brief (D05.9),
  and one escape found at the close. The spec's red text for Track A was a guess, not a
  run, and the track PR recorded only the count (D05.10).
- **Hand-offs:** the plan-auditor's F1–F3 settled in the spec. H01.1 re-pointed to Day 7 as
  H05.5. Open: H05.1 (plan.md's Day 10 cut list) to the maintainer; H05.2–H05.4 (how
  `timeline` finds the repository and store, root and direct commits, the blob cache) to
  Day 6; H05.5 and H05.6 (`grew`, the module map) to Day 7.
- **Tokens:** `docs/dashboard/token-usage.json` tags three rows with Day 5, on 2026-11-04: the
  main session (84 replies, $4.72), the spec-auditor (38 replies, $1.38) and the implementer on
  Haiku (27 replies, $0.04). The untagged main session rose from 415 to 560 replies and the
  untagged plan-auditor from 70 to 118, its runs since Day 4's close. Day 4's close added
  a defect-rater row and raised Day 4's main row to 68 replies. The folder's total from
  2026-10-28 to 2026-11-04 is $224.13, counted during the close, so the close's own session is
  only partly in it.

### Day 06: Timeline (Phase 2), closed in #43

- **Delivered:** `bearing timeline <repo> [--data DIR] [--stats]` prints one line per
  structure event of each stored merge, `<sha7> #<pr or -> <event>`, in history order (#42).
  The events are `+module`, `-module`, `renamed`, `+import` and `-import`, and come from
  `structure_events`, which compares a merge's snapshot with its first parent's through git's
  renames (#40). A blob cache in `002_blobs.sql` stores each blob's line count and parsed
  imports by SHA, so a second run parses nothing (#41). On the fixture: 18 lines, "blobs parsed
  28  cache hits 0", then "blobs parsed 0  cache hits 28". `pytest -q`: 54 passed, 51
  subtests passed.
- **Criteria:** 10 of 10 ticked: 8 `new` and 2 `hold`.
- **Breaks on purpose:** 14, all in `specs/breaks/day-06.json`: 1 in #39, 4 in #40, 4 in #41 and
  5 in #42. The close replayed all 14 in an LF worktree, and each one failed its check.
- **PRs:** 5 at the day-spec rung: the spec (#39), Tracks A, B and C (#40–#42) and the close.
  There was no Track 0.
- **Defects:** 8 in the Notes.

  | Field | Count |
  | --- | --- |
  | found: auditor | 4 |
  | found: break on purpose | 2 |
  | found: self | 1 |
  | found: Track B | 1 |
  | cause: spec | 6 |
  | cause: process | 2 |

  The blind relabel agreed on 7 of 8 stages and all 8 causes and `made:`. On D06.8 the rater
  could not tell the stage from the text, which now names Track B's red run. No tag changed.
  The spec-auditor found four gaps before any code (D06.1–D06.4). Two of them would have let
  a wrong rename rule pass C06.1. Breaks on purpose found two more defects: a spec condition
  that no test could catch (D06.5), and a break that could not reach its test (D06.6). A
  hand-run stash mixed old and new code (D06.7). C06.4's red gave a second reason that no run
  reaches (D06.8, same-as D05.10). For the second day running, a red message was reasoned out
  rather than run. Nothing escaped to the close.
- **Hand-offs:** H05.2–H05.4 were settled in the spec. H05.5 and H05.6 stay with Day 7, and
  H06.1 (the `cycle+` rotation, and whether cycles go through the rename rule) joins them. H05.1
  stays with the maintainer.
- **Tokens:** `docs/dashboard/token-usage.json` tags two rows with Day 6, on 2026-11-04: the
  main session (60 replies, $2.57) and the implementer on Haiku (36 replies, $0.04). Day 6's
  spec-auditor run is in the untagged spec-auditor row, which rose from 85 to 122 replies. The
  untagged main session rose from 560 to 646 replies. Day 5's close added a defect-rater row
  and raised Day 5's main row to 104 replies. The folder's total from 2026-10-28 to 2026-11-04
  is $234.96, counted during the close, so the close's own session is only partly in it.

### Day 07: Cycles (Phase 2), closed in the closing PR

- **Delivered:** `bearing timeline` adds `cycle+` and `cycle-` for each elementary import cycle
  a merge introduces or breaks, started at its least name and compared after the rename rule.
  It also adds `grew <name> <lines>` for a module that crosses 200 lines (#45). The timeline
  has its golden file and contract test: 21 lines on the fixture, with `cycle+` at #3,
  `grew app.core 253` at #6 and `cycle-` at #9. Phase 2's "Done when" on the targets, run at
  the close: the kit's 94 merges give 42 lines and wordtally's 56 give 29, with 6 and 5 `grew`
  and no cycle. A second run parses no blob ("blobs parsed 0  cache hits 204", and 94), in
  under 30 s. `pytest -q`: 56 passed, 51 subtests passed.
- **Criteria:** 5 of 5 ticked: 3 `new` and 2 `hold`.
- **Breaks on purpose:** 4, all in `specs/breaks/day-07.json`: 1 in #44 and 3 in #45. The close
  replayed all 4 on `main`, and each one failed its check. C07.4 was broken once by hand on
  the kit, not replayed, since it needs the clone: with the cache not committed, the second
  run printed "blobs parsed 204  cache hits 0".
- **PRs:** 3 at the day-spec rung: the spec with a plan change (#44), Track A (#45) and the
  close. There was no Track 0.
- **Defects:** 5 in the Notes.

  | Field | Count |
  | --- | --- |
  | found: auditor | 5 |
  | cause: spec | 5 |

  The blind relabel agreed on 3 of 5 stages, 4 of 5 causes and all 5 `made:`. On D07.4 the
  rater could not tell the stage from the text, which now says it was found before any code,
  and read the cause as process. On D07.5 it read Day 5's escape as found before code. No tag
  changed.
  The spec-auditor found all five before any code. Two would have let wrong code pass C07.1:
  a `cycle-` with no renamed module (D07.1), and a claim about edge order that was false
  (D07.2). Two were checks that could not fail: Verify's exit code (D07.3), and C07.4's check,
  which no break reached (D07.4). One went back to Day 5: plan.md still listed cycles as a cut
  (D07.5). Track A and the close found nothing, and for the first time this phase every red
  text matched its run.
- **Hand-offs:** H05.5 (`grew`) and H06.1 (the cycle's rotation and the rename rule) were
  settled in #45. H05.6 (the module map) was cut, and H05.1 (plan.md's Day 10 cut list) was
  settled by #44's plan change. H07.1, where `bearing.toml` is read from, goes to Day 8.
- **Tokens:** `docs/dashboard/token-usage.json` tags three rows with Day 7, on 2026-11-04: the
  main session (48 replies, $2.65), the spec-auditor (52 replies, $1.56) and the implementer on
  Haiku (16 replies, $0.02). The untagged main session rose from 646 to 686 replies. Day 6's
  close added a defect-rater row and raised Day 6's main row to 79 replies. The folder's total
  from 2026-10-28 to 2026-11-04 is $242.83, counted during the close, so the close's own
  session is only partly in it.

## What is being measured

| Question | Evidence it will be judged on |
| --- | --- |
| What does a merged PR cost, by rung? | `docs/dashboard/token-usage.json`; at the Day 4 and Day 10 stops, `scripts/token-usage.py --compare --split`, and per-rung counts by hand from the merged branches (plan.md, "Measurement") |
| Where are defects found, and what causes them? | Each day's `Defect` lines (`found:`, `cause:`, `made:`), the dashboard's defect-tag table, and the blind relabel at each close |
| Can each criterion's check fail? | The `broken:` lines under the ticked criteria, `specs/breaks/day-NN.json`, and the post-merge evidence replay (`evidence.yml`) |
| Does the work stay reviewable? | The PR diff stays under 400 changed lines; uses of `Oversized:` so far: none |

## Retrospective
