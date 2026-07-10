#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from openclaw.intelligence.memory_lifecycle import MemoryLifecycle
from openclaw.intelligence.skill_lifecycle import SkillLifecycle


MEMORY_REQUIRED_FIELDS = {
    "source_required": "source",
    "purpose_required": "purpose",
    "expiry_required": "expiry",
    "audit_required": "audit",
}

SKILL_REQUIRED_FIELDS = {
    "tests_required": "tests",
    "promotion_gate_required": "promotion_gate",
    "rollback_required": "rollback",
    "workshop_required": "workshop",
}


def validate_lifecycle(record: dict, rules: dict, required_fields: dict) -> dict:
    missing = [
        field
        for rule, field in required_fields.items()
        if rules.get(rule) and not record.get(field)
    ]
    return {
        "ok": not missing,
        "missing": missing,
        "rules": dict(rules),
    }


def verify_memory_skill_lifecycle(output_dir: str | Path = "reports/v1_1/phase_02") -> dict:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    memory = MemoryLifecycle()
    skill = SkillLifecycle()

    memory_valid = validate_lifecycle({
        "source": "reports/final/current_state.json",
        "purpose": "resume context",
        "expiry": "2026-12-31",
        "audit": "reports/v1_1/phase_02/memory_skill_lifecycle_report.md",
    }, memory.rules, MEMORY_REQUIRED_FIELDS)
    memory_invalid = validate_lifecycle({"source": "scratch"}, memory.rules, MEMORY_REQUIRED_FIELDS)
    skill_valid = validate_lifecycle({
        "tests": ["tests/v1_1/test_memory_skill_lifecycle.py"],
        "promotion_gate": "pytest-pass",
        "rollback": "disable-skill-and-restore-previous-rules",
        "workshop": "manual-review-required-before-release",
    }, skill.rules, SKILL_REQUIRED_FIELDS)
    skill_invalid = validate_lifecycle({"tests": []}, skill.rules, SKILL_REQUIRED_FIELDS)

    result = {
        "schema": "ogk.v1_1.memory_skill_lifecycle.v1",
        "ok": (
            memory_valid["ok"]
            and not memory_invalid["ok"]
            and skill_valid["ok"]
            and not skill_invalid["ok"]
        ),
        "memory_valid": memory_valid,
        "memory_invalid": memory_invalid,
        "skill_valid": skill_valid,
        "skill_invalid": skill_invalid,
    }

    (output / "memory_skill_lifecycle_result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    lines = [
        "# V1.1 Phase 02 Memory/Skill Lifecycle",
        "",
        f"Status: {'PASS' if result['ok'] else 'FAIL'}",
        "",
        "| Contract | Valid Case | Invalid Case Missing Fields |",
        "|---|---:|---|",
        f"| MemoryLifecycle | {memory_valid['ok']} | {', '.join(memory_invalid['missing'])} |",
        f"| SkillLifecycle | {skill_valid['ok']} | {', '.join(skill_invalid['missing'])} |",
    ]
    (output / "memory_skill_lifecycle_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify V1.1 Memory/Skill lifecycle contracts.")
    parser.add_argument("--output-dir", default="reports/v1_1/phase_02")
    args = parser.parse_args()
    result = verify_memory_skill_lifecycle(args.output_dir)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
