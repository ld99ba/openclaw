# ADR-004: Nested main Repository Boundary

Status: Accepted for V1.1
Date: 2026-07-09

## Context

`main/` is a nested Git repository inside the top-level OGK release workspace. Blindly staging it would blur release ownership and can accidentally import an unrelated repository history into the OGK release line.

## Decision

Continue excluding `main/` from OGK-Final V1.1 release manifests and staging operations.

## Consequences

- V1.1 release evidence stays scoped to the top-level OGK hardening line.
- `main/` can be handled later as a submodule, archive, migration, or separate release line.
- Any future inclusion requires a dedicated ADR and explicit approval.

## Verification

- Boundary status: `nested_git_repository`
- Manifest includes main paths: `False`
- Recommended decision: `continue_excluding_main`
