# Day 02 — Ingest: the first-parent line, the PR records and the mapping, stored

**Phase:** 1 · **Depends on:** Day 1 · **Expected PRs:** 7 (this spec, tracks 0 and A–D, the close)

## Goal
`bearing ingest <repo> --prs <file>` reads the first-parent line of `main` and the recorded PR
JSON, maps each record to its commit (`mergeCommit` first, the "Merge pull request #N" subject as
fallback, never guessed), stores both once in SQLite under `--data`, and on the fixture prints
`merges 10  matched 9  unmatched merges 1  unmatched PRs 1  direct 2` and the two unmatched items,
matching a golden file.

## In scope
- `bearing/ingest/__init__.py` and `bearing/store/__init__.py`, each a docstring only (Track 0;
  see Notes, "Red on CI's base").
- `bearing/ingest/history.py` (Track A):
  - `read_first_parent(repo)` runs `git -C <repo> log --first-parent --reverse
    --format=%H%x00%P%x00%ct%x00%s main --` (read-only: no checkout, fetch or write), with
    `encoding="utf-8"` given to `subprocess.run`, and returns one `Commit(sha, parents,
    committed_at, subject)` per commit, oldest first; `parents` is a tuple of full SHAs;
    `committed_at` is `%ct` as `datetime.fromtimestamp(t, UTC).isoformat()`
    ("2026-01-05T12:00:00+00:00"), so it does not depend on how a git version prints `%cI`. A
    git failure raises an error naming git's stderr.
  - `parse_merge_subject(subject)` returns `MergeSubject(number, owner, branch)`, a
    `NamedTuple`, for exactly `Merge pull request #<N> from <owner>/<branch>` (the owner has
    no `/`; the branch is the rest, and may hold `/`), and `None` for anything else, GitHub's
    squash form "Title (#N)" included.
