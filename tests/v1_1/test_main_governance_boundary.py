from __future__ import annotations

from pathlib import Path

from tools.verify_main_governance_boundary import verify_main_governance_boundary


def test_main_governance_boundary_keeps_nested_repo_out_of_manifest(tmp_path: Path) -> None:
    result = verify_main_governance_boundary(output_dir=tmp_path)

    assert result["ok"] is True
    assert result["decision"] == "continue_excluding_main"
    assert result["manifest_includes_main"] is False
    assert result["main_manifest_paths"] == []
    assert result["explicit_approval_required_for_future_inclusion"] is True
    assert result["destructive_action_taken"] is False
    assert (tmp_path / "main_governance_result.json").exists()
    assert (tmp_path / "main_governance_adr.md").exists()
