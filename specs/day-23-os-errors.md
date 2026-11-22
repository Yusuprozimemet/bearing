# Day 23 — OS errors name the path once

**Phase:** 15 · **Depends on:** Day 22 · **Expected PRs:** 2 (track A, the close; this spec is in the Days 19 to 24 spec PR)

## Goal
`bearing page --out` that cannot be written prints "bearing: cannot write OUT: <reason>", and
`bearing ingest --data` that cannot be made a store directory prints "bearing: cannot open store
at DATA: <reason>", the path once and the OS's reason, where today both print the path a second
time in Python's quoting; and every new behaviour is a test CI runs (plan.md, Phase 15).

## In scope
- **`page`** (Track A), in `_page` in `bearing/cli.py`: the `except OSError` around writing
  `--out` prints `f"cannot write {args.out}: {exc.strerror or exc}"`, where today it prints
  `{exc}`.
- **`ingest`** (Track A), in `main` in `bearing/cli.py`: the `except (OSError, sqlite3.Error)`
  around `open_store` and `save` splits in two. An `OSError` prints
  `f"cannot open store at {args.data}: {exc.strerror or exc}"`; a `sqlite3.Error` keeps
  `f"cannot open store at {args.data}: {exc}"`, its text as today (C23.3).
- The reason is `exc.strerror or exc`, as `ingest`'s "cannot run git" line and Day 20's
  `--prs` line have it. Every other error keeps its text.
- The new tests go in a new file, `tests/test_os_errors.py`. Its class builds the fixture with
  `tests/fixtures/make_repo.py` once, in `setUpClass`, ingests it with its `prs.json` into a
  `--data` directory under the class's temporary directory, and runs `python -m bearing` with
  `subprocess.run` from the repository root, as `tests/test_page_cli.py` does, with
  `--config tests/fixtures/bearing.toml` for `page`. Its stderr is read as UTF-8 with `\r\n` as
  `\n`.
- **CI** (Track A), in `.github/workflows/tests.yml`: the `pytest` step runs
  `python -m pytest -q -rf`, where today it runs `pytest -q`, so the log names each failure in
  its short summary.

## Out of scope
- Other OS errors: the store's own reads (`changelog`, `timeline`, `direction`, `page`) go
  through `sqlite3`, whose errors keep their text; `snapshot`'s and `ingest`'s "cannot run git"
  lines already use `strerror`.
- The OS's reason itself: it differs between Windows and Linux for a file where a directory
  should be ("Cannot create a file when that file already exists", "File exists"), so C23.2
  checks the form, not the reason.
- A new contract version: neither line is in a golden file (C23.5).
- `.github/`, `.claude/`, `scripts/`, `plan.md` and the dependencies: the day's code stays in
  `bearing/` and `tests/` (plan.md, Phases 11 to 16). C23.6 holds it.

## Tracks

