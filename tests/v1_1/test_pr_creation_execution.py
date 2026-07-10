from __future__ import annotations

from pathlib import Path

from tools.record_v1_1_pr_creation_execution import (
    EXPECTED_EXISTING_V1_1_TAG_REF,
    EXPECTED_EXISTING_V1_1_TAG_TARGET,
    EXPECTED_HARDENING_TAG_TARGET,
    INTEGRATION_BRANCH,
    MERGE_APPROVAL_PHRASE,
    PR_APPROVAL_PHRASE,
    build_pr_creation_execution,
)


def pr_fixture(state: str = "OPEN") -> dict:
    return {
        "number": 1,
        "url": "https://github.com/ld99ba/openclaw/pull/1",
        "title": "OGK Final V1.1 hardening",
        "headRefName": INTEGRATION_BRANCH,
        "baseRefName": "main",
        "state": state,
        "isDraft": False,
        "mergeable": "MERGEABLE",
    }


def test_pr_creation_execution_records_created_pr_without_merge(tmp_path: Path) -> None:
    result = build_pr_creation_execution(
        output_dir=tmp_path,
        pr=pr_fixture(),
        source_branch_head="source123",
        integration_branch_head="integration456",
        base_branch_head="main789",
        existing_v1_1_tag_ref=EXPECTED_EXISTING_V1_1_TAG_REF,
        existing_v1_1_tag_target=EXPECTED_EXISTING_V1_1_TAG_TARGET,
        hardening_tag_target=EXPECTED_HARDENING_TAG_TARGET,
    )

    assert result["ok"] is True
    assert result["approval_phrase"] == PR_APPROVAL_PHRASE
    assert result["direct_pr_attempted"] is True
    assert result["direct_pr_attempt_failed"] is True
    assert result["direct_pr_failure_reason"] == "no_common_history"
    assert result["integration_branch_based_on_main"] is True
    assert result["pull_request_created"] is True
    assert result["pull_request_url"] == "https://github.com/ld99ba/openclaw/pull/1"
    assert result["pull_request_state"] == "OPEN"
    assert result["pull_request_mergeable"] == "MERGEABLE"
    assert result["pytest_status"] == "101 passed"
    assert result["final_acceptance_ok"] is True
    assert result["existing_v1_1_tag_unchanged"] is True
    assert result["hardening_release_tag_unchanged"] is True
    assert result["merge_requires_owner_approval"] is True
    assert result["merge_approval_phrase"] == MERGE_APPROVAL_PHRASE
    assert result["merge_performed"] is False
    assert result["tag_move_performed"] is False
    assert result["release_mutation_performed"] is False
    assert (tmp_path / "pr_creation_execution_result.json").exists()
    assert (tmp_path / "pr_creation_execution_report.md").exists()
    assert (tmp_path / "PR_CREATION_EXECUTION_PACKET.md").exists()
    assert (tmp_path / "PHASE_22_SUMMARY.md").exists()


def test_pr_creation_execution_fails_without_exact_creation_approval(tmp_path: Path) -> None:
    result = build_pr_creation_execution(
        output_dir=tmp_path,
        pr=pr_fixture(),
        source_branch_head="source123",
        integration_branch_head="integration456",
        base_branch_head="main789",
        existing_v1_1_tag_ref=EXPECTED_EXISTING_V1_1_TAG_REF,
        existing_v1_1_tag_target=EXPECTED_EXISTING_V1_1_TAG_TARGET,
        hardening_tag_target=EXPECTED_HARDENING_TAG_TARGET,
        approval_phrase="继续下一步",
    )

    assert result["ok"] is False
    assert "pr_creation_approval_phrase_missing" in result["failures"]


def test_pr_creation_execution_fails_when_pr_is_not_open(tmp_path: Path) -> None:
    result = build_pr_creation_execution(
        output_dir=tmp_path,
        pr=pr_fixture(state="CLOSED"),
        source_branch_head="source123",
        integration_branch_head="integration456",
        base_branch_head="main789",
        existing_v1_1_tag_ref=EXPECTED_EXISTING_V1_1_TAG_REF,
        existing_v1_1_tag_target=EXPECTED_EXISTING_V1_1_TAG_TARGET,
        hardening_tag_target=EXPECTED_HARDENING_TAG_TARGET,
    )

    assert result["ok"] is False
    assert "pull_request_not_open" in result["failures"]


def test_pr_creation_execution_fails_when_tags_changed(tmp_path: Path) -> None:
    result = build_pr_creation_execution(
        output_dir=tmp_path,
        pr=pr_fixture(),
        source_branch_head="source123",
        integration_branch_head="integration456",
        base_branch_head="main789",
        existing_v1_1_tag_ref="moved",
        existing_v1_1_tag_target=EXPECTED_EXISTING_V1_1_TAG_TARGET,
        hardening_tag_target="moved",
    )

    assert result["ok"] is False
    assert "existing_v1_1_tag_changed" in result["failures"]
    assert "hardening_release_tag_changed" in result["failures"]
