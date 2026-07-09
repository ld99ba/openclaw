#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


DEFAULT_OUTPUT_DIR = Path("reports/v1_1/phase_13")
DEFAULT_POLICY_PATHS = [
    "policies/cron_governance_policy.yaml",
    "policies/final_seal_policy.yaml",
    "policies/memory_skill_policy.yaml",
    "policies/migration_policy.yaml",
    "policies/repair_policy.yaml",
    "policies/tool_permission_policy.yaml",
]
PACKAGE_POLICY_PATH = Path("openclaw/policies/policy.json")


def git_tracked_paths(paths: list[str]) -> set[str]:
    if not paths:
        return set()
    raw = subprocess.check_output(["git", "ls-files", "-z", "--", *paths])
    return {path for path in raw.decode("utf-8").split("\0") if path}


def parse_simple_yaml_scalars(text: str) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        parsed[key.strip()] = value.strip()
    return parsed


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_package_policy(path: Path = PACKAGE_POLICY_PATH) -> dict[str, Any]:
    if not path.exists():
        return {"exists": False, "version": None}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"exists": True, "version": None, "json_parse_ok": False}
    return {
        "exists": True,
        "version": data.get("version") if isinstance(data, dict) else None,
        "json_parse_ok": True,
    }


def inspect_policy_shadow(
    path: str,
    *,
    root: str | Path = ".",
    tracked_paths: set[str] | None = None,
    package_policy: dict[str, Any] | None = None,
) -> dict[str, Any]:
    base = Path(root)
    full_path = base / path
    exists = full_path.exists()
    tracked = path in tracked_paths if tracked_paths is not None else False
    package = package_policy if package_policy is not None else load_package_policy(base / PACKAGE_POLICY_PATH)

    item: dict[str, Any] = {
        "path": path,
        "exists": exists,
        "already_tracked": tracked,
        "root_policy_shadow": path.startswith("policies/"),
        "size_bytes": None,
        "line_count": None,
        "sha256": None,
        "parse_ok": False,
        "policy_name": None,
        "version": None,
        "package_policy_version": package.get("version"),
        "version_matches_package_policy": False,
        "safe_default": False,
        "forbids_destructive_without_authorization": False,
        "forbids_secret_output": False,
        "blocking_issues": [],
        "warnings": [],
        "recommended_disposition": "exclude_from_v1_1_manifest_pending_owner_adr",
        "approval_required_before_stage": True,
        "approval_required_before_delete": True,
    }

    if not exists:
        item["blocking_issues"].append("root_policy_shadow_missing")
        return item
    if tracked:
        item["blocking_issues"].append("root_policy_shadow_already_tracked")
    if not path.startswith("policies/"):
        item["blocking_issues"].append("not_root_policy_shadow")

    data = full_path.read_bytes()
    text = data.decode("utf-8")
    parsed = parse_simple_yaml_scalars(text)
    item.update(
        {
            "size_bytes": len(data),
            "line_count": data.count(b"\n") + (1 if data and not data.endswith(b"\n") else 0),
            "sha256": hashlib.sha256(data).hexdigest(),
            "parse_ok": bool(parsed),
            "policy_name": parsed.get("policy"),
            "version": parsed.get("version"),
            "version_matches_package_policy": parsed.get("version") == package.get("version"),
            "safe_default": parsed.get("default") == "safe_by_policy",
            "forbids_destructive_without_authorization": parsed.get(
                "forbid_destructive_without_authorization"
            )
            == "true",
            "forbids_secret_output": parsed.get("forbid_secret_output") == "true",
        }
    )

    required_keys = {
        "version",
        "policy",
        "default",
        "forbid_destructive_without_authorization",
        "forbid_secret_output",
    }
    missing_keys = sorted(required_keys - set(parsed))
    if missing_keys:
        item["warnings"].append("missing_expected_policy_keys:" + ",".join(missing_keys))
    if not item["version_matches_package_policy"]:
        item["warnings"].append("version_differs_from_package_policy")
    if item["safe_default"]:
        item["warnings"].append("policy_is_safety_relevant_do_not_drop_without_owner_review")

    return item


