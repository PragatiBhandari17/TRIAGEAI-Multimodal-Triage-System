"""
Core Multimodal Triage Orchestration Service.

Integrates the 3 trained models (XGBoost, 1D CNN, DenseNet) via the
Availability-Aware Multimodal Fusion Layer, coordinates dynamic longitudinal updates,
and persists patient assessments to the database.
"""
import os
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List

from .clinical_service import ClinicalService
from .ecg_service import ECGService
from .xray_service import XRayService
from .clinical_context_builder import ClinicalContextBuilder
from .clinical_differential_service import ClinicalDifferentialService
from ..fusion.model import MultimodalFusionLayer
from ..database.repository import TriageRepository


class TriageService:
    _instance = None

    def __init__(self, model_dir: Optional[str] = None):
        self.clinical_service = ClinicalService(model_dir)
        self.ecg_service = ECGService(model_dir)
        self.xray_service = XRayService(model_dir)
        self.differential_service = ClinicalDifferentialService.get_instance()
        self.fusion_layer = MultimodalFusionLayer()
        self.repository = TriageRepository()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = TriageService()
        return cls._instance

    def assess_patient(
        self,
        patient_data: Dict[str, Any],
        ecg_bytes: Optional[bytes] = None,
        xray_bytes: Optional[bytes] = None,
        patient_id: Optional[str] = None,
        patient_name: Optional[str] = "Unknown Patient",
        institution_id: Optional[str] = None,
        tenant_repo: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Runs the full multimodal triage assessment pipeline.
        Explicitly handles missing modalities without fabricating data.
        """
        active_repo = tenant_repo or self.repository
        if not patient_id or not str(patient_id).strip():
            patient_id = active_repo.get_next_patient_id()
        assessment_id = active_repo.get_next_assessment_id()

        # 1. Clinical Model Inference (Mandatory Modality)
        clinical_output = self.clinical_service.predict_patient(patient_data)

        # 2. ECG Model Inference (Optional Modality)
        ecg_output = None
        if ecg_bytes is not None and len(ecg_bytes) > 0:
            try:
                ecg_output = self.ecg_service.process_file_bytes(ecg_bytes)
            except Exception as e:
                print(f"[TriageService] Warning: ECG processing failed ({e}). Proceeding without ECG.")
                ecg_output = None

        # 3. Chest X-ray Model Inference (Optional Modality)
        xray_output = None
        if xray_bytes is not None and len(xray_bytes) > 0:
            try:
                xray_output = self.xray_service.process_image_bytes(xray_bytes)
            except Exception as e:
                print(f"[TriageService] Warning: X-ray processing failed ({e}). Proceeding without X-ray.")
                xray_output = None

        # 4. Availability-Aware Multimodal Fusion
        modality_mask = {
            "clinical": True,
            "vitals": True,
            "ecg": ecg_output is not None,
            "xray": xray_output is not None
        }

        fusion_result = self.fusion_layer.fuse(
            clinical_output=clinical_output,
            ecg_output=ecg_output,
            xray_output=xray_output,
            mask=modality_mask
        )

        # 5. Build Unified Clinical Context & Generate Evidence-Grounded Differential
        clinical_context = ClinicalContextBuilder.build_context(
            patient_data=patient_data,
            clinical_indices=clinical_output.get("clinical_indices"),
            ecg_output=ecg_output,
            xray_output=xray_output
        )
        differential_report = self.differential_service.generate_differential(clinical_context)

        # Format evidence-grounded conditions with full backward compatibility
        if differential_report.status == "success" and differential_report.conditions:
            potential_conditions = [
                {
                    "condition": c.condition_name,
                    "condition_name": c.condition_name,
                    "clinical_category": c.clinical_category,
                    "concern_level": c.concern_level,
                    "reason_for_consideration": c.reason_for_consideration,
                    "supporting_evidence": c.supporting_evidence,
                    "contradictory_evidence": c.contradictory_evidence,
                    "missing_information": c.missing_information,
                    "urgent_exclusion": c.urgent_exclusion,
                    "evidence_sources": c.evidence_sources,
                    "description": c.reason_for_consideration,
                    "clinical_disclaimer": c.clinical_disclaimer
                }
                for c in differential_report.conditions
            ]
        else:
            # Fallback or unavailable: return empty conditions, never fabricate unrelated conditions
            potential_conditions = []

        # 6. Assemble Full Clinical Response
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        record = {
            "assessment_id": assessment_id,
            "patient_id": patient_id,
            "patient_name": patient_name,
            "institution_id": institution_id or patient_data.get("institution_id") or "DEFAULT_HOSPITAL",
            "timestamp": now_str,
            "risk_score": fusion_result["risk_score"],
            "priority": fusion_result["priority"],
            "priority_label": fusion_result["priority_label"],
            "priority_level": fusion_result["priority_level"],
            "priority_color": fusion_result["priority_color"],
            "target_time": fusion_result["target_time"],
            "confidence": fusion_result["confidence"],
            "modalities_used": fusion_result["modalities_used"],
            "contributions": fusion_result["contributions"],
            "contributing_factors": fusion_result["contributing_factors"],
            "safety_overrides": fusion_result["safety_overrides"],
            "clinical_indices": clinical_output["clinical_indices"],
            "vitals_input": patient_data,
            "potential_conditions": potential_conditions,
            "clinical_differential": differential_report.model_dump(),
            "shap_factors": clinical_output["shap_summary"],
            "ecg_analysis": ecg_output,
            "xray_analysis": xray_output,
            "disclaimer": "This system is an AI-assisted research prototype intended to support triage decision-making. It is not a substitute for professional medical judgment, diagnosis, or treatment."
        }

        # 6. Save Assessment and update Patient Timeline in dedicated tenant database
        active_repo = tenant_repo or self.repository
        saved_record = active_repo.save_assessment(record)
        return saved_record

    def add_patient_observation(
        self,
        patient_id: str,
        vitals_dict: Optional[Dict[str, Any]] = None,
        ecg_bytes: Optional[bytes] = None,
        xray_bytes: Optional[bytes] = None,
        tenant_repo: Optional[Any] = None,
        institution_id: Optional[str] = None,
        reassessment_reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Adds an updated longitudinal observation point (T2, T3...) for an existing patient.
        Supports multimodal reassessment via updated Vitals, new ECG, and new Medical Scans.
        Reuses previous valid clinical information for unchanged modalities.
        """
        active_repo = tenant_repo or self.repository
        prev_assessment = active_repo.get_latest_patient_assessment(patient_id)

        # 1. Base clinical information from previous assessment or baseline defaults
        if prev_assessment:
            patient_name = prev_assessment.get("patient_name") or "Patient"
            prev_vitals = dict(prev_assessment.get("vitals_input") or {})
            if not prev_vitals:
                c_idx = prev_assessment.get("clinical_indices", {})
                prev_vitals = {
                    "age": prev_assessment.get("age", 45),
                    "sex": prev_assessment.get("sex", "Male"),
                    "arrival_mode": 1,
                    "injury": 1,
                    "chief_complaint": prev_assessment.get("chief_complaint", "Clinical follow-up"),
                    "symptoms": "",
                    "mental": 1 if not c_idx.get("altered_mental") else 2,
                    "pain": 1,
                    "nrs_pain": 5,
                    "sbp": c_idx.get("sbp", 120),
                    "dbp": c_idx.get("dbp", 80),
                    "hr": c_idx.get("hr", 75),
                    "rr": c_idx.get("rr", 16),
                    "bt": c_idx.get("bt", 36.8),
                    "saturation": c_idx.get("spo2", 98)
                }
            prev_ecg = prev_assessment.get("ecg_analysis")
            prev_xray = prev_assessment.get("xray_analysis")
            prev_priority = prev_assessment.get("priority", "UNKNOWN")
            prev_priority_label = prev_assessment.get("priority_label", prev_priority)
            prev_risk = float(prev_assessment.get("risk_score", 50.0))
        else:
            patient_name = "Patient"
            prev_vitals = {
                "age": 45, "sex": "Male", "arrival_mode": 1, "injury": 1,
                "chief_complaint": "Clinical follow-up", "mental": 1,
                "pain": 1, "nrs_pain": 5, "sbp": 120, "dbp": 80,
                "hr": 75, "rr": 16, "bt": 36.8, "saturation": 98
            }
            prev_ecg = None
            prev_xray = None
            prev_priority = "UNKNOWN"
            prev_priority_label = "Baseline"
            prev_risk = 0.0

        # 2. Merge vitals (identifying changes)
        merged_vitals = dict(prev_vitals)
        vitals_changed = False
        updated_types = []
        if vitals_dict:
            for k in ["sbp", "hr", "saturation", "rr", "dbp", "bt", "nrs_pain", "mental"]:
                val = vitals_dict.get(k)
                if val is not None and val != "":
                    try:
                        num_val = float(val)
                        if str(merged_vitals.get(k)) != str(num_val):
                            vitals_changed = True
                        merged_vitals[k] = num_val
                    except (ValueError, TypeError):
                        merged_vitals[k] = val

            for k in ["age", "sex", "arrival_mode", "injury", "chief_complaint", "symptoms"]:
                val = vitals_dict.get(k)
                if val is not None and val != "":
                    merged_vitals[k] = val

        if vitals_changed:
            updated_types.append("Vitals")

        # 3. Process ECG (New or Retained)
        ecg_output = None
        ecg_is_new = False
        if ecg_bytes is not None and len(ecg_bytes) > 0:
            ecg_output = self.ecg_service.process_file_bytes(ecg_bytes)
            ecg_is_new = True
            updated_types.append("ECG")
        elif prev_ecg is not None:
            ecg_output = prev_ecg
            ecg_is_new = False

        # 4. Process Medical Scan (New or Retained)
        xray_output = None
        scan_is_new = False
        if xray_bytes is not None and len(xray_bytes) > 0:
            xray_output = self.xray_service.process_image_bytes(xray_bytes)
            scan_is_new = True
            updated_types.append("Medical Scan")
        elif prev_xray is not None:
            xray_output = prev_xray
            scan_is_new = False

        if not updated_types:
            updated_types.append("Vitals")

        # 5. Multimodal Inference & Availability-Aware Fusion
        clinical_output = self.clinical_service.predict_patient(merged_vitals)

        modality_mask = {
            "clinical": True,
            "vitals": True,
            "ecg": ecg_output is not None,
            "xray": xray_output is not None
        }

        fusion_result = self.fusion_layer.fuse(
            clinical_output=clinical_output,
            ecg_output=ecg_output,
            xray_output=xray_output,
            mask=modality_mask
        )

        # 6. Generate Differential Context
        clinical_context = ClinicalContextBuilder.build_context(
            patient_data=merged_vitals,
            clinical_indices=clinical_output.get("clinical_indices"),
            ecg_output=ecg_output,
            xray_output=xray_output
        )
        diff_report = self.differential_service.generate_differential(clinical_context)
        if diff_report.status == "success" and diff_report.conditions:
            potential_conditions = [
                {
                    "condition": c.condition_name,
                    "condition_name": c.condition_name,
                    "clinical_category": c.clinical_category,
                    "concern_level": c.concern_level,
                    "reason_for_consideration": c.reason_for_consideration,
                    "supporting_evidence": c.supporting_evidence,
                    "contradictory_evidence": c.contradictory_evidence,
                    "missing_information": c.missing_information,
                    "urgent_exclusion": c.urgent_exclusion,
                    "evidence_sources": c.evidence_sources,
                    "description": c.reason_for_consideration,
                    "clinical_disclaimer": c.clinical_disclaimer
                }
                for c in diff_report.conditions
            ]
        else:
            potential_conditions = []

        # 7. Synthesize Objective Reassessment Reason
        new_risk = fusion_result["risk_score"]
        new_priority = fusion_result["priority"]
        new_priority_label = fusion_result["priority_label"]
        delta = round(new_risk - prev_risk, 1)

        reason_clauses = []
        if ecg_is_new and ecg_output:
            if ecg_output.get("is_abnormal"):
                reason_clauses.append(f"Updated ECG detected abnormal rhythm ({ecg_output.get('predicted_class')})")
            else:
                reason_clauses.append(f"Updated ECG confirmed rhythm ({ecg_output.get('predicted_class')})")

        if scan_is_new and xray_output:
            if xray_output.get("is_abnormal"):
                reason_clauses.append(f"Updated scan detected {xray_output.get('top_condition', 'radiological finding')}")
            else:
                reason_clauses.append("Updated scan showed no acute thoracic/cranial abnormalities")

        if vitals_changed:
            si = clinical_output["clinical_indices"].get("shock_index", 0.7)
            spo2 = clinical_output["clinical_indices"].get("spo2", 98)
            if si >= 1.2 or spo2 <= 88:
                reason_clauses.append(f"Critical hemodynamics (Shock Index {si:.2f}, SpO2 {spo2:.0f}%)")
            elif delta > 0:
                reason_clauses.append("Vital signs shifted toward instability")
            elif delta < 0:
                reason_clauses.append("Vital signs demonstrated physiological stabilization")

        if reassessment_reason and reassessment_reason.strip():
            final_reason = reassessment_reason.strip()
            if reason_clauses:
                final_reason += f" — {', '.join(reason_clauses)}"
        elif reason_clauses:
            action = "increased assessed urgency" if delta > 0 else ("reduced assessed urgency" if delta < 0 else "maintained urgency")
            final_reason = f"{' and '.join(reason_clauses)} {action} to {new_priority_label} (Risk: {new_risk}%)."
        else:
            final_reason = f"Periodic surveillance reassessment recalculated risk score at {new_risk}% ({new_priority_label})."

        # 8. Assemble Full Reassessment Record
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        record = {
            "assessment_id": active_repo.get_next_assessment_id(),
            "patient_id": patient_id,
            "patient_name": patient_name,
            "institution_id": institution_id or "DEFAULT_HOSPITAL",
            "timestamp": now_str,
            "risk_score": new_risk,
            "priority": new_priority,
            "priority_label": new_priority_label,
            "priority_level": fusion_result["priority_level"],
            "priority_color": fusion_result["priority_color"],
            "target_time": fusion_result["target_time"],
            "confidence": fusion_result["confidence"],
            "modalities_used": fusion_result["modalities_used"],
            "contributions": fusion_result["contributions"],
            "contributing_factors": fusion_result["contributing_factors"],
            "safety_overrides": fusion_result["safety_overrides"],
            "clinical_indices": clinical_output["clinical_indices"],
            "vitals_input": merged_vitals,
            "potential_conditions": potential_conditions,
            "clinical_differential": diff_report.model_dump(),
            "shap_factors": clinical_output["shap_summary"],
            "ecg_analysis": ecg_output,
            "xray_analysis": xray_output,
            "reassessment_meta": {
                "is_reassessment": True,
                "previous_priority": prev_priority,
                "previous_priority_label": prev_priority_label,
                "previous_risk_score": prev_risk,
                "ecg_updated": ecg_is_new,
                "scan_updated": scan_is_new,
                "vitals_updated": vitals_changed,
                "updated_types": updated_types,
                "clinical_reason": final_reason
            },
            "disclaimer": "This system is an AI-assisted research prototype intended to support triage decision-making."
        }

        # 9. Save Assessment and update Queue + Timeline
        saved_record = active_repo.save_assessment(record)
        return saved_record

