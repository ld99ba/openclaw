from __future__ import annotations

from pathlib import Path

from tools.propose_v1_1_workspace_hygiene import (
    build_hygiene_proposal,
    categorize_paths,
)


def test_hygiene_proposal_classifies_paths_and_stays_read_only(tmp_path: Path) -> None:
    result = build_hygiene_proposal(
        paths=[
            "node_modules/pkg/index.js",
            "reports/.archive/old.json",
            "reports/final/current_state.json",
            "unknown/file.txt",
            "tests/v1_1/__pycache__/case.pyc",
        ],
        gitignore_entries={"/main/"},
        output_dir=tmp_path,
    )

    assert result["ok"] is True
    assert result["destructive_action_taken"] is False
    assert result["direct_file_mutation_taken"] is False
    assert result["gitignore_updated"] is False
    assert result["git_stage_executed"] is False
    assert "reports/**" not in result["safe_gitignore_additions"]
    assert "reports/final/**" not in result["safe_gitignore_additions"]
    assert result["category_counts"]["generated_cache"] == 2
    assert result["category_counts"]["historical_report_or_runtime_evidence"] == 1
    assert result["category_counts"]["v1_0_baseline_preserve"] == 1
    assert result["category_counts"]["unknown_review_required"] == 1
    assert (tmp_path / "workspace_hygiene_proposal_result.json").exists()
    assert (tmp_path / "workspace_hygiene_proposal_report.md").exists()


def test_hygiene_proposal_respects_existing_gitignore_entries(tmp_path: Path) -> None:
    result = build_hygiene_proposal(
        paths=[".pytest_cache/v/cache/nodeids", "node_modules/pkg/index.js"],
        gitignore_entries={"/main/", ".pytest_cache/", "node_modules/"},
        output_dir=tmp_path,
    )

    assert ".pytest_cache/" not in result["safe_gitignore_additions"]
    assert "node_modules/" not in result["safe_gitignore_additions"]
    assert "__pycache__/" in result["safe_gitignore_additions"]


def test_categorize_paths_sorts_categories() -> None:
    categories = categorize_paths(
        [
            "z.py",
            "reports/v1_1/phase_05/result.json",
            "reports/final/current_state.json",
        ]
    )

    assert list(categories) == [
        "unknown_review_required",
        "v1_0_baseline_preserve",
        "v1_1_release_candidate",
    ]
