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
- **The layered layout is the simplest deterministic one:** each cycle of imports (a strongly
  connected component) is one node, and every other module is a node of its own; a node's layer
  is its longest import path from a node nothing imports, and a module takes its node's layer;
  within a layer, modules are in name order (Course correction after Phase 3). No
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
  paths and the rule's `shared` paths, checked only when its branch area names one of them;
  a PR whose body says "Contract
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
  flag on it, marked unverified (Course correction after Phase 3).
- **Done when:** the embedded data matches its golden file on the fixture; on the kit's
  history at `c12cfe5` with `docs/kit/bearing.toml`, the page's step count equals `bearing ingest`'s `merges`, and
  `grep -c -E 'src=|href="http' <file>` prints 0; and the maintainer has stepped through the
  first and last merge in a browser (a screenshot of each in Day 12's closing PR).

### Phase 5 — Loose ends
**Goal:** the two hand-offs no day owned, H03.1 and H04.2, closed in code in one day, Day 13
(Course correction after Phase 4). Day 13 is also the day the agentic-workflow-driver's level 1
trial runs on; the driver is a separate program, and nothing here depends on it.
- stderr is UTF-8 whatever the console's code page, as stdout already is (H03.1): every
  "bearing: ..." line and the line `--stats` prints. What `argparse` writes before the
  arguments are parsed is left as it is.
- `bearing ingest` warns when it has exactly 1000 PR records, from `gh` or from `--prs`
  (H04.2): one line on stderr, "bearing: warning: 1000 PR records is gh's limit; a history with
  more is cut". Stdout and the exit code are what they are without it. No pagination and no
  option for the limit.
- **Done when:** every check is a test under `tests/` that CI runs, with no hand run, no kit
  history and no screenshot. In a subprocess started with `PYTHONIOENCODING=cp1252`, an error
  that names a non-ASCII path reaches stderr as that path's UTF-8 bytes. `bearing ingest` on the
  fixture with a file of 1000 records prints the warning line once on stderr, none of it on
  stdout, and exits 0; with 999 records stderr is empty. `pytest -q` passes in CI, and
  `git diff --exit-code 001ed11 -- tests/contract/` prints nothing: no contract changes.

### Phase 6 — Description length
**Goal:** the Phase 1 stop's rule that a changelog description is one or two sentences,
unowned since then, closed in code in one small day, Day 14 (Course correction after Phase 5).
Day 14 is also the day the agentic-workflow-driver runs its first step inside a Docker
container; the driver is a separate program, and nothing here depends on it.
- The description `bearing changelog` prints, and the page's `paragraph` with it (both read
  `what_i_built`), is cut to its first two sentences. A sentence ends at ".", "!" or "?"
  followed by whitespace or the end of the text. The shortened description is the first two
  sentences exactly as written, trailing whitespace stripped. One or two sentences are left as
  they are.
- Known limit, not handled: "e.g. " ends a sentence, as does any other abbreviation followed by
  whitespace.
- The change stays in `bearing/` and `tests/`: no new dependency, and nothing under
  `.github/`, `.claude/` or `scripts/`.
- **Done when:** every check is a test under `tests/` that CI runs, with no hand run and no kit
  history. A "What I built" paragraph of three sentences gives its first two; one of one or two
  sentences is unchanged; a sentence ended by "!" or "?" counts as one ended by ".".
  `pytest -q` passes in CI, and `git diff --exit-code c214b09 -- tests/contract/` prints
  nothing: every description on the fixture is one sentence, so no golden file changes.

Phases 7 to 10 are one small day each, Days 15 to 18 (Course correction after Phase 6). Each
day's work stays in `bearing/` and `tests/`, with no new dependency and nothing under
`.github/`, `.claude/` or `scripts/`; and each "Done when" also holds that `pytest -q` passes in
CI and that `git diff --exit-code 714412f -- tests/contract/` prints nothing.

### Phase 7 — Coupling follows renames
**Goal:** Day 8's known limit closed: a file renamed on the first-parent line is one file in
`bearing direction`'s Coupling, not two. Day 15; it changes Day 8's code
(`bearing/direction/changes.py`, `coupling.py`, `report.py`).
- Renames are git's own pairing, the `-M` numstat that churn already reads, taken from every
  commit churn reads (merges and direct commits). Coupling names each path by the name it has
  after the last rename that reaches it, through a chain of renames; a path used again after
  its file was renamed away is a new file.
- A new function gives a commit's renames from the same numstat bytes. `parse_numstat` and
  `changed_files` keep their return values (C08.2), so churn, said vs done and the page
  (`bearing/page/data.py` calls `changed_files`) read paths as each commit changed them.
