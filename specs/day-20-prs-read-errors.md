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

- [ ] C20.1 **new** — Text that is not JSON. `<file>` holds the 4 bytes `{bad`; the line is
      exactly "bearing: cannot read <file>: not JSON: Expecting property name enclosed in double
      quotes (line 1, column 2)".
      Red today: "bearing: Expecting property name enclosed in double quotes: line 1 column 2
      (char 1)".
      Test: `tests/test_prs_read.py::PrsReadTest::test_not_json`.
- [ ] C20.2 **new** — Bytes that are not UTF-8. `<file>` holds the bytes `ff fe 5b`; the line is
      exactly "bearing: cannot read <file>: not UTF-8".
      Red today: "bearing: 'utf-8' codec can't decode byte 0xff in position 0: invalid start
      byte".
      Test: `tests/test_prs_read.py::PrsReadTest::test_not_utf8`.
- [ ] C20.3 **new** — A directory. `<file>` is a directory the test makes; stderr is one line
      that starts "bearing: cannot read <file>: " and holds no "[Errno".
      Red today: "bearing: [Errno 13] Permission denied: '<file>'" on Windows, the path in
      Python's quoting with its backslashes doubled (Linux: "[Errno 21] Is a directory").
      Test: `tests/test_prs_read.py::PrsReadTest::test_directory`.
- [ ] C20.4 **new** — A byte order mark is still not JSON, in the new form. `<file>` holds the
      bytes `ef bb bf` and then the fixture's `prs.json`; the line is exactly
      "bearing: cannot read <file>: not JSON: Unexpected UTF-8 BOM (decode using utf-8-sig)
      (line 1, column 1)".
      Red today: "bearing: Unexpected UTF-8 BOM (decode using utf-8-sig): line 1 column 1
      (char 0)".
      Test: `tests/test_prs_read.py::PrsReadTest::test_bom`.
- [ ] C20.5 **hold** — A missing file keeps its line. `<file>` is a path under the class's
      temporary directory that does not exist; the line is exactly
      "bearing: cannot read <file>: No such file or directory".
      Test: `tests/test_prs_read.py::PrsReadTest::test_missing`.
      Track A's PR breaks it: the `OSError` reason taken as `exc` where it is
      `exc.strerror or exc`.
- [ ] C20.6 **hold** — Day 19's lines keep their wording: `python -m pytest -q tests/test_prs_records.py`
      passes, and
      `git -c core.safecrlf=false diff --exit-code f6b7afe -- tests/test_prs_records.py`
      prints nothing and exits 0 (`f6b7afe` is `main` with Day 19's close merged, #136).
      Track A's PR breaks it: every `ValueError` printed as "cannot read FILE: not JSON".
- [ ] C20.7 **hold** — `ingest` on a good file is unchanged:
      `python -m pytest -q tests/test_ingest_cli.py tests/test_mapping.py tests/test_stderr.py tests/test_ingest_limit.py`
      passes, and
      `git -c core.safecrlf=false diff --exit-code 714412f -- tests/test_ingest_cli.py tests/test_mapping.py tests/test_stderr.py tests/test_ingest_limit.py`
      prints nothing and exits 0.
      The spec PR breaks each half: the missing file's line saying "cannot load" where it says
      "cannot read", and a line of `tests/test_stderr.py` changed.
- [ ] C20.8 **hold** — No contract changes: `python -m pytest -q tests/contract/` passes, and
      `git -c core.safecrlf=false diff --exit-code 714412f -- tests/contract/ tests/fixtures/expected/ tests/fixtures/make_repo.py`
      prints nothing and exits 0 (`714412f` is `main` with Day 14's spec merged, #99); and
      `python -m pytest -q` passes.
      The spec PR breaks each half: the ingest report's "unmatched merge " missing its space,
      and a line of `tests/contract/test_changelog.py` changed.
- [ ] C20.9 **hold** — The day stays in `bearing/` and `tests/`, with no new dependency:
      `git -c core.safecrlf=false diff --exit-code --name-only 1472abc -- .github .claude scripts pyproject.toml plan.md`
      prints nothing and exits 0 (`1472abc` is `main` with Phases 11 to 16 merged, #118).
      The spec PR breaks it: a line of `plan.md` changed.

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
