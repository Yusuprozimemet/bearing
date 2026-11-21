# Day 21 — A date that is not YYYY-MM-DD

**Phase:** 13 · **Depends on:** Day 20 · **Expected PRs:** 2 (track A, the close; this spec is in the Days 19 to 24 spec PR)

## Goal
`bearing changelog --since` and `--until` take a date in the store's form, YYYY-MM-DD, and give
argparse's usage and "argument --since: not a date in YYYY-MM-DD form: 'VALUE'" (exit 2,
nothing on stdout, the store not read) for anything else, where today `20260121` and
`2026-W03-2` pass as dates and other values get "invalid fromisoformat value"; and every new
behaviour is a test CI runs (plan.md, Phase 13).

## In scope
- **The type** (Track A), in `bearing/cli.py`: a new function `_date(value)`, the `type` of both
  `--since` and `--until` in place of `datetime.date.fromisoformat`. A value that is exactly
  four ASCII digits, "-", two ASCII digits, "-", two ASCII digits, and names a real day, gives
  `datetime.date.fromisoformat(value)`, a `date`, so Day 16's order check is unchanged.
  Anything else, `2026-02-30` included, raises
  `argparse.ArgumentTypeError(f"not a date in YYYY-MM-DD form: '{value}'")`: argparse prints
  the `changelog` subparser's usage and "bearing changelog: error: argument --since: not a date
  in YYYY-MM-DD form: 'VALUE'" (`--until` for that option) and exits 2. VALUE is put between
  single quotes as typed, not with `!r`, which switches to double quotes for a value holding a
  single quote. A plain `ValueError` would bring back "invalid _date value".
- This reverses a decision of Day 3: its In scope says "DATE is any ISO date
  `date.fromisoformat` accepts (`2026-01-14`, and on Python 3.12 also `20260114`)"
  (`specs/day-03-changelog.md`), set by D03.9. No criterion or test pins it, so no `Replaces:`
  line (plan.md, Phase 13).
- The new tests go in a new file, `tests/test_changelog_dates.py`. Its class builds the fixture
  with `tests/fixtures/make_repo.py` once, in `setUpClass`, ingests it with its `prs.json` into a
  `--data` directory under the class's temporary directory, and runs `python -m bearing` with
  `subprocess.run` from the repository root, as `tests/test_changelog_cli.py` does. Its stderr is
  read as UTF-8 with `\r\n` as `\n`.

## Out of scope
- Other commands: none takes a date.
- Times and time zones (`2026-01-21T10:00`): not a YYYY-MM-DD date, so refused like any other
  form; no criterion names one.
- The usage line's wording: argparse prints it, and the tests match it by its start,
  "usage: bearing changelog", as Day 16's do.
- A new contract version: the changelog for dates in YYYY-MM-DD is unchanged (C21.7, C21.8).
- `.github/`, `.claude/`, `scripts/`, `plan.md` and the dependencies: the day's code stays in
  `bearing/` and `tests/` (plan.md, Phases 11 to 16). C21.9 holds it.

## Tracks

One track. C21.1–C21.6 are `new`: Track A's PR shows their tests failing on `main`'s code with
`python scripts/seen-red.py -- python -m pytest -q tests/test_changelog_dates.py`, which
reports "6 failed". C21.7 holds Day 16's `tests/test_cli_errors.py`: its `git diff` half's
break ran in the day's spec-change PR, its test half is broken in Track A's PR. C21.8 and C21.9
are `hold` and their checks exist: their breaks ran in the spec PR for Days 19 to 24.

`tests/test_changelog_dates.py` holds 6 tests and no subtests. So `python -m pytest -q` goes
from Day 20's end, "138 passed, 131 subtests passed", to "144 passed, 131 subtests passed".

| Track | Owner | Work |
|---|---|---|
| A | implementer | C21.1–C21.6: `bearing/cli.py`, `tests/test_changelog_dates.py` |

## Acceptance criteria
Tick each box in the closing PR once its evidence is in it; under a box left unticked, write
`Not proven: <why>` (`specs/README.md`, "Evidence at the close").

Each case runs `changelog <option> <value> --data <the ingested store>` and passes when it
returns 2, its stdout is empty, its stderr's first line starts "usage: bearing changelog", and
its stderr's last line is exactly the line given.

