# Day 12 — `bearing page`: the timeline page, its graph and its controls

**Phase:** 4 · **Depends on:** Day 11 · **Expected PRs:** 6 (this spec, a spec change, track A, track B, track C, the close)

## Goal
`bearing page` writes one HTML file that steps through the history one merge at a time: each
step shows its merge, its structure change, its PR title and "What I built", every flag on it
marked unverified, and its import graph drawn as inline SVG in Mermaid's look from Day 11's
`layers`; the file's bytes do not change with the hash seed, and on the kit at `c12cfe5` it has
94 steps and no external reference (plan.md, Phase 4 "Done when"; H11.1).

## In scope
- **The drawing** (Track A), `bearing/page/svg.py`, `draw(old, new, events)`: `old` and `new`
  a merge's first-parent and merge snapshots (`snapshot-v1` dicts), `events` that step's
  `page-v1` events. It returns one `<svg>` element as a string, no `xmlns`, no `href`, no
  `src`, no `style` attribute: the look is the page's CSS, keyed on classes.
  - **What is drawn:** `new`'s modules, plus each module a `-module X` event names; `new`'s
    imports, plus each import a `-import A -> B` event names, when both its ends are drawn.
    A renamed module is drawn under its new name only, as the events call it renamed, not added.
  - **Where:** `layers(drawn modules, drawn imports)` gives the rows, top first. Each module is
    one box, 32 high and `8 * len(name) + 24` wide; in a layer, boxes go left to right in name
    order, 16 apart, and a box whose right edge would pass x = 960 starts a new row of the
    same layer (unless it would be the row's first). Rows of one layer are 24 apart; layers are
    48 apart. The first row starts at x = 16 and its top is y = 16. The SVG's `width` and `height` are the largest right and bottom edge plus 16.
    No crossing minimisation; the same input gives the same bytes.
  - **How it reads:** one `<g class="module ..." data-name="X">` per module holding a `<rect>`
    and a `<text>` with the name; one `<g class="import ..." data-from="A" data-to="B">` per
    import holding a straight `<path>` from the bottom centre of the importer's box to the top
    centre of the imported one's, ending in an arrowhead marker defined inside the SVG (the
    attribute marker-end set to "url(#arrow)", not an `href`).
    Imports come before modules, so boxes sit over lines. A module name is written with
    `html.escape` in both its `<text>` and its `data-` attributes: names come from file paths,
    which may hold `&` or `<` (`bearing/snapshot/modules.py`). The class list adds, in this order:
    `added` when a `+module X` or `+import A -> B` event names it; `removed` when a
    `-module X` or `-import A -> B` event names it; `cycle` when it is not removed and it
    (a module) is in, or (an import) has both ends in, one strongly connected component of
    `new`'s import graph of more than one module.
  - The page's CSS gives Mermaid's flowchart look: boxes `#ECECFF` with a `#9370DB` border and
    rounded corners, text `#333`, arrows `#333333`; `added` green (`#D4F7D4`, border
    `#2E8B57`), `removed` faded (opacity 0.4, dashed), `cycle` a red border or line
    (`#D33`, 2 wide). An `added cycle` box is green with a red border.
