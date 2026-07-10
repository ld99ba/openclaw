#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


PHASES = ("phase_01", "phase_02", "phase_03", "phase_04")
REQUIRED_RESULTS = {
    "phase_01": (
        "artifact_hash_result.json",
        "eventledger_replay_result.json",
    ),
    "phase_02": (
        "hermes_behavior_matrix_result.json",
        "memory_skill_lifecycle_result.json",
        "recovery_boundaries_result.json",
    ),
    "phase_03": (
        "manifest_dry_run_result.json",
        "workspace_inventory_result.json",
    ),
    "phase_04": (
        "main_governance_result.json",
        "supervisor_stability_result.json",
    ),
}


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _git_output(args: list[str]) -> str:
    return subprocess.check_output(["git", *args], text=True).strip()


def _gh_release_url(tag: str) -> str | None:
    try:
        return subprocess.check_output(
            ["gh", "release", "view", tag, "--repo", "ld99ba/openclaw", "--json", "url", "--jq", ".url"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None


def _write_report(output: Path, result: dict[str, Any]) -> None:
    lines = [
        "# V1.1 Phase 04 Final Acceptance",
        "",
        f"Status: {'PASS' if result['ok'] else 'FAIL'}",
        f"Derived final status: `{result['final_status']}`",
        f"Derived release status: `{result['release_status']}`",
        f"Local tag present: `{result['local_tag_present']}`",
        f"GitHub release URL: {result['github_release_url'] or 'not checked'}",
        "",
        "| Phase | Result |",
        "|---|---|",
    ]
    for phase, status in result["phase_status"].items():
        lines.append(f"| {phase} | {status} |")
    if result["failures"]:
        lines.extend(["", "## Failures", ""])
        lines.extend(f"- {failure}" for failure in result["failures"])
    (output / "v1_1_final_acceptance_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def verify_v1_1_final_acceptance(
    output_dir: str | Path = "reports/v1_1/phase_04",
    *,
    tag: str = "ogk-final-v1.1",
    check_github_release: bool = True,
) -> dict[str, Any]:
    base = Path("reports/v1_1")
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    failures: list[str] = []
    phase_status: dict[str, str] = {}
    evidence: dict[str, Any] = {}
    for phase in PHASES:
        phase_dir = base / phase
        summary = phase_dir / f"PHASE_{phase.split('_')[1]}_SUMMARY.md"
        if phase == "phase_04":
            summary = phase_dir / "PHASE_04_SUMMARY.md"
        if summary.exists() and "Status: PASS" in summary.read_text(encoding="utf-8"):
            phase_status[phase] = "PASS"
        elif phase == "phase_04" and not summary.exists():
            phase_status[phase] = "PENDING_SUMMARY"
        else:
            phase_status[phase] = "FAIL"
            failures.append(f"{phase} summary is missing or not PASS")
        for filename in REQUIRED_RESULTS[phase]:
            path = phase_dir / filename
            if not path.exists():
                failures.append(f"missing evidence: {path}")
                continue
            data = _load_json(path)
            evidence[str(path)] = data.get("ok")
            if data.get("ok") is not True:
                failures.append(f"evidence is not ok: {path}")

    try:
        head = _git_output(["rev-parse", "HEAD"])
        tag_target = _git_output(["rev-list", "-n", "1", tag])
        local_tag_present = bool(tag_target)
        tag_points_to_head = head == tag_target
    except subprocess.CalledProcessError:
        head = ""
        tag_target = ""
        local_tag_present = False
        tag_points_to_head = False
        failures.append(f"local tag missing or unreadable: {tag}")

    release_url = _gh_release_url(tag) if check_github_release else None
    github_release_present = bool(release_url) if check_github_release else True
    if check_github_release and not github_release_present:
        failures.append(f"GitHub release missing or unreadable: {tag}")

    phase_04_summary_pending = phase_status.get("phase_04") == "PENDING_SUMMARY"
    effective_failures = [failure for failure in failures if "phase_04 summary" not in failure]
    ok = not effective_failures and local_tag_present and github_release_present

    result = {
        "schema": "ogk.v1_1.final_acceptance.v1",
        "ok": ok,
        "final_status": "FINAL_SUCCESS" if ok else "FINAL_SEAL_FAILED",
        "release_status": "RELEASE_ACCEPTED" if ok else "PENDING",
        "phase_status": phase_status,
        "phase_04_summary_pending": phase_04_summary_pending,
        "evidence_ok": evidence,
        "local_head": head,
        "local_tag": tag,
        "local_tag_target": tag_target,
        "local_tag_present": local_tag_present,
        "tag_points_to_current_head": tag_points_to_head,
        "tag_points_to_current_head_required": False,
        "github_release_present": github_release_present,
        "github_release_url": release_url,
        "failures": effective_failures,
        "derived_from_evidence": True,
        "manual_final_status_written": False,
    }
    (output / "v1_1_final_acceptance_result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    _write_report(output, result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Derive V1.1 final acceptance from committed evidence.")
    parser.add_argument("--output-dir", default="reports/v1_1/phase_04")
    parser.add_argument("--tag", default="ogk-final-v1.1")
    parser.add_argument("--skip-github-release-check", action="store_true")
    args = parser.parse_args()
    result = verify_v1_1_final_acceptance(
        args.output_dir,
        tag=args.tag,
        check_github_release=not args.skip_github_release_check,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
