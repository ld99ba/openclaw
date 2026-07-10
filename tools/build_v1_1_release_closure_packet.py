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


DEFAULT_AUDIT_PATH = Path("reports/v1_1/phase_19/post_publication_audit_result.json")
DEFAULT_OUTPUT_DIR = Path("reports/v1_1/phase_20")
TARGET_BRANCH = "codex/ogk-final-v1.1-hardening"


def load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def git_output(args: list[str]) -> str:
    try:
        return subprocess.check_output(["git", *args], text=True, stderr=subprocess.DEVNULL).strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        return ""


def first_field(output: str) -> str:
    return output.split()[0] if output.split() else ""


def build_release_closure_packet(
    *,
    audit_result: dict[str, Any] | None = None,
    audit_path: str | Path = DEFAULT_AUDIT_PATH,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    current_branch_head: str | None = None,
    release_tag_target: str | None = None,
    release_tag_is_ancestor_of_branch: bool | None = None,
    target_branch: str = TARGET_BRANCH,
) -> dict[str, Any]:
    audit = audit_result if audit_result is not None else load_json(audit_path)
    failures: list[str] = []

    branch_head = current_branch_head
    if branch_head is None:
        branch_head = first_field(git_output(["ls-remote", "--heads", "origin", target_branch]))
    if not branch_head:
        branch_head = audit.get("target_branch_head", "")

    tag_target = release_tag_target if release_tag_target is not None else audit.get("release_tag_target", "")
    release_tag_matches_branch = bool(tag_target) and tag_target == branch_head
    if release_tag_is_ancestor_of_branch is not None:
        release_tag_is_branch_ancestor = release_tag_is_ancestor_of_branch
    elif release_tag_matches_branch:
        release_tag_is_branch_ancestor = True
    else:
        release_tag_is_branch_ancestor = git_is_ancestor(tag_target, branch_head)

    audit_ok = audit.get("ok") is True
    release_publication_performed = audit.get("release_publication_performed") is True
    existing_tag_unchanged = audit.get("existing_tag_unchanged") is True
    old_tag_moved = audit.get("tag_move_performed_on_existing_v1_1_tag") is True
    pull_request_created = audit.get("pull_request_created") is True
    destructive_action_taken = audit.get("destructive_action_taken") is True
    files_moved_or_deleted = audit.get("files_moved_or_deleted") is True

    if not audit_ok:
        failures.append("phase_19_post_publication_audit_not_ok")
    if not release_publication_performed:
        failures.append("release_publication_not_recorded")
    if not release_tag_is_branch_ancestor:
        failures.append("release_tag_target_not_reachable_from_current_branch")
    if not existing_tag_unchanged:
        failures.append("existing_v1_1_tag_not_confirmed_unchanged")
    if old_tag_moved:
        failures.append("existing_v1_1_tag_move_recorded")
    if pull_request_created:
        failures.append("pull_request_creation_recorded")
    if destructive_action_taken:
        failures.append("destructive_action_recorded")
    if files_moved_or_deleted:
        failures.append("file_move_or_delete_recorded")

    branch_continues_after_release = (
        bool(tag_target)
        and bool(branch_head)
        and not release_tag_matches_branch
        and release_tag_is_branch_ancestor
    )
    result: dict[str, Any] = {
        "schema": "ogk.v1_1.release_closure_packet.v1",
        "ok": not failures,
        "target_branch": target_branch,
        "current_branch_head": branch_head,
        "release_tag": audit.get("release_tag", ""),
        "release_url": audit.get("release_url", ""),
        "release_tag_target": tag_target,
        "release_tag_target_matches_current_branch_head": release_tag_matches_branch,
        "release_tag_target_is_current_branch_ancestor": release_tag_is_branch_ancestor,
        "branch_continues_after_release": branch_continues_after_release,
        "release_point_fixed": release_tag_is_branch_ancestor and existing_tag_unchanged,
        "release_publication_performed": release_publication_performed,
        "existing_tag": audit.get("existing_tag", ""),
        "existing_tag_target": audit.get("existing_tag_target", ""),
        "expected_existing_tag_target": audit.get("expected_existing_tag_target", ""),
        "existing_tag_unchanged": existing_tag_unchanged,
        "phase_19_schema": audit.get("schema"),
        "phase_19_audit_ok": audit_ok,
        "tag_move_performed_on_existing_v1_1_tag": old_tag_moved,
        "pull_request_created": pull_request_created,
        "git_stage_executed": False,
        "git_commit_executed": False,
        "destructive_action_taken": destructive_action_taken,
        "files_moved_or_deleted": files_moved_or_deleted,
        "failure_count": len(failures),
        "failures": failures,
    }

    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    (output / "release_closure_packet_result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    write_report(output, result)
    write_packet(output, result)
    return result


def write_report(output: Path, result: dict[str, Any]) -> None:
    lines = [
        "# V1.1 Phase 20 Release Closure Packet",
        "",
        f"Status: {'PASS' if result['ok'] else 'FAIL'}",
        f"Release URL: `{result['release_url']}`",
        f"Release tag: `{result['release_tag']}`",
        f"Release tag target: `{result['release_tag_target']}`",
        f"Current branch head: `{result['current_branch_head']}`",
        f"Release tag matches current branch head: `{result['release_tag_target_matches_current_branch_head']}`",
        f"Release tag is current branch ancestor: `{result['release_tag_target_is_current_branch_ancestor']}`",
        f"Branch continues after release: `{result['branch_continues_after_release']}`",
        f"Existing V1.1 tag unchanged: `{result['existing_tag_unchanged']}`",
        f"Release point fixed: `{result['release_point_fixed']}`",
        f"Pull request created: `{result['pull_request_created']}`",
        "",
        "## Notes",
        "",
        "- The release is attached to the hardening release tag, not to later audit commits.",
        "- Later branch commits are acceptable when the release tag remains reachable from the branch.",
        "- The existing `ogk-final-v1.1` tag remains unchanged.",
    ]
    if result["failures"]:
        lines.extend(["", "## Failures", ""])
        lines.extend(f"- {failure}" for failure in result["failures"])
    (output / "release_closure_packet_report.md").write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )


