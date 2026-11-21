# Day 17 — A branch other than `main`

**Phase:** 9 · **Depends on:** Day 16 · **Expected PRs:** 3 (this spec, track A, the close)

## Goal
`bearing ingest <repo> --branch NAME` stores NAME's first-parent line and asks `gh` only for
the PRs merged into NAME; a NAME that is not a local branch is one line on stderr, exit 1 and no
store, where a repository without `main` gives git's "fatal: bad revision 'main'" today; and
every new behaviour is a test CI runs (plan.md, Phase 9).

## In scope
- **The option** (Track A), in `main` in `bearing/cli.py`: `ingest` takes `--branch NAME`,
  default `main`, and passes it to `read_first_parent` and `fetch_prs`. The other commands read
  the store and take no new option.
- **The line** (Track A), in `bearing/ingest/history.py`: `read_first_parent(repo, branch="main")`
  first checks that `refs/heads/<branch>` exists (`git -C <repo> rev-parse --verify --quiet
  refs/heads/<branch>`, which exits 1 for a missing ref in a repository and 128 outside one),
  then runs today's `git log` on `refs/heads/<branch>` where today it names `main`. A missing
  ref raises `GitError("--branch <branch>: not a local branch in <repo>")`, `<repo>` as given,
  so `ingest` prints "bearing: --branch <branch>: not a local branch in <repo>" through its
  existing `except GitError`, exits 1 and writes no store. A tag or a SHA is not a local branch,
  even when it names a commit. Any other failure of the check falls through to `git log`, so a
  directory that is not a git repository keeps today's error.
- **`gh`** (Track A), in `bearing/ingest/gh.py`: `fetch_prs(repo, branch="main")` runs
  `PR_LIST` with `"--base", branch` appended. `PR_LIST` itself is unchanged. A `--prs` file is
  read as it is: its records are not filtered by `baseRefName`.
- The new tests go in a new file, `tests/test_ingest_branch.py`. Its class builds the fixture
  with `tests/fixtures/make_repo.py` once, in `setUpClass`, tags `main`'s tip `v-tag` there
  (a ref the fixture does not hold; `make_repo.py` is not edited), and calls
  `bearing.cli.main` in the process with `subprocess.run` patched by a fake like
  `tests/test_gh.py`'s `gh_fake` (it records each `gh` call and answers it; git runs for real)
  and stdout and stderr redirected, as `tests/test_gh.py::IngestLiveTest` does. Each run gets
  a `--data` directory of its own under the class's temporary directory.
- C04.2's test, `tests/test_gh.py::FetchPrsTest::test_command_and_output`, is edited to the new
  list (C17.4); no other existing test changes.

## Out of scope
- Remote-tracking branches (`origin/NAME`) and a `--branch` that resolves through a symbolic
  ref: plan.md's Phase 9 names `refs/heads/NAME` alone.
- Filtering a `--prs` file by its `baseRefName`: plan.md says the file is read as it is. A
  record merged into another base shows up as an unmatched PR, as the fixture's #10 does on
  `release` (C17.2).
- Recording the branch in the store: the store holds one line, and the other commands read it
  without knowing its name (plan.md, Phase 9). No migration.
- `gh`'s default branch: `--branch` defaults to `main` whatever the repository's default is
  (plan.md, Course correction after Phase 6, item 3).
- A new contract version: `ingest`'s output with no `--branch` is unchanged (C17.8, C17.9).
- `.github/`, `.claude/`, `scripts/`, `plan.md` and the dependencies: the day's code stays in
  `bearing/` and `tests/` (plan.md, Phases 7 to 10). C17.10 holds it.

## Tracks

One track. C17.1–C17.6 are `new`: Track A's PR shows their tests failing on `main`'s code with
`python scripts/seen-red.py -- python -m pytest -q tests/test_ingest_branch.py::IngestBranchTest::test_main_named tests/test_ingest_branch.py::IngestBranchTest::test_release tests/test_ingest_branch.py::IngestBranchTest::test_gh_base tests/test_ingest_branch.py::IngestBranchTest::test_not_a_branch tests/test_ingest_branch.py::IngestBranchTest::test_no_main tests/test_gh.py::FetchPrsTest::test_command_and_output`,
which reports "8 failed, 1 passed": under pytest 9, `test_not_a_branch`'s three failing
subtests each count as failed and the test itself as passed. C17.7 is `hold` with a test Track A adds, without a Track 0 (as Day
14's C14.3 and Day 16's C16.4): Track A's PR shows it passing on `main`'s code with
`python scripts/seen-red.py -- python -m pytest -q tests/test_ingest_branch.py::IngestBranchTest::test_not_a_repo`,
which exits 1 ("passes there"), and then breaks it. C17.8–C17.10 are `hold` and their checks
exist: their breaks run in this spec's PR, as does C17.11's, a `hold` on an existing test.

