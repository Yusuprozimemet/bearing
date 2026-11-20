# Day 16 — The command line's silent successes

**Phase:** 8 · **Depends on:** Day 15 · **Expected PRs:** 3 (this spec, track A, the close)

## Goal
`bearing` with no command, and `bearing changelog` with `--since` after `--until`, are argument
errors (usage and one error line on stderr, exit 2, nothing on stdout) where today both exit 0,
and every new behaviour is a test CI runs (plan.md, Phase 8).

## In scope
- **No command** (Track A), in `main` in `bearing/cli.py`: the subparsers are required
  (`add_subparsers(dest="command", required=True)`), so `bearing` with no command prints
  argparse's usage and, as Python 3.12 prints it, the line
  "bearing: error: the following arguments are required: command" on stderr, and exits 2, as
  for any missing argument. `bearing --version` is unchanged: the version action exits before
  the required check.
- **Dates out of order** (Track A), in `main` in `bearing/cli.py`: right after `parse_args`,
  before any stream is reconfigured and before `_changelog` is called, a `changelog` whose
  `--since` and `--until` are both given and `--since` is the later date calls the `changelog`
  subparser's `error` with "--since <since> is after --until <until>", the dates in ISO form.
  argparse prints the subparser's usage and "bearing changelog: error: --since 2026-01-23 is
  after --until 2026-01-21" (for those dates) on stderr and exits 2. The store is not opened
  or looked for. Equal dates stay one day; one date alone, or none, is unchanged.
- The new tests go in a new file, `tests/test_cli_errors.py`, run as `tests/test_cli.py` runs
  the command (`python -m bearing` in a subprocess, from the repository root). Its class builds
  the fixture with `tests/fixtures/make_repo.py` and ingests it with its `prs.json` once, in
  `setUpClass`, as `tests/test_changelog_cli.py` does. Each test compares stderr with its
  `\r\n` turned to `\n`; the usage is matched by its start only, since argparse wraps it to the
  terminal's width.

