# Day 11 — `bearing page`: the page data, its golden file, and the layered layout

**Phase:** 4 · **Depends on:** Day 10 · **Expected PRs:** 5 (this spec, track A, track B, track C, the close)

## Goal
`bearing page repo --data DIR --config FILE --out FILE` writes one HTML file whose embedded
`page-v1` data matches its golden file on the fixture (10 steps, one per merge), a `<` in any
PR text cannot end the data's element, and the layered layout plan.md's "Decisions" defines
exists as a function whose result on the fixture is pinned and does not change with the
process's hash seed.

## In scope
Each of plan.md's "Course correction after Phase 3", item 6, premises is settled here; the
plan-auditor's Phase 4 report (this spec's PR) is answered in "Why this approach" there.

- **The command** (Track A, errors Track B):
  `bearing page repo [--data DIR] [--config FILE] --out FILE`. `repo` and `--data` (default
  `.bearing`) as `timeline` and `direction` take them; `--config` (default `bearing.toml`) as
  `direction` takes it; `--out` is required. It prints nothing on stdout on success, and writes
  the file as UTF-8 bytes with `\n` line endings, whatever the platform.
  - Errors (Track B), in this order, each one line on stderr after `bearing: `, exit 1, and,
    for every error raised before the file is opened, the `--out` file neither created nor
    changed (everything is computed before the file is opened; a write that fails part-way is
    not promised to leave it whole):
    the config, read first with `load_config` and `load_rules`, so a missing one is C08.7's
    "no config at <path>: pass --config FILE" whatever the store holds; a missing store,
    "no store at <data>/bearing.db: run bearing ingest first", as `timeline`; a `SnapshotError`
    (a store from another repository), its message; a `sqlite3.Error`,
    "cannot read store at <db>: <error>"; an `OSError` writing the file,
    "cannot write <out>: <error>". A missing config is an error, not a page without flags:
    flags are part of every step (plan.md, Phase 4), and a page that silently drops them
    would read as "no flags".
  - The store is checked to exist before `open_store` opens it (which would create one), and
    read through a `BlobCache`, as `timeline` does.
  - For each merge, its snapshots are read before its changed files, as `timeline` reads
    them, so a store from another repository fails on the first merge's snapshot with one
    line, "not a commit: <sha>", not git's three-line message that `changed_files` gives.
  - plan.md's Phase 2 writes `bearing snapshot <ref>`; the code takes `repo ref`
    (`bearing/cli.py`). Not changed here.
- **`page-v1`** (Track A), `bearing/page/data.py`: `{"version": "page-v1", "steps": [...]}`,
  one step per commit of kind `merge`, in first-parent order (`ORDER BY position`), so the step
  count is `bearing ingest`'s `merges` (H05.3). Each step has exactly these keys:
  - `sha`: the merge's full SHA; `date`: its committed date, `committed_at[:10]`, as the
    changelog dates it;
  - `number`, `title`, `paragraph`: the changelog's choice (`read_entries`,
    `bearing/ingest/changelog.py`). With a PR record: its number, its title, and
    `what_i_built(body)`. Without one: the merge subject's number (`subject_number`, JSON
    "null" when the subject names none), the subject as the title, and the empty string. The
    fixture's #11 is 11, "Merge pull request #11 from acme/tooling/ci", and the empty string.
    The timeline's "#-" stays the timeline's.
  - `events`: the strings `structure_events` gives for the merge against its first parent,
    in its order, the timeline's lines without their `<sha7> #<n> ` prefix; `[]` when none.
  - `flags`: `[{"rule": ..., "claim": ..., "files": [...]}]`, the flags `bearing direction`
    prints for this merge, in its order: `said_vs_done` on this one merge's
    `(number, branch, body, paths)`, with direction's number, branch
    (`COALESCE(prs.head_ref, commits.subject_branch)`), body (the `prs` row of that number,
    `None` without one) and `changed_files` paths. Keyed to the step by the merge, never by
    number: a step whose number is null has no flags, whatever its branch. An empty list when
    none.
  - The paragraph is the changelog's whole paragraph (plan.md, "Output contracts"); no
    shortening (Notes).
