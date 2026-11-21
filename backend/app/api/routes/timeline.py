"""
Dynamic Adaptive Triage and Patient Timeline API Routes.
Enforces strict multi-tenant database isolation.
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from typing import Optional
import json

from ...schemas.triage import PatientVitalsInput
from ...services.triage_service import TriageService
from ...database.repository import TriageRepository
from ..deps import TenantContext, get_tenant_context

router = APIRouter(prefix="/timeline", tags=["Dynamic Adaptive Triage"])


@router.get("/{patient_id}")
def get_patient_timeline(
    patient_id: str,
    tenant: TenantContext = Depends(get_tenant_context)
):
    """
    Retrieves the longitudinal risk trajectory and observation history for a patient
    strictly from the authenticated institution's tenant database.
    """
    doc = tenant.repo.get_patient_timeline(patient_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Patient timeline not found in your institution database.")
        
    traj = doc.get("trajectory", [])
    latest_risk = traj[-1]["risk_score"] if traj else 0.0
    latest_priority = traj[-1]["priority"] if traj else "UNKNOWN"
    
    # Calculate overall clinical trend
    trend = "Stabilizing"
    if len(traj) >= 2:
        net_change = traj[-1]["risk_score"] - traj[0]["risk_score"]
        if net_change >= 10.0:
            trend = "Deteriorating"
        elif net_change <= -10.0:
            trend = "Improving"
        else:
            trend = "Stabilizing"

    return {
        "patient_id": patient_id,
        "patient_name": doc.get("patient_name", "Patient"),
        "total_observations": len(traj),
        "overall_trend": trend,
        "latest_risk": latest_risk,
        "latest_priority": latest_priority,
        "trajectory": traj
    }


@router.post("/{patient_id}/observation")
async def add_patient_observation(
    patient_id: str,
    patient_data: Optional[str] = Form(None, description="Optional JSON string of updated vitals and clinical reason"),
    ecg_file: Optional[UploadFile] = File(None, description="Optional updated ECG lead CSV signal"),
    xray_file: Optional[UploadFile] = File(None, description="Optional updated medical scan image"),
    tenant: TenantContext = Depends(get_tenant_context)
):
    """
    Appends an updated observation timestamp for an existing patient strictly inside
    the authenticated institution's database.
    Supports multimodal inputs: updated vitals, new ECG, and new medical scans.
    """
    data_dict = {}
    if patient_data and str(patient_data).strip():
        try:
            data_dict = json.loads(patient_data)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid JSON in patient_data: {str(e)}")

    vitals = data_dict.get("vitals", data_dict) if isinstance(data_dict, dict) else {}
    reason = data_dict.get("reassessment_reason", "") if isinstance(data_dict, dict) else ""

    # Validate and read ECG file
    ecg_bytes = None
    if ecg_file:
        fn = (ecg_file.filename or "").lower()
        if not (fn.endswith(".csv") or fn.endswith(".txt")):
            raise HTTPException(
                status_code=400,
                detail="Unsupported ECG file format. Only 187-sample signal lead CSV/TXT files are supported."
            )
        ecg_bytes = await ecg_file.read()
        if len(ecg_bytes) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="ECG file exceeds size limit of 10MB.")

    # Validate and read Medical Scan file
    xray_bytes = None
    if xray_file:
        fn = (xray_file.filename or "").lower()
        valid_exts = (".png", ".jpg", ".jpeg", ".webp", ".dcm", ".dicom")
        if not any(fn.endswith(ext) for ext in valid_exts):
            raise HTTPException(
                status_code=400,
                detail="Unsupported medical scan format. Supported formats: PNG, JPG, JPEG, WEBP, DICOM."
            )
        xray_bytes = await xray_file.read()
        if len(xray_bytes) > 25 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Medical scan exceeds size limit of 25MB.")

    try:
        triage_svc = TriageService.get_instance()
        assessment = triage_svc.add_patient_observation(
            patient_id=patient_id,
            vitals_dict=vitals if vitals else None,
            ecg_bytes=ecg_bytes,
            xray_bytes=xray_bytes,
            tenant_repo=tenant.repo,
            institution_id=tenant.institution_id,
            reassessment_reason=reason
        )
        return assessment
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Observation update failed: {str(e)}")
