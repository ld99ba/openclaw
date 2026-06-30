from __future__ import annotations

import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from openclaw.evidence.event_ledger import EventLedger
from openclaw.evidence.artifact_registry import ArtifactRegistry
from openclaw.evidence.replay_engine import ReplayEngine
from openclaw.governance.policy_engine import PolicyEngine
from openclaw.governance.state_machine import StateMachine


def main() -> int:
    required = [
        'reports/final/OPENCLAW_FINAL_ACCEPTANCE_REPORT.md',
        'reports/final/OPENCLAW_FINAL_AUDIT_REPORT.md',
        'reports/final/OPENCLAW_RELEASE_ARTIFACT_INDEX.md',
        'reports/final/OPENCLAW_FINAL_PROGRESS_SUMMARY.md',
        'reports/final/OPENCLAW_HERMES_SUPERIORITY_PROOF.md',
        'reports/hermes_capability_coverage_matrix.json',
        'reports/hermes_behavior_equivalence_audit.md',
        'reports/hermes_source_inventory.json',
        'reports/hermes_gap_audit.md',
    ]
    for path in required:
        p = Path(path)
        assert p.exists() and p.stat().st_size > 0, path

    ledger = EventLedger('reports/events/openclaw-governance-events.jsonl')
    assert ledger.verify()['ok'] is True

    registry = ArtifactRegistry('reports/final/artifact_registry.json')
    assert registry.verify()['ok'] is True

    replay = ReplayEngine('reports/events/openclaw-governance-events.jsonl', 'reports/final/artifact_registry.json').rebuild_state()
    assert replay['ledger_ok'] is True
    assert replay['artifact_registry_ok'] is True
    assert set(replay['accepted_phases']) == {f'PHASE_{i:02d}' for i in range(1, 8)}

    state = json.loads(Path('reports/final/current_state.json').read_text(encoding='utf-8'))
    assert state['final_status'] == 'FINAL_SUCCESS'
    assert state['release_status'] == 'RELEASE_ACCEPTED'
    assert all(v == 'ACCEPTED' for v in state['phases'].values())

    seal = json.loads(Path('reports/final/openclaw_final_seal_result.json').read_text(encoding='utf-8'))
    assert seal['status'] == 'FINAL_SUCCESS'
    assert seal['release_status'] == 'RELEASE_ACCEPTED'
    assert not seal['missing_phases']
    assert not seal['missing_artifacts']

    matrix = json.loads(Path('reports/hermes_capability_coverage_matrix.json').read_text(encoding='utf-8'))
    assert matrix['coverage']['registered_percent'] == 100.0
    required_modules = {'agent_init','conversation_loop','tool_mapping','permission_bridge','error_classifier','memory_manager','context_compressor','skill_loop','dashboard','migration','acp_adapter','scheduled_automation','subagent_delegation','final_report_audit'}
    assert {i['hermes_module'] for i in matrix['items']} == required_modules

    sm = StateMachine()
    assert sm.can_transition('PLANNED', 'FINAL_SUCCESS', final_ready=False) is False
    assert sm.can_transition('ACCEPTED', 'FINAL_SUCCESS', final_ready=True) is True

    policy = PolicyEngine()
    assert policy.decide('delete', 'core runtime').allowed is False
    assert policy.decide('write', 'openclaw/reports/probe.txt').allowed is True

    print('OGK_FINAL_ACCEPTANCE_TEST_PASS')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
