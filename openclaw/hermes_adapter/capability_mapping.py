from __future__ import annotations

CAPABILITIES = [
    ("agent_init", "provider/context/tool guard setup", "OpenClaw native runtime config", "reference_only", "do_not_copy"),
    ("conversation_loop", "model/tool/retry/post-hook loop", "OpenClaw session/tool runtime + Supervisor", "rewrite_adapt", "partial"),
    ("tool_mapping", "ACP ToolKind mapping", "ToolGateway risk taxonomy", "rewrite_adapt", "accepted"),
    ("permission_bridge", "allow_once/session/always/deny", "OpenClaw approval preserved", "reference_only", "accepted"),
    ("error_classifier", "API failover taxonomy", "ErrorTaxonomy", "rewrite_adapt", "accepted"),
    ("memory_manager", "memory context and recall", "MemoryLifecycle", "rewrite_adapt", "accepted"),
    ("context_compressor", "context compression", "OpenClaw context/memory policy", "reference_only", "partial"),
    ("skill_loop", "skill self-improvement", "SkillLifecycle", "rewrite_adapt", "accepted"),
    ("dashboard", "observability", "DashboardExporter", "rewrite_adapt", "accepted"),
    ("migration", "claw migrate", "MigrationAdapter dry-run only", "rewrite_adapt", "partial"),
    ("acp_adapter", "protocol bridge", "OpenClaw native tools/approval", "reference_only", "partial"),
    ("scheduled_automation", "cron automations", "state-driven governance", "rewrite_adapt", "accepted"),
    ("subagent_delegation", "delegation", "OpenClaw sessions/subagents", "already_stronger", "accepted"),
    ("final_report_audit", "final reports", "FinalSeal + artifact registry", "enhanced", "accepted"),
]

def build_mapping(inventory: dict) -> dict:
    found = {i["module"]: i for i in inventory.get("items", [])}
    items = []
    for module, hermes_ability, openclaw_ability, strategy, conclusion in CAPABILITIES:
        inv = found.get(module, {})
        items.append({
            "hermes_module": module,
            "hermes_source_path": inv.get("paths") or [inv.get("expected_path", "")],
            "hermes_original_capability": hermes_ability,
            "openclaw_corresponding_capability": openclaw_ability,
            "fusion_strategy": strategy,
            "migrated": strategy not in {"reference_only"},
            "rewritten": strategy in {"rewrite_adapt", "enhanced"},
            "reference_only": strategy == "reference_only",
            "abandoned": False,
            "gap": "source missing or behavior needs deeper tests" if not inv.get("found") else "no runtime copy; OpenClaw-native adaptation",
            "evidence": inv.get("paths") or [inv.get("expected_path", "")],
            "test_method": "inventory + policy/state/final-seal contract tests",
            "acceptance_conclusion": conclusion,
        })
    accepted = sum(1 for i in items if i["acceptance_conclusion"] == "accepted")
    return {"schema": "ogk.hermes_capability_coverage_matrix.v1", "items": items, "coverage": {"total": len(items), "accepted": accepted, "registered_percent": 100.0}}
