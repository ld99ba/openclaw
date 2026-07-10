from __future__ import annotations

class RepairEngine:
    allowed_auto_levels = {"R0", "R1", "R2"}
    def can_auto_repair(self, level: str, *, has_secret=False, destructive=False, external=False, core_runtime=False) -> bool:
        if has_secret or destructive or external or core_runtime:
            return False
        return level in self.allowed_auto_levels
