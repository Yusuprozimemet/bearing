# Day 03 — Changelog: areas, the "What I built" paragraph, and `bearing changelog`

**Phase:** 1 · **Depends on:** Day 2 · **Expected PRs:** 5 (this spec, tracks A–C, the close)

## Goal
`bearing changelog [--since DATE] [--until DATE] [--data DIR]` reads the store `bearing ingest`
wrote and prints one entry per merge on the first-parent line, grouped by area, each with its
"What I built" paragraph (or the body's first paragraph), matching a golden file on the fixture;
and both commands write UTF-8 whatever the console's code page (H02.2) and turn an unusable
`--data` into "bearing: ..." and exit 1 (H02.3).

## In scope
- `bearing/ingest/text.py` (Track A), two pure functions:
  - `area(branch)` returns the branch name up to its first `/` (plan.md, "Decisions"), and
    `"other"` for a branch with no `/`, an empty string or `None`.
  - `what_i_built(body)` returns a paragraph as a string, its lines joined by `\n`, each line
    with trailing whitespace removed, `\r\n` read as `\n` first. A **heading** is a line
    matching `^#{1,6} `; a **paragraph** is a maximal run of lines that are neither blank nor
    headings. The result is the first paragraph after the first heading whose text, stripped,
    is exactly `What I built` (any level, case as written), up to the next heading; when there
    is no such heading, or its section holds no paragraph, the first paragraph of the whole
    body; when the body has no paragraph, `""` (plan.md, "PR text that is not the template":
    an empty body gives an empty entry, never a missing PR).
- `bearing/ingest/changelog.py` (Track B):
  - `Entry(number, title, date, area, paragraph)`, a `NamedTuple`; `number` is an `int` or
    `None`, `date` a `"YYYY-MM-DD"` string.
  - `read_entries(conn)` returns one `Entry` per `commits` row of `kind` 'merge', in `position`
    order (first-parent order, oldest first). A row with a `pr_number` takes the number, the
    title, `area(head_ref)` and `what_i_built(body)` from its `prs` row. A row with none (an
    unmatched merge) takes `subject_number` (or `None`), the commit's subject as its title,
    `area(subject_branch)`, and `""`. `date` is the first ten characters of `committed_at`,
    the merge commit's UTC date. Direct commits and records off the line have no entry.
  - `format_changelog(entries, since=None, until=None)` returns the changelog's lines:
    `# Changelog`; then, for each area holding an entry in range, in name order: a blank line,
    `## <area>`, a blank line, and its entries in the given order, each
    `- #<number or -> <title> (<date>)` followed by each line of its paragraph indented by two
    spaces (none for `""`). `since` and `until` are `datetime.date` or `None`, inclusive.
    With no entry in range the result is `["# Changelog"]`.
- `bearing changelog [--since DATE] [--until DATE] [--data DIR]` (Track C): `--data` defaults to
  `.bearing`; DATE is any ISO date `date.fromisoformat` accepts (`2026-01-14`, and on Python
  3.12 also `20260114`), parsed by argparse with it, so a bad one is argparse's error, exit 2.
  It opens `<data>/bearing.db` only if that file exists (it never creates one), prints
  `format_changelog`'s lines, each ending in `\n`, and exits 0. No such file prints
  `bearing: no store at <data>/bearing.db: run bearing ingest first` (the database file's
  path) to stderr, nothing to stdout, exit 1.
- Both commands (Track C): stdout is written as UTF-8 whatever `PYTHONIOENCODING` or the
  console's code page say (H02.2), and `bearing ingest` with a `--data` it cannot create or
  open (a file, for one) prints `bearing: <message>` to stderr, nothing to stdout, and exits 1,
  as C02.11's errors do (H02.3).
- Tests: `tests/test_text.py`, `tests/test_entries.py`, `tests/test_changelog_cli.py`, the new
  contract test `tests/contract/test_changelog.py` and its golden file
  `tests/fixtures/expected/changelog.md` (Track B writes the golden file, Track C the contract
  test). As on Day 2: every test class subclasses `unittest.TestCase`, imports the module under
  test inside the test method, builds the fixture with `make_repo.py` as a subprocess (once per
  class), and runs `python -m bearing` with `cwd=` the repository root.

### What the fixture gives

From `make_repo.py` at the pinned HEAD `8c1b9f1`, ingested with its own `prs.json` (counted from
a prototype run on a fresh build, not from reading `make_repo.py`): 10 merges, so 10 entries, in
the numbers `1 2 4 3 5 6 8 9 10 11`; #4's body is empty, #2's heading is "What was built" (so
its first paragraph is the body's), #9's paragraph is its own, #10's branch `release` has no `/`,
and #11 has no record (its area is `tooling`, from its subject's branch). So the changelog,
which is the golden file, is these 37 lines (shown indented by four spaces here; the file is not):

    # Changelog

    ## day-01

    - #1 day-01/track-a-core (2026-01-07)
      A small change to the fixture, so the tests have a real case to read.

    ## day-02

    - #3 day-02/track-a-cycle (2026-01-14)
      A small change to the fixture, so the tests have a real case to read.
    - #6 day-02/track-b-grow (2026-01-21)
      A small change to the fixture, so the tests have a real case to read.

    ## day-03

    - #8 day-03/track-a-rename (2026-01-23)
      A small change to the fixture, so the tests have a real case to read.
    - #9 day-03/track-b-break-cycle (2026-01-26)
      app/b.py stops importing app.a, so the cycle is gone.

    ## docs

    - #4 docs/guide (2026-01-12)
    - #5 docs/typo-fix (2026-01-19)
      A small change to the fixture, so the tests have a real case to read.

    ## other

    - #10 release (2026-01-28)
      A small change to the fixture, so the tests have a real case to read.

    ## tooling

    - #2 tooling/scripts (2026-01-09)
      A script that prints a greeting, and the helper module it imports.
    - #11 Merge pull request #11 from acme/tooling/ci (2026-01-30)

With `--since 2026-01-14 --until 2026-01-23` it is these 18 lines:

    # Changelog

    ## day-02

    - #3 day-02/track-a-cycle (2026-01-14)
      A small change to the fixture, so the tests have a real case to read.
    - #6 day-02/track-b-grow (2026-01-21)
      A small change to the fixture, so the tests have a real case to read.

    ## day-03

    - #8 day-03/track-a-rename (2026-01-23)
      A small change to the fixture, so the tests have a real case to read.

    ## docs

    - #5 docs/typo-fix (2026-01-19)
      A small change to the fixture, so the tests have a real case to read.

## Out of scope
- Reading PRs live from `gh`; the kit's 91-merge line and its changelog of 91 entries; two
  records with one `oid` (H02.1); the Phase 1 stop — Day 4.
- Areas mapped to paths in `bearing.toml` — Phase 3 (Day 8); today an area is a branch prefix.
- A migration storing the area or the paragraph: both are computed from stored columns on read;
  a later day that needs them stored adds `002_*.sql`.
- stderr's encoding (a non-ASCII path in an error message) — the maintainer (H03.1).
- A `<data>/bearing.db` that exists but is empty or not SQLite (a `sqlite3` traceback today) —
  Day 4 (H03.2).
- A Windows job in CI (Day 1, Out of scope).

## Tracks

| Track | Owner | Work |
|---|---|---|
| A | implementer | C03.1–C03.2: `bearing/ingest/text.py`, areas and the paragraph |
| B | implementer | C03.3–C03.4: `bearing/ingest/changelog.py`, the entries, the format, the golden file |
| C | implementer | C03.5–C03.8: `bearing changelog`, the contract test, the range, UTF-8 stdout, the `--data` errors |

Each track depends on the one before it. No Track 0: both new modules are grandchildren of
existing subpackages (Day 2's Notes, "Red on CI's base"). C03.9 is `hold` and owned by this
spec's PR, which runs its check first.

## Acceptance criteria
Tick each box in the closing PR once its evidence is in it; under a box left unticked, write
`Not proven: <why>` (`specs/README.md`, "Evidence at the close").
- [x] C03.1 **new** — `area` gives "day-03" for "day-03/track-a-rename", "docs" for
      "docs/guide", "tooling" for "tooling/ci", "other" for "release", "" and `None`, and
      "other-owner" for "other-owner/patch-1/x". Red today: "No module named
      'bearing.ingest.text'".
      Test: `tests/test_text.py::AreaTest::test_areas`
      Evidence: `AreaTest.test_areas` (#21), seen red first on `681cca2`'s code;
      `python -m pytest -q` (#21).
      broken: area cut at the last "/" → 1 failed, 1 passed, 6 subtests passed in 0.09s (#21)
- [x] C03.2 **new** — `what_i_built` gives, for make_repo.py's template body, "A small change to
      the fixture, so the tests have a real case to read."; for #2's body ("## What was
      built" heading), "A script that prints a greeting, and the helper module it imports.";
      for #9's, "app/b.py stops importing app.a, so the cycle is gone."; for "", "";
      for "### What I built\r\n\r\nLine one  \r\nline two\r\n\r\nMore\r\n", "Line one\nline two";
      for "Intro.\n\n## What I built\n\nBuilt it.\n", "Built it.";
      for "## What I built\n\n## Why\n\nBecause.\n", "Because."; and for "## Heading only\n", "".
      Red today: as C03.1.
      Test: `tests/test_text.py::ParagraphTest::test_paragraphs`
      Evidence: `ParagraphTest.test_paragraphs` (#21), seen red first on `681cca2`'s code;
      `python -m pytest -q` (#21).
      broken: what_i_built: an empty What I built section returns "", no fallback → 1 failed, 1 passed, 7 subtests passed in 4.59s (#21)
- [x] C03.3 **new** — on the fixture ingested into a store in the test, `read_entries` returns 10
      entries whose numbers, in order, are `1 2 4 3 5 6 8 9 10 11`; whose areas are
      "day-01 tooling docs day-02 docs day-02 day-03 day-03 other tooling"; whose first date is
      "2026-01-07" and last "2026-01-30"; #4's paragraph is ""; and #11's title is
      "Merge pull request #11 from acme/tooling/ci" and its paragraph "". And the date is the
      commit's, not the record's: with a copy of `prs.json` whose #3 `mergedAt` is
      "2026-02-20T12:00:00Z", #3's date is still "2026-01-14". Red today (after Track A):
      "No module named 'bearing.ingest.changelog'".
      Test: `tests/test_entries.py::EntriesTest::test_fixture_entries` and
      `tests/test_entries.py::EntriesTest::test_date_is_the_commit`
      Evidence: `EntriesTest.test_fixture_entries` and `EntriesTest.test_date_is_the_commit`
      (#22), seen red first on `9612e53`'s code; `python -m pytest -q` (#22).
      broken: the date read from the record's merged_at → 1 failed in 4.78s (#22)
      broken: an inner join, dropping the unmatched merge → 1 failed in 5.53s (#22)
- [x] C03.4 **new** — `format_changelog(read_entries(conn))` on that store, each line ending in
      `\n`, is the bytes of `tests/fixtures/expected/changelog.md`, the 37 lines under "What
      the fixture gives"; `format_changelog([])` is `["# Changelog"]`; and one hand-built
      `Entry(None, "Merge branch 'x'", "2026-02-01", "other", "")` gives exactly
      "# Changelog", "", "## other", "", "- #- Merge branch 'x' (2026-02-01)"; and entries in one
      area keep the order given, not number or date order:
      `[Entry(5, "five", "2026-02-03", "docs", ""), Entry(3, "three", "2026-02-02", "docs", "")]`
      gives exactly "# Changelog", "", "## docs", "", "- #5 five (2026-02-03)",
      "- #3 three (2026-02-02)". Red today: as C03.3.
      Test: `tests/test_entries.py::ChangelogFormatTest::test_golden_and_edges`
      Evidence: `ChangelogFormatTest.test_golden_and_edges` (#22), seen red first on
      `9612e53`'s code; `python -m pytest -q` (#22).
      broken: entries in an area sorted by number → 1 failed, 1 passed, 2 subtests passed in 5.66s (#22)
- [x] C03.5 **new** — after `bearing ingest` of the fixture into `<tmp>`,
      `python -m bearing changelog --data <tmp>`, run from the repository root, exits 0 and
      prints, with `\r\n` read as `\n`, the bytes of `tests/fixtures/expected/changelog.md`;
      and `grep -c '^- #'` on that output would count 10, the ingest line's `merges`. Red
      today: argparse's "invalid choice: 'changelog'", exit 2.
      Test: `tests/test_changelog_cli.py::ChangelogCliTest::test_golden` and
      `tests/contract/test_changelog.py::ChangelogContractTest::test_golden`
      Evidence: `ChangelogCliTest.test_golden` and `ChangelogContractTest.test_golden` (#23),
      seen red first on `05c91b0`'s code; `python -m pytest -q` (#23).
      broken: changelog prints nothing → 1 failed in 5.44s (#23)
- [x] C03.6 **new** — `python -m bearing changelog --data <tmp> --since 2026-01-14 --until
      2026-01-23` on that store exits 0 and prints exactly the 18 lines under "What the fixture
      gives"; `--since 2026-02-01` prints exactly "# Changelog". Red today: as C03.5.
      Test: `tests/test_changelog_cli.py::ChangelogCliTest::test_range`
      Evidence: `ChangelogCliTest.test_range` (#23), seen red first on `05c91b0`'s code;
      `python -m pytest -q` (#23).
      broken: changelog ignores --since → 1 failed in 4.57s (#23)
- [x] C03.7 **new** — UTF-8 stdout (H02.2): with a copy of `prs.json` whose #1 and #7 titles are
      "Café → bar", written as UTF-8 bytes, and `PYTHONIOENCODING=cp1252` in the
      environment (stdout a pipe), `bearing ingest` exits 0 and its stdout, decoded as UTF-8,
      holds the line "unmatched PR #7 e21c62d Café → bar"; `bearing changelog` on that store
      exits 0 and its stdout, decoded as UTF-8, holds "- #1 Café → bar (2026-01-07)". The
      environment variable makes the check bite on Linux too, not only on a Windows console.
      Red today: ingest exits 1 with "UnicodeEncodeError: 'charmap' codec can't encode
      character" (seen in the spec's prototype run and the auditor's, on Windows).
      Test: `tests/test_changelog_cli.py::OutputEncodingTest::test_utf8_stdout`
      Evidence: `OutputEncodingTest.test_utf8_stdout` (#23), seen red first on `05c91b0`'s code;
      `python -m pytest -q` (#23).
      broken: cli.py stdout left in its own encoding → 1 failed in 4.38s (#23)
- [x] C03.8 **new** — `--data` errors (H02.3): `bearing ingest <dir>/repo --prs <dir>/prs.json
      --data <a file>` and `bearing changelog --data <a file>` each exit 1, stdout empty, stderr
      starting "bearing: "; `bearing changelog --data <an empty directory>` does the same and
      leaves no `bearing.db` in it; `bearing changelog --since 2026-13-01` exits 2 with
      "--since" in stderr. Red today: ingest's stderr starts "Traceback" (a `FileExistsError`,
      exit 1), and changelog is argparse's invalid choice.
      Test: `tests/test_changelog_cli.py::DataDirTest::test_errors`
      Evidence: `DataDirTest.test_errors` (#23), seen red first on `05c91b0`'s code;
      `python -m pytest -q` (#23).
      broken: changelog opens a missing store → 1 failed in 5.55s (#23)
      broken: ingest lets an OSError from --data through → 1 failed in 4.51s (#23)
- [x] C03.9 **hold** — the frozen files stay as Day 2 left them: the fixture, the ingest contract
      and its golden file, and the applied migration:
      `git -c core.safecrlf=false diff --exit-code 3f8958b -- tests/contract/test_fixture.py tests/contract/test_ingest.py tests/fixtures/make_repo.py tests/fixtures/expected/ingest.txt bearing/migrations/001_history.sql`
      prints nothing and exits 0.
      Evidence: the command above, exit 0 in #19 and on `a33c3f9` at the close.
      broken: the applied migration 001_history.sql edited → pr_number INTEGER NULL, (#19)

## Verify
```bash
python -m pytest -q
python tests/fixtures/make_repo.py .bearing/day03-check
python -m bearing ingest .bearing/day03-check/repo --prs .bearing/day03-check/prs.json --data .bearing/day03-data
python -m bearing changelog --data .bearing/day03-data
git -c core.safecrlf=false diff --exit-code 3f8958b -- tests/contract/test_fixture.py tests/contract/test_ingest.py tests/fixtures/make_repo.py tests/fixtures/expected/ingest.txt bearing/migrations/001_history.sql
```

## Notes
- Picks up H02.2 (C03.7) and H02.3 (C03.8). H02.1 stays with Day 4; H02.4 is the maintainer's.
- Where the code goes: plan.md's target structure has no changelog package, and a new direct
  child of `bearing` meets D01.7's editable-finder trap (Day 2's Notes). Phase 1's work lives in
  `bearing/ingest/`, so the changelog does too, as grandchildren, and no Track 0 is needed.
- The changelog's entries are the ingest line's `merges`: matched commits (the squash included)
  and unmatched two-parent merges. So on the kit, Phase 1's `grep -c '^- #'` gives 91 if
  ingest's `merges` is 91; Day 4 checks both. An unmatched merge's subject is its title,
  because it has no record; one whose subject does not parse is `#-` in `other`.
- The date is the merge commit's UTC date (`committed_at`), not the record's `mergedAt`: every
  entry has a commit and an unmatched merge has no record. `--since` and `--until` filter the
  same date, inclusive.
- **Departure:** plan.md's "Output contracts" opens "Each format has a version string in its
  output", yet the changelog's shape there (`# Changelog`, then `## <area>` sections) has none,
  and neither has the ingest line, which Day 2 shipped without recording the departure. The
  changelog follows its shape and carries none; the golden file is its contract. Whether the
  text formats are exempt or gain a version line is the maintainer's call, in a plan-change PR
  (H03.3). The layout the
  shape leaves open (blank lines, the paragraph indented two spaces under its bullet, an empty
  paragraph printing no line) is fixed here, as "Output contracts" leaves to this day.
- `tests/contract/test_changelog.py` and `changelog.md` are new files, not edits to a contract
  test; `.gitattributes` keeps `tests/fixtures/**` at `eol=lf`.
- The heading match is exact: "What was built" (#2) is not "What I built", and falls back. The
  kit's template uses `## What I built`; what its 91 bodies hold is Day 4's to read.
- C03.7 uses `PYTHONIOENCODING=cp1252`: "→" is not in cp1252, so without the fix the run fails on
  any platform; "é" alone would not bite, being in cp1252.
- Only stdout is made UTF-8. An error message holding a non-ASCII path goes to stderr in its
  own encoding; no criterion covers it (H03.1).
- Track C's brief: `tests/test_cli.py` calls `main(["--version"])` with stdout redirected to a
  `StringIO`, which has no `reconfigure`. Make stdout UTF-8 only where it can be (for example,
  after parsing, and only if `sys.stdout` has `reconfigure`), or C01.2's test breaks.
- The count: 20 tests pass today; the day adds 10 test methods (C03.1–C03.8's `Test:` fields),
  so `pytest -q` ends at "30 passed" (Day 2's subtests besides).
- Verify's `make_repo.py .bearing/day03-check` refuses a directory that is not empty: delete it
  before a second local run. Its changelog line is judged by its exit code; C03.5's tests check
  the output.
- **Defect** D03.1 — found: spec-change PR · cause: spec · made: Day 03 · the first draft gave the
  golden file as 34 lines and the range as 15, counted by eye; `wc -l` on the prototype's output
  counts 37 and 18. Corrected before the audit.
- **Defect** D03.2 — found: auditor · cause: spec · made: Day 03 · `tests/test_changelog.py` and
  `tests/contract/test_changelog.py` share a basename; with no `__init__.py` in `tests/`,
  pytest stops collection with "import file mismatch". The first is now `tests/test_entries.py`.
- **Defect** D03.3 — found: auditor · cause: spec · made: Day 03 · nothing checked that entries in
  one area keep first-parent order: in the fixture that order is also number and date order, so
  a format that sorted by number passed. C03.4 now has a pair out of both orders.
- **Defect** D03.4 — found: auditor · cause: process · made: Day 03 · same-as: D01.21 · C03.7's
  Red today quoted Python's escaped code point with a backslash; the file as written held the
  arrow itself, not what Python prints. It now quotes the error's text up to that point.
- **Defect** D03.5 — found: auditor · cause: spec · made: Day 03 · the spec stated no pytest count
  for the day's end, which CLAUDE.md reads the final "N passed" line against; Notes now say 30.
- **Defect** D03.6 — found: auditor · cause: spec · made: Day 03 · stderr's encoding went to "no
  day yet", owned by nobody; it is now H03.1.
- **Defect** D03.7 — found: auditor · cause: spec · made: Day 03 · the Notes said plan.md gives the
  changelog no version string, though plan.md says each format has one; recorded as a departure,
  H03.3.
- **Defect** D03.8 — found: auditor · cause: spec · made: Day 03 · nothing told `committed_at`
  from `mergedAt`: on the fixture each record's date equals its merge commit's. C03.3 now moves
  #3's `mergedAt`.
- **Defect** D03.9 — found: auditor · cause: spec · made: Day 03 · "DATE is `YYYY-MM-DD`" was not
  what `date.fromisoformat` enforces on Python 3.12 (`20260114` passes); In scope now says any
  ISO date.
- **Defect** D03.10 — found: auditor · cause: spec · made: Day 03 · H02.3's "unusable `--data`"
  was covered for a file and an empty directory only; a `bearing.db` that is empty or not SQLite
  still ends in a traceback, now H03.2, and "no store at" now names the database file.
- **Hand-off** H03.1 → the maintainer: decide whether stderr is written as UTF-8 too (a
  non-ASCII path in "bearing: ..." on a cp1252 console); no day owns it.
- **Hand-off** H03.2 → Day 4: `bearing changelog` on a `<data>/bearing.db` that exists but is
  empty or not SQLite prints "bearing: ..." and exits 1, not a `sqlite3` traceback.
- **Hand-off** H03.3 → the maintainer: plan.md's "Each format has a version string" against the
  ingest line and the changelog, which have none: exempt the text formats, or give them one, in
  a plan-change PR.
- At the close, on `a33c3f9`: `python -m pytest -q` gave "30 passed, 22 subtests passed", the
  count above. Verify's ingest printed `merges 10  matched 9  unmatched merges 1  unmatched PRs 1
  direct 2`, and its changelog matched `changelog.md` with 10 lines starting "- #". All 11
  `manifest:` lines (1 in #19, 2 in #21, 3 in #22, 5 in #23) parsed as JSON, and each `find`
  occurs once in the merged code. Replayed with `scripts/break.py` in an LF worktree, each failed
  its check. Every criterion had a break from a track or the spec PR, so the close ran no first
  break.
- **Defect** D03.11 — found: Track B · cause: environment · made: Day 03 · the implementer's
  Track B session ended before it reported, and Ruff's cache was left corrupt: `ruff check .`
  panicked with "wrong package cache for file" on every file. `--no-cache` runs passed, and
  deleting `.ruff_cache` fixed it (#22).
- **Defect** D03.12 — found: self · cause: process · made: Day 03 · the close's scratch script that
  replays the breaks printed each `broken:` line, arrow included, to a cp1252 stdout. It stopped
  at the first with a `UnicodeEncodeError`, D02.10's failure in the close's own tooling. Rerun
  with `PYTHONIOENCODING=utf-8`; nothing was committed.
