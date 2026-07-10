# OGK Final V1.1 Phase 13 Implementation Plan

Date: 2026-07-09

## Objective

Record a non-destructive disposition for the remaining root-level `policies/` source candidates after Phase 12 source inclusion.

## Scope

- Inspect the six root-level policy YAML shadows.
- Compare their version marker with `openclaw/policies/policy.json`.
- Keep them excluded from the V1.1 manifest pending owner ADR.
- Do not stage, move, or delete the root-level policy files.

## Verification

- Add a focused unit test for the disposition builder.
- Regenerate Phase 13 evidence.
- Refresh the V1.1 manifest dry run.
- Run the V1.1 test suite and final acceptance guards.
