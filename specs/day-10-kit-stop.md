# Day 10 — `bearing direction` on the kit, its flags judged, and the Phase 3 stop

**Phase:** 3 · **Depends on:** Day 9 · **Expected PRs:** 8 (this spec, track A, the plan
change, this spec's round 2 change, tracks C, D and B, the close)

## Goal
The kit's `bearing.toml` and its unmarked `bearing direction` report at `c12cfe5` are in this
repository before any flag is judged; round 1's 72 flags fell short of half `real` (#60), so the
`outside-area` rule takes a `shared` list, the config is fixed for what round 1 found, and round
2's 26 flags are each marked by the maintainer in `docs/kit/flags.md`, with the counts Phase 3's
"Done when" asks for, and a test holds the marks to the report; and a test fails when a merge
without a PR record loses the branch its merge subject gives (H09.1).

## In scope
- H08.2: the kit's `bearing.toml` at `docs/kit/bearing.toml`, and the run of `bearing
  direction` on the kit at `c12cfe55018aebe82de83485460f1edd22e4c96b` (#95) for Phase 3's
  "Done when". Round 1's file (Track A, #59; `git show 527421e:docs/kit/bearing.toml`) gave
  `dashboard` "scripts/spec-drift.py", "scripts/test_spec_drift.py", "docs/dashboard/";
  `tooling` "scripts/", ".github/", ".claude/"; `specs` "specs/"; `docs` "docs/", "kit/",
  "README.md", "CLAUDE.md", "plan.md"; `min_prs` 3; and an empty `[rules.outside-area]`.
  Round 2's file (Track D) is exactly:

  ```toml
  # The kit's bearing.toml, for round 2 of Day 10's run of bearing direction on the kit at c12cfe5.
  # Round 1's paths, fixed for three of the causes round 1's marks found (plan.md, Course
  # correction at the Day 10 stop): kit/ holds tools, the dashboard misses its own files, and
  # root tool configuration had no area. The shared list holds the other: text every area edits.
  # Fixed before any round 2 flag was judged.
  [areas]
  dashboard = [
      "scripts/spec-drift.py", "scripts/test_spec_drift.py", "docs/dashboard/",
      ".github/workflows/spec-drift-tests.yml", "spec-drift.config.json",
      "scripts/demo-data.py", "scripts/test_demo_data.py",
      "kit/compare-page.py", "kit/page/", "kit/starter-check.py",
  ]
  tooling = [
      "scripts/", ".github/", ".claude/",
      "kit/replay/", "kit/compare-page.py", "kit/page/",
      ".gitignore", ".gitattributes", ".flake8",
  ]
  specs = ["specs/"]
  docs = [
      "docs/", "kit/ASSESSMENT.md", "kit/comparison/", "kit/examples/", "kit/jobmatch/",
      "kit/lessons/", "kit/six-kits-assessment.md", "kit/six-kits-plan.md", "kit/v2-manifest.md",
      "README.md", "CLAUDE.md", "plan.md",
  ]

  [coupling]
  min_prs = 3

  [rules.outside-area]
  shared = [
      "kit/CHANGES.md", "kit/SOURCE.md", "CHANGES.md", "SOURCE.md",
      "CLAUDE.md", "README.md", "AGENTS.md", "plan.md",
      "specs/README.md", "specs/_template.md", "specs/_short-template.md", "templates/",
  ]
  ```

  Where round 2's changes come from, each from a `rule` mark of round 1
  (`docs/kit/flags-round-1.md`) under one of plan.md's four causes: `docs` loses `kit/` and
  keeps the kit's prose under it, by name (every path under `kit/` at `c12cfe5`, less the
  tools, the page and the record); `kit/replay/` goes to `tooling` (4 marks); `kit/page/`
  goes to `dashboard` (8 marks, two of them, #7 and #10, with `kit/compare-page.py`), and
  both go to `tooling` too (#7's mark);
  `kit/starter-check.py` goes to `dashboard` (#19's mark); the dashboard's test workflow,
  config and demo data (`scripts/demo-data.py` and its test, 3 marks) go to `dashboard`;
  `.gitignore`, `.gitattributes` and `.flake8` go to `tooling` (3 marks). The `shared` list
  is plan.md's cause list as it stands: the record at `kit/` and at the root, the four root
  Markdown files, `specs/README.md`, the two spec templates at `c12cfe5`, and `templates/`,
  which held the templates of the spec, `plan.md` and `CLAUDE.md` until the kit's #16 deleted
  them. Round 1's marks that this file does not take, since plan.md's causes do not name them:
  the wider shared list (the PR template, `.claude/agents/`, `docs/workflow.md`,
  `docs/architecture.md`), and only when the PR also changes its own area; `docs/dashboard/`
  and `docs/dashboard/token-usage.json` under `tooling` (4 marks: #72, #73, #88, #90), and
  the same marks' rule that a few-line `docs/dashboard/` edit is part of the tooling change;
  `scripts/token-usage.py`, its test and `scripts/behaviour-index.py` under `dashboard` (2),
  and #56's alternative, exempting a call-site change of under 5 lines;
  `spec-drift.config.json` under `tooling` (1). #54's `AGENTS.md` under `docs` and `tooling`,
  and #91's `specs/_template.md` under `docs`, are met by `shared` instead.
- The `outside-area` rule's `shared` key (Track C), as plan.md's Course correction at the Day 10
  stop, item 2, gives it: `[rules.outside-area] shared = [<path prefixes>]`, and a file a PR
  changes under one of them is never outside its area. `load_rules` returns
  `("outside-area", <the prefixes, in file order>)`, and `()` without the key, as today;
  `shared` that is not a non-empty list of strings raises `ConfigError` "config <path>:
  [rules.outside-area] shared must be a list of path prefixes". A `paths` key there stays
  ignored (Day 9). `said_vs_done` leaves out of an `outside-area` flag every file that starts
  with one of the rule's prefixes; a PR whose outside files are all shared is not flagged. The
  key changes nothing else: churn and coupling still read a shared file's area from `[areas]`
  (`other` when none lists it). `bearing.toml.example` gains a commented `# shared = [...]`
  line under `[rules.outside-area]`, which `load_rules` does not read, so C09.4 holds. Without
  the key the rule is as today, so the fixture's report and its golden file do not change
  (C10.4).
- Round 1's file, for the record: the area names are four of those the kit's
  `scripts/pr-names.py` accepts, the four its 94 merges use (`tooling` 51, `dashboard` 28,
  `docs` 13, `specs` 2), and round 2 keeps them. Where round 1's paths came from:
  the kit README at `c12cfe5` (lines 4–6) names `.claude/agents/`, `specs/README.md`,
  `.github/`, `scripts/spec-drift.py`, `docs/dashboard/` and `scripts/`. This spec widened
  those to whole directories (`.claude/`, `specs/`), added `scripts/test_spec_drift.py` to the
  dashboard beside the script it tests, and gave `docs` the rest of the kit's prose (`docs/`,
  `kit/`, the three root Markdown files the README links). That choice is this spec's, not the
  kit's, and the count moves with it: the auditor's scratch configs gave 83 flags with the
  README's paths alone, 79 with `kit/` dropped from `docs`, 52 with `kit/`, `CLAUDE.md` and the
  root `CHANGES.md`/`SOURCE.md` also in `tooling`. The config was run once, in this spec's
  prototype, before the spec was written; it was fixed from #58 on, and round 1's judged run
  read it unchanged.
  In neither round a `[rules.contract-impact]`: the kit has no contract tests and no frozen
  paths (`spec-drift.config.json` lists none under "frozen"), so the rule has no path to watch.
