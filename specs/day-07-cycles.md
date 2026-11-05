# Day 07 — `cycle+`, `cycle-` and `grew` in the timeline, and its golden file

**Phase:** 2 · **Depends on:** Day 6 · **Expected PRs:** 3 (this spec with its plan change, track A, the close)

## Goal
`bearing timeline` also reports each import cycle a merge introduces or breaks and each module
that grows past 200 lines in it, so on the fixture it prints the 21 lines of "What the fixture
gives", which become the timeline's golden file and contract test; and on the kit's and
wordtally's full histories it exits 0, with a second `--stats` run that parses nothing.

## In scope
- H06.1, decided: a cycle is an elementary cycle of the snapshot's import graph: a sequence of
  distinct modules, each importing the next and the last importing the first. Its line starts
  at its least name in Python's string order and follows the edges from there:
  `cycle+ a > b > c > a`, the first name repeated at the end, as in plan.md's format. Two cycles
  through the same modules in a different order are two cycles. Cycles are compared after the
  rename rule, as `structure_events` compares edges: each name of an `old` cycle that is a
  rename's old name is replaced by its new name, and the cycle is started again at its least
  name. So a rename inside a cycle gives no `cycle+` or `cycle-` line, and a `cycle-` line
  names a renamed module by its new name, as a `-import` line does.
