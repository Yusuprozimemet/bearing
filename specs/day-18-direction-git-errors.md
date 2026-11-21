# Day 18 — `direction`'s git errors in one line

**Phase:** 10 · **Depends on:** Day 17 · **Expected PRs:** 3 (this spec, track A, the close)

## Goal
`bearing direction` on a directory that is not a git repository prints
"bearing: not a git repository: <repo>", and on a repository that does not hold the store's
commits "bearing: not a commit: <sha>", the lines `timeline` gives, exit 1 and stdout empty,
where today it prints git's own text; and every new behaviour is a test CI runs (plan.md,
Phase 10).

## In scope
- **The check** (Track A), in `bearing/snapshot/tree.py`: the two checks `snapshot` runs first
  (`git rev-parse --git-dir`, then `git rev-parse --verify --quiet <ref>^{commit}`) move, word
  for word, into a new function `check_commit(repo, ref)`, which raises today's
  `SnapshotError("not a git repository: <repo>")` or `SnapshotError("not a commit: <ref>")` and
  otherwise returns the full SHA. `snapshot` calls it where the checks stood, so `timeline`,
  `page` and `snapshot` print what they print today (C18.4).
- **The diff's failure** (Track A), in `bearing/direction/changes.py`: where a commit's
  `git diff --numstat` exits non-zero, `check_commit(repo, sha)` runs before git's text is
  raised, so a wrong repository or a missing commit is `check_commit`'s line and any other
  failure keeps git's text. On success nothing more runs: no extra git call per commit. Every
  function in `changes.py` that runs that `git diff` (`changed_files` today; `commit_changes`
  too once Day 15 has landed, C15.1) goes through the one failure path.
- The first commit `direction` reads is the first stored commit with a parent
  (`parent_count > 0`, in `position` order), so that is the SHA the second line names. On the
  fixture it is `62c4b2fcda436266c9cdd7ec8db866427452cfb9`, #1's merge, the SHA `timeline`'s
  test names too (`tests/test_timeline_cli.py::TimelineCliTest::test_errors`).
- The new tests go in a new file, `tests/test_direction_repo.py`. Its class builds the fixture
  with `tests/fixtures/make_repo.py` once, in `setUpClass`, ingests it with the fixture's
  `prs.json` into a `--data` directory under the class's temporary directory, and makes there
  an empty directory and a repository with `git init -q` and no commit, as
  `tests/test_timeline_cli.py` does. It runs `python -m bearing` with `subprocess.run`, as
  `tests/test_direction_cli.py` does, with `--config tests/fixtures/bearing.toml`, and imports
  what it tests from `bearing` inside the test, so a missing name fails that test and not the
  file's collection.

## Out of scope
- A repository that holds a stored commit but not its first parent (a shallow clone): the
  check passes and git's text is raised as today. plan.md's Phase 10 names the two cases only.
- A `--repo` path that does not exist: it gets "bearing: not a git repository: <repo>" too,
  since `git -C` fails there as in a directory outside any repository (prototyped), but no
  criterion pins it; `timeline` has no test for it either.
- `direction`'s order of checks: the config, then the store, then git, as today
  (`tests/test_direction_cli.py::DirectionCliTest::test_errors`, C18.5).
- `timeline`'s and `page`'s own errors: unchanged (C18.4).
- A new contract version: `direction`'s report on the fixture is unchanged (C18.5, C18.6).
- `.github/`, `.claude/`, `scripts/`, `plan.md` and the dependencies: the day's code stays in
  `bearing/` and `tests/` (plan.md, Phases 7 to 10). C18.7 holds it.

## Tracks