`tests/test_ingest_branch.py` holds 6 tests, and `test_not_a_branch` 3 subtests;
`test_command_and_output` stays one test. So `python -m pytest -q` goes from Day 16's end, "115
passed, 128 subtests passed", to "121 passed, 131 subtests passed".

| Track | Owner | Work |
|---|---|---|
| A | implementer | C17.1–C17.7: `bearing/cli.py`, `bearing/ingest/history.py`, `bearing/ingest/gh.py`, `tests/test_ingest_branch.py`, `tests/test_gh.py` |

## Acceptance criteria
Tick each box in the closing PR once its evidence is in it; under a box left unticked, write
`Not proven: <why>` (`specs/README.md`, "Evidence at the close").

- [x] C17.1 **new** — `--branch main` is today's history. On the fixture,
      `ingest <repo> --prs <its prs.json> --branch main --data <dir>` returns 0, its stderr is
      empty, and its stdout is `tests/fixtures/expected/ingest.txt`'s text.
      Red today: argparse exits 2 with "unrecognized arguments: --branch main".
      Test: `tests/test_ingest_branch.py::IngestBranchTest::test_main_named`.
      Evidence: `IngestBranchTest.test_main_named` (#131), seen red in #131 on `main`'s code ("8 failed, 1 passed in 0.55s", the six `new` tests together) and again at the close on `50a000a`'s code ("8 failed, 1 passed in 0.90s"); `python -m pytest -q` at the close on `d9080a8` ("121 passed, 131 subtests passed").
- [x] C17.2 **new** — `--branch release` stores `release`'s line. On the fixture,
      `ingest <repo> --prs <its prs.json> --branch release --data <dir>` returns 0, its stderr
      is empty, and its stdout is exactly the two lines
      "merges 9  matched 9  unmatched merges 0  unmatched PRs 1  direct 2" and
      "unmatched PR #10 86761f2 release". Then `changelog --data <dir>` returns 0 and its stdout
      holds a line "- #7 docs/notes (2026-01-27)" and no line starting "- #10 " or "- #11 ".
      Red today: argparse exits 2 with "unrecognized arguments: --branch release".
      Test: `tests/test_ingest_branch.py::IngestBranchTest::test_release`.
      Evidence: `IngestBranchTest.test_release` (#131), seen red in #131 on `main`'s code ("8 failed, 1 passed in 0.55s", the six `new` tests together) and again at the close on `50a000a`'s code ("8 failed, 1 passed in 0.90s"); `python -m pytest -q` at the close on `d9080a8` ("121 passed, 131 subtests passed").
- [x] C17.3 **new** — `gh` is asked for the branch's PRs. On the fixture, with no `--prs` and
      the fake answering `gh` with the fixture's `prs.json` text,
      `ingest <repo> --branch release --data <dir>` returns 0 with C17.2's two lines, and the
      fake saw exactly one `gh` call, whose only positional argument is the literal list
      `["gh", "pr", "list", "--state", "merged", "--limit", "1000", "--json",
      "number,title,body,headRefName,baseRefName,mergeCommit,mergedAt", "--base", "release"]`,
      written out in the test, and whose `cwd` is the repository as given.
      Red today: argparse exits 2 with "unrecognized arguments: --branch release".
      Test: `tests/test_ingest_branch.py::IngestBranchTest::test_gh_base`.
      Evidence: `IngestBranchTest.test_gh_base` (#131), seen red in #131 on `main`'s code ("8 failed, 1 passed in 0.55s", the six `new` tests together) and again at the close on `50a000a`'s code ("8 failed, 1 passed in 0.90s"); `python -m pytest -q` at the close on `d9080a8` ("121 passed, 131 subtests passed").
- [x] C17.4 **new** — `fetch_prs`'s call carries the base. In
      `tests/test_gh.py::FetchPrsTest::test_command_and_output`, `fetch_prs("some/repo")` makes
      one call whose only positional argument is C04.2's literal list with `"--base", "main"`
      appended, and `fetch_prs("some/repo", "release")` one with `"--base", "release"`
      appended; both with the keywords `cwd="some/repo", capture_output=True,
      encoding="utf-8"`, no others, and both return the fake's records as C04.2 says. Its
      errors are C17.11's.
      Red today: the first call's list has no `--base`.
      Test: `tests/test_gh.py::FetchPrsTest::test_command_and_output`.
      Replaces: C04.2 — was: `fetch_prs`'s one `gh` call is exactly `["gh", "pr", "list",
      "--state", "merged", "--limit", "1000", "--json",
      "number,title,body,headRefName,baseRefName,mergeCommit,mergedAt"]`, with no base.
      Evidence: `FetchPrsTest.test_command_and_output`, edited in #131, seen red in #131 on `main`'s code ("8 failed, 1 passed in 0.55s", the six `new` tests together) and again at the close on `50a000a`'s code ("8 failed, 1 passed in 0.90s"); `python -m pytest -q` at the close on `d9080a8` ("121 passed, 131 subtests passed").
- [x] C17.5 **new** — A name that is not a local branch is one line and no store. On the
      fixture, `ingest <repo> --prs <its prs.json> --branch NAME --data <dir>`, for NAME in
      three subtests: `no-such-branch`, the tag `v-tag`, and `main`'s tip as a full SHA. Each
      returns 1, its stdout is empty, its stderr is exactly
      "bearing: --branch NAME: not a local branch in <repo>" and a line feed (`<repo>` as
      given), and `<dir>/bearing.db` does not exist.
      Red today: argparse exits 2 with "unrecognized arguments".
      Test: `tests/test_ingest_branch.py::IngestBranchTest::test_not_a_branch`.
      Evidence: `IngestBranchTest.test_not_a_branch` (#131), its three subtests, seen red in #131 on `main`'s code ("8 failed, 1 passed in 0.55s", the six `new` tests together) and again at the close on `50a000a`'s code ("8 failed, 1 passed in 0.90s"); `python -m pytest -q` at the close on `d9080a8` ("121 passed, 131 subtests passed").
- [x] C17.6 **new** — A repository without `main` names the option. In a repository the test
      makes with `git init -q` (no commit, so no `refs/heads/main` whatever git's default
      branch), `ingest <it> --prs <the fixture's prs.json> --data <dir>`, with no `--branch`,
      returns 1, its stdout is empty, its stderr is exactly
      "bearing: --branch main: not a local branch in <repo>" and a line feed, and
      `<dir>/bearing.db` does not exist.
      Red today: its stderr is "bearing: fatal: bad revision 'main'".
      Test: `tests/test_ingest_branch.py::IngestBranchTest::test_no_main`.
      Evidence: `IngestBranchTest.test_no_main` (#131), seen red in #131 on `main`'s code ("8 failed, 1 passed in 0.55s", the six `new` tests together) and again at the close on `50a000a`'s code ("8 failed, 1 passed in 0.90s"); `python -m pytest -q` at the close on `d9080a8` ("121 passed, 131 subtests passed").
- [x] C17.7 **hold** — A directory that is not a git repository keeps its error. On a new
      empty temporary directory outside any repository,
      `ingest <it> --prs <the fixture's prs.json> --data <dir>` returns 1, its stdout is empty,
      its stderr starts with "bearing: fatal: not a git repository", and `<dir>/bearing.db` does
      not exist.
      Test: `tests/test_ingest_branch.py::IngestBranchTest::test_not_a_repo`.
      Track A's PR breaks it: the branch check taking every failure, not only a missing ref, as
      a missing branch.
      Evidence: `IngestBranchTest.test_not_a_repo` (#131) passed on `main`'s code before the
      change (`seen-red.py` exit 1, "1 passed in 0.51s" in #131; "1 passed in 0.83s" on
      `50a000a` at the close) and passed at the close on `d9080a8`.
      broken: the branch check taking every failure, not only a missing ref, as a missing branch → 1 failed in 0.99s (#131)
- [x] C17.8 **hold** — With no `--branch`, `ingest` reads `main` as today:
      `python -m pytest -q tests/test_history.py tests/test_entries.py tests/test_ingest_cli.py tests/test_gh.py::IngestLiveTest`
      passes, and
      `git -c core.safecrlf=false diff --exit-code 714412f -- tests/test_history.py tests/test_entries.py tests/test_ingest_cli.py`
      prints nothing and exits 0.
      This spec's PR breaks each half: `read_first_parent` reading `release` where it reads
      `main`, and a line of `tests/test_history.py` changed.
      Evidence: at the close on `d9080a8`, the four files printed "11 passed, 7 subtests
      passed", and the diff against `714412f` printed nothing and exited 0.
      broken: read_first_parent reading release where it reads main → 6 failed, 5 passed, 4 subtests passed in 31.59s (#105)
      broken: a line of tests/test_history.py changed → import unittest (#105)
- [x] C17.9 **hold** — No contract changes: `python -m pytest -q tests/contract/` passes, and
      `git -c core.safecrlf=false diff --exit-code 714412f -- tests/contract/ tests/fixtures/expected/ tests/fixtures/make_repo.py`
      prints nothing and exits 0 (`714412f` is `main` with Day 14's spec merged, #99); and
      `python -m pytest -q` passes.
      This spec's PR breaks each half: `ingest`'s summary line saying "merge" for "merges", and
      a line of `tests/contract/test_ingest.py` changed.
      Evidence: at the close on `d9080a8`, `python -m pytest -q tests/contract/` printed "7
      passed", the diff against `714412f` printed nothing and exited 0, and `python -m pytest
      -q` printed "121 passed, 131 subtests passed".
      broken: ingest's summary line saying merge for merges → 1 failed, 6 passed in 94.76s (0:01:34) (#105)
      broken: a line of tests/contract/test_ingest.py changed → class IngestContractTest(unittest.TestCase): (#105)
- [x] C17.10 **hold** — The day stays in `bearing/` and `tests/`, with no new dependency:
      `git -c core.safecrlf=false diff --exit-code --name-only 1472abc -- .github .claude scripts pyproject.toml plan.md`
      prints nothing and exits 0 (`1472abc` is `main` with Phases 11 to 16 merged, #118).
      This spec's PR breaks it: a line of `pyproject.toml` changed.
      Evidence: at the close on `d9080a8` the check printed nothing and exited 0.
      broken: a line of pyproject.toml changed → pyproject.toml (#119)
- [x] C17.11 **hold** — `fetch_prs`'s errors stay C04.2's, word for word, each a `GhError`:
      the fake raising `FileNotFoundError` gives "gh not found: install GitHub's CLI or pass
      --prs FILE"; exit 1 with stderr "HTTP 401: Bad credentials\n" gives "gh pr list failed:
      HTTP 401: Bad credentials"; exit 4 with stderr "" gives "gh pr list failed: exit 4"; exit 0
      with stdout "not json" gives a message starting "gh pr list printed no JSON: ". The test is
      not edited.
      Test: `tests/test_gh.py::FetchPrsTest::test_errors`.
      This spec's PR breaks it: the exit code in "gh pr list failed: exit N" off by one.
      Evidence: at the close on `d9080a8`, `FetchPrsTest.test_errors` printed "1 passed, 4
      subtests passed", and #131's diff does not touch it.
      broken: the exit code in gh pr list failed: exit N off by one → 1 failed, 1 passed, 3 subtests passed in 0.35s (#105)

## Verify
```bash
python -m pytest -q                                              # 121 passed, (131 subtests passed)
python -m pytest -q tests/test_ingest_branch.py tests/test_gh.py
python -m pytest -q tests/test_history.py tests/test_entries.py tests/test_ingest_cli.py
python -m pytest -q tests/contract/
git -c core.safecrlf=false diff --exit-code 714412f -- tests/test_history.py tests/test_entries.py tests/test_ingest_cli.py
git -c core.safecrlf=false diff --exit-code 714412f -- tests/contract/ tests/fixtures/expected/ tests/fixtures/make_repo.py
git -c core.safecrlf=false diff --exit-code --name-only 1472abc -- .github .claude scripts pyproject.toml plan.md
ruff check . && ruff format --check .
```

## Notes
- What today's code does, run in this spec's session on `main` at `c2e1b9c` with Python 3.12.10
  and git 2.54.0.windows.1, on the fixture: `ingest` prints `ingest.txt`'s three lines; with
  `main` renamed, and on an empty `git init`, it exits 1 with "bearing: fatal: bad revision
  'main'" and writes no store; on a directory outside any repository, "bearing: fatal: not a git
  repository (or any of the parent directories): .git".
- The fixture's `release` (PR #10's head) is `main` at #9's merge plus #7's merge,
  `e21c62d`: 11 commits on its first-parent line, 9 merges (#6's squash counted, as on `main`)
  and 2 direct. #10's own merge, `86761f2`, is on `main` only, so on `release` it is
  the one unmatched PR; #11 is on neither the line nor the file.
- A prototype of In scope's three changes, run on a copy of `bearing/` in this spec's session,
  printed C17.1's golden text and C17.2's two lines; `changelog` on its store listed nine PRs,
  #7 among them, #10 and #11 not; `no-such-branch`, a tag and a SHA each gave the one line, exit
  1 and no store; the empty `git init` gave C17.6's line; and a directory outside any repository
  kept today's error. Its message read "no such local branch"; the spec's wording,
  "not a local branch", is plan.md's.
- `tests/test_history.py::HistoryTest::test_fixture_line` compares `read_first_parent`'s commits
  with `git log ... main`, so it holds the default (C17.8) without naming `--branch`.
- `tests/test_ingest_cli.py`'s "not-a-repo" case checks only the exit and the "bearing: "
  start: C17.7 pins "fatal: not a git repository" and the missing store, which no test does.
- C04.2's test is edited, not added to: C17.4 replaces C04.2, so `behaviour-index.py` retires
  it at the close. Day 4's Notes left "a ref other than `main`" out of scope ("decided: none");
  plan.md's Course correction after Phase 6, item 4, takes it in, and no hand-off ID names it.
- Written ahead of its day, against `main` at `c2e1b9c`, before Days 14 to 16's code has merged
  (#101 open): the test count assumes they land as their specs say (plan.md, Course correction
  after Phase 6, item 6). Day 16 also edits `main` in `bearing/cli.py` (the subparsers and the
  date check); Day 17's lines are `ingest`'s, so the two meet in one function, not one line.
  The day's own spec-auditor run re-pins C17.10's base if anything under its paths has merged
  since `85a21a1`.
- C17.10's base re-pinned after Day 15's track A (#116): the course correction after Day 15's
  track A (#118) edits `plan.md`, so on `1472abc` the check with base `85a21a1` printed
  "plan.md" and exited 1. Its base is now `1472abc`, #118's merge commit, as that change's item
  6 says, with `plan.md` still in the list: there it prints nothing and exits 0. Only the base
  moved.
- C17.8–C17.10's `git diff` checks are commands, not tests: plan.md's "every check is a test" is
  read as every new behaviour, as Days 15 and 16 did.
- C17.3's fake answers with all of `prs.json` whatever the base. A live
  `gh pr list --base release` on a repository shaped like the fixture would return only #7, the
  one record whose `baseRefName` is `release`, and most of `release`'s merges would come out
  unmatched. That follows from plan.md's decision to ask `gh` for the named base only; C17.2's
  two lines are what the `--prs` file gives, not what live `gh` would.
- Spec-auditor, before this spec's PR: 2 findings, both fixed, and 1 on the recheck, fixed. Tracks said the seen-red run
  reports "6 failed", but pytest 9 counts each failing subtest and passes a test whose failures
  are all in subtests: "8 failed, 1 passed" (shown on a scratch test). And C17.4's `Replaces:
  C04.2` would have retired C04.2's `GhError` texts with its argument list. The first fix put
  `test_errors` on C17.4's Test line; the recheck found that a `new` criterion naming a test
  that passes on `main` fails CI's "Track tests seen red" once `TRACK_RED_RUNNER` is set, so the
  texts are now their own `hold`, C17.11. It confirmed every red state, the fixture's facts, the bases, the
  prototype's outputs and C17.7's break, and found no hand-off missing. It could not make the
  `v-tag` tag or C17.6's `git init` (its guard blocks git writes); this spec's prototype ran
  both: a tag `v1` at `main` gave the one line, and the empty `git init` C17.6's line.
- **Defect** D17.1 — found: auditor · cause: spec · made: Day 17 · Tracks' seen-red count,
  "6 failed", ignored how pytest 9 counts subtests; now "8 failed, 1 passed".
- **Defect** D17.2 — found: auditor · cause: spec · made: Day 17 · `Replaces: C04.2` dropped
  C04.2's `GhError` texts from every criterion in force; C17.11 now holds them.
- **Defect** D17.3 — found: auditor · cause: spec · made: Day 17 · D17.2's first fix named
  `test_errors`, which passes on `main`, under the `new` C17.4, which CI's red check would
  fail; moved to the `hold` C17.11.
- **Defect** D17.4 — found: maintainer · cause: spec · made: Day 17 · Verify's first comment,
  "121 passed, 131 subtests passed", is two parts to `scripts/evidence.py`, and "121 passed"
  never matches pytest's "121 passed, 131 subtests passed in …s", so the post-merge replay
  would have failed it as it failed Day 14's (D14.7), a spec written before that fix. Now "121
  passed, (131 subtests passed)", as Day 14's after #110 and Day 16's after #112: the subtest
  count is a note the replay does not check.
- Closed on `main` at `d9080a8` (#131 merged), with Python 3.13.5 on Linux (WSL); CI runs 3.12.
  `python -m pytest -q` printed "121 passed, 131 subtests passed", as Tracks said; `ruff check .`
  found 73 EXE002 errors from this checkout's file modes and nothing else, `ruff check .
  --extend-ignore EXE002` passed, and `ruff format --check .` printed "121 files already
  formatted" (D17.5). CI's "Style check" and "Tests" passed on #131.
- Seen red again at the close: `python scripts/seen-red.py --base 50a000a -- python -m pytest -q`
  with C17.1–C17.6's six tests reported "8 failed, 1 passed in 0.90s", the spec's count; with
  C17.7's test it said "The check passed on 50a000a" ("1 passed in 0.83s"), as a `hold` should.
  `50a000a` is `main` just before #131.
- All 7 breaks in `specs/breaks/day-17.json` were replayed at the close with `scripts/break.py`,
  each failed its check, and each reported what its `broken:` line says, run times aside.
  C17.7's is #131's; C17.8, C17.9 and C17.11's five are #105's; C17.10's is #119's, on base
  `1472abc`, as Day 16's C16.7: #105's, on `85a21a1`, fails with no break in since #118.
  C17.8's first break edits `"main",` in `bearing/ingest/history.py`, which #131 replaced with
  `f"refs/heads/{branch}"`, so its entry carries `"at": "ad0b844"`, #105's merge commit, and
  the close replayed it in a worktree there: "6 failed, 5 passed, 4 subtests passed".
- Phase 9's "Done when" (plan.md): `--branch NAME` storing NAME's line is C17.1 and C17.2, `gh`
  asked for NAME's PRs C17.3 and C17.4, a name that is not a local branch C17.5 and C17.6, and
  `main` by default unchanged C17.7–C17.9. Each new behaviour is a test under `tests/` that CI's
  "Tests" check ran on #131.
- Track A (#131) was written by the implementer on Haiku from the main session's brief; the
  review found nothing to change. #131's diff is 294 changed lines; the close re-counted 287
  insertions and 7 deletions over its 5 files.
- This day leaves no new hand-off: C17.3's Note on live `gh --base` returning only the base's
  records follows from plan.md and is out of scope, not deferred.
- **Defect** D17.5 — found: Track A · cause: environment · made: none · same-as: D16.4 ·
  `ruff check .` failed locally with EXE002 errors (72 in #131, 73 at the close) on files the
  day did not touch, from the checkout's mode bits; CI's check passed.
- **Defect** D17.6 — found: Track A · cause: process · made: Day 17 · Day 17 is Phase 9's first
  day, and #131's session ran neither the plan-auditor on Phase 9 nor the spec-auditor on the
  day before the track, as step 1 of CLAUDE.md asks; it re-ran the `hold` checks on that day's
  `main` instead, and its body said so. The spec's own audit ran before #105.
- Blind relabel at the close (`scripts/relabel.py`, 6 entries): stage 2 of 5, cause 6 of 6,
  `made:` 5 of 6 agree. The rater left D17.1–D17.3's stage unclear: their text does not say
  when they were found, but the Note above them does (the spec-auditor, before #105), so
  `found: auditor` is kept. It left D17.4's `made:` unclear; kept as Day 17, since the Verify
  comment it fixes was written in this day's spec (#105). D17.4's stage was not compared:
  `found: maintainer` is not one of `specs/README.md`'s values, kept as written, as D16.3.
  Every tag kept.
