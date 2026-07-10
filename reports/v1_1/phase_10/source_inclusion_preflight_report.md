# V1.1 Phase 10 Source Inclusion Preflight

Status: PASS
Candidates: 10
Blocking issues: 0
Warnings: 3
Explicit approval required before stage: `True`
Git staging executed: `False`
Destructive action taken: `False`

## Candidate Preflight

| Path | Blocking Issues | Warnings |
|---|---|---|
| `openclaw/__init__.py` |  |  |
| `openclaw/evidence/__init__.py` |  |  |
| `openclaw/execution/__init__.py` |  |  |
| `openclaw/governance/__init__.py` |  |  |
| `openclaw/governance/project_spec.json` |  | project_spec_version_requires_owner_confirmation |
| `openclaw/hermes_adapter/__init__.py` |  |  |
| `openclaw/hermes_adapter/__main__.py` |  | entrypoint_has_top_level_print_call |
| `openclaw/intelligence/__init__.py` |  |  |
| `openclaw/policies/policy.json` |  | runtime_policy_config_requires_owner_confirmation |
| `openclaw/recovery/__init__.py` |  |  |
