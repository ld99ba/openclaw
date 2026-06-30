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
