# V1.1 Phase 05 Workspace Hygiene Proposal

Status: PASS
Untracked paths: 20366
Gitignore updated: `False`
Destructive action taken: `False`
`main/` status: `nested_git_repository`

## Category Counts

| Category | Count | Sample |
|---|---:|---|
| generated_cache | 383 | memory/xiaolongxia/code_proposals/proposal_0f7bd4d2fa89/__pycache__/frontier_capabilities.cpython-312.pyc, memory/xiaolongxia/code_proposals/proposal_0f7bd4d2fa89/__pycache__/test_frontier_capabilities.cpython-312.pyc, memory/xiaolongxia/code_proposals/proposal_14b2d4fcd181/__pycache__/frontier_capabilities.cpython-312.pyc, memory/xiaolongxia/code_proposals/proposal_4e75b1425762/__pycache__/frontier_capabilities.cpython-312.pyc, node_modules/.vite/vitest/da39a3ee5e6b4b0d3255bfef95601890afd80709/results.json |
| historical_report_or_runtime_evidence | 9925 | reports/.archive/hermes-empty-report-artifact/reports/hermes-archive-protection-execute-next-backlog-validate-2026-06-24-195500.stderr.log, reports/.archive/hermes-empty-report-artifact/reports/hermes-artifact-index-cleanup-protection-next-backlog-2026-06-24-220722.stderr.log, reports/.archive/hermes-empty-report-artifact/reports/hermes-artifact-index-cleanup-protection-next-backlog-2026-06-24-221151.stderr.log, reports/.archive/hermes-empty-report-artifact/reports/hermes-artifact-index-cleanup-protection-pycompile-2026-06-24-220722.log, reports/.archive/hermes-empty-report-artifact/reports/hermes-artifact-index-cleanup-protection-pycompile-2026-06-24-221151.log |
| local_control_or_hidden_state | 796 | .clawhub/lock.json, .forge/candidates.jsonl, .forge/captures.jsonl, .forge/filtered-candidates.jsonl, .forge/notifications.jsonl |
| unknown_review_required | 9246 | 03_tasks/HERMES_AUTO_PROGRESS_MASTER_PLAN.md, 03_tasks/hermes_auto_progress_status.json, 10_release/HERMES_FINAL_ACCEPTANCE_REPORT.md, 10_release/HERMES_FINAL_AUDIT_REPORT.md, 10_release/HERMES_FINAL_PROGRESS_SUMMARY.md |
| v1_0_baseline_preserve | 9 | reports/final/OGK_FINAL_HANDOFF_DOC_GENERATION_LOG.md, reports/final/OGK_FINAL_V1_0_PROJECT_HANDOFF_FOR_CHATGPT.md, reports/final/OGK_FINAL_V1_0_UPLOAD_PACKAGE_INDEX.md, reports/final/OGK_FINAL_V1_1_STARTING_POINT.md, reports/final/OPENCLAW_GIT_RELEASE_SUMMARY.md |
| v1_1_release_candidate | 7 | docs/plans/2026-07-09-ogk-final-v1-1-phase-05-implementation-plan.md, reports/v1_1/phase_01/.gitkeep, reports/v1_1/phase_05/PHASE_05_SUMMARY.md, reports/v1_1/phase_05/workspace_hygiene_proposal_report.md, reports/v1_1/phase_05/workspace_hygiene_proposal_result.json |

## Safe Gitignore Additions

- `__pycache__/`
- `*.py[cod]`
- `.pytest_cache/`
- `node_modules/`
- `.pw-browsers/`
- `.clawhub/`
- `.forge/`
- `.locks/`
- `.openclaw-locks/`
- `.openclaw/`
- `.mx-claw-workspace/`
- `.learnings/`
- `reports/.archive/`
- `reports/.backup/`
- `reports/.locks/`
- `reports/.rollback/`
- `reports/.hermes-*.lock*`
- `.hermes-*.lock*`

## Archive Plan

- `generated_cache`: ignore and regenerate on demand (approval required before move/delete: `False`)
- `local_control_or_hidden_state`: ignore runtime-local state; preserve on disk (approval required before move/delete: `True`)
- `historical_report_or_runtime_evidence`: keep out of V1.1 manifests; archive only after dedicated evidence review (approval required before move/delete: `True`)
- `unknown_review_required`: do not ignore or archive automatically; require owner review (approval required before move/delete: `True`)
- `v1_0_baseline_preserve`: preserve as baseline evidence; do not ignore broadly (approval required before move/delete: `True`)
