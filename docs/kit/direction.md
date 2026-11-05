## Churn

| Week | Area | Added | Deleted |
|---|---|---|---|
| 2026-W44 | dashboard | 2042 | 314 |
| 2026-W44 | docs | 3394 | 538 |
| 2026-W44 | other | 1402 | 136 |
| 2026-W44 | specs | 167 | 56 |
| 2026-W44 | tooling | 3787 | 359 |
| 2026-W45 | dashboard | 316 | 43 |
| 2026-W45 | docs | 1401 | 34 |
| 2026-W45 | other | 13 | 1 |
| 2026-W45 | specs | 76 | 12 |
| 2026-W45 | tooling | 2644 | 185 |

## Coupling

| File | File | PRs | Hidden dependency |
|---|---|---|---|
| .claude/agents/implementer.md | specs/README.md | #14, #21, #23 | tooling, specs |
| .claude/agents/spec-auditor.md | specs/README.md | #14, #40, #89 | tooling, specs |
| .claude/settings.json | .gitignore | #26, #61, #93 | tooling, other |
| .claude/settings.json | CLAUDE.md | #26, #59, #61, #64, #93 | tooling, docs |
| .github/pull_request_template.md | specs/README.md | #14, #23, #83, #89 | tooling, specs |
| .github/workflows/evidence.yml | CLAUDE.md | #32, #49, #94 | tooling, docs |
| .github/workflows/evidence.yml | README.md | #32, #82, #94 | tooling, docs |
| .github/workflows/evidence.yml | scripts/evidence.py | #32, #49, #82, #94 | no |
| .github/workflows/evidence.yml | specs/README.md | #32, #82, #94 | tooling, specs |
| .github/workflows/pr-checks.yml | CLAUDE.md | #26, #42, #54 | tooling, docs |
| .github/workflows/pr-checks.yml | README.md | #24, #26, #33, #54 | tooling, docs |
| .github/workflows/pr-checks.yml | kit/CHANGES.md | #17, #24, #26, #33, #42, #81 | tooling, docs |
| .github/workflows/pr-checks.yml | scripts/spec-drift.py | #14, #17, #26, #54, #81 | tooling, dashboard |
| .github/workflows/pr-checks.yml | scripts/test_invariants.py | #12, #14, #26 | no |
| .github/workflows/pr-checks.yml | scripts/test_spec_drift.py | #17, #26, #54, #81 | tooling, dashboard |
| .github/workflows/pr-checks.yml | scripts/test_track_red.py | #26, #54, #81 | no |
| .github/workflows/pr-checks.yml | scripts/track-red.py | #26, #54, #81 | no |
| .github/workflows/pr-checks.yml | specs/README.md | #14, #26, #33 | tooling, specs |
| .github/workflows/spec-drift-tests.yml | CHANGES.md | #5, #7, #11, #14 | tooling, other |
| .github/workflows/spec-drift-tests.yml | SOURCE.md | #5, #7, #11, #14 | tooling, other |
| .github/workflows/spec-drift-tests.yml | kit/CHANGES.md | #18, #26, #30 | tooling, docs |
| .github/workflows/spec-drift-tests.yml | scripts/spec-drift.py | #11, #14, #26 | tooling, dashboard |
| .github/workflows/spec-drift-tests.yml | scripts/test_spec_drift.py | #5, #7, #11, #18, #26 | tooling, dashboard |
| .gitignore | CLAUDE.md | #26, #61, #93 | other, docs |
| CHANGES.md | SOURCE.md | #2, #3, #4, #5, #7, #8, #9, #10, #11, #12, #13, #14 | no |
| CHANGES.md | docs/dashboard/dashboard.js | #3, #4, #5, #8, #10, #13 | other, dashboard |
| CHANGES.md | kit/page/jobmatch-boxes.sha256 | #7, #10, #13 | other, docs |
| CHANGES.md | scripts/spec-drift.py | #2, #8, #9, #10, #11, #13, #14 | other, dashboard |
| CHANGES.md | scripts/test_spec_drift.py | #2, #3, #4, #5, #7, #8, #9, #10, #11, #13 | other, dashboard |
| CLAUDE.md | README.md | #16, #21, #22, #26, #31, #32, #54, #55, #83, #94 | no |
| CLAUDE.md | kit/CHANGES.md | #16, #21, #22, #23, #26, #31, #32, #40, #42, #43, #83 | no |
| CLAUDE.md | kit/SOURCE.md | #16, #21, #26 | no |
| CLAUDE.md | scripts/break.py | #22, #47, #54, #83 | docs, tooling |
| CLAUDE.md | scripts/cap-output.py | #61, #62, #63 | docs, tooling |
| CLAUDE.md | scripts/evidence.py | #26, #32, #49, #94 | docs, tooling |
| CLAUDE.md | scripts/spec-drift.py | #22, #26, #54, #67 | docs, dashboard |
| CLAUDE.md | scripts/test_break.py | #22, #26, #47, #54, #83 | docs, tooling |
| CLAUDE.md | scripts/test_cap_output.py | #61, #62, #63 | docs, tooling |
| CLAUDE.md | scripts/test_evidence.py | #26, #47, #94 | docs, tooling |
| CLAUDE.md | scripts/test_spec_drift.py | #16, #22, #26, #54, #67 | docs, dashboard |
| CLAUDE.md | scripts/test_track_red.py | #26, #31, #43, #54 | docs, tooling |
| CLAUDE.md | scripts/track-red.py | #26, #43, #54 | docs, tooling |
| CLAUDE.md | specs/README.md | #21, #23, #26, #31, #32, #40, #43, #83, #85, #94 | docs, specs |
| CLAUDE.md | specs/_template.md | #23, #31, #40 | docs, specs |
| README.md | docs/workflow.md | #15, #16, #26 | no |
| README.md | kit/CHANGES.md | #15, #16, #18, #21, #22, #24, #26, #31, #32, #33, #52, #82, #83 | no |
| README.md | kit/SOURCE.md | #15, #16, #18, #21, #26 | no |
| README.md | scripts/break.py | #22, #54, #83 | docs, tooling |
| README.md | scripts/evidence.py | #26, #32, #82, #94 | docs, tooling |
| README.md | scripts/spec-drift.py | #15, #22, #26, #54 | docs, dashboard |
| README.md | scripts/test_break.py | #22, #26, #54, #83 | docs, tooling |
| README.md | scripts/test_evidence.py | #26, #82, #94 | docs, tooling |
| README.md | scripts/test_spec_drift.py | #15, #16, #18, #22, #26, #54 | docs, dashboard |
| README.md | scripts/test_track_red.py | #26, #31, #54 | docs, tooling |
| README.md | specs/README.md | #21, #26, #31, #32, #33, #82, #83, #94 | docs, specs |
| SOURCE.md | docs/dashboard/dashboard.js | #3, #4, #5, #8, #10, #13 | other, dashboard |
| SOURCE.md | kit/page/jobmatch-boxes.sha256 | #7, #10, #13 | other, docs |
| SOURCE.md | scripts/spec-drift.py | #2, #8, #9, #10, #11, #13, #14 | other, dashboard |
| SOURCE.md | scripts/test_spec_drift.py | #2, #3, #4, #5, #7, #8, #9, #10, #11, #13 | other, dashboard |
| docs/dashboard/dashboard.css | docs/dashboard/dashboard.js | #19, #26, #27, #57, #67 | no |
| docs/dashboard/dashboard.css | docs/dashboard/index.html | #19, #26, #57, #67 | no |
| docs/dashboard/dashboard.css | kit/CHANGES.md | #19, #26, #27 | dashboard, docs |
| docs/dashboard/dashboard.css | kit/page/jobmatch-boxes.sha256 | #19, #26, #27, #57, #67 | dashboard, docs |
| docs/dashboard/dashboard.css | scripts/spec-drift.py | #26, #27, #67 | no |
| docs/dashboard/dashboard.css | scripts/test_spec_drift.py | #19, #26, #27, #57, #67 | no |
| docs/dashboard/dashboard.js | docs/dashboard/index.html | #8, #13, #15, #19, #26, #57, #58, #67, #70, #90 | no |
| docs/dashboard/dashboard.js | kit/CHANGES.md | #15, #17, #19, #25, #26, #27 | dashboard, docs |
| docs/dashboard/dashboard.js | kit/SOURCE.md | #15, #17, #19, #26 | dashboard, docs |
| docs/dashboard/dashboard.js | kit/page/jobmatch-boxes.sha256 | #10, #13, #19, #25, #26, #27, #57, #67, #70 | dashboard, docs |
| docs/dashboard/dashboard.js | scripts/spec-drift.py | #8, #10, #13, #15, #17, #26, #27, #58, #67, #90 | no |
| docs/dashboard/dashboard.js | scripts/test_spec_drift.py | #3, #4, #5, #8, #10, #13, #15, #17, #19, #25, #26, #27, #57, #58, #67, #70, #90 | no |
| docs/dashboard/dashboard.js | scripts/test_token_usage.py | #8, #26, #73 | dashboard, tooling |
| docs/dashboard/dashboard.js | scripts/token-usage.py | #8, #26, #73 | dashboard, tooling |
| docs/dashboard/dashboard.js | specs/README.md | #26, #88, #90 | dashboard, specs |
| docs/dashboard/index.html | kit/CHANGES.md | #15, #19, #26 | dashboard, docs |
| docs/dashboard/index.html | kit/SOURCE.md | #15, #19, #26 | dashboard, docs |
| docs/dashboard/index.html | kit/page/jobmatch-boxes.sha256 | #13, #19, #26, #57, #67, #70 | dashboard, docs |
| docs/dashboard/index.html | scripts/spec-drift.py | #8, #13, #15, #26, #58, #67, #90 | no |
| docs/dashboard/index.html | scripts/test_spec_drift.py | #8, #13, #15, #19, #26, #57, #58, #67, #70, #90 | no |
| docs/workflow.md | kit/CHANGES.md | #15, #16, #26, #91 | no |
| docs/workflow.md | kit/SOURCE.md | #15, #16, #26 | no |
| docs/workflow.md | scripts/spec-drift.py | #14, #15, #26 | docs, dashboard |
| docs/workflow.md | scripts/test_spec_drift.py | #15, #16, #26 | docs, dashboard |
| kit/ASSESSMENT.md | kit/CHANGES.md | #31, #34, #37, #38 | no |
| kit/CHANGES.md | kit/SOURCE.md | #15, #16, #17, #18, #19, #20, #21, #26, #77 | no |
| kit/CHANGES.md | kit/page/jobmatch-boxes.sha256 | #19, #25, #26, #27 | no |
| kit/CHANGES.md | kit/replay/manifest.json | #34, #35, #36, #37 | no |
| kit/CHANGES.md | kit/starter-check.py | #18, #19, #26 | no |
| kit/CHANGES.md | scripts/break.py | #20, #22, #83 | docs, tooling |
| kit/CHANGES.md | scripts/evidence.py | #26, #32, #81, #82 | docs, tooling |
| kit/CHANGES.md | scripts/spec-drift.py | #15, #17, #20, #22, #26, #27, #29, #81 | docs, dashboard |
| kit/CHANGES.md | scripts/test_break.py | #20, #22, #26, #83 | docs, tooling |
| kit/CHANGES.md | scripts/test_evidence.py | #26, #81, #82 | docs, tooling |
| kit/CHANGES.md | scripts/test_replay_set.py | #34, #35, #36, #41 | docs, tooling |
| kit/CHANGES.md | scripts/test_spec_drift.py | #15, #16, #17, #18, #19, #20, #22, #25, #26, #27, #29, #81 | docs, dashboard |
| kit/CHANGES.md | scripts/test_track_red.py | #26, #31, #43, #81 | docs, tooling |
| kit/CHANGES.md | scripts/track-red.py | #26, #43, #81 | docs, tooling |
| kit/CHANGES.md | specs/README.md | #21, #23, #26, #31, #32, #33, #40, #43, #44, #82, #83 | docs, specs |
| kit/CHANGES.md | specs/_template.md | #23, #31, #40, #91 | docs, specs |
| kit/SOURCE.md | kit/starter-check.py | #18, #19, #26 | no |
| kit/SOURCE.md | scripts/spec-drift.py | #15, #17, #20, #26 | docs, dashboard |
| kit/SOURCE.md | scripts/test_spec_drift.py | #15, #16, #17, #18, #19, #20, #26 | docs, dashboard |
| kit/page/jobmatch-boxes.sha256 | scripts/spec-drift.py | #10, #13, #26, #27, #67 | docs, dashboard |
| kit/page/jobmatch-boxes.sha256 | scripts/test_spec_drift.py | #7, #10, #13, #19, #25, #26, #27, #57, #67, #70 | docs, dashboard |
| kit/replay/manifest.json | scripts/test_replay_set.py | #34, #35, #36 | docs, tooling |
| kit/starter-check.py | scripts/test_spec_drift.py | #18, #19, #26 | docs, dashboard |
| scripts/break.py | scripts/spec-drift.py | #20, #22, #54 | tooling, dashboard |
| scripts/break.py | scripts/test_break.py | #20, #22, #47, #54, #83 | no |
| scripts/break.py | scripts/test_spec_drift.py | #20, #22, #54 | tooling, dashboard |
| scripts/cap-output.py | scripts/test_cap_output.py | #61, #62, #63 | no |
| scripts/demo-data.py | scripts/test_demo_data.py | #66, #67, #68, #69 | no |
| scripts/evidence.py | scripts/seen-red.py | #26, #81, #94 | no |
| scripts/evidence.py | scripts/test_close_evidence.py | #32, #49, #87 | no |
| scripts/evidence.py | scripts/test_evidence.py | #26, #81, #82, #87, #88, #94 | no |
| scripts/evidence.py | scripts/test_seen_red.py | #26, #81, #94 | no |
| scripts/evidence.py | specs/README.md | #26, #32, #82, #87, #88, #94 | tooling, specs |
| scripts/seen-red.py | scripts/test_evidence.py | #26, #81, #94 | no |
| scripts/seen-red.py | scripts/test_seen_red.py | #26, #81, #94 | no |
| scripts/spec-drift.py | scripts/test_break.py | #20, #22, #26, #54 | dashboard, tooling |
| scripts/spec-drift.py | scripts/test_spec_drift.py | #2, #8, #9, #10, #11, #13, #15, #17, #20, #22, #26, #27, #29, #50, #54, #56, #58, #67, #81, #90, #92, #95 | no |
| scripts/spec-drift.py | scripts/test_track_red.py | #26, #54, #81 | dashboard, tooling |
| scripts/spec-drift.py | scripts/track-red.py | #26, #54, #81 | dashboard, tooling |
| scripts/spec-drift.py | specs/README.md | #14, #26, #90 | dashboard, specs |
| scripts/test_break.py | scripts/test_spec_drift.py | #20, #22, #26, #54 | tooling, dashboard |
| scripts/test_evidence.py | scripts/test_seen_red.py | #26, #81, #94 | no |
| scripts/test_evidence.py | specs/README.md | #26, #82, #87, #88, #94 | tooling, specs |
| scripts/test_spec_drift.py | scripts/test_track_red.py | #26, #54, #81 | dashboard, tooling |
| scripts/test_spec_drift.py | scripts/track-red.py | #26, #54, #81 | dashboard, tooling |
| scripts/test_token_usage.py | scripts/token-usage.py | #8, #26, #60, #65, #69, #72, #73, #74, #75, #76, #86 | no |
| scripts/test_track_red.py | scripts/track-red.py | #26, #43, #54, #81 | no |
| scripts/test_track_red.py | specs/README.md | #26, #31, #43 | tooling, specs |
| specs/README.md | specs/_short-template.md | #43, #85, #88 | no |
| specs/README.md | specs/_template.md | #23, #31, #40, #90 | no |

