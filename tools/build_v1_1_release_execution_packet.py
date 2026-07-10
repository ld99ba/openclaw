#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any


DEFAULT_REFRESH_PATH = Path("reports/v1_1/phase_17/publication_target_refresh_result.json")
DEFAULT_OUTPUT_DIR = Path("reports/v1_1/phase_18")
APPROVAL_PHRASE = "批准发布 V1.1 hardening 当前分支"
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


def build_release_execution_packet(
    *,
    refresh_result: dict[str, Any] | None = None,
    refresh_path: str | Path = DEFAULT_REFRESH_PATH,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    current_head: str | None = None,
    current_branch: str | None = None,
    remote_head: str | None = None,
    existing_tag_target: str | None = None,
    target_branch: str = TARGET_BRANCH,
    existing_tag: str = "ogk-final-v1.1",
) -> dict[str, Any]:
    refresh = refresh_result if refresh_result is not None else load_json(refresh_path)
    failures: list[str] = []
    if refresh.get("ok") is not True:
        failures.append("phase_17_publication_target_refresh_not_ok")
    if refresh.get("release_publication_performed") is not False:
        failures.append("phase_17_publication_state_unexpected")
    if refresh.get("tag_move_performed") is not False:
        failures.append("phase_17_tag_move_state_unexpected")

    branch = current_branch if current_branch is not None else git_output(["branch", "--show-current"])
    head = current_head if current_head is not None else git_output(["rev-parse", "HEAD"])
    remote = remote_head
    if remote is None:
        remote = first_field(git_output(["ls-remote", "--heads", "origin", target_branch]))
    tag_target = existing_tag_target
    if tag_target is None:
        tag_target = git_output(["rev-list", "-n", "1", existing_tag])

    remote_matches_current = bool(remote) and remote == head
    tag_matches_refresh = tag_target == refresh.get("existing_tag_target")
    if branch != target_branch:
        failures.append("current_branch_is_not_publication_branch")
    if not remote_matches_current:
        failures.append("remote_branch_head_does_not_match_current_head")
    if not tag_matches_refresh:
        failures.append("existing_tag_target_changed_since_phase_17")

    release_commands = [
        f"git fetch origin {target_branch} --tags",
        f"git checkout {target_branch}",
        f"git reset --hard origin/{target_branch}",
        "python3 tools/verify_v1_1_release_readiness_gate.py --output-dir reports/v1_1/phase_14",
        "python3 tools/verify_v1_1_publication_target_refresh.py --output-dir reports/v1_1/phase_17",
        "python3 tools/build_v1_1_release_execution_packet.py --output-dir reports/v1_1/phase_18",
        "# Publish only after the exact approval phrase is provided by the owner.",
    ]
    guarded_actions = [
        "create_or_update_github_release",
        "move_existing_v1_1_tag",
        "create_pull_request",
    ]
    result: dict[str, Any] = {
        "schema": "ogk.v1_1.release_execution_packet.v1",
        "ok": not failures,
        "target_branch": target_branch,
        "publication_target_ref": f"origin/{target_branch}",
        "current_branch": branch,
        "current_head": head,
        "remote_head": remote,
        "remote_head_matches_current_head": remote_matches_current,
        "existing_tag": existing_tag,
        "existing_tag_target": tag_target,
        "phase_17_existing_tag_target": refresh.get("existing_tag_target"),
        "existing_tag_target_matches_phase_17": tag_matches_refresh,
        "approval_phrase": APPROVAL_PHRASE,
        "approval_required_before_publication": True,
        "approval_granted": False,
        "execution_packet_ready": not failures,
        "release_commands_are_documentation_only": True,
        "guarded_actions": guarded_actions,
        "release_commands": release_commands,
        "release_publication_performed": False,
        "tag_move_performed": False,
        "pull_request_created": False,
        "git_stage_executed": False,
        "git_commit_executed": False,
        "destructive_action_taken": False,
        "files_moved_or_deleted": False,
        "failure_count": len(failures),
        "failures": failures,
    }

    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    (output / "release_execution_packet_result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    write_report(output, result)
    write_packet(output, result)
    return result


def write_report(output: Path, result: dict[str, Any]) -> None:
    lines = [
        "# V1.1 Phase 18 Release Execution Packet",
        "",
        f"Status: {'PASS' if result['ok'] else 'FAIL'}",
        f"Execution packet ready: `{result['execution_packet_ready']}`",
        f"Publication target ref: `{result['publication_target_ref']}`",
        f"Current head: `{result['current_head']}`",
        f"Remote head: `{result['remote_head']}`",
        f"Remote head matches current head: `{result['remote_head_matches_current_head']}`",
        f"Existing tag target matches Phase 17: `{result['existing_tag_target_matches_phase_17']}`",
        f"Approval granted: `{result['approval_granted']}`",
        f"Release publication performed: `{result['release_publication_performed']}`",
        f"Tag move performed: `{result['tag_move_performed']}`",
        f"Pull request created: `{result['pull_request_created']}`",
    ]
    if result["failures"]:
        lines.extend(["", "## Failures", ""])
        lines.extend(f"- {failure}" for failure in result["failures"])
    (output / "release_execution_packet_report.md").write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )


def write_packet(output: Path, result: dict[str, Any]) -> None:
    lines = [
        "# OGK Final V1.1 Release Execution Packet",
        "",
        "This packet documents release execution steps. It does not publish a release, move tags, or create a pull request.",
        "",
        "## Required Approval",
        "",
        f"- Exact phrase: `{result['approval_phrase']}`",
        f"- Approval granted in this packet: `{result['approval_granted']}`",
        "",
        "## Target",
        "",
        f"- Branch ref: `{result['publication_target_ref']}`",
        f"- Observed local head: `{result['current_head']}`",
        f"- Observed remote head: `{result['remote_head']}`",
        f"- Existing tag: `{result['existing_tag']}`",
        f"- Existing tag target: `{result['existing_tag_target']}`",
        "",
        "## Guarded Actions",
        "",
    ]
    lines.extend(f"- `{action}`" for action in result["guarded_actions"])
    lines.extend(["", "## Documentation-Only Commands", "", "```sh"])
    lines.extend(result["release_commands"])
    lines.extend(["```", "", "## Safety Result", ""])
    lines.extend(
        [
            f"- Release publication performed: `{result['release_publication_performed']}`",
            f"- Tag move performed: `{result['tag_move_performed']}`",
            f"- Pull request created: `{result['pull_request_created']}`",
            f"- Destructive action taken: `{result['destructive_action_taken']}`",
        ]
    )
    (output / "RELEASE_EXECUTION_PACKET.md").write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a V1.1 release execution packet without publishing.")
    parser.add_argument("--refresh", default=str(DEFAULT_REFRESH_PATH))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--target-branch", default=TARGET_BRANCH)
    parser.add_argument("--existing-tag", default="ogk-final-v1.1")
    args = parser.parse_args()
    result = build_release_execution_packet(
        refresh_path=args.refresh,
        output_dir=args.output_dir,
        target_branch=args.target_branch,
        existing_tag=args.existing_tag,
    )
    summary = {
        "schema": result["schema"],
        "ok": result["ok"],
        "execution_packet_ready": result["execution_packet_ready"],
        "publication_target_ref": result["publication_target_ref"],
        "remote_head_matches_current_head": result["remote_head_matches_current_head"],
        "approval_granted": result["approval_granted"],
        "release_publication_performed": result["release_publication_performed"],
        "tag_move_performed": result["tag_move_performed"],
        "failure_count": result["failure_count"],
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
