# OpenClaw Release Handoff Index

Purpose: external reviewer reading order for the post-acceptance OGK-Final release package.

## Recommended Reading Order

1. `docs/OPENCLAW_GOVERNANCE_KERNEL_FINAL.md` — canonical OGK-Final governance design and completion scope.
2. `reports/final/OPENCLAW_RELEASE_POST_ACCEPTANCE_REVIEW.md` — post-release scope determination and final seal recommendation.
3. `reports/final/OPENCLAW_FINAL_ACCEPTANCE_REPORT.md` — final acceptance basis and seven-phase acceptance summary.
4. `reports/final/OPENCLAW_FINAL_AUDIT_REPORT.md` — audit evidence checked and release audit conclusions.
5. `reports/final/openclaw_final_seal_result.json` — machine-readable FinalSeal result.
6. `reports/final/current_state.json` — machine-readable final project state.
7. `reports/final/issue_register.json` — issue register confirming no open BLOCKER/HIGH issues.
8. `reports/events/openclaw-governance-events.jsonl` — authoritative event ledger.
9. `reports/final/OPENCLAW_RELEASE_ARTIFACT_INDEX.md` — release artifact hash/size index.
10. `reports/final/OPENCLAW_FINAL_PROGRESS_SUMMARY.md` — concise completion summary.
11. `reports/final/OPENCLAW_HERMES_SUPERIORITY_PROOF.md` — proof of stronger-than-Hermes governance properties.

## Architecture and Audit Supplements

- `docs/OPENCLAW_HERMES_FUSION_FINAL_ARCHITECTURE.md` — final OpenClaw/Hermes fusion architecture boundary.
- `docs/OPENCLAW_FINAL_SEAL_PROTOCOL.md` — rule that `FINAL_SUCCESS` must be derived, not hand-written.
- `docs/OPENCLAW_SUPERVISOR_RUNTIME.md` — supervisor, ToolGateway, PolicyEngine, and Evidence Plane runtime model.
- `docs/OPENCLAW_HERMES_COVERAGE_AUDIT.md` — required Hermes capability coverage scope.
- `reports/hermes_capability_coverage_matrix.json` — 14/14 Hermes capability group registration matrix.
- `reports/hermes_behavior_equivalence_audit.md` — behavior equivalence / safer-than-Hermes audit.
- `reports/hermes_gap_audit.md` — partial/reference-only/do-not-copy gap register.
- `reports/hermes_source_inventory.json` — Hermes source inventory evidence.

## Phase Evidence

- `reports/quality_gates/phase_01_quality_gate.json`
- `reports/quality_gates/phase_02_quality_gate.json`
- `reports/quality_gates/phase_03_quality_gate.json`
- `reports/quality_gates/phase_04_quality_gate.json`
- `reports/quality_gates/phase_05_quality_gate.json`
- `reports/quality_gates/phase_06_quality_gate.json`
- `reports/quality_gates/phase_07_quality_gate.json`
- `reports/audits/phase_01_audit.md`
- `reports/audits/phase_02_audit.md`
- `reports/audits/phase_03_audit.md`
- `reports/audits/phase_04_audit.md`
- `reports/audits/phase_05_audit.md`
- `reports/audits/phase_06_audit.md`
- `reports/audits/phase_07_audit.md`
- `reports/artifacts/phase_01_artifact_index.json`
- `reports/artifacts/phase_02_artifact_index.json`
- `reports/artifacts/phase_03_artifact_index.json`
- `reports/artifacts/phase_04_artifact_index.json`
- `reports/artifacts/phase_05_artifact_index.json`
- `reports/artifacts/phase_06_artifact_index.json`
- `reports/artifacts/phase_07_artifact_index.json`

## Reviewer Verification Commands

```bash
python3 tools/test_ogk_final_acceptance.py
```

Expected output:

```text
OGK_FINAL_ACCEPTANCE_TEST_PASS
```

Optional direct verification:

```bash
python3 - <<'PY'
from openclaw.evidence.event_ledger import EventLedger
from openclaw.evidence.artifact_registry import ArtifactRegistry
from openclaw.evidence.replay_engine import ReplayEngine
print(EventLedger('reports/events/openclaw-governance-events.jsonl').verify())
print(ArtifactRegistry('reports/final/artifact_registry.json').verify())
print(ReplayEngine('reports/events/openclaw-governance-events.jsonl', 'reports/final/artifact_registry.json').rebuild_state())
PY
```

Expected core results:

- Event ledger: `ok: True`
- Artifact registry: `ok: True`, no missing/mismatched artifacts
- Replay: seven accepted phases, `FINAL_SUCCESS`, `RELEASE_ACCEPTED`
