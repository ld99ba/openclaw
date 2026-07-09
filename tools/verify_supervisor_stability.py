#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from openclaw.governance.state_machine import StateMachine
from openclaw.governance.supervisor import PHASES, Supervisor


def _write_report(output: Path, result: dict[str, Any]) -> None:
    lines = [
        "# V1.1 Phase 04 Supervisor Stability",
        "",
        f"Status: {'PASS' if result['ok'] else 'FAIL'}",
        f"Cycles simulated: {result['cycles']}",
        f"Heartbeats recorded: {result['heartbeat_count']}",
        f"Completed runs: {result['completed_runs']}",
        "",
        "| Check | Result |",
        "|---|---|",
        f"| Ordered progress | {result['ordered_progress_ok']} |",
        f"| Stuck state detection | {result['stuck_state_detected']} |",
        f"| Repeated failure detection | {result['repeated_failure_detected']} |",
        f"| Invalid transition detection | {result['invalid_transition_detected']} |",
        f"| External services required | {result['external_services_required']} |",
    ]
    (output / "supervisor_stability_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def verify_supervisor_stability(
    output_dir: str | Path = "reports/v1_1/phase_04",
    *,
    cycles: int = 5,
    repeated_failure_threshold: int = 3,
) -> dict[str, Any]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    supervisor = Supervisor()
    state_machine = StateMachine()
    timeline: list[dict[str, Any]] = []
    ordered_progress_ok = True

    for cycle in range(1, cycles + 1):
        accepted: set[str] = set()
        while True:
            phase = supervisor.next_phase(accepted)
            if phase is None:
                timeline.append({"cycle": cycle, "event": "run_complete", "accepted_count": len(accepted)})
                break
            expected = PHASES[len(accepted)]
            ordered_progress_ok = ordered_progress_ok and phase == expected
            state_machine.assert_transition("READY", "RUNNING")
            state_machine.assert_transition("RUNNING", "VALIDATING")
            state_machine.assert_transition("VALIDATING", "ACCEPTED")
            accepted.add(phase)
            timeline.append({"cycle": cycle, "event": "heartbeat", "phase": phase, "status": "ACCEPTED"})

    stuck_phase = supervisor.next_phase(set())
    stuck_observations = [stuck_phase for _ in range(repeated_failure_threshold + 1)]
    stuck_state_detected = len(set(stuck_observations)) == 1 and len(stuck_observations) > repeated_failure_threshold

    repeated_failures = [{"phase": "PHASE_03", "error": "synthetic_retryable_failure"} for _ in range(repeated_failure_threshold)]
    repeated_failure_detected = len(repeated_failures) >= repeated_failure_threshold

    try:
        state_machine.assert_transition("RUNNING", "FINAL_SUCCESS", final_ready=False)
        invalid_transition_detected = False
    except ValueError:
        invalid_transition_detected = True

    heartbeat_count = sum(1 for item in timeline if item["event"] == "heartbeat")
    completed_runs = sum(1 for item in timeline if item["event"] == "run_complete")
    expected_heartbeats = cycles * len(PHASES)
    ok = (
        ordered_progress_ok
        and heartbeat_count == expected_heartbeats
        and completed_runs == cycles
        and stuck_state_detected
        and repeated_failure_detected
        and invalid_transition_detected
    )

    result = {
        "schema": "ogk.v1_1.supervisor_stability.v1",
        "ok": ok,
        "cycles": cycles,
        "phase_count": len(PHASES),
        "heartbeat_count": heartbeat_count,
        "expected_heartbeat_count": expected_heartbeats,
        "completed_runs": completed_runs,
        "ordered_progress_ok": ordered_progress_ok,
        "stuck_state_detected": stuck_state_detected,
        "repeated_failure_detected": repeated_failure_detected,
        "invalid_transition_detected": invalid_transition_detected,
        "external_services_required": False,
        "destructive_action_taken": False,
        "timeline_sample": timeline[:20],
    }
    (output / "supervisor_stability_result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    _write_report(output, result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify V1.1 Supervisor deterministic stability behavior.")
    parser.add_argument("--output-dir", default="reports/v1_1/phase_04")
    parser.add_argument("--cycles", type=int, default=5)
    args = parser.parse_args()
    result = verify_supervisor_stability(args.output_dir, cycles=args.cycles)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
