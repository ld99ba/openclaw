# OGK Final V1.1 Phase 20 Implementation Plan

## Scope

Close the V1.1 hardening publication loop after the published release tag remains fixed and the hardening branch advances with audit evidence.

## Steps

1. Make the Phase 19 post-publication audit repeatable after later audit commits.
2. Keep the strict equality field for compatibility, but add an ancestor/reachability field for the release tag target.
3. Add a release closure packet that records the release tag as fixed and reachable from the current hardening branch.
4. Confirm the existing `ogk-final-v1.1` tag remains unchanged.
5. Confirm no pull request creation, tag movement, or destructive filesystem action is recorded.
6. Add tests for the release closure packet and the idempotent post-publication audit state.
7. Re-run V1.1 verification, manifest dry-run, and release safety guards.

## Safety

- No GitHub release mutation.
- No tag movement.
- No pull request creation.
- No destructive filesystem action.
- Root-level `policies/` shadows remain excluded.