def build_root_policy_shadow_disposition(
    *,
    paths: list[str] | None = None,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    root: str | Path = ".",
    tracked_paths: set[str] | None = None,
) -> dict[str, Any]:
    selected_paths = list(paths or DEFAULT_POLICY_PATHS)
    tracked = tracked_paths if tracked_paths is not None else git_tracked_paths(selected_paths)
    package_policy = load_package_policy(Path(root) / PACKAGE_POLICY_PATH)
    inspections = [
        inspect_policy_shadow(
            path,
            root=root,
            tracked_paths=tracked,
            package_policy=package_policy,
        )
        for path in selected_paths
    ]
    blocking_issue_count = sum(len(item["blocking_issues"]) for item in inspections)
    warning_count = sum(len(item["warnings"]) for item in inspections)
    excluded = [
        item["path"]
        for item in inspections
        if item["recommended_disposition"] == "exclude_from_v1_1_manifest_pending_owner_adr"
    ]

    result: dict[str, Any] = {
        "schema": "ogk.v1_1.root_policy_shadow_disposition.v1",
        "ok": blocking_issue_count == 0,
        "policy_shadow_count": len(inspections),
        "excluded_pathspec_count": len(excluded),
        "excluded_pathspec": excluded,
        "blocking_issue_count": blocking_issue_count,
        "warning_count": warning_count,
        "package_policy_path": str(PACKAGE_POLICY_PATH),
        "package_policy_exists": package_policy.get("exists") is True,
        "package_policy_version": package_policy.get("version"),
        "inspections": inspections,
        "recommended_next_action": "owner_adr_required_before_stage_migrate_or_delete",
        "explicit_approval_required_before_stage": True,
        "explicit_approval_required_before_delete": True,
        "git_stage_executed": False,
        "git_commit_executed": False,
        "destructive_action_taken": False,
        "files_moved_or_deleted": False,
    }

    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    (output / "root_policy_shadow_disposition_result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    write_report(output, result)
    return result


def write_report(output: Path, result: dict[str, Any]) -> None:
    lines = [
        "# V1.1 Phase 13 Root Policy Shadow Disposition",
        "",
        f"Status: {'PASS' if result['ok'] else 'FAIL'}",
        f"Policy shadows: {result['policy_shadow_count']}",
        f"Excluded pathspecs: {result['excluded_pathspec_count']}",
        f"Blocking issues: {result['blocking_issue_count']}",
        f"Warnings: {result['warning_count']}",
        f"Package policy: `{result['package_policy_path']}`",
        f"Package policy version: `{result['package_policy_version']}`",
        f"Recommended next action: `{result['recommended_next_action']}`",
        f"Git staging executed: `{result['git_stage_executed']}`",
        f"Destructive action taken: `{result['destructive_action_taken']}`",
        "",
        "## Disposition",
        "",
        "| Path | Policy | Version Match | Disposition | Warnings |",
        "|---|---|---|---|---|",
    ]
    for item in result["inspections"]:
        warnings = ", ".join(item["warnings"])
        lines.append(
            f"| `{item['path']}` | {item['policy_name']} | {item['version_matches_package_policy']} | "
            f"{item['recommended_disposition']} | {warnings} |"
        )

    lines.extend(["", "## Excluded Pathspec", "", "| Path |", "|---|"])
    for path in result["excluded_pathspec"]:
        lines.append(f"| `{path}` |")

    (output / "root_policy_shadow_disposition_report.md").write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect root policy shadows without staging or deleting them.")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    args = parser.parse_args()
    result = build_root_policy_shadow_disposition(output_dir=args.output_dir)
    summary = {
        "schema": result["schema"],
        "ok": result["ok"],
        "policy_shadow_count": result["policy_shadow_count"],
        "excluded_pathspec_count": result["excluded_pathspec_count"],
        "blocking_issue_count": result["blocking_issue_count"],
        "warning_count": result["warning_count"],
        "git_stage_executed": result["git_stage_executed"],
        "destructive_action_taken": result["destructive_action_taken"],
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
