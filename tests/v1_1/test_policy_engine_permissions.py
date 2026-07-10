from __future__ import annotations

import pytest

from openclaw.governance.policy_engine import (
    CHECK,
    DESTRUCTIVE,
    EXTERNAL_SIDE_EFFECT,
    SAFE_READ,
    SAFE_WRITE,
    SECRET_ACCESS,
    PolicyEngine,
)


@pytest.mark.parametrize(
    ("action", "target", "expected_risk"),
    [
        ("read", "reports/final/current_state.json", SAFE_READ),
        ("scan", "reports/events/openclaw-governance-events.jsonl", SAFE_READ),
        ("hash", "reports/final/artifact_registry.json", SAFE_READ),
        ("validate", "reports/final/current_state.json", CHECK),
        ("write", "reports/v1_1/phase_01/probe.txt", SAFE_WRITE),
    ],
)
def test_policy_allows_safe_phase_01_actions(action: str, target: str, expected_risk: str) -> None:
    decision = PolicyEngine().decide(action, target)

    assert decision.allowed is True
    assert decision.risk == expected_risk


@pytest.mark.parametrize(
    ("action", "target", "expected_risk"),
    [
        ("delete", "reports/final/current_state.json", DESTRUCTIVE),
        ("write", "api_key.txt", SECRET_ACCESS),
        ("curl", "https://example.com/upload", EXTERNAL_SIDE_EFFECT),
        ("git reset --hard", "ogk-final-v1.0", DESTRUCTIVE),
        ("write", "authorization token", SECRET_ACCESS),
    ],
)
def test_policy_blocks_high_risk_actions(action: str, target: str, expected_risk: str) -> None:
    decision = PolicyEngine().decide(action, target)

    assert decision.allowed is False
    assert decision.risk == expected_risk
