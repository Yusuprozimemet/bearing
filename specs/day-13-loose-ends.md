# Day 13 — Loose ends: stderr as UTF-8, and a warning at `gh`'s 1000-PR limit

**Phase:** 5 · **Depends on:** Day 12 · **Expected PRs:** 4 (this spec, track A, track B, the close)

## Goal
Every line Bearing writes to stderr after its arguments are parsed is UTF-8 whatever the
console's code page (H03.1), and `bearing ingest` says so on stderr when it has exactly 1000 PR
records, the number `gh` stops at (H04.2); every check is a test CI runs (plan.md, Phase 5).

## In scope
- **stderr is UTF-8** (Track A, H03.1), in `bearing/cli.py`: `main` sets stderr's encoding to
  UTF-8 where it sets stdout's, after the arguments are parsed, and leaves a stream without
  `reconfigure` (a test's `StringIO`) as it is. It keeps stderr's error handler,
  "backslashreplace" (`reconfigure` with an encoding alone sets it to "strict"), so a
  character UTF-8 cannot encode, a lone surrogate, is still written as its escape.
  Every "bearing: ..." line and the line `--stats` prints go through that stream, so no
  message's text changes.
- **The 1000-record warning** (Track B, H04.2), in `bearing/cli.py`: when `bearing ingest` has
  exactly 1000 PR records, read from `gh` or from the `--prs` file, it writes one line to
  stderr, "bearing: warning: 1000 PR records is gh's limit; a history with more is cut".
  Stdout and the exit code are what they are without it. 999 records and 1001 records print
  nothing: 1001 cannot be one `gh` call's output.
- The tests' 1000 records are the fixture's 10 (`prs.json`, which `tests/fixtures/make_repo.py`
  writes) followed by 990 that match no commit: a copy of the first record with "number"
  5000 + i, "mergeCommit" null and "title" and "headRefName" "pad-i", for i from 0 to 989. The
  999 and the 1001 are the same with 989 and 991.

## Out of scope
- What `argparse` writes before the arguments are parsed (a usage error, `--help`,
  `--version`): left in the console's encoding (plan.md, Phase 5). C13.3 holds it.
- Pagination, and an option for the limit: the maintainer's decision (plan.md, Course
  correction after Phase 4, item 2).
- A warning in `bearing changelog` or any command that reads the store: the store does not
  record where its PR records came from.
- Where in a failing run the warning is written (a store that cannot be opened after the
  records are read): not pinned; the criteria cover runs that exit 0.
- `bearing summary`, coupling that follows renames, the "one or two sentences" rule, and the
  kit's H02.4 — no day owns them (plan.md, Course correction after Phase 4, items 4 and 5).
- The agentic-workflow-driver: a separate program; nothing here depends on it (plan.md, Phase 5).

## Tracks

A and B stand alone and may run in either order; both edit `bearing/cli.py`, so the second
branches from `main` after the first has merged, as every track does.

| Track | Owner | Work |
|---|---|---|
| A | implementer | C13.1–C13.3, C13.8–C13.9: `bearing/cli.py`, `tests/test_stderr.py` |
| B | implementer | C13.4–C13.6: `bearing/cli.py`, `tests/test_ingest_limit.py` |

C13.7 is `hold` and its check exists; its break runs in this spec's PR. C13.3, C13.5 and C13.9
are `hold` with tests their tracks add: each track's PR breaks its own (C13.9's: the error
handler left out of the `reconfigure`). C13.8's check exists, but its break (stderr
reconfigured without the `hasattr` guard) needs Track A's code: Track A's PR runs it.

## Acceptance criteria
Tick each box in the closing PR once its evidence is in it; under a box left unticked, write
`Not proven: <why>` (`specs/README.md`, "Evidence at the close").

