# Day 09 — said vs done in `bearing direction`, and the direction report's golden file

**Phase:** 3 · **Depends on:** Day 8 · **Expected PRs:** 4 (this spec, track A, track B, the close)

## Goal
`bearing direction` reads said-vs-done rules from `bearing.toml` and prints a third section,
`## Said vs done`, one line per flag naming the PR, the rule, the claim and the files; on the
fixture, with `tests/fixtures/bearing.toml`, it prints exactly the 28 lines of "What the fixture
gives", which become the direction report's golden file and contract test.

## In scope
- H08.1, as plan.md's "Course correction before Phase 3" (items 1–3) has it: the outside-area
  rule, checked only for a branch area that names a `bearing.toml` area, which flags the
  fixture's #5 with `scripts/run.py`; the contract-impact rule in both forms, which flags #9
  with `tests/contract/test_api.py`, the heading form tested on a body written in the test;
  the rules' settings in `bearing.toml`; the `## Said vs done` section (`Replaces: C08.5`);
  the direction golden file and its contract test; and `bearing.toml.example` at the
  repository root (plan.md, "Target structure").
- The rules in `bearing.toml`, one table each under `[rules]`, in the order they are checked:

  ```toml
  [rules.outside-area]

  [rules.contract-impact]
  paths = ["tests/contract/"]
  ```

  A rule absent from the file is not checked; a file without `[rules]` checks none. The ids are
  `outside-area` and `contract-impact`, no others.
- `bearing/direction/config.py` (Track A): `load_rules(path)` returns the rules in file order,
  each an `(id, paths)` pair, `paths` a tuple of strings: `()` for `outside-area`, the
  `paths` list for `contract-impact`. `load_config` and its return value do not change; both
  read the file the same way, so a missing file or one that is not TOML gives `load_config`'s
  messages. `load_rules` checks only that the file exists, is TOML, and its `[rules]`; it does
  not check `[areas]` or `[coupling]`, which are `load_config`'s. A key a rule does not use
  (`paths` in `outside-area`) is ignored. `load_rules` raises `ConfigError` with these messages, which the CLI prints after
  `bearing: `:
  - `rules` not a table (`rules = 3`), or a rule's value not a table
    (`rules = { outside-area = 1 }`): "config <path>: [rules] must be a table of rule tables";
  - an id that is not one of the two (`[rules.typo]`): "config <path>: unknown rule typo: the
    rules are outside-area, contract-impact";
  - `contract-impact` with `paths` missing, empty, or not a list of strings (`paths =
    "tests/"`): "config <path>: [rules.contract-impact] paths must be a list of path prefixes".
- `bearing/direction/said_vs_done.py` (Track A):
  - `says_no_contract_impact(body)` is true when the body claims no contract impact in either
    form, case ignored, each line read with `\r\n` as `\n` and its surrounding whitespace
    stripped: a heading of any level (`#` to `######` and a space) whose text is "Contract
    impact", whose first non-blank line after it starts with the word "none"
    (`^none\b`, so "None." and "None, only tests" count, "Nonetheless" does not); or a line
    starting "Contract impact:" followed by that word. Any such heading or line in the body
    makes the claim. `None` or `""` makes none.
  - `said_vs_done(prs, areas, rules)` takes `(number, branch, body, paths)` tuples in
    first-parent order, `body` `None` for a PR without a record, `areas` as `load_config`
    returns them, `rules` as `load_rules` returns them, and returns `(number, rule_id, claim,
    files)` flags: in the PRs' order, a PR's flags in the rules' order, `files` sorted.
    - `outside-area`: when the branch holds a "/" and `bearing.ingest.text.area(branch)` is
      the name of an area (a branch without "/" is never checked, even with an area named
      "other"), the files
      that start with none of that area's prefixes; flagged when there is one, with the claim
      "area <name>". "Outside" is read against the branch's own area's prefixes, not
      `area_of`: a file that an earlier area also matches is still inside.
    - `contract-impact`: the files that start with one of the rule's `paths`; flagged when
      there is one and `says_no_contract_impact(body)`, with the claim "no contract impact".
