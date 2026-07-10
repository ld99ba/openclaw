#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import json
import subprocess
from pathlib import Path
from typing import Any


DEFAULT_DECISION_PATH = Path("reports/v1_1/phase_09/source_candidate_inclusion_decision_result.json")
DEFAULT_OUTPUT_DIR = Path("reports/v1_1/phase_10")


def load_decision(path: str | Path = DEFAULT_DECISION_PATH) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def git_tracked_paths(paths: list[str]) -> set[str]:
    if not paths:
        return set()
    raw = subprocess.check_output(["git", "ls-files", "-z", "--", *paths])
    return {path for path in raw.decode("utf-8").split("\0") if path}


def python_syntax_status(path: Path) -> dict[str, Any]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except SyntaxError as exc:
        return {
            "python_syntax_ok": False,
            "syntax_error": f"{exc.msg} at line {exc.lineno}",
            "top_level_call_count": None,
            "top_level_print_call": None,
            "module_docstring": None,
        }

    top_level_calls = [
        node for node in tree.body if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call)
    ]
    top_level_print_call = any(
        isinstance(node.value.func, ast.Name) and node.value.func.id == "print"
        for node in top_level_calls
    )
    return {
        "python_syntax_ok": True,
        "syntax_error": None,
        "top_level_call_count": len(top_level_calls),
        "top_level_print_call": top_level_print_call,
        "module_docstring": ast.get_docstring(tree),
    }


def json_status(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {
            "json_parse_ok": False,
            "json_error": f"{exc.msg} at line {exc.lineno}",
            "json_top_level_keys": [],
        }
    return {
        "json_parse_ok": True,
        "json_error": None,
        "json_top_level_keys": sorted(data) if isinstance(data, dict) else [],
    }


def preflight_candidate(path: str, *, tracked_paths: set[str] | None = None) -> dict[str, Any]:
    full_path = Path(path)
    tracked = path in tracked_paths if tracked_paths is not None else False
    exists = full_path.exists()
    result: dict[str, Any] = {
        "path": path,
        "exists": exists,
        "already_tracked": tracked,
        "root_policy_shadow": path.startswith("policies/"),
        "blocking_issues": [],
        "warnings": [],
    }

    if not exists:
        result["blocking_issues"].append("candidate_path_missing")
        return result
    if tracked:
        result["blocking_issues"].append("candidate_already_tracked")
    if path.startswith("policies/"):
        result["blocking_issues"].append("root_policy_shadow_not_allowed_in_preflight")

    suffix = full_path.suffix
    if suffix == ".py":
        result.update(python_syntax_status(full_path))
        if result["python_syntax_ok"] is False:
            result["blocking_issues"].append("python_syntax_error")
        if full_path.name == "__main__.py" and result["top_level_print_call"]:
            result["warnings"].append("entrypoint_has_top_level_print_call")
    elif suffix == ".json":
        result.update(json_status(full_path))
        if result["json_parse_ok"] is False:
            result["blocking_issues"].append("json_parse_error")
        if path.endswith("project_spec.json"):
            result["warnings"].append("project_spec_version_requires_owner_confirmation")
        if path.endswith("policy.json"):
            result["warnings"].append("runtime_policy_config_requires_owner_confirmation")

    return result


def build_source_inclusion_preflight(
    *,
    decision_result: dict[str, Any] | None = None,
    decision_path: str | Path = DEFAULT_DECISION_PATH,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
) -> dict[str, Any]:
    decision = decision_result if decision_result is not None else load_decision(decision_path)
    candidates = list(decision["next_stage_pathspec"])
    tracked = git_tracked_paths(candidates) if decision_result is None else set()
    preflight = [preflight_candidate(path, tracked_paths=tracked) for path in candidates]
    blocking_issue_count = sum(len(item["blocking_issues"]) for item in preflight)
    warning_count = sum(len(item["warnings"]) for item in preflight)

    result: dict[str, Any] = {
        "schema": "ogk.v1_1.source_inclusion_preflight.v1",
        "ok": blocking_issue_count == 0,
        "candidate_count": len(preflight),
        "blocking_issue_count": blocking_issue_count,
        "warning_count": warning_count,
        "preflight": preflight,
        "explicit_approval_required_before_stage": True,
        "git_stage_executed": False,
        "destructive_action_taken": False,
        "files_moved_or_deleted": False,
    }
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    (output / "source_inclusion_preflight_result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    write_report(output, result)
    return result


def write_report(output: Path, result: dict[str, Any]) -> None:
    lines = [
        "# V1.1 Phase 10 Source Inclusion Preflight",
        "",
        f"Status: {'PASS' if result['ok'] else 'FAIL'}",
        f"Candidates: {result['candidate_count']}",
        f"Blocking issues: {result['blocking_issue_count']}",
        f"Warnings: {result['warning_count']}",
        f"Explicit approval required before stage: `{result['explicit_approval_required_before_stage']}`",
        f"Git staging executed: `{result['git_stage_executed']}`",
        f"Destructive action taken: `{result['destructive_action_taken']}`",
        "",
        "## Candidate Preflight",
        "",
        "| Path | Blocking Issues | Warnings |",
        "|---|---|---|",
    ]
    for item in result["preflight"]:
        blocking = ", ".join(item["blocking_issues"]) or ""
        warnings = ", ".join(item["warnings"]) or ""
        lines.append(f"| `{item['path']}` | {blocking} | {warnings} |")

    (output / "source_inclusion_preflight_report.md").write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Preflight V1.1 source inclusion candidates without staging.")
    parser.add_argument("--decision", default=str(DEFAULT_DECISION_PATH))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    args = parser.parse_args()
    result = build_source_inclusion_preflight(decision_path=args.decision, output_dir=args.output_dir)
    summary = {
        "schema": result["schema"],
        "ok": result["ok"],
        "candidate_count": result["candidate_count"],
        "blocking_issue_count": result["blocking_issue_count"],
        "warning_count": result["warning_count"],
        "explicit_approval_required_before_stage": result["explicit_approval_required_before_stage"],
        "git_stage_executed": result["git_stage_executed"],
        "destructive_action_taken": result["destructive_action_taken"],
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