One track. C18.1–C18.3 are `new`: Track A's PR shows their tests failing on `main`'s code with
`python scripts/seen-red.py -- python -m pytest -q tests/test_direction_repo.py::DirectionRepoTest::test_not_a_repo tests/test_direction_repo.py::DirectionRepoTest::test_not_a_commit tests/test_direction_repo.py::DirectionRepoTest::test_changed_files`,
which reports "3 failed". C18.8 is `hold` with a test Track A adds, without a Track 0 (as Day
17's C17.7): Track A's PR shows it passing on `main`'s code with
`python scripts/seen-red.py -- python -m pytest -q tests/test_direction_repo.py::DirectionRepoTest::test_one_git_call`,
which exits 1 ("passes there"), and then breaks it. C18.4–C18.7 are `hold` and their checks
exist: their breaks run in this spec's PR.

`tests/test_direction_repo.py` holds 4 tests and no subtests. So `python -m pytest -q` goes from
Day 17's end, "121 passed, 131 subtests passed", to "125 passed, 131 subtests passed".

| Track | Owner | Work |
|---|---|---|
| A | implementer | C18.1–C18.3, C18.8: `bearing/snapshot/tree.py`, `bearing/direction/changes.py`, `tests/test_direction_repo.py` |

## Acceptance criteria
Tick each box in the closing PR once its evidence is in it; under a box left unticked, write
`Not proven: <why>` (`specs/README.md`, "Evidence at the close").

- [x] C18.1 **new** — A directory that is not a git repository is one line. On the fixture's
      store, `direction <dir> --data <store> --config tests/fixtures/bearing.toml`, `<dir>` a
      new empty directory under the class's temporary directory, returns 1, its stdout is
      empty, and its stderr, read with `\r\n` as `\n` (`tests/test_direction_cli.py`'s `text`),
      is exactly "bearing: not a git repository: <dir>" and a line feed (`<dir>` as given).
      Red today: its stderr is "bearing: error: Could not access
      '62c4b2fcda436266c9cdd7ec8db866427452cfb9^1'".
      Test: `tests/test_direction_repo.py::DirectionRepoTest::test_not_a_repo`.
      Evidence: `DirectionRepoTest.test_not_a_repo` (#133), seen red in #133 on `main`'s code ("3 failed in 1.18s", the three `new` tests together) and again at the close on `bffafe1`'s code ("3 failed in 0.89s"); `python -m pytest -q` at the close on `9efc581` ("125 passed, 131 subtests passed").
      broken: check_commit not called on the git diff's failure → 3 failed in 2.92s (#133)
- [x] C18.2 **new** — A repository without the store's commits is one line. On the fixture's
      store, `direction <other> --data <store> --config tests/fixtures/bearing.toml`, `<other>`
      a repository the test makes with `git init -q` and no commit, returns 1, its stdout is
      empty, and its stderr, read as C18.1's, is exactly
      "bearing: not a commit: 62c4b2fcda436266c9cdd7ec8db866427452cfb9" and a line feed.
      Red today: its stderr is git's three lines, starting "bearing: fatal: ambiguous argument
      '62c4b2fcda436266c9cdd7ec8db866427452cfb9^1': unknown revision or path not in the working
      tree.".
      Test: `tests/test_direction_repo.py::DirectionRepoTest::test_not_a_commit`.
      Evidence: `DirectionRepoTest.test_not_a_commit` (#133), seen red in #133 on `main`'s code ("3 failed in 1.18s", the three `new` tests together) and again at the close on `bffafe1`'s code ("3 failed in 0.89s"); `python -m pytest -q` at the close on `9efc581` ("125 passed, 131 subtests passed").
      broken: check_commit not called on the git diff's failure → 3 failed in 2.92s (#133)
- [x] C18.3 **new** — `changed_files` raises the same lines, so the page's call reads them too.
      `bearing.direction.changes.changed_files(<dir>, "62c4b2fcda436266c9cdd7ec8db866427452cfb9")`,
      `<dir>` C18.1's directory, raises `SnapshotError` whose text is exactly
      "not a git repository: <dir>"; with C18.2's `<other>`, exactly
      "not a commit: 62c4b2fcda436266c9cdd7ec8db866427452cfb9".
      Red today: the first raises "error: Could not access
      '62c4b2fcda436266c9cdd7ec8db866427452cfb9^1'".
      Test: `tests/test_direction_repo.py::DirectionRepoTest::test_changed_files`.
      Evidence: `DirectionRepoTest.test_changed_files` (#133), seen red in #133 on `main`'s code ("3 failed in 1.18s", the three `new` tests together) and again at the close on `bffafe1`'s code ("3 failed in 0.89s"); `python -m pytest -q` at the close on `9efc581` ("125 passed, 131 subtests passed").
      broken: check_commit not called on the git diff's failure → 3 failed in 2.92s (#133)
- [x] C18.4 **hold** — `timeline`'s, `page`'s and `snapshot`'s errors stay word for word, and
      `changed_files` its return value (C08.2):
      `python -m pytest -q tests/test_timeline_cli.py tests/test_page_cli.py tests/test_snapshot_tree.py tests/test_snapshot_cli.py tests/test_changes.py`
      passes, and
      `git -c core.safecrlf=false diff --exit-code 714412f -- tests/test_timeline_cli.py tests/test_page_cli.py tests/test_snapshot_tree.py tests/test_snapshot_cli.py tests/test_changes.py`
      prints nothing and exits 0.
      This spec's PR breaks each half: "not a commit: " in `snapshot`'s message missing its
      colon, and a line of `tests/test_timeline_cli.py` changed.
      Evidence: at the close on `9efc581`, the five files printed "16 passed, 6 subtests
      passed", and the diff against `714412f` printed nothing and exited 0.
      broken: not a commit: in snapshot's message missing its colon → 4 failed, 14 passed, 4 subtests passed in 76.43s (0:01:16) (#106)
      broken: a line of tests/test_timeline_cli.py changed → import unittest (#106)
- [x] C18.5 **hold** — `direction`'s report and its other errors stay as they are:
      `python -m pytest -q tests/test_direction_cli.py` passes. Day 15 edits that file (C15.5's
      `test_threshold`), so this criterion has no `git diff` half against a fixed base; the
      day's own spec-auditor run pins one against Day 15's closing commit once it exists.
      This spec's PR breaks it: every line count read from git's numstat one too many.
      Evidence: at the close on `9efc581`, `python -m pytest -q tests/test_direction_cli.py`
      printed "5 passed"; #133's diff does not touch the file.
      broken: every line count read from git's numstat one too many → 3 failed, 2 passed in 9.72s (#106)
- [x] C18.6 **hold** — No contract changes: `python -m pytest -q tests/contract/` passes, and
      `git -c core.safecrlf=false diff --exit-code 714412f -- tests/contract/ tests/fixtures/expected/ tests/fixtures/make_repo.py`
      prints nothing and exits 0 (`714412f` is `main` with Day 14's spec merged, #99); and
      `python -m pytest -q` passes.
      This spec's PR breaks each half: the direction report's "## Coupling" heading misspelt,
      and a line of `tests/contract/test_direction.py` changed.
      Evidence: at the close on `9efc581`, `python -m pytest -q tests/contract/` printed "7
      passed", the diff against `714412f` printed nothing and exited 0, and `python -m pytest
      -q` printed "125 passed, 131 subtests passed".
      broken: the direction report's Coupling heading misspelt → 1 failed, 6 passed in 47.38s (#106)
      broken: a line of tests/contract/test_direction.py changed → ENV = {k: v for k, v in os.environ.items() if k not in ("GIT_DIR", "GIT_WORK_TREE")} (#106)
- [x] C18.7 **hold** — The day stays in `bearing/` and `tests/`, with no new dependency:
      `git -c core.safecrlf=false diff --exit-code --name-only 1472abc -- .github .claude scripts pyproject.toml plan.md`
      prints nothing and exits 0 (`1472abc` is `main` with Phases 11 to 16 merged, #118).
      This spec's PR breaks it: a line of `pyproject.toml` changed.
      Evidence: at the close on `9efc581` the check printed nothing and exited 0.
      broken: a line of pyproject.toml changed → pyproject.toml (#119)
- [x] C18.8 **hold** — The check costs nothing on success: one commit's files are one git call.
      `changed_files(<the fixture's repository>, "fde93a4")`, with `subprocess.run` patched by
      `unittest.mock.patch("subprocess.run", wraps=subprocess.run)`, returns C08.2's four rows
      (`tests/test_changes.py::ChangesTest::test_fixture_merge`) and the mock is called exactly
      once; and `commit_changes(<the same repository>, "fde93a4")` (Day 15, C15.1), patched the
      same way, also calls it exactly once, so the report's path is held too.
      Test: `tests/test_direction_repo.py::DirectionRepoTest::test_one_git_call`.
      Track A's PR breaks it: `check_commit` called before the `git diff`, not on its failure.
      Evidence: `DirectionRepoTest.test_one_git_call` (#133) passed on `main`'s code before
      the change (`seen-red.py` exit 1, "1 passed in 0.81s" in #133; "1 passed in 0.87s" on
      `bffafe1` at the close) and passed at the close on `9efc581`.
      broken: check_commit called before the git diff, not on its failure → 1 failed in 1.95s (#133)

## Verify
```bash
python -m pytest -q                                              # 125 passed, (131 subtests passed)
python -m pytest -q tests/test_direction_repo.py
python -m pytest -q tests/test_timeline_cli.py tests/test_page_cli.py tests/test_snapshot_tree.py tests/test_snapshot_cli.py tests/test_changes.py
python -m pytest -q tests/test_direction_cli.py
python -m pytest -q tests/contract/
git -c core.safecrlf=false diff --exit-code 714412f -- tests/test_timeline_cli.py tests/test_page_cli.py tests/test_snapshot_tree.py tests/test_snapshot_cli.py tests/test_changes.py
git -c core.safecrlf=false diff --exit-code 714412f -- tests/contract/ tests/fixtures/expected/ tests/fixtures/make_repo.py
git -c core.safecrlf=false diff --exit-code --name-only 1472abc -- .github .claude scripts pyproject.toml plan.md
ruff check . && ruff format --check .
```

## Notes
- What today's code does, run in this spec's session on `main` at `ad0b844`, on the fixture's
  store: `direction` on an empty directory outside any repository exits 1 with "bearing: error:
  Could not access '62c4b2fcda436266c9cdd7ec8db866427452cfb9^1'"; on an empty `git init`, with
  git's three lines from `git diff` ("fatal: ambiguous argument ...", "Use '--' to separate
  paths from revisions, like this:", "'git <command> [<revision>...] -- [<file>...]'"); on a
  path that does not exist, "bearing: fatal: cannot change to '<path>': No such file or
  directory".
- A prototype of In scope's two changes, run on a copy of `bearing/` in this spec's session,
  printed C18.1's and C18.2's lines, exit 1, and "bearing: not a git repository: <path>" for a
  path that does not exist; `direction` on the fixture printed the same bytes as `main`'s code.
- The check runs on the failure path only, not before every commit's `git diff`: `direction`
  on the kit's history reads one diff per commit, and a check before each would add two git
  calls to every one. C18.8 holds it.
- `tests/test_changes.py::ChangesTest::test_fixture_merge` already asserts that
  `changed_files(repo, "0" * 40)` raises `SnapshotError`, but not its text: on the fixture's
  repository it becomes "not a commit: 000…0", which the test does not read, so it holds
  unedited (C18.4).
- The page calls `snapshot` on a merge before `changed_files` (`bearing/page/data.py`), so its
  errors already are `snapshot`'s lines and do not change; C18.3 pins `changed_files` because
  it is the function the page and plan.md's Phase 10 share.
- Written ahead of its day, against `main` at `ad0b844`, before Days 14 to 17's code has merged
  (#101 open): the test count assumes they land as their specs say (plan.md, Course correction
  after Phase 6, item 6). Day 15 adds `commit_changes` to `changes.py` and moves the report onto
  it (C15.1, C15.4); Day 18's failure path is the `git diff` both functions run, so the day's
  spec-auditor run checks that it is one call site, or names both. It also re-pins C18.7's base
  if anything under its paths has merged since `85a21a1`.
- C18.7's base re-pinned after Day 15's track A (#116): the course correction after Day 15's
  track A (#118) edits `plan.md`, so on `1472abc` the check with base `85a21a1` printed
  "plan.md" and exited 1. Its base is now `1472abc`, #118's merge commit, as that change's item
  6 says, with `plan.md` still in the list: there it prints nothing and exits 0. Only the base
  moved.
- C18.4–C18.7's `git diff` checks are commands, not tests: plan.md's "every check is a test" is
  read as every new behaviour, as Days 15 to 17 did.
- Day 8's In scope says "a git error raises `SnapshotError` with git's stderr". That is In scope
  text, not a criterion: C08.2 says only "raises `SnapshotError`" and C08.7 covers the config and
  store errors, and no test reads `direction`'s git text, so no `Replaces:` line is needed.
- No hand-off ID names this gap: plan.md's Course correction after Phase 6, item 1, found it by
  running `direction` on a wrong repository.
- Spec-auditor, before this spec's PR: 4 findings, all fixed. C18.1 and C18.2 compared stderr
  raw, which on Windows ends `\r\n` and would stay red after the fix; In scope's "no extra git
  call" had no criterion (now C18.8); C18.4 left out `tests/test_snapshot_cli.py`, which pins
  `snapshot`'s two lines (C05.7); and C18.5 cited C15.4 for Day 15's edit to
  `tests/test_direction_cli.py`, which is C15.5's, and held two kit tests that read only
  `docs/kit/` and no break could fail. It confirmed every red state, the SHA, the bases, the
  count chain and the prototype, and found no hand-off to this day. Its guard blocked
  `git init`, so it ran C18.2's red state on a repository without the commit; this spec's
  session ran the empty `git init` (Notes, first line).
  The recheck found all four fixes right, and one note, taken: C18.8 counted `changed_files`'s
  calls only, so a check placed first in `commit_changes` would pass; it now counts both.
- **Defect** D18.1 — found: auditor · cause: spec · made: Day 18 · C18.1 and C18.2 read stderr
  raw, so on Windows the `\r\n` kept them red after the fix; now read with `\r\n` as `\n`.
- **Defect** D18.2 — found: auditor · cause: spec · made: Day 18 · In scope's "no extra git call
  per commit" had no criterion; C18.8 now holds it.
- **Defect** D18.3 — found: auditor · cause: spec · made: Day 18 · C18.4 held `snapshot`'s errors
  without `tests/test_snapshot_cli.py`, the test that pins them; added.
- **Defect** D18.4 — found: auditor · cause: spec · made: Day 18 · C18.5 cited C15.4 for C15.5's
  edit and held two kit tests no change to `bearing/` can fail; cite fixed, tests dropped.
- **Defect** D18.5 — found: maintainer · cause: spec · made: Day 18 · Verify's first comment,
  "125 passed, 131 subtests passed", is two parts to `scripts/evidence.py`, and "125 passed"
  never matches pytest's "125 passed, 131 subtests passed in …s", so the post-merge replay
  would have failed it as it failed Day 14's (D14.7). Now "125 passed, (131 subtests passed)",
  as Day 14's after #110 and Days 16 and 17's after #112 and #113: the subtest count is a note
  the replay does not check.
- Closed on `main` at `9efc581` (#133 merged), with Python 3.13.5 on Linux (WSL); CI runs 3.12.
  `python -m pytest -q` printed "125 passed, 131 subtests passed", as Tracks said; `ruff check .`
  found 74 EXE002 errors from this checkout's file modes and nothing else, `ruff check .
  --extend-ignore EXE002` passed, and `ruff format --check .` printed "122 files already
  formatted" (D18.6). CI's "Style check", "Tests" and "Track tests seen red" passed on #133.
- Seen red again at the close: `python scripts/seen-red.py --base bffafe1 -- python -m pytest -q`
  with C18.1–C18.3's three tests reported "3 failed in 0.89s", the spec's count; with C18.8's
  test it said "The check passed on bffafe1" ("1 passed in 0.87s"), as a `hold` should.
  `bffafe1` is `main` just before #133.
- All 8 breaks in `specs/breaks/day-18.json` were replayed at the close with `scripts/break.py`
  on `9efc581`, each failed its check, and each reported what its `broken:` line says, run
  times aside. C18.1–C18.3's and C18.8's are #133's; C18.4, C18.5 and C18.6's five are #106's;
  C18.7's is #119's, on base `1472abc`: #106's, on `85a21a1`, fails with no break in since
  #118, as Days 16 and 17 found. No entry needs an `at`: every text a break edits is still on
  `main`.
- C18.5's `git diff` half: the spec left it to the day's spec-auditor run, to pin against Day
  15's closing commit. #133's record shows no such run (D18.8), so no half was added; #133's
  diff does not touch `tests/test_direction_cli.py`, and the test passed at the close.
- Phase 10's "Done when" (plan.md): a directory that is not a git repository is C18.1, an empty
  `git init` made in the test C18.2, and the shared `changed_files` C18.3. Each is a test under
  `tests/` that CI's "Tests" check ran on #133.
- Track A (#133) was written by the implementer on Haiku from the main session's brief; the
  review found nothing to change in the code. #133's diff is 147 changed lines; the close
  re-counted 138 insertions and 9 deletions over its 3 files.
- This day leaves no new hand-off. It is Phase 10's only day, so after this close merges the
  next step is CLAUDE.md's step 6: the plan-auditor on Phase 10 and on Phase 11, in a new
  session.
- **Defect** D18.6 — found: Track A · cause: environment · made: none · same-as: D16.4 ·
  `ruff check .` failed locally with EXE002 errors (74 at the close) on files the day did not
  touch, from the checkout's mode bits; CI's check passed.
- **Defect** D18.7 — found: Track A · cause: process · made: Day 18 · the main session's brief
  for #133 told the implementer to pass `--config` to `ingest`, which has no such option; the
  implementer used `tests/test_direction_cli.py`'s `ingest` call instead, and #133's body said
  so.
- **Defect** D18.8 — found: close · cause: process · made: Day 18 · same-as: D17.6 · Day 18 is
  Phase 10's first day, and #133's body and commit record neither the plan-auditor on Phase 10
  nor the spec-auditor on the day before the track, as step 1 of CLAUDE.md asks, nor say they
  were skipped. The spec's own audit ran before #106.
- Blind relabel at the close (`scripts/relabel.py`, 8 entries): stage 2 of 7, cause 8 of 8,
  `made:` 8 of 8 agree. The rater read D18.1's "kept them red after the fix" as found during
  the track (`before_merge`); the fix never ran red: the Note above it says the spec-auditor
  found it before #106, where the stderr "would stay red", so `found: auditor` is kept. It left
  D18.2–D18.4's stage unclear: their text does not say when they were found, but the same Note
  does, so `found: auditor` is kept. It left D18.6's unclear; kept as Track A, since #133's body
  reported the local failure before it merged. D18.5's stage was not compared: `found:
  maintainer` is not one of `specs/README.md`'s values, kept as written, as D16.3 and D17.4.
  Every tag kept.
