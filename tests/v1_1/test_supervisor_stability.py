from __future__ import annotations

from pathlib import Path

from tools.verify_supervisor_stability import verify_supervisor_stability


def test_supervisor_stability_records_progress_and_detection_guards(tmp_path: Path) -> None:
    result = verify_supervisor_stability(output_dir=tmp_path, cycles=3)

    assert result["ok"] is True
    assert result["heartbeat_count"] == result["expected_heartbeat_count"]
    assert result["completed_runs"] == 3
    assert result["ordered_progress_ok"] is True
    assert result["stuck_state_detected"] is True
    assert result["repeated_failure_detected"] is True
    assert result["invalid_transition_detected"] is True
    assert result["external_services_required"] is False
    assert result["destructive_action_taken"] is False
    assert (tmp_path / "supervisor_stability_result.json").exists()
    assert (tmp_path / "supervisor_stability_report.md").exists()
