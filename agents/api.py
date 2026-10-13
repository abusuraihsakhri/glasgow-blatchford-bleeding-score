"""
FastAPI REST API Server for Glasgow Blatchford Bleeding Score.
"""
from typing import Dict, Any, List, Literal
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from .base import AuditLogger, PHIGuard
from glasgow_blatchford import calculate_gbs
from .models import SystemTaskPayload, ConsensusDossier
from .supervisor import SystemSupervisor

supervisor = SystemSupervisor(model_provider="mock")

app = FastAPI(
    title="Glasgow Blatchford Bleeding Score API",
    description="Enterprise Distributed Component Platform (Clinical & Biomedical AI)",
    version="3.0.0-ENTERPRISE",
)


class ChatRequest(BaseModel):
    query: str



class GBSRequest(BaseModel):
    """Strict input: no identifiers or patient demographics are required."""
    bun_mmol_l: float = Field(ge=0, le=100, allow_inf_nan=False)
    hemoglobin_g_dl: float = Field(ge=0, le=30, allow_inf_nan=False)
    sex: Literal["male", "female"]
    sbp_mmhg: float = Field(ge=0, le=300, allow_inf_nan=False)
    heart_rate: float = Field(ge=0, le=300, allow_inf_nan=False)
    melena: bool = False
    syncope: bool = False
    hepatic_disease: bool = False
    cardiac_failure: bool = False


@app.post("/api/gbs")
def api_gbs(payload: GBSRequest):
    """Calculate a complete, validated Glasgow–Blatchford Score."""
    return calculate_gbs(**payload.model_dump())


@app.get("/health")
def health():
    return {"status": "HEALTHY", "service": "glasgow-blatchford-bleeding-score", "domain": "Clinical & Biomedical AI", "standard": "CAP / CLSI / ISO Standards", "version": "3.0.0-ENTERPRISE"}


@app.get("/metrics")
def metrics():
    return {
        "dossiers_processed_total": len(supervisor.dossier_registry),
        "audit_blocks_total": len(AuditLogger.get_trail()),
        "system_status": "NOMINAL_OPTIMAL"
    }


@app.post("/api/audit")
def api_audit(payload: SystemTaskPayload):
    dossier = supervisor.process_task(payload)
    return dossier.to_dict()


@app.post("/api/chat")
def api_chat(req: ChatRequest):
    try:
        ans = supervisor.query_supervisory_chat(req.query)
        return {"response": ans}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/audit/logs")
def api_audit_logs():
    return {"audit_trail": AuditLogger.get_trail(), "verified": AuditLogger.verify_integrity()}
