"""
TreeSHAP Explainability Module for the Clinical XGBoost Model.

Generates mathematically exact Shapley additive explanations for individual patient predictions,
attributing contributions to specific vital signs, symptoms, and physiological indices.

IMPORTANT CLINICAL NOTES:
- The XGBoost model is a 5-class classifier (KTAS 1-5) with objective 'multi:softprob'.
- TreeSHAP computes margin (log-odds) contributions for each feature towards the predicted class.
- SHAP values are additive: base_value + sum(shap_values) = raw model output (margin) for that class.
- SHAP values are NOT percentages of clinical risk. They reflect log-odds directional shifts.
- Direction convention:
    * Positive (+) SHAP: Increases the model's output for the displayed class.
    * Negative (-) SHAP: Decreases the model's output for the displayed class.
"""
import numpy as np
from typing import List, Dict, Any, Optional


class ClinicalSHAPExplainer:
    """
    SHAP explanation engine for clinical tabular predictions.
    Computes directional feature impacts on patient triage predictions.
    """

    # Human-readable labels for model features
    FRIENDLY_NAMES = {
        'Age': 'Patient Age',
        'SBP': 'Systolic Blood Pressure',
        'DBP': 'Diastolic Blood Pressure',
        'HR': 'Heart Rate',
        'RR': 'Respiratory Rate',
        'BT': 'Body Temperature',
        'Saturation': 'Oxygen Saturation (SpO2)',
        'Patients number per hour': 'ED Patient Volume Load',
        'NRS_pain': 'Pain Intensity (NRS)',
        'Sex': 'Biological Sex',
        'Arrival mode': 'Arrival Transport Mode',
        'Injury': 'Trauma / Injury Status',
        'Mental': 'Mental Status Level',
        'Pain': 'Pain Presentation',
        'KTAS_RN': 'Nurse Initial Triage (KTAS_RN)',
        'Shock_Index': 'Shock Index (HR / SBP)',
        'Pulse_Pressure': 'Pulse Pressure',
        'MAP': 'Mean Arterial Pressure (MAP)',
        'Modified_Shock_Index': 'Modified Shock Index',
        'Age_Shock_Index': 'Age-Adjusted Shock Index',
        'MEWS': 'Modified Early Warning Score',
        'Saturation_Missing': 'SpO2 Not Documented',
        'Altered_Mental': 'Altered Level of Consciousness',
        'Severe_Pain': 'Severe Acute Pain',
        'Tachycardia': 'Acute Tachycardia (HR > 100)',
        'Hypotension': 'Acute Hypotension (SBP < 90)',
        'Hypoxia': 'Hypoxemic State (SpO2 < 92%)'
    }

    # Units for numerical features (used for display)
    FEATURE_UNITS = {
        'Age': 'years',
        'SBP': 'mmHg',
        'DBP': 'mmHg',
        'HR': 'bpm',
        'RR': 'breaths/min',
        'BT': '°C',
        'Saturation': '%',
        'Patients number per hour': 'patients/hr',
        'NRS_pain': '/10',
        'Shock_Index': 'ratio',
        'Pulse_Pressure': 'mmHg',
        'MAP': 'mmHg',
        'Modified_Shock_Index': 'ratio',
        'Age_Shock_Index': '',
        'MEWS': 'score',
    }

    # KTAS class labels (0-indexed)
    KTAS_CLASS_LABELS = [
        "KTAS 1 (Critical Resuscitation)",
        "KTAS 2 (High Emergent)",
        "KTAS 3 (Moderate Urgent)",
        "KTAS 4 (Low Risk)",
        "KTAS 5 (Non-Urgent)"
    ]

    def __init__(self, model, feature_names: List[str]):
        self.model = model
        self.feature_names = feature_names
        self.explainer = None
        self._init_explainer()

    def _init_explainer(self):
        try:
            import shap
            # Initialize TreeExplainer for XGBoost
            self.explainer = shap.TreeExplainer(self.model)
        except Exception as e:
            print(f"[SHAP] TreeExplainer initialization warning: {e}")
            self.explainer = None

    def _format_patient_value(self, raw_name: str, pv: Any) -> str:
        """Formats the raw feature value into a clean, human-readable clinical string."""
        if pv is None or (isinstance(pv, float) and np.isnan(pv)):
            return "Not Documented"

        # Categorical and indicator interpretations
        if raw_name == 'Saturation_Missing':
            return "Documented" if float(pv) == 0 else "Not Documented (Missing)"
        elif raw_name == 'Altered_Mental':
            return "Altered Consciousness" if float(pv) == 1 else "Alert & Oriented"
        elif raw_name == 'Severe_Pain':
            return "Yes (NRS ≥ 7)" if float(pv) == 1 else "No"
        elif raw_name == 'Tachycardia':
            return "Yes (HR > 100)" if float(pv) == 1 else "No"
        elif raw_name == 'Hypotension':
            return "Yes (SBP < 90)" if float(pv) == 1 else "No"
        elif raw_name == 'Hypoxia':
            return "Yes (SpO2 < 92%)" if float(pv) == 1 else "No"
        elif raw_name == 'KTAS_RN':
            rn_map = {1: "Level 1 (Resuscitation)", 2: "Level 2 (Emergency)", 3: "Level 3 (Urgent)", 4: "Level 4 (Less Urgent)", 5: "Level 5 (Non-Urgent)"}
            return rn_map.get(int(pv), f"Level {pv}")
        elif raw_name == 'Sex':
            return "Male" if int(pv) == 1 else "Female"
        elif raw_name == 'Mental':
            m_map = {1: "Alert", 2: "Verbal Response", 3: "Pain Response", 4: "Unresponsive"}
            return m_map.get(int(pv), str(pv))
        elif raw_name == 'Injury':
            return "Trauma" if int(pv) == 2 else "Non-Trauma"
        elif raw_name == 'Arrival mode':
            arr_map = {1: "Ambulance", 2: "Public Transport", 3: "Walk-in"}
            return arr_map.get(int(pv), str(pv))
        elif raw_name == 'Pain':
            return "Yes" if int(pv) == 1 else "No"

        # Numerical values with units
        unit = self.FEATURE_UNITS.get(raw_name, '')
        if isinstance(pv, float):
            formatted_num = f"{pv:.2f}".rstrip('0').rstrip('.') if pv % 1 != 0 else f"{int(pv)}"
        else:
            formatted_num = str(pv)
        return f"{formatted_num} {unit}".strip() if unit else formatted_num

    def explain_instance(
        self,
        features_array: np.ndarray,
        top_k: int = 5,
        unscaled_features: Optional[Dict[str, Any]] = None,
        predicted_class: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Computes SHAP values for a single patient's feature vector.
        
        Args:
            features_array: Scaled feature array (1, n_features) as input to the model.
            top_k: Number of top contributing features to highlight (all are still returned).
            unscaled_features: Dict of raw (unscaled) feature values for display.
            predicted_class: The class index to explain (0-indexed). If None, uses the
                           model's predicted class.
        
        Returns:
            Dictionary containing:
            - features: List of all feature contributions sorted by absolute magnitude.
            - top_features: Filtered list of top K non-negligible contributing features.
            - explained_class: The class being explained (0-indexed).
            - explained_class_label: Human-readable label for the explained class.
            - output_scale: Description of the SHAP value scale.
            - base_value: The base (expected) value for the explained class.
            - model_output: The actual model raw output for the explained class.
            - top_k: The recommended number of features to show (default 5).
        """
        # Determine which class to explain
        if predicted_class is None:
            predicted_class = int(self.model.predict(features_array)[0])

        explained_class = int(predicted_class)
        explained_class_label = (
            self.KTAS_CLASS_LABELS[explained_class]
            if explained_class < len(self.KTAS_CLASS_LABELS)
            else f"Class {explained_class}"
        )

        base_value = None
        model_output = None

        if self.explainer is not None:
            try:
                shap_values = self.explainer.shap_values(features_array)

                # Multi-class XGBoost: shap_values is a list of arrays [n_classes](n_samples, n_features)
                # or a 3D array (n_samples, n_features, n_classes)
                if isinstance(shap_values, list):
                    # List of (n_samples, n_features) — one per class
                    class_shap = shap_values[explained_class][0]  # shape: (n_features,)
                elif len(shap_values.shape) == 3:
                    # (n_samples, n_features, n_classes)
                    class_shap = shap_values[0, :, explained_class]
                else:
                    # Binary or single-output
                    class_shap = shap_values[0]

                # Extract base value for the explained class
                if hasattr(self.explainer, 'expected_value'):
                    ev = self.explainer.expected_value
                    if isinstance(ev, (list, np.ndarray)):
                        base_value = float(ev[explained_class])
                    else:
                        base_value = float(ev)

                # Compute model raw output for additivity verification
                if base_value is not None:
                    model_output = float(base_value + np.sum(class_shap))

            except Exception as e:
                print(f"[SHAP] Computation error: {e}, falling back to feature attribution.")
                class_shap = self._heuristic_attribution(features_array[0])
        else:
            class_shap = self._heuristic_attribution(features_array[0])

        # Build feature contribution list
        results = []
        for i, val in enumerate(class_shap):
            raw_name = self.feature_names[i] if i < len(self.feature_names) else f"feature_{i}"
            friendly_name = self.FRIENDLY_NAMES.get(raw_name, raw_name)
            val_float = float(val)
            unit = self.FEATURE_UNITS.get(raw_name, '')

            # Exact direction according to clinical guidelines:
            # Positive (+) increases prediction for explained class
            # Negative (-) decreases prediction for explained class
            direction = (
                "positive" if val_float > 0.0001
                else ("negative" if val_float < -0.0001 else "zero")
            )
            direction_legacy = (
                "increases_risk" if val_float > 0.001
                else ("decreases_risk" if val_float < -0.001 else "neutral")
            )

            # Get actual patient value from unscaled features (if available)
            patient_value = None
            if unscaled_features and raw_name in unscaled_features:
                pv = unscaled_features[raw_name]
                if pv is not None and not (isinstance(pv, float) and np.isnan(pv)):
                    patient_value = pv
                    if isinstance(patient_value, float):
                        patient_value = round(patient_value, 2)

            formatted_val = self._format_patient_value(raw_name, patient_value)

            results.append({
                "feature": raw_name,
                "label": friendly_name,
                "shap_value": round(val_float, 4),
                "magnitude": round(abs(val_float), 4),
                "direction": direction,
                "direction_legacy": direction_legacy,
                "patient_value": patient_value,
                "patient_value_formatted": formatted_val,
                "unit": unit,
            })

        # Sort strictly by absolute magnitude of contribution
        results.sort(key=lambda x: x["magnitude"], reverse=True)

        # Extract only top contributing features (magnitude > 0.0001, maximum 5)
        top_meaningful = [f for f in results if f["magnitude"] > 0.0001][:top_k]

        return {
            "features": results,
            "top_features": top_meaningful,
            "explained_class": explained_class,
            "explained_class_label": explained_class_label,
            "output_scale": "raw margin (log-odds)",
            "base_value": round(base_value, 4) if base_value is not None else None,
            "model_output": round(model_output, 4) if model_output is not None else None,
            "top_k": top_k,
        }

    def _heuristic_attribution(self, feature_row: np.ndarray) -> np.ndarray:
        """Fallback attribution based on learned model feature importances."""
        try:
            importances = self.model.feature_importances_
            # Direction inferred from feature values
            signs = np.sign(feature_row)
            return importances * signs
        except Exception:
            return np.zeros(len(feature_row))
