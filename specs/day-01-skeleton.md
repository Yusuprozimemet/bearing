# Day 01 — Skeleton: a CLI that runs and a fixture history to test against

**Phase:** 0 · **Depends on:** none · **Expected PRs:** 5 (this spec, tracks A–C, the close)

## Goal
`bearing --version` runs, and `python tests/fixtures/make_repo.py <dir>` builds the same fixture
repository and `prs.json`, with the same HEAD SHA, on Linux CI and on Windows, holding every
case plan.md's Phase 0 lists, pinned by `tests/contract/test_fixture.py`.

## In scope
- `bearing/__init__.py` defines `__version__ = "0.1.0"`; `bearing/cli.py` has
  `main(argv=None)` and imports the version from `bearing`; `bearing/__main__.py` calls it;
  `[project.scripts] bearing = "bearing.cli:main"` in `pyproject.toml`. `--version` prints
  "bearing 0.1.0" and a newline and exits 0. No subcommands yet.
- `.gitignore`: add `*.egg-info/` and `.bearing/`.
- `.gitattributes`: add `tests/fixtures/** text eol=lf` (plan.md, "hard parts", reproducible
  output).
- `tests/fixtures/make_repo.py <dir>`: creates `<dir>` and its parents when missing, refuses a
  `<dir>` that is not empty, builds the history below in `<dir>/repo` and writes
  `<dir>/prs.json`. It runs git with `-c user.name=Fixture -c user.email=fixture@example.com
  -c core.autocrlf=false -c commit.gpgsign=false -c init.defaultBranch=main
  -c core.attributesFile=<os.devnull>`, with `GIT_CONFIG_NOSYSTEM=1`, `GIT_ATTR_NOSYSTEM=1` and
  `GIT_CONFIG_GLOBAL` set to `os.devnull`, `GIT_AUTHOR_DATE` and `GIT_COMMITTER_DATE` set per
  commit, and an explicit `-m` on every commit and merge. Every file is written in binary mode
  with `\n` endings (one with `\r\n`, below), none executable. Standard library only.
- `prs.json` is `json.dumps(records, sort_keys=True, indent=2)` plus a final newline, records
  sorted by number, each with exactly the keys `baseRefName`, `body`, `headRefName`,
  `mergeCommit` (`{"oid": "<full sha>"}`), `mergedAt` (`"2026-01-07T12:00:00Z"`, the step's
  date), `number`, `title`. It is generated, never committed.
- Tests: `tests/test_cli.py`, `tests/test_repo_files.py`, `tests/test_make_repo.py`, and
  `tests/contract/test_fixture.py` with the HEAD SHA as a constant. Every test class subclasses
  `unittest.TestCase`; a test that builds the fixture runs `make_repo.py` as a subprocess and
  asserts its exit status, so a missing or older builder fails an assertion, not a collection.

### The fixture history

Owner `acme`. Dates are 2026-01-DD at 12:00:00 +0000, author and committer alike. The steps are
the first-parent line of `main`, oldest first. "Merge #N from X" means a `--no-ff` merge with
the subject "Merge pull request #N from acme/X".

