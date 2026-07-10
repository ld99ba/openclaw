from __future__ import annotations

import re
from dataclasses import dataclass

SAFE_READ = "SAFE_READ"
SAFE_WRITE = "SAFE_WRITE"
CHECK = "CHECK"
METADATA_REPAIR = "METADATA_REPAIR"
CONFIG_REPAIR = "CONFIG_REPAIR"
CODE_REPAIR = "CODE_REPAIR"
DANGEROUS_WRITE = "DANGEROUS_WRITE"
DESTRUCTIVE = "DESTRUCTIVE"
EXTERNAL_SIDE_EFFECT = "EXTERNAL_SIDE_EFFECT"
SECRET_ACCESS = "SECRET_ACCESS"

@dataclass(frozen=True)
class PolicyDecision:
    allowed: bool
    risk: str
    reason: str

class PolicyEngine:
    destructive = re.compile(r"\b(rm\s+-rf|truncate|mkfs|dd\s+if=|git\s+reset\s+--hard|delete\b|clear\b)", re.I)
    external = re.compile(r"\b(curl|wget|scp|ssh|send|tweet|email)\b", re.I)
    secret = re.compile(r"\b(api[_-]?key|token|secret|authorization|password)\b", re.I)

    def classify(self, action: str, target: str = "") -> str:
        text = f"{action} {target}"
        if self.secret.search(text):
            return SECRET_ACCESS
        if self.destructive.search(text):
            return DESTRUCTIVE
        if self.external.search(text):
            return EXTERNAL_SIDE_EFFECT
        if action in {"read", "scan", "hash", "validate"}:
            return SAFE_READ if action in {"read", "scan", "hash"} else CHECK
        if action in {"write", "mkdir", "register_artifact", "append_event"}:
            return SAFE_WRITE
        if action == "metadata_repair":
            return METADATA_REPAIR
        if action == "config_repair":
            return CONFIG_REPAIR
        if action == "code_repair":
            return CODE_REPAIR
        return DANGEROUS_WRITE

    def decide(self, action: str, target: str = "") -> PolicyDecision:
        risk = self.classify(action, target)
        if risk in {SAFE_READ, SAFE_WRITE, CHECK, METADATA_REPAIR}:
            return PolicyDecision(True, risk, "allowed_by_ogk_policy")
        if risk == CONFIG_REPAIR:
            return PolicyDecision(False, risk, "requires_explicit_policy_allowance")
        if risk == CODE_REPAIR:
            return PolicyDecision(False, risk, "requires_independent_repair_phase")
        return PolicyDecision(False, risk, "blocked_or_requires_human_authorization")
