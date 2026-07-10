# V1.1 Phase 07 Untracked Review Queue

Status: PASS
Untracked paths: 19155
Review queue paths: 19153
V1.1 release candidates excluded: 2
Source candidates: 6
Manual review required: `True`
Git staging executed: `False`
Destructive action taken: `False`

## Review Buckets

| Bucket | Count | Recommendation | Sample |
|---|---:|---|---|
| baseline_evidence_preserve | 9 | preserve as V1.0 baseline evidence; do not include in V1.1 hardening manifests automatically | reports/final/OGK_FINAL_HANDOFF_DOC_GENERATION_LOG.md, reports/final/OGK_FINAL_V1_0_PROJECT_HANDOFF_FOR_CHATGPT.md, reports/final/OGK_FINAL_V1_0_UPLOAD_PACKAGE_INDEX.md, reports/final/OGK_FINAL_V1_1_STARTING_POINT.md, reports/final/OPENCLAW_GIT_RELEASE_SUMMARY.md |
| external_research_or_dependency_surface | 985 | review ownership, license, and provenance before any inclusion | ai_frontier/2025-05-25.md, backups/reboot-checks/l10-master-state.before-reboot-20260601-164310.json, backups/reboot-checks/l10-master-state.before-reboot-request-20260601-151448.json, evolution_system/README.md, evolution_system/evolution_logs/001-initial-setup.md |
| historical_release_or_planning_material | 26 | review as historical handoff material, not as code | 03_tasks/HERMES_AUTO_PROGRESS_MASTER_PLAN.md, 03_tasks/hermes_auto_progress_status.json, 10_release/HERMES_FINAL_ACCEPTANCE_REPORT.md, 10_release/HERMES_FINAL_AUDIT_REPORT.md, 10_release/HERMES_FINAL_PROGRESS_SUMMARY.md |
| historical_runtime_evidence | 9830 | keep out of release manifests unless a later evidence review selects specific files | reports/audits/resume_audit.md, reports/claude-code-evolution-plan.md, reports/deep-dives/README.md, reports/deep-dives/deepdive_agents_2412.md, reports/deep-dives/deepdive_agents_2505_07078.md |
| local_control_state | 42 | preserve locally or ignore with a narrow rule; do not publish | reports/.hermes-current-owner-token, research/hermes/hermes-agent/.dockerignore, research/hermes/hermes-agent/.env.example, research/hermes/hermes-agent/.envrc, research/hermes/hermes-agent/.gitattributes |
| local_knowledge_or_memory_state | 1328 | preserve locally; do not publish without privacy review | daily-review/2026-05-20.md, daily-review/2026-05-22.md, daily-review/2026-05-23.md, daily-review/2026-05-24.md, daily-review/README.md |
| media_or_binary_artifact | 51 | review purpose and size before any inclusion | quant_screenshot_1.png, quant_screenshot_2.png, research/hermes/hermes-agent/apps/bootstrap-installer/src-tauri/icons/128x128.png, research/hermes/hermes-agent/apps/bootstrap-installer/src-tauri/icons/128x128@2x.png, research/hermes/hermes-agent/apps/bootstrap-installer/src-tauri/icons/32x32.png |
| root_misc_review | 6876 | requires owner review before staging | 120B, 3.2K, 677B, deploy_xlx_system_final_viz.py, research/hermes/hermes-agent/AGENTS.md |
| source_surface_candidate | 6 | review for a dedicated source inclusion ADR before staging | policies/cron_governance_policy.yaml, policies/final_seal_policy.yaml, policies/memory_skill_policy.yaml, policies/migration_policy.yaml, policies/repair_policy.yaml |

## Top-Level Candidates

- `03_tasks`
- `10_release`
- `11_logs`
- `120B`
- `3.2K`
- `677B`
- `ai_frontier`
- `backups`
- `daily-review`
- `deploy_xlx_system_final_viz.py`
- `docs`
- `evolution_system`
- `external`
- `feedback`
- `memory`
- `memory_db`
- `papers`
- `plugins`
- `policies`
- `quant_screenshot_1.png`
- `quant_screenshot_2.png`
- `reports`
- `research`
- `schemas`
- `scripts`
- `self_model`
- `skills`
- `storage`
- `test`
- `tests`
- `tmp`
- `tools`
- `value_system`
- `workflow_archive`
- `workspace`
- `xiaolongxia_system`
- `大规模网络深度学习报告.md`
- `投资知识图谱.md`
- `投资认知框架.md`
- `深度学习终期报告.md`
- `生成syscall描述`
- `网络深度学习最终报告.md`
- `网络金融知识深度学习报告.md`

## Source Candidate Samples

- `policies/cron_governance_policy.yaml`
- `policies/final_seal_policy.yaml`
- `policies/memory_skill_policy.yaml`
- `policies/migration_policy.yaml`
- `policies/repair_policy.yaml`
- `policies/tool_permission_policy.yaml`
