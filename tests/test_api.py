"""Regression checks for the clinical API and tamper-evident audit trail."""
from fastapi.testclient import TestClient

from agents.api import app
from agents.base import AuditTrail

client = TestClient(app)

VALID = {
    "bun_mmol_l": 5.0,
    "hemoglobin_g_dl": 14.0,
    "sex": "male",
    "sbp_mmhg": 125,
    "heart_rate": 78,
    "melena": True,
    "syncope": False,
    "hepatic_disease": False,
    "cardiac_failure": False,
}


def test_complete_gbs_api():
    res = client.post("/api/gbs", json=VALID)
    assert res.status_code == 200
    data = res.json()
    assert data["is_complete"] is True
    assert data["total_score"] == 1
    assert data["safe_for_outpatient"] is True
    assert data["very_low_risk_criterion_met"] is True
    assert data["needs_intervention"] is None
    assert data["estimated_30d_mortality_percent"] is None


def test_gbs_api_rejects_missing_and_invalid():
    for payload in ({**VALID, "heart_rate": None}, {**VALID, "bun_mmol_l": -1}):
        assert client.post("/api/gbs", json=payload).status_code == 422
    missing = {k: v for k, v in VALID.items() if k != "hemoglobin_g_dl"}
    assert client.post("/api/gbs", json=missing).status_code == 422
    omitted_feature = {k: v for k, v in VALID.items() if k != "syncope"}
    assert client.post("/api/gbs", json=omitted_feature).status_code == 422
    assert client.post("/api/gbs", json={**VALID, "patient_name": "Example Person"}).status_code == 422


def test_audit_detects_tampered_signature_and_fields():
    log = AuditTrail(secret_key="unit-test-secret")
    log.log("tester", "unit", "CREATE", {"status": "OK"})
    assert log.verify_integrity()
    trail = log.get_trail()
    trail[0]["event_type"] = "MODIFIED"
    assert log.verify_integrity()  # External callers receive a copy.
    log.logs[0]["event_type"] = "MODIFIED"
    assert not log.verify_integrity()
