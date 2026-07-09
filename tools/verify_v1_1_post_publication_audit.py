#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any


DEFAULT_EXECUTION_PACKET_PATH = Path("reports/v1_1/phase_18/release_execution_packet_result.json")
DEFAULT_OUTPUT_DIR = Path("reports/v1_1/phase_19")
RELEASE_TAG = "ogk-final-v1.1-hardening"
EXISTING_TAG = "ogk-final-v1.1"
TARGET_BRANCH = "codex/ogk-final-v1.1-hardening"


def load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def command_output(args: list[str]) -> str:
    try:
        return subprocess.check_output(args, text=True, stderr=subprocess.DEVNULL).strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        return ""


def git_output(args: list[str]) -> str:
    return command_output(["git", *args])


def gh_release_info(tag: str) -> dict[str, Any]:
    output = command_output(
        [
            "gh",
            "release",
            "view",
            tag,
            "--json",
            "tagName,url,isDraft,isPrerelease,targetCommitish,publishedAt,name",
        ]
    )
    return json.loads(output) if output else {}


def first_field(output: str) -> str:
    return output.split()[0] if output.split() else ""


def remote_tag_target(tag: str, output: str | None = None) -> str:
    data = output if output is not None else git_output(["ls-remote", "--tags", "origin", f"{tag}*"])
    exact = ""
    dereferenced = ""
    for line in data.splitlines():
        parts = line.split()
        if len(parts) != 2:
            continue
        sha, ref = parts
        if ref == f"refs/tags/{tag}":
            exact = sha
        if ref == f"refs/tags/{tag}^{{}}":
            dereferenced = sha
    return dereferenced or exact


def build_post_publication_audit(
    *,
    execution_packet_result: dict[str, Any] | None = None,
    execution_packet_path: str | Path = DEFAULT_EXECUTION_PACKET_PATH,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    release_info: dict[str, Any] | None = None,
    release_tag_target: str | None = None,
    existing_tag_target: str | None = None,
    branch_head: str | None = None,
    release_tag: str = RELEASE_TAG,
    existing_tag: str = EXISTING_TAG,
    target_branch: str = TARGET_BRANCH,
) -> dict[str, Any]:
    packet = execution_packet_result if execution_packet_result is not None else load_json(execution_packet_path)
    failures: list[str] = []
    if packet.get("ok") is not True:
        failures.append("phase_18_execution_packet_not_ok")
    if packet.get("execution_packet_ready") is not True:
        failures.append("phase_18_execution_packet_not_ready")

    info = release_info if release_info is not None else gh_release_info(release_tag)
    tag_target = release_tag_target if release_tag_target is not None else remote_tag_target(release_tag)
    old_tag_target = existing_tag_target if existing_tag_target is not None else remote_tag_target(existing_tag)
    remote_branch_head = branch_head
    if remote_branch_head is None:
        remote_branch_head = first_field(git_output(["ls-remote", "--heads", "origin", target_branch]))

    expected_existing_tag_target = packet.get("existing_tag_target")
    release_exists = bool(info)
    release_tag_matches = info.get("tagName") == release_tag
    release_is_published = release_exists and info.get("isDraft") is False and info.get("isPrerelease") is False
    release_tag_matches_branch = bool(tag_target) and tag_target == remote_branch_head
    existing_tag_unchanged = bool(old_tag_target) and old_tag_target == expected_existing_tag_target

    if not release_exists:
        failures.append("github_release_missing")
    if not release_tag_matches:
        failures.append("github_release_tag_mismatch")
    if not release_is_published:
        failures.append("github_release_not_published")
    if not release_tag_matches_branch:
        failures.append("release_tag_target_does_not_match_hardening_branch")
    if not existing_tag_unchanged:
        failures.append("existing_v1_1_tag_target_changed")

    result: dict[str, Any] = {
        "schema": "ogk.v1_1.post_publication_audit.v1",
        "ok": not failures,
        "release_publication_performed": release_exists,
        "release_tag": release_tag,
        "release_url": info.get("url", ""),
        "release_name": info.get("name", ""),
        "release_published_at": info.get("publishedAt", ""),
        "release_is_draft": info.get("isDraft"),
        "release_is_prerelease": info.get("isPrerelease"),
        "release_target_commitish": info.get("targetCommitish", ""),
        "release_tag_target": tag_target,
        "target_branch": target_branch,
        "target_branch_head": remote_branch_head,
        "release_tag_target_matches_target_branch_head": release_tag_matches_branch,
        "existing_tag": existing_tag,
        "existing_tag_target": old_tag_target,
        "expected_existing_tag_target": expected_existing_tag_target,
        "existing_tag_unchanged": existing_tag_unchanged,
        "phase_18_schema": packet.get("schema"),
        "phase_18_execution_packet_ready": packet.get("execution_packet_ready"),
        "tag_move_performed_on_existing_v1_1_tag": False,
        "pull_request_created": False,
        "post_publication_audit_commit_expected_to_advance_branch": True,
        "git_stage_executed": False,
        "git_commit_executed": False,
        "destructive_action_taken": False,
        "files_moved_or_deleted": False,
        "failure_count": len(failures),
        "failures": failures,
    }

    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    (output / "post_publication_audit_result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    write_report(output, result)
    return result


def write_report(output: Path, result: dict[str, Any]) -> None:
    lines = [
        "# V1.1 Phase 19 Post Publication Audit",
        "",
        f"Status: {'PASS' if result['ok'] else 'FAIL'}",
        f"Release publication performed: `{result['release_publication_performed']}`",
        f"Release tag: `{result['release_tag']}`",
        f"Release URL: `{result['release_url']}`",
        f"Release published at: `{result['release_published_at']}`",
        f"Release tag target: `{result['release_tag_target']}`",
        f"Target branch head: `{result['target_branch_head']}`",
        f"Release tag target matches branch head: `{result['release_tag_target_matches_target_branch_head']}`",
        f"Existing V1.1 tag target: `{result['existing_tag_target']}`",
        f"Existing V1.1 tag unchanged: `{result['existing_tag_unchanged']}`",
        f"Existing V1.1 tag moved: `{result['tag_move_performed_on_existing_v1_1_tag']}`",
        f"Pull request created: `{result['pull_request_created']}`",
        "",
        "## Notes",
        "",
        "- This audit records the post-publication state.",
        "- The audit commit itself is expected to advance the hardening branch after the release tag.",
        "- The existing `ogk-final-v1.1` tag remains unchanged.",
    ]
    if result["failures"]:
        lines.extend(["", "## Failures", ""])
        lines.extend(f"- {failure}" for failure in result["failures"])
    (output / "post_publication_audit_report.md").write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit the published V1.1 hardening release.")
    parser.add_argument("--execution-packet", default=str(DEFAULT_EXECUTION_PACKET_PATH))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--release-tag", default=RELEASE_TAG)
    parser.add_argument("--existing-tag", default=EXISTING_TAG)
    parser.add_argument("--target-branch", default=TARGET_BRANCH)
    args = parser.parse_args()
    result = build_post_publication_audit(
        execution_packet_path=args.execution_packet,
        output_dir=args.output_dir,
        release_tag=args.release_tag,
        existing_tag=args.existing_tag,
        target_branch=args.target_branch,
    )
    summary = {
        "schema": result["schema"],
        "ok": result["ok"],
        "release_publication_performed": result["release_publication_performed"],
        "release_url": result["release_url"],
        "release_tag_target_matches_target_branch_head": result[
            "release_tag_target_matches_target_branch_head"
        ],
        "existing_tag_unchanged": result["existing_tag_unchanged"],
        "failure_count": result["failure_count"],
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