- **Done when:** every check is a test under `tests/`. Numstat bytes holding a rename give the
  old and new path. Renames given in the test: a chain a→b→c is one file named c, and a path
  used again after a rename is a second file. On the fixture with `[coupling] min_prs = 2` in
  a config the test writes, the Coupling table is exactly four rows, the three of today
  (C08.6, which the day replaces) and `scripts/run.py` with `scripts/tools.py`, PRs #2 and #8
  (#8 renamed `scripts/helpers.py` to `scripts/tools.py`); at `min_prs = 3`, the golden file's,
  the output is unchanged.

### Phase 8 — The command line's silent successes
**Goal:** two inputs that print nothing useful and exit 0 become errors. Day 16; it changes
`main` in `bearing/cli.py` (Days 1 and 4).
- `bearing` with no command prints argparse's usage and its "the following arguments are
  required" line on stderr and exits 2, as for any missing argument. `bearing --version` is
  unchanged. The day's spec pins that line as Python 3.12 prints it.
- `bearing changelog --since A --until B` with A after B is an argument error: usage and one
  line naming both dates on stderr, exit 2, nothing on stdout, and the store not read. Equal
  dates stay one day.
- **Done when:** every check is a test under `tests/`, both cases giving exit 2 and an empty
  stdout; reversed dates with a `--data` that holds no store give exit 2, not "no store", so
  the store is not read; and `changelog` with dates in order prints what it prints today. No
  test pins either case today, so no criterion is replaced.

### Phase 9 — A branch other than `main`
**Goal:** `bearing ingest` reads a repository whose history is on a branch not named `main`.
Day 17; it changes Day 2's `read_first_parent` and Day 4's `fetch_prs`.
- `bearing ingest <repo> --branch NAME`, default `main`: the history is NAME's first-parent
  line. A NAME that is not a local branch (`refs/heads/NAME`; a tag or a SHA is not one) is one
  line on stderr naming it and `--branch`, exit 1, and no store written. Today a repository
  without `main` gives "bearing: fatal: bad revision 'main'". A directory that is not a git
  repository keeps the error it gives today.
- `gh` is asked for the PRs merged into NAME only (`--base NAME`); a `--prs` file is read as it
  is. The other commands read the store, so they need no option. Day 4 left "a ref other than
  `main`" out of scope (`specs/day-04-live-prs.md`); this phase takes it in, and replaces C04.2,
  which pins `gh`'s argument list.
- **Done when:** every check is a test under `tests/`, with `gh` faked as in Day 4's tests.
  `--branch main` prints `tests/fixtures/expected/ingest.txt`; `--branch release` on the fixture
  with its `prs.json` prints "merges 9  matched 9  unmatched merges 0  unmatched PRs 1  direct 2"
  and "unmatched PR #10 86761f2 release"; a missing branch gives the error line and no store;
  and the faked `gh` call carries `--base` with the name.

### Phase 10 — `direction`'s git errors in one line
**Goal:** `bearing direction` reports a wrong repository as `timeline` and `page` do. Day 18;
it changes Day 8's `bearing/direction/` and reuses Day 5's checks in `bearing/snapshot/tree.py`.
- On a directory that is not a git repository, `direction` prints
  "bearing: not a git repository: <repo>" (today "bearing: error: Could not access
  '<sha>^1'"). On a repository that does not hold the store's commits, it prints
  "bearing: not a commit: <sha>" for the first stored commit with a parent, the first it reads
  (today git's three lines from `git diff`). Both are the lines `timeline` gives, exit 1,
  stdout empty. No test pins `direction`'s git text today.
- **Done when:** every check is a test under `tests/`; the second repository is an empty
  `git init` made in the test, as `tests/test_timeline_cli.py` already does.

Phases 11 to 16 are one small day each, Days 19 to 24 (Course correction after Day 15's track
A). They hold to the same rules as Phases 7 to 10: each day's work stays in `bearing/` and
`tests/`, with no new dependency and nothing under `.github/`, `.claude/` or `scripts/`; and
each "Done when" also holds that `pytest -q` passes in CI and that
`git diff --exit-code 714412f -- tests/contract/` prints nothing. Every error in Phases 11, 12,
14, 15 and 16 is one line on stderr starting "bearing: ", exit 1, with nothing on stdout;
Phase 13's is argparse's usage and error line, exit 2.

### Phase 11 — A `--prs` file that is not PR records
**Goal:** `bearing ingest --prs FILE` stops with one line when the file's JSON is not a list of
PR records. Today a record with no `title` ends in a traceback (`KeyError: 'title'`) and leaves
a `bearing.db` behind, a list of numbers in another (`AttributeError`), a `mergeCommit` that is
a string in a third, a JSON object exits 0 as if it held no PRs, and two records with one
`number` print "cannot open store at D: UNIQUE constraint failed: prs.number" and leave a store.
Day 19; it changes Day 2's `--prs` path in `bearing/cli.py` and `bearing/ingest/mapping.py`.
- A new function in `bearing/ingest/mapping.py` checks the records `load_prs` returned and
  raises `ValueError` carrying the line after "bearing: ". `ingest` calls it inside the `try`
  that reads the file, right after `load_prs`, so the existing `except (OSError, ValueError)`
  prints it; that is before the 1000-record warning and before the store is opened. `load_prs`
  itself is unchanged: `tests/test_mapping.py`'s `test_utf8` reads a record with no branch
  names through it. The records `gh` prints are not checked.
- The first failure found is the line, records counted from 1, exit 1, no store written:
  - "bearing: FILE: not a list of PR records", for anything but a JSON list;
  - "bearing: FILE: record N is not an object";
  - for each of `number`, `title`, `headRefName`, `baseRefName` in that order, the fields
    `save` and the report read with `[]`, its presence and then its type: "bearing: FILE:
    record N has no FIELD", "bearing: FILE: record N's number is not an integer" (`true` is
    not one), "bearing: FILE: record N's FIELD is not a string";
  - then the optional fields, each absent, `null` or of its type: "bearing: FILE: record N's
    FIELD is not a string" for `body` and `mergedAt`, "bearing: FILE: record N's mergeCommit
    is not an object", and "bearing: FILE: record N's mergeCommit oid is not a string";
  - after every record passes: "bearing: FILE: record N repeats number M", N the first record
    whose number an earlier record has.
- **Done when:** every check is a test under `tests/`. `{}`, `[1]`, and the fixture's records
  with record 3's `title` removed, its `number` the string "3", its `mergeCommit` the string
  "x", and its `number` that of record 2, each give its line, exit 1, an empty stdout and no
  store; the fixture's `prs.json` still prints `tests/fixtures/expected/ingest.txt`.

### Phase 12 — A `--prs` file that cannot be read names it
**Goal:** every failure to read a `--prs` file says "cannot read FILE", as a missing one does
today ("bearing: cannot read FILE: No such file or directory"). Day 20; it changes the same
`except` in `bearing/cli.py` as Day 19.
- Today text that is not JSON prints "bearing: Expecting property name enclosed in double
  quotes: line 1 column 2 (char 1)", bytes that are not UTF-8 print "bearing: 'utf-8' codec
  can't decode byte 0xff in position 0: invalid start byte", and a directory prints "bearing:
  [Errno 13] Permission denied: '<path>'" (Windows; Linux gives errno 21). None names the
  option or says the file is the problem.
- They become "bearing: cannot read FILE: not JSON: <msg> (line L, column C)" from the
  `JSONDecodeError`'s `msg`, `lineno` and `colno` (not `str(exc)`, which repeats the
  position), so `{bad` gives "bearing: cannot read FILE: not JSON: Expecting property name
  enclosed in double quotes (line 1, column 2)"; "bearing: cannot read FILE: not UTF-8"; and
  "bearing: cannot read FILE: <reason>", the reason `exc.strerror or exc` as `ingest`'s "cannot
  run git" line has it. Day 19's lines are `ValueError`s too and keep their wording: the day
  catches the decode errors by their own classes.
- A file that starts with a UTF-8 byte order mark (what Windows PowerShell 5.1's
  `Out-File -Encoding utf8` writes) is not JSON, as today: "not JSON: Unexpected UTF-8 BOM
  (decode using utf-8-sig) (line 1, column 1)". `gh` writes none.
- **Done when:** every check is a test under `tests/`. A file holding `{bad` and one holding the
  bytes `ff fe 5b` each give its exact line; a directory gives one line starting
  "bearing: cannot read <dir>: " with no "[Errno" in it; each exits 1 with an empty stdout and
  no store. The missing file's line is unchanged.

### Phase 13 — A date that is not YYYY-MM-DD
**Goal:** `bearing changelog --since` and `--until` take a date in the store's form,
YYYY-MM-DD, and say so when given anything else. Day 21; it changes Day 3's option types in
`bearing/cli.py`, after Day 16's date check.
- Today a value that `date.fromisoformat` refuses gives "bearing changelog: error: argument
  --since: invalid fromisoformat value: 'yesterday'", and two forms it accepts pass as dates no
  one wrote down: `20260121` is 2026-01-21 and `2026-W03-2` is 2026-01-13.
- This reverses a decision of Day 3: its In scope says DATE is any ISO date
  `date.fromisoformat` accepts, `20260114` among them (`specs/day-03-changelog.md`, set by
  D03.9). No criterion or test pins it, so no `Replaces:` line; Day 21's spec cites both.
- Both options take exactly four digits, "-", two digits, "-", two digits (ASCII digits only)
  naming a real day, and still give a `date`, so Day 16's check is unchanged. Anything else,
  `2026-02-30` included, makes the type raise `argparse.ArgumentTypeError` (a plain
  `ValueError` brings back "invalid <name> value"): "bearing changelog: error: argument
  --since: not a date in YYYY-MM-DD form: 'VALUE'", VALUE as typed between single quotes (not
  `!r`, which switches to double quotes for a value holding one), `--until` for that option;
  exit 2, nothing on stdout, and the store not read.
