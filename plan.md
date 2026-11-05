# Bearing plan

<!-- plan.md says what and why; the day specs in specs/ say how. It changes rarely, and only in a
plan-change PR. Keep it short. -->

Bearing reads a repository's merge history and the text of its pull requests, and shows where the
code is heading: how its structure changed merge by merge, where the work goes, and where what a
PR said differs from what it changed. It is also the agentic-workflow-kit's first product
project: every PR is measured for the kit's token re-measure (see "Measurement").

## Verdict: the reading is easy; making it right on real histories, and worth reading, is hard

It starts as an empty repository copied from the kit and ends as a Python CLI, `bearing`, that
turns a repository with merged PRs into a changelog, a structure timeline, a direction report and
one static HTML page. Reading git and `gh` is easy. The hard part is getting right answers on
real, messy histories (squash merges, flat script folders, relative imports) and keeping the
"said vs done" flags useful rather than noise.

| Hard part | Why | Fix |
|---|---|---|
| **PR ↔ commit mapping** | The kit's history at the copied SHA (`44d7a55`) has 91 merge commits, 11 direct commits before the first PR, and one PR closed unmerged (#71); it has no squash merge and no fork PR, and neither has wordtally's. The squash merge exists only in the fixture; a fork PR exists in no history Bearing is tested on, the fixture included | Phase 1: `mergeCommit` from `gh` first, the "Merge pull request #N" subject as fallback, an unmatched list reported, never guessed; a direct commit is listed as such, not as an error; a fork's subject ("from other-owner/patch-1") is tested as a string, the fixture being frozen |
| **Merges out of order, merges with two parents** | PR numbers, `mergedAt` and the first-parent order disagree (a PR opened early and merged late); a merge's diff is against its first parent only | Phase 1: history is the first-parent line of `main`, in that order; every diff is `merge^1..merge`; a PR record whose commit is not on that line is unmatched |
| **Renames** | A moved file is one module removed and one added unless git pairs them | Phase 2: `git diff -M` pairs them; the timeline prints a rename line; the blob cache is unaffected, the blob SHA is the same |
| **Import resolution** | Relative imports, `src/` layouts, and flat `scripts/` folders that are not packages | Phase 2: every `.py` file is one module, named by its path from its import root with `.` for `/`, no `.py`, and `__init__.py` named by its package; the root is the repository's, or `src/` in a `src/` layout (no module map: see the Course correction on Day 7); a flat folder's `import helpers` resolves to the file beside the importer |
| **Files that will not parse** | A syntax error, non-UTF-8 bytes, CRLF endings | Phase 2: lines are counted on the bytes, imports are empty, the module carries `"parse_error": true`; never a crash. The fixture holds the syntax error and the CRLF file, not non-UTF-8 bytes: that case is tested on bytes given to the parser |
| **PR text that is not the template** | An empty body, no "What I built" heading, a heading spelt differently | Phase 1: the first paragraph of the body is the fallback; an empty body gives an empty entry, never a missing PR |
| **False flags in "said vs done"** | A `docs/` PR that fixes a typo in a script is not a lie | Phase 3: rules read from config, each flag shows its evidence, and a stopping point judges them on the kit's history. The rule still raises such a flag: the fixture's #5 is one, in the direction golden file (Course correction before Phase 3) |
| **Speed on long histories** | A snapshot per merge re-reads every file | Phase 2: parse each blob once, cached by its blob SHA |
| **Reproducible output** | Golden tests fail on any ordering, timestamp, layout or line-ending randomness, and a fixture built on Windows must give the SHAs it gives on Linux | All phases: sorted output, no run-time timestamps, a layered (not force-directed) graph layout; the fixture writes bytes with `\n` and sets its own git config (see Phase 0); `.gitattributes` keeps `tests/fixtures/` at `eol=lf` |

## Decisions made before the work

- **Python 3.12, standard library first:** `sqlite3`, `ast`, `subprocess` for `git` and `gh`.
  No GitPython, no network library. Dev tools: `pytest`, `ruff`.
- **The target repository is read-only.** Bearing reads it with `git log`, `git ls-tree` and
  `git cat-file`; it never checks out, fetches or writes there. Its own data goes to a directory
  given by `--data` (default `.bearing/` in the working directory).
