from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from openclaw.evidence.event_ledger import EventLedger
from openclaw.evidence.replay_engine import ReplayEngine


def _write_report(output_dir: Path, result: dict[str, Any]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "eventledger_replay_result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    status = "PASS" if result["ok"] else "FAIL"
    lines = [
        "# V1.1 EventLedger Replay Verification",
        "",
        f"Status: {status}",
        f"Ledger OK: {result.get('ledger_ok')}",
        f"Final Status: {result.get('final_status')}",
        f"Release Status: {result.get('release_status')}",
        f"Accepted Phases: {', '.join(result.get('accepted_phases', []))}",
        f"Failure Reason: {result.get('failure_reason') or 'none'}",
        "",
    ]
    (output_dir / "eventledger_replay_report.md").write_text("\n".join(lines), encoding="utf-8")


def verify_eventledger_replay(
    ledger_path: Path,
    artifact_registry_path: Path,
    expected_state_path: Path,
    output_dir: Path,
) -> dict[str, Any]:
    ledger = EventLedger(ledger_path)
    ledger_verification = ledger.verify()
    rebuilt = ReplayEngine(ledger_path, artifact_registry_path).rebuild_state()
    expected = json.loads(expected_state_path.read_text(encoding="utf-8"))
    expected_phases = sorted(expected["phases"].keys())
    accepted_phases = sorted(rebuilt.get("accepted_phases", []))

    result: dict[str, Any] = {
        "schema": "ogk.v1_1.eventledger_replay_result.v1",
        "ok": bool(
            ledger_verification.get("ok")
            and rebuilt.get("ledger_ok")
            and rebuilt.get("final_status") == expected.get("final_status")
            and rebuilt.get("release_status") == expected.get("release_status")
            and accepted_phases == expected_phases
        ),
        "ledger_ok": bool(ledger_verification.get("ok")),
        "artifact_registry_ok": bool(rebuilt.get("artifact_registry_ok")),
        "event_count": rebuilt.get("event_count", 0),
        "accepted_phases": accepted_phases,
        "final_status": rebuilt.get("final_status"),
        "release_status": rebuilt.get("release_status"),
        "expected_final_status": expected.get("final_status"),
        "expected_release_status": expected.get("release_status"),
        "failure_reason": ledger_verification.get("reason", ""),
    }
    _write_report(output_dir, result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify OGK V1.1 EventLedger replay.")
    parser.add_argument("--ledger", default="reports/events/openclaw-governance-events.jsonl")
    parser.add_argument("--artifact-registry", default="reports/final/artifact_registry.json")
    parser.add_argument("--expected-state", default="reports/final/current_state.json")
    parser.add_argument("--output-dir", default="reports/v1_1/phase_01")
    args = parser.parse_args()
    result = verify_eventledger_replay(
        Path(args.ledger),
        Path(args.artifact_registry),
        Path(args.expected_state),
        Path(args.output_dir),
    )
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