- [x] C21.1 **new** — A word is refused in the new form. `--since yesterday` gives
      "bearing changelog: error: argument --since: not a date in YYYY-MM-DD form: 'yesterday'";
      `--since it's` gives "bearing changelog: error: argument --since: not a date in
      YYYY-MM-DD form: 'it's'", the value between single quotes as typed.
      Red today: "bearing changelog: error: argument --since: invalid fromisoformat value:
      'yesterday'".
      Test: `tests/test_changelog_dates.py::ChangelogDatesTest::test_word`.
      Evidence: `ChangelogDatesTest.test_word` (#147), seen red in #147 on `main`'s code ("6 failed in 1.89s", the six `new` tests together) and again at the close on `02ee59e`'s code ("6 failed in 1.59s"); `python -m pytest -q` at the close on `e679a9b` ("144 passed, 131 subtests passed").
      broken: _date quoting VALUE with !r → 1 failed in 2.41s (#147)
- [x] C21.2 **new** — The basic form is refused. `--since 20260121` gives
      "bearing changelog: error: argument --since: not a date in YYYY-MM-DD form: '20260121'".
      Red today: it exits 0 and prints the changelog from 2026-01-21.
      Test: `tests/test_changelog_dates.py::ChangelogDatesTest::test_basic_form`.
      Evidence: `ChangelogDatesTest.test_basic_form` (#147), seen red in #147 on `main`'s code ("6 failed in 1.89s", the six `new` tests together) and again at the close on `02ee59e`'s code ("6 failed in 1.59s"); `python -m pytest -q` at the close on `e679a9b` ("144 passed, 131 subtests passed").
      No break of its own: the seen-red runs are what show it can fail.
- [x] C21.3 **new** — A week date is refused. `--since 2026-W03-2` gives
      "bearing changelog: error: argument --since: not a date in YYYY-MM-DD form:
      '2026-W03-2'".
      Red today: it exits 0 and prints the changelog from 2026-01-13.
      Test: `tests/test_changelog_dates.py::ChangelogDatesTest::test_week_date`.
      Evidence: `ChangelogDatesTest.test_week_date` (#147), seen red in #147 on `main`'s code ("6 failed in 1.89s", the six `new` tests together) and again at the close on `02ee59e`'s code ("6 failed in 1.59s"); `python -m pytest -q` at the close on `e679a9b` ("144 passed, 131 subtests passed").
      No break of its own: the seen-red runs are what show it can fail.
- [x] C21.4 **new** — A day that does not exist is refused in the new form. `--since 2026-02-30`
      gives "bearing changelog: error: argument --since: not a date in YYYY-MM-DD form:
      '2026-02-30'".
      Red today: "... argument --since: invalid fromisoformat value: '2026-02-30'".
      Test: `tests/test_changelog_dates.py::ChangelogDatesTest::test_no_such_day`.
      Evidence: `ChangelogDatesTest.test_no_such_day` (#147), seen red in #147 on `main`'s code ("6 failed in 1.89s", the six `new` tests together) and again at the close on `02ee59e`'s code ("6 failed in 1.59s"); `python -m pytest -q` at the close on `e679a9b` ("144 passed, 131 subtests passed").
      No break of its own: the seen-red runs are what show it can fail.
- [x] C21.5 **new** — `--until` is checked the same way. `--until 20260121` gives
      "bearing changelog: error: argument --until: not a date in YYYY-MM-DD form: '20260121'".
      Red today: it exits 0 and prints the changelog up to 2026-01-21.
      Test: `tests/test_changelog_dates.py::ChangelogDatesTest::test_until`.
      Evidence: `ChangelogDatesTest.test_until` (#147), seen red in #147 on `main`'s code ("6 failed in 1.89s", the six `new` tests together) and again at the close on `02ee59e`'s code ("6 failed in 1.59s"); `python -m pytest -q` at the close on `e679a9b` ("144 passed, 131 subtests passed").
      No break of its own: the seen-red runs are what show it can fail.
- [x] C21.6 **new** — The date is checked before the store is looked for. `--since 20260121`
      with `--data` naming a directory that does not exist gives C21.2's exit, stdout and last
      line, and the directory still does not exist.
      Red today: it exits 1 with "bearing: no store at <dir>/bearing.db: run bearing ingest
      first".
      Test: `tests/test_changelog_dates.py::ChangelogDatesTest::test_no_store`.
      Evidence: `ChangelogDatesTest.test_no_store` (#147), seen red in #147 on `main`'s code ("6 failed in 1.89s", the six `new` tests together) and again at the close on `02ee59e`'s code ("6 failed in 1.59s"); `python -m pytest -q` at the close on `e679a9b` ("144 passed, 131 subtests passed").
      No break of its own: the seen-red runs are what show it can fail.
- [x] C21.7 **hold** — Day 16's checks of dates out of order still read dates:
      `python -m pytest -q tests/test_cli_errors.py` passes, and
      `git -c core.safecrlf=false diff --exit-code 50a000a -- tests/test_cli_errors.py`
      prints nothing and exits 0 (`50a000a` is `main` with Day 16's close merged, #128).
      Track A's PR breaks the test half: `_date` returning the string it was given, not a
      `date`. The day's spec-change PR breaks the `git diff` half: a line of
      `tests/test_cli_errors.py` changed.
      Evidence: at the close on `e679a9b`, `python -m pytest -q tests/test_cli_errors.py` printed "4 passed", and the `git diff` against `50a000a` printed nothing and exited 0.
      broken: _date returning the string it was given, not a date → 3 failed, 1 passed in 4.05s (#147)
      broken: a line of tests/test_cli_errors.py changed → self.assertEqual(result.stdout, b"") (#146)
- [x] C21.8 **hold** — Dates in YYYY-MM-DD print what they print today, and nothing else moves:
      `python -m pytest -q tests/test_changelog_cli.py tests/test_cli.py tests/test_stderr.py tests/contract/`
      passes, and
      `git -c core.safecrlf=false diff --exit-code 714412f -- tests/test_changelog_cli.py tests/test_cli.py tests/test_stderr.py tests/contract/ tests/fixtures/expected/ tests/fixtures/make_repo.py`
      prints nothing and exits 0 (`714412f` is `main` with Day 14's spec merged, #99); and
      `python -m pytest -q` passes.
      The spec PR breaks each half: `--since` read as a string where it is read as a date, and
      a line of `tests/test_changelog_cli.py` changed.
      Evidence: at the close on `e679a9b`, the four paths' tests printed "17 passed, 5 subtests passed", the `git diff` against `714412f` printed nothing and exited 0, and `python -m pytest -q` printed "144 passed, 131 subtests passed". #121's code break finds the `--since` line #147 rewrote, so its manifest entry runs `at` `02ee59e`; the close broke the same line on its own code too (D21.3).
      broken: --since read as a string where it is read as a date → 2 failed, 15 passed, 5 subtests passed in 73.07s (0:01:13) (#121)
      broken: --since read as a string where it is read as a date, on the close's code → 2 failed, 15 passed, 5 subtests passed in 21.17s (#148)
      broken: a line of tests/test_changelog_cli.py changed → import os (#121)
- [x] C21.9 **hold** — The day stays in `bearing/` and `tests/`, with no new dependency:
      `git -c core.safecrlf=false diff --exit-code --name-only 1472abc -- .github .claude scripts pyproject.toml plan.md`
      prints nothing and exits 0 (`1472abc` is `main` with Phases 11 to 16 merged, #118).
      The spec PR breaks it: a line of `scripts/check-links.py` changed.
      Evidence: at the close on `e679a9b`, the `git diff --name-only` against `1472abc` printed nothing and exited 0; #147 touched only `bearing/` and `tests/`.
      broken: a line of scripts/check-links.py changed → scripts/check-links.py (#121)

## Verify
```bash
python -m pytest -q                                              # 144 passed, (131 subtests passed)
python -m pytest -q tests/test_changelog_dates.py
python -m pytest -q tests/test_cli_errors.py
git -c core.safecrlf=false diff --exit-code 50a000a -- tests/test_cli_errors.py
python -m pytest -q tests/test_changelog_cli.py tests/test_cli.py tests/test_stderr.py tests/contract/
git -c core.safecrlf=false diff --exit-code 714412f -- tests/test_changelog_cli.py tests/test_cli.py tests/test_stderr.py tests/contract/ tests/fixtures/expected/ tests/fixtures/make_repo.py
git -c core.safecrlf=false diff --exit-code --name-only 1472abc -- .github .claude scripts pyproject.toml plan.md
ruff check . && ruff format --check .
```

## Notes
- What today's code does, run in the spec PR's session on `main` at `8a17f82` with Python
  3.12.10, on the ingested fixture: `--since yesterday` and `--since 2026-02-30` exit 2 with
  "invalid fromisoformat value: '<value>'"; `--since 20260121`, `--since 2026-W03-2` and
  `--until 20260121` exit 0 and print a changelog. `date.fromisoformat` refuses digits that
  are not ASCII (`٢٠٢٦-01-21`), so "ASCII digits only" changes nothing a test can see; a pattern
  with `\d` would match them and leave the refusal to `fromisoformat`'s `ValueError`, which
  `_date` must turn into the same `ArgumentTypeError`.
- `tests/test_stderr.py` is in C21.8 as a test of argparse's bytes under cp1252, but its case is
  `ingest . café`, not a date, so Day 21's change cannot reach it; `tests/test_changelog_cli.py`
  is what C21.8's break bites.
- C21.7's break bites three of Day 16's four tests, "3 failed, 1 passed" (spec-auditor, with
  `type=str` in a scratch copy): `test_equal_dates` through `format_changelog` comparing a
  string with a `date` (`TypeError`), and `test_reversed_dates` and
  `test_reversed_dates_no_store` through the order check's `args.since.isoformat()`
  (`AttributeError`); ISO strings do sort as dates, so the comparison itself passes.
  `test_no_command` passes.
- C21.8's code break from the spec PR for Days 19 to 24 finds `"--since",
  type=datetime.date.fromisoformat`, which Track A replaces, so it matches nothing on the
  closing commit. As Day 20 did (D20.5), the close gives that manifest entry an `at` of
  `main` before Track A and replays it in a worktree there, and records beside it a break of
  the same half on the new code (`--since`'s `type=_date` read as a string).
- Spec-auditor, in the spec PR for Days 19 to 24 (one run over all six): one finding here, a
  note, fixed: these Notes said `tests/test_stderr.py` checks a date. It confirmed every red
  state, `it's`'s double quotes today, and that `fromisoformat` refuses non-ASCII digits.
- **Defect** D21.1 — found: auditor · cause: spec · made: Day 21 · Notes said
  `tests/test_stderr.py` passes a date argparse refuses; it passes `ingest . café`; corrected.
- Written ahead of its day, against `main` at `8a17f82`, before the code of Days 15 to 20 has
  merged: the test count assumes they land as their specs say (plan.md, Course correction after
  Day 15's track A, item 5). Day 16 adds its date check after `parse_args` (C16.2); `_date` runs
  inside `parse_args`, so it comes first. The day's own spec-auditor run reads this spec against
  `main` as it is then, pins C21.7's base, and re-pins C21.9's if anything under its paths has
  merged since `1472abc`.
- C21.8 and C21.9's `git diff` checks are commands, not tests: plan.md's "every check is a test"
  is read as every new behaviour, as Days 15 to 18 did.
- No hand-off ID names this gap: plan.md's Course correction after Day 15's track A, item 1,
  found it by running `bearing`.
- First-day audits, on `main` at `b4217ba` (Linux, Python 3.13.5), in the spec-change PR:
  the plan-auditor on Phase 13, consistent, one finding (the C21.7 break Note, below); the
  spec-auditor on the day, four findings. C21.1–C21.6 red as written (a scratch prototype of
  `_date` and the six tests gave "6 failed" on `main`'s code), `python -m pytest -q`
  "138 passed, 131 subtests passed", nothing under C21.8's or C21.9's paths changed since
  `714412f` and `1472abc`, so no re-pin. Its findings: C21.7 had no pinned base, and said
  `tests/test_cli_errors.py` was not on `main` (fixed: `50a000a`, the Note above asked for
  it; not a defect); the C21.7 break Note (fixed, D21.2); C21.8's recorded break cannot run
  after Track A (fixed in the Notes, D21.3); and this record of the audit (fixed, here).
- **Defect** D21.2 — found: auditor · cause: spec · made: Day 21 · a Note said C21.7's break
  bites only `test_equal_dates`; the order check's `.isoformat()` fails both reversed-dates
  tests too, "3 failed, 1 passed"; corrected.
- **Defect** D21.3 — found: auditor · cause: spec · made: Day 21 · same-as: D20.5 · C21.8's
  break from the spec PR for Days 19 to 24 finds the `--since` line Track A rewrites, so it
  cannot run on the closing commit; the Notes now give the close an `at` and a break on the
  new code.
- The close, run on `main` at `e679a9b` (Linux under WSL, Python 3.13.5): `python -m pytest -q`
  "144 passed, 131 subtests passed", the spec's count; `tests/test_changelog_dates.py` "6
  passed", `tests/test_cli_errors.py` "4 passed", C21.8's four paths "17 passed, 5 subtests
  passed"; the three `git diff` checks of C21.7–C21.9 each printed nothing and exited 0.
  `ruff format --check .` printed "125 files already formatted"; `ruff check .` reported 77
  EXE002 errors and passed with `--extend-ignore EXE002` (D21.4).
- Seen red again at the close: `python scripts/seen-red.py --base 02ee59e -- python -m pytest -q
  tests/test_changelog_dates.py` reported "6 failed in 1.59s", the spec's count. `02ee59e` is
  `main` just before #147.
- All 7 breaks in `specs/breaks/day-21.json` were replayed at the close with `scripts/break.py`,
  each failed its check, and each reported what its `broken:` line says, run times aside.
  C21.7's test half and C21.1's quoting break are #147's; C21.7's `git diff` half is #146's;
  C21.8's two and C21.9's one are #121's; one more, C21.8's "on the close's code", is this
  close's own. As D21.3 said, #121's code break finds `"--since", type=datetime.date.fromisoformat`,
  gone since #147, so that entry carries `"at": "02ee59e"` and was replayed in a worktree there;
  the close broke `"--since", type=_date` the same way on its own code and recorded it beside.
- C21.2–C21.6 have no break of their own: the seen-red runs, on `main`'s code in #147 and on
  `02ee59e` at the close, are what show their tests can fail.
- The first-day audits ran in the spec-change PR (#146), as the Note above records; #146 has
  "human: none yet". Phase 13's "Done when" (plan.md): `yesterday` is C21.1, `20260121` C21.2,
  `2026-W03-2` C21.3, `2026-02-30` C21.4, `--until` C21.5 and the missing store C21.6, each a test
  in `tests/test_changelog_dates.py` that CI's "Tests" check ran on #147; YYYY-MM-DD dates
  unchanged is C21.8.
- Track A (#147) was written by the implementer on Haiku from the main session's brief. The
  close re-counted its diff from `git diff --numstat 02ee59e e679a9b`: 116 changed lines
  (`bearing/cli.py` 14+/2−, `tests/test_changelog_dates.py` 100+).
- `docs/dashboard/token-usage.json`, refreshed at the close, is unchanged: 87 rows, from
  2026-10-28 to 2026-11-21, $361.85; it tags no row with Day 21.
- This day leaves no new hand-off. It is Phase 13's only day, so after this close merges the
  next step is CLAUDE.md's step 6: the plan-auditor on Phase 13 and on Phase 14, in a new
  session.
- **Defect** D21.4 — found: Track A · cause: environment · made: none · same-as: D20.4 ·
  `ruff check .` failed locally with EXE002 errors (76 in #147, 77 at the close), from the
  checkout's file modes and on no line the day wrote; CI's check passed.
- Blind relabel at the close (`scripts/relabel.py compare`): stage 1 of 4 agree, cause 4 of 4,
  `made:` 1 of 4; the rater left 3 stages and 2 `made:` tags unclear. No tag changed. D21.1–D21.3
  stay `found: auditor`: the audit Notes beside them name the run that found each, before any
  code, and the blind file holds only the Defect lines. Their `made: Day 21` stays too, D21.3's
  included where the rater read "earlier": the spec PR for Days 19 to 24 wrote Day 21's own
  spec, so the text was this day's, as D20.5's was Day 20's.
