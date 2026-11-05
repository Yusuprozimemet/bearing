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

### Day 07: Cycles (Phase 2), closed in #46

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

### Day 08: Churn and coupling (Phase 3), closed in #51

- **Delivered:** `bearing direction <repo> [--data DIR] [--config FILE]` reads its path areas
  and coupling threshold from a `bearing.toml` outside the target repository (default
  `bearing.toml` in the working directory). It prints a `## Churn` table, lines added and
  deleted per area per ISO week, and a `## Coupling` table, file pairs changed together in at
  least `min_prs` PRs (3 by default), with each file's area. The package `bearing/direction/`
  holds the config (#48), the numstat reader and churn (#48), coupling and the report (#50). On
  the fixture it prints the spec's 23 lines. It reads git at run time, with no new migration.
  `pytest -q`: 65 passed, 58 subtests passed.
- **Criteria:** 8 of 8 ticked: 7 `new` and 1 `hold`.
- **Breaks on purpose:** 9, all in `specs/breaks/day-08.json`: 2 in #47, 3 in #48 and 4 in
  #50. The close replayed all 9 on `main`, and each one failed its check.
- **PRs:** 4 at the day-spec rung: the spec with a plan change (#47), Track A (#48), Track B
  (#50) and the close. There was no Track 0. A `tooling/` branch (#49) fixed `seen-red.py`
  between the tracks, outside the day.
- **Defects:** 11 in the Notes.

  | Field | Count |
  | --- | --- |
  | found: auditor | 7 |
  | found: spec-change PR | 2 |
  | found: Track A | 1 |
  | found: self | 1 |
  | cause: spec | 9 |
  | cause: environment | 1 |
  | cause: process | 1 |

  The spec-auditor and plan-auditor found seven before any code. Three were plan.md
  questions the maintainer settled in #47's Course correction: what an "area" is (D08.1),
  whether the fixture's #5 is a lie (D08.2), and the contract-impact form no kit PR writes
  (D08.3). Two were stale plan.md lines (D08.8, D08.9), one a criterion Day 9 would have broken
  (D08.6) and one a missing test count (D08.7). The spec-change PR caught two hand counts in
  its own draft (D08.4, D08.5). In the tracks, `seen-red.py` and CI's "Track tests seen red"
  gave a false pass for a new subpackage (D08.10), fixed in #49 before track B; and one break
  was first tried with a multi-line `--find` on a CRLF file (D08.11). Every red text matched
  its run, as on Day 7.
  The blind relabel agreed on 8 of 11 stages and on every cause and `made:`. On D08.7 and
  D08.9 the rater could not tell the stage from the text, which now says the spec-auditor
  found them before any code. On D08.8 it read Day 7's escape as found before code. No tag
  changed.
- **Human interventions:** 4. In #47 the maintainer made three choices for plan.md: one table
  of path areas, the fixture's #5 flagged and judged at the stop, and the Phase 3 split across
  Days 8 to 10. In #48 they pointed at the failing "Track tests seen red" check, which led to
  #49.
- **Hand-offs:** H07.1 (where `bearing.toml` is read from) and H01.2 (the coupling threshold)
  were decided in #47 and built in #48 and #50. H05.1's remainder, coupling in the Day 10
  stop's cut list, was dropped by #47's plan change. H08.1, said vs done with its golden file
  and `bearing.toml.example`, goes to Day 9; H08.2, the kit's `bearing.toml` and run, to Day
  10.
- **Tokens:** `docs/dashboard/token-usage.json` tags four rows with Day 8: on 2026-11-04 the
  main session (25 replies, $1.76) and the spec-auditor (39 replies, $1.28); on 2026-11-05 the
  main session (61 replies, $2.32) and the implementer on Haiku (18 replies, $0.03). The
  untagged rows rose on 2026-11-04 (main from 686 to 725 replies, the plan-auditor from 118 to
  143), and 2026-11-05 adds an untagged main session (47 replies, $2.77). Day 7's close added a
  defect-rater row and raised Day 7's main row to 65 replies. The folder's total from
  2026-10-28 to 2026-11-05 is $255.49, counted during the close, so the close's own session is
  only partly in it.

### Day 09: Said vs done (Phase 3), closed in #57

- **Delivered:** `bearing direction` ends with a `## Said vs done` section: one list line per
  flag, in first-parent order, or "No flags.". Two rules come from `[rules.<id>]` tables in
  `bearing.toml`: `contract-impact` flags a PR whose body says "Contract impact: none" but
  changes one of the rule's `paths`, and `outside-area` flags a PR that changes files outside
  the path area its branch names. `load_rules` and `said_vs_done` came in #53, with
  `bearing.toml.example` at the root; the section, the fixture's rules and the direction report's
  golden file (`tests/fixtures/expected/direction.md`, 28 lines) in #54. No migration.
  `pytest -q`: 72 passed, 78 subtests passed.
- **Criteria:** 8 of 8 ticked: 7 `new` and 1 `hold`.
- **Breaks on purpose:** 10, all in `specs/breaks/day-09.json`: 2 in #52, 4 in #53 and 4 in
  #54. The close replayed all 10 on `main`, and each one failed its check. One more break, in
  #54, was not caught: dropping the branch's fallback for a merge without a PR record (D09.10).
- **PRs:** 4 at the day-spec rung: the spec (#52), Track A (#53), Track B (#54) and the close.
  There was no Track 0. Two `tooling/` branches changed the dashboard between track B and the
  close (#55, #56), outside the day.
- **Defects:** 11 in the Notes.

  | Field | Count |
  | --- | --- |
  | found: auditor | 7 |
  | found: self | 2 |
  | found: Track A | 1 |
  | found: Track B | 1 |
  | cause: spec | 10 |
  | cause: process | 1 |

  The spec-auditor found seven before any code (D09.2 to D09.8): a promise no criterion
  checked (rules read before the store), two open questions (`[areas]` in `load_rules`, an
  unused `paths` key), a hold with no named break, an unnamed join, a red that would not
  collect, and an area named "other". The spec-change PR reworded plan.md's direction contract
  itself (D09.1). Two spec gaps got past the audit: C09.4's red was one CI's "Track tests seen
  red" refuses (D09.9), and no criterion sees the branch's fallback (D09.10, handed to Day 10
  as H09.1). The close's Verify first ran in a directory left from an earlier run (D09.11).
  The blind relabel agreed on 10 of 11 stages, causes and `made:`. On D09.1 the rater could
  not tell the stage or the day that made it, and on D09.11 it read the cause as
  `environment`. No tag changed; both texts now say what the rater could not see.
- **Human interventions:** none recorded in #52 to #54. In the sessions between track A and
  the close, the maintainer first deferred the dashboard's "Needs attention" fixes until all
  days were done, then moved them to right after track B: that became #55 and #56.
- **Hand-offs:** H08.1 (said vs done, its golden file and `bearing.toml.example`) was built in
  #53 and #54. H08.2, the kit's `bearing.toml` and run, stays with Day 10, and H09.1, a test
  for the branch's fallback, joins it.
- **Tokens:** `docs/dashboard/token-usage.json` tags three rows with Day 9, all on
  2026-11-05: the main session (98 replies, $4.67), the spec-auditor (48 replies, $1.65) and
  the implementer on Haiku (32 replies, $0.04). Day 8's close raised its main row from 61 to 82
  replies, and the untagged main row for 2026-11-05 rose from 47 to 241 replies ($13.46),
  mostly the two `tooling/` branches. The folder's total from 2026-10-28 to 2026-11-05 is
  $273.69, counted during the close, so the close's own session is only partly in it.

### Day 10: The kit's flags and the Phase 3 stop (Phase 3), closed in #65

- **Delivered:** `bearing direction` run on the kit at `c12cfe5`, its flags judged by the
  maintainer, in two rounds. Round 1 (#59, #60): the kit's `docs/kit/bearing.toml`, a report of
  72 flags, and marks of 17 `real`, short of the half Phase 3's "Done when" asks. The plan
  change (#60) added a `shared` list to the `outside-area` rule; Track C (#62) built it, and
  Track D (#63) re-ran the kit with round 2's config: 94 of 94 merges matched, 26 flags,
  `docs/kit/direction.md` 181 lines. Track B (#64) holds the marks in `docs/kit/flags.md`:
  "Marks: real 13, rule 13", exactly half. H09.1 got its test in #59. No migration, no
  contract change. `pytest -q`: 78 passed, 107 subtests passed.
- **Criteria:** 7 of 7 ticked: 5 `new` and 2 `hold`.
- **Breaks on purpose:** 10 in the PRs: 3 in #58, 1 in #59, 2 in #62, 3 in #63 and 1 in #64.
  8 are in `specs/breaks/day-10.json`, all replayed at the close, each failing its check. The
  other 2 ran on a scratch clone of the kit, which CI's replay does not have. #64's entry was
  adapted to run on CI and on a CRLF tree (D10.19).
- **PRs:** 8: the spec (#58), Track A (#59), a plan change (#60), a second spec change for
  round 2 (#61), Tracks C (#62), D (#63) and B (#64), and the close. No Track 0.
- **Defects:** 20 in the Notes: 19 at the close, and D10.20 added by #66.

  | Field | Count |
  | --- | --- |
  | found: auditor | 15 |
  | found: spec-change PR | 2 |
  | found: Track C | 1 |
  | found: close | 2 |
  | cause: spec | 18 |
  | cause: process | 2 |

  The spec-auditor found 15 before any code, the most of any day so far. They included a
  C10.5 test that passed on any well-formed file (D10.2), holds that were really `new` (D10.3,
  D10.13), and literal output in backticks (D10.10). Round 2 found one more in plan.md's own
  sentence (D10.17): round 1's 17 `real` flags shrink to 13 under the `shared` list it chose.
  Round 2's marks then gave exactly 13. Two got past the review: a break whose text `ruff
  format` had moved (D10.18) and a `manifest:` line CI could not replay (D10.19). CI's replay of
  #65's merge (`6036555`) then failed, "4 failed": four `broken:` lines the close kept could not
  be replayed (D10.20). #66 fixed them, and the replay on `b352eb2` holds (run 42038468893).
- **Human interventions:** 17 `human:` lines in #58 to #64, 12 of them in the marking. In
  round 1 (#60) the maintainer asked to be asked rather than read the 72 lines, and asked for a
  Fable analysis and Mermaid graphs of the choices. They chose Fable's marks (17 `real`) and
  the `shared` list. In round 2 (#64) they took Claude's suggestion after a blind Fable
  reading that differed on #16 and #31. Under Fable's marks alone, 11 would be `real` and
  Phase 3's "Done when" unmet: the count rests on two low-confidence marks.
- **Hand-offs:** H08.2 (the kit's run) and H09.1 (the branch's fallback) are done. H10.2 is
  closed by #64. H10.1, the Phase 3 stop, held in #67: the plan-auditor on Phase 3, Phase 4
  and the whole plan, Phase 4 going ahead with its flags marked unverified, and the kit copied
  in at `9a50a3e` in #68 (plan.md, "Course correction after Phase 3").
- **Tokens:** `docs/dashboard/token-usage.json` tags three rows with Day 10, all on
  2026-11-05: the main session (125 replies, $6.61), the spec-auditor (50 replies, $1.83) and
  the implementer on Haiku (30 replies, $0.03). The untagged rows for 2026-11-05 include the
  round 1 marking and the Fable runs: the main row rose from 241 to 430 replies ($24.25), and
  a `general-purpose` Fable row is new ($7.36). The folder's total from 2026-10-28 to
  2026-11-05 is $303.23, counted during the close.

### Day 11: The page's data and its layout (Phase 4), closed in #73

- **Delivered:** `bearing page <repo> --out <file>` writes one HTML file holding the
  `page-v1` data in a `bearing-data` element: one step per first-parent merge, with its number,
  title and paragraph (the changelog's choice), its structural events (the timeline's) and its
  flags (direction's, computed per merge). The contract is new: `tests/contract/test_page.py`
  and `tests/fixtures/expected/page-v1.json` (138 lines), in #70. #71 added the command's
  one-line errors, `--out` left alone when one happens, and every `<` in the element written as
  a JSON escape, so PR text cannot end it. #72 added `bearing/page/layout.py`: `layers`, the
  layered layout plan.md decided, each import cycle one node, the same under two hash seeds.
  The page does not draw yet (Day 12). No migration; no existing contract changed. `pytest -q`:
  89 passed, 109 subtests passed.
- **Criteria:** 9 of 9 ticked: 7 `new` and 2 `hold`.
- **Breaks on purpose:** 12, all in `specs/breaks/day-11.json`: 2 in #69, 3 in #70, 4 in #71
  and 3 in #72. The close replayed all 12 on `main`, each failing its check. #69's contract
  break now reports "6 passed" where it read "5 passed": Track A added a contract test.
- **PRs:** 5 at the day-spec rung: the spec (#69), Tracks A (#70), B (#71) and C (#72), and the
  close. No Track 0. Track A's diff was 398 changed lines, so the split the spec planned for
  it (D11.6) was not needed.
- **Defects:** 14 in the Notes.

  | Field | Count |
  | --- | --- |
  | found: auditor | 7 |
  | found: self | 1 |
  | found: break on purpose | 2 |
  | found: Track C | 2 |
  | found: review | 1 |
  | found: close | 1 |
  | cause: spec | 7 |
  | cause: process | 6 |
  | cause: implementation | 1 |

  The spec-auditor found seven before any code (D11.1 to D11.7), among them a JSON escape the
  Write tool had turned into its character, two wrong reds after Track A, and a stderr whose
  order the spec did not pin. In the tracks, five were the record around the code: the same
  Write tool escape in a commit message (D11.8), break finds that did not match (D11.9,
  D11.10), a brief's wrong merge walk (D11.11) and a test module that failed to load on `main`,
  which local `seen-red.py` printed as an error and CI's "Track tests seen red" refused
  (D11.13). One was the implementer's: a walk that gave the wrong 10 merges (D11.12). The close
  found Verify's subtest count off by two (D11.14). The blind relabel agreed on all 14 stages
  and `made:` tags and on 11 of 14 causes. The rater read D11.1 and D11.8 as `environment` and
  D11.13 as `implementation`. No tag changed; D11.8's and D11.13's texts now say why.
- **Human interventions:** 6 `human:` lines in #69 to #72. In #69 the maintainer started the
  day with the plan-auditor on Phase 4, pointed out a failing template check, and kept the
  spec's two decisions: a missing config is an error, and the layout stays out of `page-v1`.
  Each track and the close began from the previous session's suggested prompt.
- **Hand-offs:** H11.1 → Day 12: the graph drawn from `layers` as inline SVG in Mermaid's look,
  the step-through controls, every flag marked "unverified", the HTML's bytes the same under two
  hash seeds, and Phase 4's "Done when" on the kit at `c12cfe5`.
- **Tokens:** `docs/dashboard/token-usage.json` tags two rows with Day 11, on 2026-11-05: the
  main session (104 replies, $5.34) and the implementer on Haiku (59 replies, $0.08). The
  plan-auditor's and spec-auditor's runs are in the untagged rows for that date (109 replies,
  $3.83, and 105 replies, $4.03). The folder's total from 2026-10-28 to 2026-11-05 is $325.53,
  counted during the close, so the close's own session is only partly in it.

### Day 12: The timeline page, its graph and its controls (Phase 4), closed in #81

- **Delivered:** `bearing page` now writes a page a person can step through. #75 added
  `bearing/page/svg.py`: `draw(old, new, events)` draws a step's import graph as inline SVG in
  Mermaid's look, with the boxes in `layers`' rows, a wide layer wrapped at 960, added parts
  marked, removed ones faded, cycles in red, and module names escaped. #77 wrote one section per
  step around Day 11's data element: date, number, branch, events and paragraph, each flag as
  "unverified: ...", and a Previous/Next script with the arrow keys and a counter, with no
  `src=` and no outside URL. #80 put each step's graph into its section, the same bytes under
  two hash seeds. `page-v1` and every golden file are unchanged. No migration. `pytest -q`: 97
  passed, 109 subtests passed.
- **Criteria:** 10 of 10 ticked: 9 `new` and 1 `hold`.
- **Phase 4's "Done when", on the kit:** at `c12cfe5`, the page has 94 sections and 94 graphs,
  0 `src=` or `href="http`, and 2 `<script` and 2 `</script` (5317 lines). The maintainer
  stepped through the first merge (#1, 2026-10-28) and the last (#95, 2026-11-04) in a
  browser; the screenshots are in #81.
- **Breaks on purpose:** 10, all in `specs/breaks/day-12.json`: 1 in #74, 3 in #75, 4 in #77
  and 2 in #80. The close replayed all 10 on `main`, and each failed its check.
- **PRs:** 6 at the day-spec rung: the spec (#74), a second spec change (#76), Tracks A (#75),
  B (#77) and C (#80), and the close (#81); after the close, a third spec change moved the kit's
  commands out of Verify, and a fourth reworded three criteria's evidence so the dashboard
  counts it. No Track 0.
- **Defects:** 13 in the Notes (D12.10 added after the close, in the third spec change; D12.11
  to D12.13 in the fourth).

  | Field | Count |
  | --- | --- |
  | found: auditor | 6 |
  | found: self | 2 |
  | found: Track A | 1 |
  | found: close | 1 |
  | found: dashboard | 3 |
  | cause: spec | 8 |
  | cause: process | 4 |
  | cause: environment | 1 |

  The spec-auditor found six before any code (D12.1 to D12.6). Two were wrong numbers in the
  layout criterion, one was a drawing the spec left open, one a `hold` that passed with no
  graphs, one a grep that could not see CSS URLs, and one a repeat of D11.7's backticks. CI's
  "Track tests seen red" found the seventh on track A's PR: the Tracks table owned neither
  C12.8 nor C12.10 (D12.8), fixed in #76. The tracks recorded no mistake of their own. The close
  found two of its own slips: a break whose report said nothing (D12.7) and a replay script
  stopped by Windows' cp1252 (D12.9). The blind relabel agreed on all 9 causes, 7 of 8
  stages and 8 of 9 `made:` tags. D12.8's "found: CI" was not a README value and is now
  `found: Track A`. The rater read D12.9 as an escape outside any day; it stays `self` and
  `Day 12`. The evidence replay after #81 found D12.10: Verify held the kit's commands, which
  only the close's machine can run, and four of them failed in CI. They now sit in the Notes.
  The two screenshots were not in #81 when it merged; the maintainer pasted them in afterwards.
  The dashboard then found D12.11 to D12.13: the evidence of C11.8, C12.9 and C12.10 named no
  command it reads, C12.10's cited no PR of this repository, and C12.10's red line began "Red:"
  where it reads "Seen red". D12.11 is an escape from Day 11 (C11.8), recorded here, where it
  was found.
- **Human interventions:** 5 `human:` lines in #74 to #80. In #74 the maintainer started the
  day and set its order: the plan-auditor, then the spec-auditor, then the spec. In #76 they
  chose the spec-change PR over leaving #75's check red. Each track and the close began from
  the previous session's suggested prompt. At the close the maintainer stepped through the kit's
  page in a browser (C12.10).
- **Hand-offs:** Phase 4 ends here. The plan-auditor runs on Phase 4 and on the next phase, and
  the three end-of-phase auditors run once, all on fresh `main` after this close merges.
- **Tokens:** `docs/dashboard/token-usage.json` tags four rows with Day 12, on 2026-11-05: the
  main session (110 replies, $5.14), the implementer on Haiku (29 replies, $0.05), the
  plan-auditor (8 replies, $0.30) and the spec-auditor (27 replies, $0.88). The folder's total
  from 2026-10-28 to 2026-11-05 is $341.09, counted during the close, so the close's own
  session is only partly in it.

## What is being measured

| Question | Evidence it will be judged on |
| --- | --- |
| What does a merged PR cost, by rung? | `docs/dashboard/token-usage.json`; at the Day 4 and Day 10 stops, `scripts/token-usage.py --compare --split`, and per-rung counts by hand from the merged branches (plan.md, "Measurement") |
| Where are defects found, and what causes them? | Each day's `Defect` lines (`found:`, `cause:`, `made:`), the dashboard's defect-tag table, and the blind relabel at each close |
| Can each criterion's check fail? | The `broken:` lines under the ticked criteria, `specs/breaks/day-NN.json`, and the post-merge evidence replay (`evidence.yml`) |
| Does the work stay reviewable? | The PR diff stays under 400 changed lines; uses of `Oversized:` so far: none |

## Retrospective
