from __future__ import annotations

import json
from pathlib import Path

from tools.verify_v1_1_release_readiness_gate import (
    PHASES,
    REQUIRED_RESULTS,
    ROOT_POLICY_SHADOWS,
    build_release_readiness_gate,
)


def write_summary(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("# Summary\n\nStatus: PASS\n", encoding="utf-8")


def write_json(path: Path, payload: dict | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload or {"ok": True}), encoding="utf-8")


def write_complete_phase_evidence(root: Path) -> None:
    for phase in PHASES:
        number = phase.split("_")[1]
        write_summary(root / "reports" / "v1_1" / phase / f"PHASE_{number}_SUMMARY.md")
        for filename in REQUIRED_RESULTS[phase]:
            write_json(root / "reports" / "v1_1" / phase / filename)
    write_json(
        root / "reports" / "v1_1" / "phase_13" / "root_policy_shadow_disposition_result.json",
        {
            "ok": True,
            "excluded_pathspec": list(ROOT_POLICY_SHADOWS),
            "explicit_approval_required_before_stage": True,
            "explicit_approval_required_before_delete": True,
        },
    )


def test_release_readiness_gate_passes_with_complete_evidence(tmp_path: Path) -> None:
    write_complete_phase_evidence(tmp_path)

    result = build_release_readiness_gate(
        output_dir=tmp_path / "out",
        root=tmp_path,
        tracked_policy_shadows=set(),
    )

    assert result["ok"] is True
    assert result["phase_count"] == 13
    assert result["failure_count"] == 0
    assert result["tracked_root_policy_shadows"] == []
    assert result["release_publication_performed"] is False
    assert result["tag_move_performed"] is False
    assert result["explicit_approval_required_before_release_publication"] is True
    assert (tmp_path / "out" / "release_readiness_gate_result.json").exists()
    assert (tmp_path / "out" / "release_readiness_gate_report.md").exists()


def test_release_readiness_gate_fails_when_policy_shadow_is_tracked(tmp_path: Path) -> None:
    write_complete_phase_evidence(tmp_path)

    result = build_release_readiness_gate(
        output_dir=tmp_path / "out",
        root=tmp_path,
        tracked_policy_shadows={"policies/repair_policy.yaml"},
    )

    assert result["ok"] is False
    assert result["failure_count"] == 1
    assert "root policy shadows are tracked" in result["failures"][0]
