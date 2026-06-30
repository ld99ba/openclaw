from __future__ import annotations

from pathlib import Path
from typing import Any
from openclaw.governance.policy_engine import PolicyEngine
from openclaw.evidence.event_ledger import EventLedger

class ToolGateway:
    def __init__(self, policy: PolicyEngine, ledger: EventLedger) -> None:
        self.policy = policy
        self.ledger = ledger

    def safe_write_text(self, path: str | Path, content: str, phase: str, step: str) -> None:
        decision = self.policy.decide("write", str(path))
        if not decision.allowed:
            raise PermissionError(decision.reason)
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        self.ledger.append("STEP_ACTION_EXECUTED", phase, step, outputs=[str(p)], policy_decision=decision.risk)

    def classify_only(self, action: str, target: str = "") -> dict[str, Any]:
        decision = self.policy.decide(action, target)
        return {"allowed": decision.allowed, "risk": decision.risk, "reason": decision.reason}
