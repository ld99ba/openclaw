from __future__ import annotations

import json
from pathlib import Path

class DashboardExporter:
    def export(self, state_path: str, output_path: str) -> dict:
        state = json.loads(Path(state_path).read_text(encoding="utf-8"))
        view = {"schema": "ogk.dashboard.v1", "source": state_path, "final_status": state.get("final_status"), "release_status": state.get("release_status"), "read_only": True}
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_text(json.dumps(view, ensure_ascii=False, indent=2), encoding="utf-8")
        return view