- `docs/kit/direction.md`: the stdout of C10.3's `direction` run on the kit, unmarked, `\n`
  endings, committed so the marks can be checked against it without the kit. Track A (#59)
  committed round 1's 227 lines; Track D replaces them with round 2's 181, made with Track C's
  code and round 2's file.
- H09.1: a test that sees the branch's fallback (D09.10). On the fixture, with
  `tests/fixtures/bearing.toml` read as bytes and its "tooling = ["scripts/", "ci.txt"]" line
  replaced by "tooling = ["scripts/"]" in a file written in the test, #11 (`tooling/ci`, no PR
  record, its branch only in the merge subject) changes `ci.txt`, now outside `tooling`, and is
  flagged; taking the record's branch alone, without `commits.subject_branch`, leaves #11
  unchecked. The kit cannot carry this test: every one of its 94 merges has a record ("What the
  kit gives").
- `docs/kit/flags.md` (Track B, after Track D has merged and the maintainer has marked every
  round 2 flag): every line of `docs/kit/direction.md` that starts "- #", in its order, each followed by
  " -- real" or " -- rule: <what to change>", the mark the maintainer gives it. ASCII only, so
  no encoding turns a mark into `?`. Above them: the commands that made them, the code's
  commit, and one line "Marks: real <n>, rule <m>". Nothing else in the file starts "- #" or
  ends " -- real".
- `tests/test_kit_flags.py` (Track B) reads both files as bytes, `\r\n` as `\n`, and checks:
  `docs/kit/flags.md` is ASCII; its "- #" lines, each with its last " -- " and what follows
  cut, equal `docs/kit/direction.md`'s "- #" lines in order (26 from Track D); each mark is "real" or
  "rule: " and at least one more character; the "Marks:" line's two numbers are the counts of
  each mark; and the `real` marks are at least half the flags. It does not run `bearing` or
  need the kit.
- The judging, round 1: the maintainer marked round 1's 72 flags, real 17, rule 55, kept in
  `docs/kit/flags-round-1.md` (#60), which no test reads. Fewer than 36 `real`, so Track B did
  not open, and plan.md's Course correction at the Day 10 stop set round 2.
- The judging, round 2, as round 1: Claude gives the maintainer the 26 lines of Track D's
  `docs/kit/direction.md` unmarked, in a scratch file; the maintainer marks each; Claude copies
  the marks into `docs/kit/flags.md` as given, and changes neither the flags,
  `docs/kit/direction.md`, `docs/kit/bearing.toml` nor the rule after the first mark. A mark
  may name the rule or the kit's config as what to change. With fewer than 13 `real`, Track B
  does not open, and what follows is the maintainer's (H10.2): plan.md names no round 3.
- The closing PR quotes the "Marks:" line and links `docs/kit/flags.md`, which holds the list
  plan.md's Phase 3 asks the closing PR for: 26 lines in a file a test checks, not in a PR body
  nothing reads.

### What the kit gives

Round 1: a run on 2026-11-05, on this repository's `64baca6`, in a scratch directory `<s>`: `git clone
-q --bare <kit> <s>/kit.git`, `git -C <s>/kit.git update-ref refs/heads/main
c12cfe55018aebe82de83485460f1edd22e4c96b`; in the kit's checkout, in Git Bash, the `PR_LIST`
command (Day 4) to `<s>/kit-all.json`, which gave 95 records, #1 to #96 without #71; the 94
numbered 95 or less written to `<s>/kit-prs.json` as UTF-8 with Day 4's filter, "92" read as
"95"; the file above saved as `<s>/kit.toml`.

- `python -m bearing ingest <s>/kit.git --prs <s>/kit-prs.json --data <s>/data` prints "merges
  94  matched 94  unmatched merges 0  unmatched PRs 0  direct 11".
- `python -m bearing direction <s>/kit.git --data <s>/data --config <s>/kit.toml` exits 0 and
  prints 227 lines: Churn with 10 rows, Coupling with 133 rows (90 of them a hidden
  dependency), and Said vs done with 72 flags, all `outside-area`, at most one per PR: 41 on
  `tooling` branches, 27 `dashboard`, 2 `docs`, 2 `specs`. The first is "- #2 outside-area:
  area dashboard | CHANGES.md, SOURCE.md".
- The files the flags name most, in flags: `kit/CHANGES.md` 32, `CLAUDE.md` 25,
  `specs/README.md` 16, `README.md` 16, `CHANGES.md` 13, `SOURCE.md` 12,
  `kit/page/jobmatch-boxes.sha256` 10. Whether a flag is real is the maintainer's call, not
  this spec's.
- With "tooling = ["scripts/"]" (H09.1, on the fixture): the Said vs done section is "- #5
  outside-area: area docs | scripts/run.py", "- #9 contract-impact: no contract impact |
  tests/contract/test_api.py", "- #11 outside-area: area tooling | ci.txt". The fixture's store
  has `prs` rows 1 to 10; #11's merge row has no `pr_number`, `subject_number` 11 and
  `subject_branch` "tooling/ci".

Round 2: on 2026-11-05, on this repository's `527421e`, the same scratch clone, records and
`ingest` (its line unchanged), with round 2's file above saved as `<s>/kit2.toml`, run with a
scratch copy of `bearing/` holding Track C's two changes as In scope gives them:

- `python -m bearing direction <s>/kit.git --data <s>/data --config <s>/kit2.toml` exits 0
  and prints 181 lines: Churn with 10 rows, Coupling with 133 rows (91 of them a hidden
  dependency), and Said vs done with 26 flags, all `outside-area`: 12 on `dashboard`
  branches, 12 `tooling`, 2 `specs`, none `docs`. The first is "- #8 outside-area: area
  dashboard | scripts/test_token_usage.py, scripts/token-usage.py".
- Every round 2 flag is a round 1 flag, on the same or fewer files (22 on fewer; #56, #72,
  #73 and #89 unchanged); none is new. Of round 1's 17 `real`,
  13 are still flags; #18, #39, #45 and #48 are gone, each flagged in round 1 only for files
  round 2 gives the PR's area or `shared` (`README.md`, `CLAUDE.md`, `kit/replay/README.md`,
  `kit/starter-check.py`, `.github/workflows/spec-drift-tests.yml`). Of round 1's 55 `rule`,
  13 are still flags. Round 2's marks are the maintainer's, made again, not carried over.
- The files the flags name most, in flags: `docs/dashboard/dashboard.js` 5,
  `.github/workflows/pr-checks.yml` 4, `docs/workflow.md` 4, `kit/ASSESSMENT.md` 4,
  `.claude/agents/implementer.md` 3, `.github/pull_request_template.md` 3.
- The same run with today's code (no `shared` key, which today's `load_rules` ignores) prints
  73 flags: round 2's areas without the `shared` list flag more than round 1, since `docs` no
  longer holds `kit/CHANGES.md` and `kit/SOURCE.md`.

## Out of scope
- Changing a rule or its settings after round 2's first mark. Round 1 fell short (#60), and
  this spec's round 2 is that change; plan.md names no round 3 (H10.2).
- `contract-impact` on the kit: no contract path (In scope).
- The Phase 3 stop itself, after this day's close (H10.1).
- Following a rename, and PRs off the first-parent line: as Days 8 and 9. The rename limit
  shows on the kit (Notes).
- Flags in the page data (`page-v1`) — Phase 4.

## Tracks

| Track | Owner | Work |
|---|---|---|
| A | implementer; the main session runs the kit | merged (#59): C10.2, and round 1's `docs/kit/bearing.toml`, `docs/kit/direction.md` and C10.1's test; `tests/test_config.py`, `tests/test_direction_cli.py` |
| C | implementer | C10.6, C10.7: the `shared` key; `bearing/direction/config.py`, `bearing/direction/said_vs_done.py`, `bearing.toml.example`; `tests/test_config.py`, `tests/test_said_vs_done.py` |
| D | implementer; the main session runs the kit | C10.1, C10.3: round 2's `docs/kit/bearing.toml` and `docs/kit/direction.md`; `tests/test_config.py`, `tests/test_kit_report.py` |
| B | implementer; the marks the maintainer's | C10.5: `docs/kit/flags.md`, `tests/test_kit_flags.py` |

The tracks run C, D, B, not in the table's order: D's report needs C's code, and B's marks are
checked against D's report. B opens after D has merged and the maintainer has marked every
round 2 flag. No Track 0, though Track C changes `bearing/`: the tests that must pass before
and after it are there already, and pass today. `ConfigTest.test_rules` (C09.1) and
`SaidVsDoneTest.test_flags` (C09.3) hold the rule without the key, and C10.4's contract test
and diff hold the fixture's report. C10.4 is `hold`, owned by #58, which ran its check and
break; Track C's PR runs its check again. C10.1's test is Track A's, its expected values
changed in Track D.

## Acceptance criteria
Tick each box in the closing PR once its evidence is in it; under a box left unticked, write
`Not proven: <why>` (`specs/README.md`, "Evidence at the close").
- [x] C10.1 **new** — `docs/kit/bearing.toml` holds round 2's In scope text: `load_config` on
      it returns the four areas `dashboard`, `tooling`, `specs`, `docs`, in that order, each
      with exactly round 2's prefixes as a tuple in file order (10, 9, 1 and 12 of them), and
      `min_prs` 3; and `load_rules` returns `[("outside-area", ("kit/CHANGES.md",
      "kit/SOURCE.md", "CHANGES.md", "SOURCE.md", "CLAUDE.md", "README.md", "AGENTS.md",
      "plan.md", "specs/README.md", "specs/_template.md", "specs/_short-template.md",
      "templates/"))]`. The test spells out every prefix. Red today: the file is round 1's
      (#59), so `docs` holds "kit/" and `dashboard` 3 prefixes, and the test fails on the
      areas. Track A's test, met first at round 1 (#59) and reworded here; Track D changes its
      expected values.
      Test: `tests/test_config.py::ConfigTest::test_kit_config`
      The track's break: in `docs/kit/bearing.toml`, "kit/starter-check.py" made
      "kit/starter.py" → the test fails on the `dashboard` area.
      Evidence: `ConfigTest.test_kit_config` (#59, round 1's values; #63, round 2's), seen red
      first in #63 on `3beb69e`'s code, where the file was round 1's ("2 failed", with C10.3's
      test), and again at the close; `python -m pytest -q` (#63).
      broken: docs/kit/bearing.toml "kit/starter-check.py" made "kit/starter.py" → 1 failed in 0.10s (#63)
- [x] C10.2 **hold** — H09.1: on the fixture, `bearing direction` with the config of In scope
      ("tooling = ["scripts/"]") exits 0, and the lines after "## Said vs done" are exactly
      "", "- #5 outside-area: area docs | scripts/run.py", "- #9 contract-impact: no contract
      impact | tests/contract/test_api.py", "- #11 outside-area: area tooling | ci.txt"; the
      test also asserts that the store has no `prs` row numbered 11, so #11's branch can come
      only from its merge subject. True today (this spec's prototype; the auditor's run).
      Test: `tests/test_direction_cli.py::DirectionCliTest::test_branch_from_subject`
      The track's break: in `bearing/direction/report.py`,
      `COALESCE(prs.head_ref, commits.subject_branch)` made `COALESCE(prs.head_ref, '')`: the
      run still exits 0 and prints #5 and #9, and the test fails on the missing #11 line.
      Evidence: `DirectionCliTest.test_branch_from_subject` (#59), passing on `main` from #59
      on; `python -m pytest -q` (#59, #62, #63, #64, and at the close on `87b6f33`).
      broken: report.py's branch COALESCE(prs.head_ref, commits.subject_branch) made COALESCE(prs.head_ref, '') → 1 failed in 9.78s (#59)
- [x] C10.3 **new** — Phase 3's run on the kit, round 2, from Track D's merge: with the
      scratch clone, records and commands of "What the kit gives", `docs/kit/bearing.toml` in
      place of `<s>/kit.toml`, `ingest` prints exactly "merges 94  matched 94  unmatched
      merges 0  unmatched PRs 0  direct 11", `direction` exits 0, its stdout piped to `grep -c
      '^- #'` prints 26, and its stdout is `docs/kit/direction.md` (`diff` exits 0, `\r\n`
      read as `\n`). The closing PR quotes the four, run on its own code. Red today: the file
      is round 1's, and `grep -c` prints 72; with round 2's file and today's code, 73 ("What
      the kit gives"). Met at round 1 by #59, with #58's break (0 not 72); a hold then, `new`
      now that round 2 changes the file and the code; reworded in its own day, unticked, so it
      replaces nothing in force.
      The test, Track D's, stands in on CI for the run it cannot make: it reads
      `docs/kit/direction.md` as bytes, `\r\n` as `\n`, inside the test body, and checks 181
      lines, 26 that start "- #", and the first of them "- #8 outside-area: area dashboard |
      scripts/test_token_usage.py, scripts/token-usage.py". Red today: the file holds round
      1's 227 lines and 72 flags.
      Test: `tests/test_kit_report.py::KitReportTest::test_round_2`
      Track D's breaks: the last "- #" line deleted from `docs/kit/direction.md` → the test
      fails on the count; and, by hand on the kit, on Track C's merged code, in
      `bearing/direction/said_vs_done.py`, the `shared` test dropped from the `outside-area`
      filter (" and not p.startswith(prefixes)" removed, as Track C writes it) → the `grep -c`
      prints 73, not 26 (`scripts/break.py --expect-stdout '^26$'`). The kit break is not
      replayable on CI, which has no clone of the kit, so its `manifest:` line stays out of
      `specs/breaks/day-10.json`.
      Evidence: `KitReportTest.test_round_2` (#63), seen red first in #63 on `3beb69e`'s code
      and again at the close; the kit run by hand in #63 and again at the close, on `87b6f33`,
      the kit's clone at `c12cfe5` and a new data directory: `ingest` printed "merges 94
      matched 94  unmatched merges 0  unmatched PRs 0  direct 11", `direction` exited 0, `grep
      -c '^- #'` printed 26, and `diff --strip-trailing-cr` against `docs/kit/direction.md`
      exited 0.
      broken: the last "- #" line (#94) emptied in docs/kit/direction.md, 25 flags left → 1 failed in 0.09s (#63)
      broken: said_vs_done.py "and not p.startswith(prefixes)" removed from the outside-area filter, on the kit → 73 (#63)
- [x] C10.4 **hold** — the fixture's direction report still matches its golden file, and no
      contract file changed: `python -m pytest -q tests/contract/test_direction.py` passes,
      and `git -c core.safecrlf=false diff --exit-code 64baca6 -- tests/contract
      tests/fixtures/expected` prints nothing. True today ("1 passed"; the diff exits 0).
      This PR's break: in `tests/fixtures/expected/direction.md`, "| scripts/run.py" made
      "| scripts/runX.py" → the test reports "1 failed" and the diff exits 1.
      Evidence: `DirectionContractTest.test_golden` and the diff above, "1 passed" and exit 0
      in #58, #62 and at the close on `87b6f33`.
      broken: the golden file's #5 file made scripts/runX.py → 1 failed in 5.23s (#58)
      broken: the golden file's #5 file made scripts/runX.py → - #9 contract-impact: no contract impact | tests/contract/test_api.py (#58)
- [x] C10.5 **new** — `docs/kit/flags.md` lists every flag of `docs/kit/direction.md`, each
      marked by the maintainer, as In scope says, and at least half are `real`: the test
      passes, `grep -c '^- #' docs/kit/flags.md` prints 26, and `grep -c -- ' -- real$'
      docs/kit/flags.md` prints 13 or more. The test stands in for the greps' near misses: it
      reads every line, so a header line ending " -- real", or a flag line not in the report,
      fails it. Red today: the file is missing, and the test fails on it. The marks are the
      maintainer's reading; the checks see only that each is there, on the report's lines,
      and the count of `real`. Round 2's marks; round 1's are in `docs/kit/flags-round-1.md`,
      which the test does not read.
      Test: `tests/test_kit_flags.py::KitFlagsTest::test_marks`
      The track's break: the last flag line deleted from `docs/kit/flags.md`: the test must
      fail on the lines no longer matching the report's 26.
      Evidence: `KitFlagsTest.test_marks` (#64), seen red first in #64 on `6a5f0dc`'s code,
      where the file was missing ("1 failed"), and again at the close; the greps printed 26
      and 13 in #64 and at the close: the maintainer's marks are real 13, rule 13 (the
      "Marks:" line of `docs/kit/flags.md`), exactly half, which closes H10.2.
      broken: the last flag line (#94) deleted from docs/kit/flags.md → 1 failed in 0.07s (#64)
      broken: the last flag line (#94) emptied in docs/kit/flags.md, 25 flags left → 1 failed in 0.08s (close, D10.19)
- [x] C10.6 **new** — `load_rules` reads `shared`: on a file written in the test holding
      `[areas] app = ["app/"]` and `[rules.outside-area] shared = ["CHANGES.md",
      "docs/shared/"]`, it returns `[("outside-area", ("CHANGES.md", "docs/shared/"))]`; with
      `[rules.outside-area] paths = ["x/"]` and no `shared`, `[("outside-area", ())]`. And,
      each in a file that also holds a valid `[areas]`, `ConfigError` is raised with exactly
      "config <path>: [rules.outside-area] shared must be a list of path prefixes" for `shared
      = []`, `shared = "CHANGES.md"` and `shared = [1]`. Red today: the first file gives
      `[("outside-area", ())]`, and the three raise nothing.
      Test: `tests/test_config.py::ConfigTest::test_outside_area_shared`
      The track's break: in `bearing/direction/config.py`, `found.append((rule_id,
      tuple(shared)))` made `found.append((rule_id, ()))` → the test fails on the first file's
      prefixes.
      Evidence: `ConfigTest.test_outside_area_shared` (#62), seen red first in #62 on
      `7b5288c`'s code ("2 failed", with C10.7's test), and again at the close; `python -m
      pytest -q` (#62).
      broken: config.py's found.append((rule_id, tuple(shared))) made found.append((rule_id, ())) → 1 failed in 0.22s (#62)
- [x] C10.7 **new** — `said_vs_done` leaves shared files out: with the areas `[("docs",
      ("docs/",)), ("app", ("app/",))]`, the rules `[("outside-area", ("CHANGES.md",
      "docs/shared/"))]` and the PRs `[(1, "app/x", None, ["app/a.py", "CHANGES.md",
      "docs/shared/n.md", "docs/b.md"]), (2, "app/y", None, ["app/a.py", "CHANGES.md"]), (3,
      "docs/z", None, ["docs/shared/m.md", "app/c.py"])]`, it returns exactly `[(1,
      "outside-area", "area app", ["docs/b.md"]), (3, "outside-area", "area docs",
      ["app/c.py"])]`: #2's only outside file is shared, so it has no flag. Red today: #1's
      flag lists "CHANGES.md", "docs/b.md", "docs/shared/n.md", and #2 is flagged for
      "CHANGES.md".
      Test: `tests/test_said_vs_done.py::SaidVsDoneTest::test_shared`
      The track's break: in `bearing/direction/said_vs_done.py`, " and not
      p.startswith(prefixes)" removed from the `outside-area` filter → the test fails on #1's
      files.
      Evidence: `SaidVsDoneTest.test_shared` (#62), seen red first in #62 on `7b5288c`'s code,
      and again at the close; `python -m pytest -q` (#62). The break removes the text without
      its leading space (D10.18).
      broken: said_vs_done.py's 'and not p.startswith(prefixes)' removed from the outside-area filter → 1 failed in 0.10s (#62)

## Verify
```bash
python -m pytest -q
ruff check . && ruff format --check .
python -m pytest -q tests/test_config.py tests/test_said_vs_done.py tests/test_direction_cli.py tests/test_kit_report.py tests/test_kit_flags.py tests/contract/test_direction.py
git -c core.safecrlf=false diff --exit-code 64baca6 -- tests/contract tests/fixtures/expected
grep -c '^- #' docs/kit/flags.md
grep -c -- ' -- real$' docs/kit/flags.md
```

The full run gave "72 passed, 78 subtests passed" before Track A, which added two tests: "74
passed, 78 subtests passed" today (`527421e`). Track C adds two (76), Track D one (77), Track B
one (78), each with whatever subtests it holds, which its PR counts. The focused line names
`tests/test_kit_flags.py` and `tests/test_kit_report.py`, which exist only from Tracks B and D:
before then, a track runs it without them.

## Notes
- H09.1 named the kit as where merges without a PR record were likelier. The kit at
  `c12cfe5` has none (94 matched of 94), so C10.2 runs on the fixture's #11, the one such merge
  in any history Bearing is tested on.
- Day 8 named this run as where coupling's rename limit would show, and it does: the kit's #15
  moved `CHANGES.md` and `SOURCE.md` to `kit/`, so the root copies are files of their own,
  in no area (`other`): 43 Coupling rows name them, and 13 and 12 flags. The judging reads
  those flags knowing this.
- The kit's `main` is at `9a50a3e` today, one merge past `c12cfe5` (#96,
  `tooling/bearing-dashboard-flags`). The run stays at `c12cfe5`, the SHA H08.2 names and the
  one copied in (#30); #96 is for the stop's kit-update PR to weigh (H10.1).
- C10.3's break runs on the scratch clone, so its `manifest:` line names scratch paths and stays
  out of `specs/breaks/day-10.json`: the replay has no kit to run it on (as C04.6).
- **Defect** D10.1 — found: spec-change PR · cause: spec · made: Day 10 · the first draft made
  C10.5 `new` with greps and no `Test:` field, which `scripts/track-red.py` fails; the
  judged list became Track B with `tests/test_kit_flags.py`, before the audit.
- **Defect** D10.2 — found: auditor · cause: spec · made: Day 10 · C10.5's test passed for any
  72 well-formed lines with 36 `real`: nothing tied them to the run, the header's counts or
  ASCII. Track A now commits `docs/kit/direction.md`, and the test checks all three against it.
- **Defect** D10.3 — found: auditor · cause: spec · made: Day 10 · C10.3 and C10.4 were holds
  this PR owns but named no break; both are named and run (this PR).
- **Defect** D10.4 — found: auditor · cause: spec · made: Day 10 · the config's paths were
  said to come "from the README sentence", which names fewer; the run came before the spec,
  and a 10/62 split pre-sorted likely noise in front of the judge. In scope now says which
  paths are this spec's, the count's range (52 to 83) and the order; the split is gone.
- **Defect** D10.5 — found: auditor · cause: spec · made: Day 10 · "The files the flags name
  most" counted `kit/replay/` in files (17, in 5 flags) beside counts in flags, and left out
  `kit/page/jobmatch-boxes.sha256` (10 flags). Corrected.
- **Defect** D10.6 — found: auditor · cause: spec · made: Day 10 · "No Track 0: the tests that
  hold through the day exist" was false for C10.2, whose test Track A adds. Reworded.
- **Defect** D10.7 — found: auditor · cause: spec · made: Day 10 · plan.md's Phase 3 asks the
  closing PR for the list; the spec gave the close no part. The close quotes the "Marks:" line
  and links the file (In scope).
- **Defect** D10.8 — found: auditor · cause: spec · made: Day 10 · Day 8 said the rename limit
  would show on this run, and the spec did not pick it up; the Notes record it.
- **Defect** D10.9 — found: auditor · cause: spec · made: Day 10 · no expected test count, and
  Verify had no full `pytest -q` or style check. Both added.
- **Defect** D10.10 — found: auditor · cause: spec · made: Day 10 · literal output and numbers
  ("92", "95", the ingest line) were in backticks. Quoted.
- **Defect** D10.11 — found: auditor · cause: spec · made: Day 10 · the test's regex wrapped
  across a line inside backticks. The test's checks are now in words.
- **Defect** D10.12 — found: auditor · cause: spec · made: Day 10 · C10.5's greps were never
  broken both ways; a header ending " -- real" would count. The file may hold none, and the
  test, which reads every line, stands in for the near misses.
- **Defect** D10.13 — found: auditor · cause: spec · made: Day 10 · C10.3, as worded with
  `docs/kit/bearing.toml`, fails today; it is now a hold from Track A's merge.
- **Defect** D10.14 — found: auditor · cause: spec · made: Day 10 · H10.1's `--split
  2026-11-04` separates nothing, as at the Phase 1 stop. H10.1 says so.
- **Defect** D10.15 — found: auditor · cause: spec · made: Day 10 · H10.1 left out what Phase
  4 drops if the schedule slipped, and the plan-auditor on Phases 3 and 4. Added.
- **Defect** D10.16 — found: auditor · cause: spec · made: Day 10 · "ASCII only" had no check;
  the test now checks it (as D10.2).
- Round 2 (this spec's second change, after #60): round 1's marks, 17 `real` of 72, fell
  short of the half Phase 3's "Done when" asks, so Track B did not open, and the round 1
  criteria C10.1, C10.3 and C10.5 are reworded for round 2, unticked. #59's evidence for C10.1
  and C10.3 is round 1's; their evidence at the close is Track D's. Round 2's file was run
  once, in this spec's prototype, before the spec was written, and is fixed from this spec's
  PR on.
- **Defect** D10.17 — found: spec-change PR · cause: spec · made: none · plan.md's Course
  correction at the Day 10 stop (#60) says round 1's 17 `real` flags "survive a fix of all
  four" causes. With the `shared` list it chose, four do not: #18, #39, #45 and #48 named only
  files round 1's own marks give the PR's area or the shared list. 13 survive. The marks
  are made again in round 2, so the count of `real` that round 1 predicts is 13, not 17;
  plan.md's sentence is left for the maintainer to correct or keep. The sentence came in #60,
  a plan-change PR outside any day that merged before this spec change (#61), which found it
  before any round 2 code.
- **Hand-off** H10.2 → the maintainer: if round 2's marks give fewer than 13 `real` of 26,
  Track B does not open and plan.md names no round 3. What follows, a further rule change or a
  stop with Phase 3's "Done when" unmet, is the maintainer's, in a Course correction before the
  close. With 13 or more, Track B opens and H10.2 is closed by it.
- **Hand-off** H10.1 → the maintainer: the Phase 3 stop, after this day's close (plan.md,
  "Stopping points"; CLAUDE.md step 6). On fresh `main`, the plan-auditor on Phase 3, on
  Phase 4 and on the whole plan; decide whether the page (Phase 4) is worth building, whether
  Bearing is proposed to the kit (a kit decision, made in the kit's repository), and, if the
  schedule has slipped, what Phase 4 leaves out; copy the kit in at one SHA in a kit-update PR
  if it has moved; the token comparison and the per-rung counts in the stop's Course
  correction. `--split 2026-11-04`, the date of the last kit-update PR (#30), separates
  nothing: `scripts/token-usage.py` splits by day (`day >= d`), and every merge so far, #30
  included, falls on or after it, as the Phase 1 stop found (plan.md, the Day 4 stop). The stop
  names a split that separates something, or says why none can.
- The tracks ran C (#62), D (#63), B (#64), as the table says. Track B opened after the
  maintainer marked all 26 round 2 flags: "Marks: real 13, rule 13" (`docs/kit/flags.md`),
  exactly the half Phase 3's "Done when" asks. Two of the 13, #16 and #31, are low-confidence
  `real` marks on which a blind Fable reading differed (#64); under Fable's marks alone the
  count would have been 11 and Track B would not have opened. H10.2 is closed by #64.
- D10.17's sentence in plan.md is unchanged: round 1's marks predicted 13 `real`, and round 2's
  marks gave 13.
- **Defect** D10.18 — found: Track C · cause: spec · made: Day 10 · C10.7's break named the text
  " and not p.startswith(prefixes)" with a leading space; after `ruff format` wrapped the
  comprehension, that text starts its own line and the space is not there. #62 removed the text
  without the space, the same change, and #63's kit break did the same.
- **Defect** D10.19 — found: close · cause: process · made: Day 10 · #64's `manifest:` line
  named this machine's `python.exe` by its full path, which CI's replay cannot run, and its
  `find` ended in a newline, which matches on CI's LF checkout but not on this CRLF working
  tree, where `break.py` refused it ("--find occurs 0 times"). `specs/breaks/day-10.json`
  runs it with `python` and empties the line's text instead of deleting it, as #63's break
  does; replayed at the close, the test failed on it ("1 failed").
- The close, on `87b6f33`: `python -m pytest -q` gave "78 passed, 107 subtests passed", the 78
  Verify predicts; the focused line "18 passed, 56 subtests passed"; the style check passed;
  C10.4's diff exited 0; the greps printed 26 and 13. `specs/breaks/day-10.json` holds 8
  breaks from the PRs' `manifest:` lines (2 from #58, 1 from #59, 2 from #62, 2 from #63, 1
  from #64), each replayed through `scripts/break.py` and each failing its check. #63's kit
  break stays out, as C10.3 says. `scripts/seen-red.py` gave each track's red again on its base:
  "2 failed" on `7b5288c` (#62), "2 failed" on `3beb69e` (#63), "1 failed" on `6a5f0dc` (#64).
- The blind relabel of the 19 Defect lines agreed on 18 stages, 19 causes and 18 `made:`. The
  rater could not tell D10.17's stage or the day that made it: the text did not say when #60
  merged or when the sentence was found. The tags are kept, and the text now says both. On
  D10.19 the rater agreed on `process` and marked it mixed with `environment` for the CRLF
  tree. The tag stays `process`: CLAUDE.md already names the CRLF tree, and the fault was a
  `manifest:` line that no one replayed before #64 merged.
