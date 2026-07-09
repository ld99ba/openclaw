from __future__ import annotations

from pathlib import Path

from tools.verify_v1_1_source_inclusion_preflight import (
    build_source_inclusion_preflight,
    json_status,
    preflight_candidate,
    python_syntax_status,
)


def test_python_syntax_status_detects_top_level_print(tmp_path: Path) -> None:
    path = tmp_path / "__main__.py"
    path.write_text('"""entrypoint"""\nprint("ready")\n', encoding="utf-8")

    result = python_syntax_status(path)

    assert result["python_syntax_ok"] is True
    assert result["top_level_print_call"] is True
    assert result["module_docstring"] == "entrypoint"


def test_json_status_reports_top_level_keys(tmp_path: Path) -> None:
    path = tmp_path / "policy.json"
    path.write_text('{"version": "OGK-Final-1.0", "repair_levels": {}}', encoding="utf-8")

    result = json_status(path)

    assert result["json_parse_ok"] is True
    assert result["json_top_level_keys"] == ["repair_levels", "version"]


def test_preflight_candidate_blocks_missing_and_root_policy_shadow(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "policies").mkdir()
    (tmp_path / "policies" / "repair_policy.yaml").write_text("policy: repair\n", encoding="utf-8")

    missing = preflight_candidate("openclaw/missing.py", tracked_paths=set())
    shadow = preflight_candidate("policies/repair_policy.yaml", tracked_paths=set())

    assert missing["blocking_issues"] == ["candidate_path_missing"]
    assert "root_policy_shadow_not_allowed_in_preflight" in shadow["blocking_issues"]


def test_build_source_inclusion_preflight_is_read_only_and_approval_gated(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "openclaw" / "hermes_adapter").mkdir(parents=True)
    (tmp_path / "openclaw" / "governance").mkdir(parents=True)
    (tmp_path / "openclaw" / "hermes_adapter" / "__main__.py").write_text(
        '"""entrypoint"""\nprint("ready")\n',
        encoding="utf-8",
    )
    (tmp_path / "openclaw" / "governance" / "project_spec.json").write_text(
        '{"version": "OGK-Final-1.0"}',
        encoding="utf-8",
    )

    result = build_source_inclusion_preflight(
        decision_result={
            "next_stage_pathspec": [
                "openclaw/hermes_adapter/__main__.py",
                "openclaw/governance/project_spec.json",
            ],
        },
        output_dir=tmp_path / "reports",
    )

    assert result["ok"] is True
    assert result["candidate_count"] == 2
    assert result["blocking_issue_count"] == 0
    assert result["warning_count"] == 2
    assert result["explicit_approval_required_before_stage"] is True
    assert result["git_stage_executed"] is False
    assert result["destructive_action_taken"] is False
    assert result["files_moved_or_deleted"] is False
    assert (tmp_path / "reports" / "source_inclusion_preflight_result.json").exists()
    assert (tmp_path / "reports" / "source_inclusion_preflight_report.md").exists()
