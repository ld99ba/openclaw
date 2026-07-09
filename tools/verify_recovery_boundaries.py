#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from openclaw.execution.repair_engine import RepairEngine
from openclaw.recovery.error_taxonomy import classify_error


RECOVERY_LEVELS = {
    "rate_limit": "R1",
    "timeout": "R1",
    "context_overflow": "R1",
    "payload_too_large": "R1",
    "model_not_found": "R2",
    "auth": "R3",
    "billing": "R3",
    "permission_denied": "R3",
    "destructive_action": "R4",
    "unknown": "R3",
}

CASES = [
    {"name": "rate_limit_backoff", "message": "HTTP 429 rate_limit from provider", "expected_level": "R1", "expected_auto": True},
    {"name": "timeout_retry", "message": "timeout while waiting for model", "expected_level": "R1", "expected_auto": True},
    {"name": "model_fallback", "message": "model_not_found for requested model", "expected_level": "R2", "expected_auto": True},
    {"name": "auth_block", "message": "auth token rejected", "expected_level": "R3", "expected_auto": False},
    {"name": "destructive_block", "message": "destructive_action requested", "expected_level": "R4", "expected_auto": False},
    {"name": "secret_boundary", "message": "timeout while reading secret", "expected_level": "R1", "expected_auto": False, "has_secret": True},
    {"name": "external_boundary", "message": "timeout before external upload", "expected_level": "R1", "expected_auto": False, "external": True},
    {"name": "core_runtime_boundary", "message": "timeout mutating core runtime", "expected_level": "R1", "expected_auto": False, "core_runtime": True},
]


def assess_interruption(
    message: str,
    *,
    has_secret: bool = False,
    destructive: bool = False,
    external: bool = False,
    core_runtime: bool = False,
) -> dict:
    classification = classify_error(message)
    level = RECOVERY_LEVELS.get(classification["class"], "R3")
    auto_allowed = RepairEngine().can_auto_repair(
        level,
        has_secret=has_secret,
        destructive=destructive,
        external=external,
        core_runtime=core_runtime,
    )
    return {
        "class": classification["class"],
        "recovery": classification["recovery"],
        "repair_level": level,
        "auto_repair_allowed": auto_allowed,
        "requires_human_authorization": not auto_allowed,
    }


def verify_recovery_boundaries(output_dir: str | Path = "reports/v1_1/phase_02") -> dict:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    results = []

    for case in CASES:
        assessment = assess_interruption(
            case["message"],
            has_secret=case.get("has_secret", False),
            destructive=case.get("destructive", False),
            external=case.get("external", False),
            core_runtime=case.get("core_runtime", False),
        )
        passed = (
            assessment["repair_level"] == case["expected_level"]
            and assessment["auto_repair_allowed"] is case["expected_auto"]
        )
        results.append({"name": case["name"], "passed": passed, "assessment": assessment})

    result = {
        "schema": "ogk.v1_1.recovery_boundaries.v1",
        "ok": all(item["passed"] for item in results),
        "case_count": len(results),
        "results": results,
    }

    (output / "recovery_boundaries_result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    lines = [
        "# V1.1 Phase 02 Recovery Boundaries",
        "",
        f"Status: {'PASS' if result['ok'] else 'FAIL'}",
        "",
        "| Case | Level | Auto Repair | Result |",
        "|---|---|---:|---|",
    ]
    for item in results:
        assessment = item["assessment"]
        lines.append(
            f"| {item['name']} | {assessment['repair_level']} | {assessment['auto_repair_allowed']} | {'PASS' if item['passed'] else 'FAIL'} |"
        )
    (output / "recovery_boundaries_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify V1.1 recovery repair boundaries.")
    parser.add_argument("--output-dir", default="reports/v1_1/phase_02")
    args = parser.parse_args()
    result = verify_recovery_boundaries(args.output_dir)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
