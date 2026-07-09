from __future__ import annotations

import json
from pathlib import Path

from tools.verify_eventledger_replay import verify_eventledger_replay


def test_eventledger_replay_verifier_accepts_v1_0_baseline(tmp_path: Path) -> None:
    result = verify_eventledger_replay(
        ledger_path=Path("reports/events/openclaw-governance-events.jsonl"),
        artifact_registry_path=Path("reports/final/artifact_registry.json"),
        expected_state_path=Path("reports/final/current_state.json"),
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
    source = Path("reports/events/openclaw-governance-events.jsonl")
    tampered = tmp_path / "tampered-events.jsonl"
    lines = source.read_text(encoding="utf-8").splitlines()
    first = json.loads(lines[0])
    first["phase"] = "PHASE_TAMPERED"
    lines[0] = json.dumps(first, ensure_ascii=False, sort_keys=True)
    tampered.write_text("\n".join(lines) + "\n", encoding="utf-8")

    result = verify_eventledger_replay(
        ledger_path=tampered,
        artifact_registry_path=Path("reports/final/artifact_registry.json"),
        expected_state_path=Path("reports/final/current_state.json"),
        output_dir=tmp_path,
    )

    assert result["ok"] is False
    assert result["ledger_ok"] is False
    assert result["failure_reason"] in {"event_hash_mismatch", "previous_event_hash_mismatch"}