- `bearing direction` (Track B): `_direction` calls `load_rules` in the same `try` as
  `load_config`, before the store is opened, so a bad rule is an error whatever the store
  holds. Said vs done reads the PRs coupling reads (commits of kind `merge`, number
  `pr_number`, else `subject_number`, in first-parent order), each with the branch
  `COALESCE(prs.head_ref, commits.subject_branch)` and the body of the `prs` row whose number
  is that number (`LEFT JOIN prs ON prs.number = COALESCE(pr_number, subject_number)`; `None`
  without a record) and the paths of `changed_files`, read once per commit as churn and coupling read
  them. After the Coupling section, the report gains:

  ```
  <blank>
  ## Said vs done
  <blank>
  - #<n> <rule-id>: <claim> | <file>, <file>      one per flag
  ```

  With no flag, the line after the second blank is "No flags.". Each line ends `\n`. A flag is
  one line, so Day 10 can count the kit's flags by the lines that start "- #".
- The golden file, `tests/fixtures/expected/direction.md`, holds exactly the 28 lines of "What
  the fixture gives", each ending `\n`. Its contract test, `tests/contract/test_direction.py`,
  builds the fixture with `make_repo.py`, runs `python -m bearing ingest <dir>/repo --prs
  <dir>/prs.json --data <tmp>` then `python -m bearing direction <dir>/repo --data <tmp>
  --config tests/fixtures/bearing.toml`, and compares stdout's bytes with the golden file's,
  `\r\n` read as `\n` on both sides, as `tests/contract/test_timeline.py` does. Both files are
  added; no file in `tests/contract/` or `tests/fixtures/expected/` is edited.
- `tests/fixtures/bearing.toml` gains the four lines of the rules above after its `[coupling]`
  table, a blank line before each table. It is not frozen; C08.6's `test_threshold` reads it
  by replacing "min_prs = 3" and still passes.
- `bearing.toml.example` at the repository root (Track A): an `[areas]` table, `[coupling]
  min_prs = 3`, and both rules, `contract-impact` with `paths = ["tests/contract/"]`, each table with a comment
  that says what it does and that the file lives outside the repository it describes.
- plan.md, "Output contracts", direction: it said "one table each" and gave a flag as a list
  line. This spec's PR rewords it: Churn and Coupling are a table each, Said vs done a list of
  flags, one per line (D09.1).

### What the fixture gives

A prototype of the rules above, run on 2026-11-05 on the store of the fixture at `88f7cf8`,
flags exactly #5 and #9. The report is Day 8's 23 lines, then these 5:

```
<the 23 lines of Day 8's "What the fixture gives", unchanged>

## Said vs done

- #5 outside-area: area docs | scripts/run.py
- #9 contract-impact: no contract impact | tests/contract/test_api.py
```

- Checked for `outside-area`: #2 (`tooling/scripts`: `scripts/helpers.py`, `scripts/run.py`),
  #4 (`docs/guide`: `docs/guide.md`), #5 (`docs/typo-fix`: `scripts/run.py`, outside `docs`)
  and #11 (`tooling/ci`, no record, branch from the merge subject: `ci.txt`, a `tooling`
  prefix). `day-NN` and `release` PRs are not checked.
- `says_no_contract_impact` is true for every record but #2 ("What was built", no Contract
  impact) and #4 (empty body); #11 has no body. Only #9 touches `tests/contract/`.

## Out of scope
- The kit's `bearing.toml`, its run at `c12cfe5`, the maintainer's judging of each flag and
  the stop — Day 10 (H08.2).
- PRs off the first-parent line: #7 (`docs/notes`) is merged into `release` and has no commit
  row, so it is not checked; its file is in #10's diff, and `release` names no area. As for
  coupling.