| Step | Date | On `main` | Subject | Record in `prs.json` | What the PR changes (Track C) |
|---|---|---|---|---|---|
| 1 | 01-05 | direct commit (the root) | "Initial commit" | none | the starting tree, below |
| 2 | 01-07 | merge | Merge #1 from day-01/track-a-core | #1, base `main`, template body | adds `app/sub/__init__.py`, `app/sub/mod.py` (`from ..pkg import h`, `from ..core import f`); edits `app/core.py` and `src/lib/util.py` |
| 3 | 01-09 | merge | Merge #2 from tooling/scripts | #2, body with "## What was built", no "What I built" | adds `scripts/run.py` (`import helpers`); `scripts/helpers.py` comes to `import config` (flat folder) |
| 4 | 01-12 | merge | Merge #4 from docs/guide | #4, empty body `""` | `docs/guide.md` only (non-Python on its own) |
| 5 | 01-14 | merge | Merge #3 from day-02/track-a-cycle | #3, template body | adds `app/a.py` (`import app.b`) and `app/b.py` (`import app.a`): a cycle; adds `app/crlf.py` written with `\r\n`; edits `app/core.py` and `src/lib/util.py` |
| 6 | 01-16 | direct commit | "Fix README typo" | none | `README.md` |
| 7 | 01-19 | merge | Merge #5 from docs/typo-fix | #5, template body | fixes a typo in a string in `scripts/run.py` |
| 8 | 01-21 | squash commit, one parent | "Grow the core module (#6)" | #6, head `day-02/track-b-grow`, `mergeCommit` this commit | `app/core.py` grows from under 200 to over 200 lines; adds `app/broken.py`, a syntax error |
| 9 | 01-23 | merge | Merge #8 from day-03/track-a-rename | #8, template body | `git mv scripts/helpers.py scripts/tools.py` (content unchanged), `run.py` follows; adds `app/extra.py`; deletes `app/legacy.py` |
| 10 | 01-26 | merge | Merge #9 from day-03/track-b-break-cycle | #9, template body with "Contract impact: None" | removes `import app.a` from `app/b.py`; adds `tests/contract/test_api.py`; edits `app/core.py` and `src/lib/util.py` |
| 11 | 01-28 | merge | Merge #10 from release | #10, head `release` (no `/`), base `main` | branch `release` holds the side merge "Merge pull request #7 from acme/docs/notes" (01-27): record #7, head `docs/notes`, base `release`, `mergeCommit` that side merge; adds `docs/notes.md` |
| 12 | 01-30 | merge | Merge #11 from tooling/ci | none: #11 is not in `prs.json` | `ci.txt` |

The starting tree: `README.md`, `app/__init__.py` (`from . import core`), `app/core.py`
(defines `f`, under 200 lines), `app/legacy.py`, `app/pkg/__init__.py` (defines `h`),
`src/lib/__init__.py`, `src/lib/util.py` (`import app.core`), `scripts/helpers.py`,
`scripts/config.py`. Every Python file has distinct, non-empty content, so git pairs only the
`git mv` as a rename. The template body is a shortened copy of
`.github/pull_request_template.md`: "## What I built", one paragraph, "## Why this approach",
one paragraph, "## Contract impact", "None". Titles are free; the tests do not read them.

**Track B and Track C split the table.** Track B builds the history: the 12 steps, their
subjects, dates, parents, branches and records, the side merge and the squash; each PR's
branch commit adds only `changes/<N>.txt`, the direct commits edit `README.md`, the starting
tree is `README.md` alone, and every record's body is `""`. Track C replaces those contents
with the "What the PR changes" column, the starting tree and the bodies, and pins the SHA. So
C01.7–C01.9 fail on Track B's builder.

