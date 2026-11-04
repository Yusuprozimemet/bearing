# Day 06 — `bearing timeline`: what each merge changed in the structure, with a blob cache

**Phase:** 2 · **Depends on:** Day 5 · **Expected PRs:** 5 (this spec, tracks A, B and C, the close)

## Goal
`bearing timeline <repo>` prints, for each merge of the stored history, one line per structure
event between the merge's first parent and the merge (a module added, removed or renamed, an
import edge added or removed), reading each file version once across runs through a blob cache
in the store, and `--stats` reports the cache's work; on the fixture it prints the 18 lines of
"What the fixture gives".

## In scope
- H05.2, decided: `bearing timeline <repo> [--data DIR] [--stats]`, `<repo>` positional as for
  `ingest` and `snapshot`, `--data` defaulting to `.bearing`. The merges and their PR numbers
  come from the store `bearing ingest` wrote (`commits`, `kind = 'merge'`, in `position`
  order); the store records no repository, and none is added.
- H05.3, decided: only merges get lines, so Phase 4's step count stays `ingest`'s `merges`.
  Each merge is diffed against its first parent (`<sha>^1`, plan.md's "every diff is
  `merge^1..merge`", Day 2's Out of scope); a squash merge has one parent and is diffed the
  same way. The root commit and direct commits get no line: their changes are in the first
  parent of the next merge, the baseline it is compared with. Events name modules (dotted
  names), not paths. A rename pairs the two modules, and the edges are compared after the old
  name is replaced by the new one, so a pure rename is one `renamed` line and no `+import` or
  `-import` lines (#8 in the fixture: `renamed scripts.helpers -> scripts.tools` only).
- `bearing/snapshot/diff.py` (Track A), pure, no git: `structure_events(old, new, renames)`.
  `old` and `new` are `snapshot-v1` `dict`s (only `"modules"` and `"imports"` are read);
  `renames` is a list of `(old_path, new_path)` pairs. A pair is a module rename when
  `old_path` is a module's path in `old`, `new_path` a module's path in `new`, the two names
  differ, the old name is not a name in `new`, and the new name is not a name in `old`; any
  other pair is ignored. It returns a list of strings, in this order, each group sorted:
  `+module <name>` for each name in `new` not in `old` and not a rename's new name;
  `-module <name>` for each name in `old` not in `new` and not a rename's old name;
  `renamed <old> -> <new>`, sorted by the old name; `+import <a> -> <b>` for each edge of
  `new` not among `old`'s edges after renaming; `-import <a> -> <b>` for each of `old`'s edges
  after renaming not in `new`. "After renaming": each name of an `old` edge that is a rename's
  old name is replaced by its new name. A module whose path changes but whose name does not is
  no event. This is plan.md's event order without Day 7's `cycle+`, `cycle-` and `grew`.
- The blob cache (Track B), H05.4:
  - `bearing/migrations/002_blobs.sql`: `CREATE TABLE blobs (sha TEXT PRIMARY KEY, lines
    INTEGER NOT NULL, imports TEXT NULL)`; `imports` is `parse_imports`'s result as JSON
    (`json.dumps` of the list of `[level, module, [names]]`), `NULL` for a parse error. It
    stores no path and no resolved edge, so a blob is a hit whatever path it has
    (`scripts/helpers.py` at `00394fb` and `scripts/tools.py` at `main` are one blob,
    `935a04d`). `save` keeps replacing `commits` and `prs` only, so a second `ingest` keeps
    the cache.
  - `bearing/snapshot/cache.py`: `BlobCache(conn)`, `conn` a store from `open_store`. Its
    `get(sha, read)` returns `(lines, imports)`, `imports` as `parse_imports` returns it (a
    sorted list of `(level, module, names)` tuples, `names` a tuple, or `None`). On a `sha` not
    in `blobs` it calls `read()` for the bytes, computes both with `count_lines` and
    `parse_imports`, and inserts the row; it never calls `read()` for a `sha` in `blobs`. It
    commits nothing: its caller does. Its `parsed` and `hits` count distinct blobs over the
    object's life: a `sha` first asked for that is not in `blobs` adds 1 to `parsed`, one that
    is adds 1 to `hits`, and a `sha` asked for again adds nothing. So a second run over the
    same history gives `parsed` 0 and `hits` equal to the first run's `parsed` (plan.md,
    Phase 2's "Done when").
  - `bearing/snapshot/tree.py`: `snapshot(repo, ref, cache=None)`. With no cache it runs as on
    Day 5. With one, for each path that is a module it calls `cache.get(blob sha, read)`,
    `read` running `git cat-file blob`, and runs no `cat-file` for a path that is not a
    module; the result equals the uncached one.
- `bearing timeline` (Track C):
  - `renamed_paths(repo, old_sha, new_sha)` in `tree.py`: runs, read-only,
    `git -C <repo> diff --no-ext-diff -M --name-status -z <old_sha> <new_sha>` and returns the
    sorted `(old_path, new_path)` pairs of its `R` entries (an `R` or `C` entry carries two
    paths, every other one path; `C` entries are skipped). Paths are decoded as in `snapshot`.
    A failure raises `SnapshotError` with git's stderr.
  - `bearing/snapshot/timeline.py`: `timeline(repo, conn, cache)` returns the lines: for each
    row of `SELECT sha, pr_number FROM commits WHERE kind = 'merge' ORDER BY position`, it
    takes `snapshot(repo, sha, cache)` and then `snapshot(repo, sha + "^1", cache)` (in that
    order, so a store from another repository fails on the merge's own SHA), then
    `structure_events` with `renamed_paths` between the two `"ref"`s, and gives each event the
    line `<sha7> #<pr_number> <event>`, `#-` when `pr_number` is `NULL` (never the subject's
    number: plan.md's "never guessed"). A merge with no event gives no line.
  - In `bearing/cli.py`: when `<data>/bearing.db` is not a file, "no store at <that path>:
    run bearing ingest first", as `changelog` says it, and nothing is created. Otherwise
    `open_store(<data>)` (which applies `002_blobs.sql` to a Day 5 store), the lines on
    stdout, one per line, then `conn.commit()`; with `--stats`, after the lines, the line
    `blobs parsed <cache.parsed>  cache hits <cache.hits>` (two spaces, as the ingest line) on
    stderr, so stdout stays the timeline. Exit 0. An error is `bearing: <message>` on stderr,
    nothing on stdout, exit 1: `SnapshotError`'s message, or "cannot read store at <db>:
    <error>" for a `sqlite3.Error`.
- Tests: `tests/test_diff.py` (Track A); `tests/test_blob_cache.py` and the edited
  `tests/test_store.py` (Track B); `tests/test_timeline_cli.py` (Track C). As on Days 2 to 5:
  every test class subclasses `unittest.TestCase`, imports the module under test inside the
  test method (`from bearing.snapshot.diff import structure_events`, `from
  bearing.snapshot.cache import BlobCache`), builds the fixture with `make_repo.py` as a
  subprocess once per class where it needs one, and runs `python -m bearing` with `cwd=` the
  repository root and `GIT_DIR` and `GIT_WORK_TREE` removed from the environment it passes.
  Output is read with `\r\n` as `\n`.

### What the fixture gives

Run in this spec's prototype on 2026-11-04 on `9ecc9d1`: the rules above, written as a script
over Day 5's `snapshot`, on the fixture after
`bearing ingest <dir>/repo --prs <dir>/prs.json`.

- The 18 lines of `bearing timeline`, in this order:

  ```
  62c4b2f #1 +module app.sub
  62c4b2f #1 +module app.sub.mod
  62c4b2f #1 +import app.sub.mod -> app.core
  62c4b2f #1 +import app.sub.mod -> app.pkg
  1756282 #2 +module scripts.run
  1756282 #2 +import scripts.helpers -> scripts.config
  1756282 #2 +import scripts.run -> scripts.helpers
  00394fb #3 +module app.a
  00394fb #3 +module app.b
  00394fb #3 +module app.crlf
  00394fb #3 +import app.a -> app.b
  00394fb #3 +import app.b -> app.a
  448fc4d #6 +module app.broken
  fde93a4 #8 +module app.extra
  fde93a4 #8 -module app.legacy
  fde93a4 #8 renamed scripts.helpers -> scripts.tools
  e5fa51f #9 +module tests.contract.test_api
  e5fa51f #9 -import app.b -> app.a
  ```

  `4a6b109` (#4), `bd726c8` (#5, a typo fix in `scripts/run.py`), `86761f2` (#10) and
  `8c1b9f1` (no record) change no structure and print nothing; the root `3a28fe5` and the
  direct `c437100` are not merges. `git diff -M` reports #8's move as `R100
  scripts/helpers.py scripts/tools.py`. Without the rename rule, #8 would print four import
  lines more (`+import scripts.run -> scripts.tools`, `+import scripts.tools -> scripts.config`
  and their two `-import`s) and `+module`/`-module` instead of `renamed`.
- Blobs: the 20 snapshots (each merge and its first parent) ask for 268 module blobs, 28
  distinct; so the first `--stats` run prints `blobs parsed 28  cache hits 0`, the second
  `blobs parsed 0  cache hits 28`. At `448fc4d` the 15 modules are 15 distinct blobs; at
  `main` the 16 are 16, and the two commits together hold 21.
- The first merge's full SHA is `62c4b2fcda436266c9cdd7ec8db866427452cfb9`.
- Day 7 adds `cycle+` at #3 and `cycle-` at #9 (the `app.a`/`app.b` cycle) and `grew app.core`
  at #6 (13 → 253 lines), and writes the timeline's golden file with them.

## Out of scope
- `cycle+`, `cycle-`, `grew`, the timeline's golden file and contract test, and the kit's and
  wordtally's runs — Day 7 (H05.5, H06.1). A golden file written today would hold 18 lines
  that Day 7 must change, an edit of `tests/contract/`.
- The module map in `bearing.toml` — Day 7 (H05.6).
- `bearing snapshot` with the cache: it opens no store and takes no `--data`, as on Day 5.
- Two paths with one name (Day 5's Out of scope), and a rename whose two names are both
  present on both sides: no `renamed` line, the plain `+module`/`-module` rules apply.
- An empty store (ingested, no merge): prints nothing, exits 0; decided, not tested.
- Cache rows for blobs no history uses any more: never deleted; the cache is keyed by content.

## Tracks

| Track | Owner | Work |
|---|---|---|
| A | implementer | C06.1: `bearing/snapshot/diff.py` and `tests/test_diff.py` |
| B | implementer | C06.2–C06.4, C06.10: `002_blobs.sql`, `bearing/snapshot/cache.py`, `snapshot`'s `cache`, `tests/test_blob_cache.py`, `tests/test_store.py` |
| C | implementer | C06.5–C06.8: `renamed_paths`, `bearing/snapshot/timeline.py`, `bearing timeline` in `bearing/cli.py`, `tests/test_timeline_cli.py` |

A and B are independent; C uses both and lands last. Each track's `new` tests are red on its
own base, as CI's "Track tests seen red" requires: A's and B's because their modules are not
there (and C06.4 on the migration list), C's because the subcommand is not. No Track 0: the
tests that hold through the day (Day 5's, and the contract tests) exist. C06.9 is `hold` and
owned by this spec's PR, which ran its check first; C06.10 is `hold` and broken in Track B,
the track that changes `snapshot`.

## Acceptance criteria
Tick each box in the closing PR once its evidence is in it; under a box left unticked, write
`Not proven: <why>` (`specs/README.md`, "Evidence at the close").
- [x] C06.1 **new** — `structure_events(old, new, renames)` on snapshots written in the test:
      `old` with the modules `app` `app/__init__.py`, `app.b` `app/b.py`, `app.c` `app/c.py`,
      `app.old` `app/old.py`, `scripts.helpers` `scripts/helpers.py`, `scripts.run`
      `scripts/run.py` and the imports `[["app", "app.b"], ["app.b", "app.c"], ["app.c",
      "app.old"], ["scripts.helpers", "app.b"], ["scripts.run", "scripts.helpers"]]`; `new`
      with `app` `app/__init__.py`,
      `app.c` `src/app/c.py`, `app.new` `app/new.py`, `scripts.run` `scripts/run.py`,
      `scripts.tools` `scripts/tools.py` and `[["app", "app.c"], ["app.c", "app.new"],
      ["scripts.run", "scripts.tools"], ["scripts.tools", "app.c"]]`; `renames`
      `[("scripts/helpers.py", "scripts/tools.py"), ("app/c.py", "src/app/c.py"),
      ("docs/old.md", "app/new.py"), ("app/old.py", "scripts/run.py"), ("app/__init__.py",
      "app/new.py")]`. It returns exactly `["+module app.new", "-module app.b",
      "-module app.old", "renamed scripts.helpers -> scripts.tools", "+import app -> app.c",
      "+import app.c -> app.new", "+import scripts.tools -> app.c", "-import app -> app.b",
      "-import app.b -> app.c", "-import app.c -> app.old", "-import scripts.tools ->
      app.b"]`, and the same with `renames` in reverse order. That is: the edge
      `scripts.run -> scripts.helpers` carried over by the rename is no event; an edge the
      renamed module lost is named by its new name (`scripts.tools -> app.b`, not
      `scripts.helpers -> app.b`); the moved `app.c` (same name) is none; the pair from a
      non-Python path is an add; a pair whose new name was already in `old`
      (`app.old` → `scripts.run`) and one whose old name is still in `new` (`app` →
      `app.new`) are no renames. And `structure_events(old, old, [])` returns `[]`. Red today:
      "No module named 'bearing.snapshot.diff'".
      Test: `tests/test_diff.py::StructureEventsTest::test_events`
      Evidence: `StructureEventsTest.test_events` (#40), seen red first on `1e7a4c5`'s code
      with "No module named 'bearing.snapshot.diff'"; `python -m pytest -q` (#40).
      broken: structure_events renaming a module whose old name is still in new → 1 failed in 0.08s (#40)
      broken: structure_events renaming to a name already in old → 1 failed in 0.07s (#40)
      broken: structure_events comparing old edges without renaming → 1 failed in 0.08s (#40)
      broken: structure_events listing a rename's new name as +module → 1 failed in 0.07s (#40)
- [x] C06.2 **new** — `BlobCache` round trip, on a store `open_store` made in a temporary
      directory: `get("a" * 40, read)`, `read` returning `b"import b\nfrom . import c\n"`,
      returns `(2, [(0, "b", ()), (1, "", ("c",))])`, and `parsed` is 1, `hits` 0; asked again
      with a `read` that raises, it returns the same and the counts stay; `get("b" * 40, read)`
      with `b"def f(:\n"` returns `(1, None)`. After `conn.commit()`, a new `BlobCache` on a new
      connection to the same file returns both again (tuples, not lists), with a `read` that
      raises, and has `parsed` 0, `hits` 2. Red today: "No module named
      'bearing.snapshot.cache'".
      Test: `tests/test_blob_cache.py::BlobCacheTest::test_round_trip`
      Evidence: `BlobCacheTest.test_round_trip` (#41), seen red first on `bbd43ed`'s code with
      "No module named 'bearing.snapshot.cache'"; `python -m pytest -q` (#41).
      broken: cached imports come back with names as lists → 1 failed in 0.18s (#41)
- [x] C06.3 **new** — on the fixture, with a `BlobCache` on a fresh store:
      `snapshot(repo, "448fc4dc915289f0b3f0254cf80360b56f48513a", cache)` equals the uncached
      `snapshot` at that SHA, with `parsed` 15 and `hits` 0; then `snapshot(repo, "main",
      cache)` equals the uncached one at `main`, with `parsed` 21 and `hits` 0; after
      `conn.commit()`, a new `BlobCache` on the same store gives `snapshot(repo, "main", ...)`
      equal again, with `parsed` 0 and `hits` 16. Red today: as C06.2.
      Test: `tests/test_blob_cache.py::SnapshotCacheTest::test_counts`
      Evidence: `SnapshotCacheTest.test_counts` (#41), seen red first on `bbd43ed`'s code as
      C06.2; `python -m pytest -q` (#41).
      broken: a cache hit is not counted → 1 failed in 8.72s (#41)
- [x] C06.4 **new** — `open_store` and `save` run twice on the fixture into one data
      directory: after each, the counts of C02.6 hold and `schema_migrations` holds exactly
      `001_history.sql` and `002_blobs.sql`, in that order; and a row inserted into `blobs`
      between the two runs is still there after the second `save`. Red today: the migration
      list is `[('001_history.sql',)]`, and the insert into `blobs` errors with "no such
      table: blobs".
      Test: `tests/test_store.py::StoreTest::test_stored_once`
      Replaces: C02.6 — was: "`schema_migrations` holds exactly `001_history.sql`".
      Evidence: `StoreTest.test_stored_once` (#41), seen red first on `bbd43ed`'s code with
      "[('001_history.sql',)] != [('001_history.sql',), ('002_blobs.sql',)]"; the insert's
      "no such table: blobs" is never reached there (D06.8); `python -m pytest -q` (#41).
      broken: save also empties blobs → 1 failed, 1 passed, 1 subtests passed in 7.05s (#41)
- [x] C06.5 **new** — after `python -m bearing ingest <dir>/repo --prs <dir>/prs.json --data
      <tmp>`, `python -m bearing timeline <dir>/repo --data <tmp>` exits 0, stderr is empty, and
      stdout is exactly the 18 lines of "What the fixture gives", each ending in a newline. With
      the store's `pr_number` set to `NULL` for `fde93a4` by the test, in a second data
      directory, #8's three lines read `fde93a4 #- +module app.extra`, `fde93a4 #- -module
      app.legacy` and `fde93a4 #- renamed scripts.helpers -> scripts.tools`, the other 15
      unchanged. Red today: argparse's "invalid choice: 'timeline'" (exit 2).
      Test: `tests/test_timeline_cli.py::TimelineCliTest::test_lines`
      Evidence: `TimelineCliTest.test_lines` (#42), seen red first on `5cd202c`'s code with
      "invalid choice: 'timeline'" (exit 2); `python -m pytest -q` (#42).
      broken: timeline.py: #- for a NULL pr_number → 1 failed in 10.07s (#42)
      broken: tree.py: renamed_paths returns no pair → 1 failed in 8.25s (#42)
- [x] C06.6 **new** — `--stats`, on a fresh ingest: the first `python -m bearing timeline
      <dir>/repo --data <tmp> --stats` exits 0 with the 18 lines on stdout and stderr exactly
      "blobs parsed 28  cache hits 0\n"; the second, "blobs parsed 0  cache hits 28\n"; and
      after the same `ingest` is run again into `<tmp>`, a third, "blobs parsed 0  cache hits
      28\n" (an ingest keeps the cache). Red today: as C06.5.
      Test: `tests/test_timeline_cli.py::TimelineCliTest::test_stats`
      Evidence: `TimelineCliTest.test_stats` (#42), seen red first on `5cd202c`'s code as
      C06.5; `python -m pytest -q` (#42).
      broken: cli.py: the cache is not committed → 1 failed in 10.67s (#42)
- [x] C06.7 **new** — errors, each exit 1, stdout empty, stderr exactly as given:
      `python -m bearing timeline <dir>/repo --data <empty>`, `<empty>` an empty directory,
      gives "bearing: no store at <empty>/bearing.db: run bearing ingest first\n" (the path as
      `str(Path(<empty>) / "bearing.db")`) and `<empty>` stays empty; with an ingested store,
      `python -m bearing timeline <tmp> --data <store>`, `<tmp>` an empty directory, gives
      "bearing: not a git repository: <tmp>\n"; and with `<other>` a repository made by
      `git init` in the test, "bearing: not a commit:
      62c4b2fcda436266c9cdd7ec8db866427452cfb9\n"; and with `<bad>/bearing.db` a file the test
      writes as `b"not a store\n"`, stderr is exactly "bearing: cannot read store at
      <bad>/bearing.db: file is not a database\n" (the path as above): `open_store` raises
      that `sqlite3.DatabaseError`, so it lies inside the `try`. Red today: as C06.5.
      Test: `tests/test_timeline_cli.py::TimelineCliTest::test_errors`
      Evidence: `TimelineCliTest.test_errors` (#42), seen red first on `5cd202c`'s code as
      C06.5; `python -m pytest -q` (#42).
      broken: timeline.py: the parent snapshot taken first → 1 failed, 1 passed, 3 subtests passed in 6.35s (#42)
- [x] C06.8 **new** — the target is read-only (plan.md, "Decisions"): after the C06.5 and
      C06.6 commands, which the test runs itself (track-red runs each test alone),
      `<dir>/repo`'s `git status --porcelain --ignored` prints nothing, and
      `git for-each-ref` and `git rev-parse HEAD` print what they printed before them. Red
      today: the commands exit 2, so the test fails on their exit code.
      Test: `tests/test_timeline_cli.py::TimelineCliTest::test_read_only`
      Evidence: `TimelineCliTest.test_read_only` (#42), seen red first on `5cd202c`'s code,
      failing on the commands' exit code 2; `python -m pytest -q` (#42).
      broken: tree.py: snapshot writes a ref → 1 failed in 5.63s (#42)
- [x] C06.9 **hold** — the frozen files stay as Day 5 left them: the fixture, the contract tests
      and their golden files, the applied migration, and C06.10's two snapshot tests:
      `git -c core.safecrlf=false diff --exit-code 9ecc9d1 -- tests/contract/ tests/fixtures/make_repo.py tests/fixtures/expected/ bearing/migrations/001_history.sql tests/test_snapshot_tree.py tests/test_snapshot_cli.py`
      prints nothing and exits 0. The directories are named whole: the day adds no file to
      them.
      Evidence: the command above, exit 0 in #39, #41 and #42 and on `21251d3` at the close; CI's
      "Frozen files stay unedited" on #39–#42.
      broken: the applied migration 001_history.sql edited → committed_at TEXT NOT NULL, (#39)
- [x] C06.10 **hold** — `bearing snapshot` is unchanged by the cache:
      `python -m pytest -q tests/contract/test_snapshot.py tests/test_snapshot_tree.py
      tests/test_snapshot_cli.py` passes on every track's head; C06.9 checks the three files
      are unedited. Track B, which changes `snapshot`, breaks the uncached path once and
      records what it reported.
      Evidence: the three files inside `python -m pytest -q`, and CI's "Tests", on the heads of
      #40 (`a51818b`), #41 (`3d49318`) and #42 (`100e75e`), and on `21251d3` at the close.
      broken: the uncached snapshot counts one line more per module → 3 failed, 2 passed, 2 subtests passed in 19.69s (#41)

## Verify
```bash
python -m pytest -q
python tests/fixtures/make_repo.py .bearing/day06-check
python -m bearing ingest .bearing/day06-check/repo --prs .bearing/day06-check/prs.json --data .bearing/day06-check/data
python -m bearing timeline .bearing/day06-check/repo --data .bearing/day06-check/data --stats
python -m bearing timeline .bearing/day06-check/repo --data .bearing/day06-check/data --stats
git -c core.safecrlf=false diff --exit-code 9ecc9d1 -- tests/contract/ tests/fixtures/make_repo.py tests/fixtures/expected/ bearing/migrations/001_history.sql tests/test_snapshot_tree.py tests/test_snapshot_cli.py
```

## Notes
- Not the first day of Phase 2, so no plan-auditor run; the spec-auditor runs on this spec
  before its PR (CLAUDE.md, step 1).
- Choices, each a choice and not evidence: `--stats` on stderr, so a redirected timeline holds
  only the timeline; the rename rule maps edges through the rename, because the reader of a
  timeline wants to see a move as one move; `#-` for a merge with no record, though its
  subject names a number, since that number was never matched to a record.
- The merge's own snapshot is taken before its first parent's, so a store from another
  repository fails with the merge's full SHA, which C06.7 pins; `<sha>^1` in an error message
  would be less clear.
- Speed is not a criterion: two `ls-tree`s and one `diff` per merge stay. Day 7's runs on the
  kit and wordtally show whether they matter.
- Sizes, estimated: Track A about 50 lines of code and 70 of test; Track B about 80 and 120;
  Track C about 100 and 200. Each under 400.
- The count: 47 tests pass today ("47 passed, 47 subtests passed" on `9ecc9d1`); the day adds 7
  test methods (`test_diff.py` 1, `test_blob_cache.py` 2, `test_timeline_cli.py` 4) and edits
  one, so `pytest -q` ends at "54 passed" (subtests besides).
- The stderr of C06.6 and C06.7 is written in text mode, so on Windows it ends in `\r\n`; the
  tests read `\r\n` as `\n`, as Day 5's did.
- Verify's `make_repo.py .bearing/day06-check` refuses a directory that is not empty: delete it
  before a second local run.
- Known limits, stated in In scope and checked by no criterion (spec-auditor finding 5):
  nothing on stdout after an error part-way through the history (`timeline` returns the lines
  before the command prints any, which a reader checks in Track C's diff); the cache is not
  committed after an error; no `cat-file` for a `.py` path that is not a module (the fixture
  has none); `renamed_paths`' error and its `C`-entry skip (`-M` alone never gives `C`); a
  parse error stored as SQL `NULL`, not the JSON text `null` (C06.2 reads it back as `None`
  either way).
- **Defect** D06.1 — found: auditor · cause: spec · made: Day 06 · C06.1 had no renamed module
  that loses an edge, so naming the lost edge by the old name passed it; it now has
  `scripts.helpers -> app.b`.
- **Defect** D06.2 — found: auditor · cause: spec · made: Day 06 · C06.1 tested neither
  "the old name is not a name in `new`" nor "the new name is not a name in `old`"; two pairs
  now break one each.
- **Defect** D06.3 — found: auditor · cause: spec · made: Day 06 · "cannot read store at" had no
  criterion, and `open_store` raises before any read; C06.7 now has a corrupt store.
- **Defect** D06.4 — found: auditor · cause: spec · made: Day 06 · C06.10 said "unedited" with
  no check of the two snapshot tests outside `tests/contract/`; C06.9's diff now names them.
- **Defect** D06.5 — found: break on purpose · cause: spec · made: Day 06 · the rename rule
  listed "the two names differ" as a condition of its own, but "the old name is not a name in
  `new`" already implies it. The implementer's draft gave it a line of its own, and a break
  that removed that line reported "The check passed with the break in" (1 passed in 0.03s).
  No test can catch the line, so #40 removed it, with the reason in a comment.
- **Defect** D06.6 — found: break on purpose · cause: process · made: Day 06 · Track B's first
  break of the tuple decode turned the rows into lists inside the comprehension, and the outer
  `tuple(names)` turned them back. `break.py` reported "The check passed with the break in".
  The break was wrong, not the test. The recorded break removes `tuple(...)` itself, and the
  failed run is not in the manifest (#41).
- **Defect** D06.7 — found: self · cause: process · made: Day 06 · a hand-run red check in
  Track B used `git stash push -- bearing/`, which stashed `tree.py` only. The untracked
  `cache.py` and `002_blobs.sql` stayed in place, so the run mixed old and new code ("1
  failed, 2 passed"). #41 discarded that run and used `seen-red.py` instead, as CLAUDE.md
  advises.
- **Defect** D06.8 — found: Track B · cause: spec · made: Day 06 · same-as: D05.10 · C06.4's
  red gave two reasons, but only the first comes from a run. Track B's red run, before #41
  merged, showed it: on `bbd43ed`'s code, the
  migration-list assertion fails first, so the insert's "no such table: blobs" is never
  reached. #41's break "save also empties blobs" covers the insert half. Like D05.10, this
  red text was reasoned out, not run.
- Not covered, from #40: two qualifying pairs that share a name (one old path to two new
  paths). The events are the same in any order, because the pairs are sorted, but the edge
  mapping takes the last pair for that name. `renamed_paths` never gives that case: git's `-M`
  gives one `R` entry per path.
- At the close, on `21251d3`: `python -m pytest -q` gave "54 passed, 51 subtests passed", the
  count above. Verify's two `timeline --stats` runs each exited 0 with the same 18 lines; stderr
  was "blobs parsed 28  cache hits 0", then "blobs parsed 0  cache hits 28". C06.9's diff
  exited 0. All 14 `manifest:` lines parsed as JSON (1 in #39, 4 in #40, 4 in #41, 5 in #42),
  and each `find` occurs once in the merged code. I replayed each with `scripts/break.py` in an
  LF worktree of `main`, and each failed its check. I also ran `main`'s new tests on each
  track's base code (`1e7a4c5`, `bbd43ed`, `5cd202c`). Each red matched the spec's text,
  except C06.4's second reason (D06.8). Every criterion already had a break from a track or
  the spec PR, so the close ran no break of its own.
- The blind relabel at the close agreed on 7 of 8 stages, 8 of 8 causes and 8 of 8 `made:`.
  On D06.8 the rater answered "unclear" for the stage, with low confidence, because the text
  did not say when the defect was found. It keeps `found: Track B`, since #41's red run found
  it before the merge, and its text now says so. The rater also marked D06.8 as mixed, with a
  process side, because the red text was not run. It keeps `spec`: the wrong claim is in the
  criterion.
- **Hand-off** H06.1 → Day 7: the `cycle+` line's rotation (plan-auditor F6 on Day 5, carried
  by H05.3): which module a cycle's line starts from, so it is the same on every run; and
  whether `cycle+`/`cycle-` compare cycles after the rename rule, as `structure_events` does
  edges.