## Said vs done

- #2 outside-area: area dashboard | CHANGES.md, SOURCE.md
- #3 outside-area: area dashboard | CHANGES.md, SOURCE.md
- #4 outside-area: area dashboard | CHANGES.md, SOURCE.md
- #5 outside-area: area dashboard | .github/workflows/spec-drift-tests.yml, CHANGES.md, SOURCE.md
- #6 outside-area: area docs | CHANGES.md
- #7 outside-area: area tooling | CHANGES.md, SOURCE.md, kit/compare-page.py, kit/page/jobmatch-boxes.sha256, kit/page/jobmatch-data.json
- #8 outside-area: area dashboard | CHANGES.md, SOURCE.md, scripts/test_token_usage.py, scripts/token-usage.py
- #9 outside-area: area dashboard | CHANGES.md, SOURCE.md
- #10 outside-area: area dashboard | CHANGES.md, SOURCE.md, kit/compare-page.py, kit/page/jobmatch-boxes.sha256, templates/plan.template.md
- #11 outside-area: area dashboard | .github/workflows/spec-drift-tests.yml, CHANGES.md, SOURCE.md, spec-drift.config.json
- #12 outside-area: area dashboard | .github/workflows/pr-checks.yml, CHANGES.md, SOURCE.md, scripts/invariants.py, scripts/pr-names.py, scripts/test_invariants.py, scripts/test_pr_names.py, spec-drift.config.json
- #13 outside-area: area dashboard | CHANGES.md, SOURCE.md, kit/page/jobmatch-boxes.sha256, templates/plan.template.md
- #14 outside-area: area dashboard | .claude/agents/agentic-engineering-auditor.md, .claude/agents/architecture-auditor.md, .claude/agents/implementer.md, .claude/agents/security-ops-auditor.md, .claude/agents/spec-auditor.md, .gitattributes, .github/pull_request_template.md, .github/workflows/dashboard.yml, .github/workflows/pr-checks.yml, .github/workflows/spec-drift-tests.yml, CHANGES.md, SOURCE.md, docs/agent-workflow.png, docs/agent-workflow.svg, docs/workflow.md, scripts/test_invariants.py, specs/README.md, templates/CLAUDE.template.md
- #15 outside-area: area dashboard | README.md, docs/workflow.md, kit/CHANGES.md, kit/SOURCE.md, kit/examples/day-12-jwt-issuance.md, kit/examples/day-36-ecs-services.md, kit/jobmatch/CLAUDE.md, kit/jobmatch/audit-findings.md, kit/jobmatch/defects.md, kit/jobmatch/deployment.json, kit/jobmatch/lab-notebook.md, kit/jobmatch/live-checks.py, kit/jobmatch/plan.md, kit/jobmatch/token-usage.json, kit/lessons/attribution-rejected.md, kit/lessons/auditors-on-opus.md, kit/lessons/checks-before-push.md, kit/lessons/dev-loop-dropped.md, kit/lessons/implementer-on-haiku.md, kit/lessons/maintainer-review-style.md, kit/lessons/spec-auditor-eval.md, kit/lessons/spec-first-workflow.md, kit/lessons/spec-process-improvements.md
- #16 outside-area: area dashboard | CLAUDE.md, README.md, docs/lab-notebook.md, docs/workflow.md, kit/CHANGES.md, kit/SOURCE.md, plan.md, templates/spec.template.md
- #17 outside-area: area dashboard | .github/workflows/pr-checks.yml, kit/CHANGES.md, kit/SOURCE.md, scripts/pr-names.py, scripts/service-wiring.py, scripts/test_service_wiring.py
- #18 outside-area: area dashboard | .github/workflows/spec-drift-tests.yml, README.md, kit/CHANGES.md, kit/SOURCE.md, kit/starter-check.py
- #19 outside-area: area dashboard | kit/CHANGES.md, kit/SOURCE.md, kit/page/jobmatch-boxes.sha256, kit/starter-check.py
- #20 outside-area: area dashboard | kit/CHANGES.md, kit/SOURCE.md, scripts/break.py, scripts/test_break.py
- #21 outside-area: area dashboard | .claude/agents/defect-rater.md, .claude/agents/implementer.md, .gitattributes, CLAUDE.md, README.md, kit/CHANGES.md, kit/SOURCE.md, specs/README.md
- #22 outside-area: area dashboard | CLAUDE.md, README.md, kit/CHANGES.md, plan.md, scripts/break.py, scripts/test_break.py
- #23 outside-area: area dashboard | .claude/agents/implementer.md, .github/pull_request_template.md, CLAUDE.md, kit/CHANGES.md, specs/README.md, specs/_template.md
- #24 outside-area: area dashboard | .github/workflows/pr-checks.yml, README.md, kit/CHANGES.md, scripts/test_pr_names.py
- #25 outside-area: area dashboard | kit/CHANGES.md, kit/page/jobmatch-boxes.sha256
- #26 outside-area: area tooling | .gitignore, CLAUDE.md, README.md, docs/dashboard/dashboard.css, docs/dashboard/dashboard.js, docs/dashboard/index.html, docs/workflow.md, kit/CHANGES.md, kit/SOURCE.md, kit/page/jobmatch-boxes.sha256, kit/starter-check.py, kit/v2-manifest.md, specs/README.md
- #27 outside-area: area tooling | docs/dashboard/dashboard.css, docs/dashboard/dashboard.js, kit/CHANGES.md, kit/page/jobmatch-boxes.sha256
- #28 outside-area: area tooling | kit/CHANGES.md
- #29 outside-area: area tooling | kit/CHANGES.md
- #30 outside-area: area tooling | kit/CHANGES.md
- #31 outside-area: area tooling | CLAUDE.md, README.md, kit/ASSESSMENT.md, kit/CHANGES.md, specs/README.md, specs/_template.md
- #32 outside-area: area tooling | CLAUDE.md, README.md, kit/CHANGES.md, specs/README.md
- #33 outside-area: area tooling | README.md, kit/CHANGES.md, specs/README.md
- #34 outside-area: area tooling | kit/ASSESSMENT.md, kit/CHANGES.md, kit/replay/README.md, kit/replay/manifest.json, kit/replay/replay-set.py
- #35 outside-area: area tooling | kit/CHANGES.md, kit/replay/keys/dev-day10-post-fix.json, kit/replay/keys/dev-day15-proxy-passes.json, kit/replay/keys/dev-day16-post-fix.json, kit/replay/keys/dev-day21-harness-routing.json, kit/replay/keys/dev-day24-network-checks.json, kit/replay/keys/dev-day27-consumer-isolation.json, kit/replay/keys/dev-day28-review-ownership.json, kit/replay/keys/dev-day38-actuator-masked.json, kit/replay/manifest.json
- #36 outside-area: area tooling | kit/CHANGES.md, kit/replay/manifest.json
- #37 outside-area: area tooling | kit/ASSESSMENT.md, kit/CHANGES.md, kit/replay/README.md, kit/replay/manifest.json, kit/replay/results.md
- #38 outside-area: area tooling | kit/ASSESSMENT.md, kit/CHANGES.md
- #39 outside-area: area tooling | README.md, kit/replay/README.md
- #40 outside-area: area tooling | CLAUDE.md, kit/CHANGES.md, specs/README.md, specs/_template.md
- #41 outside-area: area tooling | kit/CHANGES.md
- #42 outside-area: area tooling | CLAUDE.md, kit/CHANGES.md
- #43 outside-area: area tooling | CLAUDE.md, kit/CHANGES.md, specs/README.md, specs/_short-template.md
- #44 outside-area: area tooling | kit/CHANGES.md, specs/README.md
- #45 outside-area: area tooling | CLAUDE.md
- #47 outside-area: area tooling | CLAUDE.md
- #48 outside-area: area tooling | README.md
- #49 outside-area: area tooling | CLAUDE.md
- #54 outside-area: area tooling | AGENTS.md, CLAUDE.md, README.md
- #56 outside-area: area dashboard | scripts/behaviour-index.py
- #57 outside-area: area dashboard | kit/page/jobmatch-boxes.sha256
- #59 outside-area: area tooling | CLAUDE.md
- #60 outside-area: area tooling | CLAUDE.md
- #61 outside-area: area tooling | .gitignore, CLAUDE.md
- #62 outside-area: area tooling | CLAUDE.md
- #63 outside-area: area tooling | CLAUDE.md
- #64 outside-area: area tooling | CLAUDE.md
- #67 outside-area: area dashboard | CLAUDE.md, kit/page/jobmatch-boxes.sha256, scripts/demo-data.py, scripts/test_demo_data.py
- #68 outside-area: area dashboard | scripts/demo-data.py, scripts/test_demo_data.py
- #70 outside-area: area dashboard | kit/page/jobmatch-boxes.sha256, scripts/test_demo_data.py
- #72 outside-area: area tooling | docs/dashboard/token-usage.json
- #73 outside-area: area tooling | docs/dashboard/dashboard.js, docs/dashboard/token-usage.json
- #81 outside-area: area tooling | kit/CHANGES.md
- #82 outside-area: area tooling | README.md, kit/CHANGES.md, specs/README.md
- #83 outside-area: area tooling | .flake8, CLAUDE.md, README.md, kit/CHANGES.md, kit/examples/day-12-jwt-issuance.md, specs/README.md
- #85 outside-area: area specs | CLAUDE.md, docs/architecture.md
- #87 outside-area: area tooling | specs/README.md
- #88 outside-area: area tooling | docs/dashboard/dashboard.js, specs/README.md, specs/_short-template.md
- #89 outside-area: area specs | .claude/agents/spec-auditor.md, .github/pull_request_template.md
- #90 outside-area: area tooling | docs/dashboard/dashboard.js, docs/dashboard/index.html, specs/README.md, specs/_template.md
- #91 outside-area: area docs | specs/_template.md
- #93 outside-area: area tooling | .gitignore, CLAUDE.md
- #94 outside-area: area tooling | CLAUDE.md, README.md, docs/architecture.md, spec-drift.config.json, specs/README.md
