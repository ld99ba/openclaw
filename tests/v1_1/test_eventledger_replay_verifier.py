from __future__ import annotations

import json
from pathlib import Path

from openclaw.evidence.artifact_registry import ArtifactRegistry
from openclaw.evidence.event_ledger import EventLedger
from tools.verify_eventledger_replay import verify_eventledger_replay


def _write_replay_fixture(tmp_path: Path) -> tuple[Path, Path, Path]:
    artifact = tmp_path / "phase-summary.md"
    artifact.write_text("# Phase fixture\n", encoding="utf-8")
    registry_path = tmp_path / "artifact_registry.json"
    ArtifactRegistry(registry_path).register(
        artifact,
        phase="PHASE_TEST",
        kind="report",
    )

    ledger_path = tmp_path / "openclaw-governance-events.jsonl"
    ledger = EventLedger(ledger_path)
    for phase_index in range(1, 8):
        phase = f"PHASE_{phase_index:02d}"
        ledger.append(
            "QUALITY_GATE_PASSED",
            phase,
            "fixture quality gate",
            artifacts=[str(artifact)],
            quality_gate_result="passed",
        )
    ledger.append("FINAL_SEAL_PASSED", "PHASE_07", "fixture final seal")
    ledger.append("RELEASE_ACCEPTED", "PHASE_07", "fixture release acceptance")

    expected_state_path = tmp_path / "current_state.json"
    expected_state_path.write_text(
        json.dumps(
            {
                "final_status": "FINAL_SUCCESS",
                "release_status": "RELEASE_ACCEPTED",
                "phases": {f"PHASE_{i:02d}": {} for i in range(1, 8)},
            },
            ensure_ascii=False,
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    return ledger_path, registry_path, expected_state_path


def test_eventledger_replay_verifier_accepts_fixture_baseline(tmp_path: Path) -> None:
    ledger_path, registry_path, expected_state_path = _write_replay_fixture(tmp_path)

    result = verify_eventledger_replay(
        ledger_path=ledger_path,
        artifact_registry_path=registry_path,
        expected_state_path=expected_state_path,
        output_dir=tmp_path,
    )

    assert result["ok"] is True
    assert result["ledger_ok"] is True
    assert result["release_status"] == "RELEASE_ACCEPTED"
    assert result["final_status"] == "FINAL_SUCCESS"
    assert set(result["accepted_phases"]) == {f"PHASE_{i:02d}" for i in range(1, 8)}
    assert (tmp_path / "eventledger_replay_result.json").exists()
    assert (tmp_path / "eventledger_replay_report.md").exists()


def test_eventledger_replay_verifier_detects_hash_chain_tampering(tmp_path: Path) -> None:
    source, registry_path, expected_state_path = _write_replay_fixture(tmp_path)
    tampered = tmp_path / "tampered-events.jsonl"
    lines = source.read_text(encoding="utf-8").splitlines()
    first = json.loads(lines[0])
    first["phase"] = "PHASE_TAMPERED"
    lines[0] = json.dumps(first, ensure_ascii=False, sort_keys=True)
    tampered.write_text("\n".join(lines) + "\n", encoding="utf-8")

    result = verify_eventledger_replay(
        ledger_path=tampered,
        artifact_registry_path=registry_path,
        expected_state_path=expected_state_path,
        output_dir=tmp_path,
    )

    assert result["ok"] is False
    assert result["ledger_ok"] is False
    assert result["failure_reason"] in {"event_hash_mismatch", "previous_event_hash_mismatch"}
