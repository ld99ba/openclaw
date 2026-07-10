# OGK-Final V1.1 Phase 02 Implementation Plan

Date: 2026-07-09
Scope: interruption recovery, Hermes behavior matrix, and Memory/Skill lifecycle hardening.

## Guardrails

- Do not modify `ogk-final-v1.0`.
- Do not rewrite V1.0 release history or final reports.
- Do not stage, commit, push, tag, or publish without explicit approval.
- Keep all executable evidence under `tests/v1_1`, `tools`, and `reports/v1_1/phase_02`.
- Prefer narrow contract helpers over broad runtime rewrites.

## Work Items

1. Recovery hardening
   - Add executable tests for error classification, repair authorization levels, and resume replay from fixture ledgers.
   - Verify R0-R2 automatic repair is bounded.
   - Verify secrets, destructive actions, external side effects, and core runtime mutations require human authorization.

2. Hermes behavior equivalence hardening
   - Convert the existing behavior audit constants into a machine-readable matrix.
   - Add a verifier that writes JSON and Markdown evidence.
   - Test required outcomes: enhanced, equivalent-or-safer, baseline, and no runtime copy.

3. Memory/Skill lifecycle hardening
   - Add lifecycle validation APIs with explicit missing-rule diagnostics.
   - Test valid and invalid records for source, purpose, expiry, audit, promotion gate, rollback, and workshop requirements.

4. Phase 02 summary
   - Produce `reports/v1_1/phase_02/PHASE_02_SUMMARY.md`.
   - Run the V1.1 pytest suite and the V1.0 acceptance guard.

## Acceptance

- `tests/v1_1` passes.
- V1.0 acceptance guard still passes.
- Phase 02 reports exist and explain pass/fail status.
- No V1.0 final artifacts are modified.
