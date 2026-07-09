from __future__ import annotations

from pathlib import Path

from tools.verify_hermes_behavior_matrix import (
    build_behavior_matrix,
    verify_behavior_matrix,
    verify_hermes_behavior_matrix,
)


def test_behavior_matrix_contains_required_equivalence_classes() -> None:
    matrix = build_behavior_matrix()
    results = {item["result"] for item in matrix["items"]}
    checks = {item["check"] for item in matrix["items"]}

    assert matrix["schema"] == "ogk.hermes_behavior_matrix.v1"
    assert {"ENHANCED", "EQUIVALENT_OR_SAFER", "EQUIVALENT_BASELINE"}.issubset(results)
    assert {
        "runtime_not_replaced",
        "state_driven_progress",
        "tool_safety",
        "permission_semantics",
        "error_recovery",
        "final_acceptance",
    }.issubset(checks)


def test_behavior_matrix_verification_rejects_runtime_copy_semantics() -> None:
    result = verify_behavior_matrix()
    runtime_item = next(item for item in result["items"] if item["check"] == "runtime_not_replaced")

    assert result["ok"] is True
    assert result["runtime_copied"] is False
    assert runtime_item["runtime_copied"] is False
    assert result["accepted"] == result["total"]


def test_hermes_behavior_matrix_verifier_writes_reports(tmp_path: Path) -> None:
    result = verify_hermes_behavior_matrix(output_dir=tmp_path)

    assert result["ok"] is True
    assert (tmp_path / "hermes_behavior_matrix_result.json").exists()
    assert (tmp_path / "hermes_behavior_matrix_report.md").exists()
