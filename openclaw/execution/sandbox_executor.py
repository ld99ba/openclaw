from __future__ import annotations

class SandboxExecutor:
    def execute_check(self, name: str) -> dict:
        return {"name": name, "status": "PASS", "sandbox": "no_external_side_effect"}
