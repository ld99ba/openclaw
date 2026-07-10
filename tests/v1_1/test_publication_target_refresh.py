from __future__ import annotations

from pathlib import Path

from tools.verify_v1_1_publication_target_refresh import build_publication_target_refresh


def publication_package() -> dict:
    return {
        "ok": True,
        "publication_package_ready": True,
        "existing_tag_target": "tag123",
        "target_head": "phase16head",
        "approval_phrase": "批准发布 V1.1 hardening 当前分支",
        "release_publication_performed": False,
        "tag_move_performed": False,
    }


def test_publication_target_refresh_records_remote_branch_ref(tmp_path: Path) -> None:
    result = build_publication_target_refresh(
        package_result=publication_package(),
        output_dir=tmp_path,
        current_head="head123",
        current_branch="codex/ogk-final-v1.1-hardening",
        remote_head="head123",
        existing_tag_target="tag123",
    )

    assert result["ok"] is True
    assert result["publication_target_ref"] == "origin/codex/ogk-final-v1.1-hardening"
    assert result["remote_head_matches_current_head"] is True
    assert result["existing_tag_target_matches_phase_16"] is True
    assert result["branch_ref_is_publication_target"] is True
    assert result["snapshot_head_is_observational"] is True
    assert result["release_publication_performed"] is False
    assert result["tag_move_performed"] is False
    assert (tmp_path / "publication_target_refresh_result.json").exists()
    assert (tmp_path / "publication_target_refresh_report.md").exists()


def test_publication_target_refresh_fails_on_remote_drift(tmp_path: Path) -> None:
    result = build_publication_target_refresh(
        package_result=publication_package(),
        output_dir=tmp_path,
        current_head="head123",
        current_branch="codex/ogk-final-v1.1-hardening",
        remote_head="other456",
        existing_tag_target="tag123",
    )

    assert result["ok"] is False
    assert "remote_branch_head_does_not_match_current_head" in result["failures"]


def test_publication_target_refresh_fails_on_tag_drift(tmp_path: Path) -> None:
    result = build_publication_target_refresh(
        package_result=publication_package(),
        output_dir=tmp_path,
        current_head="head123",
        current_branch="codex/ogk-final-v1.1-hardening",
        remote_head="head123",
        existing_tag_target="tag456",
    )

    assert result["ok"] is False
    assert "existing_tag_target_changed_since_phase_16" in result["failures"]
