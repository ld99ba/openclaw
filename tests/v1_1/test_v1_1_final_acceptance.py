from __future__ import annotations

import json
from pathlib import Path

from tools.verify_v1_1_final_acceptance import verify_v1_1_final_acceptance


def _write_json(path: Path, ok: bool = True) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"ok": ok}), encoding="utf-8")


def _write_summary(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("# Summary\n\nStatus: PASS\n", encoding="utf-8")


def test_v1_1_final_acceptance_fails_closed_when_evidence_is_missing(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "reports/v1_1/phase_01").mkdir(parents=True)

    result = verify_v1_1_final_acceptance(output_dir=tmp_path / "out", check_github_release=False)

    assert result["ok"] is False
    assert result["final_status"] == "FINAL_SEAL_FAILED"
    assert result["release_status"] == "PENDING"
    assert result["derived_from_evidence"] is True
    assert result["manual_final_status_written"] is False


def test_v1_1_final_acceptance_derives_success_from_evidence(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    _write_summary(Path("reports/v1_1/phase_01/PHASE_01_SUMMARY.md"))
    _write_summary(Path("reports/v1_1/phase_02/PHASE_02_SUMMARY.md"))
    _write_summary(Path("reports/v1_1/phase_03/PHASE_03_SUMMARY.md"))
    for path in [
        "reports/v1_1/phase_01/artifact_hash_result.json",
        "reports/v1_1/phase_01/eventledger_replay_result.json",
        "reports/v1_1/phase_02/hermes_behavior_matrix_result.json",
        "reports/v1_1/phase_02/memory_skill_lifecycle_result.json",
        "reports/v1_1/phase_02/recovery_boundaries_result.json",
        "reports/v1_1/phase_03/manifest_dry_run_result.json",
        "reports/v1_1/phase_03/workspace_inventory_result.json",
        "reports/v1_1/phase_04/main_governance_result.json",
        "reports/v1_1/phase_04/supervisor_stability_result.json",
    ]:
        _write_json(Path(path))

    monkeypatch.setattr("tools.verify_v1_1_final_acceptance._git_output", lambda args: "abc123")

    result = verify_v1_1_final_acceptance(output_dir=tmp_path / "out", check_github_release=False)

    assert result["ok"] is True
    assert result["final_status"] == "FINAL_SUCCESS"
    assert result["release_status"] == "RELEASE_ACCEPTED"
    assert result["phase_04_summary_pending"] is True
    assert result["local_tag_present"] is True
    assert result["github_release_present"] is True
    assert result["derived_from_evidence"] is True
