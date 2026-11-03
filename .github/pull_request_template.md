## What I built

<!-- One or two sentences. What does this change do? -->

## Why this approach

<!-- The diff already shows what changed. Explain why you did it this way, and
     what you considered instead. "An AI wrote it" is not an answer here, and it
     will not be an answer in review either. Each break on purpose is one line of
     its own, `broken: <what> → <what it reported>`, or `broken: none → <why>`, with
     the `manifest: {...}` line scripts/break.py printed above it: the close copies
     that line into specs/breaks/day-NN.json. -->

## Contract impact

<!-- A contract here is an output format under golden-file test in tests/contract/
     (golden files included), or an applied migration in bearing/migrations/. Both are
     frozen: a change is a new version, decided in a plan-change PR the maintainer
     reviews. Say "None" if not. -->

None

## How to run

<!-- The exact commands a reviewer runs to see this working. -->

```bash

```

## Self-check

- [ ] I ran this and it works
- [ ] Tests pass locally
- [ ] No secrets, tokens, or connection strings in the diff
- [ ] This pull request does one thing
- [ ] Track PRs only: each new test was run on the code before the change, and "Why this
      approach" says how it failed
- [ ] Every number in this description was counted from the diff or a run, not copied
- [ ] Spec changes only: every acceptance criterion is tagged `new` or `hold`, and each check
      has been seen to fail (see `specs/README.md`)
- [ ] Spec changes only: every spec-auditor finding is listed, one line each, with one ending:
      fixed, known limit (why), maintainer action, or rejected (why)
