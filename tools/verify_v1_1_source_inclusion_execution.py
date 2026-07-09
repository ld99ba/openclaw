#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_APPROVAL_GATE_PATH = Path("reports/v1_1/phase_11/source_inclusion_approval_gate_result.json")
DEFAULT_OUTPUT_DIR = Path("reports/v1_1/phase_12")


def load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def build_source_inclusion_execution_record(
    *,
    approval_phrase: str,
    approval_gate_result: dict[str, Any] | None = None,
    approval_gate_path: str | Path = DEFAULT_APPROVAL_GATE_PATH,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
) -> dict[str, Any]:
    gate = approval_gate_result if approval_gate_result is not None else load_json(approval_gate_path)
    expected_phrase = gate["approval_phrase"]
    approval_granted = approval_phrase == expected_phrase
    approved_pathspec = list(gate["next_stage_pathspec"]) if approval_granted else []
    excluded_pathspec = list(gate["recommended_exclusions"])
    missing_approved_paths = [path for path in approved_pathspec if not Path(path).exists()]
    forbidden_root_policy_paths = [path for path in approved_pathspec if path.startswith("policies/")]

    result: dict[str, Any] = {
        "schema": "ogk.v1_1.source_inclusion_execution.v1",
        "ok": approval_granted and not missing_approved_paths and not forbidden_root_policy_paths,
        "approval_phrase_matched": approval_granted,
        "approval_granted": approval_granted,
        "approved_pathspec_count": len(approved_pathspec),
        "approved_pathspec": approved_pathspec,
        "excluded_pathspec_count": len(excluded_pathspec),
        "excluded_pathspec": excluded_pathspec,
        "missing_approved_paths": missing_approved_paths,
        "forbidden_root_policy_paths": forbidden_root_policy_paths,
        "preflight_blocking_issue_count": gate["blocking_issue_count"],
        "preflight_warning_count": gate["warning_count"],
        "git_stage_executed_by_tool": False,
        "git_commit_executed_by_tool": False,
        "destructive_action_taken": False,
        "files_moved_or_deleted": False,
    }

    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    (output / "source_inclusion_execution_result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    write_report(output, result)
    return result


def write_report(output: Path, result: dict[str, Any]) -> None:
    lines = [
        "# V1.1 Phase 12 Source Inclusion Execution",
        "",
        f"Status: {'PASS' if result['ok'] else 'FAIL'}",
        f"Approval phrase matched: `{result['approval_phrase_matched']}`",
        f"Approval granted: `{result['approval_granted']}`",
        f"Approved pathspec candidates: {result['approved_pathspec_count']}",
        f"Excluded pathspec candidates: {result['excluded_pathspec_count']}",
        f"Missing approved paths: {len(result['missing_approved_paths'])}",
        f"Forbidden root policy paths: {len(result['forbidden_root_policy_paths'])}",
        f"Preflight blocking issues: {result['preflight_blocking_issue_count']}",
        f"Preflight warnings: {result['preflight_warning_count']}",
        f"Git staging executed by tool: `{result['git_stage_executed_by_tool']}`",
        f"Destructive action taken: `{result['destructive_action_taken']}`",
        "",
        "## Approved Pathspec",
        "",
        "| Path |",
        "|---|",
    ]
    for path in result["approved_pathspec"]:
        lines.append(f"| `{path}` |")

    lines.extend(["", "## Excluded Pathspec", "", "| Path |", "|---|"])
    for path in result["excluded_pathspec"]:
        lines.append(f"| `{path}` |")

    (output / "source_inclusion_execution_report.md").write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Record approved V1.1 source candidate inclusion.")
    parser.add_argument("--approval-phrase", required=True)
    parser.add_argument("--approval-gate", default=str(DEFAULT_APPROVAL_GATE_PATH))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    args = parser.parse_args()
    result = build_source_inclusion_execution_record(
        approval_phrase=args.approval_phrase,
        approval_gate_path=args.approval_gate,
        output_dir=args.output_dir,
    )
    summary = {
        "schema": result["schema"],
        "ok": result["ok"],
        "approval_granted": result["approval_granted"],
        "approved_pathspec_count": result["approved_pathspec_count"],
        "excluded_pathspec_count": result["excluded_pathspec_count"],
        "missing_approved_paths": result["missing_approved_paths"],
        "forbidden_root_policy_paths": result["forbidden_root_policy_paths"],
        "git_stage_executed_by_tool": result["git_stage_executed_by_tool"],
        "destructive_action_taken": result["destructive_action_taken"],
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
