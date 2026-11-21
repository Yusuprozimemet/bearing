# Day 24 — A `bearing.toml` that is not UTF-8

**Phase:** 16 · **Depends on:** Day 23 · **Expected PRs:** 2 (track A, the close; this spec is in the Days 19 to 24 spec PR)

## Goal
`bearing direction` and `bearing page` stop with "bearing: cannot read config FILE: not UTF-8",
exit 1 and nothing on stdout, when the config's bytes are not UTF-8, as they do for a config
that is not TOML, where today both end in a `UnicodeDecodeError` traceback; and every new
behaviour is a test CI runs (plan.md, Phase 16).

## In scope
- **The read** (Track A), in `_read` in `bearing/direction/config.py`, which `load_config` and
  `load_rules` (Day 9) share: `UnicodeDecodeError` from `tomllib.load` raises
  `ConfigError(f"cannot read config {path}: not UTF-8")`, `path` as given, the prefix the
  `TOMLDecodeError` line has and the reason Day 20's `--prs` line gives. Both commands already
  print a `ConfigError` through `_fail`, and they read the config before the store is looked
  for, so the line comes first whatever `--data` holds.
- A config that starts with a UTF-8 byte order mark keeps today's line, "bearing: cannot read
  config FILE: Invalid statement (at line 1, column 1)" (`tomllib` reads UTF-8, not
  `utf-8-sig`), as Day 20 keeps `--prs`'s. A missing config and a config that is not TOML keep
  theirs (C24.5).
- The new tests go in a new file, `tests/test_config_bytes.py`. Its class writes each config
  under its temporary directory and runs `python -m bearing` with `subprocess.run` from the
  repository root, as `tests/test_direction_cli.py` does, with `<repo>` the repository root and
  `--data` a directory that does not exist; it needs no fixture. Its stderr is read as UTF-8
  with `\r\n` as `\n`. It imports what it tests from `bearing` inside the test, so a missing name
  fails that test and not the file's collection.

## Out of scope
- Reading a config with a byte order mark, or in another encoding: TOML is UTF-8, and plan.md's
  Phase 16 keeps the mark an error.
- The other config errors' wording: unchanged (C24.5).
- A new contract version: neither command's output on the fixture changes (C24.6).
- `.github/`, `.claude/`, `scripts/`, `plan.md` and the dependencies: the day's code stays in
  `bearing/` and `tests/` (plan.md, Phases 11 to 16). C24.7 holds it.

## Tracks

