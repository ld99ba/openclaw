#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.propose_v1_1_workspace_hygiene import (
    FORBIDDEN_AUTO_IGNORE_PATTERNS,
    SAFE_GITIGNORE_ADDITIONS,
    load_gitignore,
)


IGNORED_SAMPLES = [
    "__pycache__/module.cpython-312.pyc",
    "pkg/__pycache__/module.cpython-312.pyc",
    ".pytest_cache/v/cache/nodeids",
    "node_modules/pkg/index.js",
    ".pw-browsers/chromium/cache.txt",
    ".clawhub/lock.json",
    ".forge/candidates.jsonl",
    ".locks/runtime.lock",
    ".openclaw-locks/runtime.lock",
    ".openclaw/local-state.json",
    ".mx-claw-workspace/session.json",
    ".learnings/index.json",
    "reports/.archive/old-evidence.json",
    "reports/.backup/old-evidence.json",
    "reports/.locks/report.lock",
    "reports/.rollback/rollback.json",
    "reports/.hermes-example.lock",
    ".hermes-auto.lock.stale-20260624-132341",
]

PROTECTED_SAMPLES = [
    "docs/plans/2026-07-09-ogk-final-v1-1-phase-06-implementation-plan.md",
    "openclaw/governance/supervisor.py",
    "reports/final/current_state.json",
    "reports/v1_1/phase_06/PHASE_06_SUMMARY.md",
    "tests/v1_1/test_gitignore_hygiene.py",
    "tools/verify_v1_1_gitignore_hygiene.py",
]


def _git_check_ignore(path: str) -> bool:
    completed = subprocess.run(
        ["git", "check-ignore", "--no-index", "-q", path],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return completed.returncode == 0


def evaluate_gitignore(entries: set[str]) -> dict[str, Any]:
    missing = [pattern for pattern in SAFE_GITIGNORE_ADDITIONS if pattern not in entries]
    forbidden = [pattern for pattern in FORBIDDEN_AUTO_IGNORE_PATTERNS if pattern in entries]
    return {
        "missing_required_patterns": missing,
        "forbidden_patterns_present": forbidden,
        "required_pattern_count": len(SAFE_GITIGNORE_ADDITIONS),
    }


def verify_gitignore_hygiene(output_dir: str | Path = "reports/v1_1/phase_06") -> dict[str, Any]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    entries = load_gitignore()
    pattern_result = evaluate_gitignore(entries)
    ignored_sample_results = {sample: _git_check_ignore(sample) for sample in IGNORED_SAMPLES}
    protected_sample_results = {sample: _git_check_ignore(sample) for sample in PROTECTED_SAMPLES}
    ignored_failures = [
        sample for sample, ignored in ignored_sample_results.items() if ignored is not True
    ]
    protected_failures = [
        sample for sample, ignored in protected_sample_results.items() if ignored is not False
    ]

    result: dict[str, Any] = {
        "schema": "ogk.v1_1.gitignore_hygiene.v1",
        "ok": not pattern_result["missing_required_patterns"]
        and not pattern_result["forbidden_patterns_present"]
        and not ignored_failures
        and not protected_failures,
        "required_pattern_count": pattern_result["required_pattern_count"],
        "missing_required_patterns": pattern_result["missing_required_patterns"],
        "forbidden_patterns_present": pattern_result["forbidden_patterns_present"],
        "ignored_sample_results": ignored_sample_results,
        "protected_sample_results": protected_sample_results,
        "ignored_sample_failures": ignored_failures,
        "protected_sample_failures": protected_failures,
        "gitignore_updated": True,
        "destructive_action_taken": False,
        "files_moved_or_deleted": False,
    }
    (output / "gitignore_hygiene_result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    write_report(output, result)
    return result


def write_report(output: Path, result: dict[str, Any]) -> None:
    lines = [
        "# V1.1 Phase 06 Gitignore Hygiene",
        "",
        f"Status: {'PASS' if result['ok'] else 'FAIL'}",
        f"Required patterns: {result['required_pattern_count']}",
        f"Missing required patterns: {len(result['missing_required_patterns'])}",
        f"Forbidden patterns present: {len(result['forbidden_patterns_present'])}",
        f"Destructive action taken: `{result['destructive_action_taken']}`",
        "",
        "## Ignored Samples",
        "",
        "| Path | Ignored |",
        "|---|---|",
    ]
    for path, ignored in result["ignored_sample_results"].items():
        lines.append(f"| `{path}` | `{ignored}` |")

    lines.extend(["", "## Protected Samples", "", "| Path | Ignored |", "|---|---|"])
    for path, ignored in result["protected_sample_results"].items():
        lines.append(f"| `{path}` | `{ignored}` |")

    if result["missing_required_patterns"] or result["forbidden_patterns_present"]:
        lines.extend(["", "## Pattern Failures", ""])
        lines.extend(f"- missing `{pattern}`" for pattern in result["missing_required_patterns"])
        lines.extend(f"- forbidden `{pattern}`" for pattern in result["forbidden_patterns_present"])

    (output / "gitignore_hygiene_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify V1.1 gitignore hygiene rules.")
    parser.add_argument("--output-dir", default="reports/v1_1/phase_06")
    args = parser.parse_args()
    result = verify_gitignore_hygiene(args.output_dir)
    summary = {
        "schema": result["schema"],
        "ok": result["ok"],
        "missing_required_patterns": result["missing_required_patterns"],
        "forbidden_patterns_present": result["forbidden_patterns_present"],
        "ignored_sample_failures": result["ignored_sample_failures"],
        "protected_sample_failures": result["protected_sample_failures"],
        "destructive_action_taken": result["destructive_action_taken"],
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
