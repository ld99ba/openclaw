from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable
from .issue_register import IssueRegister
from openclaw.evidence.event_ledger import EventLedger
from openclaw.evidence.artifact_registry import ArtifactRegistry

class QualityGate:
    def __init__(self, issue_register: IssueRegister, ledger: EventLedger, artifact_registry: ArtifactRegistry) -> None:
        self.issue_register = issue_register
        self.ledger = ledger
        self.artifact_registry = artifact_registry

    def evaluate_phase(self, phase: str, required_artifacts: Iterable[str]) -> Dict[str, Any]:
        missing = [p for p in required_artifacts if not Path(p).exists()]
        ledger_ok = self.ledger.verify().get("ok", False)
        registry_ok = self.artifact_registry.verify().get("ok", False)
        blocking = self.issue_register.open_issues({"BLOCKER", "HIGH", "High", "Critical"})
        passed = not missing and ledger_ok and registry_ok and not blocking
        return {
            "schema": "ogk.quality_gate_result.v1",
            "phase": phase,
            "status": "PASS" if passed else "FAIL",
            "missing_artifacts": missing,
            "ledger_ok": ledger_ok,
            "artifact_registry_ok": registry_ok,
            "blocking_issues": [i.get("id") for i in blocking],
        }
