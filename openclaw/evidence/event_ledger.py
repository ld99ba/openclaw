from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

EVENT_TYPES = {
    "PROJECT_INITIALIZED", "SPEC_LOADED", "STATE_REBUILT", "STEP_STARTED", "STEP_ACTION_EXECUTED",
    "ARTIFACT_CREATED", "ARTIFACT_HASHED", "QUALITY_GATE_PASSED", "QUALITY_GATE_FAILED",
    "ISSUE_OPENED", "ISSUE_REPAIRED", "ISSUE_CLOSED", "AUDIT_WRITTEN", "STATE_ADVANCED",
    "REPAIR_STARTED", "REPAIR_COMPLETED", "REPAIR_FAILED", "BLOCKER_RAISED", "RESUME_STARTED",
    "RESUME_COMPLETED", "FINAL_SEAL_STARTED", "FINAL_SEAL_PASSED", "FINAL_SEAL_FAILED",
    "RELEASE_ACCEPTED",
}

class EventLedger:
    def __init__(self, path: str | Path, project_id: str = "openclaw_hermes_fusion") -> None:
        self.path = Path(path)
        self.project_id = project_id
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.touch(exist_ok=True)

    @staticmethod
    def _canonical(event: Dict[str, Any]) -> bytes:
        payload = {k: v for k, v in event.items() if k != "event_hash"}
        return json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")

    @classmethod
    def hash_event(cls, event: Dict[str, Any]) -> str:
        return hashlib.sha256(cls._canonical(event)).hexdigest()

    def events(self) -> List[Dict[str, Any]]:
        out: List[Dict[str, Any]] = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                out.append(json.loads(line))
        return out

    def last_hash(self) -> str:
        events = self.events()
        return events[-1]["event_hash"] if events else "GENESIS"

    def append(self, event_type: str, phase: str, step: str, *, inputs: Optional[List[str]] = None,
               outputs: Optional[List[str]] = None, artifacts: Optional[List[str]] = None,
               issues: Optional[List[str]] = None, policy_decision: str = "allow",
               quality_gate_result: str = "not_evaluated", actor: str = "openclaw-ogk") -> Dict[str, Any]:
        if event_type not in EVENT_TYPES:
            raise ValueError(f"unsupported event_type: {event_type}")
        event = {
            "event_id": str(uuid.uuid4()),
            "event_version": "1.0",
            "project_id": self.project_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "actor": actor,
            "event_type": event_type,
            "phase": phase,
            "step": step,
            "inputs": inputs or [],
            "outputs": outputs or [],
            "artifacts": artifacts or [],
            "issues": issues or [],
            "policy_decision": policy_decision,
            "quality_gate_result": quality_gate_result,
            "previous_event_hash": self.last_hash(),
        }
        event["event_hash"] = self.hash_event(event)
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")
        return event

    def verify(self) -> Dict[str, Any]:
        previous = "GENESIS"
        count = 0
        for event in self.events():
            count += 1
            if event.get("previous_event_hash") != previous:
                return {"ok": False, "reason": "previous_event_hash_mismatch", "event_id": event.get("event_id")}
            expected = self.hash_event(event)
            if event.get("event_hash") != expected:
                return {"ok": False, "reason": "event_hash_mismatch", "event_id": event.get("event_id")}
            previous = event["event_hash"]
        return {"ok": True, "event_count": count, "last_hash": previous}