- **Done when:** every check is a test under `tests/`. `yesterday`, `20260121`, `2026-W03-2` and
  `2026-02-30` given to `--since`, and one of them to `--until`, each end with its line and exit
  2; the same with a `--data` that holds no store gives exit 2, not "no store"; and dates in
  YYYY-MM-DD print what they print today. No test pins argparse's date text today, so no
  criterion is replaced.

### Phase 14 — `ingest`'s "not a git repository" in one line
**Goal:** `bearing ingest` names a wrong repository as every other command does. Day 22; it
changes Day 2's `read_first_parent` as Day 17 leaves it.
- Today a directory that is not a git repository prints "bearing: fatal: not a git repository
  (or any of the parent directories): .git", and a path that does not exist "bearing: fatal:
  cannot change to '<repo>': No such file or directory". Both become
  "bearing: not a git repository: <repo>", `<repo>` as given: the line `snapshot`, `timeline`
  and `page` print, and `direction` after Day 18. Exit 1, no store.
- Day 18's `check_commit(repo, ref)` in `bearing/snapshot/tree.py` runs the
  `git rev-parse --git-dir` check and the commit check together, and raises `SnapshotError`,
  which `ingest` does not catch. Day 22 splits the first check out into its own function in
  `tree.py`, which `check_commit` calls, so the other commands print what they print.
  `read_first_parent` calls it before Day 17's branch check and raises `GitError` with the same
  text, so `ingest`'s existing `except GitError` prints it.
