#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any


DEFAULT_PACKAGE_PATH = Path("reports/v1_1/phase_16/release_publication_package_result.json")
DEFAULT_OUTPUT_DIR = Path("reports/v1_1/phase_17")
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


def build_publication_target_refresh(
    *,
    package_result: dict[str, Any] | None = None,
    package_path: str | Path = DEFAULT_PACKAGE_PATH,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    current_head: str | None = None,
    current_branch: str | None = None,
    remote_head: str | None = None,
    existing_tag_target: str | None = None,
    target_branch: str = TARGET_BRANCH,
    existing_tag: str = "ogk-final-v1.1",
) -> dict[str, Any]:
    package = package_result if package_result is not None else load_json(package_path)
    failures: list[str] = []
    if package.get("ok") is not True:
        failures.append("phase_16_publication_package_not_ok")
    if package.get("publication_package_ready") is not True:
        failures.append("phase_16_publication_package_not_ready")
    if package.get("release_publication_performed") is not False:
        failures.append("phase_16_release_publication_state_unexpected")
    if package.get("tag_move_performed") is not False:
        failures.append("phase_16_tag_move_state_unexpected")

    branch = current_branch if current_branch is not None else git_output(["branch", "--show-current"])
    head = current_head if current_head is not None else git_output(["rev-parse", "HEAD"])
    remote = remote_head
    if remote is None:
        remote = first_field(git_output(["ls-remote", "--heads", "origin", target_branch]))
    tag_target = existing_tag_target
    if tag_target is None:
        tag_target = git_output(["rev-list", "-n", "1", existing_tag])

    remote_matches_current = bool(remote) and remote == head
    tag_matches_phase16 = tag_target == package.get("existing_tag_target")
    if branch != target_branch:
        failures.append("current_branch_is_not_publication_branch")
    if not remote_matches_current:
        failures.append("remote_branch_head_does_not_match_current_head")
    if not tag_matches_phase16:
        failures.append("existing_tag_target_changed_since_phase_16")

    result: dict[str, Any] = {
        "schema": "ogk.v1_1.publication_target_refresh.v1",
        "ok": not failures,
        "target_branch": target_branch,
        "publication_target_ref": f"origin/{target_branch}",
        "current_branch": branch,
        "current_head": head,
        "remote_head": remote,
        "remote_head_matches_current_head": remote_matches_current,
        "existing_tag": existing_tag,
        "existing_tag_target": tag_target,
        "phase_16_existing_tag_target": package.get("existing_tag_target"),
        "existing_tag_target_matches_phase_16": tag_matches_phase16,
        "phase_16_target_head": package.get("target_head"),
        "phase_16_approval_phrase": package.get("approval_phrase"),
        "release_publication_performed": False,
        "tag_move_performed": False,
        "pull_request_created": False,
        "approval_required_before_publication": True,
        "tag_move_requires_separate_approval": True,
        "branch_ref_is_publication_target": True,
        "snapshot_head_is_observational": True,
        "git_stage_executed": False,
        "git_commit_executed": False,
        "destructive_action_taken": False,
        "files_moved_or_deleted": False,
        "failure_count": len(failures),
        "failures": failures,
    }

    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    (output / "publication_target_refresh_result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    write_report(output, result)
    return result


def write_report(output: Path, result: dict[str, Any]) -> None:
    lines = [
        "# V1.1 Phase 17 Publication Target Refresh",
        "",
        f"Status: {'PASS' if result['ok'] else 'FAIL'}",
        f"Publication target ref: `{result['publication_target_ref']}`",
        f"Current branch: `{result['current_branch']}`",
        f"Current head: `{result['current_head']}`",
        f"Remote head: `{result['remote_head']}`",
        f"Remote head matches current head: `{result['remote_head_matches_current_head']}`",
        f"Existing tag: `{result['existing_tag']}`",
        f"Existing tag target: `{result['existing_tag_target']}`",
        f"Existing tag target matches Phase 16: `{result['existing_tag_target_matches_phase_16']}`",
        f"Release publication performed: `{result['release_publication_performed']}`",
        f"Tag move performed: `{result['tag_move_performed']}`",
        f"Pull request created: `{result['pull_request_created']}`",
        "",
        "## Boundary",
        "",
        "- This refresh records the branch ref as the publication target.",
        "- The observed head is evidence only; evidence commits may advance the branch.",
        "- Publication still requires the Phase 15 exact approval phrase.",
        "- Moving the existing tag still requires separate explicit approval.",
    ]
    if result["failures"]:
        lines.extend(["", "## Failures", ""])
        lines.extend(f"- {failure}" for failure in result["failures"])
    (output / "publication_target_refresh_report.md").write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Refresh V1.1 publication target evidence without publishing.")
    parser.add_argument("--package", default=str(DEFAULT_PACKAGE_PATH))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--target-branch", default=TARGET_BRANCH)
    parser.add_argument("--existing-tag", default="ogk-final-v1.1")
    args = parser.parse_args()
    result = build_publication_target_refresh(
        package_path=args.package,
        output_dir=args.output_dir,
        target_branch=args.target_branch,
        existing_tag=args.existing_tag,
    )
    summary = {
        "schema": result["schema"],
        "ok": result["ok"],
        "publication_target_ref": result["publication_target_ref"],
        "current_head": result["current_head"],
        "remote_head_matches_current_head": result["remote_head_matches_current_head"],
        "existing_tag_target_matches_phase_16": result["existing_tag_target_matches_phase_16"],
        "release_publication_performed": result["release_publication_performed"],
        "tag_move_performed": result["tag_move_performed"],
        "failure_count": result["failure_count"],
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