def write_packet(output: Path, result: dict[str, Any]) -> None:
    lines = [
        "# OGK Final V1.1 Release Closure Packet",
        "",
        "This packet closes the V1.1 hardening publication loop without mutating releases, tags, pull requests, or files outside the tracked manifest.",
        "",
        "## Release State",
        "",
        f"- Release URL: `{result['release_url']}`",
        f"- Release tag: `{result['release_tag']}`",
        f"- Release tag target: `{result['release_tag_target']}`",
        f"- Current hardening branch head: `{result['current_branch_head']}`",
        f"- Release tag is branch ancestor: `{result['release_tag_target_is_current_branch_ancestor']}`",
        f"- Branch continues after release: `{result['branch_continues_after_release']}`",
        "",
        "## Safety",
        "",
        f"- Existing V1.1 tag unchanged: `{result['existing_tag_unchanged']}`",
        f"- Existing V1.1 tag moved: `{result['tag_move_performed_on_existing_v1_1_tag']}`",
        f"- Pull request created: `{result['pull_request_created']}`",
        f"- Destructive action taken: `{result['destructive_action_taken']}`",
        f"- Files moved or deleted: `{result['files_moved_or_deleted']}`",
    ]
    (output / "RELEASE_CLOSURE_PACKET.md").write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a V1.1 release closure packet.")
    parser.add_argument("--audit", default=str(DEFAULT_AUDIT_PATH))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--target-branch", default=TARGET_BRANCH)
    args = parser.parse_args()
    result = build_release_closure_packet(
        audit_path=args.audit,
        output_dir=args.output_dir,
        target_branch=args.target_branch,
    )
    summary = {
        "schema": result["schema"],
        "ok": result["ok"],
        "release_url": result["release_url"],
        "release_point_fixed": result["release_point_fixed"],
        "release_tag_target_is_current_branch_ancestor": result[
            "release_tag_target_is_current_branch_ancestor"
        ],
        "existing_tag_unchanged": result["existing_tag_unchanged"],
        "failure_count": result["failure_count"],
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
