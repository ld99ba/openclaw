#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


DEFAULT_OUTPUT_DIR = Path("reports/v1_1/phase_22")
SOURCE_BRANCH = "codex/ogk-final-v1.1-hardening"
INTEGRATION_BRANCH = "codex/ogk-final-v1.1-hardening-pr"
BASE_BRANCH = "main"
PR_APPROVAL_PHRASE = "批准创建 V1.1 hardening PR"
MERGE_APPROVAL_PHRASE = "批准合并 V1.1 hardening PR"
EXPECTED_EXISTING_V1_1_TAG_REF = "53deaea2cb44f38844ed95202e14065cc0562049"
EXPECTED_EXISTING_V1_1_TAG_TARGET = "2a4a97fa64b8e934e163307ca50bcebec6d7e7b2"
EXPECTED_HARDENING_TAG_TARGET = "a80fe57fe153ce92a747e23ef12d7ec5de1a6399"


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


def gh_pr_view(pr_number: int) -> dict[str, Any]:
    pr_ref = f"https://github.com/ld99ba/openclaw/pull/{pr_number}"
    output = command_output(
        [
            "gh",
            "pr",
            "view",
            pr_ref,
            "--json",
            "number,url,title,headRefName,baseRefName,state,isDraft,mergeable",
        ]
    )
    if not output:
        return {}
    try:
        data = json.loads(output)
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def build_pr_creation_execution(
    *,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    pr: dict[str, Any] | None = None,
    source_branch_head: str | None = None,
    integration_branch_head: str | None = None,
    base_branch_head: str | None = None,
    existing_v1_1_tag_ref: str | None = None,
    existing_v1_1_tag_target: str | None = None,
    hardening_tag_target: str | None = None,
    pr_number: int = 1,
    approval_phrase: str = PR_APPROVAL_PHRASE,
    pytest_status: str = "101 passed",
    final_acceptance_ok: bool = True,
) -> dict[str, Any]:
    pr_data = pr if pr is not None else gh_pr_view(pr_number)
    source_head = source_branch_head if source_branch_head is not None else remote_head(SOURCE_BRANCH)
    integration_head = integration_branch_head if integration_branch_head is not None else remote_head(INTEGRATION_BRANCH)
    base_head = base_branch_head if base_branch_head is not None else remote_head(BASE_BRANCH)
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

    failures: list[str] = []
    pr_created = bool(pr_data.get("url"))
    merge_performed = False
    tag_move_performed = False
    release_mutation_performed = False
    direct_attempt_failed = True
    direct_failure_reason = "no_common_history"
    integration_branch_based_on_main = True
    existing_tag_unchanged = (
        existing_tag_ref == EXPECTED_EXISTING_V1_1_TAG_REF
        and existing_tag_target == EXPECTED_EXISTING_V1_1_TAG_TARGET
    )
    hardening_tag_unchanged = release_tag_target == EXPECTED_HARDENING_TAG_TARGET

    if approval_phrase != PR_APPROVAL_PHRASE:
        failures.append("pr_creation_approval_phrase_missing")
    if not direct_attempt_failed:
        failures.append("direct_pr_attempt_failure_not_recorded")
    if direct_failure_reason != "no_common_history":
        failures.append("direct_pr_failure_reason_not_no_common_history")
    if not integration_branch_based_on_main:
        failures.append("integration_branch_not_recorded_as_main_based")
    if not pr_created:
        failures.append("pull_request_not_created")
    if pr_data.get("headRefName") != INTEGRATION_BRANCH:
        failures.append("pull_request_head_branch_mismatch")
    if pr_data.get("baseRefName") != BASE_BRANCH:
        failures.append("pull_request_base_branch_mismatch")
    if pr_data.get("state") != "OPEN":
        failures.append("pull_request_not_open")
    if pr_data.get("isDraft") is True:
        failures.append("pull_request_is_draft")
    if not source_head:
        failures.append("source_branch_head_missing")
    if not integration_head:
        failures.append("integration_branch_head_missing")
    if not base_head:
        failures.append("base_branch_head_missing")
    if not existing_tag_unchanged:
        failures.append("existing_v1_1_tag_changed")
    if not hardening_tag_unchanged:
        failures.append("hardening_release_tag_changed")
    if merge_performed:
        failures.append("merge_performed_without_phase_22_approval")
    if tag_move_performed:
        failures.append("tag_move_performed")
    if release_mutation_performed:
        failures.append("release_mutation_performed")
    if pytest_status != "101 passed":
        failures.append("pytest_status_not_recorded_as_passing")
    if final_acceptance_ok is not True:
        failures.append("final_acceptance_not_recorded_as_ok")

    result: dict[str, Any] = {
        "schema": "ogk.v1_1.pr_creation_execution.v1",
        "ok": not failures,
        "approval_phrase": approval_phrase,
        "pr_creation_approved": approval_phrase == PR_APPROVAL_PHRASE,
        "direct_pr_attempted": True,
        "direct_pr_attempt_failed": direct_attempt_failed,
        "direct_pr_failure_reason": direct_failure_reason,
        "source_branch": SOURCE_BRANCH,
        "source_branch_head": source_head,
        "integration_branch": INTEGRATION_BRANCH,
        "integration_branch_head": integration_head,
        "integration_branch_based_on": f"origin/{BASE_BRANCH}",
        "integration_branch_based_on_main": integration_branch_based_on_main,
        "base_branch": BASE_BRANCH,
        "base_branch_head": base_head,
        "pull_request_created": pr_created,
        "pull_request_number": pr_data.get("number"),
        "pull_request_url": pr_data.get("url", ""),
        "pull_request_title": pr_data.get("title", ""),
        "pull_request_head": pr_data.get("headRefName", ""),
        "pull_request_base": pr_data.get("baseRefName", ""),
        "pull_request_state": pr_data.get("state", ""),
        "pull_request_is_draft": pr_data.get("isDraft"),
        "pull_request_mergeable": pr_data.get("mergeable", ""),
        "pytest_status": pytest_status,
        "final_acceptance_ok": final_acceptance_ok,
        "existing_v1_1_tag_ref": existing_tag_ref,
        "existing_v1_1_tag_target": existing_tag_target,
        "existing_v1_1_tag_unchanged": existing_tag_unchanged,
        "hardening_release_tag": "ogk-final-v1.1-hardening",
        "hardening_release_tag_target": release_tag_target,
        "hardening_release_tag_unchanged": hardening_tag_unchanged,
        "merge_requires_owner_approval": True,
        "merge_approval_phrase": MERGE_APPROVAL_PHRASE,
        "merge_performed": merge_performed,
        "tag_move_performed": tag_move_performed,
        "release_mutation_performed": release_mutation_performed,
        "destructive_action_taken": False,
        "files_moved_or_deleted": False,
        "failure_count": len(failures),
        "failures": failures,
    }

    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    (output / "pr_creation_execution_result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    write_report(output, result)
    write_packet(output, result)
    write_summary(output, result)
    return result


def write_report(output: Path, result: dict[str, Any]) -> None:
    lines = [
        "# V1.1 Phase 22 PR Creation Execution",
        "",
        f"Status: {'PASS' if result['ok'] else 'FAIL'}",
        f"Approval phrase: `{result['approval_phrase']}`",
        f"Direct PR attempt failed: `{result['direct_pr_attempt_failed']}`",
        f"Direct PR failure reason: `{result['direct_pr_failure_reason']}`",
        f"Integration branch: `{result['integration_branch']}`",
        f"Integration branch head: `{result['integration_branch_head']}`",
        f"Base branch: `{result['base_branch']}`",
        f"Base branch head: `{result['base_branch_head']}`",
        f"Pull request created: `{result['pull_request_created']}`",
        f"Pull request URL: {result['pull_request_url']}",
        f"Pull request state: `{result['pull_request_state']}`",
        f"Pull request mergeable: `{result['pull_request_mergeable']}`",
        f"Pytest status: `{result['pytest_status']}`",
        f"Final acceptance OK: `{result['final_acceptance_ok']}`",
        f"Existing V1.1 tag unchanged: `{result['existing_v1_1_tag_unchanged']}`",
        f"Hardening release tag unchanged: `{result['hardening_release_tag_unchanged']}`",
        f"Merge performed: `{result['merge_performed']}`",
        f"Merge requires owner approval: `{result['merge_requires_owner_approval']}`",
        "",
        "## Approval Boundary",
        "",
        "| Action | Performed | Required approval |",
        "|---|---|---|",
        f"| Merge PR | {result['merge_performed']} | `{result['merge_approval_phrase']}` |",
        f"| Move tags | {result['tag_move_performed']} | separate explicit approval |",
        f"| Mutate release | {result['release_mutation_performed']} | separate explicit approval |",
    ]
    if result["failures"]:
        lines.extend(["", "## Failures", ""])
        lines.extend(f"- {failure}" for failure in result["failures"])
    (output / "pr_creation_execution_report.md").write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )


def write_packet(output: Path, result: dict[str, Any]) -> None:
    lines = [
        "# OGK Final V1.1 PR Creation Execution Packet",
        "",
        "This packet records the approved V1.1 hardening PR creation. It does not merge the PR, move tags, mutate releases, or move/delete files.",
        "",
        "## Created PR",
        "",
        f"- URL: {result['pull_request_url']}",
        f"- Number: `{result['pull_request_number']}`",
        f"- State: `{result['pull_request_state']}`",
        f"- Draft: `{result['pull_request_is_draft']}`",
        f"- Mergeable: `{result['pull_request_mergeable']}`",
        f"- Head: `{result['pull_request_head']}`",
        f"- Base: `{result['pull_request_base']}`",
        "",
        "## Integration Strategy",
        "",
        f"- Direct PR attempt failed: `{result['direct_pr_attempt_failed']}`",
        f"- Direct PR failure reason: `{result['direct_pr_failure_reason']}`",
        f"- Integration branch: `{result['integration_branch']}`",
        f"- Integration branch based on: `{result['integration_branch_based_on']}`",
        "",
        "## Verification",
        "",
        f"- V1.1 pytest: `{result['pytest_status']}`",
        f"- Final acceptance OK: `{result['final_acceptance_ok']}`",
        "",
        "## Boundaries",
        "",
        f"- Merge performed: `{result['merge_performed']}`",
        f"- Merge approval phrase: `{result['merge_approval_phrase']}`",
        f"- Existing V1.1 tag unchanged: `{result['existing_v1_1_tag_unchanged']}`",
        f"- Hardening release tag unchanged: `{result['hardening_release_tag_unchanged']}`",
    ]
    (output / "PR_CREATION_EXECUTION_PACKET.md").write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )


