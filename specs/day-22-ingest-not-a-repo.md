# Day 22 — `ingest`'s "not a git repository" in one line

**Phase:** 14 · **Depends on:** Day 21 · **Expected PRs:** 2 (track A, the close; this spec is in the Days 19 to 24 spec PR)

## Goal
`bearing ingest` on a directory that is not a git repository, or on a path that does not exist,
prints "bearing: not a git repository: <repo>", the line `snapshot`, `timeline`, `page` and
`direction` print, exit 1 and no store, where today it prints git's "fatal: ..." text; and every
new behaviour is a test CI runs (plan.md, Phase 14).

## In scope
- **The check** (Track A), in `bearing/snapshot/tree.py`: the first of Day 18's two checks in
  `check_commit(repo, ref)`, `git rev-parse --git-dir`, moves, word for word, into a new
  function `check_repo(repo)`, which raises today's `SnapshotError("not a git repository:
  <repo>")` and otherwise returns `None`. `check_commit` calls it where the check stood, so
  `snapshot`, `timeline`, `page` and `direction` print what they print today (C22.5).
- **`ingest`** (Track A), in `bearing/ingest/history.py`: `read_first_parent(repo,
  branch="main")`, Day 17's signature with its default kept, calls `check_repo(repo)` first, before Day 17's branch check, and raises
  `GitError(<the SnapshotError's text>)` from it, so `ingest`'s existing `except GitError`
  prints "bearing: not a git repository: <repo>", `<repo>` as given, exits 1 and writes no
  store. A repository with no such branch keeps Day 17's line, and any other git failure keeps
  git's text. The comment above Day 17's branch check, which says a failure outside a
  repository is left to `git log`, is rewritten to say what the code now does, without quoting
  git's old text.
- This replaces C17.7 and changes Day 17's In scope line "Any other failure of the check falls
  through to `git log`, so a directory that is not a git repository keeps today's error"
  (`specs/day-17-other-branch.md`). C17.7's test,
  `tests/test_ingest_branch.py::IngestBranchTest::test_not_a_repo`, is edited to the new line
  (C22.1); no other existing test changes.
- The other new tests go in a new file, `tests/test_ingest_repo.py`. Its class builds the
  fixture with `tests/fixtures/make_repo.py` once, in `setUpClass`, and runs `python -m bearing`
  with `subprocess.run` from the repository root, as `tests/test_ingest_cli.py` does, with a
  `--data` directory of its own. Its stderr is read as UTF-8 with `\r\n` as `\n`. It imports what
  it tests from `bearing` inside the test, so a missing name fails that test and not the file's
  collection.

## Out of scope
- git that cannot be run: `check_repo`'s `_git` raises "cannot run git in <repo>: <reason>",
  the text `ingest`'s `except OSError` prints today, so the line is unchanged; no criterion
  pins it, and no test runs `ingest` without git.
- A repository that is a bare or a shallow one: `git rev-parse --git-dir` passes, and what
  follows is as today.
