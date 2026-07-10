# V1.1 Phase 08 Source Candidate Assessment

Status: PASS
Source candidates: 16
Duplicate policy shadows: 6
Duplicate policy hash matches: 6
Manual review required: `True`
Git staging executed: `False`
Destructive action taken: `False`

## Kind Counts

| Kind | Count |
|---|---:|
| package_entrypoint | 1 |
| package_marker | 7 |
| package_policy_config | 1 |
| root_policy_shadow | 6 |
| runtime_json_config | 1 |

## Candidate Assessment

| Path | Kind | Bytes | Duplicate | Recommendation |
|---|---|---:|---|---|
| `openclaw/__init__.py` | package_marker | 42 |  | eligible for package completeness review; explicit approval required before staging |
| `openclaw/evidence/__init__.py` | package_marker | 26 |  | eligible for package completeness review; explicit approval required before staging |
| `openclaw/execution/__init__.py` | package_marker | 27 |  | eligible for package completeness review; explicit approval required before staging |
| `openclaw/governance/__init__.py` | package_marker | 28 |  | eligible for package completeness review; explicit approval required before staging |
| `openclaw/governance/project_spec.json` | runtime_json_config | 362 |  | review runtime policy/config ownership before inclusion; explicit approval required before staging |
| `openclaw/hermes_adapter/__init__.py` | package_marker | 32 |  | eligible for package completeness review; explicit approval required before staging |
| `openclaw/hermes_adapter/__main__.py` | package_entrypoint | 71 |  | review CLI behavior before inclusion; explicit approval required before staging |
| `openclaw/intelligence/__init__.py` | package_marker | 30 |  | eligible for package completeness review; explicit approval required before staging |
| `openclaw/policies/policy.json` | package_policy_config | 424 |  | review runtime policy/config ownership before inclusion; explicit approval required before staging |
| `openclaw/recovery/__init__.py` | package_marker | 26 |  | eligible for package completeness review; explicit approval required before staging |
| `policies/cron_governance_policy.yaml` | root_policy_shadow | 152 | openclaw/policies/cron_governance_policy.yaml hash_match=True | prefer tracked package policy counterpart; do not stage root shadow without ADR |
| `policies/final_seal_policy.yaml` | root_policy_shadow | 147 | openclaw/policies/final_seal_policy.yaml hash_match=True | prefer tracked package policy counterpart; do not stage root shadow without ADR |
| `policies/memory_skill_policy.yaml` | root_policy_shadow | 149 | openclaw/policies/memory_skill_policy.yaml hash_match=True | prefer tracked package policy counterpart; do not stage root shadow without ADR |
| `policies/migration_policy.yaml` | root_policy_shadow | 146 | openclaw/policies/migration_policy.yaml hash_match=True | prefer tracked package policy counterpart; do not stage root shadow without ADR |
| `policies/repair_policy.yaml` | root_policy_shadow | 143 | openclaw/policies/repair_policy.yaml hash_match=True | prefer tracked package policy counterpart; do not stage root shadow without ADR |
| `policies/tool_permission_policy.yaml` | root_policy_shadow | 152 | openclaw/policies/tool_permission_policy.yaml hash_match=True | prefer tracked package policy counterpart; do not stage root shadow without ADR |