- H05.5, decided: `grew <name> <lines>` for each module of `new` with more than 200 lines whose
  name, or for a rename's new name the old name, is a module of `old` with 200 lines or fewer.
  `<lines>` is the module's line count in `new`. So it fires when a module crosses 200 lines,
  not while it stays above (`app.core`: 13 → 253 at #6 fires, 253 → 257 at #9 does not). A
  module added with more than 200 lines gives `+module` and no `grew`. The size is a constant
  in `diff.py`, 200: Phase 2 reads no configuration.
- `structure_events(old, new, renames)` in `bearing/snapshot/diff.py` returns the three new
  groups after Day 6's five, each sorted as printed: `cycle+ <cycle>` for each cycle of `new`
  not among `old`'s cycles after renaming; `cycle- <cycle>` for each of `old`'s cycles after
  renaming not among `new`'s; `grew <name> <lines>`. Its signature, its first five groups and
  `timeline.py` do not change: `timeline` prints what `structure_events` returns. `"lines"` is
  read from the modules of both snapshots, as `snapshot-v1` gives it.
- The timeline's golden file, `tests/fixtures/expected/timeline.txt`: the 21 lines below, each
  ending in `\n`. Its contract test, `tests/contract/test_timeline.py`, builds the fixture with
  `make_repo.py`, runs `python -m bearing ingest <dir>/repo --prs <dir>/prs.json --data <tmp>`
  then `python -m bearing timeline <dir>/repo --data <tmp>`, and compares stdout's bytes with
  the golden file's, `\r\n` read as `\n` on both sides, as `tests/contract/test_snapshot.py`
  does. Both files are added; no file in `tests/contract/` or `tests/fixtures/expected/` is
  edited.
- `tests/test_timeline_cli.py`'s `LINES` gains the three new lines, so C06.5 and C06.6 expect
  21 lines (C07.3).
- H05.6, decided by the maintainer: the module map in `bearing.toml` is cut. This spec's PR
  edits plan.md ("Course corrections", "2026-11-04: Course correction on Day 7: no module
  map"), with the counts that show neither target history needs it. Where `bearing.toml` is
  read from goes to Day 8 (H07.1).
- The kit's and wordtally's runs (plan.md, Phase 2's "Done when"), with the SHAs named (H05.6,
  plan-auditor F8 on Day 5): the clones beside this repository, `../agentic-workflow-kit` and
  `../wordtally`, at their `main`. The close quotes the two `--stats` lines of each, under the
  full SHA of the `main` it ran on.
- Tests: the new method in `tests/test_diff.py`, the new `tests/contract/test_timeline.py`, and
  the edited `LINES` in `tests/test_timeline_cli.py`. As on Days 2 to 6: every test class
  subclasses `unittest.TestCase`, imports the module under test inside the test method, builds
  the fixture with `make_repo.py` as a subprocess once per class where it needs one, and runs
  `python -m bearing` with `cwd=` the repository root and `GIT_DIR` and `GIT_WORK_TREE`
  removed from the environment it passes.

### What the fixture gives

Run in this spec's prototype on 2026-11-04 on `8abee85`: the rules above, written as a script
over Day 6's `structure_events`, `snapshot` and `renamed_paths`, on the fixture after
`bearing ingest <dir>/repo --prs <dir>/prs.json`.

- The 21 lines of `bearing timeline`, in this order: Day 6's 18, with lines 13, 15 and 21 new.

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
  00394fb #3 cycle+ app.a > app.b > app.a
  448fc4d #6 +module app.broken
  448fc4d #6 grew app.core 253
  fde93a4 #8 +module app.extra
  fde93a4 #8 -module app.legacy
  fde93a4 #8 renamed scripts.helpers -> scripts.tools
  e5fa51f #9 +module tests.contract.test_api
  e5fa51f #9 -import app.b -> app.a
  e5fa51f #9 cycle- app.a > app.b > app.a
  ```

  `app.core` has 5 lines at the root `3a28fe5`, 13 before #6, 253 at `448fc4d` (#6) and 257 at
  `e5fa51f` (#9) and `main`; only #6 crosses 200.

### What the kit and wordtally give

The same prototype, run on 2026-11-04, after `bearing ingest` (PR records from `gh`):

- The kit at `c12cfe55018aebe82de83485460f1edd22e4c96b` (#95): "merges 94  matched 94  unmatched
  merges 0  unmatched PRs 0  direct 11"; Day 6's `timeline` prints 36 lines, and the rules
  above add 6 `grew` lines and no `cycle` line, 42 in all. `timeline --stats` exited 0 twice,
  stderr "blobs parsed 204  cache hits 0", then "blobs parsed 0  cache hits 204" (29 s, then
  19 s).
- wordtally at `e1d15e9bbe5067bf4b0cc67f0bb65f7cf52f5dab` (#56): "merges 56  matched 56
  unmatched merges 0  unmatched PRs 0  direct 1"; 24 lines, plus 5 `grew` and no `cycle`, 29
  in all. Stderr "blobs parsed 94  cache hits 0", then "blobs parsed 0  cache hits 94" (15 s,
  then 11 s).
- Neither history has an import cycle at any merge, so only the fixture and C07.1 test the
  cycle rules.

## Out of scope
- The module map in `bearing.toml`: cut (In scope, H05.6). Where `bearing.toml` is read from —
  Day 8 (H07.1).
- A configurable `grew` size: it would need `bearing.toml`, which Phase 2 does not read.
- A cycle through a self-import: `import_edges` drops an edge from a module to itself
  (`target != importer`), so the graph has none.
- Speed: Day 6's two `ls-tree`s and one `diff` per merge stay; the runs above take under 30 s.
- A golden file per snapshot: Phase 2's "Done when" said "snapshots", and Day 5 wrote one,
  `snapshot-448fc4d.json`. This spec's plan change makes "Done when" name that one.

## Tracks

| Track | Owner | Work |
|---|---|---|
| A | implementer | C07.1–C07.3: the three groups in `bearing/snapshot/diff.py`, `tests/test_diff.py`, `tests/fixtures/expected/timeline.txt`, `tests/contract/test_timeline.py`, `LINES` in `tests/test_timeline_cli.py` |

One track: the contract test and the CLI tests are red only on the code before the change, so
they land with it, as CI's "Track tests seen red" requires. No Track 0: the tests that hold
through the day (Days 1 to 6, the contract tests among them) exist. C07.4 and C07.5 are `hold`
and owned by this spec's PR, which ran C07.5's check and break first; C07.4's check runs at the
close.

## Acceptance criteria
Tick each box in the closing PR once its evidence is in it; under a box left unticked, write
`Not proven: <why>` (`specs/README.md`, "Evidence at the close").
- [x] C07.1 **new** — `structure_events(old, new, renames)` on snapshots written in the test,
      each module `{"name": <name>, "path": "<name>.py", "lines": <n>, "parse_error": False}`:
      `old` with `a`, `b`, `c`, `d`, `e`, `m`, `x`, `y`, `z` at 10 lines, `g1` at 200, `g2`
      at 199, `g3` at 201, `g4` at 150, and the imports `[["a", "b"], ["d", "e"], ["e", "d"],
      ["m", "z"], ["z", "m"], ["x", "y"], ["y", "x"]]`; `new` with `a`, `b`, `c`, `d`, `e`,
      `m`, `k`, `x`, `w` at 10 lines, `g1` at 201, `g2` at 200, `g3` at 300, `g5` at 250,
      `big` at 500, and the imports `[["c", "a"], ["a", "b"], ["b", "a"], ["b", "c"], ["d",
      "e"], ["k", "m"], ["m", "k"]]`; `renames` `[("z.py", "k.py"), ("g4.py", "g5.py"),
      ("y.py", "w.py")]`. It returns exactly `["+module big", "renamed g4 -> g5", "renamed y
      -> w", "renamed z -> k", "+import b -> a", "+import b -> c", "+import c -> a", "-import
      e -> d", "-import w -> x", "-import x -> w", "cycle+ a > b > a", "cycle+ a > b > c > a",
      "cycle- d > e > d", "cycle- w > x > w", "grew g1 201", "grew g5 250"]`, and the same
      with `renames` in reverse order; and `structure_events(old, old, [])` returns `[]`. That
      is: two cycles through `a` and `b` are two lines; the 3-cycle starts at `a`, its least
      name, though `c -> a` is the edge listed first; the cycle `m > z > m` renamed to `k`,
      started again at `k`, equals `new`'s `k > m > k` and is no event; a broken cycle is
      `cycle-`, and the broken `x > y > x`, whose `y` is renamed to `w`, is named by the new
      name and started again at `w`; `g1` crossing 200 grows, `g2` reaching 200 and `g3`
      staying above do not, the renamed `g4` grows under its new name, and the added `big`
      does not. Red today: the list has the first ten and lacks the six `cycle` and `grew`
      items ("Second list contains 6 additional elements").
      Test: `tests/test_diff.py::StructureEventsTest::test_cycles_and_growth`
      Evidence: `StructureEventsTest.test_cycles_and_growth` (#45), seen red first on
      `9e253f6`'s code with "Second list contains 6 additional elements"; `python -m pytest -q`
      (#45).
      broken: diff.py: old cycles taken before the rename rule → 1 failed in 0.09s (#45)
- [x] C07.2 **new** — the timeline's contract: on the fixture, after `python -m bearing ingest
      <dir>/repo --prs <dir>/prs.json --data <tmp>`, `python -m bearing timeline <dir>/repo
      --data <tmp>` exits 0 and its stdout's bytes equal those of
      `tests/fixtures/expected/timeline.txt`, which holds exactly the 21 lines of "What the
      fixture gives", `\r\n` read as `\n` on both sides. Red today: stdout lacks lines 13, 15
      and 21, so the bytes differ.
      Test: `tests/contract/test_timeline.py::TimelineContractTest::test_golden`
      Evidence: `TimelineContractTest.test_golden` (#45), seen red first on `9e253f6`'s code:
      the bytes differ, first at line 13, `00394fb #3 cycle+ app.a > app.b > app.a`, which
      stdout lacks; `python -m pytest -q` (#45).
      broken: diff.py: the cycle line without its first name repeated → 1 failed in 7.66s (#45)
- [x] C07.3 **new** — `TimelineCliTest`'s `LINES` is the 21 lines, so `test_lines` (C06.5)
      and `test_stats` (C06.6) pass on the new code, the `#-` variant of #8's lines and the
      `--stats` counts unchanged ("blobs parsed 28  cache hits 0", then "blobs parsed 0  cache
      hits 28" twice). Red today: stdout is Day 6's 18 lines, not 21.
      Test: `tests/test_timeline_cli.py::TimelineCliTest::test_lines` and
      `tests/test_timeline_cli.py::TimelineCliTest::test_stats`
      Replaces: C06.5 — was: stdout is exactly the 18 lines of Day 6's "What the fixture gives"
      Replaces: C06.6 — was: the 18 lines on stdout
      Evidence: `TimelineCliTest.test_lines` and `TimelineCliTest.test_stats` (#45), each seen
      red first on `9e253f6`'s code: stdout's bytes are Day 6's 18 lines, without line 13
      (`00394fb #3 cycle+ app.a > app.b > app.a`); `python -m pytest -q` (#45).
      broken: diff.py: grew fires while a module stays above 200 → 1 failed in 8.38s (#45)
- [x] C07.4 **hold** — Phase 2's "Done when" on the target histories: for each of
      `../agentic-workflow-kit` and `../wordtally`, after `python -m bearing ingest <repo> --data
      <d>` into a new directory `<d>`, `python -m bearing timeline <repo> --data <d> --stats`
      run twice exits 0 both times, and the second run's stderr is "blobs parsed 0  cache hits
      N", N the first run's "blobs parsed". The close quotes the two lines for each, under the
      full SHA of the clone's `main` (`git -C <repo> rev-parse main`). True today: 204 and 94
      ("What the kit and wordtally give"). The close also breaks the check once by hand, not
      replayed: C06.6's break ("cli.py: the cache is not committed") put in, the kit's second
      run must print "blobs parsed 204", and the Notes quote what it printed.
      Evidence: the commands above, run by hand at the close (#46) on `8e90f74`, each into a new
      data directory. The kit
      at `c12cfe55018aebe82de83485460f1edd22e4c96b`: "blobs parsed 204  cache hits 0", then
      "blobs parsed 0  cache hits 204", both exit 0. wordtally at
      `e1d15e9bbe5067bf4b0cc67f0bb65f7cf52f5dab`: "blobs parsed 94  cache hits 0", then "blobs
      parsed 0  cache hits 94", both exit 0. The hand break is quoted in the Notes.
      broken: none → the check needs the two clones, which CI's replay does not have, so a break of it cannot be replayed; the cache's counting is broken on the fixture by C06.6's "cli.py: the cache is not committed" (#42)
- [x] C07.5 **hold** — the frozen files stay as Day 6 left them, added files allowed: the
      fixture, the contract tests and their golden files, the migrations, and the snapshot and
      cache tests:
      `git -c core.safecrlf=false diff --diff-filter=DMRT --exit-code 8abee85 -- tests/contract/ tests/fixtures/make_repo.py tests/fixtures/expected/ bearing/migrations/ tests/test_snapshot_tree.py tests/test_snapshot_cli.py tests/test_blob_cache.py`
      prints nothing and exits 0. `--diff-filter=DMRT` lets the day add
      `tests/contract/test_timeline.py` and `tests/fixtures/expected/timeline.txt`, and fails
      on a file deleted, modified, renamed or changed in type; CI's "Frozen files stay
      unedited" also passes an added file.
      Evidence: the command above, exit 0 in #44 and #45 and on `8e90f74` at the close; CI's
      "Frozen files stay unedited" on #44 and #45.
      broken: the applied migration 001_history.sql edited → subject_number INTEGER NULL, (#44)

## Verify
```bash
python -m pytest -q
python tests/fixtures/make_repo.py .bearing/day07-check
python -m bearing ingest .bearing/day07-check/repo --prs .bearing/day07-check/prs.json --data .bearing/day07-check/data
python -m bearing timeline .bearing/day07-check/repo --data .bearing/day07-check/data | grep -c -e "448fc4d #6 grew app.core 253" -e "e5fa51f #9 cycle- app.a > app.b > app.a"  # 2
git -c core.safecrlf=false diff --diff-filter=DMRT --exit-code 8abee85 -- tests/contract/ tests/fixtures/make_repo.py tests/fixtures/expected/ bearing/migrations/ tests/test_snapshot_tree.py tests/test_snapshot_cli.py tests/test_blob_cache.py
```

C07.4's runs need the two clones beside this repository, which CI's replay does not have, so
they are not in Verify: the close runs them by hand and quotes them.

## Notes
- Not the first day of Phase 2, so no plan-auditor run; the spec-auditor runs on this spec
  before its PR (CLAUDE.md, step 1). Day 7 is Phase 2's last day: after its close merges, the
  plan-auditor runs on Phase 2 and Phase 3 (CLAUDE.md, step 6).
- Choices, each a choice and not evidence: elementary cycles rather than strongly connected
  components, because plan.md's line `cycle+ a > b > a` is a path, and a component of three or
  more modules has no single path to print; the least name first, so the line is the same on
  every run whatever order the edges come in; cycles compared after renaming, as edges are, so
  a move is one `renamed` line; `grew` on crossing only, so a large module gives one line, not
  one per merge.
- Finding the cycles: for each module `s`, in sorted order, a depth-first walk over modules
  whose names sort after `s`, recording a cycle at each edge back to `s`. Each elementary cycle
  is found once, already started at its least name. The number of cycles can grow
  exponentially with the edges of a dense graph; the target histories have at most 8 edges and
  no cycle, so it is not bounded here.
- Sizes, estimated: about 45 lines in `diff.py`, 60 in `test_diff.py`, 55 in
  `test_timeline.py`, 21 in the golden file and 3 in `test_timeline_cli.py`: under 200.
- The count: 54 tests pass today ("54 passed, 51 subtests passed" on `8abee85`); the day adds 2
  test methods (`test_diff.py` 1, `test_timeline.py` 1) and edits the list two use, so
  `pytest -q` ends at "56 passed" (subtests besides).
- Verify's `make_repo.py .bearing/day07-check` refuses a directory that is not empty: delete it
  before a second local run.
- **Defect** D07.1 — found: auditor · cause: spec · made: Day 07 · C07.1 had no `cycle-` through
  a renamed module, so an implementation that printed `old`'s names passed it; it now has
  `x > y > x` with `y` renamed to `w`, expected as `cycle- w > x > w`.
- **Defect** D07.2 — found: auditor · cause: spec · made: Day 07 · C07.1 said `c -> a` was the
  edge listed first; it was fourth. The edge now comes first in `new`'s imports.
- **Defect** D07.3 — found: auditor · cause: spec · made: Day 07 · Verify's timeline line was
  judged by its exit code alone and passed on today's 18 lines; it now counts two of the new
  lines (`# 2`), and prints 0 today.
- **Defect** D07.4 — found: auditor · cause: spec · made: Day 07 · C07.4's check was never seen to
  fail: C06.6's break is on another check. The spec-auditor found this before any code, and
  the spec now has the close break it by hand on the kit.
- **Defect** D07.5 — found: auditor · cause: spec · made: Day 05 · plan.md's Day 10 stop still
  listed cycle detection as a cut, though Day 7 builds it (H05.1, never picked up), and Phase
  2's "Done when" asked for golden files of "snapshots" while Day 5 wrote one. This spec's plan
  change corrects both.
- At the close, on `8e90f74`: `python -m pytest -q` gave "56 passed, 51 subtests passed", the
  count above. Verify's `grep -c` printed 2, and C07.5's diff exited 0. All 4 `manifest:`
  lines parsed as JSON (1 in #44, 3 in #45), and each `find` occurs once in the merged code. I
  replayed each with `scripts/break.py` on `main`, and each failed its check. I ran `main`'s
  new tests on track A's base code (`9e253f6`) in a scratch worktree: "4 failed", each red as
  the spec says.
- C07.4 at the close, each clone's `main` as the spec gives it, a new data directory for each:
  the kit printed the same 42 lines on both runs (6 `grew`, no `cycle`), in 24 s, then 17 s;
  wordtally printed 29 (5 `grew`, no `cycle`), in 12 s, then 11 s. Neither clone's
  `git status` changed. The hand break, not replayed: C06.6's break (`conn.commit()` in
  `bearing/cli.py` replaced by `pass`), then a new ingest of the kit and two runs. Both exited
  0, and the second printed "blobs parsed 204  cache hits 0", not "blobs parsed 0  cache hits
  204", so the check failed with the break in. The file's bytes were put back, and
  `git status` was clean after it.
- No defect was found in track A or at the close: the five above are all the spec-auditor's.
- The blind relabel at the close agreed on 3 of 5 stages, 4 of 5 causes and 5 of 5 `made:`. On
  D07.4 the rater answered "unclear" for the stage, with low confidence, and `process` for the
  cause. It keeps `found: auditor`, and its text now says the spec-auditor found it before any
  code. It keeps `spec` too, because the missing break was a gap in the criterion as written,
  and the spec fixed it. On D07.5 the rater gave "before code" where the tag reads as an
  escape. The tag stays: Day 5 made the defect and it got past Day 5's close, though Day 7
  found it before any code.
- **Hand-off** H07.1 → Day 8: where `bearing.toml` is read from. The target repository is
  read-only (plan.md, "Decisions"), and Phase 3 is the first phase to read the file, for its
  areas and rules (plan.md, Course correction on Day 7).
