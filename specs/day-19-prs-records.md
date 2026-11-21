# Day 19 — A `--prs` file that is not PR records

**Phase:** 11 · **Depends on:** Day 18 · **Expected PRs:** 2 (track A, the close; this spec is in the Days 19 to 24 spec PR)

## Goal
`bearing ingest <repo> --prs FILE` stops with one line on stderr, exit 1, nothing on stdout and
no store, when FILE's JSON is not a list of PR records, where today it ends in a traceback, a
UNIQUE constraint or a silent exit 0; and every new behaviour is a test CI runs (plan.md,
Phase 11).

## In scope
- **The check** (Track A), in `bearing/ingest/mapping.py`: a new function
  `check_records(path, records)` returns `None` for a list of PR records and otherwise raises
  `ValueError` whose text is the line after "bearing: ", `path` as given. The first failure
  found is the one raised, records counted from 1, in this order:
  1. anything but a JSON list: "FILE: not a list of PR records";
  2. for each record in turn, a record that is not an object: "FILE: record N is not an
     object"; then `number`, `title`, `headRefName`, `baseRefName`, in that order, each first
     present ("FILE: record N has no FIELD") and then of its type ("FILE: record N's number is
     not an integer", `true` and `false` not being one; "FILE: record N's FIELD is not a
     string" for the other three; a present `null` is of the wrong type); then the optional
     fields, each absent, `null` or of its type: "FILE: record N's FIELD is not a string" for
     `body` and then `mergedAt`, "FILE: record N's mergeCommit is not an object", and, for an
     object, its `oid` absent, `null` or a string: "FILE: record N's mergeCommit oid is not a
     string";
  3. once every record passes: "FILE: record N repeats number M", N the first record whose
     number an earlier record has.
  A record's other fields are not read.
- **The call** (Track A), in `main` in `bearing/cli.py`: `ingest` calls `check_records(args.prs,
  records)` inside the `try` that reads the `--prs` file, right after `load_prs`, so the
  existing `except (OSError, ValueError)` prints it through `_fail`. That is before the
  1000-record warning and before the store is opened, so no `bearing.db` is written.
- `load_prs` is unchanged: `tests/test_mapping.py::LoadPrsTest::test_utf8` reads a record with
  no branch names through it (C19.9).
- The new tests go in a new file, `tests/test_prs_records.py`. Its class builds the fixture with
  `tests/fixtures/make_repo.py` once, in `setUpClass`, writes each case's file under the class's
  temporary directory from the fixture's `prs.json` (record 3 is #3, `day-02/track-a-cycle`,
  and record 2 is #2), and runs `python -m bearing` with `subprocess.run` from the repository
  root, as `tests/test_ingest_cli.py` does, each run with a `--data` directory of its own. Its
  stderr is read as UTF-8 with `\r\n` as `\n`. It imports what it tests from `bearing` inside the
  test, so a missing name fails that test and not the file's collection.

## Out of scope
- The records `gh` prints: `fetch_prs`'s output is not checked (plan.md, Phase 11). No
  criterion pins that they are unchecked; a reviewer reads Track A's diff for the one call
  site.
- A `--prs` file that cannot be read, or is not JSON: Day 20 (plan.md, Phase 12). Today's lines
  for them do not change on this day.
- Fields beyond the eight named, and values of the right type that make no sense (a negative
  number, a `mergedAt` that is not a date): not checked.
- A new contract version: `ingest`'s output on the fixture is unchanged (C19.9, C19.10).
- `.github/`, `.claude/`, `scripts/`, `plan.md` and the dependencies: the day's code stays in
  `bearing/` and `tests/` (plan.md, Phases 11 to 16). C19.11 holds it.

## Tracks

One track. C19.1–C19.8 are `new`: Track A's PR shows their tests failing on `main`'s code with
`python scripts/seen-red.py -- python -m pytest -q tests/test_prs_records.py`, which reports
"8 failed". C19.9–C19.11 are `hold` and their checks exist: their breaks ran in the spec PR
for Days 19 to 24.

`tests/test_prs_records.py` holds 8 tests and no subtests. So `python -m pytest -q` goes from
Day 18's end, "125 passed, 131 subtests passed", to "133 passed, 131 subtests passed".

| Track | Owner | Work |
|---|---|---|
| A | implementer | C19.1–C19.8: `bearing/ingest/mapping.py`, `bearing/cli.py`, `tests/test_prs_records.py` |

## Acceptance criteria
Tick each box in the closing PR once its evidence is in it; under a box left unticked, write
`Not proven: <why>` (`specs/README.md`, "Evidence at the close").

Each CLI case runs `ingest <the fixture's repository> --prs <file> --data <dir>`, `<dir>` a
directory that does not exist yet, and passes when it returns 1, its stdout is empty, its
stderr is exactly the line given and a line feed (`<file>` as passed), and `<dir>/bearing.db`
does not exist.

- [x] C19.1 **new** — A JSON object is not a list. `<file>` holds `{}`; the line is
      "bearing: <file>: not a list of PR records".
      Red today: it exits 0 and prints a report with all 9 merges unmatched.
      Test: `tests/test_prs_records.py::PrsRecordsTest::test_not_a_list`.
      Evidence: `PrsRecordsTest.test_not_a_list` (#135), seen red in #135 on `main`'s code ("8 failed in 2.15s", the eight `new` tests together) and again at the close on `e72fc75`'s code ("8 failed in 3.84s"); `python -m pytest -q` at the close on `93fd6bf` ("133 passed, 131 subtests passed").
      No break of its own: the seen-red runs are what show it can fail.
- [x] C19.2 **new** — A list of numbers is not records. `<file>` holds `[1]`; the line is
      "bearing: <file>: record 1 is not an object".
      Red today: a traceback ending "AttributeError: 'int' object has no attribute 'get'".
      Test: `tests/test_prs_records.py::PrsRecordsTest::test_not_an_object`.
      Evidence: `PrsRecordsTest.test_not_an_object` (#135), seen red in #135 on `main`'s code ("8 failed in 2.15s", the eight `new` tests together) and again at the close on `e72fc75`'s code ("8 failed in 3.84s"); `python -m pytest -q` at the close on `93fd6bf` ("133 passed, 131 subtests passed").
      No break of its own: the seen-red runs are what show it can fail.
- [x] C19.3 **new** — A missing field is named. `<file>` holds the fixture's records with
      record 3's `title` removed; the line is "bearing: <file>: record 3 has no title".
      Red today: a traceback ending "KeyError: 'title'", and a `bearing.db` left behind.
      Test: `tests/test_prs_records.py::PrsRecordsTest::test_no_title`.
      Evidence: `PrsRecordsTest.test_no_title` (#135), seen red in #135 on `main`'s code ("8 failed in 2.15s", the eight `new` tests together) and again at the close on `e72fc75`'s code ("8 failed in 3.84s"); `python -m pytest -q` at the close on `93fd6bf` ("133 passed, 131 subtests passed").
      broken: ingest not calling check_records → 1 failed in 1.30s (#135)
- [x] C19.4 **new** — A number that is not an integer is named. `<file>` holds the fixture's
      records with record 3's `number` the string "3"; the line is "bearing: <file>: record 3's
      number is not an integer". The same with record 3's `number` `true` gives the same line.
      Red today: the string exits 0 and stores it; `true` prints "bearing: cannot open store at
      <dir>: UNIQUE constraint failed: prs.number" and leaves a `bearing.db`.
      Test: `tests/test_prs_records.py::PrsRecordsTest::test_number_type`.
      Evidence: `PrsRecordsTest.test_number_type` (#135), seen red in #135 on `main`'s code ("8 failed in 2.15s", the eight `new` tests together) and again at the close on `e72fc75`'s code ("8 failed in 3.84s"); `python -m pytest -q` at the close on `93fd6bf` ("133 passed, 131 subtests passed").
      broken: check_records accepting bool as a number → 1 failed in 1.81s (#135)
- [x] C19.5 **new** — A `mergeCommit` that is not an object is named. `<file>` holds the
      fixture's records with record 3's `mergeCommit` the string "x"; the line is
      "bearing: <file>: record 3's mergeCommit is not an object".
      Red today: a traceback ending "AttributeError: 'str' object has no attribute 'get'", and
      a `bearing.db` left behind.
      Test: `tests/test_prs_records.py::PrsRecordsTest::test_merge_commit_type`.
      Evidence: `PrsRecordsTest.test_merge_commit_type` (#135), seen red in #135 on `main`'s code ("8 failed in 2.15s", the eight `new` tests together) and again at the close on `e72fc75`'s code ("8 failed in 3.84s"); `python -m pytest -q` at the close on `93fd6bf` ("133 passed, 131 subtests passed").
      No break of its own: the seen-red runs are what show it can fail.
- [x] C19.6 **new** — A repeated number is named. `<file>` holds the fixture's records with
      record 3's `number` 2, record 2's; the line is "bearing: <file>: record 3 repeats number 2".
      Red today: "bearing: cannot open store at <dir>: UNIQUE constraint failed: prs.number",
      and a `bearing.db` left behind.
      Test: `tests/test_prs_records.py::PrsRecordsTest::test_repeats`.
      Evidence: `PrsRecordsTest.test_repeats` (#135), seen red in #135 on `main`'s code ("8 failed in 2.15s", the eight `new` tests together) and again at the close on `e72fc75`'s code ("8 failed in 3.84s"); `python -m pytest -q` at the close on `93fd6bf` ("133 passed, 131 subtests passed").
      No break of its own: the seen-red runs are what show it can fail.
- [x] C19.7 **new** — The check comes before the 1000-record warning. `<file>` holds the
      fixture's records padded to 1000 as `tests/test_ingest_limit.py`'s `records(1000)` does,
      with record 3's `title` removed; stderr is exactly "bearing: <file>: record 3 has no
      title" and a line feed, with no "warning" line.
      Red today: stderr starts "bearing: warning: 1000 PR records is gh's limit" and ends in a
      traceback.
      Test: `tests/test_prs_records.py::PrsRecordsTest::test_before_warning`.
      Evidence: `PrsRecordsTest.test_before_warning` (#135), seen red in #135 on `main`'s code ("8 failed in 2.15s", the eight `new` tests together) and again at the close on `e72fc75`'s code ("8 failed in 3.84s"); `python -m pytest -q` at the close on `93fd6bf` ("133 passed, 131 subtests passed").
      No break of its own: the seen-red runs are what show it can fail.
- [x] C19.8 **new** — Every message and the order. With `R` the record
      `{"number": 1, "title": "t", "headRefName": "h", "baseRefName": "main"}`,
      `check_records("p.json", records)` raises `ValueError` whose text is exactly:
      "p.json: not a list of PR records" for `{"a": 1}`;
      "p.json: record 1 is not an object" for `[[]]`;
      "p.json: record 1 has no number" for `[{}]`;
      "p.json: record 1's number is not an integer" for `R` with `number` 1.0, and for `R` with
      `number` "x" and `title` 5;
      "p.json: record 1 has no headRefName" for `R` without `headRefName`;
      "p.json: record 1's baseRefName is not a string" for `R` with `baseRefName` `None`;
      "p.json: record 1's body is not a string" for `R` with `body` 5 and `mergedAt` 5;
      "p.json: record 1's mergedAt is not a string" for `R` with `mergedAt` 0;
      "p.json: record 1's mergeCommit oid is not a string" for `R` with `mergeCommit`
      `{"oid": 7}`;
      "p.json: record 2 is not an object" for `[R, 3]`;
      and "p.json: record 3 repeats number 1" for `[R, R with number 2, R]`.
      It returns `None` for `[]`, for `[R]`, and for `[R]` with `body`, `mergedAt` and
      `mergeCommit` all `None`, with `mergeCommit` `{}`, and with `mergeCommit`
      `{"oid": None}`.
      Red today: "ImportError: cannot import name 'check_records'".
      Test: `tests/test_prs_records.py::PrsRecordsTest::test_messages`.
      Evidence: `PrsRecordsTest.test_messages` (#135), seen red in #135 on `main`'s code ("8 failed in 2.15s", the eight `new` tests together) and again at the close on `e72fc75`'s code ("8 failed in 3.84s"); `python -m pytest -q` at the close on `93fd6bf` ("133 passed, 131 subtests passed").
      broken: check_records refusing a mergeCommit oid that is null → 1 failed in 0.96s (#135)
- [x] C19.9 **hold** — `ingest` on good records is unchanged, and `load_prs` with it:
      `python -m pytest -q tests/test_ingest_cli.py tests/test_mapping.py tests/test_ingest_limit.py tests/test_stderr.py tests/test_broken_store.py`
      passes, and
      `git -c core.safecrlf=false diff --exit-code 714412f -- tests/test_ingest_cli.py tests/test_mapping.py tests/test_ingest_limit.py tests/test_stderr.py tests/test_broken_store.py`
      prints nothing and exits 0.
      The spec PR breaks each half: `load_prs` reading the file as cp1252, and a line of
      `tests/test_mapping.py` changed.
      Evidence: at the close on `93fd6bf`, the five files' tests printed "17 passed, 14 subtests passed", as in #135, and the `git diff` against `714412f` printed nothing and exited 0; on `e72fc75`'s code too (seen-red: "The check passed"), as a `hold` should.
      broken: load_prs reading the file as cp1252 → 1 failed, 16 passed, 14 subtests passed in 40.82s (#121)
      broken: a line of tests/test_mapping.py changed → import json (#121)
- [x] C19.10 **hold** — No contract changes: `python -m pytest -q tests/contract/` passes, and
      `git -c core.safecrlf=false diff --exit-code 714412f -- tests/contract/ tests/fixtures/expected/ tests/fixtures/make_repo.py`
      prints nothing and exits 0 (`714412f` is `main` with Day 14's spec merged, #99); and
      `python -m pytest -q` passes.
      The spec PR breaks each half: the ingest report's "unmatched PR #" missing its "#", and a
      line of `tests/contract/test_ingest.py` changed.
      Evidence: at the close on `93fd6bf`, `python -m pytest -q tests/contract/` printed "7 passed", the `git diff` against `714412f` printed nothing and exited 0, and `python -m pytest -q` printed "133 passed, 131 subtests passed".
      broken: the ingest report's unmatched PR # missing its # → 1 failed, 6 passed in 56.15s (#121)
      broken: a line of tests/contract/test_ingest.py changed → import sys (#121)
- [x] C19.11 **hold** — The day stays in `bearing/` and `tests/`, with no new dependency:
      `git -c core.safecrlf=false diff --exit-code --name-only 1472abc -- .github .claude scripts pyproject.toml plan.md`
      prints nothing and exits 0 (`1472abc` is `main` with Phases 11 to 16 merged, #118).
      The spec PR breaks it: a line of `.github/pull_request_template.md` changed.
      Evidence: at the close on `93fd6bf`, the `git diff --name-only` against `1472abc` printed nothing and exited 0; #135 touched only `bearing/` and `tests/`.
      broken: a line of .github/pull_request_template.md changed → .github/pull_request_template.md (#121)

## Verify
```bash
python -m pytest -q                                              # 133 passed, (131 subtests passed)
python -m pytest -q tests/test_prs_records.py
python -m pytest -q tests/test_ingest_cli.py tests/test_mapping.py tests/test_ingest_limit.py tests/test_stderr.py tests/test_broken_store.py
python -m pytest -q tests/contract/
git -c core.safecrlf=false diff --exit-code 714412f -- tests/test_ingest_cli.py tests/test_mapping.py tests/test_ingest_limit.py tests/test_stderr.py tests/test_broken_store.py
git -c core.safecrlf=false diff --exit-code 714412f -- tests/contract/ tests/fixtures/expected/ tests/fixtures/make_repo.py
git -c core.safecrlf=false diff --exit-code --name-only 1472abc -- .github .claude scripts pyproject.toml plan.md
ruff check . && ruff format --check .
```

## Notes
- What today's code does, run in the spec PR's session on `main` at `8a17f82` with Python
  3.12.10, on the fixture: `{}` exits 0 and prints "merges 9  matched 0  unmatched merges 9
  unmatched PRs 0  direct 3" and the nine merges; `[1]` ends in "AttributeError: 'int' object has no attribute 'get'" (in
  `map_history`'s `_oid`, so no store); record 3 without `title` ends in "KeyError: 'title'"
  in `save`, after `open_store` made `bearing.db`; record 3's `number` "3" exits 0; record 3's
  `mergeCommit` "x" ends in "AttributeError: 'str' object has no attribute 'get'" in `save`;
  record 3's `number` 2, or `true` (equal to record 1's 1 in SQLite), prints "bearing: cannot
  open store at <dir>: UNIQUE constraint failed: prs.number" and leaves `bearing.db`.
- `check_records` takes the path so the line names FILE as typed, the form "cannot read FILE"
  already uses for a missing file. The path is not read again.
- `bool` is a subclass of `int` in Python, so `isinstance(True, int)` is true: the number's
  check has to refuse `bool` by name, and C19.4 and C19.8 hold that.
- Written ahead of its day, against `main` at `8a17f82`, before the code of Days 15 to 18 has
  merged: the test count assumes they land as their specs say, from Day 18's "125 passed, 131
  subtests passed" (plan.md, Course correction after Day 15's track A, item 5). The day's own
  spec-auditor run reads this spec against `main` as it is then; a spec-change PR fixes what
  moved, and re-pins C19.11's base if anything under its paths has merged since `1472abc`.
- C19.9–C19.11's `git diff` checks are commands, not tests: plan.md's "every check is a test" is
  read as every new behaviour, as Days 15 to 18 did.
- Spec-auditor, in the spec PR for Days 19 to 24 (one run over all six): one finding here,
  fixed: In scope did not say whether `mergeCommit`'s `oid` may be absent or `null`; it may,
  and C19.8 pins `{"oid": None}` passing. A note on all six, taken as a known limit: plan.md's
  item 5 says the specs are written against `4118a00`, these against `8a17f82`;
  `git diff --stat 4118a00 8a17f82 -- bearing tests` is empty, so the code they read is the
  same. It confirmed every red state, the count chain 125 → 153, the bases and the cites, and
  found no hand-off to Days 19 to 24.
- **Defect** D19.1 — found: auditor · cause: spec · made: Day 19 · In scope left a
  `mergeCommit` whose `oid` is absent or `null` undecided; now allowed, and C19.8 pins it.
- **Defect** D19.2 — found: spec-change PR · cause: process · made: none · (made: none because
  the loss was the auditor's clean-up, not any day's spec or code) the spec-auditor, cleaning up
  after itself, deleted the whole session scratchpad, which held the spec PR's 30 break records
  and the script that ran them; the breaks were run again from a rewritten script.
- No criterion in force pins what this day changes: `tests/test_ingest_cli.py::IngestCliTest::test_errors`
  pins only the missing file's start, "bearing: ", so no `Replaces:` line. No hand-off ID names
  this gap: plan.md's Course correction after Day 15's track A, item 1, found it by running
  `bearing`.
- Closed on `main` at `93fd6bf` (#135 merged), with Python 3.13.5 on Linux (WSL); CI runs 3.12.
  `python -m pytest -q` printed "133 passed, 131 subtests passed", as Tracks said; `ruff check .`
  found 75 EXE002 errors from this checkout's file modes and nothing else (74 at Day 18's close;
  the 75th is the new `tests/test_prs_records.py`), `ruff check . --extend-ignore EXE002` passed,
  and `ruff format --check .` printed "123 files already formatted" (D19.4). CI's "Style check",
  "Tests" and "Track tests seen red" passed on #135.
- Seen red again at the close: `python scripts/seen-red.py --base e72fc75 -- python -m pytest -q
  tests/test_prs_records.py` reported "8 failed in 3.84s", the spec's count; with C19.9's five
  files it said "The check passed on e72fc75" ("17 passed, 14 subtests passed"), as a `hold`
  should. `e72fc75` is `main` just before #135.
- All 8 breaks in `specs/breaks/day-19.json` were replayed at the close with `scripts/break.py`
  on `93fd6bf`, each failed its check, and each reported what its `broken:` line says, run times
  aside. C19.3's, C19.4's and C19.8's are #135's; C19.9–C19.11's five are #121's. No entry needs
  an `at`: every text a break edits is still on `main`. C19.3's entry finds a text ending in a
  line feed; this checkout's working tree is CRLF, so locally it was replayed with `\r\n` in
  its place. The manifest keeps `\n`, as #135 recorded it and as CI's LF checkout reads it.
- C19.1, C19.2 and C19.5–C19.7 have no break of their own: the seen-red runs, on `main`'s code
  in #135 and on `e72fc75` at the close, are what show their tests can fail.
- The first-day audits ran before the track and #135's body records them: the plan-auditor on
  Phase 11 (consistent, no findings) and the spec-auditor on the day (ready, two notes, no spec
  change). D18.8's gap did not repeat.
- Phase 11's "Done when" (plan.md): `{}` is C19.1, `[1]` C19.2, record 3 without `title` C19.3,
  its `number` "3" C19.4, its `mergeCommit` "x" C19.5 and its `number` record 2's C19.6, each
  with its line, exit 1, an empty stdout and no store; the fixture's `prs.json` still printing
  `tests/fixtures/expected/ingest.txt` is C19.10's `tests/contract/`. Each is a test under
  `tests/` that CI's "Tests" check ran on #135.
- Track A (#135) was written by the implementer on Haiku from the main session's brief; the
  review changed nothing in the end (D19.3). #135's body says 234 changed lines over 3 files;
  the close re-counted 233 insertions and 1 deletion.
- `docs/dashboard/token-usage.json`, refreshed at the close, is unchanged: 87 rows, from
  2026-10-28 to 2026-11-21, $361.85; it tags no row with Day 19.
- This day leaves no new hand-off. It is Phase 11's only day, so after this close merges the
  next step is CLAUDE.md's step 6: the plan-auditor on Phase 11 and on Phase 12, in a new
  session.
- **Defect** D19.3 — found: self · cause: implementation · made: Day 19 · in review of #135 the main
  session took the two `# noqa: TRY004` comments for dead code, since `pyproject.toml` selects
  no ruff rules, and removed them; `ruff check .` then reported TRY004 on both lines, and they
  were put back before the commit.
- **Defect** D19.4 — found: Track A · cause: environment · made: none · same-as: D16.4 ·
  `ruff check .` failed locally with EXE002 errors (75 at the close), from the checkout's
  file modes and on no line the day wrote; CI's check passed.
- Blind relabel at the close (`scripts/relabel.py`, 4 entries): stage 2 of 4, cause 3 of 4,
  `made:` 4 of 4 agree. The rater left D19.1's stage unclear: its text does not say when it was
  found, but the spec-auditor Note above it does, in the spec PR before any code, so `found:
  auditor` is kept. It left D19.4's unclear; kept as Track A, since #135's body reported the
  local failure before it merged. It read D19.3's cause as `implementation`, where the close
  wrote `process`: the review's edit was to the code, the spec was right and the edited code
  failed `ruff check .`, so the tag is changed to `implementation`.
