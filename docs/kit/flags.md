# The kit's flags, round 2

Round 2 of the judging of the kit's flags (Day 10; plan.md, Course correction at the Day 10
stop). These are the 26 flags of `docs/kit/direction.md` (Day 10 Track D, #63), each with the
maintainer's mark. The report came from the run Track D records, with Bearing's code at
`3ca3f7d` (Track C, #62) and the kit at `c12cfe5`:
`python -m bearing ingest <s>/kit.git --prs <s>/kit-prs.json --data <s>/data`, then
`python -m bearing direction <s>/kit.git --data <s>/data --config <s>/kit.toml`, where
`<s>/kit.toml` is `docs/kit/bearing.toml`.

The maintainer took Claude's suggestion: round 1's marks for the same 26 PRs, with each rule
mark rewritten for round 2's config, after a blind Fable reading of each PR's files and body
that differed on two flags (#16 and #31, both rule at low confidence). The flags,
`docs/kit/direction.md`, `docs/kit/bearing.toml` and the rule did not change after the first
mark. Round 1's marks are in `docs/kit/flags-round-1.md`.

Marks: real 13, rule 13

- #8 outside-area: area dashboard | scripts/test_token_usage.py, scripts/token-usage.py -- rule: list scripts/token-usage.py and scripts/test_token_usage.py under dashboard as well as tooling (the script writes docs/dashboard/token-usage.json)
- #12 outside-area: area dashboard | .github/workflows/pr-checks.yml, scripts/invariants.py, scripts/pr-names.py, scripts/test_invariants.py, scripts/test_pr_names.py -- real
- #14 outside-area: area dashboard | .claude/agents/agentic-engineering-auditor.md, .claude/agents/architecture-auditor.md, .claude/agents/implementer.md, .claude/agents/security-ops-auditor.md, .claude/agents/spec-auditor.md, .gitattributes, .github/pull_request_template.md, .github/workflows/dashboard.yml, .github/workflows/pr-checks.yml, docs/agent-workflow.png, docs/agent-workflow.svg, docs/workflow.md, scripts/test_invariants.py -- real
- #15 outside-area: area dashboard | docs/workflow.md, kit/examples/day-12-jwt-issuance.md, kit/examples/day-36-ecs-services.md, kit/jobmatch/CLAUDE.md, kit/jobmatch/audit-findings.md, kit/jobmatch/defects.md, kit/jobmatch/deployment.json, kit/jobmatch/lab-notebook.md, kit/jobmatch/live-checks.py, kit/jobmatch/plan.md, kit/jobmatch/token-usage.json, kit/lessons/attribution-rejected.md, kit/lessons/auditors-on-opus.md, kit/lessons/checks-before-push.md, kit/lessons/dev-loop-dropped.md, kit/lessons/implementer-on-haiku.md, kit/lessons/maintainer-review-style.md, kit/lessons/spec-auditor-eval.md, kit/lessons/spec-first-workflow.md, kit/lessons/spec-process-improvements.md -- real
- #16 outside-area: area dashboard | docs/lab-notebook.md, docs/workflow.md -- real
- #17 outside-area: area dashboard | .github/workflows/pr-checks.yml, scripts/pr-names.py, scripts/service-wiring.py, scripts/test_service_wiring.py -- real
- #20 outside-area: area dashboard | scripts/break.py, scripts/test_break.py -- real
- #21 outside-area: area dashboard | .claude/agents/defect-rater.md, .claude/agents/implementer.md, .gitattributes -- real
- #22 outside-area: area dashboard | scripts/break.py, scripts/test_break.py -- real
- #23 outside-area: area dashboard | .claude/agents/implementer.md, .github/pull_request_template.md -- real
- #24 outside-area: area dashboard | .github/workflows/pr-checks.yml, scripts/test_pr_names.py -- real
- #26 outside-area: area tooling | docs/dashboard/dashboard.css, docs/dashboard/dashboard.js, docs/dashboard/index.html, docs/workflow.md, kit/starter-check.py, kit/v2-manifest.md -- real
- #27 outside-area: area tooling | docs/dashboard/dashboard.css, docs/dashboard/dashboard.js -- real
- #31 outside-area: area tooling | kit/ASSESSMENT.md -- real
- #34 outside-area: area tooling | kit/ASSESSMENT.md -- rule: do not flag outside files that total under 20 changed lines and under 10% of the PR's non-shared changed lines (one link line to the replay format the PR adds)
- #37 outside-area: area tooling | kit/ASSESSMENT.md -- rule: do not flag outside files that total under 20 changed lines and under 10% of the PR's non-shared changed lines (three link lines to kit/replay/results.md the PR adds)
- #38 outside-area: area tooling | kit/ASSESSMENT.md -- rule: do not flag outside files that total under 20 changed lines and under 10% of the PR's non-shared changed lines (two pointer lines recording a tooling decision)
- #56 outside-area: area dashboard | scripts/behaviour-index.py -- rule: do not flag outside files that total under 20 changed lines and under 10% of the PR's non-shared changed lines (3 lines in scripts/behaviour-index.py beside 180 in-area lines)
- #72 outside-area: area tooling | docs/dashboard/token-usage.json -- rule: list docs/dashboard/token-usage.json under tooling as well as dashboard (scripts/token-usage.py writes it)
- #73 outside-area: area tooling | docs/dashboard/dashboard.js, docs/dashboard/token-usage.json -- rule: list docs/dashboard/token-usage.json under tooling as well as dashboard; do not flag outside files that total under 20 changed lines and under 10% of the PR's non-shared changed lines (the 4-line dashboard.js reader)
- #83 outside-area: area tooling | kit/examples/day-12-jwt-issuance.md -- rule: do not flag outside files that total under 20 changed lines and under 10% of the PR's non-shared changed lines (2 lines removing rm -rf from the example the new pitfall names)
- #85 outside-area: area specs | docs/architecture.md -- rule: add docs/architecture.md and docs/workflow.md to shared (drawn process text every process change edits)
- #88 outside-area: area tooling | docs/dashboard/dashboard.js -- rule: do not flag outside files that total under 20 changed lines and under 10% of the PR's non-shared changed lines (1 line: the evidence table's column for the new check kind)
- #89 outside-area: area specs | .claude/agents/spec-auditor.md, .github/pull_request_template.md -- rule: add .claude/agents/ and .github/pull_request_template.md to shared (process text every process change edits)
- #90 outside-area: area tooling | docs/dashboard/dashboard.js, docs/dashboard/index.html -- rule: do not flag outside files that total under 20 changed lines and under 10% of the PR's non-shared changed lines (17 of 191 lines showing the new count on the page)
- #94 outside-area: area tooling | docs/architecture.md, spec-drift.config.json -- rule: list spec-drift.config.json under tooling as well as dashboard (tooling scripts read it); add docs/architecture.md to shared