## Out of scope
- Other argument combinations that print little: `--since` alone after every merge prints
  "# Changelog" and stays a success (C03's `test_range` pins it). Not asked for.
- Dates out of order anywhere but `changelog`: no other command takes `--since` or `--until`.
- The line `if args.command != "ingest": return 0` in `main`: unreachable once a command is
  required, and left as it is; it is not a behaviour, and no criterion checks it.
- A check on the order of the date check and the stream reconfigure, or on a store that
  exists not being read: plan.md's Phase 8 defines "not read" by the no-store case, which C16.3
  checks. With an ingested store, code that read it and then raised the error would pass C16.2;
  a reviewer reads Track A's diff for it.
- A new contract version: neither case is in a golden file, and the outputs of every command
  given valid arguments do not change (C16.6).
- `.github/`, `.claude/`, `scripts/`, `plan.md` and the dependencies: the day's code stays in
  `bearing/` and `tests/` (plan.md, Phases 7 to 10). C16.7 holds it.

## Tracks

One track. C16.1–C16.3 are `new`: Track A's PR shows their three tests failing on `main`'s code
with
`python scripts/seen-red.py -- python -m pytest -q tests/test_cli_errors.py::CliErrorsTest::test_no_command tests/test_cli_errors.py::CliErrorsTest::test_reversed_dates tests/test_cli_errors.py::CliErrorsTest::test_reversed_dates_no_store`,
which reports "3 failed". C16.4 is `hold` with a test Track A adds, without a Track 0 (as Day
14's C14.3): Track A's PR shows it passing on `main`'s code with
`python scripts/seen-red.py -- python -m pytest -q tests/test_cli_errors.py::CliErrorsTest::test_equal_dates`,
which exits 1 ("passes there"), and then breaks it. C16.5–C16.7 are `hold` and their checks exist: their breaks run in
this spec's PR.

`tests/test_cli_errors.py` holds 4 tests and no subtests. So `python -m pytest -q` goes from
Day 15's end, "111 passed, 128 subtests passed", to "115 passed, 128 subtests passed".

| Track | Owner | Work |
|---|---|---|
| A | implementer | C16.1–C16.4: `bearing/cli.py`, `tests/test_cli_errors.py` |

## Acceptance criteria
Tick each box in the closing PR once its evidence is in it; under a box left unticked, write
`Not proven: <why>` (`specs/README.md`, "Evidence at the close").

- [ ] C16.1 **new** — `bearing` with no command is a missing argument. `python -m bearing`
      exits 2, prints nothing on stdout, and its stderr starts with "usage: bearing " and ends
      with the line "bearing: error: the following arguments are required: command".
      Red today: it exits 0 with an empty stderr.
      Test: `tests/test_cli_errors.py::CliErrorsTest::test_no_command`.
- [ ] C16.2 **new** — `--since` after `--until` is an argument error. On the ingested fixture,
      `python -m bearing changelog --data <its store> --since 2026-01-23 --until 2026-01-21`
      exits 2, prints nothing on stdout, and its stderr starts with "usage: bearing changelog "
      and ends with the line
      "bearing changelog: error: --since 2026-01-23 is after --until 2026-01-21".
      Red today: it exits 0 and prints "# Changelog".
      Test: `tests/test_cli_errors.py::CliErrorsTest::test_reversed_dates`.
- [ ] C16.3 **new** — The dates are checked before the store is looked for. The same command
      with `--data` naming a directory that does not exist gives the same exit, stdout and
      stderr as C16.2, and the directory still does not exist.
      Red today: it exits 1 with "bearing: no store at ...: run bearing ingest first".
      Test: `tests/test_cli_errors.py::CliErrorsTest::test_reversed_dates_no_store`.
- [ ] C16.4 **hold** — Equal dates stay one day. On the ingested fixture,
      `bearing changelog --since 2026-01-21 --until 2026-01-21` exits 0, its stderr is empty,
      and its stdout is these 6 lines: "# Changelog", "", "## day-02", "",
      "- #6 day-02/track-b-grow (2026-01-21)" and
      "  A small change to the fixture, so the tests have a real case to read.".
      Test: `tests/test_cli_errors.py::CliErrorsTest::test_equal_dates`.
      Track A's PR breaks it: the new check's `>` made `>=`.
- [ ] C16.5 **hold** — `bearing --version` and `changelog` with dates in order print what they
      print today: `python -m pytest -q tests/test_cli.py tests/test_changelog_cli.py` passes,
      and
      `git -c core.safecrlf=false diff --exit-code 714412f -- tests/test_cli.py tests/test_changelog_cli.py`
      prints nothing and exits 0.
      This spec's PR breaks each half: `format_changelog` dropping the `--until` date itself,
      and a line of `tests/test_changelog_cli.py` changed.
- [ ] C16.6 **hold** — No contract changes: `python -m pytest -q tests/contract/` passes, and
      `git -c core.safecrlf=false diff --exit-code 714412f -- tests/contract/ tests/fixtures/expected/`
      prints nothing and exits 0 (`714412f` is `main` with Day 14's spec merged, #99); and
      `python -m pytest -q` passes.
      This spec's PR breaks each half: the changelog's heading changed, and a line of
      `tests/contract/test_changelog.py` changed.
- [ ] C16.7 **hold** — The day stays in `bearing/` and `tests/`, with no new dependency:
      `git -c core.safecrlf=false diff --exit-code --name-only 85a21a1 -- .github .claude scripts pyproject.toml plan.md`
      prints nothing and exits 0 (`85a21a1` is `main` with Phases 7 to 10 merged, #102).
      This spec's PR breaks it: a line of `pyproject.toml` changed.

## Verify
```bash
python -m pytest -q                                              # 115 passed, 128 subtests passed
python -m pytest -q tests/test_cli_errors.py tests/test_cli.py tests/test_changelog_cli.py
python -m pytest -q tests/contract/
git -c core.safecrlf=false diff --exit-code 714412f -- tests/test_cli.py tests/test_changelog_cli.py
git -c core.safecrlf=false diff --exit-code 714412f -- tests/contract/ tests/fixtures/expected/
git -c core.safecrlf=false diff --exit-code --name-only 85a21a1 -- .github .claude scripts pyproject.toml plan.md
ruff check . && ruff format --check .
```

## Notes
- What today's code does, run in this spec's session on `main` at `537e986` with Python 3.12.10:
  `python -m bearing` exits 0 and prints nothing; `changelog --since 2026-01-23 --until 2026-01-21`
  on the ingested fixture exits 0 and prints "# Changelog"; on a `--data` with no store it exits 1
  with "no store". With equal dates 2026-01-21 it prints C16.4's 6 lines.
- A prototype of In scope's two changes, run on a copy of `bearing/cli.py` in this spec's
  session, printed C16.1's and C16.2's last lines, exit 2 and an empty stdout, C16.3's with no
  store, `--version` as today, and C16.4's lines with equal dates. Its usage for no command
  wrapped to two lines at the default width of 80 columns: hence the tests match the usage by
  its start.
- `bearing changelog`'s usage, "usage: bearing changelog [-h] [--since SINCE] [--until UNTIL]
  [--data DATA]", is printed by argparse; C16.2 pins its start, not its options, so a new option
  does not break it.
- CI runs Python 3.12 (`.github/workflows/tests.yml`), the version plan.md's Phase 8 names for
  C16.1's line. Python 3.13 and later may word it differently; a run on them is not this day's.
- Written ahead of its day, against `main` at `537e986`, before Days 14 and 15's code has merged
  (#101 open): the test count assumes both land as their specs say (plan.md, Course correction
  after Phase 6, item 6). The day's own spec-auditor run re-pins C16.7's base to `main` before
  the day if anything under its paths has merged since `85a21a1`.
- C16.5–C16.7's `git diff` checks are commands, not tests: plan.md's "every check is a test" is
  read as every new behaviour, as Day 15's C15.6–C15.8 did.
- Spec-auditor, before this spec's PR: 2 findings, both fixed. C16.4, a `hold` whose test Track A
  adds with no Track 0, had no run showing it pass on `main`'s code (a `seen-red.py` run that
  exits 1, as Day 14's C14.3); and In scope promised the check comes before the reconfigure and
  before an existing store is read, with no criterion for either (Out of scope now says so). It
  confirmed every `new` criterion red as stated, C16.4's 6 lines, C16.5's break ("1 failed, 5
  passed"), the counts and the bases, and found no hand-off to this day.
- **Defect** D16.1 — found: auditor · cause: spec · made: Day 16 · C16.4's new `hold` test had no
  stated run on `main`'s code before its break; Tracks now names the `seen-red.py` run.
- **Defect** D16.2 — found: auditor · cause: spec · made: Day 16 · In scope's "before any stream
  is reconfigured" and "the store is not opened" with a store present had no check; Out of scope
  now says they are left to review.
