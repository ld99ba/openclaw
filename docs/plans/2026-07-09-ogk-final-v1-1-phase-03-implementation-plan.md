# OGK-Final V1.1 Phase 03 Implementation Plan

Date: 2026-07-09
Scope: workspace boundary governance, untracked file classification, and release manifest dry-run.

## Guardrails

- Do not delete, move, archive, stage, commit, push, or tag files.
- Do not modify V1.0 final reports, event ledger, artifact registry, or release tag.
- Treat `main/` as a boundary decision, not as an automatic inclusion target.
- Produce reports first; require human approval before cleanup or release actions.

## Work Items

1. Workspace inventory
   - Enumerate untracked files using Git porcelain plumbing.
   - Classify candidates into V1.1 release files, V1.0 baseline preserve, generated cache, historical reports, nested repo boundary, and unknown.

2. `main/` nested repository governance
   - Detect whether `main/` has its own `.git` directory or file.
   - Report recommended handling without changing it.

3. Manifest-driven release dry-run
   - Build a deterministic V1.1 candidate manifest.
   - Verify all required Phase 01-03 files exist.
   - Verify V1.0 final artifacts are excluded.
   - Write JSON and Markdown reports for review.

## Acceptance

- Workspace inventory report exists.
- Manifest dry-run report exists and passes.
- `tests/v1_1` passes.
- V1.0 acceptance guard still passes.