One track. C24.1–C24.3 are `new`: Track A's PR shows their tests failing on `main`'s code with
`python scripts/seen-red.py -- python -m pytest -q tests/test_config_bytes.py::ConfigBytesTest::test_direction tests/test_config_bytes.py::ConfigBytesTest::test_page tests/test_config_bytes.py::ConfigBytesTest::test_load`,
which reports "3 failed". C24.4 is `hold` with a test Track A adds, without a Track 0 (as Day
17's C17.7): Track A's PR shows it passing on `main`'s code with
`python scripts/seen-red.py -- python -m pytest -q tests/test_config_bytes.py::ConfigBytesTest::test_bom`,
which exits 1 ("passes there"), and then breaks it. C24.5–C24.7 are `hold` and their checks
exist: their breaks ran in the spec PR for Days 19 to 24.

`tests/test_config_bytes.py` holds 4 tests and no subtests. So `python -m pytest -q` goes from
Day 23's end, "149 passed, 131 subtests passed", to "153 passed, 131 subtests passed".

| Track | Owner | Work |
|---|---|---|
| A | implementer | C24.1–C24.4: `bearing/direction/config.py`, `tests/test_config_bytes.py` |

## Acceptance criteria
Tick each box in the closing PR once its evidence is in it; under a box left unticked, write
`Not proven: <why>` (`specs/README.md`, "Evidence at the close").

`<cfg>` is a file holding the bytes `ff fe` followed by `[areas]` and a line feed.

- [ ] C24.1 **new** — `direction` names the config. `direction <repo> --data <dir> --config
      <cfg>`, `<dir>` a directory that does not exist, returns 1, its stdout is empty, and its
      stderr is exactly "bearing: cannot read config <cfg>: not UTF-8" and a line feed (`<cfg>`
      as given).
      Red today: a traceback ending "UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff
      in position 0: invalid start byte".
      Test: `tests/test_config_bytes.py::ConfigBytesTest::test_direction`.
- [ ] C24.2 **new** — `page` names the config and writes nothing. `page <repo> --data <dir>
      --config <cfg> --out <out>`, `<out>` a path under the class's temporary directory that
      does not exist, returns 1, its stdout is empty, its stderr is C24.1's line, and `<out>`
      does not exist.
      Red today: C24.1's traceback.
      Test: `tests/test_config_bytes.py::ConfigBytesTest::test_page`.
- [ ] C24.3 **new** — Both readers raise it. `bearing.direction.config.load_config(<cfg>)` and
      `load_rules(<cfg>)` each raise `ConfigError` whose text is exactly
      "cannot read config <cfg>: not UTF-8".
      Red today: each raises `UnicodeDecodeError`.
      Test: `tests/test_config_bytes.py::ConfigBytesTest::test_load`.
- [ ] C24.4 **hold** — A byte order mark keeps its line. With `<bom>` a file holding the bytes
      `ef bb bf` and then `tests/fixtures/bearing.toml`'s bytes, `direction <repo> --data <dir>
      --config <bom>` returns 1, its stdout is empty, and its stderr is exactly "bearing: cannot
      read config <bom>: Invalid statement (at line 1, column 1)" and a line feed.
      Test: `tests/test_config_bytes.py::ConfigBytesTest::test_bom`.
      Track A's PR breaks it: the config read through `utf-8-sig`, so the mark is dropped and
      the command reaches the missing store.
- [ ] C24.5 **hold** — The other config errors stay word for word:
      `python -m pytest -q tests/test_config.py tests/test_direction_cli.py tests/test_page_cli.py`
      passes, and
      `git -c core.safecrlf=false diff --exit-code 714412f -- tests/test_config.py tests/test_page_cli.py`
      prints nothing and exits 0. Day 15 edits `tests/test_direction_cli.py` (C15.5), so it has
      no `git diff` half here.
      The spec PR breaks each half: the `TOMLDecodeError` line's "cannot read config " reading
      "cannot parse config ", and a line of `tests/test_config.py` changed.
- [ ] C24.6 **hold** — No contract changes: `python -m pytest -q tests/contract/` passes, and
      `git -c core.safecrlf=false diff --exit-code 714412f -- tests/contract/ tests/fixtures/expected/ tests/fixtures/make_repo.py tests/fixtures/bearing.toml`
      prints nothing and exits 0 (`714412f` is `main` with Day 14's spec merged, #99); and
      `python -m pytest -q` passes.
      The spec PR breaks each half: the direction report's "## Churn" heading misspelt, and a
      line of `tests/fixtures/bearing.toml` changed.
- [ ] C24.7 **hold** — The day stays in `bearing/` and `tests/`, with no new dependency:
      `git -c core.safecrlf=false diff --exit-code --name-only 1472abc -- .github .claude scripts pyproject.toml plan.md`
      prints nothing and exits 0 (`1472abc` is `main` with Phases 11 to 16 merged, #118).
      The spec PR breaks it: a line of `.github/workflows/tests.yml` changed.

## Verify
```bash
python -m pytest -q                                              # 153 passed, (131 subtests passed)
python -m pytest -q tests/test_config_bytes.py
python -m pytest -q tests/test_config.py tests/test_direction_cli.py tests/test_page_cli.py
python -m pytest -q tests/contract/
git -c core.safecrlf=false diff --exit-code 714412f -- tests/test_config.py tests/test_page_cli.py
git -c core.safecrlf=false diff --exit-code 714412f -- tests/contract/ tests/fixtures/expected/ tests/fixtures/make_repo.py tests/fixtures/bearing.toml
git -c core.safecrlf=false diff --exit-code --name-only 1472abc -- .github .claude scripts pyproject.toml plan.md
ruff check . && ruff format --check .
```

## Notes
- What today's code does, run in the spec PR's session on `main` at `8a17f82` with Python
  3.12.10: `direction` and `page` with `<cfg>` each end in a 22-line traceback ending
  "UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff in position 0: invalid start byte",
  exit 1, empty stdout, and `page` writes no `--out`; with `<bom>`, "bearing: cannot read config
  <bom>: Invalid statement (at line 1, column 1)". `_read` catches only
  `tomllib.TOMLDecodeError`, and `tomllib.load` decodes the bytes as UTF-8 first.
- `tests/test_config.py::ConfigTest::test_errors` checks the not-TOML line by its prefix,
  "cannot read config <path>: ", which the new line shares; it passes unedited (C24.5).
- Written ahead of its day, against `main` at `8a17f82`, before the code of Days 15 to 23 has
  merged: the test count assumes they land as their specs say (plan.md, Course correction after
  Day 15's track A, item 5). The day's own spec-auditor run reads this spec against `main` as it
  is then, and re-pins C24.7's base if anything under its paths has merged since `1472abc`.
- C24.5–C24.7's `git diff` checks are commands, not tests: plan.md's "every check is a test" is
  read as every new behaviour, as Days 15 to 18 did.
- Spec-auditor, in the spec PR for Days 19 to 24 (one run over all six): no finding here. It
  confirmed both tracebacks, that `page` writes no `--out`, the byte order mark's line, and the
  count.
- Phase 16 is the course correction's margin, found by #118's plan-auditor (plan.md, Course
  correction after Day 15's track A, item 7); no hand-off ID names it. No criterion in force
  pins a non-UTF-8 config, so no `Replaces:` line.
