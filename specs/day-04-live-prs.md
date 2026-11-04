# Day 04 — PRs live from `gh`, one `oid` one PR, and the Phase 1 stop

**Phase:** 1 · **Depends on:** Day 3 · **Expected PRs:** 5 (this spec, tracks 0, A and B, the close)

## Goal
`bearing ingest <repo>` with no `--prs` reads the PR records from `gh` itself; two records that
name one merge commit are mapped by a rule that does not depend on `gh`'s list order (H02.1); a
broken `<data>/bearing.db` is pinned by a test (H03.2); and Phase 1's done line holds on the kit's
history at the copied SHA, quoted in the closing PR, for the stop.

## In scope
- `bearing/ingest/gh.py` (Track A):
  - `GhError(Exception)`, its message the text after "bearing: ".
  - `PR_LIST`, the argument list `["gh", "pr", "list", "--state", "merged", "--limit", "1000",
    "--json", "number,title,body,headRefName,baseRefName,mergeCommit,mergedAt"]` (plan.md,
    "Decisions": exactly the command `--prs` files are recorded with).
  - `fetch_prs(repo)` calls `subprocess.run(PR_LIST, cwd=repo, capture_output=True,
    encoding="utf-8")` once, through the `subprocess` module's attribute (so a test can patch
    `subprocess.run`), and returns `json.loads` of its stdout. `gh` finds the GitHub repository
    from `<repo>`'s remotes; nothing is written there. Errors, each a `GhError`:
    - `gh` cannot be started (`FileNotFoundError`): "gh not found: install GitHub's CLI or pass
      --prs FILE";
    - a non-zero exit: "gh pr list failed: " and its stderr, stripped, or "exit <code>" when
      that is empty;
    - stdout that is not JSON: "gh pr list printed no JSON: " and `json.loads`'s message.
- `bearing ingest <repo> [--prs FILE] [--data DIR]` (Track A): `--prs` becomes optional. Without
  it the records come from `fetch_prs(<repo>)`, read after git and before the store is opened,
  as `--prs` files are now, so a `gh` error prints `bearing: <message>` to stderr, nothing to
  stdout, exits 1, and creates no store. With it, `gh` is never run.
- `map_history` (Track B), pass 1 only: when more than one record names a commit on the line by
  its `oid`, the commit is matched to the record whose number the commit's merge subject names
  (`parse_merge_subject`), and when it names none of them, to the lowest number. The others stay
  unmatched PRs. The choice does not depend on the records' order (H02.1). Nothing else in the
  two passes changes.
- Tests: `tests/test_broken_store.py` (Track 0), `tests/test_gh.py` (Track A), and a new class
  in `tests/test_mapping.py` (Track B). As on Days 2 and 3: every test class subclasses
  `unittest.TestCase`, imports the module under test inside the test method, and builds the
  fixture with `make_repo.py` as a subprocess (once per class) where it needs one. The tests of
  `gh` run it never: they patch `subprocess.run` with a fake that answers a call whose first
  argument is "gh" and passes every other call to the real `subprocess.run`, saved before the
  patch (git still runs for real), and they call `bearing.cli.main` in the test's process with
  stdout and stderr redirected to `io.StringIO`.

### What the kit gives

Counted in this spec's prototype on 2026-11-04, on today's code (`e578053`):
- The kit's `main` is at `d9712fe`, two merges past the copied SHA `44d7a55` (#92's merge):
  `git rev-list --count --first-parent --merges` gives 93 there and 91 at `44d7a55`.
