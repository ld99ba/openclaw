from __future__ import annotations

ALLOWED_STATES = {"PLANNED", "READY", "RUNNING", "WAITING", "REPAIRING", "VALIDATING", "ACCEPTED", "BLOCKED", "FAILED", "RELEASE_ACCEPTED", "FINAL_SUCCESS"}
ALLOWED_TRANSITIONS = {
    ("PLANNED", "READY"), ("READY", "RUNNING"), ("RUNNING", "VALIDATING"),
    ("VALIDATING", "ACCEPTED"), ("VALIDATING", "REPAIRING"), ("REPAIRING", "VALIDATING"),
    ("RUNNING", "BLOCKED"), ("BLOCKED", "REPAIRING"), ("ACCEPTED", "READY"),
    ("ACCEPTED", "FINAL_SUCCESS"), ("FINAL_SUCCESS", "RELEASE_ACCEPTED"),
}
FORBIDDEN_FINAL = {"PLANNED", "RUNNING", "FAILED", "BLOCKED", "WAITING"}
PHASES = [f"PHASE_{i:02d}" for i in range(1, 8)]

class StateMachine:
    def can_transition(self, source: str, target: str, *, final_ready: bool = False) -> bool:
        if source not in ALLOWED_STATES or target not in ALLOWED_STATES:
            return False
        if target == "FINAL_SUCCESS" and (source in FORBIDDEN_FINAL or not final_ready):
            return False
        return (source, target) in ALLOWED_TRANSITIONS

    def assert_transition(self, source: str, target: str, *, final_ready: bool = False) -> None:
        if not self.can_transition(source, target, final_ready=final_ready):
            raise ValueError(f"illegal transition: {source}->{target}")
