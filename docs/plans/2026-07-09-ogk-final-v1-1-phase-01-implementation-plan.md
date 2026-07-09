# OGK-Final V1.1 Phase 01 Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build V1.1 Phase 01 independent verification and safety tests without modifying V1.0 release artifacts, tag history, or final reports.

**Architecture:** Add a thin V1.1 hardening layer around the existing OGK modules. The implementation should create CLI/report wrappers and focused tests that reuse `EventLedger`, `ReplayEngine`, `ArtifactRegistry`, `PolicyEngine`, and `ToolGateway` instead of changing their core semantics unless a failing test proves a real gap.

**Tech Stack:** Python 3, pytest, JSON/Markdown report files, existing OpenClaw modules under `/root/.openclaw/workspace/openclaw`.

---

## Baseline Rules

- Work in `/root/.openclaw/workspace`.
- Do not modify `ogk-final-v1.0`.
- Do not rewrite V1.0 release history.
- Do not edit V1.0 final acceptance/audit/current state files.
- Do not use `git add .`.
- Do not stage or include `main/`.
- Treat `reports/events/openclaw-governance-events.jsonl` as the highest fact source.
- Write V1.1 outputs under `reports/v1_1/phase_01/`.
- Put Phase 01 tests under `tests/v1_1/`.

## Phase 01 Deliverables

- `tools/verify_eventledger_replay.py`
- `tools/verify_artifact_registry_hashes.py`
- `tests/v1_1/test_eventledger_replay_verifier.py`
- `tests/v1_1/test_artifact_registry_hash_verifier.py`
- `tests/v1_1/test_policy_engine_permissions.py`
- `tests/v1_1/test_tool_gateway_security.py`
- Generated reports:
  - `reports/v1_1/phase_01/eventledger_replay_result.json`
  - `reports/v1_1/phase_01/eventledger_replay_report.md`
  - `reports/v1_1/phase_01/artifact_hash_result.json`
  - `reports/v1_1/phase_01/artifact_hash_report.md`

## Task 1: Create Phase 01 Test and Report Directories

**Files:**
- Create: `tests/v1_1/.gitkeep`
- Create: `reports/v1_1/phase_01/.gitkeep`

**Step 1: Create directories**

Run:

```bash
cd /root/.openclaw/workspace
mkdir -p tests/v1_1 reports/v1_1/phase_01
touch tests/v1_1/.gitkeep reports/v1_1/phase_01/.gitkeep
```

Expected: directories exist.

**Step 2: Check precise git status**

Run:

```bash
git status --short -- tests/v1_1 reports/v1_1/phase_01
```

Expected: only the two `.gitkeep` files appear.

**Step 3: Commit**

Run:

```bash
git add tests/v1_1/.gitkeep reports/v1_1/phase_01/.gitkeep
git commit -m "chore: create v1.1 phase 01 structure"
```

Expected: commit succeeds. If commits are being deferred, record this as pending and do not stage unrelated files.

## Task 2: EventLedger Replay Verifier Test

**Files:**
- Create: `tests/v1_1/test_eventledger_replay_verifier.py`
- Create later: `tools/verify_eventledger_replay.py`

**Step 1: Write failing tests**

Create `tests/v1_1/test_eventledger_replay_verifier.py`:

```python
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
```

**Step 2: Run test to verify it fails**

Run:

```bash
pytest tests/v1_1/test_eventledger_replay_verifier.py -q
```

Expected: FAIL because `tools.verify_eventledger_replay` does not exist.

## Task 3: EventLedger Replay Verifier Implementation

**Files:**
- Create: `tools/verify_eventledger_replay.py`
- Test: `tests/v1_1/test_eventledger_replay_verifier.py`

**Step 1: Implement minimal verifier**

Create `tools/verify_eventledger_replay.py`:

```python
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

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
        f"Failure Reason: {result.get('failure_reason', '')}",
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
```

**Step 2: Run focused tests**

Run:

```bash
pytest tests/v1_1/test_eventledger_replay_verifier.py -q
```

Expected: PASS.

**Step 3: Run CLI**

Run:

```bash
python tools/verify_eventledger_replay.py
```

Expected: exit 0 and create the two EventLedger reports under `reports/v1_1/phase_01/`.

**Step 4: Commit**

Run:

```bash
git add tools/verify_eventledger_replay.py tests/v1_1/test_eventledger_replay_verifier.py reports/v1_1/phase_01/eventledger_replay_result.json reports/v1_1/phase_01/eventledger_replay_report.md
git commit -m "feat: add v1.1 eventledger replay verifier"
```

