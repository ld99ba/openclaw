#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any


DEFAULT_READINESS_PATH = Path("reports/v1_1/phase_14/release_readiness_gate_result.json")
DEFAULT_OUTPUT_DIR = Path("reports/v1_1/phase_15")
APPROVAL_PHRASE = "批准发布 V1.1 hardening 当前分支"


def load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def git_output(args: list[str]) -> str:
    try:
        return subprocess.check_output(["git", *args], text=True, stderr=subprocess.DEVNULL).strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        return ""


def build_release_publication_approval_gate(
    *,
    readiness_result: dict[str, Any] | None = None,
    readiness_path: str | Path = DEFAULT_READINESS_PATH,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    current_head: str | None = None,
    current_branch: str | None = None,
) -> dict[str, Any]:
    readiness = readiness_result if readiness_result is not None else load_json(readiness_path)
    failures: list[str] = []
    if readiness.get("ok") is not True:
        failures.append("phase_14_release_readiness_not_ok")
    if readiness.get("failure_count") not in (0, None):
        failures.append("phase_14_release_readiness_has_failures")
    if readiness.get("tracked_root_policy_shadows"):
        failures.append("root_policy_shadows_are_tracked")
    if readiness.get("release_publication_performed") is not False:
        failures.append("phase_14_publication_state_unexpected")
    if readiness.get("tag_move_performed") is not False:
        failures.append("phase_14_tag_state_unexpected")

    head = current_head if current_head is not None else git_output(["rev-parse", "HEAD"])
    branch = current_branch if current_branch is not None else git_output(["branch", "--show-current"])

    result: dict[str, Any] = {
        "schema": "ogk.v1_1.release_publication_approval_gate.v1",
        "ok": not failures,
        "approval_required": True,
        "approval_granted": False,
        "approval_phrase": APPROVAL_PHRASE,
        "current_branch": branch,
        "current_head": head,
        "readiness_schema": readiness.get("schema"),
        "readiness_ok": readiness.get("ok") is True,
        "readiness_failure_count": readiness.get("failure_count"),
        "root_policy_shadow_count": readiness.get("root_policy_shadow_count"),
        "tracked_root_policy_shadows": readiness.get("tracked_root_policy_shadows", []),
        "recommended_publication_target": "codex/ogk-final-v1.1-hardening branch evidence package",
        "release_publication_blocked_until_approval": True,
        "tag_move_requires_separate_approval": True,
        "pull_request_requires_owner_decision": True,
        "publication_actions_performed": False,
        "release_publication_performed": False,
        "tag_move_performed": False,
        "pull_request_created": False,
        "git_stage_executed": False,
        "git_commit_executed": False,
        "destructive_action_taken": False,
        "files_moved_or_deleted": False,
        "failure_count": len(failures),
        "failures": failures,
    }

    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    (output / "release_publication_approval_gate_result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    write_report(output, result)
    return result


def write_report(output: Path, result: dict[str, Any]) -> None:
    lines = [
        "# V1.1 Phase 15 Release Publication Approval Gate",
        "",
        f"Status: {'PASS' if result['ok'] else 'FAIL'}",
        f"Approval required: `{result['approval_required']}`",
        f"Approval granted: `{result['approval_granted']}`",
        f"Approval phrase: `{result['approval_phrase']}`",
        f"Current branch: `{result['current_branch']}`",
        f"Current head: `{result['current_head']}`",
        f"Readiness OK: `{result['readiness_ok']}`",
        f"Publication actions performed: `{result['publication_actions_performed']}`",
        f"Release publication blocked until approval: `{result['release_publication_blocked_until_approval']}`",
        f"Tag move requires separate approval: `{result['tag_move_requires_separate_approval']}`",
        "",
        "## Publication Boundary",
        "",
        "| Action | Performed | Approval Rule |",
        "|---|---|---|",
        f"| GitHub release publication | {result['release_publication_performed']} | exact approval phrase required |",
        f"| Tag movement | {result['tag_move_performed']} | separate explicit approval required |",
        f"| Pull request creation | {result['pull_request_created']} | owner decision required |",
    ]
    if result["failures"]:
        lines.extend(["", "## Failures", ""])
        lines.extend(f"- {failure}" for failure in result["failures"])

    (output / "release_publication_approval_gate_report.md").write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Build V1.1 release publication approval gate without publishing.")
    parser.add_argument("--readiness", default=str(DEFAULT_READINESS_PATH))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    args = parser.parse_args()
    result = build_release_publication_approval_gate(
        readiness_path=args.readiness,
        output_dir=args.output_dir,
    )
    summary = {
        "schema": result["schema"],
        "ok": result["ok"],
        "approval_required": result["approval_required"],
        "approval_granted": result["approval_granted"],
        "approval_phrase": result["approval_phrase"],
        "publication_actions_performed": result["publication_actions_performed"],
        "failure_count": result["failure_count"],
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
