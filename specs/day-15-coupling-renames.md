# Day 15 — Coupling follows renames

**Phase:** 7 · **Depends on:** Day 14 · **Expected PRs:** 3 (this spec, track A, the close)

## Goal
A file renamed on the first-parent line is one file in `bearing direction`'s Coupling, named by
its last name, so the fixture at `min_prs = 2` gains the pair `scripts/run.py`,
`scripts/tools.py` (#2, #8), and every new behaviour is a test CI runs (plan.md, Phase 7).

## In scope
- **A commit's renames** (Track A), in `bearing/direction/changes.py`:
  - `parse_renames(raw)` reads the same `git diff --numstat -z -M` bytes `parse_numstat` reads
    and returns the commit's renames as a list of `(old, new)` path pairs, in the order git
    prints them, decoded as `parse_numstat` decodes paths; `[]` when there are none. git's own
    pairing (`-M`, its default similarity) is the only rename rule.
  - `commit_changes(repo, sha)` runs that one `git diff` and returns
    `(parse_numstat(raw), parse_renames(raw))`, raising `SnapshotError` as `changed_files` does.
  - `parse_numstat` and `changed_files` keep their return values (C08.2): churn, said vs done
    and the page (`bearing/page/data.py` calls `changed_files`) read paths as each commit
    changed them.
- **Last names** (Track A), in `bearing/direction/coupling.py`: `latest_names(commits)` takes
  the commits in first-parent order, each a `(paths, renames)` pair (the paths as that commit
  changed them, a renamed file under its new name, and its renames), and returns one list per
  commit, its paths in the order given, each replaced by the name its file has after the last
  rename that reaches it, through a chain of renames. A path used again after its file was
  renamed away is a new file: it keeps its own name, and the renamed file keeps the new one. A
  path no rename reaches keeps its name. `coupling` itself is unchanged (C08.4's test,
  `tests/test_coupling.py`, stays unedited).
- **The report** (Track A), in `bearing/direction/report.py`: each commit churn reads
  (`parent_count > 0`: merges and direct commits) is read once, with `commit_changes`, in place
  of `changed_files`; the renames of all of them go to `latest_names`, and the merges' paths
  are passed to `coupling` by their last names. Churn and said vs done keep the paths as
  changed.
- The new tests go in a new file, `tests/test_renames.py`, each importing what it tests inside
  the test (as `tests/test_changes.py` does), so a missing name fails that test and not the
  file's collection. C08.6's test,
  `tests/test_direction_cli.py::DirectionCliTest::test_threshold`, gains the fourth row (C15.5
  replaces C08.6).

## Out of scope
- A file deleted in one commit and added again later: no rename joins them, so it stays one
  path. Not asked for.
- Renames off the first-parent line (inside a PR's branch): each merge is diffed against its
  first parent, as Day 2's Notes and Day 8 do; a rename inside a branch shows as git pairs it
  in the merge's diff.
- Churn and said vs done by last name: plan.md, Phase 7, keeps them on the paths as changed.
- The kit's report, `docs/kit/direction.md`: a committed file from Day 10's run, not run again;
  `tests/test_kit_report.py` and `tests/test_kit_flags.py` read it as it is.
- A new contract version: at `min_prs = 3`, the golden file's threshold, the output does not
  change (plan.md, Course correction after Phase 6, item 2).
- `.github/`, `.claude/`, `scripts/`, `plan.md` and the dependencies: the day's code stays in
  `bearing/` and `tests/` (plan.md, Phases 7 to 10). C15.8 holds it.

## Tracks

One track. C15.1–C15.5 are `new`: Track A's PR shows their five tests failing on `main`'s code
with
`python scripts/seen-red.py -- python -m pytest -q tests/test_renames.py tests/test_direction_cli.py::DirectionCliTest::test_threshold`,
which reports "5 failed". C15.6–C15.8 are `hold` and their checks exist: their breaks run in
this spec's PR.

`tests/test_renames.py` holds 4 tests and no subtests; `test_threshold` stays one test. So
`python -m pytest -q` goes from Day 14's end, "107 passed, 128 subtests passed", to "111 passed,
128 subtests passed".

| Track | Owner | Work |
|---|---|---|
| A | implementer | C15.1–C15.5: `bearing/direction/changes.py`, `coupling.py`, `report.py`, `tests/test_renames.py`, `tests/test_direction_cli.py` |

## Acceptance criteria
Tick each box in the closing PR once its evidence is in it; under a box left unticked, write
`Not proven: <why>` (`specs/README.md`, "Evidence at the close").

- [ ] C15.1 **new** — Numstat bytes holding a rename give its old and new path, in git's order.
      `parse_renames` gives, for
      `b"3\t1\tapp/a.py\x00-\t-\tlogo.png\x000\t0\t\x00scripts/helpers.py\x00scripts/tools.py\x001\t0\t\x00docs/old.md\x00docs/new.md\x00"`,
      `[("scripts/helpers.py", "scripts/tools.py"), ("docs/old.md", "docs/new.md")]`; for
      `b"3\t1\tapp/a.py\x00"`, `[]`; and for `b""`, `[]`. `commit_changes("no-such-repo", "HEAD")`
      raises `SnapshotError`, as `changed_files` does.
      Red today: the import of `parse_renames` from `bearing.direction.changes` fails.
      Test: `tests/test_renames.py::RenamesTest::test_parse_renames`.
- [ ] C15.2 **new** — A chain of renames is one file, named by its last name. `latest_names` gives,
      for `[(["a.py"], []), (["b.py", "x.py"], [("a.py", "b.py")]), (["c.py"], [("b.py", "c.py")])]`,
      `[["c.py"], ["c.py", "x.py"], ["c.py"]]`.
      Red today: the import of `latest_names` from `bearing.direction.coupling` fails.
      Test: `tests/test_renames.py::RenamesTest::test_chain`.
- [ ] C15.3 **new** — A path used again after its file was renamed away is a second file.
      `latest_names` gives, for
      `[(["a.py", "x.py"], []), (["b.py"], [("a.py", "b.py")]), (["a.py", "x.py"], [])]`,
      `[["b.py", "x.py"], ["b.py"], ["a.py", "x.py"]]`.
      Red today: as C15.2.
      Test: `tests/test_renames.py::RenamesTest::test_reused_path`.
- [ ] C15.4 **new** — The report follows a rename made by a direct commit, reads each commit with
      one `commit_changes` call, and keeps churn and said vs done on the paths as changed. The
      test builds a store with `bearing.store.db.open_store` in a temporary directory, holding
      four commits (`sha`, `position`, `parent_count`, `kind`, `pr_number`, `committed_at`):
      `r0`, 0, 0, direct, none, 2026-01-04; `m1`, 1, 2, merge, 1, 2026-01-05; `d2`, 2, 1,
      direct, none, 2026-01-06; `m3`, 3, 2, merge, 2, 2026-01-07 (each at `T12:00:00+00:00`,
      `subject` ""), and PRs 1 and 2 with `title` "", body "", `base_ref` "main" and
      `head_ref` "x/one" and "x/two". It patches `bearing.direction.report.commit_changes` with
      a fake that records each `sha` it is called with and returns, for `m1`,
      `([("old/m.py", 3, 0), ("x/y.py", 1, 0)], [])`; for `d2`,
      `([("new/m.py", 0, 0)], [("old/m.py", "new/m.py")])`; for `m3`,
      `([("new/m.py", 2, 0), ("x/y.py", 1, 0)], [])`; and raising `KeyError` for any other.
      `direction_report("no-such-repo", conn, [("old", ("old/",)), ("new", ("new/",)), ("x", ("x/",))], 2, [("outside-area", ())])`
      returns these 18 lines: "## Churn", "", "| Week | Area | Added | Deleted |",
      "|---|---|---|---|", "| 2026-W02 | new | 2 | 0 |", "| 2026-W02 | old | 3 | 0 |",
      "| 2026-W02 | x | 2 | 0 |", "", "## Coupling", "",
      "| File | File | PRs | Hidden dependency |", "|---|---|---|---|",
      "| new/m.py | x/y.py | #1, #2 | new, x |", "", "## Said vs done", "",
      "- #1 outside-area: area x | old/m.py", "- #2 outside-area: area x | new/m.py";
      and the fake was called exactly with `m1`, `d2`, `m3`, in that order, once each.
      A report that read merges' renames only gives no Coupling row; one that called git besides
      raises `SnapshotError` on "no-such-repo"; one that called `commit_changes` twice for a
      commit fails the recorded calls; one that gave churn or said vs done last names gives
      "| 2026-W02 | new | 5 | 0 |" or "#1 ... | new/m.py".
      Red today: patching `bearing.direction.report.commit_changes` raises `AttributeError`, as
      `report.py` has no such name.
      Test: `tests/test_renames.py::RenamesTest::test_report_direct_rename`.
- [ ] C15.5 **new** — On the fixture, after `bearing ingest` with its `prs.json`, `bearing direction`
      with a copy of `tests/fixtures/bearing.toml` at `min_prs = 2`, written in the test, prints
      the Churn section of today and a Coupling table of exactly four rows, in this order, the
      next line blank:
      "| app/b.py | app/core.py | #3, #9 | no |",
      "| app/b.py | src/lib/util.py | #3, #9 | app, lib |",
      "| app/core.py | src/lib/util.py | #1, #3, #9 | app, lib |" and
      "| scripts/run.py | scripts/tools.py | #2, #8 | no |"
      (#2 changed `scripts/helpers.py`, which #8 renamed to `scripts/tools.py`); at
      `min_prs = 4` no row follows the table's separator line and the next line is blank.
      Red today: the fourth row is missing; the line after the third row is blank where the test
      expects the fourth row, and `test_threshold` fails.
      Test: `tests/test_direction_cli.py::DirectionCliTest::test_threshold`.
      Replaces: C08.6 — was: at `min_prs = 2` the fixture's Coupling table is exactly three rows,
      the three above without `scripts/run.py`, `scripts/tools.py`.
- [ ] C15.6 **hold** — At `min_prs = 3`, the golden file's, the output is unchanged, and no
      contract changes: `python -m pytest -q tests/contract/test_direction.py` passes, and
      `git -c core.safecrlf=false diff --exit-code 714412f -- tests/contract/ tests/fixtures/expected/`
      prints nothing and exits 0 (`714412f` is `main` with Day 14's spec merged, #99); and
      `python -m pytest -q` passes.
      This spec's PR breaks each half: coupling's threshold lowered by one, and a line of
      `tests/contract/test_direction.py` changed.
- [ ] C15.7 **hold** — `parse_numstat` and `changed_files` keep their return values (C08.2) and
      `coupling` its (C08.4): `python -m pytest -q tests/test_changes.py tests/test_coupling.py`
      passes, and
      `git -c core.safecrlf=false diff --exit-code 714412f -- tests/test_changes.py tests/test_coupling.py`
      prints nothing and exits 0.
      This spec's PR breaks each half: `parse_numstat` naming a rename by its old path, and a
      line of `tests/test_coupling.py` changed.
- [ ] C15.8 **hold** — The day stays in `bearing/` and `tests/`, with no new dependency:
      `git -c core.safecrlf=false diff --exit-code --name-only 1472abc -- .github .claude scripts pyproject.toml plan.md`
      prints nothing and exits 0 (`1472abc` is `main` with Phases 11 to 16 merged, #118).
      This spec's PR breaks it: a line of `pyproject.toml` changed.

## Verify
```bash
python -m pytest -q                                              # 111 passed, (128 subtests passed)
python -m pytest -q tests/test_renames.py tests/test_direction_cli.py tests/contract/test_direction.py
python -m pytest -q tests/test_changes.py tests/test_coupling.py
git -c core.safecrlf=false diff --exit-code 714412f -- tests/contract/ tests/fixtures/expected/
git -c core.safecrlf=false diff --exit-code 714412f -- tests/test_changes.py tests/test_coupling.py
git -c core.safecrlf=false diff --exit-code --name-only 1472abc -- .github .claude scripts pyproject.toml plan.md
ruff check . && ruff format --check .
```

## Notes
- What the fixture gives: a prototype of `parse_renames` and `latest_names`, run in this spec's
  session on the fixture built by `tests/fixtures/make_repo.py` (HEAD `8c1b9f1`), printed the four
  rows of C15.5 at `min_prs = 2` and the golden file's one row at 3. The fixture has one rename
  on the first-parent line, `scripts/helpers.py` to `scripts/tools.py` in #8's merge
  (`fde93a4`); #2 modified `scripts/helpers.py` and added `scripts/run.py`. No direct commit on
  the fixture renames a file, and `make_repo.py` is frozen, so C15.4 builds its own store.
- C15.4's 18 lines: today's `direction_report` on that store, with `changed_files` faked to give
  the same files, printed the same lines without the Coupling row (run in this spec's session).
- The page's golden file names `scripts/run.py` and neither `scripts/helpers.py` nor
  `scripts/tools.py`, so it does not tell paths as changed from last names; C08.2's
  `test_fixture_merge`, which C15.7 holds unedited, pins `changed_files` at #8, and the page
  reads `changed_files`.
- A commit that swaps two names (a→b and b→a) is not tested.
- Day 8's Out of scope ("The fixture's one rename (#8) is in no pair at 2 or 3") held for paths
  as changed; followed, it is in one pair at 2 (plan.md, Course correction after Phase 6, item 2).
- Written ahead of its day, against `main` at `85a21a1`, before Day 14's code has merged (#101
  open): the test count assumes Day 14 lands as its spec says (plan.md, Course correction after
  Phase 6, item 6). The day's own spec-auditor run re-pins C15.8's base to `main` before the
  day if anything under its paths has merged since `85a21a1`. Audited on `02362b0`: Day 14
  merged as specified ("107 passed, 128 subtests passed"), and nothing under C15.8's paths has
  merged since `85a21a1`, so its base stands.
- C15.8's base re-pinned after track A (#116): the course correction after Day 15's track A
  (#118) edits `plan.md`, so on `1472abc` the check with base `85a21a1` printed "plan.md" and
  exited 1. Its base is now `1472abc`, #118's merge commit, as that change's item 6 says, with
  `plan.md` still in the list: there it prints nothing and exits 0. Only the base moved.
- C15.6–C15.8's `git diff` checks are commands, not tests: plan.md's "every check is a test"
  is read as every new behaviour, as Day 14's C14.4 and C14.5 did.
- Spec-auditor, before this spec's PR: 6 findings, all fixed. One seen-red command for the
  `new` tests would stop at `tests/test_renames.py`'s import error and never run
  `test_threshold` (imports moved inside each test); churn and said vs done on paths as
  changed, and renames from direct commits, had no test (C15.4 added); "the same git call" had
  no named function or check (`commit_changes`, checked by C15.4); C15.8's base may move before
  the day (the Note above); the `git diff` halves had no break (a second break each).
- Spec-auditor's recheck: the six fixes hold (C15.4's 18 lines, its red and its breaks
  prototyped), and 3 findings, all fixed: a second `commit_changes` call per commit passed
  C15.4 (the calls now recorded); C15.4's rows left out three NOT NULL columns (`subject`,
  `title`, `base_ref` given); `commit_changes`' `SnapshotError` had no test (added to C15.1).
- **Defect** D15.1 — found: auditor · cause: spec · made: Day 15 · the one seen-red command for
  C15.1–C15.4 stopped at `tests/test_renames.py`'s import error, so `test_threshold` was never
  shown red; the tests now import inside each test, and the run reports "5 failed".
- **Defect** D15.2 — found: auditor · cause: spec · made: Day 15 · no criterion checked that churn
  and said vs done keep the paths as changed; C15.4 added.
- **Defect** D15.3 — found: auditor · cause: spec · made: Day 15 · renames from direct commits,
  which plan.md's Phase 7 asks for, were left to a reviewer though a test without `make_repo.py`
  reaches them; C15.4 added.
- **Defect** D15.4 — found: auditor · cause: spec · made: Day 15 · "the same git call per commit"
  named no function and had no check; `commit_changes` named, and C15.4 fails on a second git call.
- **Defect** D15.5 — found: auditor · cause: spec · made: Day 15 · C15.8's base, `85a21a1`, is
  fixed ahead of the day and a later merge under its paths would fail it; the Notes say the
  day's audit re-pins it.
- **Defect** D15.6 — found: auditor · cause: spec · made: Day 15 · the `hold` breaks changed only
  `bearing/` code, so the `git diff` half of C15.6 and C15.7 was never seen to fail, and the Goal
  called those diffs tests; a second break each, and the Goal reworded.
- **Defect** D15.7 — found: auditor · cause: spec · made: Day 15 · D15.4's fix checked a second git
  call but not a second `commit_changes` call, which never reaches git and passed C15.4; the
  fake now records its calls.
- **Defect** D15.8 — found: auditor · cause: spec · made: Day 15 · C15.4's store rows left out
  `commits.subject`, `prs.title` and `prs.base_ref`, which are NOT NULL, so the test as written
  failed at its inserts; the three given.
- **Defect** D15.9 — found: auditor · cause: spec · made: Day 15 · `commit_changes` raising
  `SnapshotError` had no test once the report stops calling `changed_files`; added to C15.1.
- **Defect** D15.10 — found: auditor · cause: spec · made: Day 15 · Verify's first comment,
  "111 passed, 128 subtests passed", is two parts to `scripts/evidence.py`, and "111 passed"
  never matches pytest's "111 passed, 128 subtests passed in …s", so the post-merge replay
  would have failed it as it failed Day 14's (D14.7), a spec written before that fix. Now "111
  passed, (128 subtests passed)", as Day 14's after #110: the subtest count is a note the
  replay does not check.
