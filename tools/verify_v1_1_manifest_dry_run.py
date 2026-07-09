#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


FORBIDDEN_PREFIXES = (
    "reports/final/",
    "reports/events/",
    "main/",
)

REQUIRED_STATIC_PATHS = [
    ".gitignore",
    "docs/plans/2026-07-09-ogk-final-v1-1-hardening-design.md",
    "docs/plans/2026-07-09-ogk-final-v1-1-phase-01-implementation-plan.md",
    "docs/plans/2026-07-09-ogk-final-v1-1-phase-02-implementation-plan.md",
    "docs/plans/2026-07-09-ogk-final-v1-1-phase-03-implementation-plan.md",
    "docs/plans/2026-07-09-ogk-final-v1-1-phase-04-implementation-plan.md",
    "docs/plans/2026-07-09-ogk-final-v1-1-phase-05-implementation-plan.md",
    "docs/plans/2026-07-09-ogk-final-v1-1-phase-06-implementation-plan.md",
    "docs/plans/2026-07-09-ogk-final-v1-1-phase-07-implementation-plan.md",
    "docs/plans/2026-07-09-ogk-final-v1-1-phase-08-implementation-plan.md",
    "docs/plans/2026-07-09-ogk-final-v1-1-phase-09-implementation-plan.md",
    "docs/plans/2026-07-09-ogk-final-v1-1-phase-10-implementation-plan.md",
    "docs/plans/2026-07-09-ogk-final-v1-1-phase-11-implementation-plan.md",
    "docs/plans/2026-07-09-ogk-final-v1-1-phase-12-implementation-plan.md",
    "docs/plans/2026-07-09-ogk-final-v1-1-phase-13-implementation-plan.md",
    "docs/plans/2026-07-09-ogk-final-v1-1-phase-14-implementation-plan.md",
    "docs/plans/2026-07-09-ogk-final-v1-1-phase-15-implementation-plan.md",
    "docs/plans/2026-07-09-ogk-final-v1-1-phase-16-implementation-plan.md",
    "docs/plans/2026-07-09-ogk-final-v1-1-phase-17-implementation-plan.md",
    "docs/plans/2026-07-09-ogk-final-v1-1-phase-18-implementation-plan.md",
    "docs/plans/2026-07-10-ogk-final-v1-1-phase-19-implementation-plan.md",
    "docs/plans/2026-07-10-ogk-final-v1-1-phase-20-implementation-plan.md",
    "openclaw/__init__.py",
    "openclaw/evidence/__init__.py",
    "openclaw/execution/__init__.py",
    "openclaw/governance/__init__.py",
    "openclaw/governance/project_spec.json",
    "openclaw/hermes_adapter/__init__.py",
    "openclaw/hermes_adapter/__main__.py",
    "openclaw/intelligence/__init__.py",
    "openclaw/policies/policy.json",
    "openclaw/recovery/__init__.py",
    "tools/build_v1_1_release_publication_package.py",
    "tools/build_v1_1_release_execution_packet.py",
    "tools/build_v1_1_release_closure_packet.py",
    "tools/verify_v1_1_publication_target_refresh.py",
    "tools/verify_v1_1_post_publication_audit.py",
    "tools/verify_eventledger_replay.py",
    "tools/verify_artifact_registry_hashes.py",
    "tools/verify_recovery_boundaries.py",
    "tools/verify_hermes_behavior_matrix.py",
    "tools/verify_memory_skill_lifecycle.py",
    "tools/classify_v1_1_workspace_inventory.py",
    "tools/verify_v1_1_manifest_dry_run.py",
    "tools/verify_v1_1_release_publication_approval_gate.py",
    "tools/verify_v1_1_release_readiness_gate.py",
    "tools/verify_supervisor_stability.py",
    "tools/verify_main_governance_boundary.py",
    "tools/verify_v1_1_final_acceptance.py",
    "tools/propose_v1_1_workspace_hygiene.py",
    "tools/verify_v1_1_gitignore_hygiene.py",
    "tools/triage_v1_1_untracked_review_queue.py",
    "tools/assess_v1_1_source_candidates.py",
    "tools/plan_v1_1_source_candidate_inclusion.py",
    "tools/verify_v1_1_source_inclusion_preflight.py",
    "tools/verify_v1_1_source_inclusion_approval_gate.py",
    "tools/verify_v1_1_source_inclusion_execution.py",
    "tools/verify_v1_1_root_policy_shadow_disposition.py",
    "reports/v1_1/phase_01/PHASE_01_SUMMARY.md",
    "reports/v1_1/phase_02/PHASE_02_SUMMARY.md",
    "reports/v1_1/phase_03/PHASE_03_SUMMARY.md",
    "reports/v1_1/phase_03/manifest_dry_run_result.json",
    "reports/v1_1/phase_03/manifest_dry_run_report.md",
    "reports/v1_1/phase_03/workspace_inventory_result.json",
    "reports/v1_1/phase_03/workspace_inventory_report.md",
    "reports/v1_1/phase_04/PHASE_04_SUMMARY.md",
    "reports/v1_1/phase_04/main_governance_adr.md",
    "reports/v1_1/phase_04/main_governance_result.json",
    "reports/v1_1/phase_04/supervisor_stability_report.md",
    "reports/v1_1/phase_04/supervisor_stability_result.json",
    "reports/v1_1/phase_04/v1_1_final_acceptance_report.md",
    "reports/v1_1/phase_04/v1_1_final_acceptance_result.json",
    "reports/v1_1/phase_05/PHASE_05_SUMMARY.md",
    "reports/v1_1/phase_05/workspace_hygiene_proposal_report.md",
    "reports/v1_1/phase_05/workspace_hygiene_proposal_result.json",
    "reports/v1_1/phase_06/PHASE_06_SUMMARY.md",
    "reports/v1_1/phase_06/gitignore_hygiene_report.md",
    "reports/v1_1/phase_06/gitignore_hygiene_result.json",
    "reports/v1_1/phase_07/PHASE_07_SUMMARY.md",
    "reports/v1_1/phase_07/untracked_review_queue_report.md",
    "reports/v1_1/phase_07/untracked_review_queue_result.json",
    "reports/v1_1/phase_08/PHASE_08_SUMMARY.md",
    "reports/v1_1/phase_08/source_candidate_assessment_report.md",
    "reports/v1_1/phase_08/source_candidate_assessment_result.json",
    "reports/v1_1/phase_09/PHASE_09_SUMMARY.md",
    "reports/v1_1/phase_09/source_candidate_inclusion_decision_report.md",
    "reports/v1_1/phase_09/source_candidate_inclusion_decision_result.json",
    "reports/v1_1/phase_10/PHASE_10_SUMMARY.md",
    "reports/v1_1/phase_10/source_inclusion_preflight_report.md",
    "reports/v1_1/phase_10/source_inclusion_preflight_result.json",
    "reports/v1_1/phase_11/PHASE_11_SUMMARY.md",
    "reports/v1_1/phase_11/source_inclusion_approval_gate_report.md",
    "reports/v1_1/phase_11/source_inclusion_approval_gate_result.json",
    "reports/v1_1/phase_12/PHASE_12_SUMMARY.md",
    "reports/v1_1/phase_12/source_inclusion_execution_report.md",
    "reports/v1_1/phase_12/source_inclusion_execution_result.json",
    "reports/v1_1/phase_13/PHASE_13_SUMMARY.md",
    "reports/v1_1/phase_13/root_policy_shadow_disposition_report.md",
    "reports/v1_1/phase_13/root_policy_shadow_disposition_result.json",
    "reports/v1_1/phase_14/PHASE_14_SUMMARY.md",
    "reports/v1_1/phase_14/release_readiness_gate_report.md",
    "reports/v1_1/phase_14/release_readiness_gate_result.json",
    "reports/v1_1/phase_15/PHASE_15_SUMMARY.md",
    "reports/v1_1/phase_15/release_publication_approval_gate_report.md",
    "reports/v1_1/phase_15/release_publication_approval_gate_result.json",
    "reports/v1_1/phase_16/PHASE_16_SUMMARY.md",
    "reports/v1_1/phase_16/RELEASE_NOTES_DRAFT.md",
    "reports/v1_1/phase_16/release_publication_package_report.md",
    "reports/v1_1/phase_16/release_publication_package_result.json",
    "reports/v1_1/phase_17/PHASE_17_SUMMARY.md",
    "reports/v1_1/phase_17/publication_target_refresh_report.md",
    "reports/v1_1/phase_17/publication_target_refresh_result.json",
    "reports/v1_1/phase_18/PHASE_18_SUMMARY.md",
    "reports/v1_1/phase_18/RELEASE_EXECUTION_PACKET.md",
    "reports/v1_1/phase_18/release_execution_packet_report.md",
    "reports/v1_1/phase_18/release_execution_packet_result.json",
    "reports/v1_1/phase_19/PHASE_19_SUMMARY.md",
    "reports/v1_1/phase_19/post_publication_audit_report.md",
    "reports/v1_1/phase_19/post_publication_audit_result.json",
    "reports/v1_1/phase_20/PHASE_20_SUMMARY.md",
    "reports/v1_1/phase_20/RELEASE_CLOSURE_PACKET.md",
    "reports/v1_1/phase_20/release_closure_packet_report.md",
    "reports/v1_1/phase_20/release_closure_packet_result.json",
]