- **The embedding** (Track A writes it plain, Track B escapes it), `bearing/page/html.py`,
  `render(data)` returns the page's text. The data's element is exactly
  `<script id="bearing-data" type="application/json">` + TEXT + `</script>`, where TEXT is
  `json.dumps(data, sort_keys=True, indent=2) + "\n"` with `ensure_ascii` at its default (so
  the "→" in a kit paragraph, #16's, is `\u2192`), and, Track B, every `<` in it written `\u003c`.
  JSON reads `\u003c` as `<`, so `json.loads(TEXT)` is the data, and the golden file is TEXT's bytes: the
  fixture's PR text holds no `<`, so the escape does not change it. The HTML around the element
  is not under contract; on Day 11 it is a shell (`<!doctype html>`, `<meta charset="utf-8">`,
  `<title>Bearing</title>`, the element), and Day 12 draws in it.
- **The golden file and its contract test** (Track A): `tests/fixtures/expected/page-v1.json`
  (138 lines, from the prototype of "Why this approach"), and `tests/contract/test_page.py`,
  which builds the fixture, ingests it, runs `bearing page` with `tests/fixtures/bearing.toml`,
  takes TEXT from the element by its id, and compares it with the golden file's bytes after
  `\r\n` is read as `\n`. New files: no existing contract test or golden file changes.
- **The layout** (Track C), `bearing/page/layout.py`, `layers(modules, imports)`: `modules`
  an iterable of module names, `imports` an iterable of `(importer, imported)` pairs, as a
  snapshot's `modules[*].name` and `imports` give them. It returns a list of layers, top
  first, each a list of module names in name order (`sorted`). As plan.md's "Decisions":
  each strongly connected component of the import graph is one node, every other module a node
  of its own; a node's layer is its longest import path from a node nothing imports (layer 0);
  a module takes its node's layer. An import whose end is not in `modules`, and a module
  importing itself, are ignored. The result depends on neither the order nor the hash seed:
  every set is sorted before it is walked. Iterative, or recursive with a depth the kit's
  graph cannot reach; no crossing minimisation, no positions (Day 12 draws). Not yet called
  by `bearing page`: Day 12 draws from it (H11.1).

## Out of scope
- The graph drawn as SVG in Python with Mermaid's look, the step-through controls, flags shown
  marked unverified, the HTML's bytes compared under two hash seeds, the kit's run (94 steps,
  `grep -c -E 'src=|href="http'` printing 0, #18's `</script>`), and the browser screenshots —
  Day 12 (H11.1).
- A `page-v1` key marking flags unverified: every flag is unverified, so the mark is the page's
  wording, checked on Day 12's HTML (H11.1); the data stays what direction found.
- Mermaid itself, and `bearing snapshot --format mermaid` — not in plan.md (the maintainer's
  choice: the look, not the library).
- Paragraph length ("one or two sentences", the Phase 1 stop) — no day owns it (plan.md,
  Course correction after Phase 3, item 6).

## Tracks

Run in the order A, B, C: B's escape and errors are added to A's command; C stands alone and
may go first if A waits.

| Track | Owner | Work |
|---|---|---|
| A | implementer | C11.1–C11.3 (about 400 changed lines, the golden file's 138 included: if the diff passes 400, split the CLI tests C11.2 and C11.3 off into a track A2 branched after A merges, never an `Oversized:` line without the maintainer): `bearing/page/__init__.py` (C creates it if C goes first), `bearing/page/data.py`, `bearing/page/html.py` (plain embedding), `page` in `bearing/cli.py` with no error handling of its own, `tests/fixtures/expected/page-v1.json`, `tests/contract/test_page.py`, `tests/test_page_cli.py` |
| B | implementer | C11.4–C11.5: the `<` escape in `render`, the command's errors and the untouched `--out`; tests in `tests/test_page_cli.py` and `tests/test_page_html.py` |
| C | implementer | C11.6–C11.7: `bearing/page/layout.py`, `tests/test_layout.py` |

C11.8 and C11.9 are `hold`; their breaks run in this spec's PR.

## Acceptance criteria
Tick each box in the closing PR once its evidence is in it; under a box left unticked, write
`Not proven: <why>` (`specs/README.md`, "Evidence at the close").

- [ ] C11.1 **new** — On the fixture, after `bearing ingest` with the fixture's `prs.json`,
      `bearing page <repo> --data <dir> --config tests/fixtures/bearing.toml --out <file>`
      exits 0, prints nothing on stdout, and the element `bearing-data`'s text equals
      `tests/fixtures/expected/page-v1.json` byte for byte (after `\r\n` is read as `\n`):
      10 steps, in the order 62c4b2f, 1756282, 4a6b109, 00394fb, bd726c8, 448fc4d, fde93a4,
      e5fa51f, 86761f2, 8c1b9f1, numbers 1, 2, 4, 3, 5, 6, 8, 9, 10, 11; 21 events in all
      (4, 3, 0, 6, 0, 2, 3, 3, 0, 0), the timeline golden file's 21 lines in its order;
      flags only on #5 (`outside-area`, "area docs", `scripts/run.py`) and #9
      (`contract-impact`, "no contract impact", `tests/contract/test_api.py`).
      Red today: there is no `page` command ("invalid choice: 'page'").
      Test: `tests/contract/test_page.py::PageContractTest::test_golden`.
- [ ] C11.2 **new** — A merge without a PR record takes the changelog's number, title and
      paragraph: on the fixture, step 10 (8c1b9f1) is `11`, "Merge pull request #11 from
      acme/tooling/ci", and the empty string (pinned by C11.1's golden file); and, with C10.2's
      config (`tooling = ["scripts/"]`) and the store's `subject_number` of 8c1b9f1 set to NULL
      and its subject to "Merge branch x" (an UPDATE on the ingested store; `subject_branch`
      stays "tooling/ci", so a page that ran `said_vs_done` on that merge would flag `ci.txt`),
      step 10 has number null, title "Merge branch x", the empty paragraph, and no flags; and
      the written file's bytes hold no carriage return (a check that bites only on Windows,
      where text mode would add one; CI runs on Linux).
      Red today: no `page` command.
      Test: `tests/test_page_cli.py::PageCliTest::test_merge_without_number`.
- [ ] C11.3 **new** — A step's flags are the ones `bearing direction` prints for its merge,
      keyed by the merge: on the fixture with C10.2's config (`tooling = ["scripts/"]`,
      without `ci.txt`), the steps' flags, written `- #<number> <rule>: <claim> | <files>`
      in step order, equal direction's Said vs done lines for the same config, and #11's
      step (8c1b9f1), which has no PR record, holds one flag: rule "outside-area", claim
      "area tooling", files "ci.txt".
      Red today: no `page` command.
      Test: `tests/test_page_cli.py::PageCliTest::test_flags_match_direction`.
- [ ] C11.4 **new** — `render` cannot be ended or commented out by PR text: for data whose
      step title is `</script><script>alert(1)</script>` and whose paragraph holds
      `<!-- PROJECT: x -->` (the kit's #14 holds such a line), the output contains `</script`
      (any case) exactly as many times as it contains `<script` (any case), the element's
      text contains no `<`, and `json.loads` of it gives back both strings unchanged.
      Red today: no `bearing.page` package; after Track A, `</script` is counted 3 times
      against 2 opening tags.
      Test: `tests/test_page_html.py::RenderTest::test_script_end_is_escaped`.
- [ ] C11.5 **new** — The command's errors leave `--out` alone: (a) with `--config` naming a
      missing file and no store, exit 1, stderr "bearing: no config at <path>: pass --config
      FILE", and `--out` not created; (b) with the fixture's config and no store, exit 1,
      stderr "bearing: no store at <data>/bearing.db: run bearing ingest first", `--out` not
      created; (c) with a store ingested from the fixture and `repo` an empty `git init`
      directory, exit 1, stdout empty, stderr exactly "bearing: not a commit: <the full SHA of
      62c4b2f>", and an `--out` file written beforehand with the bytes "keep" still holds
      exactly "keep"; (d) with `--out` naming an existing directory, exit 1 and stderr starting
      "bearing: cannot write ".
      Red today: no `page` command; after Track A, (a) ends in a ConfigError traceback, (b)
      exits 0, creates the store and writes a page of no steps, (c) ends in a SnapshotError
      traceback, and (d) in an OSError traceback.
      Test: `tests/test_page_cli.py::PageErrorTest::test_missing_config`,
      `tests/test_page_cli.py::PageErrorTest::test_missing_store`,
      `tests/test_page_cli.py::PageErrorTest::test_error_keeps_out` and
      `tests/test_page_cli.py::PageErrorTest::test_out_is_a_directory`.
- [ ] C11.6 **new** — `layers` gives plan.md's layout: for modules `a b c d` and imports
      `a→b, b→a, c→a, a→x, d→d`, it returns `[["c", "d"], ["a", "b"]]`, and the same for the
      imports in reverse order; on the fixture's snapshots it returns, at 00394fb (#3, the
      cycle), `[["app", "app.a", "app.b", "app.crlf", "app.legacy", "app.sub", "app.sub.mod",
      "lib", "lib.util", "scripts.run"], ["app.core", "app.pkg", "scripts.helpers"],
      ["scripts.config"]]`, and at e5fa51f (#9, the cycle broken) app.b moves to layer 1:
      `[["app", "app.a", "app.broken", "app.crlf", "app.extra", "app.sub", "app.sub.mod",
      "lib", "lib.util", "scripts.run", "tests.contract.test_api"], ["app.b", "app.core",
      "app.pkg", "scripts.tools"], ["scripts.config"]]`.
      Red today: no `bearing.page.layout` ("No module named 'bearing.page'" before Track A,
      "No module named 'bearing.page.layout'" after it).
      Test: `tests/test_layout.py::LayoutTest::test_cycle_is_one_node` and
      `tests/test_layout.py::LayoutTest::test_fixture_layers`.
- [ ] C11.7 **new** — The layout does not change between runs: a child Python process that
      prints `layers` for each of the fixture's 10 merges' snapshots, one JSON line each,
      prints the same bytes under `PYTHONHASHSEED=0` and `PYTHONHASHSEED=1`, and 10 lines.
      Red today: no `bearing.page.layout`.
      Test: `tests/test_layout.py::LayoutTest::test_same_under_two_hash_seeds`.
- [ ] C11.8 **hold** — No existing contract test or golden file changes:
      `git -c core.safecrlf=false diff --exit-code --diff-filter=MD 3843f3b -- tests/contract tests/fixtures/expected`
      prints nothing and exits 0 on the closing commit (new files, `test_page.py` and
      `page-v1.json`, are not M or D).
- [ ] C11.9 **hold** — The changelog, timeline and direction contract tests pass unedited:
      `python -m pytest -q tests/contract` passes on every track's head (Track A may move
      direction's merge query into a shared function; the output may not change).

## Verify
```bash
python -m pytest -q tests/contract tests/test_page_cli.py tests/test_page_html.py tests/test_layout.py
git -c core.safecrlf=false diff --exit-code --diff-filter=MD 3843f3b -- tests/contract tests/fixtures/expected
ruff check . && ruff format --check .
python -m pytest -q
```

The full run reads "89 passed" (78 on `3843f3b`, plus 1 contract, 2 in `PageCliTest`, 4 in
`PageErrorTest`, 1 in `RenderTest`, 3 in `LayoutTest`) and the 107 subtests; the close
re-counts it.

## Notes
- The fixture's PR text has no `<` (`grep -n "<" tests/fixtures/make_repo.py` finds only usage
  strings), so the golden file cannot show the escape; C11.4 tests it on strings. The kit's
  text has `<` in eight PRs (plan-auditor, Phase 4: paragraphs of #14, #33, #40, #61, #87,
  #88, #90, #91, and #87's title); #14's `<!-- PROJECT: ... -->` would change how a browser
  reads the element. Day 12's kit run checks it on a real file (H11.1).
- C11.7 compares two processes because string hashing is seeded per process: two runs in one
  process cannot see set order change. The fixture's layer 0 holds 7 to 11 names across the
  10 merges, enough for an unsorted set to come out in another order under another seed.
  Strongly connected components and longest paths on a DAG are unique, so C11.7 can fail only
  where a layer is left unsorted, which C11.6 also catches; the seed risk that matters is Day
  12's drawing, whose bytes H11.1 compares the same way.
- The layout's layer 0 is wide on the fixture (every module nothing imports, packages
  included); that is plan.md's simplest layout, kept, and Day 12 draws it as it is.
- Flags are computed per merge, so two merges sharing a number (possible without records)
  each get their own; direction's report is unchanged.
- Paragraphs on the kit run from 16 to 1159 characters (plan-auditor; a median of 299 on the
  94 merges' records, 296 on all 97 records the spec-auditor read); the page shows them whole.
  The "one or two sentences" rule stays unowned.
- `scripts/test_spec_drift.py` holds test data the dashboard reads as a hand-off "to Day 12"
  (plan.md, Course correction after Phase 3, item 8): it shows unpicked unless Day 12's spec
  names that file; a kit fault either way.
- **Defect** D11.1 — found: auditor · cause: process · made: Day 11 · same-as: D01.21 · the
  Write tool turned the spec's two JSON escapes into the characters they stand for, so the
  embedding rule read "every `<` written `<`"; restored with a script that writes the
  backslash, and read back, in this PR.
- **Defect** D11.2 — found: auditor · cause: spec · made: Day 11 · C11.2's no-flags check for
  a merge without a number ran under the fixture's config, where #11 has no flag anyway; now
  under C10.2's config, in this PR.
- **Defect** D11.3 — found: auditor · cause: spec · made: Day 11 · C11.5's red after Track A
  was wrong for (b), which exits 0 and creates the store, and (c), which prints a traceback;
  restated, and the store's existence checked before `open_store`, in this PR.
- **Defect** D11.4 — found: auditor · cause: spec · made: Day 11 · C11.5 (c)'s one-line
  stderr depended on an order the spec did not pin (snapshot before changed files); pinned,
  with the exact message, in this PR.
- **Defect** D11.5 — found: auditor · cause: spec · made: Day 11 · three promised errors had
  no criterion and "`--out` not changed" could not hold for a failed write; (d) added and the
  promise narrowed, in this PR. The SnapshotError and `sqlite3.Error` messages are reused
  from `timeline`; only (c) checks one.
- **Defect** D11.6 — found: auditor · cause: spec · made: Day 11 · Track A's estimated diff
  (about 410–440 lines) had no plan; the record half of C11.2, already pinned by the golden
  file, lost its test, and the Tracks table names the split, in this PR.
- **Defect** D11.7 — found: auditor · cause: spec · made: Day 11 · same-as: D10.10 · literal
  output values were in backticks; quoted, in this PR.
- **Hand-off** H11.1 → Day 12: draw the graph from `layers` as inline SVG with Mermaid's look
  (one box per module, arrows for imports, layers top to bottom; this merge's added modules
  and imports green, removed ones faded, a cycle red); the step-through controls; every flag
  shown with the word "unverified" (a test on the HTML text); the HTML's bytes the same under
  `PYTHONHASHSEED=0` and `1`; and plan.md's Phase 4 "Done when" on the kit at `c12cfe5` with
  `docs/kit/bearing.toml` (94 steps, `grep -c -E 'src=|href="http'` printing 0, `</script`
  counted as `<script`), with a checked-in artefact or the command quoted in the close, since
  CI cannot reach the kit, and the maintainer's two screenshots.