- Following a rename: a renamed file is its new path, as `changed_files` gives it.
- Flags in the page data (`page-v1`) — Phase 4.
- The changelog's areas and golden file: unchanged.

## Tracks

| Track | Owner | Work |
|---|---|---|
| A | implementer | C09.1–C09.4: `load_rules` in `bearing/direction/config.py`, `bearing/direction/said_vs_done.py`, `bearing.toml.example`; `tests/test_config.py`, `tests/test_said_vs_done.py` |
| B | implementer | C09.5–C09.7: the section in `bearing/direction/report.py`, `load_rules` in `bearing/cli.py`, the rules in `tests/fixtures/bearing.toml`, `tests/fixtures/expected/direction.md`, `tests/contract/test_direction.py`, `tests/test_direction_cli.py` |

Two tracks, so each PR stays under 400 changed lines; B uses A's functions and lands after it.
No Track 0: the tests that hold through the day (Days 1 to 8, the contract tests among them)
exist. C09.8 is `hold` and owned by this spec's PR, which runs its check and break first.

## Acceptance criteria
Tick each box in the closing PR once its evidence is in it; under a box left unticked, write
`Not proven: <why>` (`specs/README.md`, "Evidence at the close").
- [ ] C09.1 **new** — `load_rules` on a file written in the test holding `[areas] app =
      ["app/"]`, then `[rules.contract-impact] paths = ["tests/contract/", "api/"]`, then
      `[rules.outside-area]`, returns `[("contract-impact", ("tests/contract/", "api/")),
      ("outside-area", ())]` in that order; on a file with `[areas]` and no `[rules]` it
      returns `[]`. And `ConfigError` is raised with exactly the In scope messages for: a path
      that does not exist (load_config's "no config at" message); and, each in a file that
      also holds a valid `[areas]`: `rules = 3`; `rules = {
      outside-area = 1 }`; `[rules.typo]`; `[rules.contract-impact]` with no `paths`; `paths =
      []`; `paths = "tests/"`. Red today: `load_rules` cannot be imported ("cannot import name
      'load_rules'").
      Test: `tests/test_config.py::ConfigTest::test_rules` and
      `tests/test_config.py::ConfigTest::test_rule_errors`
- [ ] C09.2 **new** — `says_no_contract_impact` is true for each of: "## Contract
      impact\n\nNone\n"; "## Contract impact\r\n\r\nNone. The format is unchanged.\r\n";
      "### contract impact\n\n  none\n"; "Contract impact: None\n"; "contract impact: none,
      only tests\n"; "## What I built\n\nX.\n\n## Contract impact\n\nNone\n"; and false for
      each of: "## Contract impact\n\nAdds snapshot-v2.\n"; "## Contract impact\n\nNonetheless
      the format changes.\n"; "## Contract impact\n\n## Next\n\nNone\n"; "It says Contract
      impact: none in passing.\n"; "Contract impact: unknown\n"; ""; `None`. Red today: the
      import of `bearing.direction.said_vs_done` fails ("No module named
      'bearing.direction.said_vs_done'").
      Test: `tests/test_said_vs_done.py::SaidVsDoneTest::test_claim`
- [ ] C09.3 **new** — `said_vs_done` with the areas `[("docs", ("docs/", "README.md")),
      ("app", ("app/",)), ("api", ("app/api/",))]`, the rules `[("contract-impact",
      ("tests/contract/",)), ("outside-area", ())]` and the PRs
      `[(7, "docs/fix", "## Contract impact\n\nNone\n", ["tests/contract/t.py", "app/x.py",
      "README.md", "docs/a.md"]), (2, "api/handler", None, ["app/api/h.py"]), (3,
      "day-04/track-a", "Contract impact: none\n", ["app/y.py", "tests/contract/u.py"]), (4,
      "release", "Contract impact: none\n", ["app/z.py"]), (5, "app/thing", "## Contract
      impact\n\nAdds v2.\n", ["tests/contract/v.py"]), (6, "tooling/ci", None,
      ["tests/contract/w.py"])]` returns exactly `[(7, "contract-impact", "no contract impact",
      ["tests/contract/t.py"]), (7, "outside-area", "area docs", ["app/x.py",
      "tests/contract/t.py"]), (3, "contract-impact", "no contract impact",
      ["tests/contract/u.py"]), (5, "outside-area", "area app", ["tests/contract/v.py"])]`.
      That is: the PRs' order is kept, not sorted; a PR's flags follow the rules' order; files
      come sorted; #2's `app/api/h.py` is inside `api` though `app` comes first; `day-04`,
      `release` and `tooling` (no area of that name) are not checked for `outside-area`; a
      body that claims an impact, or none at all (#6), raises no contract flag. With the rules
      `[]` it returns `[]`. Red today: as C09.2.
      Test: `tests/test_said_vs_done.py::SaidVsDoneTest::test_flags`
- [ ] C09.4 **new** — `bearing.toml.example` at the repository root loads: `load_config`
      returns at least one area and `min_prs` 3, and `load_rules` returns
      `[("outside-area", ()), ("contract-impact", ("tests/contract/",))]`. Red today: with
      `load_rules` imported at the top of `tests/test_config.py`, as C09.1's tests need, the
      module fails to collect on `main` ("cannot import name 'load_rules'"); that is the red the
      track PR records for C09.1 and C09.4 alike. The file is also missing today.
      Test: `tests/test_config.py::ConfigTest::test_example`
- [ ] C09.5 **new** — the direction report's contract: on the fixture, after `python -m
      bearing ingest <dir>/repo --prs <dir>/prs.json --data <tmp>`, `python -m bearing
      direction <dir>/repo --data <tmp> --config tests/fixtures/bearing.toml` exits 0 and its
      stdout's bytes equal those of `tests/fixtures/expected/direction.md`, which holds
      exactly the 28 lines of "What the fixture gives", `\r\n` read as `\n` on both sides. Red
      today: stdout is Day 8's 23 lines, without the 5 of Said vs done, so the bytes differ.
      Test: `tests/contract/test_direction.py::DirectionContractTest::test_golden`
- [ ] C09.6 **new** — `DirectionCliTest.test_fixture_report` expects the 28 lines: exit 0,
      stderr empty, stdout's bytes exactly the 28 lines of "What the fixture gives". Red
      today: stdout is Day 8's 23 lines.
      Test: `tests/test_direction_cli.py::DirectionCliTest::test_fixture_report`
      Replaces: C08.5 — was: stdout's bytes are exactly the 23 lines of Day 8's "What the fixture gives"
- [ ] C09.7 **new** — on the fixture's store, a copy of the fixture's toml without its
      `[rules...]` tables, written in the test, prints the 23 lines of Day 8, then "",
      "## Said vs done", "", "No flags."; and a copy with `[rules.typo]` added exits 1, stdout
      empty, stderr exactly "bearing: config <path>: unknown rule typo: the rules are
      outside-area, contract-impact\n"; and the `[rules.typo]` copy with `--data` an empty
      directory exits 1 with that same stderr, not "no store at", and leaves no `bearing.db`
      there: the rules are read before the store. Red today: the first prints Day 8's 23 lines
      and stops; the second exits 0, the unknown table unread; the third prints "no store at".
      Test: `tests/test_direction_cli.py::DirectionCliTest::test_rules_config`
- [ ] C09.8 **hold** — the frozen files stay as Day 8 left them, added files allowed outside
      the migrations: `git -c core.safecrlf=false diff --diff-filter=DMRT --exit-code 88f7cf8
      -- tests/contract/ tests/fixtures/make_repo.py tests/fixtures/expected/` and
      `git -c core.safecrlf=false diff --exit-code 88f7cf8 -- bearing/migrations/` print
      nothing and exit 0. Track B adds `tests/contract/test_direction.py` and
      `tests/fixtures/expected/direction.md`, which the first allows; the day adds no
      migration. The second sees an added migration only once it is committed (in a PR, and
      at replay), not an untracked file, so its break edits an applied one. This spec's PR
      breaks each command once with `scripts/break.py`: a line of
      `bearing/migrations/001_history.sql` and a line of `tests/fixtures/make_repo.py`.

## Verify
```bash
python -m pytest -q
python tests/fixtures/make_repo.py .bearing/day09-check
python -m bearing ingest .bearing/day09-check/repo --prs .bearing/day09-check/prs.json --data .bearing/day09-check/data
python -m bearing direction .bearing/day09-check/repo --data .bearing/day09-check/data --config tests/fixtures/bearing.toml | grep -c "^- #"  # 2
git -c core.safecrlf=false diff --diff-filter=DMRT --exit-code 88f7cf8 -- tests/contract/ tests/fixtures/make_repo.py tests/fixtures/expected/
git -c core.safecrlf=false diff --exit-code 88f7cf8 -- bearing/migrations/
```

## Notes
- Flags come in first-parent order, a PR's in the rules' order, not grouped by rule: plan.md's
  "rules in `bearing.toml` order" is kept within each PR, and `page-v1` gives each merge its
  own flags, so Phase 4 reads them per PR as they stand.
- `load_rules` is a second function rather than a third value from `load_config`, so C08.1's
  test and its unpacking in `bearing/cli.py` stay as they are.
- C08.6's `test_threshold` survives the new section unedited: at `min_prs = 2` and 4 it reads
  only up to the blank line after the Coupling table, which Day 8 worded for this.
- Tests: `python -m pytest -q` prints "65 passed, 58 subtests passed" on `88f7cf8`. The
  criteria name 7 new tests (Track A 5, Track B 2) and change one, so the day ends at "72
  passed", subtests besides.
- **Defect** D09.1 — found: self · cause: spec · made: none · plan.md's direction contract said
  "one table each" and gave a flag as a list line; reworded in this PR.
- **Defect** D09.2 — found: auditor · cause: spec · made: Day 09 · the first draft said the
  rules are read before the store, but no criterion checked it: a `load_rules` after the store
  check passed every test. The spec-auditor found this before any code; C09.7 now runs the
  bad rule against an empty data directory.
- **Defect** D09.3 — found: auditor · cause: spec · made: Day 09 · the first draft left open
  whether `load_rules` checks `[areas]`, so C09.1's error files could get the areas message;
  the spec-auditor found this before any code, and In scope and C09.1 now settle it.
- **Defect** D09.4 — found: auditor · cause: spec · made: Day 09 · the first draft gave
  `bearing.toml.example`'s `outside-area` a `paths` key and never said what an unused key
  does; the spec-auditor found this before any code; the key is now ignored and the example
  gives `paths` to `contract-impact` only.
- **Defect** D09.5 — found: auditor · cause: spec · made: Day 09 · the first draft of C09.8
  named no break and dropped C08.8's warning that the migrations diff misses an untracked file;
  the spec-auditor found this before any code, and both are back.
- **Defect** D09.6 — found: auditor · cause: spec · made: Day 09 · the first draft did not
  name the join between `commits` and `prs`, which the golden file cannot tell apart; the
  spec-auditor found this before any code, and In scope now names it.
- **Defect** D09.7 — found: auditor · cause: spec · made: Day 09 · the first draft gave C09.4
  two reds, but a top-level import makes the whole module fail to collect; the spec-auditor
  found this before any code, and C09.4 now names the one red to record.
- **Defect** D09.8 — found: auditor · cause: spec · made: Day 09 · `area()` returns "other"
  for a branch without "/", so an area named "other" would have checked every such branch,
  against plan.md's "`other` PRs are not checked"; the spec-auditor found this before any code,
  and `outside-area` now skips a branch without "/".
</content>
</invoke>
