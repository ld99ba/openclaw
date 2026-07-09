# V1.1 Phase 13 Root Policy Shadow Disposition

Status: PASS
Policy shadows: 6
Excluded pathspecs: 6
Blocking issues: 0
Warnings: 6
Package policy: `openclaw/policies/policy.json`
Package policy version: `OGK-Final-1.0`
Recommended next action: `owner_adr_required_before_stage_migrate_or_delete`
Git staging executed: `False`
Destructive action taken: `False`

## Disposition

| Path | Policy | Version Match | Disposition | Warnings |
|---|---|---|---|---|
| `policies/cron_governance_policy.yaml` | cron_governance_policy | True | exclude_from_v1_1_manifest_pending_owner_adr | policy_is_safety_relevant_do_not_drop_without_owner_review |
| `policies/final_seal_policy.yaml` | final_seal_policy | True | exclude_from_v1_1_manifest_pending_owner_adr | policy_is_safety_relevant_do_not_drop_without_owner_review |
| `policies/memory_skill_policy.yaml` | memory_skill_policy | True | exclude_from_v1_1_manifest_pending_owner_adr | policy_is_safety_relevant_do_not_drop_without_owner_review |
| `policies/migration_policy.yaml` | migration_policy | True | exclude_from_v1_1_manifest_pending_owner_adr | policy_is_safety_relevant_do_not_drop_without_owner_review |
| `policies/repair_policy.yaml` | repair_policy | True | exclude_from_v1_1_manifest_pending_owner_adr | policy_is_safety_relevant_do_not_drop_without_owner_review |
| `policies/tool_permission_policy.yaml` | tool_permission_policy | True | exclude_from_v1_1_manifest_pending_owner_adr | policy_is_safety_relevant_do_not_drop_without_owner_review |

## Excluded Pathspec

| Path |
|---|
| `policies/cron_governance_policy.yaml` |
| `policies/final_seal_policy.yaml` |
| `policies/memory_skill_policy.yaml` |
| `policies/migration_policy.yaml` |
| `policies/repair_policy.yaml` |
| `policies/tool_permission_policy.yaml` |