- **The page** (Track B), `bearing/page/html.py`, `render(data, graphs=None)`: the
  `bearing-data` element as Day 11 left it, then one `<section class="step"
  data-sha="<sha>">` per step in step order, all but the first `hidden`. Each holds, HTML-escaped
  (`html.escape`, so no PR text can open or close an element): a heading with the step's
  position ("Step 1 of 10"), date, "#" and number (no "#" when the number is null) and title;
  the paragraph in a `<p>`, left out when empty; the events, one `<li>` each in a
  `<ul class="events">`, left out when none; the flags, one `<li class="flag">` each in a
  `<ul class="flags">`, written `unverified: <rule>: <claim> (<files joined by ", ">)`, left
  out when none; and `graphs[i]`, when `graphs` is given. Above the steps: one line saying
  what "unverified" means ("Flags are unverified: their rules have not been judged on a
  history they were not fitted to." — plan.md, Course correction after Phase 3, item 2), two
  buttons `id="prev"` "Previous" and `id="next"` "Next", and `<span id="counter">` holding
  "1 / N". One `<style>` in the head, and one `<script>` after the steps, inline, with no
  `src`: the buttons and the ArrowLeft and ArrowRight keys show the previous or next section
  and set the counter; the first and last step stay where they are.
- **The graph in the page** (Track C): `bearing page` passes `render` one `draw(old, new,
  events)` per step, from the same two snapshots `page_data` reads for that step's events.
  `page-v1` does not change.
- `scripts/test_spec_drift.py`'s test data, which the dashboard reads as a hand-off "to Day 12"
  (plan.md, Course correction after Phase 3, item 8; Day 11's Notes): named here so it shows as
  picked up. It is a kit fault and is not changed in this repository.

## Out of scope
- A `page-v2` holding positions or classes: the drawing is the HTML's, which is not under
  contract; `page-v1` stays (plan.md, Course correction after Phase 3, item 6).
- Mermaid itself, `bearing snapshot --format mermaid`, crossing minimisation, zoom, and a
  summarising layer — not in plan.md (the maintainer's choice: the look, not the library).
- Paragraph length ("one or two sentences", the Phase 1 stop) — no day owns it.
- H03.1, H04.2 and the kit's H02.4 — left open by plan.md (Course correction after Phase 3,
  item 8); no day owns them.

## Tracks

Run in the order A, B, C: C joins A's drawing to B's page. A and B stand alone, and B may go
first if A waits.

| Track | Owner | Work |
|---|---|---|
| A | implementer | C12.1–C12.2: `bearing/page/svg.py`, `bearing/page/layout.py` (a public `components` for the cycle class, if `draw` reuses `_components`), `tests/test_page_svg.py` |
| B | implementer | C12.3–C12.6: `bearing/page/html.py`, `tests/test_page_html.py` |
| C | implementer | C12.7–C12.8: `bearing/page/data.py`, `bearing/cli.py`, tests in `tests/test_page_html.py` |
| close | main session | C12.10: the kit's run, its evidence the Verify commands' output |

C12.9 is `hold`; its break runs in this spec's PR. The close row is the closing PR, not a track:
no track branch carries it.

## Acceptance criteria
Tick each box in the closing PR once its evidence is in it; under a box left unticked, write
`Not proven: <why>` (`specs/README.md`, "Evidence at the close").

- [ ] C12.1 **new** — `draw` draws and marks what the In scope says. With `old` holding
      modules `a`, `b`, `gone`, `keep` and imports `a -> gone`, `b -> keep`, and `new` holding
      modules `a`, `b`, `c`, `keep` and imports `a -> b`, `b -> a`, `c -> keep`, `b -> keep`,
      and events "+module c", "-module gone", "+import a -> b", "+import b -> a",
      "+import c -> keep", "-import a -> gone", "cycle+ a > b > a": the `<g class="module ...">`
      elements are, by `data-name` and class, `a` "module cycle", `b` "module cycle", `c`
      "module added", `gone` "module removed", `keep` "module"; the imports, by `data-from`,
      `data-to` and class, `a -> b` "import added cycle", `b -> a` "import added cycle",
      `a -> gone` "import removed", `b -> keep` "import", `c -> keep` "import added"; every
      `import` element comes before the first `module` element; and the string holds none of
      "xmlns", "href", "src", "style=". And with `new` holding one module "a&b<c" and no
      events, its `<text>` holds "a&amp;b&lt;c" and `html.parser` reads its `data-name` as
      "a&b<c".
      Red today: there is no `bearing.page.svg` (the test imports it when it runs, so it fails,
      not errors at collection: D11.13).
      Test: `tests/test_page_svg.py::DrawTest::test_classes`.
- [ ] C12.2 **new** — The boxes follow `layers`, top to bottom, in name order, wrapped at 960.
      With 41 modules "top" and "m00" … "m39", and "top" importing every "m" module: "top"
      is the only box in the first row, at x = 16 and y = 16; every "m" box's `y` is greater
      than "top"'s; the "m" boxes, each 32 high and 48 wide (64 apart from left edge to left
      edge), take three rows of 15, 15 and 10, the first "m" row at y = 96 (16 + 32 + 48) and
      the next two 56 lower each (32 + 24); within each row the `x` values rise with the
      names; no box's right edge passes 960; no two boxes overlap; and the SVG's `width` is
      the largest right edge plus 16.
      Red today: no `bearing.page.svg`.
      Test: `tests/test_page_svg.py::DrawTest::test_positions`.
- [ ] C12.3 **new** — On the fixture, `render` writes one `<section class="step">` per step:
      10, in `page-v1`'s order by `data-sha`, the first without `hidden` and the other nine
      with it; section 4 (00394fb) has the heading text "Step 4 of 10", "2026-01-14", "#3"
      and "day-02/track-a-cycle", its 6 events as 6 `<li>` in order, and no `ul.flags`; section 10
      (8c1b9f1) has "#11", "Merge pull request #11 from acme/tooling/ci", and no `<p>`. Read
      with `html.parser` on `bearing page`'s output (`tests/fixtures/bearing.toml`).
      Red today: the page has no section ("0 != 10").
      Test: `tests/test_page_html.py::PageHtmlTest::test_sections`.
- [ ] C12.4 **new** — Every flag is shown as unverified: on the fixture the file holds exactly
      two `<li class="flag">`, in section 5 (bd726c8) "unverified: outside-area: area docs
      (scripts/run.py)" and in section 8 (e5fa51f) "unverified: contract-impact: no contract
      impact (tests/contract/test_api.py)", and the line "Flags are unverified: their rules
      have not been judged on a history they were not fitted to." once.
      Red today: no `li.flag`.
      Test: `tests/test_page_html.py::PageHtmlTest::test_flags_unverified`.
- [ ] C12.5 **new** — PR text cannot add an element: with the store's `prs.body` of #3 set
      so its "What I built" paragraph reads "x </script><script>alert(1)</script><!-- y" (an
      UPDATE on the ingested store), the file holds `<script` twice and `</script` twice
      (the data and the controls), section 4's `<p>` text read by `html.parser` is that
      paragraph exactly, and the `bearing-data` element still parses as JSON holding it.
      Red today: `<script` once (no controls).
      Test: `tests/test_page_html.py::PageHtmlTest::test_pr_text_escaped`.
- [ ] C12.6 **new** — The controls are in the page: `button#prev` "Previous",
      `button#next` "Next", `span#counter` "1 / 10", one `<style>`, a second `<script>` with
      no `src` that names "ArrowLeft", "ArrowRight" and "hidden"; and
      `grep -c -E 'src=|href="http'` on the fixture's file prints 0, so neither the script
      (no ".src=") can add one; and the `<style>` element's text holds neither "url(" nor
      "@import", which the grep would not see. Whether they step is
      C12.10's browser check: no test runs the script.
      Red today: no `button#prev`.
      Test: `tests/test_page_html.py::PageHtmlTest::test_controls`.
- [ ] C12.7 **new** — Each step's graph is in its section: on the fixture, 10 `<svg>`, one per
      section; section 4 (00394fb, #3) has `app.a` and `app.b` as "module added cycle",
      `app.crlf` as "module added", and `app.a -> app.b` and `app.b -> app.a` as
      "import added cycle"; section 7 (fde93a4, #8) has `app.extra` "module added",
      `app.legacy` "module removed", `scripts.tools` "module", and no `scripts.helpers`;
      section 8 (e5fa51f, #9) has `app.b -> app.a` "import removed", `tests.contract.test_api`
      "module added", and no `cycle` class.
      Red today: no `<svg>`.
      Test: `tests/test_page_html.py::PageGraphTest::test_fixture_graphs`.
- [ ] C12.8 **new** — The page's bytes, graphs included, do not depend on the hash seed:
      `bearing page` on the fixture under `PYTHONHASHSEED=0` and `PYTHONHASHSEED=1` writes the
      same bytes, and each file holds 10 `<svg>`.
      Red today: the file holds no `<svg>` ("0 != 10"); the bytes already match.
      Test: `tests/test_page_html.py::PageGraphTest::test_same_under_two_seeds`.
- [ ] C12.9 **hold** — No existing contract test or golden file changes, `page-v1.json`
      included: `git -c core.safecrlf=false diff --exit-code --diff-filter=MDR 4c2143a -- tests/contract tests/fixtures/expected`
      prints nothing and exits 0 on the closing commit, and `python -m pytest -q tests/contract`
      passes on every track's head.
- [ ] C12.10 **new** — plan.md's Phase 4 "Done when" on the kit: on `c12cfe5` with
      `docs/kit/bearing.toml`, after `bearing ingest` (its `merges`, 94), `bearing page` writes
      a file in which `grep -c '<section class="step"'` prints 94, `grep -c -E 'src=|href="http'`
      prints 0, and `grep -o '<script' | wc -l` and `grep -o '</script' | wc -l` each print 2;
      and the maintainer has stepped through the first and last merge in a browser (#1,
      2026-10-28, and #95, 2026-11-04), with a screenshot of each pasted into the closing PR. CI cannot reach the kit: the close quotes each
      command and what it printed.
      Red today: `grep -c '<section class="step"'` prints 0.
      Test: the commands in Verify, run in the closing PR.

## Verify
```bash
python -m pytest -q tests/test_page_svg.py tests/test_page_html.py tests/contract/test_page.py
python -m pytest -q
git -c core.safecrlf=false diff --exit-code --diff-filter=MDR 4c2143a -- tests/contract tests/fixtures/expected
# The kit (C12.10), <s> a scratch directory with the kit's history and PRs as Day 10 made them:
python -m bearing ingest <s>/kit.git --prs <s>/kit-prs.json --data <s>/data
python -m bearing page <s>/kit.git --data <s>/data --config docs/kit/bearing.toml --out <s>/kit.html
grep -c '<section class="step"' <s>/kit.html
grep -c -E 'src=|href="http' <s>/kit.html
grep -o '<script' <s>/kit.html | wc -l
grep -o '</script' <s>/kit.html | wc -l
```

## Notes
- The plan-auditor ran on Phase 4 on `4c2143a` before this spec was written. Its run of
  today's shell on the kit: "merges 94  matched 94  unmatched merges 0  unmatched PRs 0
  direct 11", 94 steps, 26 flags, `src=` 0, `<script` 1, 1185 lines. Its five "fix before
  Day 12" findings are answered in In scope: the graphs reach `render` through an optional
  argument, so Day 11's `render(data)` calls still hold and no `Replaces:` is needed; a wide
  layer wraps; the drawn graph, renamed modules and cycle members are defined; PR text and
  module names are escaped; and the grep's reach over the script and CSS is a criterion.
- The kit has no cycle and no `-module` event: only the fixture (#3 to #9) can test the red
  and faded marks.
- The kit's page cannot be checked in (1185 lines on today's shell, over the 400-line rule):
  the close quotes the commands and what they printed.
- The kit at `c12cfe5` has 47 modules and 6 imports, in two layers of 43 and 4 (measured on
  `4c2143a` before this spec): one row of 43 boxes would be about 10,000 wide, so a layer wraps
  at 960.
- `grep -c -E 'src=|href="http'` counts text too: an escaped paragraph that mentions `src=`
  still prints 1. The kit's paragraphs are to be checked before the close; a hit is a
  departure to record, not a reason to escape `=`.
- C12.10 has no test name after "Test:", a departure from `specs/README.md`'s rule: CI cannot
  reach the kit, so its evidence is the Verify commands and their output, quoted in the close.
- C12.9 uses `--diff-filter=MDR`, where C11.8 used `MD`: with rename detection, a renamed
  golden file shows as R and would pass `MD` (spec-auditor; the contract test would still fail).
- **Defect** D12.1 — found: auditor · cause: spec · made: Day 12 · C12.2 gave "m00" as 56 wide;
  the rule gives 48. Fixed in this PR.
- **Defect** D12.2 — found: auditor · cause: spec · made: Day 12 · C12.2's input, one import
  "top -> m00", puts "top" in layer 0 with 39 "m" boxes, not alone in the first row; now
  "top" imports every "m", in this PR.
- **Defect** D12.3 — found: auditor · cause: spec · made: Day 12 · the In scope did not give
  the first box's position or the arrows' ends, so two drawings could differ; pinned in this PR.
- **Defect** D12.4 — found: auditor · cause: spec · made: Day 12 · C12.8 was a `hold` that
  passes with no graphs at all; now `new`, counting 10 `<svg>`, in this PR.
- **Defect** D12.5 — found: auditor · cause: spec · made: Day 12 · C12.6 said the grep keeps
  URLs out of the CSS; it cannot see "url(" or "@import". Asserted directly, in this PR.
- **Defect** D12.6 — found: auditor · cause: spec · made: Day 12 · same-as: D11.7 · literal
  values were in backticks; quoted, in this PR.
- **Defect** D12.7 — found: self · cause: process · made: Day 12 · the first break for C12.9 ran
  the diff, whose last line is a bare "}", so its `broken:` line said nothing; the break was
  run again on the contract tests, in this PR.
- **Defect** D12.8 — found: CI · cause: spec · made: Day 12 · the Tracks table named neither
  C12.8 (`new` since D12.4) nor C12.10, so CI's "Track tests seen red" failed on track A's PR
  (#75): "C12.8 is new and no row of the Tracks table names it", and the same for C12.10.
  Track C now names C12.8, and a close row names C12.10, in a spec-change PR.