- **PR text comes from `gh` JSON**, exactly the output of
  `gh pr list --state merged --limit 1000 --json number,title,body,headRefName,baseRefName,mergeCommit,mergedAt`,
  live or from a file given by `--prs`. Tests use recorded files only; the fixture's file is
  written by `make_repo.py` itself, so its numbers and commits agree with the repository.
- **A PR's area is its branch name up to the first `/`** (`headRefName`, or the "from
  owner/branch" of the merge subject when there is no record): `docs`, `tooling`, `day-03`.
  A branch with no `/` has the area `other`. This is the changelog's area. A file's area is
  another thing, a path area from `bearing.toml`, which Phase 3 reads; the two meet only in
  said vs done (Course correction before Phase 3).
- **The layered layout is the simplest deterministic one:** a module's layer is its longest
  import path from a module nothing imports; within a layer, modules are in name order. No
  crossing minimisation in v1. It is less pretty and is the same on every run and machine.
- **No LLM calls in v1.** Every output is computed, so it can be tested against golden files. A
  summarising layer may come after Phase 4 as an optional extra.
- **Python only for structure.** The import graph reads `.py` files; churn, coupling and said vs
  done work on any language.
- **The test history is built, not downloaded:** `tests/fixtures/make_repo.py` builds a git
  repository with fixed authors and dates, so the same commit SHAs come out every time.

## Output contracts

Each format has a golden file under `tests/fixtures/expected/` and a test in `tests/contract/`
that compares bytes after `\r\n` is read as `\n`. The JSON formats carry a version string
(`snapshot-v1`, `page-v1`); the text formats (the ingest line, the changelog, the timeline, the
direction report) carry none, and their golden file is their version: a new shape is a new
contract with new golden files, decided in a plan-change PR. JSON is
`json.dumps(sort_keys=True, indent=2)` with a final newline; lists are sorted where this section
says. The shape below is the contract; the names of columns and keys inside it are fixed by the
day spec that first writes the golden file, and then by the golden file.

- **`bearing ingest`** prints one line: `merges N  matched M  unmatched merges X  unmatched PRs Y
  direct D`, and lists each unmatched item below it, one per line.
- **changelog** (Markdown): `# Changelog`, then `## <area>` sections in area name order; each
  entry is `- #N <title> (<YYYY-MM-DD>)` followed by its paragraph, entries in first-parent
  order, oldest first. The paragraph is the first paragraph under the "What I built" heading of
  the kit's PR template, or the body's first paragraph when there is none.
- **`snapshot-v1`** (JSON): `{"version": "snapshot-v1", "ref": "<full sha>", "modules": [...],
  "imports": [...]}`; a module is `{"name", "path", "lines", "parse_error"}`, sorted by name; an
  import is `["from.module", "to.module"]`, sorted; only in-repository edges.
- **timeline** (text): one line per merge that changed structure, in first-parent order:
  `<sha7> #<pr or -> <event>`, one event per line, events in a fixed order: `+module`,
  `-module`, `renamed a -> b`, `+import a -> b`, `-import a -> b`, `cycle+ a > b > a`,
  `cycle- ...`, `grew <module> <lines>`.
- **direction** (Markdown): `## Churn`, `## Coupling`, `## Said vs done`, in that order;
  Churn and Coupling a table each, Said vs done one line per flag, `- #N <rule-id>: <claim> |
  <files>`, in first-parent order, a PR's flags in `bearing.toml`'s rule order.
- **page data** (JSON, embedded in the HTML as `<script id="bearing-data"
  type="application/json">`): `{"version": "page-v1", "steps": [...]}`, one step per merge in
  first-parent order, each with the merge, the structure events, the PR's number, title and
  paragraph, and its flags. The contract test extracts it by that id; the HTML around it is
  not under contract.

## Target structure

```
bearing/
  cli.py            # bearing ingest | changelog | snapshot | timeline | direction | page
  ingest/           # git merges, gh PR records, the mapping between them
  store/            # SQLite access
  migrations/       # 001_*.sql ...; applied ones are frozen
  snapshot/         # module names, import graph, blob cache, snapshot diff
  direction/        # churn, co-change coupling, said-vs-done rules
  page/             # static HTML timeline
tests/
  contract/         # golden-file tests of every output format; frozen
  fixtures/         # make_repo.py, recorded gh JSON, expected outputs
  ...               # unit tests per package
bearing.toml.example  # areas → paths, rule settings for a target repository
```

