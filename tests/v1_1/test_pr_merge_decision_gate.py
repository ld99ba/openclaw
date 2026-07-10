from __future__ import annotations

from pathlib import Path

from tools.verify_v1_1_pr_merge_decision_gate import (
    MERGE_APPROVAL_PHRASE,
    PR_APPROVAL_PHRASE,
    build_pr_merge_decision_gate,
)


def closure_result(ok: bool = True) -> dict:
    return {
        "schema": "ogk.v1_1.release_closure_packet.v1",
        "ok": ok,
        "release_point_fixed": ok,
        "release_tag": "ogk-final-v1.1-hardening",
        "release_url": "https://github.com/ld99ba/openclaw/releases/tag/ogk-final-v1.1-hardening",
        "release_tag_target": "release123",
        "existing_tag_unchanged": True,
        "tag_move_performed_on_existing_v1_1_tag": False,
        "pull_request_created": False,
        "destructive_action_taken": False,
        "files_moved_or_deleted": False,
    }


def test_pr_merge_decision_gate_recommends_pr_without_creating_it(tmp_path: Path) -> None:
    result = build_pr_merge_decision_gate(
        closure_result=closure_result(),
        output_dir=tmp_path,
        source_branch_head="head456",
        base_branch_head="main123",
        release_tag_is_ancestor_of_source=True,
        open_pull_requests=[],
    )

    assert result["ok"] is True
    assert result["release_tag_target_reachable_from_source_branch"] is True
    assert result["open_pull_request_count"] == 0
    assert result["pr_creation_recommended"] is True
    assert result["pr_creation_requires_owner_approval"] is True
    assert result["merge_requires_owner_approval"] is True
    assert result["pr_approval_phrase"] == PR_APPROVAL_PHRASE
    assert result["merge_approval_phrase"] == MERGE_APPROVAL_PHRASE
    assert result["pull_request_created"] is False
    assert result["merge_performed"] is False
    assert result["tag_move_performed"] is False
    assert result["release_mutation_performed"] is False
    assert (tmp_path / "pr_merge_decision_gate_result.json").exists()
    assert (tmp_path / "pr_merge_decision_gate_report.md").exists()
    assert (tmp_path / "PR_MERGE_DECISION_PACKET.md").exists()


def test_pr_merge_decision_gate_records_existing_open_pr(tmp_path: Path) -> None:
    result = build_pr_merge_decision_gate(
        closure_result=closure_result(),
        output_dir=tmp_path,
        source_branch_head="head456",
        base_branch_head="main123",
        release_tag_is_ancestor_of_source=True,
        open_pull_requests=[
            {
                "number": 7,
                "url": "https://github.com/ld99ba/openclaw/pull/7",
                "title": "V1.1 hardening",
                "isDraft": False,
            }
        ],
    )

    assert result["ok"] is True
    assert result["open_pull_request_count"] == 1
    assert result["pr_creation_recommended"] is False
    assert result["pull_request_created"] is False


def test_pr_merge_decision_gate_fails_when_closure_failed(tmp_path: Path) -> None:
    result = build_pr_merge_decision_gate(
        closure_result=closure_result(ok=False),
        output_dir=tmp_path,
        source_branch_head="head456",
        base_branch_head="main123",
        release_tag_is_ancestor_of_source=True,
        open_pull_requests=[],
    )

    assert result["ok"] is False
    assert "phase_20_release_closure_not_ok" in result["failures"]
    assert "phase_20_release_point_not_fixed" in result["failures"]


def test_pr_merge_decision_gate_fails_when_release_tag_not_reachable(tmp_path: Path) -> None:
    result = build_pr_merge_decision_gate(
        closure_result=closure_result(),
        output_dir=tmp_path,
        source_branch_head="head456",
        base_branch_head="main123",
        release_tag_is_ancestor_of_source=False,
        open_pull_requests=[],
    )

    assert result["ok"] is False
    assert "release_tag_target_not_reachable_from_source_branch" in result["failures"]
