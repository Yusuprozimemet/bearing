# Day 08 — `bearing.toml`, churn and co-change coupling in `bearing direction`

**Phase:** 3 · **Depends on:** Day 7 · **Expected PRs:** 4 (this spec with its plan change, track A, track B, the close)

## Goal
`bearing direction <repo> --data DIR --config FILE` reads its areas and coupling threshold from
a `bearing.toml` outside the target repository, and prints a `## Churn` table (lines added and
deleted per path area per ISO week) and a `## Coupling` table (file pairs changed together in at
least `min_prs` PRs, a pair across two areas marked as a hidden dependency); on the fixture,
with `tests/fixtures/bearing.toml`, it prints exactly the 23 lines of "What the fixture gives".

## In scope
- The plan-auditor's Phase 3 findings on `43d5012`, settled in this spec's plan change (plan.md,
  "Course correction before Phase 3", items 1–5): one `[areas]` table of path areas; the
  fixture's #5 is flagged on Day 9; both forms of "Contract impact"; the file's location; the
  days' split; no new migration.
- H07.1, decided: `bearing.toml` is read from `--config FILE`, default `bearing.toml` in the
  working directory, never from the target repository. The fixture's is
  `tests/fixtures/bearing.toml`, a new file beside the frozen `make_repo.py`:

  ```toml
  [areas]
  app = ["app/"]
  lib = ["src/"]
  tooling = ["scripts/", "ci.txt"]
  docs = ["docs/", "README.md"]

  [coupling]
  min_prs = 3
  ```
