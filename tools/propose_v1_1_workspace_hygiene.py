#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.classify_v1_1_workspace_inventory import classify_path, inspect_main_boundary


SAFE_GITIGNORE_ADDITIONS = [
    "__pycache__/",
    "*.py[cod]",
    ".pytest_cache/",
    "node_modules/",
    ".pw-browsers/",
    ".clawhub/",
    ".forge/",
    ".locks/",
    ".openclaw-locks/",
    ".openclaw/",
    ".mx-claw-workspace/",
    ".learnings/",
    "reports/.archive/",
    "reports/.backup/",
    "reports/.locks/",
    "reports/.rollback/",
    "reports/.hermes-*.lock*",
    ".hermes-*.lock*",
]

FORBIDDEN_AUTO_IGNORE_PATTERNS = [
    "reports/**",
    "reports/final/**",
    "reports/v1_1/**",
    "docs/**",
    "tools/**",
    "tests/**",
    "openclaw/**",
]


def git_untracked_paths() -> list[str]:
    raw = subprocess.check_output(["git", "ls-files", "--others", "--exclude-standard", "-z"])
    return sorted(path for path in raw.decode("utf-8").split("\0") if path)


def load_gitignore(path: str | Path = ".gitignore") -> set[str]:
    gitignore = Path(path)
    if not gitignore.exists():
        return set()
    return {
        line.strip()
        for line in gitignore.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    }


def categorize_paths(paths: list[str]) -> dict[str, list[str]]:
    categories: dict[str, list[str]] = {}
    for path in paths:
        categories.setdefault(classify_path(path), []).append(path)
    return {key: sorted(value) for key, value in sorted(categories.items())}


def build_hygiene_proposal(
    *,
    paths: list[str] | None = None,
    gitignore_entries: set[str] | None = None,
    output_dir: str | Path = "reports/v1_1/phase_05",
) -> dict[str, Any]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    untracked = git_untracked_paths() if paths is None else sorted(paths)
    existing_gitignore = load_gitignore() if gitignore_entries is None else set(gitignore_entries)
    categories = categorize_paths(untracked)
    pending_gitignore = [
        pattern for pattern in SAFE_GITIGNORE_ADDITIONS if pattern not in existing_gitignore
    ]
    forbidden_hits = [
        pattern for pattern in pending_gitignore if pattern in FORBIDDEN_AUTO_IGNORE_PATTERNS
    ]
    category_counts = {key: len(value) for key, value in categories.items()}
    category_samples = {key: value[:20] for key, value in categories.items()}
    main_boundary = inspect_main_boundary()

    result: dict[str, Any] = {
        "schema": "ogk.v1_1.workspace_hygiene_proposal.v1",
        "ok": not forbidden_hits,
        "untracked_count": len(untracked),
        "category_counts": category_counts,
        "category_samples": category_samples,
        "safe_gitignore_additions": pending_gitignore,
        "forbidden_auto_ignore_patterns": FORBIDDEN_AUTO_IGNORE_PATTERNS,
        "forbidden_hits": forbidden_hits,
        "archive_plan": [
            {
                "category": "generated_cache",
                "recommendation": "ignore and regenerate on demand",
                "approval_required_before_move_or_delete": False,
            },
            {
                "category": "local_control_or_hidden_state",
                "recommendation": "ignore runtime-local state; preserve on disk",
                "approval_required_before_move_or_delete": True,
            },
            {
                "category": "historical_report_or_runtime_evidence",
                "recommendation": "keep out of V1.1 manifests; archive only after dedicated evidence review",
                "approval_required_before_move_or_delete": True,
            },
            {
                "category": "unknown_review_required",
                "recommendation": "do not ignore or archive automatically; require owner review",
                "approval_required_before_move_or_delete": True,
            },
            {
                "category": "v1_0_baseline_preserve",
                "recommendation": "preserve as baseline evidence; do not ignore broadly",
                "approval_required_before_move_or_delete": True,
            },
        ],
        "main_boundary": main_boundary,
        "direct_file_mutation_taken": False,
        "destructive_action_taken": False,
        "gitignore_updated": False,
        "git_stage_executed": False,
    }

    (output / "workspace_hygiene_proposal_result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    write_report(output, result)
    return result


def write_report(output: Path, result: dict[str, Any]) -> None:
    lines = [
        "# V1.1 Phase 05 Workspace Hygiene Proposal",
        "",
        f"Status: {'PASS' if result['ok'] else 'FAIL'}",
        f"Untracked paths: {result['untracked_count']}",
        f"Gitignore updated: `{result['gitignore_updated']}`",
        f"Destructive action taken: `{result['destructive_action_taken']}`",
        f"`main/` status: `{result['main_boundary']['status']}`",
        "",
        "## Category Counts",
        "",
        "| Category | Count | Sample |",
        "|---|---:|---|",
    ]
    for category, count in result["category_counts"].items():
        sample = ", ".join(result["category_samples"][category][:5])
        lines.append(f"| {category} | {count} | {sample} |")

    lines.extend(["", "## Safe Gitignore Additions", ""])
    if result["safe_gitignore_additions"]:
        lines.extend(f"- `{pattern}`" for pattern in result["safe_gitignore_additions"])
    else:
        lines.append("- none")

    lines.extend(["", "## Archive Plan", ""])
    for item in result["archive_plan"]:
        lines.append(
            f"- `{item['category']}`: {item['recommendation']} "
            f"(approval required before move/delete: `{item['approval_required_before_move_or_delete']}`)"
        )

    (output / "workspace_hygiene_proposal_report.md").write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Propose V1.1 workspace hygiene without mutating files.")
    parser.add_argument("--output-dir", default="reports/v1_1/phase_05")
    args = parser.parse_args()
    result = build_hygiene_proposal(output_dir=args.output_dir)
    summary = {
        "schema": result["schema"],
        "ok": result["ok"],
        "untracked_count": result["untracked_count"],
        "category_counts": result["category_counts"],
        "safe_gitignore_additions": result["safe_gitignore_additions"],
        "destructive_action_taken": result["destructive_action_taken"],
        "gitignore_updated": result["gitignore_updated"],
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
