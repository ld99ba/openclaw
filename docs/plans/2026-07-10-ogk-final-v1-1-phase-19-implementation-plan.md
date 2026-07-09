# OGK Final V1.1 Phase 19 Implementation Plan

## Scope

Record a post-publication audit for the published `ogk-final-v1.1-hardening` GitHub release.

## Steps

1. Add a post-publication audit verifier.
2. Confirm the GitHub release exists and is neither draft nor prerelease.
3. Confirm the `ogk-final-v1.1-hardening` tag points at the hardening branch release head.
4. Confirm the existing `ogk-final-v1.1` tag remains unchanged.
5. Record that no pull request was created and that the original V1.1 tag was not moved.
6. Add tests for the passing case, missing release, annotated tag dereference, and old-tag drift.
7. Re-run V1.1 verification and manifest dry-run.

## Safety

- No release mutation.
- No tag movement.
- No pull request creation.
- No destructive filesystem action.
- Root-level `policies/` shadows remain excluded.
