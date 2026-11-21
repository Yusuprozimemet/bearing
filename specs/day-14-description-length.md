# Day 14 — Description length: one or two sentences

**Phase:** 6 · **Depends on:** Day 13 · **Expected PRs:** 3 (this spec, track A, the close)

## Goal
The description `what_i_built` gives, and with it the one `bearing changelog` prints and the
page's `paragraph`, is at most its first two sentences, and every check is a test CI runs
(plan.md, Phase 6).

## In scope
- **The two-sentence cut** (Track A), in `bearing/ingest/text.py`: `what_i_built` returns at
  most the first two sentences of the paragraph it finds, from the "What I built" section or
  from the fallback, the body's first paragraph. A sentence ends at ".", "!" or "?" followed by
  whitespace (a space, a tab or a line feed) or by the end of the text. The shortened text is
  the paragraph's characters up to and including the second sentence's end mark, as written
  (the line feeds and spaces inside it kept), with trailing whitespace stripped. A paragraph of
  one or two sentences, or with no end mark, is returned as it is today.
- `bearing changelog` and the page read `what_i_built` and nothing else for the description
  (`bearing/ingest/changelog.py`, `bearing/page/data.py`), so neither changes.
- The new tests go in a new file, `tests/test_sentences.py`, so `tests/test_text.py`, which
  holds C03.2's cases, stays unedited.

## Out of scope
- Abbreviations: "e.g. " ends a sentence, as does any other abbreviation followed by
  whitespace ("Mr. ", "v1. "). A known limit, recorded and not handled (plan.md, Phase 6).
