# OGK-Final V1.1 Phase 04 Implementation Plan

Status: Implemented
Date: 2026-07-09

## Scope

Phase 04 closes the V1.1 hardening release with post-release governance evidence that was intentionally not backfilled into V1.0:

1. Supervisor deterministic stability harness.
2. Nested `main/` repository governance ADR and safety check.
3. V1.1 final acceptance verifier derived from evidence and release metadata.

## Outputs

- `tools/verify_supervisor_stability.py`
- `tools/verify_main_governance_boundary.py`
- `tools/verify_v1_1_final_acceptance.py`
- `tests/v1_1/test_supervisor_stability.py`
- `tests/v1_1/test_main_governance_boundary.py`
- `tests/v1_1/test_v1_1_final_acceptance.py`
- `reports/v1_1/phase_04/*`

## Verification

- The Supervisor harness must simulate progress, heartbeats, stuck-state detection, repeated-failure detection, and invalid-transition detection without external services.
- The `main/` governance verifier must keep nested repository paths out of release manifests unless a later ADR explicitly changes the decision.
- The final acceptance verifier must fail closed when evidence is missing and derive `FINAL_SUCCESS` only from passing evidence plus release metadata.