- `gh pr list` (the `PR_LIST` command, run in the kit's checkout) gives 93 records, #1 to #94
  less the unmerged #71, newest first, all with base `main`. No two name one `oid`, so H02.1
  has no case on the kit and is pinned on records built in the test.
- With the records numbered 92 or less (91), ingested from a bare clone whose `main` is set to
  `44d7a55`: `merges 91  matched 91  unmatched merges 0  unmatched PRs 0  direct 11`; the
  changelog has 91 lines starting "- #", 215 lines in all, in four areas (`dashboard`, `docs`,
  `specs`, `tooling`); 86 of the 91 bodies have a "What I built" heading and none is empty.
- On the kit's own `main`, with all 93 records: `merges 93  matched 93  unmatched merges 0
  unmatched PRs 0  direct 11`. So no record is off the line there either (Day 2, Out of scope).

## Out of scope
- A `--ref` option: history stays the first-parent line of `main` (plan.md, "Merges out of
  order"). The kit's check reads a scratch clone whose `main` is set to the copied SHA, so no
  option is needed (Day 2, Out of scope, "a ref other than `main`").
- More than 1000 merged PRs: `PR_LIST` caps the list at 1000 and `gh` gives no sign of a cut
  (H04.2).
- A SQLite `bearing.db` that is not Bearing's: decided, left as it is (no day owns it).
  `bearing ingest` adds its tables beside the others and exits 0; the changelog on such a file
  before an ingest is C04.1's error.
- The Phase 1 stop itself, after this day's close: the maintainer's verdict on the kit's
  changelog, the kit-update PR, and the token comparison and per-rung counts in the stop's
  Course correction (plan.md, "Stopping points" and "Measurement") — the maintainer (H04.1).
- stderr's encoding (H03.1) and version strings in the text formats (H03.3) — the maintainer.
- A Windows job in CI (Day 1, Out of scope).

## Tracks

| Track | Owner | Work |
|---|---|---|
| 0 | implementer | C04.1: `tests/test_broken_store.py`, the broken stores, passing before and after |
| A | implementer | C04.2–C04.4, C04.8: `bearing/ingest/gh.py`, `--prs` optional, the `gh` errors |
| B | implementer | C04.5: two records on one `oid` in `map_history` |

Track 0 lands first. A and B touch different files and either may go first; the table's order
is the plan. No subpackage is new: `gh.py` is a grandchild of `bearing.ingest` (Day 2's Notes,
"Red on CI's base"). C04.6 and C04.7 are `hold` and owned by this spec's PR, which runs their
checks first.

## Acceptance criteria
Tick each box in the closing PR once its evidence is in it; under a box left unticked, write
`Not proven: <why>` (`specs/README.md`, "Evidence at the close").
- [x] C04.1 **hold** — a broken store (H03.2): with `<tmp>/bearing.db` written by the test as
      0 bytes, as the bytes "not a database, just text", and as a SQLite file holding only
      `CREATE TABLE x (a)`, `python -m bearing changelog --data <tmp>` each time exits 1,
      prints nothing to stdout, prints to stderr a line starting "bearing: cannot read store
      at ", and leaves the file's bytes as they were. And `bearing ingest <dir>/repo --prs
      <dir>/prs.json --data <tmp>` on the second of these exits 1, stdout empty, stderr starting
      "bearing: cannot open store at ". True today: #23 catches `sqlite3.Error` in both
      commands, and no test pins it (D04.1).
      Test: `tests/test_broken_store.py::BrokenStoreTest::test_changelog_refuses` and
      `tests/test_broken_store.py::BrokenStoreTest::test_ingest_refuses`
      Evidence: `BrokenStoreTest.test_changelog_refuses` and `BrokenStoreTest.test_ingest_refuses`
      (#26), passing on `4bfbd6c`'s code before the change, as a `hold` does (D04.1);
      `python -m pytest -q` (#26).
      broken: changelog's except sqlite3.Error narrowed to KeyError → 3 failed, 1 passed in 7.06s (#26)
      broken: ingest's except (OSError, sqlite3.Error) narrowed to OSError → 1 failed in 6.70s (#26)
- [x] C04.2 **new** — `fetch_prs`, with `subprocess.run` patched by a fake that records each call
      and returns `subprocess.CompletedProcess(args, 0, stdout='[{"number": 1, "title": "Café →
      bar"}]', stderr="")`, returns `[{"number": 1, "title": "Café → bar"}]`, and the fake saw
      exactly one call: as its only positional argument the literal list `["gh", "pr", "list",
      "--state", "merged", "--limit", "1000", "--json",
      "number,title,body,headRefName,baseRefName,mergeCommit,mergedAt"]`, written out in the
      test (not read from `PR_LIST`), and the keywords
      `cwd=<repo as given>, capture_output=True, encoding="utf-8"`, no others. Errors, each a
      `GhError` with exactly this text: the fake raising `FileNotFoundError` gives "gh not
      found: install GitHub's CLI or pass --prs FILE"; exit 1 with stderr "HTTP 401: Bad
      credentials\n" gives "gh pr list failed: HTTP 401: Bad credentials"; exit 4 with stderr ""
      gives "gh pr list failed: exit 4"; exit 0 with stdout "not json" gives a message starting
      "gh pr list printed no JSON: ". Red today: "No module named 'bearing.ingest.gh'".
      Test: `tests/test_gh.py::FetchPrsTest::test_command_and_output` and
      `tests/test_gh.py::FetchPrsTest::test_errors`
      Evidence: `FetchPrsTest.test_command_and_output` and `FetchPrsTest.test_errors` (#27), seen
      red first on `2d063b2`'s code with "No module named 'bearing.ingest.gh'";
      `python -m pytest -q` (#27).
      broken: fetch_prs's encoding="utf-8" replaced by text=True → 1 failed in 0.08s (#27)
      broken: fetch_prs's stderr no longer stripped → 1 failed, 1 passed, 3 subtests passed in 0.09s (#27)
- [x] C04.3 **new** — no `--prs`: with the fake answering `gh` with the text of the fixture's
      `<dir>/prs.json` (read as UTF-8), `main(["ingest", "<dir>/repo", "--data", "<tmp>"])`
      returns 0 and its stdout is the text of `tests/fixtures/expected/ingest.txt` (the three
      lines `merges 10  matched 9  unmatched merges 1  unmatched PRs 1  direct 2`, `unmatched
      merge 8c1b9f1 ...` and `unmatched PR #7 e21c62d docs/notes`), and the fake's one `gh` call
      had `cwd` "<dir>/repo". Red today: argparse's "the following arguments are required:
      --prs" (`SystemExit` 2).
      Test: `tests/test_gh.py::IngestLiveTest::test_without_prs`
      Evidence: `IngestLiveTest.test_without_prs` (#27), seen red first on `2d063b2`'s code with
      argparse's "the following arguments are required: --prs"; `python -m pytest -q` (#27).
      broken: ingest without --prs uses no records instead of fetch_prs → 1 failed in 4.86s (#27)
- [x] C04.4 **new** — `gh` errors at the command: with no `--prs` and the fake raising
      `FileNotFoundError` for `gh`, `main(["ingest", "<dir>/repo", "--data", "<tmp>"])` returns
      1, stdout is empty, stderr is exactly "bearing: gh not found: install GitHub's CLI or pass
      --prs FILE\n", and `<tmp>/bearing.db` does not exist; with the fake exiting 1 with stderr
      "HTTP 401: Bad credentials\n", stderr is exactly "bearing: gh pr list failed: HTTP 401:
      Bad credentials\n", return 1, no store. Red today: as C04.3.
      Test: `tests/test_gh.py::IngestLiveTest::test_gh_errors`
      Evidence: `IngestLiveTest.test_gh_errors` (#27), seen red first on `2d063b2`'s code, both
      subtests with argparse's error; `python -m pytest -q` (#27).
      broken: ingest's except GhError narrowed to KeyError → 2 failed, 1 passed in 5.60s (#27)
- [x] C04.5 **new** — one `oid`, two records (H02.1): commits built in the test, oldest first,
      `A = Commit("a" * 40, ("0" * 40, "1" * 40), "2026-02-01T00:00:00Z", "Merge pull request #8
      from acme/docs/x")` and `B = Commit("b" * 40, ("a" * 40,), "2026-02-02T00:00:00Z", "One
      squashed change (#9)")` and `C = Commit("c" * 40, ("b" * 40, "2" * 40),
      "2026-02-03T00:00:00Z", "Merge pull request #20 from acme/docs/y")`, and records `#3` and
      `#8` whose `mergeCommit.oid` is A's SHA, `#5` and `#9` whose `oid` is B's, and `#12` and
      `#11` whose `oid` is C's (each `{"number", "title", "mergeCommit": {"oid"}}`; no #20).
      `map_history([A, B, C], records)` gives `pr_by_sha == {A: 8, B: 5, C: 11}` (A's subject
      names #8; B's does not parse; C's names #20, neither of its records; so B and C take the
      lowest number), unmatched PRs numbered `[3, 9, 12]`, and merges 3, matched 3, unmatched
      merges 0, direct 0, for the records in the order 3, 8, 5, 9, 12, 11 and in the order 11,
      12, 9, 5, 8, 3. Red today: in the first order the code gives `{A: 3, B: 5, C: 12}`; in the
      second, `{A: 8, B: 9, C: 11}`.
      Test: `tests/test_mapping.py::SharedOidTest::test_subject_then_lowest`
      Evidence: `SharedOidTest.test_subject_then_lowest` (#28), seen red first on `621dd43`'s
      code, both order subtests failing with the values above; `python -m pytest -q` (#28).
      broken: map_history pass 1 ignores the merge subject → 2 failed, 1 passed in 0.09s (#28)
- [x] C04.6 **hold** — Phase 1's done line, on the kit (plan.md, Phase 1): in a scratch directory
      `<s>`, with the kit's checkout at `<kit>`,
      `git clone -q --bare <kit> <s>/kit.git` and
      `git -C <s>/kit.git update-ref refs/heads/main 44d7a55`; in `<kit>`, in Git Bash, the
      `PR_LIST` command with its output to `<s>/kit-all.json` (Windows PowerShell 5.1's `>`
      writes UTF-16, which the filter cannot read); the records numbered 92 or less written to
      `<s>/kit-prs.json` as UTF-8 (the Notes give the one-line filter). Then `python -m bearing ingest <s>/kit.git --prs <s>/kit-prs.json --data
      <s>/data` prints exactly `merges 91  matched 91  unmatched merges 0  unmatched PRs 0
      direct 11`, and `python -m bearing changelog --data <s>/data` piped to `grep -c '^- #'`
      prints 91, and piped to `grep -c '^- #[0-9]* Merge pull request #'` prints 0 (no entry
      fell back to its merge subject: every merge found its record). The closing PR quotes the
      three lines, run on its own code (plan.md, Phase 1). True today (this spec's prototype,
      "What the kit gives").
      Not replayable on CI, which has no clone of the kit: the close's line under it is
      `broken: none → <why>`, and the spec PR's break, run by hand, is in its description.
      Evidence: at the close, on `e291344` with the kit's `gh` list of 93 records cut to 91: the
      ingest line `merges 91  matched 91  unmatched merges 0  unmatched PRs 0  direct 11`, then
      `91`, then `0` (the closing PR quotes them); the same in #25's prototype.
      broken: none → the check needs a clone of the kit, which CI has not; pass 1 matching nothing was run by hand in #25, and the subject grep printed 91
- [x] C04.8 **hold** — with `--prs`, `gh` is never run: with the fake of C04.3 in place,
      `main(["ingest", "<dir>/repo", "--prs", "<dir>/prs.json", "--data", "<tmp>"])` returns 0,
      its stdout is the text of `tests/fixtures/expected/ingest.txt`, and the fake sees no `gh`
      call. True today (`--prs` is required and `gh` is never called); Track A adds the test
      and breaks it once by calling `fetch_prs` even when `--prs` is given.
      Test: `tests/test_gh.py::IngestLiveTest::test_with_prs_no_gh`
      Evidence: `IngestLiveTest.test_with_prs_no_gh` (#27), passing on `2d063b2`'s code, as a
      `hold` does; `python -m pytest -q` (#27).
      broken: ingest calls fetch_prs even when --prs is given → 1 failed in 5.51s (#27)
- [x] C04.7 **hold** — the frozen files stay as Day 3 left them: the fixture, the three contract
      tests and their golden files, and the applied migration:
      `git -c core.safecrlf=false diff --exit-code e578053 -- tests/contract/ tests/fixtures/make_repo.py tests/fixtures/expected/ bearing/migrations/001_history.sql`
      prints nothing and exits 0.
      Evidence: the command above, exit 0 in #25 and on `e291344` at the close.
      broken: the applied migration 001_history.sql edited → pr_number INTEGER NULL, (#25)

## Verify
```bash
python -m pytest -q
python tests/fixtures/make_repo.py .bearing/day04-check
python -m bearing ingest .bearing/day04-check/repo --prs .bearing/day04-check/prs.json --data .bearing/day04-data
python -m bearing changelog --data .bearing/day04-data
git -c core.safecrlf=false diff --exit-code e578053 -- tests/contract/ tests/fixtures/make_repo.py tests/fixtures/expected/ bearing/migrations/001_history.sql
```

## Notes
- Picks up H02.1 (C04.5) and H03.2 (C04.1), and Day 2's Out of scope for Day 4: live `gh`
  (C04.2–C04.4), the kit's 91-merge line (C04.6), a ref other than `main` (decided: none, Out of
  scope), and whether the kit's list holds a record off the line (none, "What the kit gives").
- H02.1's rule: the merge subject is evidence in the commit itself, so it wins when it names one
  of the records; the lowest number otherwise is a choice, not evidence, and the loser is still
  reported as an unmatched PR with its `oid`, so nothing is hidden (plan.md: "an unmatched list
  reported, never guessed"). Day 2's In scope said "the first in first-parent order wins"
  for two records with one `oid`, which ranks commits, not records; no criterion pinned it
  (D02.7), so C04.5 has no `Replaces:` line.
- `gh` reads its repository from `<repo>`'s remotes. The bare scratch clone in C04.6 has only a
  local path as `origin`, so live `gh` would fail there; C04.6 uses a recorded file, as plan.md
  says. Track A's PR quotes one live run on the kit's own checkout, which reads every merged PR
  as of that day: on 2026-11-04 the line is `merges 93  matched 93  unmatched merges 0
  unmatched PRs 0  direct 11` (with the records recorded by `PR_LIST`). Its counts move with
  the kit, so it is not a criterion.
- C04.6's filter, from the repository root:
  `python -c "import json,sys; r=json.load(open(sys.argv[1],encoding='utf-8')); json.dump([x for x in r if x['number']<=92],open(sys.argv[2],'w',encoding='utf-8'))" <s>/kit-all.json <s>/kit-prs.json`.
  The bodies of PRs up to #92 can still be edited on GitHub; that changes paragraphs, not the
  two counted lines.
- C04.6's break, by hand in this spec's PR: pass 1 of `map_history` matching nothing. The ingest
  line becomes `merges 91  matched 0  unmatched merges 91  unmatched PRs 91  direct 11`, and
  the subject grep counts 91, not 0; the `grep -c '^- #'` count stays 91, since an unmatched
  merge is still an entry (its subject as title). So that count alone cannot fail on this
  break, and the subject grep is there for it. The fixture's contract test (C02.7, unedited)
  also catches it. It is not in the break manifest: its command needs the kit.
- `encoding="utf-8"` in C04.2: `gh` writes UTF-8, and a text-mode `subprocess.run` with no
  encoding reads it in the locale's code page (cp1252 on Windows), which turns "→" into noise
  (D02.10's cause, in a new place). The fake cannot show a decoding fault, so C04.2 pins the
  keyword itself.
- The fake in C04.3 and C04.4 passes git's calls through: `bearing.ingest.history` and
  `bearing.ingest.gh` both use the one `subprocess.run`, so a fake that answered every call would
  also answer git's.
- The count: 30 tests pass today; the day adds 8 test methods (the `Test:` fields of C04.1–C04.5
  and C04.8), so `pytest -q` ends at "38 passed" (subtests besides).
- Verify's `make_repo.py .bearing/day04-check` refuses a directory that is not empty: delete it
  before a second local run.
- **Defect** D04.1 — found: spec-change PR · cause: process · made: Day 03 · H03.2 went forward
  as open (Day 3's Out of scope: "a `sqlite3` traceback today"; its Notes and the lab notebook
  carry it on), yet #23
  (`c5e3b50`) had already wrapped `bearing changelog`'s read in `except sqlite3.Error`, beyond
  Day 3's In scope and with no test. Seen in this spec's prototype: the three broken stores each
  print "bearing: cannot read store at" and exit 1. C04.1 is a `hold` with a test.
- **Defect** D04.2 — found: auditor · cause: spec · made: Day 04 · the first draft counted 7 new
  test methods and "37 passed"; the `Test:` fields name 8, so 38.
- **Defect** D04.3 — found: auditor · cause: spec · made: Day 04 · C04.6's own break (pass 1
  matching nothing) left `grep -c '^- #'` at 91: an unmatched merge is still an entry. C04.6 now
  also counts entries titled by their merge subject, 0.
- **Defect** D04.4 — found: auditor · cause: spec · made: Day 04 · C04.3 was tagged `new` but
  its `--prs` half passes today (no `gh` call); it is now C04.8, a `hold`.
- **Defect** D04.5 — found: auditor · cause: spec · made: Day 04 · C04.2 compared the call with
  `PR_LIST`, so a wrong command (no `body`, `--limit 100`) passed; the test now writes the list
  out.
- **Defect** D04.6 — found: auditor · cause: spec · made: Day 04 · C04.5 had no subject that
  parses but names neither record, so mapping to the subject's number whatever it is passed;
  commit C (#20, records #12 and #11) is that case.
- **Defect** D04.7 — found: auditor · cause: spec · made: Day 04 · C04.6's `gh ... >`
  in Windows PowerShell 5.1 writes UTF-16LE, which the filter fails on ("byte 0xff in position
  0"); C04.6 now says Git Bash.
- **Defect** D04.8 — found: auditor · cause: process · made: none · #20 (`681cca2`,
  `tooling/human-record`) changed the kit's `.github/pull_request_template.md` and `CLAUDE.md`
  with no Course correction, against plan.md's "Constraints"; H04.1 now names it for the
  kit-update PR.
- **Defect** D04.9 — found: auditor · cause: spec · made: Day 04 · C04.7 said "both contract
  tests"; `tests/contract/` holds three.
- At the close, on `e291344`: `python -m pytest -q` gave "38 passed, 33 subtests passed", the
  count above. Verify's ingest printed `merges 10  matched 9  unmatched merges 1  unmatched PRs 1
  direct 2`, and its changelog matched `changelog.md` with 10 lines starting "- #". C04.6 ran on
  the kit's checkout at `d9712fe`: `PR_LIST` gave 93 records, 91 kept by the filter, and the
  three lines were as the spec says. All 9 `manifest:` lines (1 in #25, 2 in #26, 5 in #27, 1 in
  #28) parsed as JSON, and each `find` occurs once in the merged code. Replayed with
  `scripts/break.py` in an LF worktree of `main`, each failed its check. Every criterion had a
  break from a track or the spec PR (C04.6's by hand), so the close ran no first break.
- **Defect** D04.10 — found: Track A · cause: process · made: Day 04 · the main session's
  Track A brief gave the expected count as 35, the spec's baseline of 30 plus 5, but Track 0
  (#26) had already brought `main` to 32. The implementer reported 37; the main session
  recounted it and said so in #27.
- **Defect** D04.11 — found: Track B · cause: process · made: Day 04 · the implementer ran the
  full suite before `ruff format`, so its count was from code that then changed. The main
  session re-ran the suite after formatting and took the count from that run (#28).
- **Defect** D04.12 — found: Track B · cause: process · made: Day 04 · the implementer's report
  gave no red value for the first record order of C04.5, though the criterion names it
  (`{A: 3, B: 5, C: 12}`). The main session ran `main`'s `mapping.py` on the test's input and
  confirmed both values in #28.
- The blind relabel at the close agreed on 11 of 12 stages, 11 of 12 causes and 12 of 12
  `made:`. D04.7's cause changed from `environment` to `spec`: Windows PowerShell's UTF-16 is
  the machine's, but the command could not be met as written, and the fix was to the spec's
  wording. D04.8 keeps `found: auditor`, where the rater read an escape: the auditor found it,
  and `made: none` already marks it as work outside any day, which the rules count as an escape
  whatever `found:` says.
- **Hand-off** H04.1 → the maintainer: the Phase 1 stop, after this day's close. Judge whether
  the kit's changelog is useful enough to go on; copy the kit in at one SHA in the kit-update PR,
  replacing the local changes to kit files (#4, #5, #7 and #9 in plan.md's Course corrections,
  and #20's `.github/pull_request_template.md` and `CLAUDE.md`, D04.8), with the kit fixes
  still open (H01.5, H01.6, H01.7, H02.4) made there first; and record
  `python scripts/token-usage.py --compare --split <date>` and the per-rung counts in the stop's
  Course correction. Then the plan-auditor on Phase 1 and Phase 2 (CLAUDE.md, step 6).
- **Hand-off** H04.2 → the maintainer: `PR_LIST` stops at 1000 merged PRs and `gh` does not say
  so; a history with more is cut without a word. Neither the kit (93) nor wordtally is near it.
