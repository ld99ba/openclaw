from tools.build_final_fusion_complete_design import build_design, render_markdown


def test_complete_design_contains_three_audits():
    design = build_design()

    assert design["summary"]["audit_count"] == 3
    assert [audit["id"] for audit in design["audits"]] == ["AUDIT-1", "AUDIT-2", "AUDIT-3"]
    assert design["summary"]["final_claim_allowed_now"] is False


def test_complete_design_rejects_unbounded_version_ladder():
    design = build_design()
    markdown = render_markdown(design)

    assert "不是 V1.2/V1.3 版本计划" in markdown
    assert any("版本梯子" in item for item in design["objective"]["non_goals"])
    assert "这些阶段是有限 gate" in markdown


def test_complete_design_requires_capability_centric_fusion():
    design = build_design()

    assert "capability-centric" in design["architecture"]["principle"]
    assert any(module["path"] == "openclaw/fusion/capability_inventory.py" for module in design["architecture"]["proposed_modules"])
    assert any("每一项 Hermes 能力" in gate for gate in design["acceptance_gates"])


def test_complete_design_keeps_human_approval_boundaries():
    design = build_design()

    gates = "\n".join(design["acceptance_gates"])
    assert "发布" in gates
    assert "密钥访问" in gates
    assert "人工审批门" in gates
