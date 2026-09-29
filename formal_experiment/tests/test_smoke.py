from bpc_hybrid.smoke import project_health


def test_project_health_reports_scaffold_ok() -> None:
    health = project_health()

    assert health["project"] == "LLM4BPC"
    assert health["stage"] == "R1"
    assert health["status"] == "scaffold-ok"
    assert health["benchmark"] == "none"
    assert health["uses_real_gdpr_bpmn_data"] is False
    assert health["uses_real_llm_api"] is False
