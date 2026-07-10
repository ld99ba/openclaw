from __future__ import annotations

from pathlib import Path

from tools.verify_v1_1_release_publication_approval_gate import (
    APPROVAL_PHRASE,
    build_release_publication_approval_gate,
)


def readiness(ok: bool = True) -> dict:
    return {
        "schema": "ogk.v1_1.release_readiness_gate.v1",
        "ok": ok,
        "failure_count": 0 if ok else 1,
        "root_policy_shadow_count": 6,
        "tracked_root_policy_shadows": [],
        "release_publication_performed": False,
        "tag_move_performed": False,
    }


def test_release_publication_approval_gate_records_required_phrase(tmp_path: Path) -> None:
    result = build_release_publication_approval_gate(
        readiness_result=readiness(),
        output_dir=tmp_path,
        current_head="abc123",
        current_branch="codex/ogk-final-v1.1-hardening",
    )

    assert result["ok"] is True
    assert result["approval_required"] is True
    assert result["approval_granted"] is False
    assert result["approval_phrase"] == APPROVAL_PHRASE
    assert result["publication_actions_performed"] is False
    assert result["release_publication_performed"] is False
    assert result["tag_move_performed"] is False
    assert result["tag_move_requires_separate_approval"] is True
    assert (tmp_path / "release_publication_approval_gate_result.json").exists()
    assert (tmp_path / "release_publication_approval_gate_report.md").exists()


def test_release_publication_approval_gate_fails_when_readiness_failed(tmp_path: Path) -> None:
    result = build_release_publication_approval_gate(
        readiness_result=readiness(ok=False),
        output_dir=tmp_path,
        current_head="abc123",
        current_branch="codex/ogk-final-v1.1-hardening",
    )

    assert result["ok"] is False
    assert result["approval_required"] is True
    assert result["approval_granted"] is False
    assert "phase_14_release_readiness_not_ok" in result["failures"]
