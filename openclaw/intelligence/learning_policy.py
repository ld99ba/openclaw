from __future__ import annotations

class LearningPolicy:
    def allow_learning_update(self, *, source: str, evidence: str) -> bool:
        return bool(source and evidence)