## Task 4: ArtifactRegistry Hash Verifier Test

**Files:**
- Create: `tests/v1_1/test_artifact_registry_hash_verifier.py`
- Create later: `tools/verify_artifact_registry_hashes.py`

**Step 1: Write failing tests**

Create `tests/v1_1/test_artifact_registry_hash_verifier.py`:

```python
from __future__ import annotations

import json
from pathlib import Path

from tools.verify_artifact_registry_hashes import verify_artifact_registry_hashes


def test_artifact_registry_hash_verifier_accepts_v1_0_baseline(tmp_path: Path) -> None:
    result = verify_artifact_registry_hashes(
        registry_path=Path("reports/final/artifact_registry.json"),
        output_dir=tmp_path,
    )

    assert result["ok"] is True
    assert result["missing"] == []
    assert result["mismatched"] == []
    assert result["artifact_count"] > 0
    assert (tmp_path / "artifact_hash_result.json").exists()
    assert (tmp_path / "artifact_hash_report.md").exists()


def test_artifact_registry_hash_verifier_reports_missing_required_artifact(tmp_path: Path) -> None:
    data = {
        "schema": "ogk.artifact_registry.v1",
        "artifacts": [
            {
                "path": str(tmp_path / "missing.md"),
                "phase": "PHASE_TEST",
                "kind": "report",
                "required": True,
                "size": 10,
                "sha256": "0" * 64,
            }
        ],
    }
    registry = tmp_path / "artifact_registry.json"
    registry.write_text(json.dumps(data), encoding="utf-8")

    result = verify_artifact_registry_hashes(registry_path=registry, output_dir=tmp_path)

    assert result["ok"] is False
    assert result["missing"] == [str(tmp_path / "missing.md")]
```

**Step 2: Run test to verify it fails**

Run:

```bash
pytest tests/v1_1/test_artifact_registry_hash_verifier.py -q
```

Expected: FAIL because `tools.verify_artifact_registry_hashes` does not exist.

## Task 5: ArtifactRegistry Hash Verifier Implementation

**Files:**
- Create: `tools/verify_artifact_registry_hashes.py`
- Test: `tests/v1_1/test_artifact_registry_hash_verifier.py`

**Step 1: Implement minimal verifier**

Create `tools/verify_artifact_registry_hashes.py`:

```python
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from openclaw.evidence.artifact_registry import ArtifactRegistry


def _write_report(output_dir: Path, result: dict[str, Any]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "artifact_hash_result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    status = "PASS" if result["ok"] else "FAIL"
    lines = [
        "# V1.1 ArtifactRegistry Hash Verification",
        "",
        f"Status: {status}",
        f"Artifact Count: {result['artifact_count']}",
        f"Missing: {len(result['missing'])}",
        f"Mismatched: {len(result['mismatched'])}",
        "",
    ]
    (output_dir / "artifact_hash_report.md").write_text("\n".join(lines), encoding="utf-8")


def verify_artifact_registry_hashes(registry_path: Path, output_dir: Path) -> dict[str, Any]:
    registry = ArtifactRegistry(registry_path)
    verification = registry.verify()
    data = registry.data()
    result = {
        "schema": "ogk.v1_1.artifact_hash_result.v1",
        "ok": bool(verification.get("ok")),
        "artifact_count": len(data.get("artifacts", [])),
        "missing": verification.get("missing", []),
        "mismatched": verification.get("mismatched", []),
    }
    _write_report(output_dir, result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify OGK V1.1 ArtifactRegistry hashes.")
    parser.add_argument("--registry", default="reports/final/artifact_registry.json")
    parser.add_argument("--output-dir", default="reports/v1_1/phase_01")
    args = parser.parse_args()
    result = verify_artifact_registry_hashes(Path(args.registry), Path(args.output_dir))
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
```

**Step 2: Run focused tests**

Run:

```bash
pytest tests/v1_1/test_artifact_registry_hash_verifier.py -q
```

Expected: PASS.

**Step 3: Run CLI**

Run:

```bash
python tools/verify_artifact_registry_hashes.py
```

Expected: exit 0 and create the two ArtifactRegistry reports under `reports/v1_1/phase_01/`.

**Step 4: Commit**

Run:

```bash
git add tools/verify_artifact_registry_hashes.py tests/v1_1/test_artifact_registry_hash_verifier.py reports/v1_1/phase_01/artifact_hash_result.json reports/v1_1/phase_01/artifact_hash_report.md
git commit -m "feat: add v1.1 artifact hash verifier"
```

## Task 6: PolicyEngine Permission Tests

