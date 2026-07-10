from __future__ import annotations

import json
from pathlib import Path

from openclaw.evidence.artifact_registry import ArtifactRegistry
from tools.verify_artifact_registry_hashes import verify_artifact_registry_hashes


def test_artifact_registry_hash_verifier_accepts_registered_artifacts(tmp_path: Path) -> None:
    artifact = tmp_path / "release-note.md"
    artifact.write_text("# Release fixture\n", encoding="utf-8")
    registry_path = tmp_path / "artifact_registry.json"
    ArtifactRegistry(registry_path).register(
        artifact,
        phase="PHASE_TEST",
        kind="report",
    )

    result = verify_artifact_registry_hashes(
        registry_path=registry_path,
        output_dir=tmp_path,
    )

    assert result["ok"] is True
    assert result["missing"] == []
    assert result["mismatched"] == []
    assert result["artifact_count"] == 1
    assert (tmp_path / "artifact_hash_result.json").exists()
    assert (tmp_path / "artifact_hash_report.md").exists()


def test_artifact_registry_hash_verifier_reports_missing_required_artifact(tmp_path: Path) -> None:
    data = {
        "schema": "ogk.artifact_registry.v1",
        "artifacts": [
            {
                "path": str(tmp_path / "missing.md"),
                "phase": "PHASE_TEST",
                "kind": "report",
                "required": True,
                "size": 10,
                "sha256": "0" * 64,
            }
        ],
    }
    registry = tmp_path / "artifact_registry.json"
    registry.write_text(json.dumps(data), encoding="utf-8")

    result = verify_artifact_registry_hashes(registry_path=registry, output_dir=tmp_path)

    assert result["ok"] is False
    assert result["missing"] == [str(tmp_path / "missing.md")]
