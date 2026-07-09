from __future__ import annotations

from pathlib import Path

from tools.build_v1_1_release_closure_packet import build_release_closure_packet


def audit_result(ok: bool = True) -> dict:
    return {
        "schema": "ogk.v1_1.post_publication_audit.v1",
        "ok": ok,
        "release_publication_performed": True,
        "release_tag": "ogk-final-v1.1-hardening",
        "release_url": "https://github.com/ld99ba/openclaw/releases/tag/ogk-final-v1.1-hardening",
        "release_tag_target": "release123",
        "target_branch_head": "audit456",
        "release_tag_target_matches_target_branch_head": False,
        "release_tag_target_is_target_branch_ancestor": True,
        "existing_tag": "ogk-final-v1.1",
        "existing_tag_target": "oldtag123",
        "expected_existing_tag_target": "oldtag123",
        "existing_tag_unchanged": True,
        "tag_move_performed_on_existing_v1_1_tag": False,
        "pull_request_created": False,
        "destructive_action_taken": False,
        "files_moved_or_deleted": False,
    }


def test_release_closure_packet_accepts_fixed_release_point_on_branch_history(tmp_path: Path) -> None:
    result = build_release_closure_packet(
        audit_result=audit_result(),
        output_dir=tmp_path,
        current_branch_head="audit456",
        release_tag_target="release123",
        release_tag_is_ancestor_of_branch=True,
    )

    assert result["ok"] is True
    assert result["release_publication_performed"] is True
    assert result["release_tag_target_matches_current_branch_head"] is False
    assert result["release_tag_target_is_current_branch_ancestor"] is True
    assert result["branch_continues_after_release"] is True
    assert result["release_point_fixed"] is True
    assert result["existing_tag_unchanged"] is True
    assert result["pull_request_created"] is False
    assert (tmp_path / "release_closure_packet_result.json").exists()
    assert (tmp_path / "release_closure_packet_report.md").exists()
    assert (tmp_path / "RELEASE_CLOSURE_PACKET.md").exists()


def test_release_closure_packet_fails_when_phase_19_failed(tmp_path: Path) -> None:
    result = build_release_closure_packet(
        audit_result=audit_result(ok=False),
        output_dir=tmp_path,
        current_branch_head="audit456",
        release_tag_target="release123",
        release_tag_is_ancestor_of_branch=True,
    )

    assert result["ok"] is False
    assert "phase_19_post_publication_audit_not_ok" in result["failures"]


def test_release_closure_packet_fails_when_existing_tag_not_unchanged(tmp_path: Path) -> None:
    audit = audit_result()
    audit["existing_tag_unchanged"] = False

    result = build_release_closure_packet(
        audit_result=audit,
        output_dir=tmp_path,
        current_branch_head="audit456",
        release_tag_target="release123",
        release_tag_is_ancestor_of_branch=True,
    )

    assert result["ok"] is False
    assert "existing_v1_1_tag_not_confirmed_unchanged" in result["failures"]
