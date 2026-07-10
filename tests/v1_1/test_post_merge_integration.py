from __future__ import annotations

from pathlib import Path

from tools.record_v1_1_post_merge_integration import (
    EXPECTED_EXISTING_V1_1_TAG_REF,
    EXPECTED_EXISTING_V1_1_TAG_TARGET,
    EXPECTED_HARDENING_TAG_TARGET,
    EXPECTED_MERGE_COMMIT,
    EXPECTED_POST_MERGE_MANIFEST_COUNT,
    EXPECTED_POST_MERGE_PYTEST_STATUS,
    FOLLOW_UP_BRANCH,
    FOLLOW_UP_PR_APPROVAL_PHRASE,
    MERGE_APPROVAL_PHRASE,
    build_post_merge_integration,
)


def pr_fixture(state: str = "MERGED", merge_commit: str = EXPECTED_MERGE_COMMIT) -> dict:
    return {
        "number": 1,
        "url": "https://github.com/ld99ba/openclaw/pull/1",
        "title": "OGK Final V1.1 hardening",
        "headRefName": "codex/ogk-final-v1.1-hardening-pr",
        "baseRefName": "main",
        "state": state,
        "isDraft": False,
        "mergedAt": "2026-07-10T14:53:29Z",
        "mergeCommit": {"oid": merge_commit},
    }


def test_post_merge_integration_records_merged_pr_and_main_validation(tmp_path: Path) -> None:
    result = build_post_merge_integration(
        output_dir=tmp_path,
        pr=pr_fixture(),
        main_head=EXPECTED_MERGE_COMMIT,
        follow_up_branch=FOLLOW_UP_BRANCH,
        follow_up_branch_head=EXPECTED_MERGE_COMMIT,
        existing_v1_1_tag_ref=EXPECTED_EXISTING_V1_1_TAG_REF,
        existing_v1_1_tag_target=EXPECTED_EXISTING_V1_1_TAG_TARGET,
        hardening_tag_target=EXPECTED_HARDENING_TAG_TARGET,
        main_tracked_paths=["openclaw/policies/policy.json"],
    )

    assert result["ok"] is True
    assert result["approval_phrase"] == MERGE_APPROVAL_PHRASE
    assert result["pull_request_merged"] is True
    assert result["pull_request_state"] == "MERGED"
    assert result["merge_commit"] == EXPECTED_MERGE_COMMIT
    assert result["origin_main_matches_merge_commit"] is True
    assert result["post_merge_pytest_status"] == EXPECTED_POST_MERGE_PYTEST_STATUS
    assert result["post_merge_final_acceptance_ok"] is True
    assert result["post_merge_manifest_ok"] is True
    assert result["post_merge_manifest_count"] == EXPECTED_POST_MERGE_MANIFEST_COUNT
    assert result["root_policy_shadow_absent_from_main"] is True
    assert result["existing_v1_1_tag_unchanged"] is True
    assert result["hardening_release_tag_unchanged"] is True
    assert result["follow_up_pr_created"] is False
    assert result["follow_up_pr_creation_requires_owner_approval"] is True
    assert result["follow_up_pr_approval_phrase"] == FOLLOW_UP_PR_APPROVAL_PHRASE
    assert (tmp_path / "post_merge_integration_result.json").exists()
    assert (tmp_path / "post_merge_integration_report.md").exists()
    assert (tmp_path / "POST_MERGE_INTEGRATION_PACKET.md").exists()
    assert (tmp_path / "PHASE_23_SUMMARY.md").exists()


def test_post_merge_integration_fails_without_exact_merge_approval(tmp_path: Path) -> None:
    result = build_post_merge_integration(
        output_dir=tmp_path,
        pr=pr_fixture(),
        main_head=EXPECTED_MERGE_COMMIT,
        follow_up_branch=FOLLOW_UP_BRANCH,
        follow_up_branch_head=EXPECTED_MERGE_COMMIT,
        existing_v1_1_tag_ref=EXPECTED_EXISTING_V1_1_TAG_REF,
        existing_v1_1_tag_target=EXPECTED_EXISTING_V1_1_TAG_TARGET,
        hardening_tag_target=EXPECTED_HARDENING_TAG_TARGET,
        main_tracked_paths=[],
        approval_phrase="继续下一步",
    )

    assert result["ok"] is False
    assert "merge_approval_phrase_missing" in result["failures"]


def test_post_merge_integration_fails_when_pr_not_merged(tmp_path: Path) -> None:
    result = build_post_merge_integration(
        output_dir=tmp_path,
        pr=pr_fixture(state="OPEN"),
        main_head=EXPECTED_MERGE_COMMIT,
        follow_up_branch=FOLLOW_UP_BRANCH,
        follow_up_branch_head=EXPECTED_MERGE_COMMIT,
        existing_v1_1_tag_ref=EXPECTED_EXISTING_V1_1_TAG_REF,
        existing_v1_1_tag_target=EXPECTED_EXISTING_V1_1_TAG_TARGET,
        hardening_tag_target=EXPECTED_HARDENING_TAG_TARGET,
        main_tracked_paths=[],
    )

    assert result["ok"] is False
    assert "pull_request_not_merged" in result["failures"]


def test_post_merge_integration_fails_when_main_or_tags_changed(tmp_path: Path) -> None:
    result = build_post_merge_integration(
        output_dir=tmp_path,
        pr=pr_fixture(merge_commit=EXPECTED_MERGE_COMMIT),
        main_head="different",
        follow_up_branch=FOLLOW_UP_BRANCH,
        follow_up_branch_head=EXPECTED_MERGE_COMMIT,
        existing_v1_1_tag_ref="moved",
        existing_v1_1_tag_target=EXPECTED_EXISTING_V1_1_TAG_TARGET,
        hardening_tag_target="moved",
        main_tracked_paths=["policies/policy.json"],
    )

    assert result["ok"] is False
    assert "origin_main_not_at_merge_commit" in result["failures"]
    assert "existing_v1_1_tag_changed" in result["failures"]
    assert "hardening_release_tag_changed" in result["failures"]
    assert "root_policy_shadow_present_in_main" in result["failures"]