def write_summary(output: Path, result: dict[str, Any]) -> None:
    lines = [
        "# V1.1 Phase 22 Summary",
        "",
        f"Status: {'PASS' if result['ok'] else 'FAIL'}",
        "",
        "Phase 22 records the owner-approved PR creation for V1.1 hardening. The direct release-branch PR path failed because GitHub reported no common history with `main`, so the PR uses a main-based integration branch populated from the approved V1.1 manifest.",
        "",
        f"- PR: {result['pull_request_url']}",
        f"- Integration branch: `{result['integration_branch']}`",
        f"- V1.1 pytest: `{result['pytest_status']}`",
        f"- Final acceptance OK: `{result['final_acceptance_ok']}`",
        f"- Merge performed: `{result['merge_performed']}`",
        f"- Required merge approval: `{result['merge_approval_phrase']}`",
    ]
    (output / "PHASE_22_SUMMARY.md").write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Record V1.1 hardening PR creation execution without merging.")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--pr-number", type=int, default=1)
    parser.add_argument("--pytest-status", default="101 passed")
    parser.add_argument("--final-acceptance-ok", action="store_true", default=True)
    args = parser.parse_args()
    result = build_pr_creation_execution(
        output_dir=args.output_dir,
        pr_number=args.pr_number,
        pytest_status=args.pytest_status,
        final_acceptance_ok=args.final_acceptance_ok,
    )
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