def discover_manifest_paths() -> list[str]:
    discovered = list(REQUIRED_STATIC_PATHS)
    discovered.extend(str(path) for path in sorted(Path("tests/v1_1").glob("test_*.py")))
    for phase in ("phase_01", "phase_02"):
        discovered.extend(str(path) for path in sorted(Path("reports/v1_1", phase).glob("*_result.json")))
        discovered.extend(str(path) for path in sorted(Path("reports/v1_1", phase).glob("*_report.md")))
    return sorted(dict.fromkeys(discovered))


def verify_v1_1_manifest_dry_run(output_dir: str | Path = "reports/v1_1/phase_03") -> dict:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    manifest = discover_manifest_paths()
    missing = [path for path in manifest if not Path(path).exists()]
    forbidden = [path for path in manifest if path.startswith(FORBIDDEN_PREFIXES)]
    result = {
        "schema": "ogk.v1_1.manifest_dry_run.v1",
        "ok": not missing and not forbidden,
        "manifest_count": len(manifest),
        "missing": missing,
        "forbidden": forbidden,
        "manifest": manifest,
        "git_stage_executed": False,
        "git_add_dot_used": False,
    }
    (output / "manifest_dry_run_result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    lines = [
        "# V1.1 Phase 03 Manifest Dry Run",
        "",
        f"Status: {'PASS' if result['ok'] else 'FAIL'}",
        f"Manifest paths: {result['manifest_count']}",
        f"Missing paths: {len(missing)}",
        f"Forbidden paths: {len(forbidden)}",
        "Git staging executed: False",
        "",
        "| Path |",
        "|---|",
    ]
    for path in manifest:
        lines.append(f"| {path} |")
    (output / "manifest_dry_run_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Dry-run V1.1 manifest-driven release candidates.")
    parser.add_argument("--output-dir", default="reports/v1_1/phase_03")
    args = parser.parse_args()
    result = verify_v1_1_manifest_dry_run(args.output_dir)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
