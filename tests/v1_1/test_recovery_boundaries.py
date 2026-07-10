from __future__ import annotations

import json
from pathlib import Path

import pytest

from openclaw.evidence.event_ledger import EventLedger
from openclaw.recovery.error_taxonomy import classify_error
from openclaw.recovery.resume_protocol import ResumeProtocol
from tools.verify_recovery_boundaries import assess_interruption, verify_recovery_boundaries


@pytest.mark.parametrize(
    ("message", "expected_class", "expected_recovery"),
    [
        ("HTTP 429 rate_limit from provider", "rate_limit", "backoff"),
        ("timeout while waiting for model", "timeout", "retry_or_lighten_context"),
        ("context_overflow in prompt assembly", "context_overflow", "compress_context"),
        ("payload_too_large from gateway", "payload_too_large", "reduce_payload"),
        ("permission_denied by policy", "permission_denied", "policy_block"),
        ("402 credit exhausted", "billing", "switch_provider_or_block"),
    ],
)
def test_error_taxonomy_classifies_recoverable_interruptions(
    message: str,
    expected_class: str,
    expected_recovery: str,
) -> None:
    result = classify_error(message)

    assert result == {"class": expected_class, "recovery": expected_recovery}


@pytest.mark.parametrize(
    ("message", "expected_level", "expected_auto"),
    [
        ("HTTP 429 rate_limit from provider", "R1", True),
        ("timeout while waiting for model", "R1", True),
        ("model_not_found from provider", "R2", True),
        ("auth token rejected", "R3", False),
        ("destructive_action requested", "R4", False),
    ],
)
def test_repair_engine_maps_interruptions_to_bounded_repair_levels(
    message: str,
    expected_level: str,
    expected_auto: bool,
) -> None:
    assessment = assess_interruption(message)

    assert assessment["repair_level"] == expected_level
    assert assessment["auto_repair_allowed"] is expected_auto
    assert assessment["requires_human_authorization"] is (not expected_auto)


@pytest.mark.parametrize(
    "boundary",
    ["has_secret", "destructive", "external", "core_runtime"],
)
def test_repair_engine_blocks_auto_repair_across_authorization_boundaries(boundary: str) -> None:
    kwargs = {boundary: True}

    assessment = assess_interruption("timeout while waiting for model", **kwargs)

    assert assessment["repair_level"] == "R1"
    assert assessment["auto_repair_allowed"] is False
    assert assessment["requires_human_authorization"] is True


def test_resume_protocol_rebuilds_state_from_fixture_ledger(tmp_path: Path) -> None:
    ledger_path = tmp_path / "events.jsonl"
    registry_path = tmp_path / "artifact_registry.json"
    registry_path.write_text(json.dumps({"schema": "ogk.artifact_registry.v1", "artifacts": []}), encoding="utf-8")
    ledger = EventLedger(ledger_path)
    ledger.append("STATE_ADVANCED", "PHASE_01", "phase_one")
    ledger.append("QUALITY_GATE_PASSED", "PHASE_02", "phase_two")
    ledger.append("FINAL_SEAL_PASSED", "PHASE_07", "seal")
    ledger.append("RELEASE_ACCEPTED", "PHASE_07", "release")

    state = ResumeProtocol(str(ledger_path), str(registry_path)).rebuild()

    assert state["ledger_ok"] is True
    assert state["artifact_registry_ok"] is True
    assert state["accepted_phases"] == ["PHASE_01", "PHASE_02"]
    assert state["final_status"] == "FINAL_SUCCESS"
    assert state["release_status"] == "RELEASE_ACCEPTED"


def test_recovery_boundary_verifier_writes_phase_02_reports(tmp_path: Path) -> None:
    result = verify_recovery_boundaries(output_dir=tmp_path)

    assert result["ok"] is True
    assert result["case_count"] >= 8
    assert (tmp_path / "recovery_boundaries_result.json").exists()
    assert (tmp_path / "recovery_boundaries_report.md").exists()
