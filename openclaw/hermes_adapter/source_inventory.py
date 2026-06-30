from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

CORE_MODULES = {
    "agent_init": "agent/agent_init.py",
    "conversation_loop": "agent/conversation_loop.py",
    "tool_mapping": "acp_adapter/tools.py",
    "permission_bridge": "acp_adapter/permissions.py",
    "error_classifier": "agent/error_classifier.py",
    "memory_manager": "agent/memory_manager.py",
    "context_compressor": "agent/context_compressor.py",
    "skill_loop": "tools/skill_manager.py",
    "dashboard": "hermes_dashboard.py",
    "migration": "hermes_cli/migrate.py",
    "acp_adapter": "acp_adapter/server.py",
    "scheduled_automation": "cron",
    "subagent_delegation": "tools/delegate_task.py",
    "final_report_audit": "reports",
}

def build_inventory(root: str | Path = "research/hermes/hermes-agent") -> dict:
    base = Path(root)
    items: List[Dict] = []
    for name, rel in CORE_MODULES.items():
        candidates = []
        target = base / rel
        if target.exists():
            candidates.append(target)
        else:
            stem = Path(rel).name
            candidates.extend(base.rglob(stem)) if base.exists() and stem not in {"cron", "reports"} else None
        items.append({
            "module": name,
            "expected_path": str(target),
            "found": bool(candidates),
            "paths": [str(p) for p in candidates[:10]],
            "strategy": "inventory_only_no_runtime_copy",
        })
    return {"schema": "ogk.hermes_source_inventory.v1", "root": str(base), "core_module_count": len(items), "items": items}
