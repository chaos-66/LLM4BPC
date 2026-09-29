"""Smoke checks for the R1 scaffold."""


def project_health() -> dict:
    """Return a minimal project health summary.

    This function does not call external APIs, read secrets, or use real
    GDPR/BPMN/Sun-aligned benchmark data.
    """
    return {
        "project": "LLM4BPC",
        "stage": "R1",
        "status": "scaffold-ok",
        "benchmark": "none",
        "uses_real_gdpr_bpmn_data": False,
        "uses_real_llm_api": False,
    }
