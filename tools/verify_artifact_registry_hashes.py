from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from openclaw.evidence.artifact_registry import ArtifactRegistry


def _write_report(output_dir: Path, result: dict[str, Any]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "artifact_hash_result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    status = "PASS" if result["ok"] else "FAIL"
    lines = [
        "# V1.1 ArtifactRegistry Hash Verification",
        "",
        f"Status: {status}",
        f"Artifact Count: {result['artifact_count']}",
        f"Missing: {len(result['missing'])}",
        f"Mismatched: {len(result['mismatched'])}",
        "",
    ]
    (output_dir / "artifact_hash_report.md").write_text("\n".join(lines), encoding="utf-8")


def verify_artifact_registry_hashes(registry_path: Path, output_dir: Path) -> dict[str, Any]:
    registry = ArtifactRegistry(registry_path)
    verification = registry.verify()
    data = registry.data()
    result = {
        "schema": "ogk.v1_1.artifact_hash_result.v1",
        "ok": bool(verification.get("ok")),
        "artifact_count": len(data.get("artifacts", [])),
        "missing": verification.get("missing", []),
        "mismatched": verification.get("mismatched", []),
    }
    _write_report(output_dir, result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify OGK V1.1 ArtifactRegistry hashes.")
    parser.add_argument("--registry", default="reports/final/artifact_registry.json")
    parser.add_argument("--output-dir", default="reports/v1_1/phase_01")
    args = parser.parse_args()
    result = verify_artifact_registry_hashes(Path(args.registry), Path(args.output_dir))
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
