# OpenClaw-Hermes Final Fusion Gap Audit

Status: ALIGNMENT_BASELINE

## Objective

Create one final deliverable system that preserves OpenClaw capabilities, preserves Hermes capabilities, and adds unified capabilities that exceed either source system alone.

This is not a new version ladder and not an immediate freeze. The goal is one final fused deliverable system.

## Non-goals

- Do not continue an unbounded V1.2/V1.3 version ladder.
- Do not freeze the current state as final before fusion gaps are closed.
- Do not treat migration/adaptation as full fusion without runtime evidence.

## Workstreams

| ID | Workstream | Current read | Done when |
|---|---|---|---|
| WS1 | Capability inventory and parity proof | partial | Every capability has a source anchor, OpenClaw owner, test surface, and evidence path.<br>No Hermes capability is classified only by narrative claim. |
| WS2 | Hermes capability promotion | open_gap | Adapter-only Hermes capabilities are either promoted, explicitly replaced by stronger OpenClaw-native behavior, or rejected with evidence.<br>The migrate-hermes plugin is a bridge, not the final proof of fusion. |
| WS3 | Unified governance kernel | strong_foundation | StateMachine, EventLedger, PolicyEngine, ToolGateway, Supervisor, and final acceptance share one coherent contract.<br>Approval boundaries are machine-checkable and human-readable. |
| WS4 | Memory, skill, and knowledge lifecycle | partial | Memory and skill artifacts carry source, purpose, expiry, audit, promotion, and rollback metadata.<br>Hermes-origin knowledge can be imported, validated, promoted, and reverted. |
| WS5 | Recovery and autonomous execution | partial | Interruptions, missing state, missing artifacts, inconsistent ledgers, and retry loops have bounded recovery paths.<br>Autonomy never crosses destructive, external, secret, release, or final-seal approval gates. |
| WS6 | Installable and operable product | open_gap | Fresh install, upgrade, smoke, package acceptance, and core e2e workflows are reproducible.<br>A third party can run the fused system without private project memory. |
| WS7 | Beyond-both-system capabilities | open_gap | The system can prove evidence-driven autonomous progress across sessions.<br>The system can supervise agent work, enforce policy, recover state, and emit acceptance evidence as one loop.<br>The beyond-both claims are covered by executable tests or replayable evidence. |

## Current Evidence Read

| Path | Meaning | Limitation |
|---|---|---|
| `openclaw/hermes_adapter/behavior_equivalence.py` | High-level Hermes behavior equivalence matrix source. | Only covers six broad checks; not a complete Hermes capability inventory. |
| `extensions/migrate-hermes` | OpenClaw plugin surface for importing Hermes state. | Migration provider is not by itself first-class runtime fusion. |
| `extensions/codex-supervisor` | Supervisor surface for listing, reading, and steering Codex sessions. | Needs integration proof with final fusion governance and recovery loops. |
| `openclaw/governance` | Policy, state machine, and supervisor kernel. | Needs final fusion contract spanning Hermes-origin capabilities. |
| `openclaw/evidence` | Artifact registry, event ledger, and replay primitives. | Needs final fusion evidence model for all workstreams. |
| `openclaw/intelligence` | Memory and skill lifecycle primitives. | Needs Hermes import/promotion/rollback evidence. |
| `reports/v1_1` | Hardening evidence for the current merged baseline. | Good baseline evidence, but not the final fusion completion program. |

## Gates

- No unbounded version ladder: work is closed by final fusion gates, not by V1.2/V1.3 naming.
- No final claim until every Hermes capability is inventoried, mapped, tested, or explicitly superseded.
- No adapter-only claim: migration and compatibility surfaces must be promoted or bounded.
- No unsafe autonomy: destructive, external, secret, release, and final-seal actions remain approval-gated.
- No release/tag mutation in this audit step.

## Immediate Next Action

Build the source-anchored capability inventory for OpenClaw and Hermes.
