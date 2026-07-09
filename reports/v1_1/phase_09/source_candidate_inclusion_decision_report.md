# V1.1 Phase 09 Source Candidate Inclusion Decision

Status: PASS
Source candidates: 16
Next-stage pathspec candidates: 10
Deferred candidates: 6
Explicit approval required before stage: `True`
Git staging executed: `False`
Destructive action taken: `False`

## Decision Counts

| Decision | Count |
|---|---:|
| defer_root_policy_shadow_duplicate | 6 |
| include_entrypoint_after_behavior_review | 1 |
| include_package_marker_after_approval | 7 |
| include_runtime_config_after_owner_review | 2 |

## Next-Stage Pathspec

| Path |
|---|
| `openclaw/__init__.py` |
| `openclaw/evidence/__init__.py` |
| `openclaw/execution/__init__.py` |
| `openclaw/governance/__init__.py` |
| `openclaw/governance/project_spec.json` |
| `openclaw/hermes_adapter/__init__.py` |
| `openclaw/hermes_adapter/__main__.py` |
| `openclaw/intelligence/__init__.py` |
| `openclaw/policies/policy.json` |
| `openclaw/recovery/__init__.py` |

## Deferred Pathspec

| Path | Reason |
|---|---|
| `policies/cron_governance_policy.yaml` | Root policy shadow matches the tracked package policy counterpart. |
| `policies/final_seal_policy.yaml` | Root policy shadow matches the tracked package policy counterpart. |
| `policies/memory_skill_policy.yaml` | Root policy shadow matches the tracked package policy counterpart. |
| `policies/migration_policy.yaml` | Root policy shadow matches the tracked package policy counterpart. |
| `policies/repair_policy.yaml` | Root policy shadow matches the tracked package policy counterpart. |
| `policies/tool_permission_policy.yaml` | Root policy shadow matches the tracked package policy counterpart. |

## Candidate Decisions

| Path | Kind | Decision | Next Action |
|---|---|---|---|
| `openclaw/__init__.py` | package_marker | include_package_marker_after_approval | Stage only after explicit approval for source candidate inclusion. |
| `openclaw/evidence/__init__.py` | package_marker | include_package_marker_after_approval | Stage only after explicit approval for source candidate inclusion. |
| `openclaw/execution/__init__.py` | package_marker | include_package_marker_after_approval | Stage only after explicit approval for source candidate inclusion. |
| `openclaw/governance/__init__.py` | package_marker | include_package_marker_after_approval | Stage only after explicit approval for source candidate inclusion. |
| `openclaw/governance/project_spec.json` | runtime_json_config | include_runtime_config_after_owner_review | Stage only after explicit approval for source candidate inclusion. |
| `openclaw/hermes_adapter/__init__.py` | package_marker | include_package_marker_after_approval | Stage only after explicit approval for source candidate inclusion. |
| `openclaw/hermes_adapter/__main__.py` | package_entrypoint | include_entrypoint_after_behavior_review | Stage only after explicit approval for source candidate inclusion. |
| `openclaw/intelligence/__init__.py` | package_marker | include_package_marker_after_approval | Stage only after explicit approval for source candidate inclusion. |
| `openclaw/policies/policy.json` | package_policy_config | include_runtime_config_after_owner_review | Stage only after explicit approval for source candidate inclusion. |
| `openclaw/recovery/__init__.py` | package_marker | include_package_marker_after_approval | Stage only after explicit approval for source candidate inclusion. |
| `policies/cron_governance_policy.yaml` | root_policy_shadow | defer_root_policy_shadow_duplicate | Keep unstaged unless an ADR approves root-level policy ownership. |
| `policies/final_seal_policy.yaml` | root_policy_shadow | defer_root_policy_shadow_duplicate | Keep unstaged unless an ADR approves root-level policy ownership. |
| `policies/memory_skill_policy.yaml` | root_policy_shadow | defer_root_policy_shadow_duplicate | Keep unstaged unless an ADR approves root-level policy ownership. |
| `policies/migration_policy.yaml` | root_policy_shadow | defer_root_policy_shadow_duplicate | Keep unstaged unless an ADR approves root-level policy ownership. |
| `policies/repair_policy.yaml` | root_policy_shadow | defer_root_policy_shadow_duplicate | Keep unstaged unless an ADR approves root-level policy ownership. |
| `policies/tool_permission_policy.yaml` | root_policy_shadow | defer_root_policy_shadow_duplicate | Keep unstaged unless an ADR approves root-level policy ownership. |