**Files:**
- Create: `tests/v1_1/test_policy_engine_permissions.py`
- Modify only if needed: `openclaw/governance/policy_engine.py`

**Step 1: Write tests**

Create `tests/v1_1/test_policy_engine_permissions.py`:

```python
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
```

**Step 2: Run tests**

Run:

```bash
pytest tests/v1_1/test_policy_engine_permissions.py -q
```

Expected: PASS with current `PolicyEngine`. If it fails, make the smallest policy fix and rerun.

**Step 3: Commit**

Run:

```bash
git add tests/v1_1/test_policy_engine_permissions.py openclaw/governance/policy_engine.py
git commit -m "test: add v1.1 policy permission coverage"
```

If `policy_engine.py` was unchanged, omit it from `git add`.

## Task 7: ToolGateway Security Tests

**Files:**
- Create: `tests/v1_1/test_tool_gateway_security.py`
- Modify only if needed: `openclaw/execution/tool_gateway.py`

**Step 1: Write tests**

Create `tests/v1_1/test_tool_gateway_security.py`:

```python
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
```

**Step 2: Run tests**

Run:

```bash
pytest tests/v1_1/test_tool_gateway_security.py -q
```

Expected: PASS with current `ToolGateway` and `PolicyEngine`. If it fails, make the smallest fix and rerun.

**Step 3: Commit**

Run:

```bash
git add tests/v1_1/test_tool_gateway_security.py openclaw/execution/tool_gateway.py
git commit -m "test: add v1.1 tool gateway security coverage"
```

If `tool_gateway.py` was unchanged, omit it from `git add`.

## Task 8: Phase 01 Combined Validation

**Files:**
- Read: `tools/test_ogk_final_acceptance.py`
- Read: all Phase 01 files

**Step 1: Run Phase 01 tests**

Run:

```bash
pytest tests/v1_1 -q
```

Expected: all V1.1 Phase 01 tests pass.

**Step 2: Run V1.0 final acceptance test as a regression guard**

Run:

```bash
python tools/test_ogk_final_acceptance.py
```

Expected: prints `OGK_FINAL_ACCEPTANCE_TEST_PASS`.

**Step 3: Run both V1.1 verifier CLIs**

Run:

```bash
python tools/verify_eventledger_replay.py
python tools/verify_artifact_registry_hashes.py
```

Expected: both exit 0 and write reports under `reports/v1_1/phase_01/`.

**Step 4: Check precise git status**

Run:

```bash
git status --short -- tools/verify_eventledger_replay.py tools/verify_artifact_registry_hashes.py tests/v1_1 reports/v1_1/phase_01 docs/plans
```

Expected: only intended Phase 01 files and plan/design docs are listed.

## Task 9: Phase 01 Summary Report

**Files:**
- Create: `reports/v1_1/phase_01/PHASE_01_SUMMARY.md`

**Step 1: Write summary**

Create `reports/v1_1/phase_01/PHASE_01_SUMMARY.md`:

```markdown
# OGK-Final V1.1 Phase 01 Summary

Status: PASS

## Scope

- Independent EventLedger replay verification
- Independent ArtifactRegistry hash verification
- PolicyEngine permission tests
- ToolGateway security tests

## Verification Commands

- `pytest tests/v1_1 -q`
- `python tools/test_ogk_final_acceptance.py`
- `python tools/verify_eventledger_replay.py`
- `python tools/verify_artifact_registry_hashes.py`

## Boundary Confirmation

- V1.0 tag/history unchanged.
- V1.0 final reports not edited.
- `main/` not staged.
- No blind `git add .` used.
```

Adjust `Status` only if all commands pass.

**Step 2: Commit**

Run:

```bash
git add reports/v1_1/phase_01/PHASE_01_SUMMARY.md
git commit -m "docs: add v1.1 phase 01 summary"
```

## Task 10: Final Review Before Handoff

**Step 1: Confirm V1.0 tag still exists**

Run:

```bash
git tag --list 'ogk-final-v1.0'
```

Expected: `ogk-final-v1.0`.

**Step 2: Confirm no `main/` staging**

Run:

```bash
git diff --name-only --cached | grep '^main/' && exit 1 || true
```

Expected: command exits 0 and prints nothing.

**Step 3: Confirm final test set**

Run:

```bash
pytest tests/v1_1 -q
python tools/test_ogk_final_acceptance.py
```

Expected: all pass.

**Step 4: Prepare handoff note**

In the final response, include:

- Files added.
- Commands run.
- Whether V1.0 acceptance still passes.
- Whether any BLOCKER/HIGH issues remain.
- Exact files staged/committed, if staging or commit was performed.