- `bearing/ingest/mapping.py` (Track B):
  - `load_prs(path)` reads `gh`'s JSON list (plan.md, "Decisions") as UTF-8, whatever the
    system's code page.
  - `map_history(commits, records)` maps in two passes, and nothing else:
    1. a record whose `mergeCommit.oid` is a commit on the line is matched to it;
    2. a two-parent commit still unmatched whose subject parses to #N is matched to record #N
       only when that record's `mergeCommit` is absent, `null` or has no `oid`.

    A record and a commit are each matched at most once: the first in first-parent order wins
    (two records with one `oid`, two merges saying one #N), and the loser stays unmatched. A
    record whose `oid` names a commit off the line stays unmatched, whatever a subject says
    (plan.md, "Merges out of order"; H01.3: #7). A single-parent commit is matched only by
    pass 1: the squash commit's "(#N)" is never read (H01.3: #6).
  - The counts: **merges** = matched commits + unmatched two-parent commits; **matched** =
    matched commits; **unmatched merges** = two-parent commits not matched; **unmatched PRs** =
    records not matched; **direct** = single-parent (and root) commits not matched. A direct
    commit is counted as direct, not reported as an error.
  - `format_report(result)` returns the report's lines: the summary line, fields separated by
    two spaces, then `unmatched merge <sha7> <subject>` for each unmatched merge in first-parent
    order, then `unmatched PR #<N> <oid7 or -> <title>` for each unmatched record in number
    order (`-` when it has no `oid`).
- `bearing/migrations/001_history.sql` and `bearing/store/db.py` (Track C):
  - the schema: `commits(sha PRIMARY KEY, position UNIQUE, parent_count, subject, committed_at,
    kind CHECK IN ('merge', 'direct'), pr_number NULL, subject_number NULL, subject_owner NULL,
    subject_branch NULL)` and `prs(number PRIMARY KEY, title, body, head_ref, base_ref,
    merge_oid NULL, merged_at NULL)`; `kind` is `merge` for a matched or two-parent commit,
    `direct` otherwise; the `subject_*` columns come from `parse_merge_subject` (Day 3 reads
    them for the area of a merge with no record).
  - `open_store(data_dir)` creates `data_dir` and `<data_dir>/bearing.db` when missing and
    applies each `bearing/migrations/*.sql` not yet applied, in name order, recording its file
    name in `schema_migrations(name PRIMARY KEY)`; it reads them with `importlib.resources`,
    and `pyproject.toml` lists `migrations/*.sql` as package data.
  - `save(conn, commits, records, result)` replaces both tables' rows in one transaction, so a
    second ingest stores each commit and PR once. Nothing records the time of the run.
- `bearing ingest <repo> --prs <file> [--data DIR]` (Track D): `--prs` is required today,
  `--data` defaults to `.bearing`; it prints `format_report`'s lines, each ending in `\n`, and
  exits 0. A git error (a `<repo>` that is not a repository) or a file error (a missing
  `--prs` file) prints `bearing: <message>` to stderr, nothing to stdout, and exits 1.
- Tests: `tests/test_history.py`, `tests/test_mapping.py`, `tests/test_store.py`,
  `tests/test_ingest_cli.py`, the new contract test `tests/contract/test_ingest.py` and its
  golden file `tests/fixtures/expected/ingest.txt`. Every test class subclasses
  `unittest.TestCase`; a test builds the fixture with `make_repo.py` as a subprocess (once per
  class is enough), imports the module under test **inside the test method**, and runs
  `python -m bearing` with `cwd=` the repository root, as `tests/test_cli.py` does (see Notes).

### What the fixture gives

From `make_repo.py` at the pinned HEAD `8c1b9f1` (counted from a build, Day 1's table): 12
commits on the line; parent counts, oldest first, `0 2 2 2 2 1 2 1 2 2 2 2`; the squash commit
`448fc4d` is matched by #6's `mergeCommit`; `8c1b9f1` (#11) has no record; #7's `mergeCommit`
`e21c62d` is the second parent of `86761f2`, off the line. Each record's title is its head
branch. So `format_report` gives, on the fixture's own `prs.json`:

```
merges 10  matched 9  unmatched merges 1  unmatched PRs 1  direct 2
unmatched merge 8c1b9f1 Merge pull request #11 from acme/tooling/ci
unmatched PR #7 e21c62d docs/notes
```

## Out of scope
- Areas, the changelog, `--since`/`--until`, "What I built" paragraphs — Day 3.
- Reading PRs live from `gh` when `--prs` is absent; a ref other than `main` (the kit's local
  clone may be past the copied SHA `44d7a55`); the kit's 91-merge line, and whether its `gh`
  list holds a record off the line — Day 4.
- Diffs: plan.md's "every diff is `merge^1..merge`" — Phase 2 (Day 5), the first day that
  diffs a merge; Phase 3's churn reads the same rule.
- A Windows job in CI (Day 1, Out of scope).

## Tracks

| Track | Owner | Work |
|---|---|---|
| 0 | main session | the two empty subpackages, so that A's and C's tests can be seen red on CI's base. No criterion |
| A | implementer | C02.1–C02.2: `bearing/ingest/history.py`, the first-parent line and the subject parser |
| B | implementer | C02.3–C02.5, C02.10: `bearing/ingest/mapping.py`, the two passes, the counts, the report, UTF-8 |
| C | implementer | C02.6: the migration, `bearing/store/db.py`, package data |
| D | implementer | C02.7–C02.8, C02.11: `bearing ingest`, the golden file and its contract test, the errors |

Each track depends on the one before it. C02.9 is `hold` and owned by this spec's PR, which ran
its check first.

## Acceptance criteria
Tick each box in the closing PR once its evidence is in it; under a box left unticked, write
`Not proven: <why>` (`specs/README.md`, "Evidence at the close").
- [x] C02.1 **new** — on the fixture, `read_first_parent(<dir>/repo)` returns 12 commits whose
      full SHAs, in order, are the fixture's `git log --first-parent --reverse --format=%H main`,
      whose parent counts are `0 2 2 2 2 1 2 1 2 2 2 2`, whose first `committed_at` is
      "2026-01-05T12:00:00+00:00" and whose last subject is
      "Merge pull request #11 from acme/tooling/ci". Red today (after Track 0): the test fails
      with "ModuleNotFoundError: No module named 'bearing.ingest.history'".
      Test: `tests/test_history.py::FirstParentTest::test_fixture_line`
      Evidence: `FirstParentTest.test_fixture_line` (#13), seen red first on `44c2ec0`'s code;
      `python -m pytest -q` (#13).
      broken: read_first_parent without --first-parent → 1 failed in 5.12s (#13)
- [x] C02.2 **new** — `parse_merge_subject` gives `(7, "acme", "docs/notes")` for
      "Merge pull request #7 from acme/docs/notes", `(12, "other-owner", "patch-1")` for the
      fork subject "Merge pull request #12 from other-owner/patch-1" (a string: the fixture has
      no fork PR, plan.md's 2026-11-04 Course correction), `(10, "acme", "release")` for #10's,
      and `None` for "Grow the core module (#6)", "Fix README typo" and
      "Merge branch 'main' into x"; the results compare equal to plain tuples. Red today: as
      C02.1. Test: `tests/test_history.py::MergeSubjectTest::test_subjects`
      Evidence: `MergeSubjectTest.test_subjects` (#13), seen red first on `44c2ec0`'s code;
      `python -m pytest -q` (#13).
      broken: parse_merge_subject owner allowed to hold / → 1 failed in 0.08s (#13)
- [x] C02.3 **new** — on the fixture and its `prs.json`, `format_report(map_history(...))` is
      exactly the three lines under "What the fixture gives". Red today (after Track A): "No
      module named 'bearing.ingest.mapping'".
      Test: `tests/test_mapping.py::MappingTest::test_fixture_report`
      Evidence: `MappingTest.test_fixture_report` (#14), seen red first on `058e841`'s code;
      `python -m pytest -q` (#14).
      broken: one space between the summary's first fields → 1 failed in 8.00s (#14)
- [x] C02.4 **new** — the subject fallback, on the fixture with records written in the test: a
      copy of `prs.json` with #1's `mergeCommit` key removed and #6's set to `null` gives exactly
      "merges 9  matched 8  unmatched merges 1  unmatched PRs 2  direct 3",
      "unmatched merge 8c1b9f1 Merge pull request #11 from acme/tooling/ci",
      "unmatched PR #6 - day-02/track-b-grow", "unmatched PR #7 e21c62d docs/notes": #1 is
      matched by its subject, the squash commit becomes direct. Red today: as C02.3.
      Test: `tests/test_mapping.py::FallbackTest::test_absent_and_null`
      Evidence: `FallbackTest.test_absent_and_null` (#14), seen red first on `058e841`'s code;
      `python -m pytest -q` (#14).
      broken: the subject fallback never matches → 1 failed in 4.89s (close; D02.14)
- [x] C02.5 **new** — never guessed: a copy of `prs.json` with only #1's `mergeCommit.oid` set to
      forty `0`s (every other record as built) gives exactly
      "merges 10  matched 8  unmatched merges 2  unmatched PRs 2  direct 2",
      "unmatched merge 62c4b2f Merge pull request #1 from acme/day-01/track-a-core",
      "unmatched merge 8c1b9f1 Merge pull request #11 from acme/tooling/ci",
      "unmatched PR #1 0000000 day-01/track-a-core", "unmatched PR #7 e21c62d docs/notes".
      Red today: as C02.3. Test: `tests/test_mapping.py::FallbackTest::test_oid_off_the_line`
      Evidence: `FallbackTest.test_oid_off_the_line` (#14), seen red first on `058e841`'s code;
      `python -m pytest -q` (#14).
      broken: pass 2 matches a record whatever its oid → 1 failed in 6.32s (#14)
- [x] C02.6 **new** — `open_store` and `save` run twice on the fixture into one data directory:
      after each, `commits` holds 12 rows (9 with a `pr_number`, 2 of `kind` 'direct'), `prs`
      holds 10, and `schema_migrations` holds exactly `001_history.sql`. Red today (after
      Track 0): "No module named 'bearing.store.db'".
      Test: `tests/test_store.py::StoreTest::test_stored_once`
      Evidence: `StoreTest.test_stored_once` (#15), seen red first on `f5a5d18`'s code;
      `python -m pytest -q` (#15).
      broken: save keeps the old commits rows → 1 failed, 1 passed, 1 subtests passed in 7.44s (#15)
- [x] C02.7 **new** — `python -m bearing ingest <dir>/repo --prs <dir>/prs.json --data <tmp>`,
      run from the repository root, exits 0 and prints, with `\r\n` read as `\n`, the bytes of
      `tests/fixtures/expected/ingest.txt`, which are the three lines under "What the fixture
      gives", each ending in `\n`. Red today: argparse's "unrecognized arguments", exit 2.
      Test: `tests/test_ingest_cli.py::IngestCliTest::test_report` and
      `tests/contract/test_ingest.py::IngestContractTest::test_golden`
      Evidence: `IngestCliTest.test_report` and `IngestContractTest.test_golden` (#16), seen red
      first on `87002ea`'s code; `python -m pytest -q` (#16).
      broken: cli.py writes each report line without its newline → 1 failed in 7.05s (#16)
- [x] C02.8 **new** — the target is read-only: after the C02.7 command, the fixture's
      `git status --porcelain --ignored` prints nothing, `git for-each-ref` and `HEAD` are what
      they were before, and `<tmp>/bearing.db` exists. Red today: as C02.7.
      Test: `tests/test_ingest_cli.py::IngestCliTest::test_target_untouched`
      Evidence: `IngestCliTest.test_target_untouched` (#16), seen red first on `87002ea`'s code;
      `python -m pytest -q` (#16).
      broken: cli.py opens the store inside the target repository → 1 failed in 8.10s (#16)
- [x] C02.9 **hold** — the frozen fixture stays as Day 1 pinned it:
      `git -c core.safecrlf=false diff --exit-code 31eaca5 -- tests/contract/test_fixture.py tests/fixtures/make_repo.py`
      prints nothing and exits 0.
      Evidence: the command above, exit 0 in #11 and on `1ba07d6` at the close.
      broken: the pinned HEAD SHA edited in tests/contract/test_fixture.py → class FixtureTest(unittest.TestCase): (#11)
- [x] C02.10 **new** — `load_prs` reads UTF-8 whatever the code page: a file the test writes as
      bytes, `[{"number": 1, "title": "Café → bar", ...}]` encoded UTF-8 (non-ASCII
      bytes on disk, not `\u` escapes), loads with the title "Café → bar". Red today: as C02.3.
      Test: `tests/test_mapping.py::LoadPrsTest::test_utf8`
      Evidence: `LoadPrsTest.test_utf8` (#14), seen red first on `058e841`'s code;
      `python -m pytest -q` (#14).
      broken: load_prs reads with the locale's code page → 1 failed in 0.10s (#14)
- [x] C02.11 **new** — errors: `bearing ingest <dir>/repo --prs <missing file>` and
      `bearing ingest <an empty directory> --prs <dir>/prs.json`, run from the repository root,
      each exit 1 with stdout empty and stderr starting "bearing: ". Red today: argparse's
      "unrecognized arguments", exit 2.
      Test: `tests/test_ingest_cli.py::IngestCliTest::test_errors`
      Evidence: `IngestCliTest.test_errors` (#16), seen red first on `87002ea`'s code;
      `python -m pytest -q` (#16).
      broken: cli.py prints errors to stdout → 2 failed, 1 passed in 7.38s (#16)

## Verify
```bash
python -m pytest -q
python tests/fixtures/make_repo.py .bearing/day02-check
python -m bearing ingest .bearing/day02-check/repo --prs .bearing/day02-check/prs.json --data .bearing/day02-data
# merges 10  matched 9  unmatched merges 1  unmatched PRs 1  direct 2
git -c core.safecrlf=false diff --exit-code 31eaca5 -- tests/contract/test_fixture.py tests/fixtures/make_repo.py
```

## Notes
- Red by assertion, not by collection: with `TRACK_RED_RUNNER=pytest`, `scripts/track-red.py`
  counts a collection error as "an error, not an assertion" and does not accept it as red. An
  import at the top of a test file fails collection on `main`; inside the test method it fails
  the test. So each test imports the module it tests in its body.
- Red on CI's base (D01.7's trap again): the track-red job installs the head editable, and
  setuptools' editable finder serves a direct child of `bearing` that the base lacks
  (`bearing.ingest`, `bearing.store`) from the head, so a test of a new subpackage passes on
  the base. A grandchild (`bearing.ingest.history`) is looked up under its parent's path and is
  not served. Track 0 lands the two subpackages empty, so every later test imports a
  grandchild. The same finder loads the head's `bearing` when `python -m bearing` runs from
  another directory, so CLI tests run it with `cwd=` the repository root.
- Test names: as Day 1's Notes, `Test:` holds pytest node IDs and each `Evidence:` line names
  `Class.test_x` and `python -m pytest -q`. The class names are new under `tests/`
  (`tests/test_make_repo.py` already has `HistoryTest`), so `scripts/evidence.py` finds each
  once.
- `tests/contract/test_ingest.py` and the golden file are new files, not edits to a contract
  test. The ingest line carries no version string: plan.md's "Output contracts" gives it a
  shape with none, and the golden file is its contract. Its unmatched-item lines are fixed
  here, as "Output contracts" leaves to the day that first writes the golden file.
- `committed_at` is the committer time from `%ct`; `mergedAt` is stored as the record gives it.
  Neither is the time of the run. git 2.54 prints `%cI` for a `+0000` date as `Z`, which is why
  the code formats `%ct` itself.
- `8c1b9f1`, `e21c62d`, `62c4b2f` and `448fc4d` follow from the pinned HEAD; a build that gives
  others fails `tests/contract/test_fixture.py` first.
- Verify's `make_repo.py .bearing/day02-check` refuses a directory that is not empty: delete it
  before a second local run.
- The kit's line follows from these rules: 91 two-parent merges all matched by `mergeCommit`,
  and 11 single-parent commits, root included, give
  `merges 91  matched 91  unmatched merges 0  unmatched PRs 0  direct 11` (spec-auditor), if
  the kit's `gh` list holds no record off the line, which Day 4 checks.
- **Defect** D02.1 — found: auditor · cause: spec · made: Day 02 · C02.1, C02.2 and C02.6 could
  not be seen red on CI's base: the editable finder serves a new direct subpackage of `bearing`
  from the head (D01.7's trap); a Track 0 now lands the subpackages empty, and CLI tests run
  from the repository root.
- **Defect** D02.2 — found: auditor · cause: spec · made: Day 02 · C02.5's "the same copy" read as
  C02.4's copy, which gives other counts; it now names a copy with only #1's `oid` changed.
- **Defect** D02.3 — found: auditor · cause: spec · made: Day 02 · C02.1 expected `%cI` as
  "+00:00"; git 2.54 prints "Z"; `committed_at` now comes from `%ct`, formatted in the code.
- **Defect** D02.4 — found: auditor · cause: spec · made: Day 02 · In scope promised UTF-8
  reading and the git and file errors with no criterion checking them, and the fixture is
  pure ASCII; C02.10 and C02.11 added.
- **Defect** D02.5 — found: auditor · cause: spec · made: Day 02 · the mapping left open a record
  or commit matched twice, `mergeCommit: {}`, and what `MergeSubject` compares equal to; In
  scope now says at most once, first in first-parent order, `{}` as absent, and a `NamedTuple`.
- **Defect** D02.6 — found: auditor · cause: spec · made: Day 02 · plan.md's "every diff is
  `merge^1..merge`" was owned by no Out-of-scope line; it now goes to Day 5.
- **Defect** D02.7 — found: Track B · cause: spec · made: Day 02 · two records naming the same
  `oid`: In scope's "first in first-parent order" does not choose between two records on one
  commit. The code takes the first in `gh`'s list order; the fixture has no such case and no
  test pins it. Seen while writing Track B, before #14 merged, and stated in its PR. H02.1.
- **Defect** D02.8 — found: review · cause: implementation · made: Day 02 · the implementer's
  Track A draft carried a comment claiming the three-way split keeps a NUL inside a subject; a
  git subject cannot hold one. Corrected before #13.
- **Defect** D02.9 — found: review · cause: process · made: Day 02 · the implementer's Track D
  report gave the golden file as "0x253 bytes", `od`'s octal offset; `wc -c` counts 171 (#16).
- **Defect** D02.10 — found: Track D · cause: spec · made: Day 02 · C02.10 covers reading UTF-8
  only. The report is written in stdout's encoding, so an unmatched PR with a non-ASCII title,
  stdout piped on Windows (cp1252), ends in a `UnicodeEncodeError` traceback and exit 1 instead of
  the report. Listed in #16's "Known gaps" before it merged; reproduced at the close with #7's
  title set to "Café → bar". H02.2.
- **Defect** D02.11 — found: Track D · cause: spec · made: Day 02 · In scope's errors leave out
  the data directory: `--data` naming a file ends in a `FileExistsError` traceback, not
  "bearing: ...". Listed in #16's "Known gaps" before it merged; reproduced at the close. H02.3.
- **Defect** D02.12 — found: close · cause: process · made: Day 02 · same-as: D01.21 · #13's
  second `manifest:` line lost a level of backslashes in the PR body (`\s` for `\\s`) and no
  longer parsed as JSON. The close restored it from `history.py`'s regex. How the body lost them
  is not known; at the close, a Python script passed through a Bash-tool heredoc lost backslashes
  the same way. H02.4.
- **Defect** D02.13 — found: close · cause: process · made: Day 02 · same-as: D01.21 · #16's
  first `manifest:` line lost a level too (`\n` for `\\n`): it still parsed, but its `find`
  became a real newline and matched nothing in `cli.py`. The close restored it and replayed all
  11 entries in an LF worktree; each failed its check, as its `broken:` line says. H02.4.
- **Defect** D02.14 — found: close · cause: process · made: Day 02 · no track broke C02.4 (#14
  broke C02.3, C02.5 and C02.10); the close ran its first break, the subject fallback never
  matching.
- **Defect** D02.15 — found: self · cause: process · made: Day 02 · to replay the breaks on LF
  files, the close ran `git -C <scratch worktree> config core.autocrlf false`, which writes the
  repository's shared config. The main tree's next `git add` staged four files as CRLF, every
  line changed. Seen in the staged `--numstat` before any commit; the setting was removed.
- **Hand-off** H02.1 → Day 4: two `gh` records with the same `oid` (D02.7). Check the kit's list
  for one, and pin which record wins in a test.
- **Hand-off** H02.2 → Day 3: write the CLI's output as UTF-8 whatever the console's code page
  (D02.10); `bearing changelog` prints every title. A test with a non-ASCII title, stdout piped.
- **Hand-off** H02.3 → Day 3: an unusable `--data` directory prints "bearing: ..." and exits 1
  (D02.11); `bearing changelog` opens the same store.
- **Hand-off** H02.4 → the maintainer: D01.21 recurred twice (D02.12, D02.13). A check that each
  `manifest:` line in a track PR's body parses and its `find` occurs once in the PR's code would
  catch it at the PR, not the close; fix in the kit.
- Verify's ingest line is judged by its exit code only: the counts line under it is a comment on
  a line of its own, which `scripts/evidence.py` runs as nothing. C02.7's tests check the output.
