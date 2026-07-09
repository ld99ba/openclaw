from __future__ import annotations

from tools.propose_v1_1_workspace_hygiene import SAFE_GITIGNORE_ADDITIONS
from tools.verify_v1_1_gitignore_hygiene import (
    PROTECTED_SAMPLES,
    evaluate_gitignore,
    verify_gitignore_hygiene,
)


def test_evaluate_gitignore_requires_all_safe_patterns() -> None:
    result = evaluate_gitignore({"/main/", "__pycache__/"})

    assert result["forbidden_patterns_present"] == []
    assert "__pycache__/" not in result["missing_required_patterns"]
    assert "node_modules/" in result["missing_required_patterns"]


def test_evaluate_gitignore_blocks_broad_release_evidence_patterns() -> None:
    result = evaluate_gitignore(set(SAFE_GITIGNORE_ADDITIONS) | {"reports/**", "tools/**"})

    assert result["missing_required_patterns"] == []
    assert result["forbidden_patterns_present"] == ["reports/**", "tools/**"]


def test_gitignore_hygiene_verifier_keeps_protected_paths_visible(tmp_path) -> None:
    result = verify_gitignore_hygiene(output_dir=tmp_path)

    assert result["ok"] is True
    assert result["destructive_action_taken"] is False
    assert result["files_moved_or_deleted"] is False
    assert result["missing_required_patterns"] == []
    assert result["forbidden_patterns_present"] == []
    assert result["protected_sample_failures"] == []
    assert all(result["protected_sample_results"][path] is False for path in PROTECTED_SAMPLES)
    assert (tmp_path / "gitignore_hygiene_result.json").exists()
    assert (tmp_path / "gitignore_hygiene_report.md").exists()
