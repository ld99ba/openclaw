#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_ASSESSMENT_PATH = Path("reports/v1_1/phase_08/source_candidate_assessment_result.json")
DEFAULT_OUTPUT_DIR = Path("reports/v1_1/phase_09")


def load_assessment(path: str | Path = DEFAULT_ASSESSMENT_PATH) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def decision_for_candidate(candidate: dict[str, Any]) -> dict[str, Any]:
    path = candidate["path"]
    kind = candidate["kind"]
    duplicate_hash_match = candidate.get("duplicate_hash_match")

    if kind == "root_policy_shadow" and duplicate_hash_match is True:
        return {
            "path": path,
            "kind": kind,
            "decision": "defer_root_policy_shadow_duplicate",
            "include_in_next_stage_pathspec": False,
            "requires_adr_before_inclusion": True,
            "requires_explicit_approval_before_stage": True,
            "reason": "Root policy shadow matches the tracked package policy counterpart.",
            "next_action": "Keep unstaged unless an ADR approves root-level policy ownership.",
        }

    if kind == "package_marker":
        decision = "include_package_marker_after_approval"
        reason = "Package marker can make the package surface explicit."
    elif kind == "package_entrypoint":
        decision = "include_entrypoint_after_behavior_review"
        reason = "Package entrypoint changes CLI execution surface and needs behavior review."
    elif kind in {"package_policy_config", "runtime_json_config"}:
        decision = "include_runtime_config_after_owner_review"
        reason = "Runtime config needs ownership confirmation before inclusion."
    else:
        decision = "include_source_candidate_after_owner_review"
        reason = "Source candidate needs owner and behavior review before inclusion."

    return {
        "path": path,
        "kind": kind,
        "decision": decision,
        "include_in_next_stage_pathspec": True,
        "requires_adr_before_inclusion": False,
        "requires_explicit_approval_before_stage": True,
        "reason": reason,
        "next_action": "Stage only after explicit approval for source candidate inclusion.",
    }


def build_source_candidate_inclusion_decision(
    *,
    assessment_result: dict[str, Any] | None = None,
    assessment_path: str | Path = DEFAULT_ASSESSMENT_PATH,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
) -> dict[str, Any]:
    assessment = assessment_result if assessment_result is not None else load_assessment(assessment_path)
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    decisions = [decision_for_candidate(candidate) for candidate in assessment["assessments"]]
    next_stage_pathspec = [
        decision["path"]
        for decision in decisions
        if decision["include_in_next_stage_pathspec"]
    ]
    deferred_pathspec = [
        decision["path"]
        for decision in decisions
        if not decision["include_in_next_stage_pathspec"]
    ]
    decision_counts: dict[str, int] = {}
    for decision in decisions:
        key = decision["decision"]
        decision_counts[key] = decision_counts.get(key, 0) + 1

    result: dict[str, Any] = {
        "schema": "ogk.v1_1.source_candidate_inclusion_decision.v1",
        "ok": True,
        "source_candidate_count": len(decisions),
        "next_stage_pathspec_count": len(next_stage_pathspec),
        "deferred_pathspec_count": len(deferred_pathspec),
        "decision_counts": dict(sorted(decision_counts.items())),
        "next_stage_pathspec": next_stage_pathspec,
        "deferred_pathspec": deferred_pathspec,
        "decisions": decisions,
        "explicit_approval_required_before_stage": True,
        "git_stage_executed": False,
        "destructive_action_taken": False,
        "files_moved_or_deleted": False,
    }
    (output / "source_candidate_inclusion_decision_result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    write_report(output, result)
    return result


def write_report(output: Path, result: dict[str, Any]) -> None:
    lines = [
        "# V1.1 Phase 09 Source Candidate Inclusion Decision",
        "",
        f"Status: {'PASS' if result['ok'] else 'FAIL'}",
        f"Source candidates: {result['source_candidate_count']}",
        f"Next-stage pathspec candidates: {result['next_stage_pathspec_count']}",
        f"Deferred candidates: {result['deferred_pathspec_count']}",
        f"Explicit approval required before stage: `{result['explicit_approval_required_before_stage']}`",
        f"Git staging executed: `{result['git_stage_executed']}`",
        f"Destructive action taken: `{result['destructive_action_taken']}`",
        "",
        "## Decision Counts",
        "",
        "| Decision | Count |",
        "|---|---:|",
    ]
    for decision, count in result["decision_counts"].items():
        lines.append(f"| {decision} | {count} |")

    lines.extend(
        [
            "",
            "## Next-Stage Pathspec",
            "",
            "| Path |",
            "|---|",
        ]
    )
    for path in result["next_stage_pathspec"]:
        lines.append(f"| `{path}` |")

    lines.extend(
        [
            "",
            "## Deferred Pathspec",
            "",
            "| Path | Reason |",
            "|---|---|",
        ]
    )
    decisions_by_path = {decision["path"]: decision for decision in result["decisions"]}
    for path in result["deferred_pathspec"]:
        lines.append(f"| `{path}` | {decisions_by_path[path]['reason']} |")

    lines.extend(
        [
            "",
            "## Candidate Decisions",
            "",
            "| Path | Kind | Decision | Next Action |",
            "|---|---|---|---|",
        ]
    )
    for decision in result["decisions"]:
        lines.append(
            f"| `{decision['path']}` | {decision['kind']} | {decision['decision']} | {decision['next_action']} |"
        )

    (output / "source_candidate_inclusion_decision_report.md").write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Plan V1.1 source candidate inclusion without staging candidates."
    )
    parser.add_argument("--assessment", default=str(DEFAULT_ASSESSMENT_PATH))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    args = parser.parse_args()
    result = build_source_candidate_inclusion_decision(
        assessment_path=args.assessment,
        output_dir=args.output_dir,
    )
    summary = {
        "schema": result["schema"],
        "ok": result["ok"],
        "source_candidate_count": result["source_candidate_count"],
        "next_stage_pathspec_count": result["next_stage_pathspec_count"],
        "deferred_pathspec_count": result["deferred_pathspec_count"],
        "explicit_approval_required_before_stage": result["explicit_approval_required_before_stage"],
        "git_stage_executed": result["git_stage_executed"],
        "destructive_action_taken": result["destructive_action_taken"],
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
