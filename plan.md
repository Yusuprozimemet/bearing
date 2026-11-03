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
| **PR ↔ commit mapping** | The kit's history has 90 merge commits, 11 direct commits before the first PR, and one PR closed unmerged (#71); it has no squash merge and no fork PR, and neither has wordtally's, so those cases exist only in the fixture | Phase 1: `mergeCommit` from `gh` first, the "Merge pull request #N" subject as fallback, an unmatched list reported, never guessed; a direct commit is listed as such, not as an error |
| **Merges out of order, merges with two parents** | PR numbers, `mergedAt` and the first-parent order disagree (a PR opened early and merged late); a merge's diff is against its first parent only | Phase 1: history is the first-parent line of `main`, in that order; every diff is `merge^1..merge`; a PR record whose commit is not on that line is unmatched |
| **Renames** | A moved file is one module removed and one added unless git pairs them | Phase 2: `git diff -M` pairs them; the timeline prints a rename line; the blob cache is unaffected, the blob SHA is the same |
| **Import resolution** | Relative imports, `src/` layouts, and flat `scripts/` folders that are not packages | Phase 2: a module map that is configurable, with flat files as their own modules by default |
| **Files that will not parse** | A syntax error, non-UTF-8 bytes, CRLF endings | Phase 2: lines are counted on the bytes, imports are empty, the module carries `"parse_error": true`; never a crash |
| **PR text that is not the template** | An empty body, no "What I built" heading, a heading spelt differently | Phase 1: the first paragraph of the body is the fallback; an empty body gives an empty entry, never a missing PR |
| **False flags in "said vs done"** | A `docs/` PR that fixes a typo in a script is not a lie | Phase 3: rules read from config, each flag shows its evidence, and a stopping point judges them on the kit's history |
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
  A branch with no `/` has the area `other`.
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

Each format has a version string in its output, a golden file under `tests/fixtures/expected/`
and a test in `tests/contract/` that compares bytes after `\r\n` is read as `\n`. JSON is
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
- **direction** (Markdown): `## Churn`, `## Coupling`, `## Said vs done`, in that order; one
  table each; a flag is `- #N <rule-id>: <claim> | <files>`, rules in `bearing.toml` order.
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
  snapshot/         # module map, import graph, blob cache, snapshot diff
  direction/        # churn, co-change coupling, said-vs-done rules
  page/             # static HTML timeline
tests/
  contract/         # golden-file tests of every output format; frozen
  fixtures/         # make_repo.py, recorded gh JSON, expected outputs
  ...               # unit tests per package
bearing.toml.example  # areas → paths, module map, rule settings for a target repository
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
    while touching `tests/contract/`; two files across modules changed together in at least
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
  `merges 90  matched 90  unmatched merges 0  unmatched PRs 0  direct 11`, and
  `bearing changelog | grep -c '^- #'` prints 90. Day 4's closing PR quotes both lines.

### Phase 2 — Structure snapshots
**Goal:** the module and import graph at every merge, and what changed between two merges.
- `bearing snapshot <ref>`: modules (package, or file for flat folders), their line counts, and
  the in-repository imports between them, as `snapshot-v1` JSON.
- A blob cache, so each file version is parsed once across the whole history.
- `bearing timeline`: one line per merge that changed structure: module added or removed, import
  edge added or removed, a cycle introduced or broken, a module that grew past a set size.
- **Done when:** the fixture's snapshots and timeline match their golden files; on the kit's
  and wordtally's full histories, `bearing timeline` exits 0, and `bearing timeline --stats`
  prints `blobs parsed 0  cache hits N` on its second run, N equal to the first run's
  `blobs parsed`. Day 7's closing PR quotes the two lines for each repository.

### Phase 3 — Direction
**Goal:** where the work goes, and where a PR's words and its diff disagree.
- Churn per area, by week. (Per module is cut: the timeline's `grew` events already show
  where a module grows.)
- Co-change coupling: file pairs that change together in at least N PRs, with pairs across
  modules flagged as a hidden dependency.
- Said vs done, from `bearing.toml`'s areas: a PR whose changed files lie outside its area's
  paths; a PR whose body says "Contract impact: none" while touching a contract path. Each flag
  names the PR, the claim and the files.
- `bearing direction` prints all three.
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

- **Day 4 (Phase 1) is a stopping point.** Is the changelog of the kit's 90 PRs useful enough to
  go on? If not, stop the project here; that is a valid result for the kit's measurement too.
- **Day 10 (Phase 3) is a stopping point.** The plan-auditor reads the whole plan against the
  code. Decide whether the page is worth building, and whether Bearing should be proposed to
  the kit (a kit decision, made in the kit's own repository, not here). If the schedule has
  slipped, co-change coupling is the next cut, then cycle detection in the timeline.

## Constraints

- `tests/contract/` is never edited, including its golden files and any timing. A change to an
  output format is a new contract version (`snapshot-v2`) with new golden files, decided in a
  plan-change PR.
- Applied migrations in `bearing/migrations/` are never edited; a schema change is a new file.
- Tests never use the network and never run `gh`; they run on `make_repo.py`'s repository and
  recorded JSON.
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

## Day-by-day specs

The phases are broken into day specs in [`specs/`](specs/). Read
[`specs/README.md`](specs/README.md) for the workflow.

1. Phase 0: Day 1.
2. Phase 1: Days 2-4. **Stop and evaluate.**
3. Phase 2: Days 5-7.
4. Phase 3: Days 8-10. **Stop and evaluate.**
5. Phase 4: Days 11-12.
