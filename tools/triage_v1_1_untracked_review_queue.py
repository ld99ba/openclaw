#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.classify_v1_1_workspace_inventory import classify_path


SOURCE_PREFIXES = (
    "openclaw/",
    "policies/",
)
DOC_PREFIXES = (
    "docs/",
    "03_tasks/",
    "10_release/",
    "11_logs/",
)
LOCAL_KNOWLEDGE_PREFIXES = (
    "daily-review/",
    "feedback/",
    "memory/",
    "memory_db/",
)
EXTERNAL_PREFIXES = (
    "ai_frontier/",
    "backups/",
    "evolution_system/",
    "external/",
    "papers/",
    "plugins/",
)
MEDIA_SUFFIXES = (
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".mp4",
    ".mov",
    ".pdf",
)

BUCKET_RECOMMENDATIONS = {
    "source_surface_candidate": "review for a dedicated source inclusion ADR before staging",
    "baseline_evidence_preserve": "preserve as V1.0 baseline evidence; do not include in V1.1 hardening manifests automatically",
    "historical_runtime_evidence": "keep out of release manifests unless a later evidence review selects specific files",
    "historical_release_or_planning_material": "review as historical handoff material, not as code",
    "local_knowledge_or_memory_state": "preserve locally; do not publish without privacy review",
    "external_research_or_dependency_surface": "review ownership, license, and provenance before any inclusion",
    "media_or_binary_artifact": "review purpose and size before any inclusion",
    "local_control_state": "preserve locally or ignore with a narrow rule; do not publish",
    "root_misc_review": "requires owner review before staging",
}


def git_untracked_paths() -> list[str]:
    raw = subprocess.check_output(["git", "ls-files", "--others", "--exclude-standard", "-z"])
    return sorted(path for path in raw.decode("utf-8").split("\0") if path)


def review_bucket(path: str) -> str:
    if path.startswith(SOURCE_PREFIXES):
        return "source_surface_candidate"
    if path.startswith("reports/final/"):
        return "baseline_evidence_preserve"
    if path.startswith("reports/"):
        if path.startswith("reports/.") or "/." in path:
            return "local_control_state"
        return "historical_runtime_evidence"
    if path.startswith(DOC_PREFIXES):
        return "historical_release_or_planning_material"
    if path.startswith(LOCAL_KNOWLEDGE_PREFIXES):
        return "local_knowledge_or_memory_state"
    if path.startswith(EXTERNAL_PREFIXES):
        return "external_research_or_dependency_surface"
    if path.startswith(".") or "/." in path:
        return "local_control_state"
    if path.lower().endswith(MEDIA_SUFFIXES):
        return "media_or_binary_artifact"
    return "root_misc_review"


def build_review_queue(
    *,
    paths: list[str] | None = None,
    output_dir: str | Path = "reports/v1_1/phase_07",
) -> dict[str, Any]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    untracked = git_untracked_paths() if paths is None else sorted(paths)
    release_candidates = [
        path for path in untracked if classify_path(path) == "v1_1_release_candidate"
    ]
    review_paths = [path for path in untracked if path not in set(release_candidates)]
    buckets: dict[str, list[str]] = {}
    for path in review_paths:
        buckets.setdefault(review_bucket(path), []).append(path)

    bucket_counts = {key: len(value) for key, value in sorted(buckets.items())}
    bucket_samples = {key: sorted(value)[:25] for key, value in sorted(buckets.items())}
    source_candidates = buckets.get("source_surface_candidate", [])
    top_level_candidates = sorted({path.split("/", 1)[0] for path in review_paths})

    result: dict[str, Any] = {
        "schema": "ogk.v1_1.untracked_review_queue.v1",
        "ok": True,
        "untracked_count": len(untracked),
        "review_queue_count": len(review_paths),
        "v1_1_release_candidate_excluded_count": len(release_candidates),
        "v1_1_release_candidate_excluded_samples": sorted(release_candidates)[:30],
        "bucket_counts": bucket_counts,
        "bucket_samples": bucket_samples,
        "bucket_recommendations": BUCKET_RECOMMENDATIONS,
        "source_candidate_count": len(source_candidates),
        "source_candidate_samples": sorted(source_candidates)[:50],
        "top_level_candidate_count": len(top_level_candidates),
        "top_level_candidate_samples": top_level_candidates[:80],
        "manual_review_required": True,
        "explicit_approval_required_before_stage": True,
        "destructive_action_taken": False,
        "files_moved_or_deleted": False,
        "git_stage_executed": False,
    }
    (output / "untracked_review_queue_result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    write_report(output, result)
    return result


def write_report(output: Path, result: dict[str, Any]) -> None:
    lines = [
        "# V1.1 Phase 07 Untracked Review Queue",
        "",
        f"Status: {'PASS' if result['ok'] else 'FAIL'}",
        f"Untracked paths: {result['untracked_count']}",
        f"Review queue paths: {result['review_queue_count']}",
        f"V1.1 release candidates excluded: {result['v1_1_release_candidate_excluded_count']}",
        f"Source candidates: {result['source_candidate_count']}",
        f"Manual review required: `{result['manual_review_required']}`",
        f"Git staging executed: `{result['git_stage_executed']}`",
        f"Destructive action taken: `{result['destructive_action_taken']}`",
        "",
        "## Review Buckets",
        "",
        "| Bucket | Count | Recommendation | Sample |",
        "|---|---:|---|---|",
    ]
    for bucket, count in result["bucket_counts"].items():
        recommendation = result["bucket_recommendations"][bucket]
        sample = ", ".join(result["bucket_samples"][bucket][:5])
        lines.append(f"| {bucket} | {count} | {recommendation} | {sample} |")

    lines.extend(["", "## Top-Level Candidates", ""])
    lines.extend(f"- `{path}`" for path in result["top_level_candidate_samples"])

    if result["source_candidate_samples"]:
        lines.extend(["", "## Source Candidate Samples", ""])
        lines.extend(f"- `{path}`" for path in result["source_candidate_samples"])

    (output / "untracked_review_queue_report.md").write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a V1.1 untracked review queue without mutating files.")
    parser.add_argument("--output-dir", default="reports/v1_1/phase_07")
    args = parser.parse_args()
    result = build_review_queue(output_dir=args.output_dir)
    summary = {
        "schema": result["schema"],
        "ok": result["ok"],
        "untracked_count": result["untracked_count"],
        "review_queue_count": result["review_queue_count"],
        "v1_1_release_candidate_excluded_count": result[
            "v1_1_release_candidate_excluded_count"
        ],
        "bucket_counts": result["bucket_counts"],
        "source_candidate_count": result["source_candidate_count"],
        "manual_review_required": result["manual_review_required"],
        "destructive_action_taken": result["destructive_action_taken"],
        "git_stage_executed": result["git_stage_executed"],
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
