from __future__ import annotations

from pathlib import Path

from tools.build_v1_1_release_execution_packet import build_release_execution_packet


def refresh_result(ok: bool = True) -> dict:
    return {
        "ok": ok,
        "existing_tag_target": "tag123",
        "release_publication_performed": False,
        "tag_move_performed": False,
    }


def test_release_execution_packet_records_documentation_only_commands(tmp_path: Path) -> None:
    result = build_release_execution_packet(
        refresh_result=refresh_result(),
        output_dir=tmp_path,
        current_head="head123",
        current_branch="codex/ogk-final-v1.1-hardening",
        remote_head="head123",
        existing_tag_target="tag123",
    )

    assert result["ok"] is True
    assert result["execution_packet_ready"] is True
    assert result["approval_required_before_publication"] is True
    assert result["approval_granted"] is False
    assert result["release_commands_are_documentation_only"] is True
    assert result["release_publication_performed"] is False
    assert result["tag_move_performed"] is False
    assert result["pull_request_created"] is False
    assert "create_or_update_github_release" in result["guarded_actions"]
    assert (tmp_path / "RELEASE_EXECUTION_PACKET.md").exists()
    assert (tmp_path / "release_execution_packet_result.json").exists()
    assert (tmp_path / "release_execution_packet_report.md").exists()


def test_release_execution_packet_fails_when_phase_17_failed(tmp_path: Path) -> None:
    result = build_release_execution_packet(
        refresh_result=refresh_result(ok=False),
        output_dir=tmp_path,
        current_head="head123",
        current_branch="codex/ogk-final-v1.1-hardening",
        remote_head="head123",
        existing_tag_target="tag123",
    )

    assert result["ok"] is False
    assert "phase_17_publication_target_refresh_not_ok" in result["failures"]


def test_release_execution_packet_fails_on_tag_drift(tmp_path: Path) -> None:
    result = build_release_execution_packet(
        refresh_result=refresh_result(),
        output_dir=tmp_path,
        current_head="head123",
        current_branch="codex/ogk-final-v1.1-hardening",
        remote_head="head123",
        existing_tag_target="tag456",
    )

    assert result["ok"] is False
    assert "existing_tag_target_changed_since_phase_17" in result["failures"]