- H01.2, decided: the coupling threshold is `[coupling] min_prs`, 3 when the table or the key is
  absent; at 3 the fixture gives exactly the pair `app/core.py`, `src/lib/util.py` (#1, #3, #9).
- `bearing/direction/config.py` (Track A): `load_config(path)` returns `(areas, min_prs)`:
  the areas in file order, each a `(name, tuple of path prefixes)` pair, and an `int`. `area_of(path, areas)` is the name of
  the first area one of whose prefixes `path` starts with (`str.startswith`), else `other`. It
  raises `ConfigError` with these messages, which the CLI prints after `bearing: `:
  - no file: "no config at <path>: pass --config FILE";
  - not TOML: "cannot read config <path>: " and `tomllib`'s message;
  - `areas` missing, not a table (`areas = "x"`), empty, or a value that is not a non-empty
    list of strings: "config <path>: [areas] must map names to lists of path prefixes";
  - `coupling` present but not a table (`coupling = 3`), or `min_prs` not an integer of at
    least 1 (`true` is not one): "config <path>: [coupling] min_prs must be a positive
    integer".
- `bearing/direction/changes.py` (Track A): `parse_numstat(raw)` reads the bytes of
  `git diff --numstat -z -M` into `(path, added, deleted)` triples sorted by path; a rename is
  its new path; a binary file (`-` counts) is 0 and 0; paths are decoded as `renamed_paths`
  decodes them (UTF-8, `surrogateescape`). `changed_files(repo, sha)` runs
  `git diff --no-ext-diff --numstat -z -M <sha>^1 <sha>` read-only and returns
  `parse_numstat`'s list; a git error raises `SnapshotError` with git's stderr.
- `bearing/direction/churn.py` (Track A): `churn(commits, areas)` takes `(committed_at,
  files)` pairs, `files` as `changed_files` returns them, and returns `(week, area, added,
  deleted)` rows, one for each week and area with at least one changed file (0 and 0 included,
  as a pure rename gives), sorted by week then area. The week is
  `f"{year}-W{week:02d}"` from `date.isocalendar()` of the UTC date of `committed_at`.
- `bearing/direction/coupling.py` (Track B): `coupling(prs, areas, min_prs)` takes `(number,
  paths)` pairs and returns `(a, b, numbers, area_a, area_b)` for each pair of paths `a < b`
  (Python's string order) changed together in at least `min_prs` distinct PR numbers, sorted by
  `(a, b)`, `numbers` ascending.
- `bearing direction <repo> [--data DIR] [--config FILE]` (Track B), with `--data` as in the
  other subcommands. It reads the config first, then the store, which it never creates (as
  `timeline`); a missing store prints "bearing: no store at <db>: run bearing ingest first".
  Churn reads every commit of the store with `parent_count > 0` (merges, the squash, direct
  commits; not the root). Coupling reads the commits of kind `merge` whose PR number is known,
  `pr_number`, else `subject_number`. The output, all of it computed before any is printed:

  ```
  ## Churn
  <blank>
  | Week | Area | Added | Deleted |
  |---|---|---|---|
  | <week> | <area> | <added> | <deleted> |      one per churn row
  <blank>
  ## Coupling
  <blank>
  | File | File | PRs | Hidden dependency |
  |---|---|---|---|
  | <a> | <b> | #<n>, #<n> | <area_a>, <area_b> |   or "no" when the areas are equal
  ```

  With no pair, the Coupling section ends at its separator row. Each line ends `\n`.

### What the fixture gives

A prototype of the rules above (`git diff --numstat -z -M` per first-parent commit), run on
2026-11-04 on the fixture at `8c1b9f1`, prints these 23 lines with the fixture's toml:

```
## Churn

| Week | Area | Added | Deleted |
|---|---|---|---|
| 2026-W02 | app | 13 | 0 |
| 2026-W02 | lib | 4 | 0 |
| 2026-W02 | tooling | 7 | 0 |
| 2026-W03 | app | 19 | 0 |
| 2026-W03 | docs | 5 | 0 |
| 2026-W03 | lib | 4 | 0 |
| 2026-W04 | app | 247 | 3 |
| 2026-W04 | tooling | 2 | 2 |
| 2026-W05 | app | 4 | 2 |
| 2026-W05 | docs | 3 | 0 |
| 2026-W05 | lib | 4 | 0 |
| 2026-W05 | other | 5 | 0 |
| 2026-W05 | tooling | 1 | 0 |

## Coupling

| File | File | PRs | Hidden dependency |
|---|---|---|---|
| app/core.py | src/lib/util.py | #1, #3, #9 | app, lib |
```

- 2026-W03's `docs` holds the direct commit "Fix README typo" (2 lines of `README.md`) beside
  #4's 3: churn counts direct commits. 2026-W04's `tooling` holds #5's and #8's one-line
  changes to `scripts/run.py` and #8's pure rename `scripts/helpers.py` → `scripts/tools.py`
  (0 and 0). 2026-W05's `other` is #9's `tests/contract/test_api.py`, in no area.
- With `min_prs = 2` the Coupling table has three rows: "| app/b.py | app/core.py | #3, #9 |
  no |", "| app/b.py | src/lib/util.py | #3, #9 | app, lib |", and the row above. With
  `min_prs = 4` it has none.

## Out of scope
- Said vs done, the `## Said vs done` section, the direction golden file and its contract test —
  Day 9 (H08.1).
- The kit's `bearing.toml` and its run at `c12cfe5` — Day 10 (H08.2).
- Following a rename in coupling: a file's pairs before and after a rename are separate pairs.
  The fixture's one rename (#8) is in no pair at 2 or 3. A known limit, recorded in the Notes.
- A `003_*.sql` migration: churn and coupling read git at run time (plan.md, Course correction
  before Phase 3, item 5).
- The changelog's areas: they stay branch areas; its golden file is frozen.

## Tracks

| Track | Owner | Work |
|---|---|---|
| A | implementer | C08.1–C08.3: `bearing/direction/__init__.py`, `config.py`, `changes.py`, `churn.py`; `tests/test_config.py`, `tests/test_changes.py`, `tests/test_churn.py` |
| B | implementer | C08.4–C08.7: `bearing/direction/coupling.py`, `bearing/direction/report.py`, the `direction` subcommand in `bearing/cli.py`, `tests/fixtures/bearing.toml`; `tests/test_coupling.py`, `tests/test_direction_cli.py` |

Two tracks, so each PR stays under 400 changed lines; B uses A's functions and lands after it.
No Track 0: the tests that hold through the day (Days 1 to 7, the contract tests among them)
exist. C08.8 is `hold` and owned by this spec's PR, which ran its check and break first.

## Acceptance criteria
Tick each box in the closing PR once its evidence is in it; under a box left unticked, write
`Not proven: <why>` (`specs/README.md`, "Evidence at the close").
- [ ] C08.1 **new** — `load_config` on a file written in the test with `[areas]` `docs =
      ["docs/", "README.md"]`, `app = ["app/"]`, `deep = ["app/sub/"]` and `[coupling] min_prs
      = 2` returns the areas `[("docs", ("docs/", "README.md")), ("app", ("app/",)), ("deep",
      ("app/sub/",))]` in that order and `min_prs` 2; the same file without `[coupling]` gives
      3. `area_of` gives "docs" for "README.md", "app" for "app/sub/m.py" (the first area in
      file order wins over the longer prefix), and "other" for "tests/x.py". And `ConfigError`
      is raised with exactly the In scope messages for: a path that does not exist; a file
      holding `[areas` (not TOML; the message starts "cannot read config"); no `[areas]`;
      `app = "app/"`; `app = []`; `min_prs = 0`; `min_prs = true`. Red today: the import of
      `bearing.direction.config` fails ("No module named 'bearing.direction'").
      Test: `tests/test_config.py::ConfigTest::test_areas_and_threshold` and
      `tests/test_config.py::ConfigTest::test_errors`
- [ ] C08.2 **new** — `parse_numstat(b"3\t1\tapp/a.py\x00-\t-\tlogo.png\x000\t0\t\x00scripts/helpers.py\x00scripts/tools.py\x00")`
      returns `[("app/a.py", 3, 1), ("logo.png", 0, 0), ("scripts/tools.py", 0, 0)]`; and on
      the fixture, `changed_files(<dir>/repo, <#8's merge, fde93a4>)` returns
      `[("app/extra.py", 5, 0), ("app/legacy.py", 0, 3), ("scripts/run.py", 1, 1),
      ("scripts/tools.py", 0, 0)]`, and `changed_files` on a SHA not in the repository raises
      `SnapshotError`. Red today: the import of `bearing.direction.changes` fails.
      Test: `tests/test_changes.py::ChangesTest::test_parse_numstat` and
      `tests/test_changes.py::ChangesTest::test_fixture_merge`
- [ ] C08.3 **new** — `churn` on `[("2025-12-29T10:00:00+00:00", [("app/a.py", 2, 1),
      ("docs/x.md", 1, 0)]), ("2026-01-02T23:00:00+00:00", [("app/b.py", 3, 0)]),
      ("2027-01-01T00:00:00+00:00", [("z.txt", 0, 4)]), ("2026-01-05T08:00:00+00:00",
      [("docs/y.md", 0, 0)])]` with the areas `app = ["app/"]`, `docs = ["docs/"]` returns
      exactly `[("2026-W01", "app", 5, 1), ("2026-W01", "docs", 1, 0), ("2026-W02", "docs", 0,
      0), ("2026-W53", "other", 0, 4)]`. That is: 2025-12-29 and 2027-01-01 fall in ISO year
      2026; two commits in a week add up; a file in no area is "other"; a 0-and-0 file alone in
      its week still makes its row; rows come sorted, whatever the input's order. Red today: the
      import of `bearing.direction.churn` fails.
      Test: `tests/test_churn.py::ChurnTest::test_weeks_and_areas`
- [ ] C08.4 **new** — `coupling([(1, ["x/a", "y/b", "x/c"]), (3, ["x/a", "y/b"]), (2, ["x/a",
      "x/c"]), (4, ["y/b", "x/a"]), (4, ["x/a", "y/b"])], [("x", ("x/",)), ("y", ("y/",))], 2)`
      returns exactly `[("x/a", "x/c", [1, 2], "x", "x"), ("x/a", "y/b", [1, 3, 4], "x",
      "y")]`: PR 4, listed twice, counts once, and its unsorted paths make the same pair; with
      `min_prs` 4 it returns `[]`. Red today: the import of `bearing.direction.coupling` fails.
      Test: `tests/test_coupling.py::CouplingTest::test_pairs`
- [ ] C08.5 **new** — on the fixture, after `python -m bearing ingest <dir>/repo --prs
      <dir>/prs.json --data <tmp>`, `python -m bearing direction <dir>/repo --data <tmp>
      --config tests/fixtures/bearing.toml` exits 0, stderr empty, and its stdout's bytes are
      exactly the 23 lines of "What the fixture gives", each ending `\n`. Red today: argparse
      rejects the subcommand ("invalid choice: 'direction'"), exit 2.
      Test: `tests/test_direction_cli.py::DirectionCliTest::test_fixture_report`
- [ ] C08.6 **new** — the same run with a copy of the fixture's toml at `min_prs = 2`, written
      in the test, prints the three Coupling rows of "What the fixture gives" in that order, the
      Churn section unchanged; at `min_prs = 4` no row follows the Coupling table's separator
      line "|---|---|---|---|": the output ends there, or the next line is blank. Red today: as
      C08.5.
      Test: `tests/test_direction_cli.py::DirectionCliTest::test_threshold`
- [ ] C08.7 **new** — `bearing direction` exits 1 with nothing on stdout and stderr exactly:
      "bearing: no config at <path>: pass --config FILE" for a `--config` that does not exist;
      a line starting "bearing: cannot read config <path>: " for a file holding `[areas`;
      "bearing: no store at <tmp>/bearing.db: run bearing ingest first" with the fixture's toml
      and an empty `--data` directory, which it leaves without a `bearing.db`; and, with no
      `--config` and no `--data`, run in an empty working directory, "bearing: no config at
      bearing.toml: pass --config FILE", the config read before the store. Red today: as C08.5.
      Test: `tests/test_direction_cli.py::DirectionCliTest::test_errors`
- [ ] C08.8 **hold** — the frozen files stay as Day 7 left them, added files allowed outside
      the migrations: `git -c core.safecrlf=false diff --diff-filter=DMRT --exit-code 43d5012 --
      tests/contract/ tests/fixtures/make_repo.py tests/fixtures/expected/` and
      `git -c core.safecrlf=false diff --exit-code 43d5012 -- bearing/migrations/` print
      nothing and exit 0. The second has no filter: the day adds no migration (plan.md, Course
      correction before Phase 3, item 5). It sees an added migration only once it is committed
      (in a PR, and at replay), not an untracked file, so its break edits an applied one.

## Verify
```bash
python -m pytest -q
python tests/fixtures/make_repo.py .bearing/day08-check
python -m bearing ingest .bearing/day08-check/repo --prs .bearing/day08-check/prs.json --data .bearing/day08-check/data
python -m bearing direction .bearing/day08-check/repo --data .bearing/day08-check/data --config tests/fixtures/bearing.toml | grep -c -e "| 2026-W04 | app | 247 | 3 |" -e "| app/core.py | src/lib/util.py | #1, #3, #9 | app, lib |"  # 2
git -c core.safecrlf=false diff --diff-filter=DMRT --exit-code 43d5012 -- tests/contract/ tests/fixtures/make_repo.py tests/fixtures/expected/
git -c core.safecrlf=false diff --exit-code 43d5012 -- bearing/migrations/
```

## Notes
- The prototype behind "What the fixture gives" read git directly, not the store; it found the
  PR number in the subject. Track B reads `pr_number`, else `subject_number`, which give the
  same numbers on the fixture: #6's squash and #11, which has no record, both carry one.
- Known limit: coupling does not follow renames (Out of scope). On the kit, a pair split by a
  rename shows as two pairs, each with fewer PRs; Day 10's run is where that would show.
- Day 9's `## Said vs done` section changes C08.5's output, so its criterion names
  `Replaces: C08.5`. C08.6 is worded to survive it: a blank line may follow the separator.
- Tests: `pytest -q` prints "56 passed, 51 subtests passed" on `43d5012`. The criteria name 9
  tests (Track A 5, Track B 4), so the day ends at "65 passed", subtests besides.
- H05.1's remainder: the Day 10 stop named coupling as "the next cut". Day 8 builds it, so this
  PR's plan change drops it from the stop and leaves what Phase 4 cuts to the stop.
- Churn and coupling diff `<sha>^1 <sha>`, the rule Day 2's Notes gave Phase 3 (every diff is
  `merge^1..merge`).
- **Defect** D08.6 — found: auditor · cause: spec · made: Day 08 · C08.6 required the output to
  end at the Coupling separator, which Day 9's section would break with no `Replaces:` for it;
  reworded in this PR.
- **Defect** D08.7 — found: auditor · cause: spec · made: Day 08 · the spec gave no test count
  for the day's end; the Notes now say "65 passed".
- **Defect** D08.8 — found: auditor · cause: spec · made: Day 07 · plan.md's Day 10 stop still
  named coupling as the next cut; Day 7's Course correction dropped only cycle detection from
  it (H05.1). Fixed in this PR's plan change.
- **Defect** D08.9 — found: auditor · cause: spec · made: none · plan.md's "Target structure"
  lists `bearing.toml.example`, which no day owned; given to Day 9 in H08.1.
- **Defect** D08.1 — found: auditor · cause: spec · made: none · plan.md used "area" for a PR's
  branch prefix and for `bearing.toml`'s path areas, and the fixture's coupling pair changes
  only in `day-NN` PRs, so no branch area could put it apart; settled in this PR's Course
  correction, item 1.
- **Defect** D08.2 — found: auditor · cause: spec · made: none · plan.md's said-vs-done rule
  flags the fixture's #5, which its hard-parts row and H01.4 call not a lie; settled in this
  PR's Course correction, item 2 (#5 is flagged, and the stop judges it).
- **Defect** D08.3 — found: auditor · cause: spec · made: none · plan.md's rule quoted the
  one-line "Contract impact: none", which no kit PR at `c12cfe5` writes (94 of 94 use the
  heading); settled in this PR's Course correction, item 3.
- **Defect** D08.4 — found: spec-change PR · cause: spec · made: Day 08 · the first draft said
  the fixture's report is 22 lines, a count by hand; it is 23 (the Coupling section's blank
  line was missed). Fixed in this PR before the audit.
- **Defect** D08.5 — found: spec-change PR · cause: spec · made: Day 08 · the first draft of
  C08.3 put its 0-and-0 file in a week and area that already had a row, so the case "a 0-and-0
  file still makes its row" could not fail; it now has a week of its own. Fixed in this PR
  before the audit.
- **Hand-off** H08.1 → Day 9: said vs done as the Course correction before Phase 3 has it
  (items 1–3): the outside-area rule, checked only for a branch area that names a
  `bearing.toml` area, which flags the fixture's #5 with `scripts/run.py`; the contract-impact
  rule in both forms, which flags #9 with `tests/contract/test_api.py`, the heading form tested
  on a body written in the test; the rules' settings in `bearing.toml`; the `## Said vs done`
  section (`Replaces: C08.5`), the direction golden file and its contract test; and
  `bearing.toml.example` at the repository root (plan.md, "Target structure"), once the rule
  settings exist.
- **Hand-off** H08.2 → Day 10: the kit's `bearing.toml`, in this repository, and the run of
  `bearing direction` on the kit at `c12cfe55018aebe82de83485460f1edd22e4c96b` (#95) for
  Phase 3's "Done when".
