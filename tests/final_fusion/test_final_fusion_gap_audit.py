from tools.build_final_fusion_gap_audit import build_audit


def test_final_fusion_is_not_unbounded_version_ladder():
    audit = build_audit()

    assert audit["objective"]["name"] == "OpenClaw-Hermes Final Fusion"
    assert any("unbounded V1.2/V1.3" in item for item in audit["objective"]["not_the_goal"])
    assert any("No unbounded version ladder" in gate for gate in audit["gates"])


def test_final_fusion_requires_hermes_capability_inventory():
    audit = build_audit()

    assert audit["summary"]["final_claim_allowed"] is False
    assert audit["summary"]["next_action"] == "Build the source-anchored capability inventory for OpenClaw and Hermes."
    assert any(item["id"] == "WS1" for item in audit["workstreams"])
    assert any("Hermes capability" in gate for gate in audit["gates"])


def test_final_fusion_distinguishes_adapter_from_runtime_fusion():
    audit = build_audit()

    migrate_entry = next(item for item in audit["current_evidence"] if item["path"] == "extensions/migrate-hermes")
    assert "not by itself first-class runtime fusion" in migrate_entry["limitation"]
    assert any("No adapter-only claim" in gate for gate in audit["gates"])
