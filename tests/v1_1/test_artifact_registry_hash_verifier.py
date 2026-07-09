from __future__ import annotations

import json
from pathlib import Path

from tools.verify_artifact_registry_hashes import verify_artifact_registry_hashes


def test_artifact_registry_hash_verifier_accepts_v1_0_baseline(tmp_path: Path) -> None:
    result = verify_artifact_registry_hashes(
        registry_path=Path("reports/final/artifact_registry.json"),
        output_dir=tmp_path,
    )

    assert result["ok"] is True
    assert result["missing"] == []
    assert result["mismatched"] == []
    assert result["artifact_count"] > 0
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
