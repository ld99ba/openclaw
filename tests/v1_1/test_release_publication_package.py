from __future__ import annotations

from pathlib import Path

from tools.build_v1_1_release_publication_package import build_release_publication_package


def approval_gate() -> dict:
    return {
        "ok": True,
        "approval_required": True,
        "approval_granted": False,
        "approval_phrase": "批准发布 V1.1 hardening 当前分支",
        "current_head": "abc123",
        "publication_actions_performed": False,
    }


def test_release_publication_package_builds_draft_without_publication(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(
        "tools.build_v1_1_release_publication_package.git_output",
        lambda args: {
            ("rev-list", "-n", "1", "ogk-final-v1.1"): "base123",
        }.get(tuple(args), ""),
    )
    monkeypatch.setattr(
        "tools.build_v1_1_release_publication_package.commit_log",
        lambda from_ref, to_ref: ["abc123 Add V1.1 phase 15 publication approval gate"],
    )

    result = build_release_publication_package(
        approval_gate_result=approval_gate(),
        output_dir=tmp_path,
        current_head="abc123",
        current_branch="codex/ogk-final-v1.1-hardening",
    )

    assert result["ok"] is True
    assert result["publication_package_ready"] is True
    assert result["approval_gate_head_matches_current_head"] is True
    assert result["release_publication_performed"] is False
    assert result["tag_move_performed"] is False
    assert result["pull_request_created"] is False
    assert (tmp_path / "RELEASE_NOTES_DRAFT.md").exists()
    assert (tmp_path / "release_publication_package_result.json").exists()
    assert (tmp_path / "release_publication_package_report.md").exists()


def test_release_publication_package_fails_when_approval_gate_failed(tmp_path: Path) -> None:
    gate = approval_gate()
    gate["ok"] = False

    result = build_release_publication_package(
        approval_gate_result=gate,
        output_dir=tmp_path,
        current_head="abc123",
        current_branch="codex/ogk-final-v1.1-hardening",
    )

    assert result["ok"] is False
    assert result["publication_package_ready"] is False
    assert "phase_15_approval_gate_not_ok" in result["failures"]
