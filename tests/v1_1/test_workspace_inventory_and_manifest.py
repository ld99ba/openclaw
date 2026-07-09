from __future__ import annotations

from pathlib import Path

from tools.classify_v1_1_workspace_inventory import build_workspace_inventory, classify_path
from tools.verify_v1_1_manifest_dry_run import verify_v1_1_manifest_dry_run


def test_workspace_inventory_classifies_key_v1_1_and_baseline_paths() -> None:
    assert classify_path("tests/v1_1/test_recovery_boundaries.py") == "v1_1_release_candidate"
    assert classify_path("reports/v1_1/phase_02/PHASE_02_SUMMARY.md") == "v1_1_release_candidate"
    assert classify_path("reports/final/current_state.json") == "v1_0_baseline_preserve"
    assert classify_path("main/package.json") == "nested_repo_boundary"
    assert classify_path("tests/v1_1/__pycache__/x.pyc") == "generated_cache"


def test_workspace_inventory_writes_reports_without_destructive_action(tmp_path: Path) -> None:
    result = build_workspace_inventory(output_dir=tmp_path)

    assert result["ok"] is True
    assert result["destructive_action_taken"] is False
    assert "main_boundary" in result
    assert (tmp_path / "workspace_inventory_result.json").exists()
    assert (tmp_path / "workspace_inventory_report.md").exists()


def test_manifest_dry_run_excludes_v1_0_and_nested_repo_boundaries(tmp_path: Path) -> None:
    result = verify_v1_1_manifest_dry_run(output_dir=tmp_path)

    assert result["ok"] is True
    assert result["missing"] == []
    assert result["forbidden"] == []
    assert result["git_stage_executed"] is False
    assert result["git_add_dot_used"] is False
    assert all(not path.startswith("reports/final/") for path in result["manifest"])
    assert all(not path.startswith("main/") for path in result["manifest"])
    assert (tmp_path / "manifest_dry_run_result.json").exists()
    assert (tmp_path / "manifest_dry_run_report.md").exists()
