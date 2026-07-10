from __future__ import annotations

from pathlib import Path

from tools.verify_v1_1_root_policy_shadow_disposition import (
    build_root_policy_shadow_disposition,
    parse_simple_yaml_scalars,
)


def test_parse_simple_yaml_scalars_ignores_comments_and_blank_lines() -> None:
    parsed = parse_simple_yaml_scalars(
        """
        # comment
        version: OGK-Final-1.0

        policy: repair_policy
        forbid_secret_output: true
        """
    )

    assert parsed == {
        "version": "OGK-Final-1.0",
        "policy": "repair_policy",
        "forbid_secret_output": "true",
    }


def test_root_policy_shadow_disposition_excludes_untracked_policy(tmp_path: Path) -> None:
    (tmp_path / "openclaw" / "policies").mkdir(parents=True)
    (tmp_path / "openclaw" / "policies" / "policy.json").write_text(
        '{"version": "OGK-Final-1.0"}\n',
        encoding="utf-8",
    )
    (tmp_path / "policies").mkdir()
    (tmp_path / "policies" / "repair_policy.yaml").write_text(
        "\n".join(
            [
                "version: OGK-Final-1.0",
                "policy: repair_policy",
                "default: safe_by_policy",
                "forbid_destructive_without_authorization: true",
                "forbid_secret_output: true",
                "",
            ]
        ),
        encoding="utf-8",
    )

    result = build_root_policy_shadow_disposition(
        paths=["policies/repair_policy.yaml"],
        output_dir=tmp_path / "reports",
        root=tmp_path,
        tracked_paths=set(),
    )

    assert result["ok"] is True
    assert result["policy_shadow_count"] == 1
    assert result["excluded_pathspec"] == ["policies/repair_policy.yaml"]
    assert result["explicit_approval_required_before_stage"] is True
    assert result["explicit_approval_required_before_delete"] is True
    assert result["git_stage_executed"] is False
    assert result["destructive_action_taken"] is False

    inspection = result["inspections"][0]
    assert inspection["policy_name"] == "repair_policy"
    assert inspection["version_matches_package_policy"] is True
    assert inspection["safe_default"] is True
    assert inspection["forbids_secret_output"] is True
    assert inspection["recommended_disposition"] == "exclude_from_v1_1_manifest_pending_owner_adr"
    assert (tmp_path / "reports" / "root_policy_shadow_disposition_result.json").exists()
    assert (tmp_path / "reports" / "root_policy_shadow_disposition_report.md").exists()
