#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


OBJECTIVE = {
    "name": "OpenClaw-Hermes Final Fusion",
    "intent": (
        "Create one final deliverable system that preserves OpenClaw capabilities, "
        "preserves Hermes capabilities, and adds unified capabilities that exceed "
        "either source system alone."
    ),
    "not_the_goal": [
        "Do not continue an unbounded V1.2/V1.3 version ladder.",
        "Do not freeze the current state as final before fusion gaps are closed.",
        "Do not treat migration/adaptation as full fusion without runtime evidence.",
    ],
}


WORKSTREAMS = [
    {
        "id": "WS1",
        "name": "Capability inventory and parity proof",
        "goal": "Build a source-anchored inventory for every OpenClaw and Hermes capability.",
        "done_when": [
            "Every capability has a source anchor, OpenClaw owner, test surface, and evidence path.",
            "No Hermes capability is classified only by narrative claim.",
        ],
        "current_read": "partial",
    },
    {
        "id": "WS2",
        "name": "Hermes capability promotion",
        "goal": "Promote Hermes behavior from migration/adapter surfaces into first-class OpenClaw runtime capabilities.",
        "done_when": [
            "Adapter-only Hermes capabilities are either promoted, explicitly replaced by stronger OpenClaw-native behavior, or rejected with evidence.",
            "The migrate-hermes plugin is a bridge, not the final proof of fusion.",
        ],
        "current_read": "open_gap",
    },
    {
        "id": "WS3",
        "name": "Unified governance kernel",
        "goal": "Unify policy, approvals, state progression, event ledger, and final acceptance into one governed runtime.",
        "done_when": [
            "StateMachine, EventLedger, PolicyEngine, ToolGateway, Supervisor, and final acceptance share one coherent contract.",
            "Approval boundaries are machine-checkable and human-readable.",
        ],
        "current_read": "strong_foundation",
    },
    {
        "id": "WS4",
        "name": "Memory, skill, and knowledge lifecycle",
        "goal": "Fuse persistent memory, skill lifecycle, migration history, and rollback rules into a durable intelligence layer.",
        "done_when": [
            "Memory and skill artifacts carry source, purpose, expiry, audit, promotion, and rollback metadata.",
            "Hermes-origin knowledge can be imported, validated, promoted, and reverted.",
        ],
        "current_read": "partial",
    },
    {
        "id": "WS5",
        "name": "Recovery and autonomous execution",
        "goal": "Combine Hermes-style continuity with OpenClaw safety into bounded autonomous execution.",
        "done_when": [
            "Interruptions, missing state, missing artifacts, inconsistent ledgers, and retry loops have bounded recovery paths.",
            "Autonomy never crosses destructive, external, secret, release, or final-seal approval gates.",
        ],
        "current_read": "partial",
    },
    {
        "id": "WS6",
        "name": "Installable and operable product",
        "goal": "Make the fused system installable, runnable, observable, and handoff-ready.",
        "done_when": [
            "Fresh install, upgrade, smoke, package acceptance, and core e2e workflows are reproducible.",
            "A third party can run the fused system without private project memory.",
        ],
        "current_read": "open_gap",
    },
    {
        "id": "WS7",
        "name": "Beyond-both-system capabilities",
        "goal": "Deliver explicit capabilities that are only possible after fusion.",
        "done_when": [
            "The system can prove evidence-driven autonomous progress across sessions.",
            "The system can supervise agent work, enforce policy, recover state, and emit acceptance evidence as one loop.",
            "The beyond-both claims are covered by executable tests or replayable evidence.",
        ],
        "current_read": "open_gap",
    },
]


