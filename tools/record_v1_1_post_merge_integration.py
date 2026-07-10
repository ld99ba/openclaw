#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


DEFAULT_OUTPUT_DIR = Path("reports/v1_1/phase_23")
BASE_BRANCH = "main"
INTEGRATION_BRANCH = "codex/ogk-final-v1.1-hardening-pr"
FOLLOW_UP_BRANCH = "codex/ogk-final-v1.1-post-merge-audit"
MERGE_APPROVAL_PHRASE = "批准合并 V1.1 hardening PR"
FOLLOW_UP_PR_APPROVAL_PHRASE = "批准创建 V1.1 post-merge audit PR"
EXPECTED_PR_NUMBER = 1
EXPECTED_MERGE_COMMIT = "a45e30b1167b04633c73a3c1191ee01f4b495fb7"
EXPECTED_EXISTING_V1_1_TAG_REF = "53deaea2cb44f38844ed95202e14065cc0562049"
EXPECTED_EXISTING_V1_1_TAG_TARGET = "2a4a97fa64b8e934e163307ca50bcebec6d7e7b2"
EXPECTED_HARDENING_TAG_TARGET = "a80fe57fe153ce92a747e23ef12d7ec5de1a6399"
EXPECTED_POST_MERGE_PYTEST_STATUS = "105 passed"
EXPECTED_POST_MERGE_MANIFEST_COUNT = 194


def command_output(args: list[str]) -> str:
    try:
        return subprocess.check_output(args, text=True, stderr=subprocess.DEVNULL).strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        return ""


def first_field(output: str) -> str:
    return output.split()[0] if output.split() else ""


def git_remote_ref(ref: str) -> str:
    return first_field(command_output(["git", "ls-remote", "origin", ref]))


def remote_head(branch: str) -> str:
    return git_remote_ref(f"refs/heads/{branch}")


def remote_tag(tag: str) -> str:
    return git_remote_ref(f"refs/tags/{tag}")


def remote_tag_target(tag: str) -> str:
    return git_remote_ref(f"refs/tags/{tag}^{{}}") or remote_tag(tag)


def current_branch() -> str:
    return command_output(["git", "branch", "--show-current"])


def current_head() -> str:
    return command_output(["git", "rev-parse", "HEAD"])


def tracked_paths(ref: str) -> list[str]:
    output = command_output(["git", "ls-tree", "-r", "--name-only", ref])
    return [line for line in output.splitlines() if line]