- [x] C13.1 **new** — A "bearing: ..." line reaches stderr as UTF-8. In a subprocess started
      with `PYTHONIOENCODING=cp1252`, with NAME the directory name "łódź-café" under a
      temporary directory (never created), each of these exits 1 with nothing on stdout and a
      stderr that decodes as UTF-8 to one line starting "bearing: " and holding NAME:
      `bearing changelog --data NAME`; `bearing timeline . --data NAME`;
      `bearing direction . --data NAME --config tests/fixtures/bearing.toml`;
      `bearing page . --data NAME --config tests/fixtures/bearing.toml --out NAME.html`; and,
      on the fixture's repository, `bearing ingest <repo> --prs NAME.json`. The first four say
      "no store at", the fifth "cannot read".
      Red today: stderr holds the escapes for U+0142 and U+017A (a backslash, "u" and four
      hex digits: six ASCII bytes each) and the single bytes F3 and E9, so it does not decode
      as UTF-8 ("UnicodeDecodeError" at F3); five subtests fail.
      Test: `tests/test_stderr.py::StderrTest::test_error_lines_are_utf8`.
      Evidence: `StderrTest.test_error_lines_are_utf8` (#90), seen red in #90 on `main` and again at the close on `0472de4` ("6 failed, 1 passed", with C13.2's test); `python -m pytest -q` at the close on `56892cd`.
- [x] C13.2 **new** — The line `--stats` prints goes through the same stream. Called in the
      test's process on the ingested fixture, with `sys.stderr` a `TextIOWrapper` over a
      `BytesIO` in cp1252 and `sys.stdout` a `StringIO`, `bearing.cli.main` given "timeline",
      the repository, "--data", a data directory no timeline has run on, and "--stats"
      returns 0; the wrapper's `encoding` is then "utf-8"; and, once the wrapper is flushed,
      the `BytesIO` holds the one line "blobs parsed 28  cache hits 0" (a carriage return
      before the line feed ignored).
      Red today: the wrapper's `encoding` is still "cp1252".
      Test: `tests/test_stderr.py::StderrTest::test_stats_stream_is_utf8`.
      Evidence: `StderrTest.test_stats_stream_is_utf8` (#90), seen red in #90 on `main` and again at the close on `0472de4` ("6 failed, 1 passed", with C13.1's test); `python -m pytest -q` at the close on `56892cd`.
- [x] C13.3 **hold** — What `argparse` writes is left as it is. In a subprocess started with
      `PYTHONIOENCODING=cp1252`, `bearing ingest . café` exits 2 with nothing on stdout, and
      stderr's last line is the bytes of "bearing: error: unrecognized arguments: caf"
      followed by the single byte E9.
      Test: `tests/test_stderr.py::StderrTest::test_argparse_left_alone`.
      Evidence: `StderrTest.test_argparse_left_alone` (#90); `python -m pytest -q` at the close on `56892cd`.
      broken: stderr reconfigured before parse_args → 1 failed in 4.69s (#90)
- [x] C13.4 **new** — `bearing ingest` on the fixture with a `--prs` file of 1000 records (In
      scope) exits 0; stderr is the one line "bearing: warning: 1000 PR records is gh's
      limit; a history with more is cut"; stdout has 993 lines, the first
      "merges 10  matched 9  unmatched merges 1  unmatched PRs 991  direct 2", and none
      holds "warning".
      Red today: stderr is empty.
      Test: `tests/test_ingest_limit.py::IngestLimitTest::test_warns_at_1000`.
      Evidence: `IngestLimitTest.test_warns_at_1000` (#91), seen red in #91 on `main` and again at the close on `ec3eb23` ("2 failed, 1 passed, 2 subtests passed", with C13.6's test); `python -m pytest -q` at the close on `56892cd`.
      broken: the warning only for records from gh, not for a --prs file → 1 failed in 4.85s (#91)
      broken: the warning written to stdout → 1 failed in 4.81s (#91)
- [x] C13.5 **hold** — One record either side prints no warning. With 999 records and with
      1001, `bearing ingest` on the fixture exits 0 with an empty stderr; stdout's first line
      is "merges 10  matched 9  unmatched merges 1  unmatched PRs 990  direct 2" with 999
      and "merges 10  matched 9  unmatched merges 1  unmatched PRs 992  direct 2" with 1001.
      Test: `tests/test_ingest_limit.py::IngestLimitTest::test_silent_at_999_and_1001`.
      Evidence: `IngestLimitTest.test_silent_at_999_and_1001` (#91); `python -m pytest -q` at the close on `56892cd`.
      broken: the warning at 1000 or more records, so 1001 warns → 1 failed, 1 passed, 1 subtests passed in 5.08s (#91)
      broken: the warning at 999 or more records, so 999 warns → 2 failed, 1 passed in 5.14s (#91)
- [x] C13.6 **new** — The warning covers records read from `gh`. Called in the test's process
      without `--prs`, with `gh`'s call answered by the same 1000 records
      (`tests/test_gh.py`'s way: `subprocess.run` patched for `gh` only), `bearing.cli.main`
      given "ingest", the repository, "--data" and a temporary directory returns 0, what it
      wrote to stderr is the warning line once and nothing else, and stdout is the 993 lines
      of C13.4.
      Red today: stderr is empty.
      Test: `tests/test_ingest_limit.py::IngestLimitTest::test_warns_from_gh`.
      Evidence: `IngestLimitTest.test_warns_from_gh` (#91), seen red in #91 on `main` and again at the close on `ec3eb23` ("2 failed, 1 passed, 2 subtests passed", with C13.4's test); `python -m pytest -q` at the close on `56892cd`.
      broken: the warning only for a --prs file, not for records from gh → 1 failed in 4.96s (#91)
- [x] C13.7 **hold** — No contract changes: `git diff --exit-code 001ed11 -- tests/contract/`
      prints nothing and exits 0 (`001ed11` is `main` at Day 12's close, #81).
      Evidence: `git -c core.safecrlf=false diff --exit-code 001ed11 -- tests/contract/ tests/test_gh.py` printed nothing and exited 0 at the close on `56892cd`; CI's "Frozen files stay unedited" passed on the heads of #90 and #91. The break's report is the diff's last line, ")"; the check failed by its exit code, 1.
      broken: a contract test edited (the golden file's bytes stripped before the comparison) → ) (#88)
- [x] C13.8 **hold** — A stderr without `reconfigure` is left as it is: `tests/test_gh.py`,
      whose `IngestLiveTest` calls `main` with a `StringIO` as stderr, passes unedited:
      `python -m pytest -q tests/test_gh.py` prints "5 passed, 6 subtests passed", and
      `git diff --exit-code 001ed11 -- tests/test_gh.py` prints nothing and exits 0.
      Evidence: `python -m pytest -q tests/test_gh.py` printed "5 passed, 6 subtests passed" and the diff against `001ed11` printed nothing and exited 0, at the close on `56892cd` (#90).
      broken: stderr reconfigured without the hasattr guard → 4 failed, 3 passed, 4 subtests passed in 5.50s (#90)
- [x] C13.9 **hold** — A character UTF-8 cannot encode is still an escape, not a traceback.
      In a subprocess started with `PYTHONIOENCODING=cp1252`, `bearing changelog --data` with
      a name holding the lone surrogate U+DC80 exits 1 with nothing on stdout; stderr is one
      line starting "bearing: no store at" that holds the escape for U+DC80 (a backslash and
      "udc80") and does not hold "Traceback".
      Test: `tests/test_stderr.py::StderrTest::test_surrogate_is_escaped`.
      Evidence: `StderrTest.test_surrogate_is_escaped` (#90); `python -m pytest -q` at the close on `56892cd`.
      broken: the error handler left out of the reconfigure → 1 failed in 4.71s (#90)

## Verify
```bash
python -m pytest -q
python -m pytest -q tests/test_stderr.py tests/test_ingest_limit.py
git -c core.safecrlf=false diff --exit-code 001ed11 -- tests/contract/ tests/test_gh.py
ruff check . && ruff format --check .
```

## Notes
- The reconfigure stays after `parse_args`, as stdout's does: `--version` never touches a
  stream (`bearing/cli.py`'s comment), and C13.3 pins what that leaves in the console's
  encoding.
- Python gives stderr the error handler "backslashreplace" whatever `PYTHONIOENCODING` says,
  and `reconfigure(encoding="utf-8")` alone replaces it with "strict": a lone surrogate in a
  path (on Linux, any byte of an argument that is not UTF-8) would then end in a
  "UnicodeEncodeError" traceback where today it prints the line. The handler is passed again,
  and C13.9 holds it. stdout's handler is as Day 3 left it and is not changed here.
- In C13.4 to C13.6 every `bearing ingest` names a temporary `--data`, so no test writes
  `.bearing/` in the working directory; a subprocess's stderr is compared with a carriage
  return before a line feed ignored (Windows writes one), as in C13.1, C13.3 and C13.9.
- C13.2's line is ASCII, so its bytes are the same in any encoding: the criterion reads the
  stream's `encoding` instead. 28 is the count `tests/test_timeline_cli.py` already pins for a
  first run on the fixture.
- C13.1 and C13.3 pass a non-ASCII argument to a subprocess. CI's Linux runner decodes it as
  UTF-8; a runner with a C locale and no UTF-8 coercion would not, and the tests would fail
  there, not pass wrongly.
- plan.md (Course correction after Phase 4, item 5) lists `README.md` as still the kit's own,
  with #86 open; #86 merged before this day (`8e8dd4b`), so that item is closed. plan.md is
  not changed here.
- Exactly 1000 records may be a whole history; the line says what the limit does, not that
  anything is missing (plan.md, Course correction after Phase 4, item 3).
- C13.7's break ran in this spec's PR; `scripts/break.py` reports the last line the check
  printed, which for a `git diff` is the last line of the diff, ")". The check failed by its
  exit code, 1.
- The close ran on `56892cd`. `python -m pytest -q` printed "104 passed, 116 subtests passed",
  against "97 passed, 109 subtests passed" before the day. Each of the Verify commands ran as
  written: the two test files "7 passed, 7 subtests passed", the diff nothing with exit 0, and
  ruff clean.
- All 9 breaks in `specs/breaks/day-13.json` were replayed at the close with `scripts/break.py`
  and each failed its check. The `broken:` lines above are the close's, not the PRs'.
- Phase 5's "Done when" (plan.md): the non-ASCII path's UTF-8 bytes are C13.1; the warning line
  once on stderr, none on stdout and exit 0 is C13.4; an empty stderr at 999 records is C13.5;
  the contract diff is C13.7. `pytest -q` in CI is the "Tests" check on #96. Every one is a
  test or command CI runs, with no hand run, no kit history and no screenshot.
- H03.1 is closed by C13.1 and C13.2, H04.2 by C13.4 to C13.6. This day leaves no new hand-off.
- Neither the tracks nor the close recorded a defect; the seven below were all found before any
  code. The blind rater agreed with all seven on stage, cause and `made:`.
- **Defect** D13.1 — found: auditor · cause: spec · made: Day 13 · the draft let Track A
  reconfigure stderr with no criterion on the `hasattr` guard, which `tests/test_gh.py`'s
  `StringIO` needs (plan-auditor, finding 4); C13.8 added in this spec's PR.
- **Defect** D13.2 — found: auditor · cause: spec · made: Day 13 · the Notes said stderr's error
  handler is not changed; `reconfigure` with an encoding alone sets it to "strict", and a lone
  surrogate in a path would end in a traceback with C13.1, C13.3 and C13.8 passing
  (spec-auditor, finding 1); the In scope names the handler and C13.9 holds it, in this spec's
  PR.
- **Defect** D13.3 — found: auditor · cause: spec · made: Day 13 · C13.1's "Red today" wrote
  the two escapes with a backslash, which the saved file showed as the characters themselves
  (spec-auditor, finding 2); described in words in this spec's PR.
- **Defect** D13.4 — found: auditor · cause: spec · made: Day 13 · C13.2 read the `BytesIO`
  without a flush and without saying how the line ends on Windows (spec-auditor, finding 3);
  fixed in this spec's PR.
- **Defect** D13.5 — found: auditor · cause: spec · made: Day 13 · C13.8 said "unedited" with
  no check of it (spec-auditor, finding 4); the diff against `001ed11` added in this spec's PR.
- **Defect** D13.6 — found: auditor · cause: spec · made: Day 13 · C13.4 and C13.5 named no
  `--data` and did not say how stderr's line ending is read (spec-auditor, finding 5); a Note
  added in this spec's PR.
- **Defect** D13.7 — found: auditor · cause: spec · made: Day 13 · two backticked calls of
  `main` wrapped across lines, so the text between them read as code (spec-auditor, finding
  6); written in words in this spec's PR.
