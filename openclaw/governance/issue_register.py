from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

class IssueRegister:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text(json.dumps({"schema": "ogk.issue_register.v1", "issues": []}, indent=2), encoding="utf-8")

    def data(self) -> Dict[str, Any]:
        return json.loads(self.path.read_text(encoding="utf-8"))

    def write(self, data: Dict[str, Any]) -> None:
        self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")

    def open_issues(self, severities: set[str] | None = None) -> List[Dict[str, Any]]:
        issues = [i for i in self.data().get("issues", []) if i.get("status") not in {"closed", "resolved"}]
        if severities:
            issues = [i for i in issues if i.get("severity") in severities]
        return issues

    def has_blocking(self) -> bool:
        return bool(self.open_issues({"BLOCKER", "HIGH", "High", "Critical"}))
