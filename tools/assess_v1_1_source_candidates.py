#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.classify_v1_1_workspace_inventory import classify_path
from tools.triage_v1_1_untracked_review_queue import review_bucket


def git_untracked_paths() -> list[str]:
    raw = subprocess.check_output(["git", "ls-files", "--others", "--exclude-standard", "-z"])
    return sorted(path for path in raw.decode("utf-8").split("\0") if path)


def discover_source_candidates(paths: list[str] | None = None) -> list[str]:
    untracked = git_untracked_paths() if paths is None else sorted(paths)
    return [
        path
        for path in untracked
        if classify_path(path) != "v1_1_release_candidate"
        and review_bucket(path) == "source_surface_candidate"
    ]


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def candidate_kind(path: str) -> str:
    name = Path(path).name
    if name == "__init__.py":
        return "package_marker"
    if name == "__main__.py":
        return "package_entrypoint"
    if path.startswith("policies/"):
        return "root_policy_shadow"
    if path.startswith("openclaw/policies/"):
        return "package_policy_config"
    if path.endswith(".json"):
        return "runtime_json_config"
    return "source_or_config_candidate"


def candidate_recommendation(kind: str, duplicate_of: str | None = None) -> str:
    if kind == "root_policy_shadow" and duplicate_of:
        return "prefer tracked package policy counterpart; do not stage root shadow without ADR"
    if kind == "package_marker":
        return "eligible for package completeness review; explicit approval required before staging"
    if kind == "package_entrypoint":
        return "review CLI behavior before inclusion; explicit approval required before staging"
    if kind in {"package_policy_config", "runtime_json_config"}:
        return "review runtime policy/config ownership before inclusion; explicit approval required before staging"
    return "review ownership and behavior before inclusion; explicit approval required before staging"


def assess_candidate(path: str, *, root: str | Path = ".") -> dict[str, Any]:
    base = Path(root)
    full_path = base / path
    exists = full_path.exists()
    kind = candidate_kind(path)
    duplicate_of: str | None = None
    duplicate_hash_match: bool | None = None
    if path.startswith("policies/"):
        counterpart = base / "openclaw" / "policies" / Path(path).name
        if counterpart.exists():
            duplicate_of = str(counterpart.relative_to(base))
            duplicate_hash_match = (
                exists and sha256_file(full_path) == sha256_file(counterpart)
            )

    size_bytes = full_path.stat().st_size if exists else None
    line_count = None
    sha256 = None
    if exists and full_path.is_file():
        data = full_path.read_bytes()
        sha256 = hashlib.sha256(data).hexdigest()
        line_count = data.count(b"\n") + (1 if data and not data.endswith(b"\n") else 0)

    return {
        "path": path,
        "exists": exists,
        "kind": kind,
        "size_bytes": size_bytes,
        "line_count": line_count,
        "sha256": sha256,
        "duplicate_of": duplicate_of,
        "duplicate_hash_match": duplicate_hash_match,
        "recommendation": candidate_recommendation(kind, duplicate_of),
        "explicit_approval_required_before_stage": True,
        "auto_stage_recommended": False,
    }


def build_source_candidate_assessment(
    *,
    paths: list[str] | None = None,
    output_dir: str | Path = "reports/v1_1/phase_08",
) -> dict[str, Any]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    candidates = discover_source_candidates(paths)
    assessments = [assess_candidate(path) for path in candidates]
    kind_counts: dict[str, int] = {}
    for item in assessments:
        kind_counts[item["kind"]] = kind_counts.get(item["kind"], 0) + 1

    duplicate_policy_shadows = [
        item for item in assessments if item["kind"] == "root_policy_shadow"
    ]
    result: dict[str, Any] = {
        "schema": "ogk.v1_1.source_candidate_assessment.v1",
        "ok": True,
        "source_candidate_count": len(assessments),
        "kind_counts": dict(sorted(kind_counts.items())),
        "duplicate_policy_shadow_count": len(duplicate_policy_shadows),
        "duplicate_policy_hash_match_count": sum(
            1 for item in duplicate_policy_shadows if item["duplicate_hash_match"] is True
        ),
        "assessments": assessments,
        "manual_review_required": True,
        "explicit_approval_required_before_stage": True,
        "git_stage_executed": False,
        "destructive_action_taken": False,
        "files_moved_or_deleted": False,
    }
    (output / "source_candidate_assessment_result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    write_report(output, result)
    return result


def write_report(output: Path, result: dict[str, Any]) -> None:
    lines = [
        "# V1.1 Phase 08 Source Candidate Assessment",
        "",
        f"Status: {'PASS' if result['ok'] else 'FAIL'}",
        f"Source candidates: {result['source_candidate_count']}",
        f"Duplicate policy shadows: {result['duplicate_policy_shadow_count']}",
        f"Duplicate policy hash matches: {result['duplicate_policy_hash_match_count']}",
        f"Manual review required: `{result['manual_review_required']}`",
        f"Git staging executed: `{result['git_stage_executed']}`",
        f"Destructive action taken: `{result['destructive_action_taken']}`",
        "",
        "## Kind Counts",
        "",
        "| Kind | Count |",
        "|---|---:|",
    ]
    for kind, count in result["kind_counts"].items():
        lines.append(f"| {kind} | {count} |")

    lines.extend(["", "## Candidate Assessment", "", "| Path | Kind | Bytes | Duplicate | Recommendation |", "|---|---|---:|---|---|"])
    for item in result["assessments"]:
        duplicate = item["duplicate_of"] or ""
        if item["duplicate_hash_match"] is not None:
            duplicate = f"{duplicate} hash_match={item['duplicate_hash_match']}"
        lines.append(
            f"| `{item['path']}` | {item['kind']} | {item['size_bytes']} | {duplicate} | {item['recommendation']} |"
        )

    (output / "source_candidate_assessment_report.md").write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Assess V1.1 source candidates without staging them.")
    parser.add_argument("--output-dir", default="reports/v1_1/phase_08")
    args = parser.parse_args()
    result = build_source_candidate_assessment(output_dir=args.output_dir)
    summary = {
        "schema": result["schema"],
        "ok": result["ok"],
        "source_candidate_count": result["source_candidate_count"],
        "kind_counts": result["kind_counts"],
        "duplicate_policy_shadow_count": result["duplicate_policy_shadow_count"],
        "duplicate_policy_hash_match_count": result["duplicate_policy_hash_match_count"],
        "manual_review_required": result["manual_review_required"],
        "git_stage_executed": result["git_stage_executed"],
        "destructive_action_taken": result["destructive_action_taken"],
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
