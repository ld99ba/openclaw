#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any


DEFAULT_OUTPUT_DIR = Path("reports/v1_1/phase_14")
PHASES = tuple(f"phase_{index:02d}" for index in range(1, 14))
REQUIRED_RESULTS = {
    "phase_01": ("artifact_hash_result.json", "eventledger_replay_result.json"),
    "phase_02": (
        "hermes_behavior_matrix_result.json",
        "memory_skill_lifecycle_result.json",
        "recovery_boundaries_result.json",
    ),
    "phase_03": ("manifest_dry_run_result.json", "workspace_inventory_result.json"),
    "phase_04": (
        "main_governance_result.json",
        "supervisor_stability_result.json",
        "v1_1_final_acceptance_result.json",
    ),
    "phase_05": ("workspace_hygiene_proposal_result.json",),
    "phase_06": ("gitignore_hygiene_result.json",),
    "phase_07": ("untracked_review_queue_result.json",),
    "phase_08": ("source_candidate_assessment_result.json",),
    "phase_09": ("source_candidate_inclusion_decision_result.json",),
    "phase_10": ("source_inclusion_preflight_result.json",),
    "phase_11": ("source_inclusion_approval_gate_result.json",),
    "phase_12": ("source_inclusion_execution_result.json",),
    "phase_13": ("root_policy_shadow_disposition_result.json",),
}
ROOT_POLICY_SHADOWS = (
    "policies/cron_governance_policy.yaml",
    "policies/final_seal_policy.yaml",
    "policies/memory_skill_policy.yaml",
    "policies/migration_policy.yaml",
    "policies/repair_policy.yaml",
    "policies/tool_permission_policy.yaml",
)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def git_tracked_paths(paths: list[str]) -> set[str]:
    if not paths:
        return set()
    raw = subprocess.check_output(["git", "ls-files", "-z", "--", *paths])
    return {path for path in raw.decode("utf-8").split("\0") if path}


def summary_status(phase_dir: Path, phase: str) -> str:
    number = phase.split("_")[1]
    summary = phase_dir / f"PHASE_{number}_SUMMARY.md"
    if not summary.exists():
        return "MISSING"
    return "PASS" if "Status: PASS" in summary.read_text(encoding="utf-8") else "FAIL"


def build_release_readiness_gate(
    *,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    root: str | Path = ".",
    tracked_policy_shadows: set[str] | None = None,
) -> dict[str, Any]:
    root_path = Path(root)
    base = root_path / "reports" / "v1_1"
    failures: list[str] = []
    phase_status: dict[str, str] = {}
    evidence_status: dict[str, bool | None] = {}

    for phase in PHASES:
        phase_dir = base / phase
        phase_status[phase] = summary_status(phase_dir, phase)
        if phase_status[phase] != "PASS":
            failures.append(f"{phase} summary status is {phase_status[phase]}")
        for filename in REQUIRED_RESULTS[phase]:
            path = phase_dir / filename
            relative = str(path.relative_to(root_path))
            if not path.exists():
                evidence_status[relative] = None
                failures.append(f"missing evidence: {relative}")
                continue
            data = load_json(path)
            ok = data.get("ok")
            evidence_status[relative] = ok
            if ok is not True:
                failures.append(f"evidence is not ok: {relative}")

    policy_tracked = (
        tracked_policy_shadows
        if tracked_policy_shadows is not None
        else git_tracked_paths(list(ROOT_POLICY_SHADOWS))
    )
    if policy_tracked:
        failures.append("root policy shadows are tracked: " + ", ".join(sorted(policy_tracked)))

    phase13 = load_json(base / "phase_13" / "root_policy_shadow_disposition_result.json")
    phase13_excluded = sorted(phase13.get("excluded_pathspec", []))
    expected_excluded = sorted(ROOT_POLICY_SHADOWS)
    if phase13_excluded != expected_excluded:
        failures.append("phase_13 excluded pathspec does not match expected root policy shadows")
    if phase13.get("explicit_approval_required_before_stage") is not True:
        failures.append("phase_13 does not require approval before staging root policy shadows")
    if phase13.get("explicit_approval_required_before_delete") is not True:
        failures.append("phase_13 does not require approval before deleting root policy shadows")

    result: dict[str, Any] = {
        "schema": "ogk.v1_1.release_readiness_gate.v1",
        "ok": not failures,
        "phase_count": len(PHASES),
        "phase_status": phase_status,
        "evidence_status": evidence_status,
        "failure_count": len(failures),
        "failures": failures,
        "root_policy_shadow_count": len(ROOT_POLICY_SHADOWS),
        "tracked_root_policy_shadows": sorted(policy_tracked),
        "excluded_root_policy_shadows": phase13_excluded,
        "release_publication_performed": False,
        "tag_move_performed": False,
        "pull_request_created": False,
        "explicit_approval_required_before_release_publication": True,
        "explicit_approval_required_before_policy_shadow_stage_or_delete": True,
        "git_stage_executed": False,
        "git_commit_executed": False,
        "destructive_action_taken": False,
        "files_moved_or_deleted": False,
    }

    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    (output / "release_readiness_gate_result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    write_report(output, result)
    return result


def write_report(output: Path, result: dict[str, Any]) -> None:
    lines = [
        "# V1.1 Phase 14 Release Readiness Gate",
        "",
        f"Status: {'PASS' if result['ok'] else 'FAIL'}",
        f"Phases checked: {result['phase_count']}",
        f"Failures: {result['failure_count']}",
        f"Root policy shadows tracked: {len(result['tracked_root_policy_shadows'])}",
        f"Release publication performed: `{result['release_publication_performed']}`",
        f"Tag move performed: `{result['tag_move_performed']}`",
        f"Explicit approval required before release publication: `{result['explicit_approval_required_before_release_publication']}`",
        "",
        "## Phase Status",
        "",
        "| Phase | Status |",
        "|---|---|",
    ]
    for phase, status in result["phase_status"].items():
        lines.append(f"| {phase} | {status} |")

    lines.extend(["", "## Excluded Root Policy Shadows", "", "| Path |", "|---|"])
    for path in result["excluded_root_policy_shadows"]:
        lines.append(f"| `{path}` |")

    if result["failures"]:
        lines.extend(["", "## Failures", ""])
        lines.extend(f"- {failure}" for failure in result["failures"])

    (output / "release_readiness_gate_report.md").write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify V1.1 hardening evidence readiness without publishing.")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    args = parser.parse_args()
    result = build_release_readiness_gate(output_dir=args.output_dir)
    summary = {
        "schema": result["schema"],
        "ok": result["ok"],
        "phase_count": result["phase_count"],
        "failure_count": result["failure_count"],
        "root_policy_shadow_count": result["root_policy_shadow_count"],
        "tracked_root_policy_shadow_count": len(result["tracked_root_policy_shadows"]),
        "release_publication_performed": result["release_publication_performed"],
        "tag_move_performed": result["tag_move_performed"],
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