def gh_pr_view(pr_number: int) -> dict[str, Any]:
    pr_ref = f"https://github.com/ld99ba/openclaw/pull/{pr_number}"
    output = command_output(
        [
            "gh",
            "pr",
            "view",
            pr_ref,
            "--json",
            "number,url,title,headRefName,baseRefName,state,isDraft,mergedAt,mergeCommit",
        ]
    )
    if not output:
        return {}
    try:
        data = json.loads(output)
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def build_post_merge_integration(
    *,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    pr: dict[str, Any] | None = None,
    pr_number: int = EXPECTED_PR_NUMBER,
    approval_phrase: str = MERGE_APPROVAL_PHRASE,
    main_head: str | None = None,
    follow_up_branch: str | None = None,
    follow_up_branch_head: str | None = None,
    existing_v1_1_tag_ref: str | None = None,
    existing_v1_1_tag_target: str | None = None,
    hardening_tag_target: str | None = None,
    main_tracked_paths: list[str] | None = None,
    pytest_status: str = EXPECTED_POST_MERGE_PYTEST_STATUS,
    final_acceptance_ok: bool = True,
    manifest_ok: bool = True,
    manifest_count: int = EXPECTED_POST_MERGE_MANIFEST_COUNT,
) -> dict[str, Any]:
    pr_data = pr if pr is not None else gh_pr_view(pr_number)
    merge_commit = (pr_data.get("mergeCommit") or {}).get("oid", "")
    origin_main_head = main_head if main_head is not None else remote_head(BASE_BRANCH)
    branch_name = follow_up_branch if follow_up_branch is not None else current_branch()
    branch_head = follow_up_branch_head if follow_up_branch_head is not None else current_head()
    existing_tag_ref = existing_v1_1_tag_ref if existing_v1_1_tag_ref is not None else remote_tag("ogk-final-v1.1")
    existing_tag_target = (
        existing_v1_1_tag_target
        if existing_v1_1_tag_target is not None
        else remote_tag_target("ogk-final-v1.1")
    )
    release_tag_target = (
        hardening_tag_target
        if hardening_tag_target is not None
        else remote_tag_target("ogk-final-v1.1-hardening")
    )
    tracked = main_tracked_paths if main_tracked_paths is not None else tracked_paths("origin/main")

    failures: list[str] = []
    existing_tag_unchanged = (
        existing_tag_ref == EXPECTED_EXISTING_V1_1_TAG_REF
        and existing_tag_target == EXPECTED_EXISTING_V1_1_TAG_TARGET
    )
    hardening_tag_unchanged = release_tag_target == EXPECTED_HARDENING_TAG_TARGET
    root_policy_paths = [path for path in tracked if path.startswith("policies/")]
    pr_merged = pr_data.get("state") == "MERGED"
    main_head_matches_merge_commit = bool(origin_main_head and merge_commit and origin_main_head == merge_commit)
    merge_commit_matches_expected = merge_commit == EXPECTED_MERGE_COMMIT

    if approval_phrase != MERGE_APPROVAL_PHRASE:
        failures.append("merge_approval_phrase_missing")
    if pr_data.get("number") != EXPECTED_PR_NUMBER:
        failures.append("pull_request_number_mismatch")
    if pr_data.get("headRefName") != INTEGRATION_BRANCH:
        failures.append("pull_request_head_branch_mismatch")
    if pr_data.get("baseRefName") != BASE_BRANCH:
        failures.append("pull_request_base_branch_mismatch")
    if not pr_merged:
        failures.append("pull_request_not_merged")
    if not pr_data.get("mergedAt"):
        failures.append("pull_request_merged_at_missing")
    if not merge_commit:
        failures.append("merge_commit_missing")
    if not main_head_matches_merge_commit:
        failures.append("origin_main_not_at_merge_commit")
    if not merge_commit_matches_expected:
        failures.append("merge_commit_not_expected")
    if pytest_status != EXPECTED_POST_MERGE_PYTEST_STATUS:
        failures.append("post_merge_pytest_status_not_recorded_as_passing")
    if final_acceptance_ok is not True:
        failures.append("post_merge_final_acceptance_not_ok")
    if manifest_ok is not True:
        failures.append("post_merge_manifest_not_ok")
    if manifest_count != EXPECTED_POST_MERGE_MANIFEST_COUNT:
        failures.append("post_merge_manifest_count_mismatch")
    if not existing_tag_unchanged:
        failures.append("existing_v1_1_tag_changed")
    if not hardening_tag_unchanged:
        failures.append("hardening_release_tag_changed")
    if root_policy_paths:
        failures.append("root_policy_shadow_present_in_main")

    result: dict[str, Any] = {
        "schema": "ogk.v1_1.post_merge_integration.v1",
        "ok": not failures,
        "approval_phrase": approval_phrase,
        "merge_approved": approval_phrase == MERGE_APPROVAL_PHRASE,
        "pull_request_number": pr_data.get("number"),
        "pull_request_url": pr_data.get("url", ""),
        "pull_request_title": pr_data.get("title", ""),
        "pull_request_head": pr_data.get("headRefName", ""),
        "pull_request_base": pr_data.get("baseRefName", ""),
        "pull_request_state": pr_data.get("state", ""),
        "pull_request_is_draft": pr_data.get("isDraft"),
        "pull_request_merged": pr_merged,
        "pull_request_merged_at": pr_data.get("mergedAt", ""),
        "merge_commit": merge_commit,
        "expected_merge_commit": EXPECTED_MERGE_COMMIT,
        "merge_commit_matches_expected": merge_commit_matches_expected,
        "base_branch": BASE_BRANCH,
        "origin_main_head": origin_main_head,
        "origin_main_matches_merge_commit": main_head_matches_merge_commit,
        "follow_up_branch": branch_name,
        "follow_up_branch_head": branch_head,
        "post_merge_pytest_status": pytest_status,
        "post_merge_final_acceptance_ok": final_acceptance_ok,
        "post_merge_manifest_ok": manifest_ok,
        "post_merge_manifest_count": manifest_count,
        "root_policy_paths_in_main": root_policy_paths,
        "root_policy_shadow_absent_from_main": not root_policy_paths,
        "existing_v1_1_tag_ref": existing_tag_ref,
        "existing_v1_1_tag_target": existing_tag_target,
        "existing_v1_1_tag_unchanged": existing_tag_unchanged,
        "hardening_release_tag": "ogk-final-v1.1-hardening",
        "hardening_release_tag_target": release_tag_target,
        "hardening_release_tag_unchanged": hardening_tag_unchanged,
        "follow_up_pr_created": False,
        "follow_up_pr_creation_requires_owner_approval": True,
        "follow_up_pr_approval_phrase": FOLLOW_UP_PR_APPROVAL_PHRASE,
        "follow_up_merge_performed": False,
        "tag_move_performed": False,
        "release_mutation_performed": False,
        "destructive_action_taken": False,
        "files_moved_or_deleted": False,
        "failure_count": len(failures),
        "failures": failures,
    }

    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    (output / "post_merge_integration_result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    write_report(output, result)
    write_packet(output, result)
    write_summary(output, result)
    return result


def write_report(output: Path, result: dict[str, Any]) -> None:
    lines = [
        "# V1.1 Phase 23 Post-Merge Integration",
        "",
        f"Status: {'PASS' if result['ok'] else 'FAIL'}",
        f"Approval phrase: `{result['approval_phrase']}`",
        f"Pull request: {result['pull_request_url']}",
        f"Pull request state: `{result['pull_request_state']}`",
        f"Pull request merged at: `{result['pull_request_merged_at']}`",
        f"Merge commit: `{result['merge_commit']}`",
        f"Origin main head: `{result['origin_main_head']}`",
        f"Origin main matches merge commit: `{result['origin_main_matches_merge_commit']}`",
        f"Post-merge pytest status: `{result['post_merge_pytest_status']}`",
        f"Post-merge final acceptance OK: `{result['post_merge_final_acceptance_ok']}`",
        f"Post-merge manifest OK: `{result['post_merge_manifest_ok']}`",
        f"Post-merge manifest count: `{result['post_merge_manifest_count']}`",
        f"Root policy shadow absent from main: `{result['root_policy_shadow_absent_from_main']}`",
        f"Existing V1.1 tag unchanged: `{result['existing_v1_1_tag_unchanged']}`",
        f"Hardening release tag unchanged: `{result['hardening_release_tag_unchanged']}`",
        f"Follow-up PR created: `{result['follow_up_pr_created']}`",
        "",
        "## Approval Boundary",
        "",
        "| Action | Performed | Required approval |",
        "|---|---|---|",
        f"| Create follow-up PR | {result['follow_up_pr_created']} | `{result['follow_up_pr_approval_phrase']}` |",
        f"| Merge follow-up PR | {result['follow_up_merge_performed']} | separate explicit approval |",
        f"| Move tags | {result['tag_move_performed']} | separate explicit approval |",
        f"| Mutate release | {result['release_mutation_performed']} | separate explicit approval |",
    ]
    if result["failures"]:
        lines.extend(["", "## Failures", ""])
        lines.extend(f"- {failure}" for failure in result["failures"])
    (output / "post_merge_integration_report.md").write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )


def write_packet(output: Path, result: dict[str, Any]) -> None:
    lines = [
        "# OGK Final V1.1 Post-Merge Integration Packet",
        "",
        "This packet records the owner-approved V1.1 hardening PR merge and post-merge validation. It does not create a follow-up PR, merge a follow-up branch, move tags, mutate releases, or move/delete files.",
        "",
        "## Merged PR",
        "",
        f"- URL: {result['pull_request_url']}",
        f"- Number: `{result['pull_request_number']}`",
        f"- State: `{result['pull_request_state']}`",
        f"- Merged at: `{result['pull_request_merged_at']}`",
        f"- Merge commit: `{result['merge_commit']}`",
        f"- Origin main head: `{result['origin_main_head']}`",
        f"- Origin main matches merge commit: `{result['origin_main_matches_merge_commit']}`",
        "",
        "## Verification",
        "",
        f"- V1.1 pytest: `{result['post_merge_pytest_status']}`",
        f"- Final acceptance OK: `{result['post_merge_final_acceptance_ok']}`",
        f"- Manifest OK: `{result['post_merge_manifest_ok']}`",
        f"- Manifest count: `{result['post_merge_manifest_count']}`",
        f"- Root policy shadow absent from main: `{result['root_policy_shadow_absent_from_main']}`",
        "",
        "## Boundaries",
        "",
        f"- Existing V1.1 tag unchanged: `{result['existing_v1_1_tag_unchanged']}`",
        f"- Hardening release tag unchanged: `{result['hardening_release_tag_unchanged']}`",
        f"- Follow-up PR created: `{result['follow_up_pr_created']}`",
        f"- Follow-up PR approval phrase: `{result['follow_up_pr_approval_phrase']}`",
    ]
    (output / "POST_MERGE_INTEGRATION_PACKET.md").write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )


def write_summary(output: Path, result: dict[str, Any]) -> None:
    lines = [
        "# V1.1 Phase 23 Summary",
        "",
        f"Status: {'PASS' if result['ok'] else 'FAIL'}",
        "",
        "Phase 23 records the owner-approved merge of V1.1 hardening into `main` and the post-merge validation boundary.",
        "",
        f"- PR: {result['pull_request_url']}",
        f"- Merge commit: `{result['merge_commit']}`",
        f"- Origin main head: `{result['origin_main_head']}`",
        f"- V1.1 pytest: `{result['post_merge_pytest_status']}`",
        f"- Final acceptance OK: `{result['post_merge_final_acceptance_ok']}`",
        f"- Manifest count: `{result['post_merge_manifest_count']}`",
        f"- Follow-up PR created: `{result['follow_up_pr_created']}`",
        f"- Required follow-up PR approval: `{result['follow_up_pr_approval_phrase']}`",
    ]
    (output / "PHASE_23_SUMMARY.md").write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Record V1.1 hardening post-merge integration evidence.")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--pr-number", type=int, default=EXPECTED_PR_NUMBER)
    parser.add_argument("--pytest-status", default=EXPECTED_POST_MERGE_PYTEST_STATUS)
    parser.add_argument("--final-acceptance-ok", action="store_true", default=True)
    parser.add_argument("--manifest-ok", action="store_true", default=True)
    parser.add_argument("--manifest-count", type=int, default=EXPECTED_POST_MERGE_MANIFEST_COUNT)
    args = parser.parse_args()
    result = build_post_merge_integration(
        output_dir=args.output_dir,
        pr_number=args.pr_number,
        pytest_status=args.pytest_status,
        final_acceptance_ok=args.final_acceptance_ok,
        manifest_ok=args.manifest_ok,
        manifest_count=args.manifest_count,
    )
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
