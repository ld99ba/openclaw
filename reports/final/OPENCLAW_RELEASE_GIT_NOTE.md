# OpenClaw Release Git Note

This release commit is scoped to the top-level workspace repository:

`/root/.openclaw/workspace`

## Nested Repository Exclusion

`main/` is a nested Git repository under the top-level workspace. It is intentionally excluded from this top-level OGK-Final release commit and tag.

This release process did not:

- delete `main/`;
- modify `main/` contents;
- modify `main/` internal Git state;
- include `main/` as a submodule;
- include `main/` files in the top-level release commit.

## Release Scope

The top-level release commit covers the OGK-Final / Hermes OpenClaw fusion source, governance documents, reports, event ledger, final seal artifacts, handoff notes, and release metadata that live directly under `/root/.openclaw/workspace`, excluding `main/`.

The top-level `.gitignore` contains `/main/` to preserve this boundary and prevent accidental inclusion of the nested repository in the top-level release history.

## Patch Seal Correction

A post-tag Git sealing review found that the original `ogk-final-v1.0` tag/commit omitted two release-critical files that were present in the workspace but not included in the initial commit:

- `reports/final/issue_register.json`
- `tools/test_ogk_final_acceptance.py`

This patch commit corrects the Git sealing boundary only. It does not re-run OGK-Final phases, regenerate the release, modify core code, or change the accepted release decision.

The patch commit adds:

- `reports/final/issue_register.json`
- `tools/test_ogk_final_acceptance.py`

Because `ogk-final-v1.0` had not been pushed to any remote, the local annotated tag is moved to the corrected complete release commit after this patch. The new tag target should be treated as the complete Git-sealed OGK-Final V1.0 release.
