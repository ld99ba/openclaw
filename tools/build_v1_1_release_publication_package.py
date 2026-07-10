#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any


DEFAULT_APPROVAL_GATE_PATH = Path("reports/v1_1/phase_15/release_publication_approval_gate_result.json")
DEFAULT_OUTPUT_DIR = Path("reports/v1_1/phase_16")


def load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def git_output(args: list[str]) -> str:
    try:
        return subprocess.check_output(["git", *args], text=True, stderr=subprocess.DEVNULL).strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        return ""


def commit_log(from_ref: str, to_ref: str) -> list[str]:
    if not from_ref or not to_ref:
        return []
    output = git_output(["log", "--oneline", f"{from_ref}..{to_ref}"])
    return [line for line in output.splitlines() if line]


def build_release_notes(
    *,
    target_branch: str,
    target_head: str,
    approval_phrase: str,
    commits_since_tag: list[str],
) -> str:
    lines = [
        "# OGK Final V1.1 Hardening Publication Draft",
        "",
        "This is a draft publication note. It is not a release publication record.",
        "",
        "## Target",
        "",
        f"- Branch: `{target_branch}`",
        f"- Head: `{target_head}`",
        f"- Required approval phrase: `{approval_phrase}`",
        "",
        "## Included Hardening Chain",
        "",
        "- Phase 05: workspace hygiene proposal",
        "- Phase 06: gitignore hygiene guard",
        "- Phase 07: untracked review queue",
        "- Phase 08: source candidate assessment",
        "- Phase 09: source inclusion decision packet",
        "- Phase 10: source inclusion preflight",
        "- Phase 11: source inclusion approval gate",
        "- Phase 12: approved `openclaw/` source inclusion",
        "- Phase 13: root policy shadow disposition",
        "- Phase 14: release readiness gate",
        "- Phase 15: publication approval gate",
        "- Phase 16: publication package draft",
        "",
        "## Safety Boundary",
        "",
        "- No tag movement is performed by this package.",
        "- No GitHub release is published by this package.",
        "- No pull request is created by this package.",
        "- Root-level `policies/` shadows remain excluded pending owner ADR.",
        "",
        "## Commits Since Existing V1.1 Tag",
        "",
    ]
    if commits_since_tag:
        lines.extend(f"- `{line}`" for line in commits_since_tag)
    else:
        lines.append("- No commit range was available.")
    return "\n".join(lines) + "\n"


def build_release_publication_package(
    *,
    approval_gate_result: dict[str, Any] | None = None,
    approval_gate_path: str | Path = DEFAULT_APPROVAL_GATE_PATH,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    current_head: str | None = None,
    current_branch: str | None = None,
    existing_tag: str = "ogk-final-v1.1",
) -> dict[str, Any]:
    approval_gate = approval_gate_result if approval_gate_result is not None else load_json(approval_gate_path)
    failures: list[str] = []
    if approval_gate.get("ok") is not True:
        failures.append("phase_15_approval_gate_not_ok")
    if approval_gate.get("approval_required") is not True:
        failures.append("phase_15_approval_not_required_unexpected")
    if approval_gate.get("approval_granted") is not False:
        failures.append("phase_15_approval_granted_unexpected")
    if approval_gate.get("publication_actions_performed") is not False:
        failures.append("phase_15_publication_action_already_performed")

    head = current_head if current_head is not None else git_output(["rev-parse", "HEAD"])
    branch = current_branch if current_branch is not None else git_output(["branch", "--show-current"])
    tag_target = git_output(["rev-list", "-n", "1", existing_tag])
    commits = commit_log(tag_target, head)
    approval_head = approval_gate.get("current_head")
    approval_head_matches_current = approval_head == head

    notes = build_release_notes(
        target_branch=branch,
        target_head=head,
        approval_phrase=str(approval_gate.get("approval_phrase", "")),
        commits_since_tag=commits,
    )

    result: dict[str, Any] = {
        "schema": "ogk.v1_1.release_publication_package.v1",
        "ok": not failures,
        "target_branch": branch,
        "target_head": head,
        "existing_tag": existing_tag,
        "existing_tag_target": tag_target,
        "approval_phrase": approval_gate.get("approval_phrase"),
        "approval_gate_head": approval_head,
        "approval_gate_head_matches_current_head": approval_head_matches_current,
        "commit_count_since_existing_tag": len(commits),
        "commits_since_existing_tag": commits,
        "draft_release_notes_path": "reports/v1_1/phase_16/RELEASE_NOTES_DRAFT.md",
        "publication_package_ready": not failures,
        "approval_required_before_publication": True,
        "tag_move_requires_separate_approval": True,
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
    (output / "release_publication_package_result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    (output / "RELEASE_NOTES_DRAFT.md").write_text(notes, encoding="utf-8")
    write_report(output, result)
    return result


def write_report(output: Path, result: dict[str, Any]) -> None:
    lines = [
        "# V1.1 Phase 16 Release Publication Package",
        "",
        f"Status: {'PASS' if result['ok'] else 'FAIL'}",
        f"Target branch: `{result['target_branch']}`",
        f"Target head: `{result['target_head']}`",
        f"Existing tag: `{result['existing_tag']}`",
        f"Existing tag target: `{result['existing_tag_target']}`",
        f"Approval gate head matches current head: `{result['approval_gate_head_matches_current_head']}`",
        f"Commits since existing tag: {result['commit_count_since_existing_tag']}",
        f"Draft release notes: `{result['draft_release_notes_path']}`",
        f"Release publication performed: `{result['release_publication_performed']}`",
        f"Tag move performed: `{result['tag_move_performed']}`",
        "",
        "## Commit Range",
        "",
        "| Commit |",
        "|---|",
    ]
    for line in result["commits_since_existing_tag"]:
        lines.append(f"| `{line}` |")
    if result["failures"]:
        lines.extend(["", "## Failures", ""])
        lines.extend(f"- {failure}" for failure in result["failures"])
    (output / "release_publication_package_report.md").write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a V1.1 release publication package without publishing.")
    parser.add_argument("--approval-gate", default=str(DEFAULT_APPROVAL_GATE_PATH))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--existing-tag", default="ogk-final-v1.1")
    args = parser.parse_args()
    result = build_release_publication_package(
        approval_gate_path=args.approval_gate,
        output_dir=args.output_dir,
        existing_tag=args.existing_tag,
    )
    summary = {
        "schema": result["schema"],
        "ok": result["ok"],
        "target_branch": result["target_branch"],
        "target_head": result["target_head"],
        "commit_count_since_existing_tag": result["commit_count_since_existing_tag"],
        "publication_package_ready": result["publication_package_ready"],
        "release_publication_performed": result["release_publication_performed"],
        "tag_move_performed": result["tag_move_performed"],
        "failure_count": result["failure_count"],
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