## Phases

Each phase is a series of <400-line PRs, so CI stays green.

### Phase 0 — Skeleton
**Goal:** a package, a CLI that runs, and a reproducible test history to test against.
- `pyproject.toml` with a `bearing` entry point; `bearing --version`.
- `python tests/fixtures/make_repo.py <dir>` builds the fixture repository and writes
  `<dir>/prs.json` beside it in the `gh` format above. It runs `git` with `-c` config only
  (`user.name`, `user.email`, `core.autocrlf=false`, `commit.gpgsign=false`,
  `init.defaultBranch=main`), fixed `GIT_AUTHOR_DATE` and `GIT_COMMITTER_DATE` per commit, and
  writes every file in binary mode. It must contain, so that every later rule has a case:
  - areas: at least `docs`, `tooling` and a `day-NN` branch; a branch with no `/`;
  - merges: `--no-ff` merges with "Merge pull request #N from owner/branch" subjects; one
    squash merge (a plain commit, its record's `mergeCommit` pointing at it); one merge with no
    record; one record whose commit is on a side branch, not the first-parent line; one
    direct commit on `main`; PR numbers merged out of order; dates spanning at least three
    weeks;
  - structure: a package with `__init__.py`, a `src/`-style package, a flat `scripts/` folder
    whose files import each other; absolute, `from . import` and `from ..pkg import` imports;
    a module added, one deleted, one renamed with `git mv`, one that grows past the size
    threshold; an import cycle introduced in one merge and broken in a later one; a file with
    a syntax error; a file with CRLF endings; a non-Python file changed on its own;
  - PR text: a body with the kit's template; one with no "What I built" heading; an empty
    body; a `docs/` PR that touches a script (a typo fix); a PR saying "Contract impact: None"
    while touching `tests/contract/`; two files in different areas changed together in at least
    the coupling threshold of PRs.
- The project's own test workflow in CI; `STYLE_CHECK_COMMAND` and `TRACK_RED_RUNNER=pytest` set.
- **Done when:** `pytest -q` passes in CI, and `tests/contract/test_fixture.py` asserts the
  fixture's HEAD SHA against a constant written into it on Day 1, on Linux CI and on Windows.

### Phase 1 — History and changelog
**Goal:** every merged PR stored once, with its commit, area and text, and a changelog from it.
- `bearing ingest <repo> [--prs file.json]`: merges on the first-parent line of `main`, PR records,
  the mapping between them, and an "unmatched" list for both sides.
- The SQLite schema as frozen migrations.
- `bearing changelog [--since] [--until]`: Markdown grouped by area, each entry the PR title,
  number and the first paragraph of its "What I built" section, or of the body when there is
  none ("Output contracts").
- **Done when:** on the fixture, the changelog matches its golden file; on the kit's repository
  at the copied SHA, with its PRs recorded to a file, `bearing ingest` prints
  `merges 91  matched 91  unmatched merges 0  unmatched PRs 0  direct 11`, and
  `bearing changelog | grep -c '^- #'` prints 91. Day 4's closing PR quotes both lines.

### Phase 2 — Structure snapshots
**Goal:** the module and import graph at every merge, and what changed between two merges.
- `bearing snapshot <ref>`: modules (one `.py` file each, with a dotted name: `app/core.py` is
  `app.core`, `src/lib/util.py` is `lib.util`; see "Import resolution"), their line counts,
  and the in-repository imports between them, as `snapshot-v1` JSON.
- A blob cache, so each file version is parsed once across the whole history.
- `bearing timeline`: one line per merge that changed structure: module added or removed, import
  edge added or removed, a cycle introduced or broken, a module that grew past a set size.
- **Done when:** the fixture's snapshot at `448fc4d` and its timeline match their golden files; on the kit's
  and wordtally's full histories, `bearing timeline` exits 0, and `bearing timeline --stats`
  prints `blobs parsed 0  cache hits N` on its second run, N equal to the first run's
  `blobs parsed`. Day 7's closing PR quotes the two lines for each repository.

### Phase 3 — Direction
**Goal:** where the work goes, and where a PR's words and its diff disagree.
- Churn per area, by week. (Per module is cut: the timeline's `grew` events already show
  where a module grows.) The area is the file's path area; the week is the ISO week of the
  first-parent commit's `committed_at`.
- Co-change coupling: file pairs that change together in at least N PRs, with pairs whose
  files lie in different `bearing.toml` areas flagged as a hidden dependency.
- Said vs done, from `bearing.toml`'s areas: a PR whose changed files lie outside its area's
  paths, checked only when its branch area names one of them; a PR whose body says "Contract
  impact: none" while touching a contract path. Each flag names the PR, the claim and the files.
- `bearing direction` prints all three. `bearing.toml` is read from `--config FILE`, default
  `bearing.toml` in the working directory, never from the target repository.
- **Done when:** the fixture's report matches its golden file, and Day 10's closing PR lists
  every flag `bearing direction` prints on the kit's history, as many lines as flags, each
  marked `real` or `rule: <what to change>` by the maintainer, with the counts of each; and at
  least half are `real`. With fewer, the rules change (a plan-change PR) and the flags are
  judged again before Phase 4 starts: a report that is mostly noise is not done.

### Phase 4 — Timeline page
**Goal:** one HTML file to step through the history, graph and PR text side by side.
- `bearing page --out <file>`: a single static file, data embedded as JSON, no external scripts,
  opens offline. The graph uses a layered layout computed in Python, so it is the same each run.
- Each step shows the merge, the structure change, the PR's title and "What I built", and any
  flag on it.
- **Done when:** the embedded data matches its golden file on the fixture; on the kit's
  history, the page's step count equals `bearing ingest`'s `merges`, and
  `grep -c -E 'src=|href="http' <file>` prints 0; and the maintainer has stepped through the
  first and last merge in a browser (a screenshot of each in Day 12's closing PR).

## Stopping points

- **Day 4 (Phase 1) is a stopping point.** Is the changelog of the kit's 91 PRs useful enough to
  go on? If not, stop the project here; that is a valid result for the kit's measurement too.
- **Day 10 (Phase 3) is a stopping point.** The plan-auditor reads the whole plan against the
  code. Decide whether the page is worth building, and whether Bearing should be proposed to
  the kit (a kit decision, made in the kit's own repository, not here). Co-change coupling is
  built on Day 8, before this stop, so it is no longer a cut; if the schedule has slipped, the
  stop decides what Phase 4 leaves out (Course correction before Phase 3, item 5).

## Constraints

- `tests/contract/` is never edited, including its golden files and any timing. A change to an
  output format is a new contract version (`snapshot-v2`) with new golden files, decided in a
  plan-change PR.
- Applied migrations in `bearing/migrations/` are never edited; a schema change is a new file.
- Tests never use the network and never run `gh`; they run on `make_repo.py`'s repository and
  recorded JSON, or on strings and bytes written in the test for a case the frozen fixture lacks.
- Output is deterministic: sorted, no time of the run in it.
- The kit's files in this repository (`scripts/`, `.claude/`, `.github/`, `specs/README.md`) stay
  as copied during the build, except the `PROJECT:` placeholders and the install steps the
  kit's workflows leave to the project (`evidence.yml`, and the seen-red job of
  `pr-checks.yml`, which installs nothing of its own and needs `pytest`). A kit fault found here
  is recorded in the day's Notes and fixed in the kit's repository, then copied over in one
  dated PR (see "Measurement").

## What we are not doing

- **No LLM summaries in v1.** They cannot be tested against golden files.
- **No import graph for languages other than Python.**
- **No server, account or hosted service.** A CLI and a static file.
- **No writes to the target repository**, and no GitHub write calls.
- **No adoption into the kit from here.** That is decided at the Day 10 stop and done in the kit.

## Measurement

This project is how the kit is measured on product work (`kit/six-kits-assessment.md` §9 in the
kit's repository). For it to count:

- Copy the kit from one commit of its `main`, and record that SHA in the first commit message,
  with the main session's model, the implementer's model and the Claude Code version. A change
  to any of the three is a split: record it in a Course correction with its date.
- Every PR states its rung (area branch, short spec, day spec), as `specs/README.md` asks. The
  rung is also readable from the merged branch: `day-NN/` is a day spec, `change/` a short
  spec, anything else an area branch.
- Each close runs `python scripts/token-usage.py` as usual. At the Day 4 and Day 10 stops,
  `python scripts/token-usage.py --compare --split <date of the last kit-update PR>` gives
  replies and $ per merged PR per window; the per-rung figures are counted by hand from the
  merged PRs' branches, in the stop's Course correction.
- Each day's Notes tag every defect with the kit's `found:` values (`auditor`,
  `spec-change PR`, `review`, `break on purpose`, `self`, `Track <X>`, `close`, `dashboard`,
  `Day <NN> review`), so the counts compare with the kit's earlier projects.
- Kit updates are copied in only at a stop, in one PR named for the kit SHA, so the measurement
  has dated splits.
- All Bearing sessions run in Bearing's own folder, so its transcripts are counted apart from
  the kit's. Nothing in the kit's repository is changed from a Bearing session.

## Course corrections

<!-- Added by plan-change PRs, newest first. Empty at the start. -->

### 2026-11-04: Course correction before Day 5

The maintainer's two decisions before Phase 2's first spec.

- **A module is one `.py` file with a dotted name.** Phase 2 said "package, or file for flat
  folders", yet the rest of the plan already counted files: the Renames row ("a moved file is
  one module removed and one added"), and the fixture, four of whose structure events lie inside
  the one package `app` (`app/a.py` and `app/b.py` make and break the cycle, `app/core.py`
  grows past 200 lines, `app/extra.py` is added and `app/legacy.py` deleted). Counted by
  package, the timeline would show none of these four. "Import resolution" now says how a file is named;
  `snapshot-v1`'s shape is unchanged, its `name` dotted and its `path` the file.
- **Co-change coupling flags pairs across areas, not modules.** With a file per module, every
  pair of files is across modules and every pair would be flagged. A hidden dependency is now
  a pair in different `bearing.toml` areas, the areas "said vs done" reads; the fixture's pair
  (`app/core.py` and `src/lib/util.py`, changed together in #1, #3 and #9) is the one Phase 3's
  areas must put apart. The maintainer chose this over "no import between them", which would
  not flag that pair, since `util.py` imports `app.core`.
- **H03.3: the text formats carry no version string.** "Output contracts" said every format
  has one; Day 2's ingest line and Day 3's changelog shipped without, and the changelog's
  golden file is a contract that may not change. The JSON formats keep theirs (`snapshot-v1`,
  `page-v1`); for the ingest line, the changelog, the timeline and the direction report, the
  golden file is the version, and a new shape is a new contract, decided here.

### 2026-11-04: Course correction after Phase 1

The Day 4 stop (H04.1), recorded in the kit-update PR (#30).

- **Verdict: the changelog is useful enough to go on.** On the kit at `44d7a55`, with 91 of its
  93 PR records: `merges 91  matched 91  unmatched merges 0  unmatched PRs 0  direct 11`, 215
  lines, 91 entries, in four areas (dashboard 28, docs 13, specs 2, tooling 48). Findings, not
  fixed now:
  - "tooling" is too broad: 48 of 91 entries. The areas need to be finer than the title prefix
    gives.
  - A description should be one or two sentences. Some carry a whole PR body (#11), and some
    an opener that says nothing ("Two follow-ups from CHANGES item 26, one commit each:", #5).
    This is a rule for whichever day next touches the changelog.
  - On a Windows console (Git Bash), "°" and "…" print as "Â°" and "â€¦"; the file is clean
    UTF-8, and `PYTHONIOENCODING=utf-8` prints them right. This is H03.1's stdout side, and it
    stays unowned for now.
- **The kit is copied in at `c12cfe5`** (kit PRs #93, #94, #95), a split in the measurement
  dated 2026-11-04. Main session Opus 5.5 (`claude-opus-5-5`), implementer Haiku
  (`claude-haiku-5-5`), Claude Code 2.1.170: unchanged. The local changes to kit files:
  - #4 `scripts/seen-red.py`, #7 `scripts/evidence.py` and #9 `scripts/step-guard.py` (its
    test and hooks) are now the kit's files.
  - #5 `scripts/test_evidence_workflow.py` stays Bearing's: the kit now says a project that
    changes the install step replaces the two default install tests with its own, as #5 did.
  - #20's `human:` lines in `.github/pull_request_template.md` and `CLAUDE.md` are kept
    (D04.8): the kit has none, so these two files stay ahead of it until the kit takes them.
  - H01.5, H01.6 and H01.7 are fixed in the kit. H02.4 is half done: the kit's
    `specs/README.md` says to copy a `manifest:` line from the raw body and check it parses, but
    no check does it; it stays open in the kit.
  - The kit's `lifted()` (#95) lifts a stop only on a heading here saying "after Phase N", or a
    bullet opening "**Phase N stop:**". The entry below names Phase 1 and no longer lifts it.
- **The token split separates nothing yet.**
  `python scripts/token-usage.py --compare --split 2026-11-04`: the first kit copy (`dfc762f`),
  all 29 merged PRs and every transcript fall on 2026-11-04, so only the "after" side has
  replies: 863 replies, median 81,069 and mean 88,240 context tokens per reply, 0.0% read past
  300k, $47.58 ($0.0551 per reply), 29.8 replies per merged PR. The $47.58 counts the main
  sessions only; Day 4's close counted $206.89 for the whole folder, subagents included. At the
  Day 10 stop the boundary is this PR's date.
- **Merged PRs per rung**, from the merged branches, to #29: day spec 23 (#1–#3, #6, #8,
  #11–#19, #21–#29), area branch 6 (#4, #5, #7, #9, #10, #20), short spec 0.

### 2026-11-04: after the Phase 0/1 audit

- **The kit has 91 merges, not 90.** The kit was copied at `44d7a55`, the merge of its PR #92;
  the plan counted to `8a9d53a` (#91), one merge earlier. The count follows the copied SHA, so
  Phase 1's line and the Day 4 stop now say 91. Direct commits (11), the one unmerged PR (#71),
  and no squash or fork PR still hold there.
- **Kit files changed during Day 1, against "Constraints".** Four area-branch PRs changed kit
  files in this repository instead of in the kit, all merged on 2026-11-04 while the kit's
  `main` stayed at `44d7a55`:
  - #4 `scripts/seen-red.py` (and its test): left out code under `tests/` the project file
    names, so Tracks B and C could be seen red (D01.1; H01.5 carries it to the kit);
  - #5 `scripts/test_evidence_workflow.py`: the kit's test of the install step that
    "Constraints" lets the project change;
  - #7 `scripts/evidence.py` (and its test): the replay compared pytest's run time and failed
    10 of Day 1's 13 breaks;
  - #9 `scripts/step-guard.py`, its test and three hooks in `.claude/settings.json`, none in
    the kit: the step boundary skipped after a "merged" (D01.23, H01.7).

  From that date Bearing's kit files are `44d7a55` plus these four. This is a split in the
  measurement: their sessions are Bearing's tokens spent on kit work, counted in Day 1. Each is
  to be made in the kit's repository, outside a Bearing session, and the Day 4 stop's kit-update
  PR replaces the local copies with that kit SHA. The rule stays: the next kit fault is recorded
  in the Notes first, and a change here before a stop is a new Course correction.
- **Two hard cases are not in the fixture.** The fixture is frozen at its pinned HEAD
  (`tests/contract/test_fixture.py`), and it holds no fork PR and no file with non-UTF-8 bytes,
  although the hard-parts table said the fork PR was in it and listed non-UTF-8 bytes. Adding them would move the pinned SHA, a contract
  edit. So Phase 1 tests a fork's merge subject as a string, and Phase 2 tests non-UTF-8 bytes
  given to the parser; "Constraints" now allows such tests. Neither case is in a golden file.

### 2026-11-04: Course correction on Day 7: no module map

- **The module map in `bearing.toml` is cut.** "Import resolution" let a map in `bearing.toml`
  change a module's import root. Day 5 left it to Day 7 (H05.6): if the kit's and wordtally's
  histories need no map, a plan-change PR may cut it. Neither does. At the kit's `c12cfe5` and
  at wordtally's `e1d15e9`, 15 imports name a top-level folder or a `.py` file's name of the
  same repository, or are relative (6 in the kit, 9 in wordtally); 14 resolve to an edge
  without a map. The one that does not is wordtally's `experiments/jev/e1/build.py` importing
  `evidence`, which it reaches through a `sys.path` edit. A map that resolved it would make
  `scripts/` an import root and rename every `scripts.*` module. The kit's tests load their
  hyphenated scripts with `importlib`, which no map can reach. The maintainer chose the cut.
  Modules keep the names "Import resolution" gives them, and Phase 2 reads no `bearing.toml`.
- **Where `bearing.toml` is read from is now Phase 3's question.** Phase 3 is the first phase
  to read the file, for its areas and rules. The target repository is read-only, so Day 8
  decides the file's location (H07.1).
- **Cycle detection is no longer a cut.** The Day 10 stop named it as the cut after co-change
  coupling, and Day 7 builds it (`cycle+`, `cycle-`), so the stop now names coupling alone (Day
  5's H05.1, which was left to the maintainer and never picked up).
- **One snapshot golden file.** Phase 2's "Done when" asked that the fixture's "snapshots" match
  their golden files. Day 5 wrote one, `snapshot-448fc4d.json`, and no day was given more. A
  snapshot of every merge is checked through the timeline's golden file, which is built from
  them. "Done when" now names the one snapshot.

### 2026-11-04: Course correction before Phase 3

The plan-auditor's Phase 3 findings on fresh `main` (`43d5012`), settled in Day 8's spec PR.
The maintainer chose 1, 2 and the days' split; 3 and 4 follow from the facts below.

1. **Two kinds of area.** "Decisions" makes a PR's area its branch prefix; Phase 3 needs areas
   that are paths. The fixture's coupling pair (`app/core.py`, `src/lib/util.py`) changes only
   in `day-NN` PRs (#1, #3, #9), so no branch area can put it apart. `bearing.toml` has one
   `[areas]` table, each area a name and a list of path prefixes; a file's area is the first
   whose prefix it starts with, in file order, else `other`. Churn and coupling use the file's
   area. Said vs done checks a PR's files only when its branch area is the name of a
   `bearing.toml` area; `day-NN`, `release` and `other` PRs are not checked for it. The
   changelog keeps branch areas: its golden file is frozen.
2. **The fixture's #5 is flagged.** `docs/typo-fix` changes one line of `scripts/run.py`. The
   rule flags it, and the direction golden file lists it with that file as evidence. A typo fix
   is not a lie, so the flag is false, but judging flags is the stop's job (the hard-parts row,
   and Phase 3's "Done when"); a rule that hides small changes would hide small real ones too.
   This settles H01.4's second half.
3. **Both forms of "Contract impact".** All 94 of the kit's merged PRs at `c12cfe5` write a
   `## Contract impact` heading, and none the one-line form; many write "None." with more text
   after it. The fixture's template does the same; only #9 writes "Contract impact: None", and
   #9 is the only PR that touches `tests/contract/`. So the claim is "none" in either form: a
   `Contract impact` heading of any level whose first non-blank line starts with the word
   "none", or a line starting `Contract impact:` followed by that word, case ignored (H01.4's
   first half). The fixture can show only the one-line form, so the heading form is tested on
   a body written in the test.
4. **Where `bearing.toml` lives (H07.1).** The target repository is read-only and the fixture
   frozen, so the file always lives outside the repository it describes: `--config FILE`,
   default `bearing.toml` in the working directory, as `--data` defaults there. The fixture's is
   `tests/fixtures/bearing.toml`. The kit's is written on Day 10, which runs on the kit at
   `c12cfe55018aebe82de83485460f1edd22e4c96b` (#95), the SHA Day 7 ran, unless Day 10's spec
   names another and says why.
5. **The days.** Day 8: `bearing.toml`, churn and coupling, and `bearing direction` printing
   those two sections. Day 9: said vs done, the direction golden file and its contract test.
   Day 10: the kit's run, the maintainer's judging and the stop. Churn and coupling read each
   commit's `git diff --numstat -M` at run time, as the timeline reads its renames; the store
   gains no table.

## Day-by-day specs

The phases are broken into day specs in [`specs/`](specs/). Read
[`specs/README.md`](specs/README.md) for the workflow.

1. Phase 0: Day 1.
2. Phase 1: Days 2-4. **Stop and evaluate.**
3. Phase 2: Days 5-7.
4. Phase 3: Days 8-10. **Stop and evaluate.**
5. Phase 4: Days 11-12.
