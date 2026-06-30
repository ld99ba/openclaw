from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable
from openclaw.evidence.event_ledger import EventLedger
from openclaw.evidence.artifact_registry import ArtifactRegistry
from openclaw.governance.issue_register import IssueRegister
from openclaw.evidence.replay_engine import ReplayEngine

class FinalSeal:
    def __init__(self, ledger: EventLedger, registry: ArtifactRegistry, issues: IssueRegister, replay: ReplayEngine) -> None:
        self.ledger = ledger
        self.registry = registry
        self.issues = issues
        self.replay = replay

    def evaluate(self, required_phases: Iterable[str], required_artifacts: Iterable[str]) -> Dict:
        events = self.ledger.events()
        accepted = {e["phase"] for e in events if e["event_type"] == "QUALITY_GATE_PASSED"}
        missing_phases = [p for p in required_phases if p not in accepted]
        missing_artifacts = [p for p in required_artifacts if not Path(p).exists()]
        ledger_ok = self.ledger.verify().get("ok", False)
        registry_ok = self.registry.verify().get("ok", False)
        replay_state = self.replay.rebuild_state()
        blocking = self.issues.open_issues({"BLOCKER", "HIGH", "High", "Critical"})
        passed = not missing_phases and not missing_artifacts and ledger_ok and registry_ok and replay_state.get("ledger_ok") and not blocking
        return {
            "schema": "ogk.final_seal_result.v1",
            "status": "FINAL_SUCCESS" if passed else "FINAL_SEAL_FAILED",
            "release_status": "RELEASE_ACCEPTED" if passed else "PENDING",
            "missing_phases": missing_phases,
            "missing_artifacts": missing_artifacts,
            "ledger_ok": ledger_ok,
            "artifact_registry_ok": registry_ok,
            "state_rebuild_ok": replay_state.get("ledger_ok", False),
            "replay_result": replay_state,
            "blocking_issues": [i.get("id") for i in blocking],
        }
