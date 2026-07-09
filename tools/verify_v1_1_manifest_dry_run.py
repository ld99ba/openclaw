#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


FORBIDDEN_PREFIXES = (
    "reports/final/",
    "reports/events/",
    "main/",
)

REQUIRED_STATIC_PATHS = [
    "docs/plans/2026-07-09-ogk-final-v1-1-hardening-design.md",
    "docs/plans/2026-07-09-ogk-final-v1-1-phase-01-implementation-plan.md",
    "docs/plans/2026-07-09-ogk-final-v1-1-phase-02-implementation-plan.md",
    "docs/plans/2026-07-09-ogk-final-v1-1-phase-03-implementation-plan.md",
    "tools/verify_eventledger_replay.py",
    "tools/verify_artifact_registry_hashes.py",
    "tools/verify_recovery_boundaries.py",
    "tools/verify_hermes_behavior_matrix.py",
    "tools/verify_memory_skill_lifecycle.py",
    "tools/classify_v1_1_workspace_inventory.py",
    "tools/verify_v1_1_manifest_dry_run.py",
    "reports/v1_1/phase_01/PHASE_01_SUMMARY.md",
    "reports/v1_1/phase_02/PHASE_02_SUMMARY.md",
    "reports/v1_1/phase_03/PHASE_03_SUMMARY.md",
    "reports/v1_1/phase_03/manifest_dry_run_result.json",
    "reports/v1_1/phase_03/manifest_dry_run_report.md",
    "reports/v1_1/phase_03/workspace_inventory_result.json",
    "reports/v1_1/phase_03/workspace_inventory_report.md",
]


def discover_manifest_paths() -> list[str]:
    discovered = list(REQUIRED_STATIC_PATHS)
    discovered.extend(str(path) for path in sorted(Path("tests/v1_1").glob("test_*.py")))
    for phase in ("phase_01", "phase_02"):
        discovered.extend(str(path) for path in sorted(Path("reports/v1_1", phase).glob("*_result.json")))
        discovered.extend(str(path) for path in sorted(Path("reports/v1_1", phase).glob("*_report.md")))
    return sorted(dict.fromkeys(discovered))


def verify_v1_1_manifest_dry_run(output_dir: str | Path = "reports/v1_1/phase_03") -> dict:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    manifest = discover_manifest_paths()
    missing = [path for path in manifest if not Path(path).exists()]
    forbidden = [path for path in manifest if path.startswith(FORBIDDEN_PREFIXES)]
    result = {
        "schema": "ogk.v1_1.manifest_dry_run.v1",
        "ok": not missing and not forbidden,
        "manifest_count": len(manifest),
        "missing": missing,
        "forbidden": forbidden,
        "manifest": manifest,
        "git_stage_executed": False,
        "git_add_dot_used": False,
    }
    (output / "manifest_dry_run_result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    lines = [
        "# V1.1 Phase 03 Manifest Dry Run",
        "",
        f"Status: {'PASS' if result['ok'] else 'FAIL'}",
        f"Manifest paths: {result['manifest_count']}",
        f"Missing paths: {len(missing)}",
        f"Forbidden paths: {len(forbidden)}",
        "Git staging executed: False",
        "",
        "| Path |",
        "|---|",
    ]
    for path in manifest:
        lines.append(f"| {path} |")
    (output / "manifest_dry_run_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Dry-run V1.1 manifest-driven release candidates.")
    parser.add_argument("--output-dir", default="reports/v1_1/phase_03")
    args = parser.parse_args()
    result = verify_v1_1_manifest_dry_run(args.output_dir)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
