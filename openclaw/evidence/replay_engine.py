from __future__ import annotations

from pathlib import Path
from typing import Any, Dict
from .event_ledger import EventLedger
from .artifact_registry import ArtifactRegistry

class ReplayEngine:
    def __init__(self, ledger_path: str | Path, artifact_registry_path: str | Path) -> None:
        self.ledger = EventLedger(ledger_path)
        self.registry = ArtifactRegistry(artifact_registry_path)

    def rebuild_state(self) -> Dict[str, Any]:
        verification = self.ledger.verify()
        events = self.ledger.events()
        accepted = sorted({e["phase"] for e in events if e["event_type"] in {"QUALITY_GATE_PASSED", "STATE_ADVANCED"} and e["phase"].startswith("PHASE_")})
        final = any(e["event_type"] == "FINAL_SEAL_PASSED" for e in events)
        release = any(e["event_type"] == "RELEASE_ACCEPTED" for e in events)
        return {
            "schema": "ogk.rebuilt_state.v1",
            "ledger_ok": verification.get("ok", False),
            "event_count": len(events),
            "accepted_phases": accepted,
            "final_status": "FINAL_SUCCESS" if final else "RUNNING",
            "release_status": "RELEASE_ACCEPTED" if release else "PENDING",
            "artifact_registry_ok": self.registry.verify().get("ok", False),
        }