- A repository with no such branch keeps Day 17's line, and any other git failure keeps
  git's text. Day 22 replaces C17.7, which pins "bearing: fatal: not a git repository", and
  changes Day 17's In scope line "a directory that is not a git repository keeps today's
  error"; its spec cites both.
- **Done when:** every check is a test under `tests/`, with the fixture, an empty temporary
  directory and a path that does not exist; the missing-branch line is unchanged.

### Phase 15 — OS errors name the path once
**Goal:** two of `bearing`'s OS errors print the path twice, the second time in Python's
quoting (with its backslashes doubled on Windows). They print it once, with the OS's reason,
as `ingest`'s "cannot run git" line does, and `--prs`'s after Day 20. Day 23; it changes `page`
and `ingest` in `bearing/cli.py`.
- Today `page --out missing/x.html` prints "bearing: cannot write missing/x.html: [Errno 2] No
  such file or directory: 'missing\\x.html'", and `ingest --data FILE`, a file where the store's
  directory should be, prints "bearing: cannot open store at FILE: [WinError 183] Cannot create
  a file when that file already exists: 'FILE'" (Linux: "[Errno 17] File exists").
- They become "bearing: cannot write OUT: <reason>" and "bearing: cannot open store at DATA:
  <reason>", the reason `exc.strerror or exc` as Day 20's. A `sqlite3.Error` at the store keeps its text, as does every other error.
- **Done when:** every check is a test under `tests/`. `page --out` into a directory that does
  not exist prints exactly "bearing: cannot write <out>: No such file or directory" (ENOENT reads
  the same on Linux and Windows), and `ingest --data` naming a file one line starting
  "bearing: cannot open store at <file>: " with no "[Errno" or "[WinError" in it; each exits 1
  with an empty stdout. The two tests that pin these lines' starts today
  (`tests/test_broken_store.py`, `tests/test_page_cli.py`) pass unedited.

### Phase 16 — A `bearing.toml` that is not UTF-8
**Goal:** `bearing direction` and `bearing page` stop with one line when the config's bytes are
not UTF-8, as they do for a config that is not TOML. Day 24; it changes Day 8's `_read` in
`bearing/direction/config.py`, which `load_config` and `load_rules` (Day 9) share.
- Today a config holding the bytes `ff fe` followed by `[areas]` ends both commands in a
  traceback, "UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff in position 0: invalid
  start byte", exit 1: `_read` catches only `tomllib.TOMLDecodeError`.
- It becomes "bearing: cannot read config FILE: not UTF-8", FILE as given, the prefix the
  `TOMLDecodeError` line has and the reason Day 20's `--prs` line gives. `_read` raises it as a
  `ConfigError`, which both commands already print, before the store is looked for.
- A config that starts with a UTF-8 byte order mark keeps today's line, "bearing: cannot read
  config FILE: Invalid statement (at line 1, column 1)", as Day 20 keeps `--prs`'s. A missing
  config and a config that is not TOML keep theirs.
