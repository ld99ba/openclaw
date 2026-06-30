from __future__ import annotations

PHASES = [f"PHASE_{i:02d}" for i in range(1, 8)]

class Supervisor:
    def __init__(self) -> None:
        self.phases = PHASES

    def next_phase(self, accepted: set[str]) -> str | None:
        for phase in self.phases:
            if phase not in accepted:
                return phase
        return None
