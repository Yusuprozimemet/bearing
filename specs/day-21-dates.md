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

- [ ] C21.1 **new** — A word is refused in the new form. `--since yesterday` gives
      "bearing changelog: error: argument --since: not a date in YYYY-MM-DD form: 'yesterday'";
      `--since it's` gives "bearing changelog: error: argument --since: not a date in
      YYYY-MM-DD form: 'it's'", the value between single quotes as typed.
      Red today: "bearing changelog: error: argument --since: invalid fromisoformat value:
      'yesterday'".
      Test: `tests/test_changelog_dates.py::ChangelogDatesTest::test_word`.
- [ ] C21.2 **new** — The basic form is refused. `--since 20260121` gives
      "bearing changelog: error: argument --since: not a date in YYYY-MM-DD form: '20260121'".
      Red today: it exits 0 and prints the changelog from 2026-01-21.
      Test: `tests/test_changelog_dates.py::ChangelogDatesTest::test_basic_form`.
- [ ] C21.3 **new** — A week date is refused. `--since 2026-W03-2` gives
      "bearing changelog: error: argument --since: not a date in YYYY-MM-DD form:
      '2026-W03-2'".
      Red today: it exits 0 and prints the changelog from 2026-01-13.
      Test: `tests/test_changelog_dates.py::ChangelogDatesTest::test_week_date`.
- [ ] C21.4 **new** — A day that does not exist is refused in the new form. `--since 2026-02-30`
      gives "bearing changelog: error: argument --since: not a date in YYYY-MM-DD form:
      '2026-02-30'".
      Red today: "... argument --since: invalid fromisoformat value: '2026-02-30'".
      Test: `tests/test_changelog_dates.py::ChangelogDatesTest::test_no_such_day`.
- [ ] C21.5 **new** — `--until` is checked the same way. `--until 20260121` gives
      "bearing changelog: error: argument --until: not a date in YYYY-MM-DD form: '20260121'".
      Red today: it exits 0 and prints the changelog up to 2026-01-21.
      Test: `tests/test_changelog_dates.py::ChangelogDatesTest::test_until`.
- [ ] C21.6 **new** — The date is checked before the store is looked for. `--since 20260121`
      with `--data` naming a directory that does not exist gives C21.2's exit, stdout and last
      line, and the directory still does not exist.
      Red today: it exits 1 with "bearing: no store at <dir>/bearing.db: run bearing ingest
      first".
      Test: `tests/test_changelog_dates.py::ChangelogDatesTest::test_no_store`.
- [ ] C21.7 **hold** — Day 16's checks of dates out of order still read dates:
      `python -m pytest -q tests/test_cli_errors.py` passes, and
      `git -c core.safecrlf=false diff --exit-code 50a000a -- tests/test_cli_errors.py`
      prints nothing and exits 0 (`50a000a` is `main` with Day 16's close merged, #128).
      Track A's PR breaks the test half: `_date` returning the string it was given, not a
      `date`. The day's spec-change PR breaks the `git diff` half: a line of
      `tests/test_cli_errors.py` changed.
- [ ] C21.8 **hold** — Dates in YYYY-MM-DD print what they print today, and nothing else moves:
      `python -m pytest -q tests/test_changelog_cli.py tests/test_cli.py tests/test_stderr.py tests/contract/`
      passes, and
      `git -c core.safecrlf=false diff --exit-code 714412f -- tests/test_changelog_cli.py tests/test_cli.py tests/test_stderr.py tests/contract/ tests/fixtures/expected/ tests/fixtures/make_repo.py`
      prints nothing and exits 0 (`714412f` is `main` with Day 14's spec merged, #99); and
      `python -m pytest -q` passes.
      The spec PR breaks each half: `--since` read as a string where it is read as a date, and
      a line of `tests/test_changelog_cli.py` changed.
- [ ] C21.9 **hold** — The day stays in `bearing/` and `tests/`, with no new dependency:
      `git -c core.safecrlf=false diff --exit-code --name-only 1472abc -- .github .claude scripts pyproject.toml plan.md`
      prints nothing and exits 0 (`1472abc` is `main` with Phases 11 to 16 merged, #118).
      The spec PR breaks it: a line of `scripts/check-links.py` changed.

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