CURRENT_EVIDENCE = [
    {
        "path": "openclaw/hermes_adapter/behavior_equivalence.py",
        "meaning": "High-level Hermes behavior equivalence matrix source.",
        "limitation": "Only covers six broad checks; not a complete Hermes capability inventory.",
    },
    {
        "path": "extensions/migrate-hermes",
        "meaning": "OpenClaw plugin surface for importing Hermes state.",
        "limitation": "Migration provider is not by itself first-class runtime fusion.",
    },
    {
        "path": "extensions/codex-supervisor",
        "meaning": "Supervisor surface for listing, reading, and steering Codex sessions.",
        "limitation": "Needs integration proof with final fusion governance and recovery loops.",
    },
    {
        "path": "openclaw/governance",
        "meaning": "Policy, state machine, and supervisor kernel.",
        "limitation": "Needs final fusion contract spanning Hermes-origin capabilities.",
    },
    {
        "path": "openclaw/evidence",
        "meaning": "Artifact registry, event ledger, and replay primitives.",
        "limitation": "Needs final fusion evidence model for all workstreams.",
    },
    {
        "path": "openclaw/intelligence",
        "meaning": "Memory and skill lifecycle primitives.",
        "limitation": "Needs Hermes import/promotion/rollback evidence.",
    },
    {
        "path": "reports/v1_1",
        "meaning": "Hardening evidence for the current merged baseline.",
        "limitation": "Good baseline evidence, but not the final fusion completion program.",
    },
]


GATES = [
    "No unbounded version ladder: work is closed by final fusion gates, not by V1.2/V1.3 naming.",
    "No final claim until every Hermes capability is inventoried, mapped, tested, or explicitly superseded.",
    "No adapter-only claim: migration and compatibility surfaces must be promoted or bounded.",
    "No unsafe autonomy: destructive, external, secret, release, and final-seal actions remain approval-gated.",
    "No release/tag mutation in this audit step.",
]


def build_audit() -> dict:
    open_gaps = [item for item in WORKSTREAMS if item["current_read"] == "open_gap"]
    partial = [item for item in WORKSTREAMS if item["current_read"] == "partial"]
    return {
        "schema": "openclaw.hermes_final_fusion_gap_audit.v1",
        "objective": OBJECTIVE,
        "workstreams": WORKSTREAMS,
        "current_evidence": CURRENT_EVIDENCE,
        "gates": GATES,
        "summary": {
            "workstreams_total": len(WORKSTREAMS),
            "open_gap_count": len(open_gaps),
            "partial_count": len(partial),
            "strong_foundation_count": sum(1 for item in WORKSTREAMS if item["current_read"] == "strong_foundation"),
            "final_claim_allowed": False,
            "next_action": "Build the source-anchored capability inventory for OpenClaw and Hermes.",
        },
    }


def render_markdown(audit: dict) -> str:
    lines = [
        "# OpenClaw-Hermes Final Fusion Gap Audit",
        "",
        "Status: ALIGNMENT_BASELINE",
        "",
        "## Objective",
        "",
        audit["objective"]["intent"],
        "",
        "This is not a new version ladder and not an immediate freeze. The goal is one final fused deliverable system.",
        "",
        "## Non-goals",
        "",
    ]
    for item in audit["objective"]["not_the_goal"]:
        lines.append(f"- {item}")

    lines += [
        "",
        "## Workstreams",
        "",
        "| ID | Workstream | Current read | Done when |",
        "|---|---|---|---|",
    ]
    for item in audit["workstreams"]:
        done_when = "<br>".join(item["done_when"])
        lines.append(f"| {item['id']} | {item['name']} | {item['current_read']} | {done_when} |")

    lines += [
        "",
        "## Current Evidence Read",
        "",
        "| Path | Meaning | Limitation |",
        "|---|---|---|",
    ]
    for item in audit["current_evidence"]:
        lines.append(f"| `{item['path']}` | {item['meaning']} | {item['limitation']} |")

    lines += [
        "",
        "## Gates",
        "",
    ]
    for gate in audit["gates"]:
        lines.append(f"- {gate}")

    lines += [
        "",
        "## Immediate Next Action",
        "",
        audit["summary"]["next_action"],
        "",
    ]
    return "\n".join(lines)


def write_outputs(output_dir: Path) -> dict:
    audit = build_audit()
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "final_fusion_gap_audit.json").write_text(
        json.dumps(audit, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (output_dir / "final_fusion_gap_audit.md").write_text(render_markdown(audit), encoding="utf-8")
    return audit


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the OpenClaw-Hermes final fusion gap audit.")
    parser.add_argument("--output-dir", default="reports/final_fusion")
    args = parser.parse_args()
    audit = write_outputs(Path(args.output_dir))
    print(json.dumps(audit["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
