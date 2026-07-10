from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List

class ArtifactRegistry:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text(json.dumps({"schema": "ogk.artifact_registry.v1", "artifacts": []}, indent=2), encoding="utf-8")

    @staticmethod
    def sha256(path: str | Path) -> str:
        h = hashlib.sha256()
        with Path(path).open("rb") as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                h.update(chunk)
        return h.hexdigest()

    def data(self) -> Dict[str, Any]:
        return json.loads(self.path.read_text(encoding="utf-8"))

    def register(self, artifact_path: str | Path, phase: str, kind: str, required: bool = True) -> Dict[str, Any]:
        p = Path(artifact_path)
        if not p.exists():
            raise FileNotFoundError(str(p))
        entry = {
            "path": str(p),
            "phase": phase,
            "kind": kind,
            "required": required,
            "size": p.stat().st_size,
            "sha256": self.sha256(p),
        }
        data = self.data()
        data["artifacts"] = [x for x in data.get("artifacts", []) if x.get("path") != entry["path"]]
        data["artifacts"].append(entry)
        self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        return entry

    def verify(self) -> Dict[str, Any]:
        missing: List[str] = []
        mismatched: List[str] = []
        for entry in self.data().get("artifacts", []):
            p = Path(entry["path"])
            if not p.exists():
                if entry.get("required", True):
                    missing.append(entry["path"])
                continue
            if self.sha256(p) != entry.get("sha256"):
                # Active event ledger is append-only and verified by its hash chain;
                # final release snapshots register a stable ledger hash after sealing.
                if entry.get("path") == "reports/events/openclaw-governance-events.jsonl":
                    continue
                mismatched.append(entry["path"])
        return {"ok": not missing and not mismatched, "missing": missing, "mismatched": mismatched}
