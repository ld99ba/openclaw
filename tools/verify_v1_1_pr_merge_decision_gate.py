#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.verify_v1_1_post_publication_audit import git_is_ancestor


DEFAULT_CLOSURE_PATH = Path("reports/v1_1/phase_20/release_closure_packet_result.json")
DEFAULT_OUTPUT_DIR = Path("reports/v1_1/phase_21")
SOURCE_BRANCH = "codex/ogk-final-v1.1-hardening"
BASE_BRANCH = "main"
PR_APPROVAL_PHRASE = "批准创建 V1.1 hardening PR"
MERGE_APPROVAL_PHRASE = "批准合并 V1.1 hardening PR"


def load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def command_output(args: list[str]) -> str:
    try:
        return subprocess.check_output(args, text=True, stderr=subprocess.DEVNULL).strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        return ""


def git_output(args: list[str]) -> str:
    return command_output(["git", *args])


def gh_output(args: list[str]) -> str:
    return command_output(["gh", *args])


def first_field(output: str) -> str:
    return output.split()[0] if output.split() else ""


def remote_head(branch: str) -> str:
    return first_field(git_output(["ls-remote", "--heads", "origin", branch]))


def open_prs_for_branch(source_branch: str, base_branch: str) -> list[dict[str, Any]]:
    output = gh_output(
        [
            "pr",
            "list",
            "--repo",
            "ld99ba/openclaw",
            "--head",
            source_branch,
            "--base",
            base_branch,
            "--state",
            "open",
            "--json",
            "number,url,title,isDraft",
        ]
    )
    if not output:
        return []
    try:
        data = json.loads(output)
    except json.JSONDecodeError:
        return []
    return data if isinstance(data, list) else []


def build_pr_merge_decision_gate(
    *,
    closure_result: dict[str, Any] | None = None,
    closure_path: str | Path = DEFAULT_CLOSURE_PATH,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    source_branch_head: str | None = None,
    base_branch_head: str | None = None,
    release_tag_is_ancestor_of_source: bool | None = None,
    open_pull_requests: list[dict[str, Any]] | None = None,
    source_branch: str = SOURCE_BRANCH,
    base_branch: str = BASE_BRANCH,
) -> dict[str, Any]:
    closure = closure_result if closure_result is not None else load_json(closure_path)
    failures: list[str] = []

    source_head = source_branch_head if source_branch_head is not None else remote_head(source_branch)
    base_head = base_branch_head if base_branch_head is not None else remote_head(base_branch)
    release_tag_target = closure.get("release_tag_target", "")

    release_tag_reachable = False
    if release_tag_is_ancestor_of_source is not None:
        release_tag_reachable = release_tag_is_ancestor_of_source
    elif release_tag_target and source_head:
        release_tag_reachable = release_tag_target == source_head or git_is_ancestor(release_tag_target, source_head)

    prs = open_pull_requests
    if prs is None:
        prs = open_prs_for_branch(source_branch, base_branch)

    closure_ok = closure.get("ok") is True
    release_point_fixed = closure.get("release_point_fixed") is True
    existing_tag_unchanged = closure.get("existing_tag_unchanged") is True
    old_tag_moved = closure.get("tag_move_performed_on_existing_v1_1_tag") is True
    prior_pr_created = closure.get("pull_request_created") is True
    destructive_action_taken = closure.get("destructive_action_taken") is True
    files_moved_or_deleted = closure.get("files_moved_or_deleted") is True

    if not closure_ok:
        failures.append("phase_20_release_closure_not_ok")
    if not release_point_fixed:
        failures.append("phase_20_release_point_not_fixed")
    if not existing_tag_unchanged:
        failures.append("existing_v1_1_tag_not_confirmed_unchanged")
    if not release_tag_reachable:
        failures.append("release_tag_target_not_reachable_from_source_branch")
    if not source_head:
        failures.append("source_branch_head_missing")
    if not base_head:
        failures.append("base_branch_head_missing")
    if old_tag_moved:
        failures.append("existing_v1_1_tag_move_recorded")
    if prior_pr_created:
        failures.append("prior_pull_request_creation_recorded")
    if destructive_action_taken:
        failures.append("destructive_action_recorded")
    if files_moved_or_deleted:
        failures.append("file_move_or_delete_recorded")

    open_pr_count = len(prs)
    result: dict[str, Any] = {
        "schema": "ogk.v1_1.pr_merge_decision_gate.v1",
        "ok": not failures,
        "source_branch": source_branch,
        "base_branch": base_branch,
        "source_branch_head": source_head,
        "base_branch_head": base_head,
        "release_tag": closure.get("release_tag", ""),
        "release_url": closure.get("release_url", ""),
        "release_tag_target": release_tag_target,
        "release_tag_target_reachable_from_source_branch": release_tag_reachable,
        "phase_20_schema": closure.get("schema"),
        "phase_20_closure_ok": closure_ok,
        "release_point_fixed": release_point_fixed,
        "existing_tag_unchanged": existing_tag_unchanged,
        "open_pull_request_count": open_pr_count,
        "open_pull_requests": prs,
        "pr_creation_recommended": open_pr_count == 0,
        "pr_creation_requires_owner_approval": True,
        "merge_requires_owner_approval": True,
        "pr_approval_phrase": PR_APPROVAL_PHRASE,
        "merge_approval_phrase": MERGE_APPROVAL_PHRASE,
        "pull_request_created": False,
        "merge_performed": False,
        "tag_move_performed": False,
        "release_mutation_performed": False,
        "git_stage_executed": False,
        "git_commit_executed": False,
        "destructive_action_taken": destructive_action_taken,
        "files_moved_or_deleted": files_moved_or_deleted,
        "failure_count": len(failures),
        "failures": failures,
    }

    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    (output / "pr_merge_decision_gate_result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    write_report(output, result)
    write_packet(output, result)
    return result


def write_report(output: Path, result: dict[str, Any]) -> None:
    lines = [
        "# V1.1 Phase 21 PR Merge Decision Gate",
        "",
        f"Status: {'PASS' if result['ok'] else 'FAIL'}",
        f"Source branch: `{result['source_branch']}`",
        f"Source branch head: `{result['source_branch_head']}`",
        f"Base branch: `{result['base_branch']}`",
        f"Base branch head: `{result['base_branch_head']}`",
        f"Release tag target: `{result['release_tag_target']}`",
        f"Release tag reachable from source branch: `{result['release_tag_target_reachable_from_source_branch']}`",
        f"Release point fixed: `{result['release_point_fixed']}`",
        f"Existing V1.1 tag unchanged: `{result['existing_tag_unchanged']}`",
        f"Open pull requests: `{result['open_pull_request_count']}`",
        f"PR creation recommended: `{result['pr_creation_recommended']}`",
        f"PR creation requires owner approval: `{result['pr_creation_requires_owner_approval']}`",
        f"Merge requires owner approval: `{result['merge_requires_owner_approval']}`",
        f"Pull request created: `{result['pull_request_created']}`",
        f"Merge performed: `{result['merge_performed']}`",
        "",
        "## Approval Boundary",
        "",
        "| Action | Performed | Required approval |",
        "|---|---|---|",
        f"| Create PR | {result['pull_request_created']} | `{result['pr_approval_phrase']}` |",
        f"| Merge PR | {result['merge_performed']} | `{result['merge_approval_phrase']}` |",
        f"| Move tags | {result['tag_move_performed']} | separate explicit approval |",
        f"| Mutate release | {result['release_mutation_performed']} | separate explicit approval |",
    ]
    if result["open_pull_requests"]:
        lines.extend(["", "## Open Pull Requests", ""])
        for pr in result["open_pull_requests"]:
            lines.append(f"- #{pr.get('number')}: {pr.get('title')} ({pr.get('url')})")
    if result["failures"]:
        lines.extend(["", "## Failures", ""])
        lines.extend(f"- {failure}" for failure in result["failures"])
    (output / "pr_merge_decision_gate_report.md").write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )


