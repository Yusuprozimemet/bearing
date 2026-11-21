# Day 20 — A `--prs` file that cannot be read names it

**Phase:** 12 · **Depends on:** Day 19 · **Expected PRs:** 2 (track A, the close; this spec is in the Days 19 to 24 spec PR)

## Goal
Every failure to read `bearing ingest`'s `--prs` file prints "bearing: cannot read FILE: " and
its reason on one line, exit 1, nothing on stdout and no store, as a missing file does today,
where text that is not JSON, bytes that are not UTF-8 and a directory print Python's message
alone; and every new behaviour is a test CI runs (plan.md, Phase 12).

## In scope
- **The `except`** (Track A), in `main` in `bearing/cli.py`, the `try` around `load_prs` and
  Day 19's `check_records`: before the `except (OSError, ValueError)` that prints `str(exc)`,
  - `json.JSONDecodeError` prints "cannot read FILE: not JSON: <msg> (line L, column C)" from
    the exception's `msg`, `lineno` and `colno`, not `str(exc)`, which repeats the position;
  - `UnicodeDecodeError` prints "cannot read FILE: not UTF-8";
  - `OSError` prints "cannot read FILE: <reason>", the reason `exc.strerror or exc`, as
    `ingest`'s "cannot run git" line has it. `FileNotFoundError` is an `OSError`, so the
    missing file's own `except FileNotFoundError` is removed and this branch prints its line,
    "cannot read FILE: No such file or directory", unchanged (C20.5).
  FILE is `args.prs` as given. Both decode errors are `ValueError`s, so they are caught by their
  own classes before it; Day 19's lines are plain `ValueError`s and keep their wording (C20.6).
- `load_prs` is unchanged: it reads the file with `encoding="utf-8"`, so a file that starts
  with a UTF-8 byte order mark is not JSON, as today, now in the new form (C20.4). `gh` writes
  none.
- The new tests go in a new file, `tests/test_prs_read.py`. Its class builds the fixture with
  `tests/fixtures/make_repo.py` once, in `setUpClass`, writes each case's file under the class's
  temporary directory, and runs `python -m bearing` with `subprocess.run` from the repository
  root, as `tests/test_ingest_cli.py` does, each run with a `--data` directory of its own. Its
  stderr is read as UTF-8 with `\r\n` as `\n`.

## Out of scope
- Reading a file with a byte order mark as JSON (`utf-8-sig`): plan.md's Phase 12 keeps it an
  error.
- The JSON's shape: Day 19 (C19.1–C19.8), unchanged here.
- `gh`'s output that is not JSON: `bearing/ingest/gh.py`'s `GhError` lines are unchanged.
- A new contract version: `ingest`'s output on the fixture is unchanged (C20.7, C20.8).
- `.github/`, `.claude/`, `scripts/`, `plan.md` and the dependencies: the day's code stays in
  `bearing/` and `tests/` (plan.md, Phases 11 to 16). C20.9 holds it.

## Tracks

