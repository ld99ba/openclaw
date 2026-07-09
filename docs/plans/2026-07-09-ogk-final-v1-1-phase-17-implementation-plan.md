# OGK Final V1.1 Phase 17 Implementation Plan

## Scope

Refresh publication target evidence after the Phase 16 publication package draft, without publishing a GitHub release, moving tags, or creating a pull request.

## Steps

1. Add a publication target refresh verifier that records the remote branch ref as the publication target.
2. Confirm the local branch head matches the remote branch head at generation time.
3. Confirm the existing `ogk-final-v1.1` tag target has not changed since Phase 16.
4. Record that release publication, tag movement, and pull request creation remain unperformed.
5. Add tests for pass, remote drift, and tag drift cases.
6. Re-run V1.1 verification and manifest dry-run.

## Safety

- No destructive filesystem action.
- No tag movement.
- No GitHub release publication.
- No pull request creation.
- Root-level `policies/` shadows remain excluded.
