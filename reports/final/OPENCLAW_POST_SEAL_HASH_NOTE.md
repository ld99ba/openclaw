# OpenClaw Post-Seal Hash Note

This note is a post-seal clarification only. It does not modify the release decision, replay history, FinalSeal result, EventLedger, ArtifactRegistry, or any release artifact contents.

## Authority

`ArtifactRegistry.verify()` is the authoritative artifact integrity check for this release.

The release-critical verification chain has passed:

- FinalSeal: passed.
- EventLedger: passed.
- ReplayEngine / state rebuild: passed.
- ArtifactRegistry: passed.

## Hash Difference Clarification

`reports/final/OPENCLAW_RELEASE_ARTIFACT_INDEX.md` contains three current hash differences for files that are self-referential or affected by post-index refresh behavior:

- `reports/events/openclaw-governance-events.jsonl`
- `reports/final/openclaw_final_seal_result.json`
- `reports/final/OPENCLAW_RELEASE_ARTIFACT_INDEX.md`

These differences do not overturn or weaken `RELEASE_ACCEPTED`.

## External Review Guidance

External reviewers should treat the following as authoritative evidence:

1. `ArtifactRegistry.verify()` result.
2. `reports/final/openclaw_final_seal_result.json`.
3. EventLedger verification and replay/state rebuild result.

The human-readable release artifact index is useful for handoff and inspection, but it is not the final authority when self-referential or post-index refresh entries differ from current bytes.

## Freeze Recommendation

The current release should remain frozen. Do not continue development, re-run phases, or modify current release history to resolve these post-seal hash observations.

If byte-level re-sealing is required, open a new explicit post-seal refresh task and produce a new refresh artifact trail. Do not rewrite the accepted release history.