- "Any other git failure keeps git's text": a repository that passes both checks and still
  fails `git log` is not one any test here makes (it takes a corrupted object store, such as the
  tip's object deleted), so no criterion pins it; a reviewer reads Track A's diff for
  `git log`'s `GitError` left as it is.
- One more git call per `ingest`: one `rev-parse` before Day 17's, on a command that runs once.
- A new contract version: `ingest`'s output on the fixture is unchanged (C22.6, C22.7).
- `.github/`, `.claude/`, `scripts/`, `plan.md` and the dependencies: the day's code stays in
  `bearing/` and `tests/` (plan.md, Phases 11 to 16). C22.8 holds it.

## Tracks

One track. C22.1–C22.3 are `new`: Track A's PR shows their tests failing on `main`'s code with
`python scripts/seen-red.py -- python -m pytest -q tests/test_ingest_branch.py::IngestBranchTest::test_not_a_repo tests/test_ingest_repo.py`,
which reports "3 failed". C22.4 holds Day 17's tests and C22.5 Day 18's as well as older ones.
Their `git diff` halves against Day 17's and Day 18's closes were pinned in Day 22's spec-change
PR, which broke them; Track A's PR breaks C22.4's test half and C22.5's third part, and the spec
PR for Days 19 to 24 broke C22.5's first two. C22.6–C22.8 are `hold` and their checks exist:
their breaks ran in that spec PR.

`tests/test_ingest_repo.py` holds 2 tests and no subtests, and the edited test stays one test.
So `python -m pytest -q` goes from Day 21's end, "144 passed, 131 subtests passed", to
"146 passed, 131 subtests passed".

| Track | Owner | Work |
|---|---|---|
| A | implementer | C22.1–C22.4: `bearing/snapshot/tree.py`, `bearing/ingest/history.py`, `tests/test_ingest_branch.py`, `tests/test_ingest_repo.py` |

## Acceptance criteria
Tick each box in the closing PR once its evidence is in it; under a box left unticked, write
`Not proven: <why>` (`specs/README.md`, "Evidence at the close").

- [x] C22.1 **new** — A directory that is not a git repository is one line. On a new empty
      temporary directory outside any repository,
      `ingest <it> --prs <the fixture's prs.json> --data <dir>` returns 1, its stdout is empty,
      its stderr is exactly "bearing: not a git repository: <it>" and a line feed (`<it>` as
      given), and `<dir>/bearing.db` does not exist.
      Red today: its stderr is "bearing: fatal: not a git repository (or any of the parent
      directories): .git".
      Test: `tests/test_ingest_branch.py::IngestBranchTest::test_not_a_repo`.
      Replaces: C17.7 — was: on a directory that is not a git repository, `ingest` returns 1,
      its stdout is empty, its stderr starts with "bearing: fatal: not a git repository", and
      no `bearing.db` is written.
      Evidence: `IngestBranchTest.test_not_a_repo` (#153), seen red in #153 on `main`'s code ("3 failed in 1.12s", the three `new` tests together) and again at the close on `456659b`'s code ("3 failed in 1.12s"); `python -m pytest -q` at the close on `5bbe4e1` ("146 passed, 131 subtests passed").
      No break of its own: the seen-red runs are what show it can fail.
- [x] C22.2 **new** — A path that does not exist is the same line. With `<repo>` a path under
      the class's temporary directory that does not exist,
      `ingest <repo> --prs <the fixture's prs.json> --data <dir>` returns 1, its stdout is
      empty, its stderr is exactly "bearing: not a git repository: <repo>" and a line feed, and
      `<dir>/bearing.db` does not exist.
      Red today: "bearing: fatal: cannot change to '<repo>': No such file or directory".
      Test: `tests/test_ingest_repo.py::IngestRepoTest::test_missing_path`.
      Evidence: `IngestRepoTest.test_missing_path` (#153), seen red in #153 on `main`'s code ("3 failed in 1.12s", the three `new` tests together) and again at the close on `456659b`'s code ("3 failed in 1.12s"); `python -m pytest -q` at the close on `5bbe4e1` ("146 passed, 131 subtests passed").
      No break of its own: the seen-red runs are what show it can fail.
- [x] C22.3 **new** — The check is one function. `bearing.snapshot.tree.check_repo(<the
      fixture's repository>)` returns `None`, and `check_repo(<a new empty temporary
      directory outside any repository>)` raises `SnapshotError` whose text is exactly "not a git repository: <it>".
      Red today: "ImportError: cannot import name 'check_repo'".
      Test: `tests/test_ingest_repo.py::IngestRepoTest::test_check_repo`.
      Evidence: `IngestRepoTest.test_check_repo` (#153), seen red in #153 on `main`'s code ("3 failed in 1.12s", the three `new` tests together) and again at the close on `456659b`'s code ("3 failed in 1.12s"); `python -m pytest -q` at the close on `5bbe4e1` ("146 passed, 131 subtests passed").
      No break of its own: the seen-red runs are what show it can fail.
- [x] C22.4 **hold** — Day 17's branch lines stay: `python -m pytest -q tests/test_ingest_branch.py`
      prints "6 passed, 3 subtests passed", and
      `diff --strip-trailing-cr <(git show bffafe1:tests/test_ingest_branch.py | head -n 211) <(head -n 211 tests/test_ingest_branch.py)`
      prints nothing and exits 0 (`bffafe1` is `main` with Day 17's close merged, #132; lines
      1–211 are the whole file but `test_not_a_repo`, its last function, which C22.1 edits).
      Track A's PR breaks the first: the branch check's result ignored, so a missing branch
      reaches `git log`. Day 22's spec-change PR breaks the second: a line of
      `test_not_a_branch` changed.
      Evidence: at the close on `5bbe4e1`, `python -m pytest -q tests/test_ingest_branch.py` printed "6 passed, 3 subtests passed", and the `diff` of lines 1–211 against `bffafe1` printed nothing and exited 0.
      broken: read_first_parent's branch check result ignored, so a missing branch reaches git log → 4 failed, 5 passed in 1.85s (#153)
      broken: a line of test_not_a_branch changed → >     def test_not_a_branch(self): (#151)
- [x] C22.5 **hold** — The other commands keep their lines:
      `python -m pytest -q tests/test_timeline_cli.py tests/test_page_cli.py tests/test_snapshot_tree.py tests/test_snapshot_cli.py`
      passes, and
      `git -c core.safecrlf=false diff --exit-code 714412f -- tests/test_timeline_cli.py tests/test_page_cli.py tests/test_snapshot_tree.py tests/test_snapshot_cli.py`
      prints nothing and exits 0; and `python -m pytest -q tests/test_direction_repo.py`
      (Day 18's) passes, and
      `git -c core.safecrlf=false diff --exit-code e72fc75 -- tests/test_direction_repo.py`
      prints nothing and exits 0 (`e72fc75` is `main` with Day 18's close merged, #134).
      The spec PR for Days 19 to 24 breaks the first two: "not a git repository: " in
      `snapshot`'s message reading "not a git repo: ", and a line of `tests/test_snapshot_cli.py`
      changed. Track A's PR breaks the third: `check_commit` no longer calling `check_repo`, its
      check gone. Day 22's spec-change PR breaks the fourth: a line of
      `tests/test_direction_repo.py` changed.
      Evidence: at the close on `5bbe4e1`, the four files' tests printed "14 passed, 6 subtests passed" and `tests/test_direction_repo.py` "4 passed"; the `git diff` against `714412f` and the one against `e72fc75` each printed nothing and exited 0.
      broken: snapshot's not a git repository message reading not a git repo → 2 failed, 14 passed, 4 subtests passed in 56.80s (#121)
      broken: a line of tests/test_snapshot_cli.py changed → import subprocess (#121)
      broken: check_commit no longer calling check_repo, its check gone → 2 failed, 2 passed in 1.82s (#153)
      broken: a line of tests/test_direction_repo.py changed → from unittest import mock (#151)
- [x] C22.6 **hold** — `ingest` on the fixture is unchanged:
      `python -m pytest -q tests/test_ingest_cli.py tests/test_history.py tests/test_entries.py`
      passes, and
      `git -c core.safecrlf=false diff --exit-code 714412f -- tests/test_ingest_cli.py tests/test_history.py tests/test_entries.py`
      prints nothing and exits 0.
      The spec PR breaks each half: `read_first_parent`'s `--first-parent` dropped, and a line
      of `tests/test_history.py` changed.
      Evidence: at the close on `5bbe4e1`, the three files' tests printed "8 passed, 5 subtests passed", and the `git diff` against `714412f` printed nothing and exited 0.
      broken: read_first_parent's --first-parent dropped → 4 failed, 4 passed, 2 subtests passed in 21.70s (#121)
      broken: a line of tests/test_history.py changed → import sys (#121)
- [x] C22.7 **hold** — No contract changes: `python -m pytest -q tests/contract/` passes, and
      `git -c core.safecrlf=false diff --exit-code 714412f -- tests/contract/ tests/fixtures/expected/ tests/fixtures/make_repo.py`
      prints nothing and exits 0 (`714412f` is `main` with Day 14's spec merged, #99); and
      `python -m pytest -q` passes.
      The spec PR breaks each half: the ingest report's "direct " missing its space, and a line
      of `tests/contract/test_fixture.py` changed.
      Evidence: at the close on `5bbe4e1`, `python -m pytest -q tests/contract/` printed "7 passed", the `git diff` against `714412f` printed nothing and exited 0, and `python -m pytest -q` printed "146 passed, 131 subtests passed".
      broken: the ingest report's direct missing its space → 1 failed, 6 passed in 46.25s (#121)
      broken: a line of tests/contract/test_fixture.py changed → import sys (#121)
- [x] C22.8 **hold** — The day stays in `bearing/` and `tests/`, with no new dependency:
      `git -c core.safecrlf=false diff --exit-code --name-only 1472abc -- .github .claude scripts pyproject.toml plan.md`
      prints nothing and exits 0 (`1472abc` is `main` with Phases 11 to 16 merged, #118).
      The spec PR breaks it: a line of `.claude/agents/spec-auditor.md` changed.
      Evidence: at the close on this branch, which changes only `specs/` and `docs/`, the `git diff --name-only` against `1472abc` printed nothing and exited 0.
      broken: a line of .claude/agents/spec-auditor.md changed → .claude/agents/spec-auditor.md (#121)

## Verify
```bash
python -m pytest -q                                              # 146 passed, (131 subtests passed)
python -m pytest -q tests/test_ingest_repo.py tests/test_ingest_branch.py
python -m pytest -q tests/test_timeline_cli.py tests/test_page_cli.py tests/test_snapshot_tree.py tests/test_snapshot_cli.py tests/test_direction_repo.py
python -m pytest -q tests/test_ingest_cli.py tests/test_history.py tests/test_entries.py
python -m pytest -q tests/contract/
diff --strip-trailing-cr <(git show bffafe1:tests/test_ingest_branch.py | head -n 211) <(head -n 211 tests/test_ingest_branch.py)
git -c core.safecrlf=false diff --exit-code e72fc75 -- tests/test_direction_repo.py
git -c core.safecrlf=false diff --exit-code 714412f -- tests/test_timeline_cli.py tests/test_page_cli.py tests/test_snapshot_tree.py tests/test_snapshot_cli.py
git -c core.safecrlf=false diff --exit-code 714412f -- tests/test_ingest_cli.py tests/test_history.py tests/test_entries.py
git -c core.safecrlf=false diff --exit-code 714412f -- tests/contract/ tests/fixtures/expected/ tests/fixtures/make_repo.py
git -c core.safecrlf=false diff --exit-code --name-only 1472abc -- .github .claude scripts pyproject.toml plan.md
ruff check . && ruff format --check .
```

## Notes
- What today's code does, run in the spec PR's session on `main` at `8a17f82` with Python
  3.12.10 and git for Windows, with the fixture's `prs.json`: an empty directory outside any
  repository gives "bearing: fatal: not a git repository (or any of the parent directories):
  .git", and a path that does not exist "bearing: fatal: cannot change to '<path>': No such
  file or directory", each exit 1 and no store. `git -C <path> rev-parse --git-dir` fails for
  both, which is why one check covers them (Day 18's Out of scope found the same for
  `direction`).
- `tests/test_ingest_cli.py::IngestCliTest::test_errors` runs `ingest` on an empty directory and
  checks only that stderr starts "bearing: ", so it passes unedited (C22.6).
- `bearing/ingest/history.py` importing from `bearing/snapshot/tree.py` adds no cycle: `tree.py`
  imports only `bearing.snapshot.modules`.
- Written ahead of its day, against `main` at `8a17f82`, before the code of Days 15 to 21 has
  merged: `check_commit` is Day 18's (C18.1–C18.3) and `read_first_parent`'s branch check Day
  17's, and the test count assumes they land as their specs say (plan.md, Course correction
  after Day 15's track A, item 5). The day's own spec-auditor run reads this spec against `main`
  as it is then, pins C22.4's base, and re-pins C22.8's if anything under its paths has merged
  since `1472abc`. Done in Day 22's spec-change PR, below: C22.4 pinned at `bffafe1`, C22.8 left
  at `1472abc`.
- C22.5–C22.8's `git diff` checks are commands, not tests: plan.md's "every check is a test" is
  read as every new behaviour, as Days 15 to 18 did.
- No hand-off ID names this gap: plan.md's Course correction after Day 15's track A, items 1 and
  4, found it and chose the replacement.
- Spec-auditor, in the spec PR for Days 19 to 24 (one run over all six): three findings here,
  all fixed. In scope wrote `read_first_parent(repo, branch)` without Day 17's default, which
  `tests/test_mapping.py` and `tests/test_history.py` rely on; "any other git failure keeps
  git's text" had no criterion (Out of scope now says so); and C22.3's directory was not said
  to be outside any repository. It confirmed both red states, that `snapshot` already prints
  the line for both, and that the import adds no cycle.
- **Defect** D22.1 — found: auditor · cause: spec · made: Day 22 · In scope's
  `read_first_parent(repo, branch)` dropped Day 17's `branch="main"` default; now written.
- **Defect** D22.2 — found: auditor · cause: spec · made: Day 22 · In scope's "any other git
  failure keeps git's text" had no criterion and no Out of scope line; Out of scope now leaves it
  to review.
- **Defect** D22.3 — found: auditor · cause: spec · made: Day 22 · C22.3's empty directory was
  not said to be outside any repository, so a test could make it inside one; now said.
- First-day audits, on `main` at `8596edd` (Linux under WSL, Python 3.13.5), in the spec-change
  PR: the plan-auditor on Phase 13 (just ended, CLAUDE.md's step 6) and Phase 14, consistent,
  four findings; the spec-auditor on the day, four findings. C22.1–C22.3 red as written (scratch
  copies of the three tests on `main`'s code gave "3 failed", with the three red lines the
  criteria quote; a scratch prototype of Track A collected 146 tests). `python -m pytest -q`
  "144 passed, 131 subtests passed"; `tests/test_ingest_branch.py` "6 passed, 3 subtests
  passed"; the `git diff` checks of C22.5–C22.8 each printed nothing and exited 0, and nothing
  under C22.8's paths changed since `1472abc`, so no re-pin. Every `hold`'s break, tried on a
  scratch copy, failed its check. Their findings: C22.4 had no pinned base and Tracks said Day
  17's and Day 18's files were not on `main` (fixed: `bffafe1`, as the Note above asked; not a
  defect); C22.5 ran `tests/test_direction_repo.py` without pinning it (fixed, D22.4);
  `history.py`'s comment above the branch check will be false after Track A (fixed in In scope,
  D22.5); the local `ruff check .` EXE002 errors (77, D21.4), not a spec defect, for the close to
  record again; plan.md's "any other git failure keeps git's text" has no criterion, already
  left to review by Out of scope (known limit); and this record of the audits (fixed, here).
- **Defect** D22.4 — found: auditor · cause: spec · made: Day 22 · C22.5 ran
  Day 18's `tests/test_direction_repo.py` but had no `git diff` half, so an edited test would
  still pass it; now pinned at `e72fc75`.
- **Defect** D22.5 — found: auditor · cause: spec · made: Day 22 · In scope left
  `history.py`'s comment that a failure outside a repository goes to `git log`, which Track A
  makes false; In scope now has Track A rewrite it.
- Closed on `main` at `5bbe4e1` (Linux under WSL, Python 3.13.5), branch
  `day-22/close-the-day`. `python -m pytest -q` printed "146 passed, 131 subtests passed", the
  spec's count; `tests/test_ingest_repo.py tests/test_ingest_branch.py` "8 passed, 3 subtests
  passed". `ruff format --check .` printed "126 files already formatted"; `ruff check .`
  reported 78 errors, every one EXE002, and passed with `--extend-ignore EXE002` (D22.6).
- Seen red again at the close: `python scripts/seen-red.py --base 456659b -- python -m pytest -q
  tests/test_ingest_branch.py::IngestBranchTest::test_not_a_repo tests/test_ingest_repo.py`
  reported "3 failed in 1.12s", the spec's count. `456659b` is `main` just before #153.
- All 11 breaks in `specs/breaks/day-22.json` were replayed at the close with `scripts/break.py`
  on `5bbe4e1`'s code, each failed its check, and each reported what its `broken:` line says,
  run times aside. C22.4's test half and C22.5's third part are #153's; C22.4's `diff` half and
  C22.5's fourth part are #151's; C22.5's first two, C22.6's two, C22.7's two and C22.8's one
  are #121's. None needs an `at`: #153 moved the `"not a git repository: {repo}"` line into
  `check_repo` word for word, so #121's find still matches once.
- C22.1–C22.3 have no break of their own: the seen-red runs, on `main`'s code in #153 and on
  `456659b` at the close, are what show their tests can fail.
- Phase 14's "Done when" (plan.md): the empty temporary directory is C22.1, the path that does
  not exist C22.2 and the one function C22.3, each a test under `tests/` that CI's "Tests" check
  ran on #153 (15 checks passed, 2 skipped); the missing-branch line unchanged is C22.4.
- Track A (#153) was written by the implementer on Haiku from the main session's brief. The
  close re-counted its diff from `git diff --numstat 456659b 5bbe4e1`: 83 changed lines
  (`bearing/ingest/history.py` 8+/2−, `bearing/snapshot/tree.py` 5+/1−,
  `tests/test_ingest_branch.py` 1+/1−, `tests/test_ingest_repo.py` 65+).
- `docs/dashboard/token-usage.json`, refreshed at the close, is unchanged: 87 rows, from
  2026-10-28 to 2026-11-21, $361.85; it tags no row with Day 22.
- This day leaves no new hand-off. It is Phase 14's only day, so after this close merges the
  next step is CLAUDE.md's step 6: the plan-auditor on Phase 14 and on Phase 15, in a new
  session.
- **Defect** D22.6 — found: Track A · cause: environment · made: none · same-as: D21.4 ·
  `ruff check .` failed locally with EXE002 errors (77 in #153, 78 at the close), from the
  checkout's file modes and on no line the day wrote; CI's check passed.
- **Defect** D22.7 — found: Track A · cause: process · made: Day 22 · Track A's first try at
  C22.5's third break gave `scripts/break.py` a two-line `--find`, which matched nothing on the
  CRLF tree; `break.py` refused it ("--find occurs 0 times") and changed nothing, and the break
  was rerun with a one-line find.
- Blind relabel at the close (`scripts/relabel.py compare`): stage 7 of 7 agree, cause 7 of 7,
  `made:` 7 of 7. No disagreement, so no tag changed.
