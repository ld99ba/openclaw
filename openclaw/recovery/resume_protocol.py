from __future__ import annotations

from pathlib import Path
from openclaw.evidence.replay_engine import ReplayEngine

class ResumeProtocol:
    def __init__(self, ledger_path: str, artifact_registry_path: str) -> None:
        self.replay = ReplayEngine(ledger_path, artifact_registry_path)

    def rebuild(self) -> dict:
        return self.replay.rebuild_state()
