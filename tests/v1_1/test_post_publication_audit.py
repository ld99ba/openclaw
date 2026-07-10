from __future__ import annotations

from pathlib import Path

from tools.verify_v1_1_post_publication_audit import (
    build_post_publication_audit,
    remote_tag_target,
)


def execution_packet(ok: bool = True) -> dict:
    return {
        "schema": "ogk.v1_1.release_execution_packet.v1",
        "ok": ok,
        "execution_packet_ready": ok,
        "existing_tag_target": "oldtag123",
    }


def release_info() -> dict:
    return {
        "tagName": "ogk-final-v1.1-hardening",
        "url": "https://github.com/ld99ba/openclaw/releases/tag/ogk-final-v1.1-hardening",
        "isDraft": False,
        "isPrerelease": False,
        "targetCommitish": "main",
        "publishedAt": "2026-07-09T15:57:12Z",
        "name": "OGK-Final-V1.1-Hardening",
    }


def test_remote_tag_target_prefers_dereferenced_annotated_tag() -> None:
    output = "\n".join(
        [
            "tagobject refs/tags/ogk-final-v1.1",
            "committarget refs/tags/ogk-final-v1.1^{}",
        ]
    )

    assert remote_tag_target("ogk-final-v1.1", output=output) == "committarget"


def test_post_publication_audit_records_published_release(tmp_path: Path) -> None:
    result = build_post_publication_audit(
        execution_packet_result=execution_packet(),
        output_dir=tmp_path,
        release_info=release_info(),
        release_tag_target="head123",
        existing_tag_target="oldtag123",
        branch_head="head123",
    )

    assert result["ok"] is True
    assert result["release_publication_performed"] is True
    assert result["release_tag_target_matches_target_branch_head"] is True
    assert result["release_tag_target_is_target_branch_ancestor"] is True
    assert result["existing_tag_unchanged"] is True
    assert result["tag_move_performed_on_existing_v1_1_tag"] is False
    assert result["pull_request_created"] is False
    assert (tmp_path / "post_publication_audit_result.json").exists()
    assert (tmp_path / "post_publication_audit_report.md").exists()


def test_post_publication_audit_accepts_release_tag_ancestor_after_audit_commit(tmp_path: Path) -> None:
    result = build_post_publication_audit(
        execution_packet_result=execution_packet(),
        output_dir=tmp_path,
        release_info=release_info(),
        release_tag_target="release123",
        release_tag_is_ancestor_of_branch=True,
        existing_tag_target="oldtag123",
        branch_head="auditcommit456",
    )

    assert result["ok"] is True
    assert result["release_tag_target_matches_target_branch_head"] is False
    assert result["release_tag_target_is_target_branch_ancestor"] is True
    assert "release_tag_target_not_reachable_from_hardening_branch" not in result["failures"]


def test_post_publication_audit_fails_when_release_missing(tmp_path: Path) -> None:
    result = build_post_publication_audit(
        execution_packet_result=execution_packet(),
        output_dir=tmp_path,
        release_info={},
        release_tag_target="head123",
        existing_tag_target="oldtag123",
        branch_head="head123",
    )

    assert result["ok"] is False
    assert "github_release_missing" in result["failures"]


def test_post_publication_audit_fails_when_existing_tag_changed(tmp_path: Path) -> None:
    result = build_post_publication_audit(
        execution_packet_result=execution_packet(),
        output_dir=tmp_path,
        release_info=release_info(),
        release_tag_target="head123",
        existing_tag_target="changed456",
        branch_head="head123",
    )

    assert result["ok"] is False
    assert "existing_v1_1_tag_target_changed" in result["failures"]