def write_packet(output: Path, result: dict[str, Any]) -> None:
    lines = [
        "# OGK Final V1.1 PR Merge Decision Packet",
        "",
        "This packet records the PR and merge decision boundary for V1.1 hardening. It does not create a pull request, merge a branch, move tags, or mutate the release.",
        "",
        "## Decision State",
        "",
        f"- Source branch: `{result['source_branch']}`",
        f"- Source branch head: `{result['source_branch_head']}`",
        f"- Base branch: `{result['base_branch']}`",
        f"- Base branch head: `{result['base_branch_head']}`",
        f"- Release tag target reachable from source branch: `{result['release_tag_target_reachable_from_source_branch']}`",
        f"- Open pull requests: `{result['open_pull_request_count']}`",
        f"- PR creation recommended: `{result['pr_creation_recommended']}`",
        "",
        "## Required Approvals",
        "",
        f"- PR creation phrase: `{result['pr_approval_phrase']}`",
        f"- Merge phrase: `{result['merge_approval_phrase']}`",
        "",
        "## Actions Performed",
        "",
        f"- Pull request created: `{result['pull_request_created']}`",
        f"- Merge performed: `{result['merge_performed']}`",
        f"- Tag move performed: `{result['tag_move_performed']}`",
        f"- Release mutation performed: `{result['release_mutation_performed']}`",
    ]
    (output / "PR_MERGE_DECISION_PACKET.md").write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Build V1.1 PR merge decision gate without creating or merging a PR.")
    parser.add_argument("--closure", default=str(DEFAULT_CLOSURE_PATH))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--source-branch", default=SOURCE_BRANCH)
    parser.add_argument("--base-branch", default=BASE_BRANCH)
    args = parser.parse_args()
    result = build_pr_merge_decision_gate(
        closure_path=args.closure,
        output_dir=args.output_dir,
        source_branch=args.source_branch,
        base_branch=args.base_branch,
    )
    summary = {
        "schema": result["schema"],
        "ok": result["ok"],
        "source_branch": result["source_branch"],
        "base_branch": result["base_branch"],
        "open_pull_request_count": result["open_pull_request_count"],
        "pr_creation_recommended": result["pr_creation_recommended"],
        "pr_creation_requires_owner_approval": result["pr_creation_requires_owner_approval"],
        "merge_requires_owner_approval": result["merge_requires_owner_approval"],
        "failure_count": result["failure_count"],
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