Counts this gives: 12 commits on the first-parent line: 9 two-parent merges and 3
single-parent commits (2 direct, steps 1 and 6; 1 squash, step 8). 10 records (#1–#10); #11 has
none; #7's commit is off the first-parent line. Areas: `day-01`, `day-02`, `day-03`, `docs`,
`tooling`, `other` (`release`). PR numbers are out of order (#4 before #3; #7, merged 01-27,
after #8 and #9). Dates span 25 days. `app/core.py` and `src/lib/util.py`, in different
modules, change together in 3 PRs (#1, #3, #9).

**Thresholds this day sets** (the fixture is frozen once its SHA is pinned, so later days
inherit them): the size threshold is **200 lines** (`grew`, Phase 2) and the coupling
threshold is **3 PRs** (Phase 3).

## Out of scope
- Reading the fixture: ingest, the mapping, the changelog — Phase 1, Days 2–4.
- Snapshots, the timeline, the module map — Phase 2, Days 5–7.
- Churn, coupling, said vs done — Phase 3, Days 8–10.
- A Windows job in CI: `.github/` is kit files (plan.md, Constraints); Windows is a local run
  here (C01.9). A Windows job would need a plan-change PR.

## Tracks

| Track | Owner | Work |
|---|---|---|
| A | implementer | C01.1–C01.4: the CLI, `.gitignore`, `.gitattributes`. Lands first: the first tests make "Tests" pass (pytest exits 5 with none) |
| B | implementer | C01.5–C01.6: `make_repo.py`, the history and `prs.json`, with placeholder contents |
| C | implementer | C01.7–C01.9: the table's contents and bodies, and `tests/contract/test_fixture.py` pinning the HEAD SHA |

C01.10 and C01.11 are `hold` and owned by this spec's PR, which ran their checks first.

## Acceptance criteria
Tick each box in the closing PR once its evidence is in it; under a box left unticked, write
`Not proven: <why>` (`specs/README.md`, "Evidence at the close").
- [x] C01.1 **new** — `python -m bearing --version` prints exactly "bearing 0.1.0\n" and exits
      0. Red today: "No module named bearing.__main__", exit 1; on CI's base worktree, where
      the head is installed editable, the head's `bearing.cli` finds no `__version__` in the
      base's `bearing/__init__.py` and exits 1.
      Test: `tests/test_cli.py::CliTest::test_version_module`
      Evidence: `CliTest.test_version_module` (#2), seen red first on `aa85066`'s code;
      `python -m pytest -q` (#2).
      broken: python -m bearing exits 1 without running main → 1 failed in 0.14s (#2)
- [x] C01.2 **new** — `pyproject.toml` declares the console script `bearing` as
      `bearing.cli:main`, and loading that entry point and calling it with `["--version"]`
      prints "bearing 0.1.0\n" and returns 0 (or raises `SystemExit(0)`). Red today: no
      `console_scripts` entry point named `bearing`; on CI's base worktree, loading it raises
      `ImportError` (no `__version__` in the base's `bearing`), inside the test.
      Test: `tests/test_cli.py::CliTest::test_console_script`
      Evidence: `CliTest.test_console_script` (#2), seen red first on `aa85066`'s code;
      `python -m pytest -q` (#2).
      broken: the version line printed as bearing-0.1.0 → 1 failed in 0.10s (#2)
- [x] C01.3 **new** — `git check-ignore bearing.egg-info/PKG-INFO .bearing/bearing.db` prints
      both paths and exits 0. Red today: it prints nothing and exits 1. (A path ending in `/`
      matches the CRLF blank line of the working tree's `.gitignore` on Windows today; the
      check names a file inside each directory.)
      Test: `tests/test_repo_files.py::RepoFilesTest::test_gitignore`
      Evidence: `RepoFilesTest.test_gitignore` (#2), seen red first on `aa85066`'s code;
      `python -m pytest -q` (#2).
      broken: the data directory ignored under another name → 1 failed in 0.10s (#2)
- [x] C01.4 **new** — `git check-attr eol -- tests/fixtures/make_repo.py` prints
      "tests/fixtures/make_repo.py: eol: lf". Red today: "eol: unspecified".
      Test: `tests/test_repo_files.py::RepoFilesTest::test_fixtures_eol_lf`
      Evidence: `RepoFilesTest.test_fixtures_eol_lf` (#2), seen red first on `aa85066`'s code;
      `python -m pytest -q` (#2).
      broken: the fixtures rule without eol=lf → 1 failed in 0.11s (#2)
- [x] C01.5 **new** — `make_repo.py <dir>` exits 0 and builds `<dir>/repo` whose
      `git log --first-parent --format=%s main` is the table's 12 subjects, newest first, with
      the table's parent counts (9 two, 3 one) and author dates; the side merge of #7 is
      reachable from `main` but not on the first-parent line. Red today: there is no
      `make_repo.py`, so the build exits 2.
      Test: `tests/test_make_repo.py::HistoryTest::test_first_parent_line`
      Evidence: `HistoryTest.test_first_parent_line` (#3), seen red first on `4a71d83`'s code,
      with `make_repo.py` moved aside; `python -m pytest -q` (#3).
      broken: PR #5's merge dated 01-20, not 01-19 → 1 failed in 4.28s (#3)
- [x] C01.6 **new** — `<dir>/prs.json` holds 10 records, #1–#10, with exactly the seven keys of
      "In scope"; `headRefName`, `baseRefName` and `mergedAt` as the table says; each
      `mergeCommit.oid` is its step's commit (#6 the squash commit, #7 the side merge); #11 is
      absent; the file is `sort_keys=True, indent=2` with a final `\n`. Red today: no
      `make_repo.py`.
      Test: `tests/test_make_repo.py::HistoryTest::test_pr_records`
      Evidence: `HistoryTest.test_pr_records` (#3), seen red first on `4a71d83`'s code, with
      `make_repo.py` moved aside; `python -m pytest -q` (#3).
      broken: #7's record based on main, not release → 1 failed in 4.31s (#3)
- [x] C01.7 **new** — the structure cases: at step 5 `app/a.py` and `app/b.py` import each other
      and at step 10 `app/b.py` no longer imports `app.a`; `app/crlf.py`'s blob holds `\r\n`;
      `ast.parse` fails on `app/broken.py` and succeeds on every other `.py` blob at HEAD;
      `app/core.py` has under 200 lines at step 7 and over 200 at step 8;
      `git diff -M --name-status <step 9>^1 <step 9>` has a line starting "R" for
      `scripts/helpers.py` → `scripts/tools.py`, an "A" for `app/extra.py` and a "D" for
      `app/legacy.py`; at HEAD `app/sub/mod.py` holds `from ..pkg import` and
      `from ..core import`, `app/__init__.py` holds `from . import core`, `scripts/run.py`
      imports `tools` and `scripts/tools.py` imports `config`. Red today: no `make_repo.py`;
      on Track B's builder, none of these files exist.
      Test: `tests/test_make_repo.py::StructureTest::test_cases`
      Evidence: `StructureTest.test_cases` (#6), seen red first on `a6ae0d8`'s code;
      `python -m pytest -q` (#6).
      broken: app/a.py no longer imports app.b (no cycle at step 5) → 1 failed in 4.98s (#6)
- [x] C01.8 **new** — the PR-text cases: #1's body has "## What I built"; #2's body has text and
      no "What I built"; #4's body is `""`; #5's head starts with `docs/` and its merge
      (`merge^1..merge`) changes `scripts/run.py`; #9's body holds "Contract impact: None" and
      its merge changes `tests/contract/test_api.py`; `app/core.py` and `src/lib/util.py` are
      both changed by exactly the merges of #1, #3 and #9 among the PR merges. Red today: no
      `make_repo.py`; on Track B's builder, every body is `""`.
      Test: `tests/test_make_repo.py::TextTest::test_cases`
      Evidence: `TextTest.test_cases` (#6), seen red first on `a6ae0d8`'s code;
      `python -m pytest -q` (#6).
      broken: #3 changes app/sub/mod.py instead of src/lib/util.py → 1 failed in 5.26s (#6)
- [x] C01.9 **new** — two builds in two empty directories give the same HEAD SHA and the same
      `prs.json` bytes, and the HEAD SHA equals the constant in
      `tests/contract/test_fixture.py`; on Linux CI ("Tests") and in a local run on Windows with
      the system gitconfig's `core.autocrlf true`. Red today: no `make_repo.py`; on Track B's
      builder, another SHA.
      Test: `tests/contract/test_fixture.py::FixtureTest::test_head_sha`
      Evidence: `FixtureTest.test_head_sha` (#6), seen red first on `a6ae0d8`'s code;
      `python -m pytest -q` (#6), on Linux CI ("Tests", #6) and locally on Windows (#8).
      broken: author dates shifted by one second → 1 failed in 9.11s (#6)
- [x] C01.10 **hold** — `.github/workflows/tests.yml` runs the style check and the tests:
      `grep -c -E '^\s+run: (pytest -q|ruff check \. && ruff format --check \.)\s*$' .github/workflows/tests.yml`
      prints 2.
      broken: the test step replaced by an echo in tests.yml → 1 (#1)
      broken: near miss: the test step narrowed to tests/unit → 1 (#1)
      broken: near miss: the style step without the format check → 1 (#1)
- [x] C01.11 **hold** — the repository variables are set: `gh variable list` shows
      `STYLE_CHECK_COMMAND` as "ruff check . && ruff format --check ." and `TRACK_RED_RUNNER`
      as "pytest". They live outside the repository, so no break can run from it: a reader
      checks the listing at the close.
      broken: none → the variables live outside the repository
      Not proven: a reader read gh variable list (#8): `STYLE_CHECK_COMMAND` "ruff check . &&
      ruff format --check .", `TRACK_RED_RUNNER` "pytest".

## Verify
```bash
python -m pytest -q
python -m bearing --version  # bearing 0.1.0
python tests/fixtures/make_repo.py .bearing/fixture-check
git -C .bearing/fixture-check/repo log --first-parent --oneline HEAD
grep -c -E '^\s+run: (pytest -q|ruff check \. && ruff format --check \.)\s*$' .github/workflows/tests.yml  # 2
```

## Notes
- Test names: with `TRACK_RED_RUNNER=pytest`, `scripts/track-red.py` passes each `Test:` name to
  pytest as is, so `Test:` fields hold node IDs; `scripts/evidence.py` recognises only
  `` `Class.test_x` `` and finds the class under `tests/`. So `Test:` holds the node ID, and
  each `Evidence:` line names `Class.test_x` and the command `python -m pytest -q`.
- C01.1 and C01.2 on CI's base worktree: the head is installed editable, and setuptools' finder
  supplies the head's `bearing.cli` and `bearing.__main__` where the base has none, while
  `bearing` itself comes from the base (the working directory is first on `sys.path`). So the
  version must come from `bearing.__version__`, which the base's empty `__init__.py` lacks, and
  the tests import inside the test function. Reading it from `importlib.metadata` would pass
  on the base (the spec-auditor ran both).
- **Known limit, Tracks B and C:** "Track tests seen red" copies every changed file under
  `tests/` into the base worktree (`scripts/seen-red.py`, `changed_tests` and `on_base`),
  `tests/fixtures/make_repo.py` included, so C01.5–C01.9's tests pass there and the check
  reports "it does not see the change". It is a required check. Track B shows seen red by hand
  with `make_repo.py` moved aside (the subprocess exits 2, an assertion fails); Track C with
  `git stash push -- tests/fixtures/make_repo.py`, the new tests run against main's builder.
  Both PRs need the maintainer's admin merge, or a kit fix first (H01.5).
- C01.9's break shifts one fixture date by a second, so the SHA differs on every system. The
  Windows-only guard (the system's `core.autocrlf true` kept out by `GIT_CONFIG_NOSYSTEM` and
  `-c core.autocrlf=false` together) is not one replacement; the local Windows run guards it.
- C01.10's grep is judged by its output, not its exit (`grep -c` exits 0 at 1): its breaks
  carry `expect_stdout` "^2$". Broken three ways in this spec's PR (one step replaced, two near
  misses). It cannot see `continue-on-error: true` or `if: false` added to a step (the
  spec-auditor tried both: still 2): a known limit.
- C01.11 at the close: under the box, `broken: none → the variables live outside the
  repository`, then `Not proven: a reader read gh variable list (#n)`, in that order; a
  `Not proven:` line before them reads as a changed statement.
- Verify builds into `.bearing/fixture-check` and `make_repo.py` refuses it non-empty, so a
  second local run needs that directory removed first.
- The spec-auditor's findings 1–11 (this spec's PR) are D01.7–D01.17.
- **Defect** D01.1 — found: auditor · cause: environment · made: none · "Track tests seen red"
  cannot see a test of code under `tests/` fail (H01.5); recorded in this spec's PR.
- **Defect** D01.2 — found: auditor · cause: spec · made: none · plan.md's hard-parts table
  requires `tests/fixtures/` at `eol=lf`, but Phase 0's list leaves it out; C01.4 adds it.
- **Defect** D01.3 — found: auditor · cause: spec · made: none · plan.md requires the fixture
  to pass the size and coupling thresholds but defines neither, and the fixture freezes on
  Day 1; this spec sets 200 lines and 3 PRs.
- **Defect** D01.4 — found: auditor · cause: spec · made: none · plan.md's Done-when asks for the
  SHA test "on Windows", but CI runs Ubuntu only and `.github/` is kit files; C01.9 takes a
  local Windows run.
- **Defect** D01.5 — found: auditor · cause: process · made: none · the "Tests" check exits 5
  with no tests, so it fails on every PR until Track A lands; this spec's PR needs an admin
  merge.
- **Defect** D01.6 — found: auditor · cause: process · made: none · CLAUDE.md ("The
  implementer") and `specs/README.md` ("Short specs") name the runner `unittest`; this
  project's `TRACK_RED_RUNNER` is `pytest` (H01.6).
- **Defect** D01.7 — found: auditor · cause: spec · made: Day 01 · the draft let C01.1 and
  C01.2 pass on CI's base worktree (the head's `bearing.cli` through the editable finder);
  the version now comes from `bearing.__version__`; fixed in this spec's PR.
- **Defect** D01.8 — found: auditor · cause: spec · made: Day 01 · a Verify line named `main`,
  which the replay rewrites to a Bearing SHA the fixture does not have; now `HEAD`.
- **Defect** D01.9 — found: auditor · cause: spec · made: Day 01 · C01.11 as drafted would fail
  the replay (a hold with no `broken:` line) or the wording check; the close's lines are now
  set out above.
- **Defect** D01.10 — found: auditor · cause: spec · made: Day 01 · the draft's Windows-only
  break of C01.9 (`core.autocrlf=false` left out) could not bite under `GIT_CONFIG_NOSYSTEM=1`;
  the break is now a shifted date.
- **Defect** D01.11 — found: auditor · cause: spec · made: Day 01 · the draft gave every case to
  Track B, so Track C's new tests would pass on its base; Track B now builds placeholder
  contents.
- **Defect** D01.12 — found: auditor · cause: spec · made: Day 01 · identical or empty contents
  in `app/legacy.py` and `app/extra.py` turn C01.7's "A" and "D" into a rename; contents must
  now be distinct and non-empty.
- **Defect** D01.13 — found: auditor · cause: spec · made: Day 01 · the draft claimed its
  environment kept a global attributes file out; `XDG_CONFIG_HOME/git/attributes` still
  applied; `-c core.attributesFile` and `GIT_ATTR_NOSYSTEM=1` added.
- **Defect** D01.14 — found: auditor · cause: spec · made: Day 01 · the draft did not require
  `unittest.TestCase` classes, and pytest collects no plain `CliTest`; now required.
- **Defect** D01.15 — found: auditor · cause: spec · made: Day 01 · two Verify lines were judged
  by exit code only (`grep -c` exits 0 at 1); they now carry their expected output.
- **Defect** D01.16 — found: auditor · cause: spec · made: Day 01 · the draft did not say
  `make_repo.py` creates a missing `<dir>`, and Verify fails on a second local run; both now
  stated.
- **Defect** D01.17 — found: auditor · cause: spec · made: Day 01 · the Out-of-scope list and the
  hand-offs named days differently; Out of scope now names the phases.
- The spec-auditor also read plan.md's "flat `scripts/` folder whose files import each other"
  and "`from ..pkg import`" as looser than the draft built them; the table now has
  `scripts/config.py` and `app/pkg/`.
- **Hand-off** H01.1 → Day 5: the size threshold is 200 lines; the fixture's `app/core.py`
  crosses it at step 8.
- **Hand-off** H01.2 → Day 8: the coupling threshold is 3 PRs; `app/core.py` and
  `src/lib/util.py` meet it exactly (#1, #3, #9).
- **Hand-off** H01.3 → Day 2: the squash commit's subject is GitHub's "Title (#N)" form, not
  "Merge pull request #N"; only its record's `mergeCommit` matches it. #7's record points off
  the first-parent line and must be reported unmatched.
- **Hand-off** H01.4 → Day 8: #9 says "Contract impact: None" (capital N; plan.md's Phase 3
  says "none": match without case); #5 is a `docs/` PR that touches a script, which plan.md
  says is not a lie.
- **Hand-off** H01.5 → the maintainer: fix `scripts/seen-red.py` in the kit so it does not copy
  fixtures (or code) under `tests/` into the base, and copy it over at a stop.
- **Hand-off** H01.6 → the maintainer: the kit's documents say `unittest` where the runner is the
  project's; fix in the kit.
- At the close: #4 fixed D01.1's limit in this repository (`code_under_tests`) before Tracks B
  and C merged; #3 took `main` in, and "Track tests seen red" passed on both #3 and #6, so
  neither needed the admin merge the Notes above foresaw. H01.5 still stands for the kit.
- At the close: #6 recorded a fourth break, "the builder no longer sets GIT_AUTHOR_NAME, so
  this machine's identity leaks in", which failed `FixtureTest.test_head_sha` in 8.93s. It bites
  only where the environment sets `GIT_AUTHOR_NAME`, as this Windows machine's does; on the
  replay's Ubuntu runner, `-c user.name=Fixture` gives the same identity and the test passes
  with the break in. So it is not under C01.9 and not in `specs/breaks/day-01.json`: a local
  Windows run guards it.
- At the close, all 13 recorded breaks were run again through `scripts/break.py`, one at a
  time, from the manifest's arguments: each failed its check, with the PRs' reports apart from
  pytest's run time. The run time was why #7 came first: the replay compared it, and
  10 of the 13 reports carry one.
- **Defect** D01.18 — found: Track A · cause: environment · made: Day 01 · CI installs ruff
  unpinned and got 0.17.3, which reports PLW1510 on `subprocess.run` without `check=`; the
  local 0.15.13 passed it. #2's first push failed "Style check"; fixed with `check=False`. ruff
  is still unpinned.
- **Defect** D01.19 — found: Track C · cause: spec · made: Day 01 · "In scope" listed the git
  settings that pin the fixture's SHA but not `GIT_AUTHOR_NAME`, `GIT_AUTHOR_EMAIL`,
  `GIT_COMMITTER_NAME` and `GIT_COMMITTER_EMAIL`, which override `-c user.name`; this machine
  sets them, so #6's first push built another SHA here than on CI. Track B's builder had the
  same leak, unseen with no SHA pinned. The builder now sets all four (#6).
- **Defect** D01.20 — found: close · cause: environment · made: none · `scripts/evidence.py`
  compared pytest's run time ("1 failed in 0.14s") when replaying a break, so no pytest break
  could match twice; fixed in #7 before this close.
- **Defect** D01.21 — found: close · cause: process · made: Day 01 · the `manifest:` lines in
  #1 and #6 lost a level of backslashes in the PR bodies (`\s` for `\\s`, a newline for `\n`):
  #1's no longer parsed as JSON, and two of #6's finds no longer matched `make_repo.py`. The
  close restored them to the source's text and replayed every entry.
- **Defect** D01.22 — found: self · cause: process · made: none · in #7, the break on purpose
  ran while a background run of every `scripts/test_*.py` was still reading the same file, which
  then reported 4 failures; alone, the file passed.