One track. C23.1 and C23.2 are `new`: Track A's PR shows their tests failing on `main`'s code
with
`python scripts/seen-red.py -- python -m pytest -q tests/test_os_errors.py::OsErrorsTest::test_out_missing_dir tests/test_os_errors.py::OsErrorsTest::test_data_is_a_file`,
which reports "2 failed". C23.3 is `hold` with a test Track A adds, without a Track 0 (as Day
17's C17.7): Track A's PR shows it passing on `main`'s code with
`python scripts/seen-red.py -- python -m pytest -q tests/test_os_errors.py::OsErrorsTest::test_sqlite_text`,
which exits 1 ("passes there"), and then breaks it. C23.4–C23.6 are `hold` and their checks
exist: their breaks ran in the spec PR for Days 19 to 24.

`tests/test_os_errors.py` holds 3 tests and no subtests. So `python -m pytest -q` goes from Day
22's end, "146 passed, 131 subtests passed", to "149 passed, 131 subtests passed".

| Track | Owner | Work |
|---|---|---|
| A | implementer | C23.1–C23.3: `bearing/cli.py`, `tests/test_os_errors.py` |

## Acceptance criteria
Tick each box in the closing PR once its evidence is in it; under a box left unticked, write
`Not proven: <why>` (`specs/README.md`, "Evidence at the close").

- [ ] C23.1 **new** — `--out` in a directory that does not exist names it once. On the ingested
      fixture, `page <repo> --data <store> --config tests/fixtures/bearing.toml --out <out>`,
      `<out>` the path `missing/x.html` under the class's temporary directory, `missing` not
      made, returns 1, its stdout is empty, its stderr is exactly
      "bearing: cannot write <out>: No such file or directory" and a line feed (`<out>` as
      given; ENOENT's `strerror` reads the same on Windows and Linux), and `<out>` does not
      exist.
      Red today: "bearing: cannot write <out>: [Errno 2] No such file or directory: '<out>'",
      the second path in Python's quoting, its backslashes doubled on Windows.
      Test: `tests/test_os_errors.py::OsErrorsTest::test_out_missing_dir`.
- [ ] C23.2 **new** — A file where the store's directory should be names it once. With `<file>`
      a file under the class's temporary directory holding the bytes `x`,
      `ingest <repo> --prs <the fixture's prs.json> --data <file>` returns 1, its stdout is
      empty, its stderr is one line that starts "bearing: cannot open store at <file>: " and
      holds neither "[Errno" nor "[WinError", and `<file>` still holds `x`.
      Red today: "bearing: cannot open store at <file>: [WinError 183] Cannot create a file
      when that file already exists: '<file>'" (Linux: "[Errno 17] File exists: '<file>'").
      Test: `tests/test_os_errors.py::OsErrorsTest::test_data_is_a_file`.
- [ ] C23.3 **hold** — A store that is not a database keeps SQLite's text. With `<data>` a
      directory whose `bearing.db` holds the bytes "not a database, just text",
      `ingest <repo> --prs <the fixture's prs.json> --data <data>` returns 1, its stdout is
      empty, and its stderr is exactly "bearing: cannot open store at <data>: file is not a
      database" and a line feed.
      Test: `tests/test_os_errors.py::OsErrorsTest::test_sqlite_text`.
      Track A's PR breaks it: the `sqlite3.Error` reason taken as `exc.strerror or exc`, which
      a `sqlite3.Error` does not have.
- [ ] C23.4 **hold** — The two tests that pin these lines' starts pass unedited:
      `python -m pytest -q tests/test_broken_store.py tests/test_page_cli.py`
      passes, and
      `git -c core.safecrlf=false diff --exit-code 714412f -- tests/test_broken_store.py tests/test_page_cli.py`
      prints nothing and exits 0.
      The spec PR breaks each half: "cannot write " in `page`'s line reading "cannot save ",
      and a line of `tests/test_broken_store.py` changed.
- [ ] C23.5 **hold** — No contract changes: `python -m pytest -q tests/contract/` passes, and
      `git -c core.safecrlf=false diff --exit-code 714412f -- tests/contract/ tests/fixtures/expected/ tests/fixtures/make_repo.py`
      prints nothing and exits 0 (`714412f` is `main` with Day 14's spec merged, #99); and
      `python -m pytest -q` passes.
      The spec PR breaks each half: the page data's version "page-v1" written "page-v0", and a
      line of `tests/contract/test_page.py` changed.
- [ ] C23.6 **hold** — The day stays in `bearing/` and `tests/`, with no new dependency:
      `git -c core.safecrlf=false diff --exit-code --name-only 1472abc -- .github .claude scripts pyproject.toml plan.md`
      prints nothing and exits 0 (`1472abc` is `main` with Phases 11 to 16 merged, #118).
      The spec PR breaks it: a line of `scripts/spec-drift.py` changed.

## Verify
```bash
python -m pytest -q                                              # 149 passed, (131 subtests passed)
python -m pytest -q tests/test_os_errors.py
python -m pytest -q tests/test_broken_store.py tests/test_page_cli.py
python -m pytest -q tests/contract/
git -c core.safecrlf=false diff --exit-code 714412f -- tests/test_broken_store.py tests/test_page_cli.py
git -c core.safecrlf=false diff --exit-code 714412f -- tests/contract/ tests/fixtures/expected/ tests/fixtures/make_repo.py
git -c core.safecrlf=false diff --exit-code --name-only 1472abc -- .github .claude scripts pyproject.toml plan.md
ruff check . && ruff format --check .
```

## Notes
- What today's code does, run in the spec PR's session on `main` at `8a17f82` with Python
  3.12.10 on Windows, on the ingested fixture: `page --out missing/x.html` prints "bearing:
  cannot write missing/x.html: [Errno 2] No such file or directory: 'missing\\x.html'";
  `ingest --data <a file>` prints "bearing: cannot open store at <file>: [WinError 183] Cannot
  create a file when that file already exists: '<file>'", from `open_store`'s `mkdir`; and a
  `bearing.db` that is not a database prints "bearing: cannot open store at <data>: file is not
  a database". Each exits 1 with an empty stdout. `FileExistsError`'s `strerror` there is
  "Cannot create a file when that file already exists".
- `tests/test_broken_store.py::BrokenStoreTest::test_ingest_refuses` pins the third line's
  start only, so C23.3 pins its whole text before the `except` is split.
- Written ahead of its day, against `main` at `8a17f82`, before the code of Days 15 to 22 has
  merged: the test count assumes they land as their specs say (plan.md, Course correction after
  Day 15's track A, item 5). The day's own spec-auditor run reads this spec against `main` as it
  is then, and re-pins C23.6's base if anything under its paths has merged since `1472abc`.
- C23.4–C23.6's `git diff` checks are commands, not tests: plan.md's "every check is a test" is
  read as every new behaviour, as Days 15 to 18 did.
- Spec-auditor, in the spec PR for Days 19 to 24 (one run over all six): no finding here. It
  confirmed the three lines above, that `<file>` still holds `x`, and the count.
- No criterion in force pins the text after these lines' starts, so no `Replaces:` line. No
  hand-off ID names this gap: plan.md's Course correction after Day 15's track A, item 1, found
  it by running `bearing`.
