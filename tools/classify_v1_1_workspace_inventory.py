#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def git_untracked_paths() -> list[str]:
    raw = subprocess.check_output(["git", "ls-files", "--others", "--exclude-standard", "-z"])
    return sorted(path for path in raw.decode("utf-8").split("\0") if path)


def classify_path(path: str) -> str:
    parts = path.split("/")
    if path.startswith("main/"):
        return "nested_repo_boundary"
    if "__pycache__" in parts or path.endswith(".pyc") or ".pytest_cache" in parts:
        return "generated_cache"
    if path.startswith("docs/plans/2026-07-09-ogk-final-v1-1"):
        return "v1_1_release_candidate"
    if path.startswith("tests/v1_1/"):
        return "v1_1_release_candidate"
    if path.startswith("reports/v1_1/"):
        return "v1_1_release_candidate"
    if path.startswith("tools/verify_") or path.startswith("tools/classify_v1_1_"):
        return "v1_1_release_candidate"
    if path.startswith("reports/final/"):
        return "v1_0_baseline_preserve"
    if path.startswith("reports/"):
        return "historical_report_or_runtime_evidence"
    if path.startswith(".") or "/." in path:
        return "local_control_or_hidden_state"
    return "unknown_review_required"


def inspect_main_boundary() -> dict:
    main = Path("main")
    git_marker = main / ".git"
    if not main.exists():
        return {"path": "main", "status": "absent", "recommendation": "no action required"}
    if git_marker.is_dir():
        status = "nested_git_repository"
    elif git_marker.is_file():
        status = "gitfile_boundary"
    else:
        status = "directory_without_git_marker"
    return {
        "path": "main",
        "status": status,
        "recommendation": "keep excluded until explicit governance approval; do not force-add into V1.1",
    }


def build_workspace_inventory(output_dir: str | Path = "reports/v1_1/phase_03") -> dict:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    paths = git_untracked_paths()
    categories: dict[str, list[str]] = {}
    for path in paths:
        categories.setdefault(classify_path(path), []).append(path)

    result = {
        "schema": "ogk.v1_1.workspace_inventory.v1",
        "ok": True,
        "untracked_count": len(paths),
        "category_counts": {key: len(value) for key, value in sorted(categories.items())},
        "category_samples": {key: value[:20] for key, value in sorted(categories.items())},
        "main_boundary": inspect_main_boundary(),
        "destructive_action_taken": False,
        "full_inventory_omitted": True,
        "full_inventory_omitted_reason": "release evidence records counts and samples only to avoid staging volatile caches and historical path noise",
    }
    (output / "workspace_inventory_result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    lines = [
        "# V1.1 Phase 03 Workspace Inventory",
        "",
        f"Status: {'PASS' if result['ok'] else 'FAIL'}",
        f"Untracked paths: {result['untracked_count']}",
        f"`main/` status: {result['main_boundary']['status']}",
        f"Recommendation: {result['main_boundary']['recommendation']}",
        "",
        "| Category | Count | Sample |",
        "|---|---:|---|",
    ]
    for category, count in result["category_counts"].items():
        sample = ", ".join(result["category_samples"][category][:5])
        lines.append(f"| {category} | {count} | {sample} |")
    (output / "workspace_inventory_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Classify V1.1 workspace inventory without changing files.")
    parser.add_argument("--output-dir", default="reports/v1_1/phase_03")
    args = parser.parse_args()
    result = build_workspace_inventory(args.output_dir)
    summary = {
        "schema": result["schema"],
        "ok": result["ok"],
        "untracked_count": result["untracked_count"],
        "category_counts": result["category_counts"],
        "main_boundary": result["main_boundary"],
        "destructive_action_taken": result["destructive_action_taken"],
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