- **Done when:** every check is a test under `tests/`. The `ff fe` config gives its exact line
  for `direction` and for `page`, each exit 1 with an empty stdout, and `page` writes no
  `--out` file; `tests/test_config.py` passes unedited.

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

### 2026-11-21: Course correction after Day 15's track A: Phases 11 to 16, one day each

Day 15's close and Days 16 to 18 give the agentic-workflow-driver about 7 more pull requests;
it needs about 14 opened and merged by its own sessions at level 1, then one whole day at
level 2. The maintainer adds six phases of one small day each, Days 19 to 24, with one track
each, and their specs are written now, one spec PR per day after this one, so the driver never
stops at "write its day spec". Five days would give exactly the 14 and the level 2 day, so one
count set back to 0 would end the plan before the driver is done; the sixth is the margin.

1. **Found by running `bearing`,** on `main` at `4118a00` (#116 merged) with Python 3.12.10, on
   the fixture and on inputs a user can type: each phase's "Today" lines are what it printed.
   Chosen: a `--prs` file of the wrong shape, a traceback or a silent exit 0 (Phase 11); a
   `--prs` file that cannot be read, with no file named (Phase 12); dates in forms no one wrote
   down, and argparse's "invalid fromisoformat value" (Phase 13); `ingest`, the one command
   that prints git's text for a wrong repository (Phase 14); OS errors that print their path
   twice (Phase 15); and a config that is not UTF-8, a traceback (Phase 16).
2. **One track each, small enough for one sitting:** each day is one function or one `except`
   and a new test file, in `bearing/` and `tests/`. Days 19 and 20 touch the same `except`, and
   Day 21 the options Day 16 checks, so they run in this order.
3. **Decisions made here so the days need none,** proposed in this PR and the maintainer's by
   its merge: the six wordings above, word for word; records counted from 1 and the first
   failure reported; every field `save` stores checked for its type, and numbers for
   repeats; `gh`'s records not checked; `load_prs` unchanged; dates narrowed to YYYY-MM-DD,
   `20260121` and ISO week dates refused (Day 3's choice, reversed); `ingest`'s
   wrong-repository line from a check split out of Day 18's `check_commit`; `exc.strerror or
   exc` for an OS error.
4. **One day replaces a criterion:** Day 22 replaces C17.7 ("bearing: fatal: not a git
   repository"), which Day 17 adds, with a `Replaces:` line. Day 21 reverses Day 3's In scope
   choice of dates, which no criterion pins. No other test pins what these
   phases change: `tests/test_broken_store.py` and `tests/test_page_cli.py` pin Phase 15's
   lines by their start, which stays.
5. **Specs written ahead of their day,** as item 6 of the course correction after Phase 6:
   against `main` at `4118a00`, before the code of Days 15 to 18 has merged. Each day's
   spec-auditor run reads its spec against `main` as it is then, and a spec-change PR fixes what
   moved; the test counts assume the days before land as their specs say, from Day 18's
   "125 passed, (131 subtests passed)".
6. **This change breaks four holds, and four spec-change PRs re-pin them.** C15.8, C16.7, C17.10
   and C18.7 require `git diff --exit-code --name-only 85a21a1 -- .github .claude scripts
   pyproject.toml plan.md` to print nothing, and this PR edits `plan.md`. After it merges, and
   before Day 15's close, one spec-change PR per day (`day-15/spec-...` to `day-18/spec-...`)
   moves its criterion's base from `85a21a1` to this PR's merge commit, `plan.md` still in the
   list. Day 14's C14.5 leaves `plan.md` out, which is why the change after Phase 6 (#102) did
   not hit this. Days 19 to 24 take the same base.
7. **Not chosen.** `changelog --since` after the last merge prints "# Changelog" and exits 0:
   Day 16's Out of scope keeps it, and C03's `test_range` pins it. A `bearing.toml` that is not
   UTF-8, found by this PR's plan-auditor, is Phase 16. Everything the course correction after
   Phase 6 left unowned stays so.

### 2026-11-19: Course correction after Phase 6: Phases 7 to 10, one day each

The plan ended at Day 14, and the agentic-workflow-driver needs about 15 more pull requests,
each opened by the driver in a container, before its level 2 trial; with no day spec it stops
at "write its day spec". The maintainer adds four phases of one small day each, Days 15 to 18,
and their specs are written now, in one spec PR per day after this one. Each day was found by
reading the plan's open items and Notes and by running today's `bearing` on the fixture, not
made up for the count.

1. **Chosen, one gap each:** Day 8's known limit, coupling that does not follow renames
   (Phase 7); `bearing` with no command and `changelog` with `--since` after `--until`, both
   exit 0 with nothing useful (Phase 8); `ingest` on a repository without `main` (Phase 9); and
   `direction`'s errors on a wrong repository, raw git text where `timeline` and `page` give one
   line (Phase 10).
2. **Day 8's Out of scope is narrower than it reads.** "The fixture's one rename (#8) is in no
   pair at 2 or 3" holds for paths as changed. Followed, #2's `scripts/helpers.py` and #8's
   `scripts/tools.py` are one file, paired with `scripts/run.py` in 2 PRs: below the golden
   file's threshold of 3, so a CI test reaches the rename at 2 and no golden file changes. The
   Phase 5 entry said its effect shows only on the kit's history, and the Phase 6 entry that it
   needs a test repository of its own; both were wrong.
3. **Decisions made here so the days need none,** proposed in this PR and the maintainer's by
   its merge: a renamed file is named by
   its last name; a missing argument and dates out of order are argparse errors, exit 2, as
   every other argument error is; `--branch` defaults to `main` and asks `gh` for that base
   only; `direction`'s errors are `timeline`'s two lines, word for word.
4. **Phase 9 widens "Decisions"** (the hard parts table and Phase 1's `ingest` line): the
   history is the first-parent line of the branch `--branch` names, `main` when it names none.
   Those lines stay as written; this entry is where the change is recorded. Day 4 left "a ref
   other than `main`" out of scope; Phase 9 takes it in.
5. **Two days replace a criterion.** Day 15 replaces C08.6 (exactly three Coupling rows at
   `min_prs = 2`) and Day 17 replaces C04.2 (`gh`'s exact argument list), each with a
   `Replaces:` line. No other existing test pins what these phases change.
6. **Specs written ahead of their day.** `specs/README.md` writes each spec on its day, from
   `main`. These four are written against `main` at `714412f`, before Day 14's code has
   merged. Each day's spec-auditor run (CLAUDE.md, "A day, in order", step 1) reads its spec
   against `main` as it is then, and a spec-change PR fixes what moved; the test counts each
   spec gives assume the days before it landed as their specs say.
7. **The days stay in `bearing/` and `tests/`,** as Day 14 does: the driver's token cannot
   change `.github/`, `.claude/`, `scripts/` or this file. No new dependency and no contract
   change; each spec holds both with a `git diff --exit-code` criterion.
8. **Not chosen.** "e.g. " ending a sentence: Phase 6 made it a known limit days ago, and that
   decision stands. An opener that says nothing (#5) and a computed `bearing summary`: product
   decisions. `timeline`'s `#-` for a merge with no PR record, where `direction` gives the
   subject's number: the timeline's format is under contract. All stay unowned. The kit's
   H02.4 and the test data its dashboard reads as a hand-off "to Day 12" stay the kit's, fixed
   in its repository.

### 2026-11-12: Course correction after Phase 5: Phase 6, one small day

Phase 5 closed at Day 13 (#96), which left no new hand-off. The maintainer adds one phase of
one small day, Day 14, so the agentic-workflow-driver can run its first step inside a Docker
container on it; the day's size matters more than its content. It was chosen from three
candidates drawn from what this plan still left unowned (Course correction after Phase 4,
items 4 and 5).

1. **Chosen: the "one or two sentences" rule** (Course correction after Phase 1). One function,
   `what_i_built` in `bearing/ingest/text.py`, and no golden file: every fixture description is
   one sentence.
2. **The maintainer's decisions, made here so the day needs none:** what ends a sentence, that
   the cut keeps the first two sentences exactly as written with trailing whitespace stripped,
   and that "e.g. " is a known limit, not handled.
3. **Not chosen.** An opener that says nothing (#5's "...one commit each:"): what replaces it is
   a product decision. Coupling that follows renames: a test repository of its own, and its
   effect shows only on the kit's history. Both stay unowned, with `bearing summary` and the
   kit's H02.4.
4. **The day's work stays in `bearing/` and `tests/`:** the driver's token cannot change
   `.github/`, `.claude/`, `scripts/` or this file, and the day installs nothing new.

### 2026-11-10: Course correction after Phase 4: Phase 5, one day of loose ends

Phase 4 closed at Day 12 (#81) and the plan named nothing after it. The maintainer adds one
phase of one small day, Day 13, chosen from three candidates drawn from what the plan and the
Notes of Days 10 to 12 left unowned.

1. **Chosen: the two unowned hand-offs.** H03.1 (stderr is not UTF-8) and H04.2 (`gh`'s
   1000-PR cap), both listed as left open after Phase 3 (item 8 below). Two tracks, one each.
2. **The maintainer's decisions, made here so the day needs none:** H04.2 warns and does not
   paginate, with the line Phase 5 quotes; H03.1 makes stderr UTF-8 as stdout is; and Phase 5's
   "Done when" is checkable by CI alone.
3. **The warning also covers `--prs`.** A recorded file is the same `gh` command's output
   ("Decisions"), so it is cut at the same place, and a file is what a test can give without
   `gh`. Exactly 1000 records may be a whole history; the line says what the limit does, not
   that anything is missing.
4. **Not chosen.** A computed `bearing summary` (the optional summarising layer of
   "Decisions"): a new output contract whose shape is a product decision. Coupling that follows
   renames (Day 8's known limit; 43 Coupling rows on the kit at Day 10): its effect shows only
   on the kit's history, which CI cannot reach.
5. **Still left open; no day owns them:** `README.md`, still the kit's own on `main` (#86, open
   on this date, rewrites it outside any day); the Phase 1 stop's
   "one or two sentences" rule for a description; the two not chosen in item 4; and, in the
   kit, H02.4 and the test data the dashboard reads as a hand-off "to Day 12".
6. **`.gitignore`** gains `evidence.json`, the report `scripts/evidence.py` writes after a
   close, and `evidence-rehearsal.json`, which no script here names and the maintainer asked
   for: left untracked they make the tree unclean, and the driver stops on an unclean tree.

### 2026-11-05: Course correction after Phase 3: the Day 10 stop

The Phase 3 stop (H10.1). The plan-auditor ran on Phase 3, on Phase 4 and on the whole plan, on
fresh `main` at `b352eb2`. All three say to go on to Phase 4 once this entry is made, and none
found code that argues against the page. Items 1 to 4 are the maintainer's decisions.

1. **The page is built, and nothing is cut.** Phase 4 stays as planned, Days 11 and 12.
   Coupling and cycles were built before the stop (Course correction before Phase 3, item 5),
   and the schedule has not slipped: 66 PRs in 10 days. Whether Bearing is proposed to the kit
   is a kit decision, made in the kit's repository, not here.
2. **The page marks its flags as unverified.** Phase 3's bar was met with no margin: "Marks:
   real 13, rule 13" (`docs/kit/flags.md`, #64). The rules were fitted to the same history that
   judged them, the kit at `c12cfe5`. Two of the 13, #16 and #31, are low-confidence marks
   where a blind Fable reading differed; under Fable's marks alone the count is 11. So the page
   shows each flag as unverified: its rules have not been judged on a history they were not
   fitted to. There is no new run and no new marking. Coupling's hidden-dependency column
   (91 of the kit's 133 rows) was never judged either: the noise bar covered said vs done only.
3. **Layers in an import cycle.** "Decisions" gave a module's layer as its longest import path
   from a module nothing imports, and that is undefined inside a cycle. The fixture's `app.a`
   and `app.b` import each other from #3 until #9 removes it, in four of the page's steps
   (#3, #5, #6 and #8, by the changelog's dates). Each cycle
   is now one node for layering (Decisions).
4. **The kit is copied in at `9a50a3e`** (kit #96), in a kit-update PR after this one: a split
   in the measurement. Bearing's kit files are `c12cfe5` plus four area-branch PRs that changed
   them here, against "Constraints", with no Course correction (9 files, +216/-19 since
   `e994832`):
   - #38 `scripts/evidence.py` and its test: it rewrites `main` only in git commands on this
     repository;
   - #49 `scripts/seen-red.py` and its test: it drops the editable install's finder in its run
     on the base;
   - #55 `scripts/spec-drift.py`, `scripts/close-evidence.py`, `scripts/evidence.py`, their
     tests and `.github/workflows/dashboard.yml`: the replay report at build, fixtures out of
     the tests ratio, and two attention rules;
   - #56 `scripts/spec-drift.py` and its test: a reader's "Not proven" line counts as cited.

   The kit-update PR states, for each one, whether the kit at `9a50a3e` has it or it stays
   Bearing's, as the Phase 1 stop did, and records the models and the Claude Code version.
5. **Tokens: no split at a kit copy.** `--split` takes a day and counts `day >= d`. The copy at
   `c12cfe5` (#30) and every PR since fall on 2026-11-04 or 2026-11-05, so no date separates
   before and after it. `python scripts/token-usage.py --compare --split 2026-11-05` separates
   the two days only, main sessions only: before, 1,426 replies, $79.44, 47 PRs merged on
   2026-11-04, 30.3 replies per merged PR; after, 810 replies, $42.74, 19 PRs, 42.6 replies per
   merged PR. A split at a kit-update PR needs a time or a PR number in the kit's
   `token-usage.py`; that is a kit fault, for the kit. Until then Bearing's windows are days.
   Merged PRs per rung, #30 to #66, from the merged branches: day spec 30 (#32–#37, #39–#48,
   #50–#54, #57–#59, #61–#66), area branch 7 (#30, #31, #38, #49, #55, #56, #60), short spec 0.
6. **Phase 4's premises, for Day 11's spec to settle:**
   - The command's arguments. Every other command takes `repo` and `--data`, and flags need
     `--config` (only `direction` reads it today), so the spec gives `bearing page`'s full
     arguments and what a missing config does. ("Decisions" also writes
     `bearing snapshot <ref>`; the code takes `repo ref`.)
   - A merge with no PR record: the timeline prints `#-` and `direction` prints the merge
     subject's number (the fixture's #11). The spec picks the page's number and title.
   - A check that can fail if the layout changes between runs: `page-v1` holds no positions,
     and the HTML is not under contract.
   - `<` escaped in the embedded JSON. The kit's #18 has `</script>` in its body; the page is
     safe today only because it lies outside "What I built".
   - The graph is SVG drawn in Python with Mermaid's look, not Mermaid: the maintainer's choice.
   - The paragraph is the changelog's, as "Output contracts" says. The Phase 1 stop's "one or two
     sentences" rule stays unowned.

   Phase 4's "Done when" now names the kit's history it runs on: `c12cfe5` with
   `docs/kit/bearing.toml`, where the flags were judged (94 merges).
7. **Corrected here.** Item 1 of the round 1 entry below said round 1's 17 `real` flags survive
   a fix of all four causes; D10.17 showed 13 do under the `shared` list chosen, and round 2
   gave 13. The lab notebook's Day 10 entry now names #65, counts D10.20, and records that CI's
   replay of #65's merge failed before #66.
8. **Left open; no day owns them:** H03.1 (stderr is not UTF-8); H04.2 (`gh`'s 1000-PR cap;
   the kit has 96); H02.4 in the kit, a check that a `manifest:` line replays, of which D10.19
   and D10.20 are new cases; test data in `scripts/test_spec_drift.py` that the dashboard reads
   as a hand-off "to Day 12", a kit fault; and `README.md`, still the kit's own, with none of
   the Findings CLAUDE.md says it keeps.

### 2026-11-05: Course correction at the Day 10 stop: the kit's flags, round 1

The maintainer's marks on the 72 flags of `docs/kit/direction.md` (Day 10 Track A, #59), kept
in [`docs/kit/flags-round-1.md`](docs/kit/flags-round-1.md): real 17, rule 55. Fewer than
half, so Track B does not open (Phase 3's "Done when"; H10.2). The maintainer took the marks
of a Fable reading of each flagged PR's diff and body at `c12cfe5`, over 39 `real` that Claude
had first proposed from the file names alone; and chose the fix in item 2.

1. **Where the noise came from.** Four causes, by that reading; 13 of the 17 `real` flags
   survive a fix of all four with the `shared` list chosen (D10.17; corrected after Phase 3):
   - `kit/` is given to `docs`, but it holds tools (`kit/replay/`, `kit/compare-page.py`), the
     page's fixtures and the change record.
   - The `dashboard` area misses the dashboard's own files: its test workflow, its config, its
     demo data, the page comparison and the hash it writes.
   - Shared text is edited from every area to record or document the PR's own change:
     `kit/CHANGES.md` and `kit/SOURCE.md` (at the root before the kit's #15), `CLAUDE.md`,
     `README.md`, `AGENTS.md`, `plan.md`, `specs/README.md` and the spec templates.
   - Root tool configuration (`.gitignore`, `.gitattributes`, `.flake8`) has no area.
2. **The outside-area rule takes a `shared` list.** `[rules.outside-area] shared = [<path
   prefixes>]`: a PR's file under one of them is never outside its area. Without the key the
   rule is as today, so the fixture's report and its golden file do not change. Listing the
   shared files under every area instead needs no code, but a file's area is the first that
   lists it, so churn and coupling would count them in the wrong area.
3. **Round 2.** The kit's `bearing.toml` is fixed for the first, second and fourth causes, and
   its `shared` list holds the third's files, all from round 1's reading and before the new
   report is made. The report is made again at `c12cfe5`, and the maintainer marks every flag
   it prints, as in round 1. The bar stays at least half `real`, and neither the config nor the
   rule changes after round 2's first mark. A Day 10 spec-change PR sets the tracks: the
   `shared` key and its test, the new config and report, then the marks (C10.5's 72 becomes the
   new report's count).

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
6. Phase 5: Day 13.
7. Phase 6: Day 14.
8. Phase 7: Day 15.
9. Phase 8: Day 16.
10. Phase 9: Day 17.
11. Phase 10: Day 18.
12. Phase 11: Day 19.
13. Phase 12: Day 20.
14. Phase 13: Day 21.
15. Phase 14: Day 22.
16. Phase 15: Day 23.
17. Phase 16: Day 24.