- Any other description rule: an opener that says nothing (#5), a length in characters, a
  marker that the text was cut. None is asked for.
- A new contract version: every description on the fixture is at most one sentence, so no golden file
  changes (plan.md, Phase 6).
- `.github/`, `.claude/`, `scripts/`, `plan.md`, `specs/README.md` and the dependencies: the
  day's code stays in `bearing/` and `tests/` (plan.md, Phase 6). C14.5 holds it.
- The agentic-workflow-driver, which runs this day's first step in a Docker container: a
  separate program; nothing here depends on it (plan.md, Phase 6).

## Tracks

One track. C14.3 is `hold` with a test Track A adds, without a Track 0 (as Day 13's C13.3
did): Track A's PR shows that test passing on `main`'s code
(`python scripts/seen-red.py -- python -m pytest -q tests/test_sentences.py::SentenceTest::test_short_unchanged`
exits 1, "passes there"), then breaks it. C14.4 and C14.5 are `hold` and their checks exist:
their breaks run in this spec's PR.

Each case in `tests/test_sentences.py` is a `subTest`: 3 tests and 12 subtests, so
`python -m pytest -q` goes from "104 passed, 116 subtests passed" to "107 passed, 128 subtests
passed".

| Track | Owner | Work |
|---|---|---|
| A | implementer | C14.1–C14.3: `bearing/ingest/text.py`, `tests/test_sentences.py` |

## Acceptance criteria
Tick each box in the closing PR once its evidence is in it; under a box left unticked, write
`Not proven: <why>` (`specs/README.md`, "Evidence at the close").

- [x] C14.1 **new** — Three or more sentences give the first two, exactly as written,
      trailing whitespace stripped. `what_i_built` gives, for
      "## What I built\n\nOne. Two. Three.\n", "One. Two."; for
      "## What I built\n\nOne.  Two.\tThree.\n", "One.  Two."; for
      "## What I built\n\nFirst line. Second\nline.  Third one.\n", "First line. Second\nline.";
      for "## What I built\n\nOne.\nTwo.\nThree.\n" (an end mark followed by a line feed),
      "One.\nTwo."; and for the body with no section "One. Two. Three. Four.\n", "One. Two.".
      Red today: each returns the whole paragraph, "One. Two. Three." for the first.
      Test: `tests/test_sentences.py::SentenceTest::test_three_sentences_give_two`.
      Evidence: `SentenceTest.test_three_sentences_give_two` (#101), seen red in #101 on `main` ("5 failed, 1 passed") and again at the close on `714412f`'s code ("7 failed, 3 passed, 5 subtests passed", the whole file); `python -m pytest -q` at the close on `2d45f42`.
- [x] C14.2 **new** — "!" and "?" end a sentence as "." does. `what_i_built` gives, for
      "## What I built\n\nDone! Really? Yes.\n", "Done! Really?"; and for
      "## What I built\n\nWhy? Because. More.\n", "Why? Because.".
      Red today: each returns the whole paragraph, "Done! Really? Yes." for the first.
      Test: `tests/test_sentences.py::SentenceTest::test_bang_and_question_end`.
      Evidence: `SentenceTest.test_bang_and_question_end` (#101), seen red in #101 on `main` ("2 failed, 1 passed") and again at the close on `714412f`'s code (with C14.1's test); `python -m pytest -q` at the close on `2d45f42`.
- [x] C14.3 **hold** — One or two sentences, and a "." with no whitespace after it, are left as
      they are. `what_i_built` gives, for "## What I built\n\nOne. Two.\n", "One. Two.";
      for "## What I built\n\nOne sentence.\n", "One sentence."; for
      "## What I built\n\nNo end mark\n", "No end mark"; for
      "## What I built\n\nIs it? Yes!\n", "Is it? Yes!"; and for
      "## What I built\n\napp/b.py stops importing app.a. Version 1.2 is out.\n" the same
      text, "app/b.py stops importing app.a. Version 1.2 is out.".
      Test: `tests/test_sentences.py::SentenceTest::test_short_unchanged`.
      Track A's PR breaks it: the cut made after the first sentence, not the second.
      Evidence: `SentenceTest.test_short_unchanged` (#101), which passed on `main`'s code in #101 (`seen-red.py`, "1 passed, 5 subtests passed"); `python -m pytest -q` at the close on `2d45f42`.
      broken: the cut made after the first sentence, not the second → 3 failed, 1 passed, 2 subtests passed in 0.29s (#101)
- [x] C14.4 **hold** — No contract change, and C03.2's cases pass unedited:
      `git -c core.safecrlf=false diff --exit-code c214b09 -- tests/contract/ tests/test_text.py`
      prints nothing and exits 0 (`c214b09` is `main` at Day 13's close, #96), and
      `python -m pytest -q` passes.
      Evidence: the diff against `c214b09` printed nothing and exited 0, and `python -m pytest -q` printed "107 passed, 128 subtests passed", at the close on `2d45f42` (#101).
      broken: a contract test edited (its docstring) → import sys (#99)
- [x] C14.5 **hold** — The day stays in `bearing/` and `tests/`, with no new dependency:
      `git -c core.safecrlf=false diff --exit-code --name-only 52416c1 -- .github .claude scripts pyproject.toml`
      prints nothing and exits 0 (`52416c1` is `main` with Phase 6 merged, #98).
      Evidence: the diff against `52416c1` printed nothing and exited 0 at the close on `2d45f42` (#101).
      broken: a file under scripts/ edited → scripts/pr-names.py (#99)

## Verify
```bash
python -m pytest -q                                              # 107 passed, 128 subtests passed
python -m pytest -q tests/test_sentences.py tests/test_text.py
git -c core.safecrlf=false diff --exit-code c214b09 -- tests/contract/ tests/test_text.py
git -c core.safecrlf=false diff --exit-code --name-only 52416c1 -- .github .claude scripts pyproject.toml
ruff check . && ruff format --check .
```

## Notes
- The cut is in `what_i_built`, not in the changelog or the page, so `read_entries` and both
  outputs see one text; the store keeps `prs.body` whole, and the page's flags still read it
  whole (`bearing/page/data.py`). The criteria test `what_i_built` alone: `Entry.paragraph`
  is its return value (`bearing/ingest/changelog.py`) and the page's `paragraph` is
  `Entry.paragraph` (`bearing/page/data.py`), with no other path.
- Inside a paragraph the line feeds are kept: a sentence that runs over two lines of the PR
  body is two lines in the changelog, as today (C03.2's "Line one\nline two").
- "Exactly as written" means the characters up to the second end mark, not the sentences
  rejoined: two spaces or a tab between them stay (C14.1's second case).
- Known limit (plan.md, Phase 6): "e.g. " ends a sentence, so "Use a flag, e.g. --x. Then y."
  is cut to "Use a flag, e.g. --x." No criterion pins it either way.
- plan.md says "whitespace"; this spec narrows it to a space, a tab or a line feed, so a
  no-break space, a form feed or a vertical tab after an end mark does not end a sentence. No
  criterion tells the two apart. "Trailing whitespace stripped" is kept from plan.md's wording,
  but cannot change the result: the cut ends at an end mark, and `what_i_built` already strips
  each line's right side.
- Spec-auditor, before this spec's PR: 5 findings. Fixed: no case had an end mark followed by
  a line feed (C14.1's fourth case added); C14.3, a `hold` with no Track 0 and no run on
  `main`'s code (the `seen-red.py` run added under Tracks); the Note said the store held the
  cut text, and the expected test count was missing. Noted: the narrowed whitespace (the Note
  above); "one sentence" on the fixture is "at most one" (#4's body is "").
- Two defects were found before any code (D14.1, D14.2), two in Track A's review (D14.3,
  D14.4) and two outside any day's work (D14.5, D14.6). The blind rater agreed with all six on
  stage, cause and `made:`.
- **Defect** D14.1 — found: auditor · cause: spec · made: Day 14 · C14.1 named a line feed as
  a sentence end but had no case with one, so a cut that ignored line feeds passed every
  criterion; a case added before the spec's PR.
- **Defect** D14.2 — found: auditor · cause: spec · made: Day 14 · the first Note said the
  store held the cut text; it keeps the body whole. Corrected before the spec's PR.
- The close ran on `2d45f42`. `python -m pytest -q` printed "107 passed, 128 subtests passed",
  against "104 passed, 116 subtests passed" before the day. Each of the Verify commands ran as
  written: the two test files "5 passed, 27 subtests passed", both diffs nothing with exit 0,
  and `ruff format --check .` clean. `ruff check .` here reports 70 EXE002 errors ("executable
  but no shebang"), all of them because this checkout's files are mode 777 on disk with
  `core.filemode=false`; every file in the index is `100644`, CI's "Style check" passed on #101,
  and `ruff check . --ignore EXE002` passes (D14.6).
- All 3 breaks in `specs/breaks/day-14.json` were replayed at the close with `scripts/break.py`
  and each failed its check. The `broken:` lines above are the close's, not the PRs'; C14.4's
  and C14.5's failed by exit code 1, the line being the check's last output.
- Phase 6's "Done when" (plan.md): three sentences give two is C14.1; one or two unchanged is
  C14.3; "!" and "?" as "." is C14.2; the contract diff is C14.4. `pytest -q` in CI is the
  "Tests" check on #101. Every one is a test or command CI runs, with no hand run and no kit
  history.
- This day leaves no new hand-off. The known limit ("e.g. " ends a sentence) stays recorded
  above and in plan.md, owned by no day. Phase 6 ends here: the plan-auditor runs on Phase 6
  and Phase 7 on fresh `main` after this close merges.
- Hand-off: to the maintainer, for CLAUDE.md: `scripts/token-usage.py` reads
  `~/.claude/projects` by default, and in a session whose Claude Code keeps its transcripts
  elsewhere (here `/claude/projects`, the driver's container) it counts nothing new and rewrites
  only the file's formatting. Pass `--transcripts <dir>` there, and check that the day's rows
  appear before committing (D14.5).
- **Defect** D14.3 — found: review · cause: implementation · made: Day 14 · Track A's comment
  said a paragraph "with fewer than three end marks is returned whole", but "One. Two. more" is
  cut; the comment was corrected in review, before #101.
- **Defect** D14.4 — found: review · cause: process · made: Day 14 · the implementer reported
  `tests/test_sentences.py` as 45 lines; `git diff --numstat` counted 50. Recounted before
  #101's description.
- **Defect** D14.5 — found: close · cause: environment · made: none · `scripts/token-usage.py`
  with its default transcripts directory found none of this machine's transcripts, which are
  under `/claude/projects`; the close ran it again with `--transcripts /claude/projects`.
- **Defect** D14.6 — found: Track A · cause: environment · made: none · `ruff check .` fails
  locally on 70 EXE002 errors from the checkout's file modes, which the index and CI do not
  have; recorded in #101 and at the close, no file changed.
