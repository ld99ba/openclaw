#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_DECISION_PATH = Path("reports/v1_1/phase_09/source_candidate_inclusion_decision_result.json")
DEFAULT_PREFLIGHT_PATH = Path("reports/v1_1/phase_10/source_inclusion_preflight_result.json")
DEFAULT_OUTPUT_DIR = Path("reports/v1_1/phase_11")


def load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def build_source_inclusion_approval_gate(
    *,
    decision_result: dict[str, Any] | None = None,
    preflight_result: dict[str, Any] | None = None,
    decision_path: str | Path = DEFAULT_DECISION_PATH,
    preflight_path: str | Path = DEFAULT_PREFLIGHT_PATH,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
) -> dict[str, Any]:
    decision = decision_result if decision_result is not None else load_json(decision_path)
    preflight = preflight_result if preflight_result is not None else load_json(preflight_path)
    next_stage = list(decision["next_stage_pathspec"])
    deferred = list(decision["deferred_pathspec"])
    warning_paths = [
        item["path"]
        for item in preflight["preflight"]
        if item.get("warnings")
    ]

    result: dict[str, Any] = {
        "schema": "ogk.v1_1.source_inclusion_approval_gate.v1",
        "ok": preflight["blocking_issue_count"] == 0,
        "approval_granted": False,
        "approval_required": True,
        "approval_phrase": "批准纳入 Phase 09/10 的 10 个 openclaw 源码候选",
        "next_stage_pathspec_count": len(next_stage),
        "next_stage_pathspec": next_stage,
        "deferred_pathspec_count": len(deferred),
        "deferred_pathspec": deferred,
        "blocking_issue_count": preflight["blocking_issue_count"],
        "warning_count": preflight["warning_count"],
        "warning_paths": warning_paths,
        "recommended_exclusions": deferred,
        "git_stage_executed": False,
        "git_commit_executed": False,
        "destructive_action_taken": False,
        "files_moved_or_deleted": False,
    }

    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    (output / "source_inclusion_approval_gate_result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    write_report(output, result)
    return result


def write_report(output: Path, result: dict[str, Any]) -> None:
    lines = [
        "# V1.1 Phase 11 Source Inclusion Approval Gate",
        "",
        f"Status: {'PASS' if result['ok'] else 'FAIL'}",
        f"Approval granted: `{result['approval_granted']}`",
        f"Approval required: `{result['approval_required']}`",
        f"Approval phrase: `{result['approval_phrase']}`",
        f"Next-stage pathspec candidates: {result['next_stage_pathspec_count']}",
        f"Deferred candidates: {result['deferred_pathspec_count']}",
        f"Blocking issues: {result['blocking_issue_count']}",
        f"Warnings: {result['warning_count']}",
        f"Git staging executed: `{result['git_stage_executed']}`",
        f"Destructive action taken: `{result['destructive_action_taken']}`",
        "",
        "## Candidates Awaiting Approval",
        "",
        "| Path |",
        "|---|",
    ]
    for path in result["next_stage_pathspec"]:
        lines.append(f"| `{path}` |")

    lines.extend(["", "## Warning Paths", "", "| Path |", "|---|"])
    for path in result["warning_paths"]:
        lines.append(f"| `{path}` |")

    lines.extend(["", "## Recommended Exclusions", "", "| Path |", "|---|"])
    for path in result["recommended_exclusions"]:
        lines.append(f"| `{path}` |")

    (output / "source_inclusion_approval_gate_report.md").write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the V1.1 source inclusion approval gate packet.")
    parser.add_argument("--decision", default=str(DEFAULT_DECISION_PATH))
    parser.add_argument("--preflight", default=str(DEFAULT_PREFLIGHT_PATH))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    args = parser.parse_args()
    result = build_source_inclusion_approval_gate(
        decision_path=args.decision,
        preflight_path=args.preflight,
        output_dir=args.output_dir,
    )
    summary = {
        "schema": result["schema"],
        "ok": result["ok"],
        "approval_granted": result["approval_granted"],
        "approval_required": result["approval_required"],
        "next_stage_pathspec_count": result["next_stage_pathspec_count"],
        "deferred_pathspec_count": result["deferred_pathspec_count"],
        "blocking_issue_count": result["blocking_issue_count"],
        "warning_count": result["warning_count"],
        "git_stage_executed": result["git_stage_executed"],
        "destructive_action_taken": result["destructive_action_taken"],
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
