from __future__ import annotations

def build_gap_audit(mapping: dict) -> str:
    lines = ["# Hermes Gap Audit", "", "| Module | Conclusion | Gap |", "|---|---|---|"]
    for item in mapping.get("items", []):
        lines.append(f"| {item['hermes_module']} | {item['acceptance_conclusion']} | {item['gap']} |")
    return "\n".join(lines) + "\n"
