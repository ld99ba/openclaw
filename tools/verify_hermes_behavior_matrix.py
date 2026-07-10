#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from openclaw.hermes_adapter.behavior_equivalence import CHECKS


ACCEPTED_RESULTS = {"ENHANCED", "EQUIVALENT_OR_SAFER", "EQUIVALENT_BASELINE"}


def build_behavior_matrix() -> dict:
    items = []
    for check, evidence, result in CHECKS:
        items.append({
            "check": check,
            "result": result,
            "evidence": evidence,
            "accepted": result in ACCEPTED_RESULTS,
            "runtime_copied": False if check == "runtime_not_replaced" else None,
        })
    return {
        "schema": "ogk.hermes_behavior_matrix.v1",
        "items": items,
        "summary": {
            "total": len(items),
            "accepted": sum(1 for item in items if item["accepted"]),
            "runtime_copied": False,
        },
    }


def verify_behavior_matrix() -> dict:
    matrix = build_behavior_matrix()
    missing = [item["check"] for item in matrix["items"] if not item["accepted"]]
    runtime_copied = matrix["summary"]["runtime_copied"]
    return {
        "ok": not missing and runtime_copied is False,
        "schema": matrix["schema"],
        "total": matrix["summary"]["total"],
        "accepted": matrix["summary"]["accepted"],
        "missing": missing,
        "runtime_copied": runtime_copied,
        "items": matrix["items"],
    }


def verify_hermes_behavior_matrix(output_dir: str | Path = "reports/v1_1/phase_02") -> dict:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    result = verify_behavior_matrix()

    (output / "hermes_behavior_matrix_result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    lines = [
        "# V1.1 Phase 02 Hermes Behavior Matrix",
        "",
        f"Status: {'PASS' if result['ok'] else 'FAIL'}",
        f"Accepted: {result['accepted']} / {result['total']}",
        f"Runtime copied: {result['runtime_copied']}",
        "",
        "| Check | Result | Accepted | Evidence |",
        "|---|---|---:|---|",
    ]
    for item in result["items"]:
        lines.append(f"| {item['check']} | {item['result']} | {item['accepted']} | {item['evidence']} |")
    (output / "hermes_behavior_matrix_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify V1.1 Hermes behavior equivalence matrix.")
    parser.add_argument("--output-dir", default="reports/v1_1/phase_02")
    args = parser.parse_args()
    result = verify_hermes_behavior_matrix(args.output_dir)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
