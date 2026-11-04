# Day 05 — `bearing snapshot`: one module per `.py` file, its lines and its imports

**Phase:** 2 · **Depends on:** Day 4 · **Expected PRs:** 6 (this spec, tracks 0, A, B and C, the close)

## Goal
`bearing snapshot <repo> <ref>` prints the `snapshot-v1` JSON of the target repository at one
commit: every `.py` file as one module with a dotted name (plan.md, Course correction "before
Day 5"), its line count, whether it parses, and the in-repository imports between modules,
resolved for relative imports, a `src/` layout and a flat folder; on the fixture it matches a
golden file.

## In scope
- `bearing/snapshot/__init__.py` (Track 0): empty, so every later test imports a grandchild of
  `bearing` (Day 2's Notes, "Red on CI's base").
- `bearing/snapshot/modules.py` (Track A), pure functions on paths, bytes and strings; no git:
  - `module_names(paths)`: from an iterable of repository paths (POSIX, `/`) ending in `.py`,
    a `dict` path → dotted name. A path is named by its parts from its import root, `.` for
    `/`, with no `.py`; `__init__.py` is named by its package. The root is per file: a path
    whose first part is `src` and that has more parts drops `src/` (`src/lib/util.py` is
    `lib.util`); every other path is named from the repository root (`app/core.py` is
    `app.core`). When two paths would take one name (`x.py` and `src/x.py`), the path outside
    `src/` keeps it and the `src/` one is named from the repository root (`src.x`). First,
    before that rule, a path whose name from its root is empty (`__init__.py`, and
    `src/__init__.py`) is left out of the `dict`, and takes no part in a collision. Any other
    two paths with one name (`x.py` beside `x/__init__.py`) both keep it; the snapshot lists
    them sorted by name, then path, so its bytes are still fixed (Out of scope).
  - `count_lines(data)`: the number of `b"\n"` in the bytes, plus 1 when the bytes are not
    empty and do not end in `b"\n"`. A `\r\n` counts once; a lone `\r` is not a line end.
  - `parse_imports(data)`: `ast.parse` on the bytes (so a coding cookie or a BOM is honoured),
    inside `warnings.catch_warnings()` with `warnings.simplefilter("ignore")`, so a
    `SyntaxWarning` neither reaches stderr nor, under `-W error`, turns into a parse error.
    On `SyntaxError`, `ValueError`, `RecursionError` or `MemoryError` it returns `None` (the
    module's `parse_error`; non-UTF-8 bytes and a NUL byte are `SyntaxError`s on 3.12, deep
    nesting the other two: plan.md, "never a crash"). Otherwise a sorted list of tuples
    `(level, module, names)`, one per import statement anywhere in the file (inside functions
    and `if` blocks too): `import a.b, c` gives `(0, "a.b", ())` and `(0, "c", ())`;
    `from ..pkg import h, k` gives `(2, "pkg", ("h", "k"))`; `from . import core` gives
    `(1, "", ("core",))`. This form names no module of the repository, so a later day can
    cache it by blob SHA whatever path the blob has (the Renames row; plan-auditor F4).
  - `import_edges(imports, names)`: `imports` maps a path to `parse_imports`'s result (or
    `None`), `names` is `module_names`'s `dict` for the same tree. Returns the sorted list of
    distinct `[from, to]` pairs of module names, with no self-edge and no edge to a name that
    is not a module of the tree. One import resolves this way:
    - a relative import's base is the importer's package (the module itself for an
      `__init__.py`, its name less the last part otherwise), less `level - 1` parts, then
      `.module` when there is one; when `level - 1` is not less than the package's number of
      parts (the whole package or more consumed, as Python's ImportError), there is no edge;
    - `import a.b` resolves to `a.b` only, when it is a module, never also to `a`;
    - `from base import n` resolves, for each `n`, to `base.n` when that is a module, otherwise
      to `base` when that is (so `from ..pkg import h` gives `app.pkg`, and `from . import
      core` in `app/__init__.py` gives `app.core`);
    - an absolute import (level 0) that resolves to nothing as above, from a file whose folder
      holds no `__init__.py` in the tree, is tried again with the importer's name less its last
      part before it, when that is not empty (`import helpers` in `scripts/run.py`, named
      `scripts.run`, gives `scripts.helpers`). The absolute name
      wins when both exist; a folder with `__init__.py` gets no such second try.
- `bearing/snapshot/tree.py` (Track B): `snapshot(repo, ref)` runs, read-only,
  `git -C <repo> rev-parse --git-dir` (a failure is "not a git repository: <repo>"),
  `git -C <repo> rev-parse --verify --quiet <ref>^{commit}` (a failure is "not a commit:
  <ref>"), `git -C <repo> ls-tree -r -z --full-tree <sha>`, keeping the entries of type
  `blob` with mode `100644` or `100755` whose path ends in `.py`, and
  `git -C <repo> cat-file blob <blob sha>` for each; it returns the `dict`
  `{"version": "snapshot-v1", "ref": <full sha>, "modules": [...], "imports": [...]}`, each
  module `{"name", "path", "lines", "parse_error"}`, modules sorted by name, imports from
  `import_edges` (plan.md, "Output contracts"). A git failure raises `SnapshotError(Exception)`
  (in `tree.py`) with the message above; no other git command runs. Git that cannot be started
  (`OSError`) is `SnapshotError("cannot run git in <repo>: <strerror>")`, as for `ingest`.
- `bearing snapshot <repo> <ref>` (Track C), in `bearing/cli.py`: prints
  `json.dumps(snapshot, sort_keys=True, indent=2)` and a newline, exits 0. On an error it prints
  `bearing: <message>` to stderr, nothing to stdout, and exits 1. It opens no store and takes
  no `--data`.
- Tests: `tests/test_modules.py` (Track A); the golden file
  `tests/fixtures/expected/snapshot-448fc4d.json` and `tests/test_snapshot_tree.py` (Track B);
  `tests/contract/test_snapshot.py` and `tests/test_snapshot_cli.py` (Track C). The CLI tests run git with `GIT_DIR` and `GIT_WORK_TREE` removed from the
  environment they pass, so a hook's environment cannot point git at this repository.
  As on Days 2 to 4: every test class subclasses `unittest.TestCase`, imports the module under
  test inside the test method, and builds the fixture with `make_repo.py` as a subprocess (once
  per class) where it needs one; CLI tests run `python -m bearing` with `cwd=` the repository
  root. Track A's tests use paths, strings and bytes written in the test: the fixture is
  frozen and holds no non-UTF-8 file and no name collision.

### What the fixture gives

Run in this spec's prototype on 2026-11-04 on `004a5c8`, and again, independently, by the
plan-auditor; both gave these values.

- At `448fc4dc915289f0b3f0254cf80360b56f48513a` (the squash of #6, step 8), 15 modules, as
  name `path` lines, `parse_error` false unless marked: `app` `app/__init__.py` 1, `app.a`
  `app/a.py` 3, `app.b` `app/b.py` 7, `app.broken` `app/broken.py` 2 (`parse_error` true),
  `app.core` `app/core.py` 253, `app.crlf` `app/crlf.py` 5 (CRLF), `app.legacy`
  `app/legacy.py` 3, `app.pkg` `app/pkg/__init__.py` 5, `app.sub` `app/sub/__init__.py` 1,
  `app.sub.mod` `app/sub/mod.py` 8, `lib` `src/lib/__init__.py` 1, `lib.util`
  `src/lib/util.py` 13, `scripts.config` `scripts/config.py` 3, `scripts.helpers`
  `scripts/helpers.py` 7, `scripts.run` `scripts/run.py` 5; and 8 imports: `app → app.core`,
  `app.a → app.b`, `app.b → app.a`, `app.sub.mod → app.core`, `app.sub.mod → app.pkg`,
  `lib.util → app.core`, `scripts.helpers → scripts.config`, `scripts.run → scripts.helpers`.
  Every hard case of Phase 2 that a single snapshot shows is here: the cycle, the parse error,
  the CRLF file, relative imports, the `src/` layout and the flat folder.
- At `main` (`8c1b9f1b90d3e582590942e15b131cea986d94c3`), 16 modules: the 15 above less
  `app.legacy` and `scripts.helpers`, plus `app.extra` `app/extra.py` 5, `scripts.tools`
  `scripts/tools.py` 7 and `tests.contract.test_api` `tests/contract/test_api.py` 5; with
  `app.b` at 5 lines, `app.core` at 257 and `lib.util` at 17. 7 imports: `app → app.core`,
  `app.a → app.b`, `app.sub.mod → app.core`, `app.sub.mod → app.pkg`, `lib.util → app.core`,
  `scripts.run → scripts.tools`, `scripts.tools → scripts.config`.
- `json.dumps(sort_keys=True)` orders the keys `imports`, `modules`, `ref`, `version`, and a
  module's `lines`, `name`, `parse_error`, `path`: the golden file's bytes are the contract,
  not the order plan.md lists them in (plan-auditor F9).

## Out of scope
- The blob cache, its `002_*.sql` migration and `--stats` — Day 6 (H05.4).
- The snapshot diff, rename pairing with `git diff -M`, and the timeline's events — Day 6
  (H05.2, H05.3); `cycle+`/`cycle-`, `grew` (H01.1, re-pointed as H05.5), the timeline golden
  file and the kit's and wordtally's runs — Day 7.
- The module map in `bearing.toml`, and where `bearing.toml` is read from — Day 7 (H05.6).
- A `.py` path that is not UTF-8, a symlink (mode `120000`) or a submodule entry: decided, not
  tested. Paths are decoded as UTF-8 with `surrogateescape`; symlinks and submodules are not
  modules (`ls-tree`'s filter above).
- Two paths with one name besides the `src/` collision (`x.py` beside `x/__init__.py`;
  `src/x.py` beside `src/x/__init__.py`), and a `src/` package renamed by a collision whose
  files keep their `src/`-less names: deterministic as In scope says, not resolved further.
  No history Bearing is tested on has one.
- Imports of names outside the repository (`os`, `pytest`): never an edge (plan.md, "only
  in-repository edges").

## Tracks

| Track | Owner | Work |
|---|---|---|
| 0 | implementer | `bearing/snapshot/__init__.py`, empty; no criterion of its own |
| A | implementer | C05.1–C05.4: `bearing/snapshot/modules.py` and `tests/test_modules.py` |
| B | implementer | C05.6, C05.10: `bearing/snapshot/tree.py`, the golden file, `tests/test_snapshot_tree.py` |
| C | implementer | C05.5, C05.7, C05.8: `bearing snapshot` in `bearing/cli.py`, `tests/contract/test_snapshot.py`, `tests/test_snapshot_cli.py` |

Track 0 lands first, then A, then B (B imports A's functions), then C (C calls B's
`snapshot`). Each track's `new` tests are red on its own base, as CI's "Track tests seen red"
requires (`TRACK_RED_RUNNER` is `pytest` here): B's because `tree.py` and the golden file are
not there, C's because the subcommand is not. A test of the command alone in a later track
would pass on its base and fail that check. C05.9 is `hold` and owned by
this spec's PR, which runs its check first.

## Acceptance criteria
Tick each box in the closing PR once its evidence is in it; under a box left unticked, write
`Not proven: <why>` (`specs/README.md`, "Evidence at the close").
- [ ] C05.1 **new** — `module_names` on the paths `app/__init__.py`, `app/core.py`,
      `app/pkg/__init__.py`, `src/lib/__init__.py`, `src/lib/util.py`, `scripts/helpers.py`,
      `tests/contract/test_api.py`, `setup.py`, `src/x.py`, `x.py`, `__init__.py` and
      `src/__init__.py` returns exactly `{"app/__init__.py": "app", "app/core.py": "app.core",
      "app/pkg/__init__.py": "app.pkg", "src/lib/__init__.py": "lib", "src/lib/util.py":
      "lib.util", "scripts/helpers.py": "scripts.helpers", "tests/contract/test_api.py":
      "tests.contract.test_api", "setup.py": "setup", "src/x.py": "src.x", "x.py": "x"}`, the
      same for the paths in reverse order; and `{"src/x.py": "x"}` for `["src/x.py"]` alone.
      Red today: "No module named 'bearing.snapshot'"; after Track 0, "No module named
      'bearing.snapshot.modules'".
      Test: `tests/test_modules.py::ModuleNameTest::test_names`
- [ ] C05.2 **new** — `count_lines` gives 0 for `b""`, 1 for `b"a"`, 1 for `b"a\n"`, 2 for
      `b"a\nb"`, 2 for `b"a\r\nb\r\n"`, 1 for `b"a\rb\n"` and 3 for `b"\n\n\n"`. Red today: as
      C05.1.
      Test: `tests/test_modules.py::LinesTest::test_counts`
- [ ] C05.3 **new** — `parse_imports` returns `None` for `b"def broken(:\n    return 1\n"`, for
      `b"x = '\xe9'\n"` (latin-1 bytes, no cookie) and for `b"x = 1\x00\n"`; for
      `b"# -*- coding: latin-1 -*-\nx = '\xe9'\n"` it returns `[]`; for the CRLF bytes
      `b"import b\r\n\r\ndef f():\r\n    from ..pkg import h, k\r\n"` it returns
      `[(0, "b", ()), (2, "pkg", ("h", "k"))]`; and for
      `b"from . import core\nimport a.b, c\n"` it returns
      `[(0, "a.b", ()), (0, "c", ()), (1, "", ("core",))]`. It returns `None`, without raising,
      for `b"1+" * 200000 + b"1\n"` (`RecursionError` on 3.12) and for
      `b"x=" + b"-" * 200000 + b"1\n"` (`MemoryError`, "Parser stack overflowed"). And called
      inside `warnings.catch_warnings()` with `warnings.simplefilter("error")`, for the bytes
      `x = "\d"` and a newline (an invalid escape: a `SyntaxWarning`) it returns `[]`, not
      `None`. Red today: as C05.1.
      Test: `tests/test_modules.py::ParseTest::test_imports_and_errors`
- [ ] C05.4 **new** — `import_edges` on a tree written in the test, each file's source given to
      `parse_imports` and the paths to `module_names`: `app/__init__.py` `from . import core`,
      `app/core.py` `import os\nimport app.core`, `app/pkg/__init__.py` empty, `app/sub/__init__.py`
      empty, `app/sub/mod.py` `from ..pkg import h\nfrom ..core import f\nfrom ... import app`,
      `app/x.py` `import core\nfrom app import pkg, sub`, `src/lib/util.py`
      `import app.core\nimport app.nothing`, `scripts/run.py` `import helpers\nimport app`,
      `scripts/helpers.py` `from config import DEBUG`, `scripts/config.py` empty,
      `scripts/app.py` empty, and `app/broken.py` `def broken(:`; returns exactly
      `[["app", "app.core"], ["app.sub.mod", "app.core"], ["app.sub.mod", "app.pkg"],
      ["app.x", "app.pkg"], ["app.x", "app.sub"], ["lib.util", "app.core"],
      ["scripts.helpers", "scripts.config"], ["scripts.run", "app"],
      ["scripts.run", "scripts.helpers"]]`. That is: no self-edge (`app.core`), no edge
      outside the tree (`os`, `app.nothing`), none when the whole package is consumed
      (`from ... import app` in `app.sub.mod`: a reading that clamps at the top would give
      `app.sub.mod → app`), none from the
      parse error, no sibling try inside a package (`import core` in `app/x.py`), and the
      absolute `app` wins over `scripts/app.py`. Red today: as C05.1.
      Test: `tests/test_modules.py::ResolveTest::test_edges`
- [ ] C05.5 **new** — the `snapshot-v1` contract: `python -m bearing snapshot <dir>/repo
      448fc4dc915289f0b3f0254cf80360b56f48513a`, on the fixture, exits 0, and its stdout, with
      `\r\n` read as `\n`, equals the bytes of `tests/fixtures/expected/snapshot-448fc4d.json`.
      The golden file holds exactly the 15 modules and 8 imports of "What the fixture gives",
      `"ref"` the full SHA and `"version"` `"snapshot-v1"`, written as
      `json.dumps(..., sort_keys=True, indent=2)` plus `"\n"`; C05.10 checks its content
      against that list, written out apart from the code. The bytes are compared, not the parsed
      object (`specs/README.md`): every path comes from git with `/`, and the bytes are the
      contract (plan-auditor F9). Red today: argparse's "invalid choice: 'snapshot'" (exit 2).
      Test: `tests/contract/test_snapshot.py::SnapshotContractTest::test_golden`
- [ ] C05.6 **new** — at `main`: `snapshot("<dir>/repo", "main")` returns a `dict` with
      `"version"` `"snapshot-v1"`, `"ref"` `"8c1b9f1b90d3e582590942e15b131cea986d94c3"`, its
      modules as `"<name> <path> <lines> <parse_error>"` strings equal to the 16 of "What the
      fixture gives" written out in the test, in that sorted order, and its imports equal to the
      7 written out there. And `snapshot("<dir>/repo", "no-such-ref")` raises `SnapshotError`
      with the message "not a commit: no-such-ref". Red today: "No module named
      'bearing.snapshot'" (after Track 0, 'bearing.snapshot.tree').
      Test: `tests/test_snapshot_tree.py::SnapshotTreeTest::test_main`
- [ ] C05.7 **new** — errors, stderr read with `\r\n` as `\n`:
      `python -m bearing snapshot <dir>/repo no-such-ref` exits 1, stdout is empty, and stderr
      is exactly "bearing: not a commit: no-such-ref\n"; `python -m bearing snapshot <tmp> main`,
      `<tmp>` an empty directory made by the test, exits 1, stdout empty, stderr exactly
      "bearing: not a git repository: <tmp>\n", `<tmp>` as the test passed it. Red today: as
      C05.5.
      Test: `tests/test_snapshot_cli.py::SnapshotCliTest::test_errors`
- [ ] C05.8 **new** — the target is read-only (plan.md, "Decisions"): after
      `python -m bearing snapshot <dir>/repo main` and the first command of C05.7, its `git status --porcelain --ignored` prints nothing, and
      `git for-each-ref` and `git rev-parse HEAD` print what they printed before them. Red
      today: the commands exit 2 before reading anything, so the test fails on their exit code.
      Test: `tests/test_snapshot_cli.py::SnapshotCliTest::test_read_only`
- [ ] C05.10 **new** — the golden file's content, from a list written apart from the code:
      `json.loads` of `tests/fixtures/expected/snapshot-448fc4d.json` has `"version"`
      `"snapshot-v1"`, `"ref"` `"448fc4dc915289f0b3f0254cf80360b56f48513a"`, its modules as
      `"<name> <path> <lines> <parse_error>"` strings equal to the 15 of "What the fixture
      gives" written out in the test (`"app.broken app/broken.py 2 True"`, the others `False`),
      and its imports equal to the 8 written out there; and `snapshot("<dir>/repo",
      "448fc4dc915289f0b3f0254cf80360b56f48513a")` equals that parsed object. So a golden file
      written from a wrong implementation's output fails here, not only in a reader's eyes. Red
      today: as C05.6.
      Test: `tests/test_snapshot_tree.py::SnapshotTreeTest::test_golden_content`
- [ ] C05.9 **hold** — the frozen files stay as Day 4 and the kit copy left them: the fixture, the
      three contract tests and their golden files, and the applied migration:
      `git -c core.safecrlf=false diff --exit-code 004a5c8 -- tests/contract/test_fixture.py tests/contract/test_ingest.py tests/contract/test_changelog.py tests/fixtures/make_repo.py tests/fixtures/expected/changelog.md tests/fixtures/expected/ingest.txt bearing/migrations/001_history.sql`
      prints nothing and exits 0. The files are named one by one: the day adds a contract test
      and a golden file beside them, which a diff of the directories would report.

## Verify
```bash
python -m pytest -q
python tests/fixtures/make_repo.py .bearing/day05-check
python -m bearing snapshot .bearing/day05-check/repo 448fc4dc915289f0b3f0254cf80360b56f48513a
python -m bearing snapshot .bearing/day05-check/repo main
git -c core.safecrlf=false diff --exit-code 004a5c8 -- tests/contract/test_fixture.py tests/contract/test_ingest.py tests/contract/test_changelog.py tests/fixtures/make_repo.py tests/fixtures/expected/changelog.md tests/fixtures/expected/ingest.txt bearing/migrations/001_history.sql
```

## Notes
- The plan-auditor ran on Phase 2 before this spec (CLAUDE.md, step 1). F1–F3 are settled here;
  the others are hand-offs below. F1: plan.md's `bearing snapshot <ref>` names no repository,
  and the store records none; the repository is a positional argument, as for `ingest`, and
  no migration is needed today. F2: the module map is Day 7's (H05.6). F3: the resolution
  rules in In scope.
- Resolution choices, each a choice and not evidence: the submodule before the package for
  `from base import n` (it is what Python loads); `import a.b` names `a.b` only (an edge to the
  parent package would put every `__init__.py` on every path through it); the absolute name
  before the sibling in a flat folder (where Python, running the script, tries the folder
  first; an absolute in-repository name shadowing a sibling is rare, and the absolute rule is
  the one that holds inside packages). Imports anywhere in the file count, `if TYPE_CHECKING:`
  included: they are dependencies of the code as written.
- The golden file is pinned at `448fc4d`, not `main`: it holds the cycle, which `main` has
  broken. `main` is pinned by C05.6 on the parsed object, outside `tests/contract/`, as a written-out
  list: one golden file is the contract, and the second state is a test that may change.
- Sizes, from the spec-auditor's estimate: the golden file is about 130 lines; module lists
  are written as one string per module (C05.6, C05.10), not `dict`s (about 99 lines for 16).
  Track B, `tree.py` (about 70), the golden file and the tree tests, comes to about 300; Track
  C, the CLI (about 25), the contract test (about 55) and the CLI tests, to about 150.
- The count: 38 tests pass today; the day adds 9 test methods (the `Test:` fields of
  C05.1–C05.8 and C05.10), so `pytest -q` ends at "47 passed" (subtests besides).
- "Opens no store and takes no `--data`" is not tested: the CLI tests run with `cwd=` the
  repository root, where a stray `.bearing/` would go unseen. A reader checks it in Track C's
  diff (no use of `bearing.store` in the command).
- "cannot run git in <repo>" (no git on the PATH) is not tested, as on Day 2.
- Verify's `make_repo.py .bearing/day05-check` refuses a directory that is not empty: delete it
  before a second local run.
- **Defect** D05.1 — found: spec-change PR · cause: spec · made: Day 05 · the first draft of
  `module_names` let `src/__init__.py` read two ways: its name from `src/` is empty, which
  collides with the empty name of `__init__.py`, so the collision rule named it `src`, against
  C05.1. The spec's own rules, run in a scratch implementation, showed it; the empty-name rule
  now comes first.
- **Defect** D05.2 — found: auditor · cause: spec · made: Day 05 · Track B held the command,
  the golden file, its contract test and the CLI tests, about 500 lines against the 400 limit,
  and the Notes' reason for one golden file was wrong. Split by what is red on each base: B is
  `snapshot()` with the golden file, tested as a function; C is the command with its contract
  and CLI tests (a tests-only Track C, the auditor's split, would pass on its base, and CI's
  `TRACK_RED_RUNNER` is set).
- **Defect** D05.3 — found: auditor · cause: spec · made: Day 05 · C05.4's `from .... import z`
  gave no edge under a correct rule and under one that clamps at the top alike, and "a level
  past the top" left the whole-package case open; the rule now says `level - 1` not less than
  the package's parts, and the case is `from ... import app`.
- **Defect** D05.4 — found: auditor · cause: spec · made: Day 05 · the collision rule covered
  only one path outside `src/` against one inside; any other pair took one name with no rule
  for the snapshot's order. Both now keep the name, sorted by name then path, and the cases
  are Out of scope.
- **Defect** D05.5 — found: auditor · cause: spec · made: Day 05 · C05.5's golden file could be
  written from a wrong implementation's output, checked only by a reader; C05.10 checks its
  content against a list written apart from the code.
- **Defect** D05.6 — found: auditor · cause: spec · made: Day 05 · `parse_imports` caught only
  `SyntaxError` and `ValueError`; deep nesting raises `RecursionError` or `MemoryError` (a
  crash, against plan.md), and a `SyntaxWarning` printed to stderr, or under `-W error`
  became a parse error. Both now caught or silenced, with C05.3 cases.
- **Defect** D05.7 — found: auditor · cause: spec · made: Day 05 · C05.1's red was given as
  "No module named 'bearing.snapshot.modules'", which is the red after Track 0; today it is
  'bearing.snapshot'.
- **Defect** D05.8 — found: auditor · cause: spec · made: Day 05 · C05.7 compared stderr exactly
  with no `\r\n` rule and did not say the path is echoed as given; and a `GIT_DIR` in the
  environment would point git at this repository. C05.7 now reads `\r\n` as `\n`, and the CLI
  tests drop `GIT_DIR` and `GIT_WORK_TREE`.
- **Hand-off** H05.1 → the maintainer: plan.md's Day 10 stop names "co-change coupling, then
  cycle detection in the timeline" as the next cuts, but cycle detection is Phase 2 (Day 7)
  and coupling is built by the stop; the cut list wants a plan-change PR (plan-auditor F7).
- **Hand-off** H05.2 → Day 6: how `bearing timeline` finds the target repository and the
  store (it needs `commits.pr_number` for `#<pr or ->`): a positional `<repo>` and `--data`, or
  a `002_*.sql` that records the repository at ingest (plan-auditor F1).
- **Hand-off** H05.3 → Day 6: the root and direct commits change structure but are not merges
  (the kit's `5507876` adds 18 `.py` files); say whether they are the baseline with no line,
  or get lines that Phase 4's step count leaves out. And the event rules after a paired rename
  (`renamed scripts.helpers -> scripts.tools` at #8: are its import edges also `+import` and
  `-import` lines; do events name modules or paths?) and the `cycle+` rotation (plan-auditor
  F5, F6). Day 2's Out of scope ("every diff is `merge^1..merge`", D02.6) comes with it.
- **Hand-off** H05.4 → Day 6: the blob cache stores `parse_imports`'s result and the line
  count by blob SHA, never resolved edges (a renamed blob is a hit: `scripts/helpers.py` at
  `00394fb` and `scripts/tools.py` at `main` are one blob, `935a04d`); and `cache hits N` equal
  to the first run's `blobs parsed` holds only if a hit is counted once per distinct blob per
  run: 160 `.py` lookups on the fixture's first-parent line, 28 distinct blobs (plan-auditor F4).
- **Hand-off** H05.5 → Day 7: H01.1, re-pointed: `grew` fires when a module crosses 200 lines,
  not while it stays above (`app.core` goes 13 → 253 at #6, then 253 → 257 at #9).
- **Hand-off** H05.6 → Day 7: the module map in `bearing.toml` (plan.md, "Import resolution"),
  and where `bearing.toml` is read from, since the target is read-only and Phase 3 reads its
  areas from the same file; if the kit's and wordtally's histories need no map, a plan-change PR
  may cut it. And name the kit's and wordtally's SHAs in Day 7's quoted lines: the kit's `main`
  is past `44d7a55` (plan-auditor F8).
