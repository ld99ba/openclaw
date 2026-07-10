from __future__ import annotations

from pathlib import Path

import pytest

from openclaw.evidence.event_ledger import EventLedger
from openclaw.execution.tool_gateway import ToolGateway
from openclaw.governance.policy_engine import PolicyEngine


def make_gateway(tmp_path: Path) -> ToolGateway:
    return ToolGateway(
        policy=PolicyEngine(),
        ledger=EventLedger(tmp_path / "events.jsonl"),
    )


def test_tool_gateway_safe_write_records_event(tmp_path: Path) -> None:
    gateway = make_gateway(tmp_path)
    output = tmp_path / "reports" / "v1_1" / "phase_01" / "probe.txt"

    gateway.safe_write_text(output, "ok", "PHASE_01", "safe_write_probe")

    assert output.read_text(encoding="utf-8") == "ok"
    events = gateway.ledger.events()
    assert len(events) == 1
    assert events[0]["event_type"] == "STEP_ACTION_EXECUTED"
    assert events[0]["policy_decision"] == "SAFE_WRITE"


@pytest.mark.parametrize(
    ("action", "target"),
    [
        ("delete", "reports/final/current_state.json"),
        ("write", "secret token"),
        ("curl", "https://example.com/upload"),
        ("git reset --hard", "ogk-final-v1.0"),
    ],
)
def test_tool_gateway_classifies_blocked_actions(tmp_path: Path, action: str, target: str) -> None:
    gateway = make_gateway(tmp_path)

    decision = gateway.classify_only(action, target)

    assert decision["allowed"] is False


def test_tool_gateway_safe_write_rejects_secret_target(tmp_path: Path) -> None:
    gateway = make_gateway(tmp_path)

    with pytest.raises(PermissionError):
        gateway.safe_write_text(tmp_path / "api_key.txt", "secret", "PHASE_01", "secret_probe")
