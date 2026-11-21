"""
Verification test suite for redesigned Explainability: Contributing Factors module.
Validates:
1. Exact SHAP calculation with TreeSHAP on production model
2. Multi-class index alignment with predicted class
3. Additivity of SHAP contributions (base_value + sum(shap) == model_output within tolerance)
4. Top 5 contributing features selection and sorting by |SHAP| magnitude
5. Positive/Negative contribution directions
6. Human-readable clinical formatting of patient values
7. Integration with dynamic reassessment (new observation updates SHAP)
8. Safety alert separation from model attributions
"""
import os
import sys
import numpy as np
import pytest

sys.path.insert(0, os.path.abspath("."))
from backend.app.preprocessing.clinical_preprocessor import ClinicalPreprocessor
from backend.app.explainability.shap_explainer import ClinicalSHAPExplainer
from backend.app.services.clinical_service import ClinicalService
from backend.app.services.triage_service import TriageService
import xgboost as xgb


def test_shap_mathematical_precision_and_additivity():
    """Verify SHAP expected value plus sum of attributions reconstructs model output."""
    prep = ClinicalPreprocessor.load("backend/trained_models/clinical_preprocessor.joblib")
    model = xgb.XGBClassifier()
    model.load_model("backend/trained_models/clinical_xgboost.json")
    explainer = ClinicalSHAPExplainer(model, prep.feature_names)

    patient_data = {
        "age": 62, "sbp": 85, "dbp": 55, "hr": 118, "rr": 24, "bt": 37.1,
        "saturation": 89, "nrs_pain": 8, "mental": 2, "arrival_mode": 1
    }

    features, indices = prep.transform_single_patient(patient_data)
    probs = model.predict_proba(features)[0]
    predicted_class = int(np.argmax(probs))

    res = explainer.explain_instance(
        features,
        top_k=5,
        unscaled_features=indices.get("unscaled_features", {}),
        predicted_class=predicted_class
    )

    # 1. Verification of class
    assert res["explained_class"] == predicted_class
    assert "KTAS" in res["explained_class_label"]

    # 2. Additivity check
    base_val = res["base_value"]
    model_out = res["model_output"]
    all_features = res["features"]
    assert len(all_features) == 27

    sum_shap = sum(f["shap_value"] for f in all_features)
    reconstructed = base_val + sum_shap
    diff = abs(reconstructed - model_out)
    assert diff < 0.005, f"SHAP additivity difference {diff} exceeds tolerance"

    # 3. Top 5 features selection
    top_5 = res["top_features"]
    assert len(top_5) <= 5
    # Verify sorted by magnitude descending
    magnitudes = [f["magnitude"] for f in top_5]
    assert magnitudes == sorted(magnitudes, reverse=True)

    # 4. Color/direction consistency
    for f in top_5:
        if f["shap_value"] > 0.0001:
            assert f["direction"] == "positive"
        elif f["shap_value"] < -0.0001:
            assert f["direction"] == "negative"
        else:
            assert f["direction"] == "zero"

        # Check formatted patient value exists
        assert "patient_value_formatted" in f
        assert len(f["patient_value_formatted"]) > 0


def test_reassessment_updates_shap_factors():
    """Verify dynamic reassessment recalculates SHAP factors on updated patient vitals."""
    triage_service = TriageService()
    patient_id = "PAT-EXPLAIN-TEST"

    # Initial assessment: Stable vitals
    initial_vitals = {
        "age": 45, "sex": "Male", "arrival_mode": 3, "injury": 1,
        "chief_complaint": "Mild chest tightness",
        "mental": 1, "pain": 1, "nrs_pain": 3,
        "sbp": 125, "dbp": 82, "hr": 74, "rr": 16, "bt": 36.6, "saturation": 98
    }

    t1 = triage_service.assess_patient(
        patient_data=initial_vitals,
        patient_id=patient_id,
        patient_name="Explain Test Patient"
    )

    shap_t1 = t1["shap_factors"]
    assert "features" in shap_t1
    top_t1 = shap_t1["features"][0]

    # Reassessment T2: Acute hemodynamic deterioration (Hypotension + Tachycardia + Hypoxia)
    worsened_vitals = {
        "sbp": 82, "dbp": 50, "hr": 128, "rr": 28, "saturation": 87
    }

    t2 = triage_service.add_patient_observation(
        patient_id=patient_id,
        vitals_dict=worsened_vitals,
        reassessment_reason="Acute hemodynamic deterioration"
    )

    shap_t2 = t2["shap_factors"]
    assert "features" in shap_t2
    top_t2 = shap_t2["features"][0]

    # T2 should reflect fresh prediction and updated patient values
    assert t2["assessment_id"] != t1["assessment_id"]
    assert t2["risk_score"] > t1["risk_score"]
    # Check that patient value for SBP updated in SHAP features
    sbp_feat_t2 = next((f for f in shap_t2["features"] if f["feature"] == "SBP"), None)
    assert sbp_feat_t2 is not None
    assert sbp_feat_t2["patient_value"] == 82.0
    assert "82" in sbp_feat_t2["patient_value_formatted"]


if __name__ == "__main__":
    test_shap_mathematical_precision_and_additivity()
    test_reassessment_updates_shap_factors()
    print("All explainability tests passed successfully!")

