# V1.1 Phase 06 Gitignore Hygiene

Status: PASS
Required patterns: 18
Missing required patterns: 0
Forbidden patterns present: 0
Destructive action taken: `False`

## Ignored Samples

| Path | Ignored |
|---|---|
| `__pycache__/module.cpython-312.pyc` | `True` |
| `pkg/__pycache__/module.cpython-312.pyc` | `True` |
| `.pytest_cache/v/cache/nodeids` | `True` |
| `node_modules/pkg/index.js` | `True` |
| `.pw-browsers/chromium/cache.txt` | `True` |
| `.clawhub/lock.json` | `True` |
| `.forge/candidates.jsonl` | `True` |
| `.locks/runtime.lock` | `True` |
| `.openclaw-locks/runtime.lock` | `True` |
| `.openclaw/local-state.json` | `True` |
| `.mx-claw-workspace/session.json` | `True` |
| `.learnings/index.json` | `True` |
| `reports/.archive/old-evidence.json` | `True` |
| `reports/.backup/old-evidence.json` | `True` |
| `reports/.locks/report.lock` | `True` |
| `reports/.rollback/rollback.json` | `True` |
| `reports/.hermes-example.lock` | `True` |
| `.hermes-auto.lock.stale-20260624-132341` | `True` |

## Protected Samples

| Path | Ignored |
|---|---|
| `docs/plans/2026-07-09-ogk-final-v1-1-phase-06-implementation-plan.md` | `False` |
| `openclaw/governance/supervisor.py` | `False` |
| `reports/final/current_state.json` | `False` |
| `reports/v1_1/phase_06/PHASE_06_SUMMARY.md` | `False` |
| `tests/v1_1/test_gitignore_hygiene.py` | `False` |
| `tools/verify_v1_1_gitignore_hygiene.py` | `False` |