One track. C20.1–C20.4 are `new`: Track A's PR shows their tests failing on `main`'s code with
`python scripts/seen-red.py -- python -m pytest -q tests/test_prs_read.py::PrsReadTest::test_not_json tests/test_prs_read.py::PrsReadTest::test_not_utf8 tests/test_prs_read.py::PrsReadTest::test_directory tests/test_prs_read.py::PrsReadTest::test_bom`,
which reports "4 failed". C20.5 is `hold` with a test Track A adds, without a Track 0 (as Day
17's C17.7): Track A's PR shows it passing on `main`'s code with
`python scripts/seen-red.py -- python -m pytest -q tests/test_prs_read.py::PrsReadTest::test_missing`,
which exits 1 ("passes there"), and then breaks it. C20.6 is `hold` on Day 19's tests: Track A's
PR breaks it. C20.7–C20.9 are `hold`
and their checks exist: their breaks ran in the spec PR for Days 19 to 24.

`tests/test_prs_read.py` holds 5 tests and no subtests. So `python -m pytest -q` goes from Day
19's end, "133 passed, 131 subtests passed", to "138 passed, 131 subtests passed".

| Track | Owner | Work |
|---|---|---|
| A | implementer | C20.1–C20.6: `bearing/cli.py`, `tests/test_prs_read.py` |

## Acceptance criteria
Tick each box in the closing PR once its evidence is in it; under a box left unticked, write
`Not proven: <why>` (`specs/README.md`, "Evidence at the close").

Each case runs `ingest <the fixture's repository> --prs <file> --data <dir>`, `<dir>` a
directory that does not exist yet, and passes when it returns 1, its stdout is empty, its
stderr is the one line given and a line feed (`<file>` as passed), and `<dir>/bearing.db` does
not exist.

- [x] C20.1 **new** — Text that is not JSON. `<file>` holds the 4 bytes `{bad`; the line is
      exactly "bearing: cannot read <file>: not JSON: Expecting property name enclosed in double
      quotes (line 1, column 2)".
      Red today: "bearing: Expecting property name enclosed in double quotes: line 1 column 2
      (char 1)".
      Test: `tests/test_prs_read.py::PrsReadTest::test_not_json`.
      Evidence: `PrsReadTest.test_not_json` (#142), seen red in #142 on `main`'s code ("4 failed in 1.17s", the four `new` tests together) and again at the close on `dac5747`'s code ("4 failed in 1.10s"); `python -m pytest -q` at the close on `bb167c0` ("138 passed, 131 subtests passed").
      No break of its own: the seen-red runs are what show it can fail.
- [x] C20.2 **new** — Bytes that are not UTF-8. `<file>` holds the bytes `ff fe 5b`; the line is
      exactly "bearing: cannot read <file>: not UTF-8".
      Red today: "bearing: 'utf-8' codec can't decode byte 0xff in position 0: invalid start
      byte".
      Test: `tests/test_prs_read.py::PrsReadTest::test_not_utf8`.
      Evidence: `PrsReadTest.test_not_utf8` (#142), seen red in #142 on `main`'s code ("4 failed in 1.17s", the four `new` tests together) and again at the close on `dac5747`'s code ("4 failed in 1.10s"); `python -m pytest -q` at the close on `bb167c0` ("138 passed, 131 subtests passed").
      No break of its own: the seen-red runs are what show it can fail.
- [x] C20.3 **new** — A directory. `<file>` is a directory the test makes; stderr is one line
      that starts "bearing: cannot read <file>: " and holds no "[Errno".
      Red today: "bearing: [Errno 13] Permission denied: '<file>'" on Windows, the path in
      Python's quoting with its backslashes doubled (Linux: "[Errno 21] Is a directory").
      Test: `tests/test_prs_read.py::PrsReadTest::test_directory`.
      Evidence: `PrsReadTest.test_directory` (#142), seen red in #142 on `main`'s code ("4 failed in 1.17s", the four `new` tests together) and again at the close on `dac5747`'s code ("4 failed in 1.10s"); `python -m pytest -q` at the close on `bb167c0` ("138 passed, 131 subtests passed"). On Linux the line's reason is "Is a directory".
      No break of its own: the seen-red runs are what show it can fail.
- [x] C20.4 **new** — A byte order mark is still not JSON, in the new form. `<file>` holds the
      bytes `ef bb bf` and then the fixture's `prs.json`; the line is exactly
      "bearing: cannot read <file>: not JSON: Unexpected UTF-8 BOM (decode using utf-8-sig)
      (line 1, column 1)".
      Red today: "bearing: Unexpected UTF-8 BOM (decode using utf-8-sig): line 1 column 1
      (char 0)".
      Test: `tests/test_prs_read.py::PrsReadTest::test_bom`.
      Evidence: `PrsReadTest.test_bom` (#142), seen red in #142 on `main`'s code ("4 failed in 1.17s", the four `new` tests together) and again at the close on `dac5747`'s code ("4 failed in 1.10s"); `python -m pytest -q` at the close on `bb167c0` ("138 passed, 131 subtests passed").
      No break of its own: the seen-red runs are what show it can fail.
- [x] C20.5 **hold** — A missing file keeps its line. `<file>` is a path under the class's
      temporary directory that does not exist; the line is exactly
      "bearing: cannot read <file>: No such file or directory".
      Test: `tests/test_prs_read.py::PrsReadTest::test_missing`.
      Track A's PR breaks it: the `OSError` reason taken as `exc` where it is
      `exc.strerror or exc`.
      Evidence: `PrsReadTest.test_missing` (#142), "5 passed" for `tests/test_prs_read.py` at the close on `bb167c0`; on `dac5747`'s code too (seen-red: "The check passed", "1 passed in 0.52s"), as a `hold` should.
      broken: the OSError reason taken as exc where it is exc.strerror or exc → 1 failed in 1.53s (#142)
- [x] C20.6 **hold** — Day 19's lines keep their wording: `python -m pytest -q tests/test_prs_records.py`
      passes, and
      `git -c core.safecrlf=false diff --exit-code f6b7afe -- tests/test_prs_records.py`
      prints nothing and exits 0 (`f6b7afe` is `main` with Day 19's close merged, #136).
      Track A's PR breaks it: every `ValueError` printed as "cannot read FILE: not JSON".
      Evidence: at the close on `bb167c0`, `python -m pytest -q tests/test_prs_records.py` printed "8 passed", and the `git diff` against `f6b7afe` printed nothing and exited 0.
      broken: every ValueError printed as cannot read FILE: not JSON → 7 failed, 1 passed in 3.43s (#142)
- [x] C20.7 **hold** — `ingest` on a good file is unchanged:
      `python -m pytest -q tests/test_ingest_cli.py tests/test_mapping.py tests/test_stderr.py tests/test_ingest_limit.py`
      passes, and
      `git -c core.safecrlf=false diff --exit-code 714412f -- tests/test_ingest_cli.py tests/test_mapping.py tests/test_stderr.py tests/test_ingest_limit.py`
      prints nothing and exits 0.
      The spec PR breaks each half: the missing file's line saying "cannot load" where it says
      "cannot read", and a line of `tests/test_stderr.py` changed.
      Evidence: at the close on `bb167c0`, the four files' tests printed "15 passed, 11 subtests passed", and the `git diff` against `714412f` printed nothing and exited 0. #121's first break edits a text that #142 made occur three times, so its manifest entry runs `at` `dac5747`; the close broke the same line on its own code too.
      broken: the missing --prs file's line saying cannot load → 1 failed, 15 passed, 10 subtests passed in 31.89s (#121)
      broken: the missing --prs file's line saying cannot load, on the close's code → 1 failed, 15 passed, 10 subtests passed in 10.00s (#143)
      broken: a line of tests/test_stderr.py changed → import os (#121)
- [x] C20.8 **hold** — No contract changes: `python -m pytest -q tests/contract/` passes, and
      `git -c core.safecrlf=false diff --exit-code 714412f -- tests/contract/ tests/fixtures/expected/ tests/fixtures/make_repo.py`
      prints nothing and exits 0 (`714412f` is `main` with Day 14's spec merged, #99); and
      `python -m pytest -q` passes.
      The spec PR breaks each half: the ingest report's "unmatched merge " missing its space,
      and a line of `tests/contract/test_changelog.py` changed.
      Evidence: at the close on `bb167c0`, `python -m pytest -q tests/contract/` printed "7 passed", the `git diff` against `714412f` printed nothing and exited 0, and `python -m pytest -q` printed "138 passed, 131 subtests passed".
      broken: the ingest report's unmatched merge missing its space → 1 failed, 6 passed in 60.54s (0:01:00) (#121)
      broken: a line of tests/contract/test_changelog.py changed → import sys (#121)
- [x] C20.9 **hold** — The day stays in `bearing/` and `tests/`, with no new dependency:
      `git -c core.safecrlf=false diff --exit-code --name-only 1472abc -- .github .claude scripts pyproject.toml plan.md`
      prints nothing and exits 0 (`1472abc` is `main` with Phases 11 to 16 merged, #118).
      The spec PR breaks it: a line of `plan.md` changed.
      Evidence: at the close on `bb167c0`, the `git diff --name-only` against `1472abc` printed nothing and exited 0; #142 touched only `bearing/` and `tests/`.
      broken: a line of plan.md changed → plan.md (#121)

## Verify
```bash
python -m pytest -q                                              # 138 passed, (131 subtests passed)
python -m pytest -q tests/test_prs_read.py
python -m pytest -q tests/test_prs_records.py
python -m pytest -q tests/test_ingest_cli.py tests/test_mapping.py tests/test_stderr.py tests/test_ingest_limit.py
python -m pytest -q tests/contract/
git -c core.safecrlf=false diff --exit-code f6b7afe -- tests/test_prs_records.py
git -c core.safecrlf=false diff --exit-code 714412f -- tests/test_ingest_cli.py tests/test_mapping.py tests/test_stderr.py tests/test_ingest_limit.py
git -c core.safecrlf=false diff --exit-code 714412f -- tests/contract/ tests/fixtures/expected/ tests/fixtures/make_repo.py
git -c core.safecrlf=false diff --exit-code --name-only 1472abc -- .github .claude scripts pyproject.toml plan.md
ruff check . && ruff format --check .
```

## Notes
- What today's code does, run in the spec PR's session on `main` at `8a17f82` with Python
  3.12.10 on Windows, on the fixture: each red line above, exit 1, no store. On Windows,
  reading a directory raises `PermissionError` (`strerror` "Permission denied"); on Linux,
  `IsADirectoryError` ("Is a directory"). C20.3 checks the form, not the reason, so it passes on
  both.
- `json.JSONDecodeError`'s `msg`, `lineno` and `colno` for `{bad` are "Expecting property name
  enclosed in double quotes", 1 and 2; for a leading byte order mark, "Unexpected UTF-8 BOM
  (decode using utf-8-sig)", 1 and 1 (checked in the same session).
- `tests/test_stderr.py` runs `ingest --prs` on a missing file named "łódź-café" with the
  console's code page set to cp1252 and checks for "cannot read" (C20.7): the reason stays
  `strerror`, so the path is printed once, in UTF-8.
- Written ahead of its day, against `main` at `8a17f82`, before the code of Days 15 to 19 has
  merged: the test count assumes they land as their specs say (plan.md, Course correction after
  Day 15's track A, item 5). The day's own spec-auditor run reads this spec against `main` as it
  is then, pins C20.6's base, and re-pins C20.9's if anything under its paths has merged since
  `1472abc`.
- C20.7–C20.9's `git diff` checks are commands, not tests: plan.md's "every check is a test" is
  read as every new behaviour, as Days 15 to 18 did.
- Spec-auditor, in the spec PR for Days 19 to 24 (one run over all six): one finding here,
  fixed. In scope said the missing file's own `except` "may go"; kept, the missing file never
  reaches the `OSError` branch and C20.5's break leaves its test green. In scope now removes it.
  It confirmed every red state above and the count chain.
- **Defect** D20.1 — found: auditor · cause: spec · made: Day 20 · In scope let the missing
  file's `except FileNotFoundError` stay, so C20.5's named break could not fail its test; In
  scope now removes it.
- First-day audits, on `main` at `f6b7afe` (Linux, Python 3.13.5), in the spec-change PR:
  the plan-auditor on Phase 12, consistent, one finding (C20.6's base, below); the spec-auditor
  on the day, three findings. C20.1–C20.4 red as written (Linux's "[Errno 21] Is a directory"
  for C20.3), C20.5 green, `python -m pytest -q` "133 passed, 131 subtests passed", nothing
  under C20.9's paths changed since `1472abc`, so no re-pin. Its findings: C20.6 had no
  pinned base (fixed: `f6b7afe`, the Note above asked for it; not a defect); this Note's
  "łódź-café.json" (fixed, D20.2); and an untracked `--help/` directory left in the working
  tree during the audits (D20.3, removed). It also tried C20.6's break: "7 failed, 1 passed".
- **Defect** D20.2 — found: auditor · cause: spec · made: Day 20 · a Note named the file
  `tests/test_stderr.py` passes to `--prs` "łódź-café.json"; the test names it "łódź-café".
- **Defect** D20.3 — found: auditor · cause: process · made: Day 20 · a read-only auditor run
  left an untracked `--help/` directory in the repository root, holding the fixture's
  `prs.json` and `repo/`. That is what `tests/fixtures/make_repo.py --help` writes, since it
  takes its one argument as the output directory. `scripts/auditor-guard.py` reads git and gh
  commands only, so it let the run through. The directory made `ruff check .` report F401,
  I001 and syntax errors; the main session removed it before the spec-change PR.
- No criterion in force pins the lines this day changes: `tests/test_ingest_cli.py::IngestCliTest::test_errors`
  pins only "bearing: ", so no `Replaces:` line. No hand-off ID names this gap: plan.md's Course
  correction after Day 15's track A, item 1, found it by running `bearing`.
- The close, on `main` at `bb167c0` (Linux under WSL, Python 3.13.5): `python -m pytest -q`
  printed "138 passed, 131 subtests passed", the spec's count; `tests/test_prs_read.py` "5
  passed", `tests/test_prs_records.py` "8 passed", C20.7's four files "15 passed, 11 subtests
  passed", `tests/contract/` "7 passed"; the four `git diff` checks of C20.6–C20.9 each printed
  nothing and exited 0. `ruff format --check .` printed "124 files already formatted";
  `ruff check .` reported 76 EXE002 errors and passed with `--extend-ignore EXE002` (D20.4).
- Seen red again at the close: `python scripts/seen-red.py --base dac5747 -- python -m pytest -q`
  on C20.1–C20.4's four tests reported "4 failed in 1.10s", the spec's count; on C20.5's
  `test_missing` it said "The check passed on dac5747" ("1 passed in 0.52s"), as a `hold`
  should. `dac5747` is `main` just before #142.
- All 8 breaks in `specs/breaks/day-20.json` were replayed at the close with `scripts/break.py`,
  each failed its check, and each reported what its `broken:` line says, run times aside.
  C20.5's and C20.6's are #142's; C20.7–C20.9's five are #121's; one more, C20.7's "on the
  close's code", is this close's own. #121's "cannot load" break finds
  `f"cannot read {args.prs}: `, which occurs once on `dac5747` and three times on `bb167c0`,
  since #142 gave every read failure that start; `break.py` refuses a text that is not unique,
  so that entry carries `"at": "dac5747"` and was replayed in a worktree there (D20.5). The
  close broke the same line on its own code, finding the `OSError` branch's whole f-string,
  and recorded it beside.
- C20.1–C20.4 have no break of their own: the seen-red runs, on `main`'s code in #142 and on
  `dac5747` at the close, are what show their tests can fail.
- The first-day audits ran in the spec-change PR (#139), as the Note above records; #139 has
  "human: none yet". Phase 12's "Done when" (plan.md): text that is not JSON is C20.1, bytes
  that are not UTF-8 C20.2, a directory C20.3, a byte order mark C20.4 and a missing file C20.5,
  each a test in `tests/test_prs_read.py` that CI's "Tests" check ran on #142.
- Track A (#142) was written by the implementer on Haiku from the main session's brief. #142's
  body says 105 changed lines (`bearing/cli.py` 9+/3−, `tests/test_prs_read.py` 96+); the close
  re-counted the same from `git diff --numstat dac5747 bb167c0`.
- `docs/dashboard/token-usage.json`, refreshed at the close, is unchanged: 87 rows, from
  2026-10-28 to 2026-11-21, $361.85; it tags no row with Day 20.
- This day leaves no new hand-off. It is Phase 12's only day, so after this close merges the
  next step is CLAUDE.md's step 6: the plan-auditor on Phase 12 and on Phase 13, in a new
  session.
- **Defect** D20.4 — found: Track A · cause: environment · made: none · same-as: D16.4 ·
  `ruff check .` failed locally with EXE002 errors (75 in #142, 76 at the close), from the
  checkout's file modes and on no line the day wrote; CI's check passed.
- **Defect** D20.5 — found: close · cause: spec · made: Day 20 · C20.7's break in #121, "the
  missing --prs file's line saying cannot load", finds a text that this day's own In scope
  makes occur three times in `bearing/cli.py`, so the break cannot run on the closing commit;
  the spec did not see it, and the close gave the entry an `at` and added a break on its own
  code.
- Blind relabel at the close (`scripts/relabel.py`, 5 entries): stage 4 of 5, cause 4 of 5,
  `made:` 4 of 5 agree. The rater left D20.2's stage unclear: its text does not say when it was
  found, but the first-day audits Note above it does, the spec-auditor before any code, so
  `found: auditor` is kept. It read D20.3 as `cause: environment`, `made: none`, a tooling gap;
  kept as `process` and `Day 20`: what went wrong was a step of this day's workflow, an auditor
  run that wrote into the repository, and the guard's reach is the known limit CLAUDE.md
  states, not a fault of the tool.
