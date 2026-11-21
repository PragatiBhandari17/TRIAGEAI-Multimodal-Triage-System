"""
Script to create the Demo Patient Test Suite (10 Diverse Clinical Cases).
Covers Head Injuries, Cardiac/Heart Emergencies, Sepsis, Trauma, Pediatric, Geriatric, and Routine cases.
"""
import os
import shutil
import json

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEMO_DIR = os.path.join(BASE_DIR, "datasets", "demo_patient_inputs")
SAMPLES_DIR = os.path.join(BASE_DIR, "datasets", "demo_samples")
NIH_DIR = os.path.join(BASE_DIR, "datasets", "xray_dataset", "images_001", "images")

os.makedirs(DEMO_DIR, exist_ok=True)

# Normal and Arrhythmia ECG paths
normal_ecg_path = os.path.join(SAMPLES_DIR, "demo_ecg_normal.csv")
arrhythmia_ecg_path = os.path.join(SAMPLES_DIR, "demo_ecg_arrhythmia.csv")

# Normal and Abnormal CXR paths
normal_cxr_path = os.path.join(SAMPLES_DIR, "demo_chest_xray_normal.png")
abnormal_cxr_path = os.path.join(SAMPLES_DIR, "demo_chest_xray_abnormal.png")
general_cxr_path = os.path.join(SAMPLES_DIR, "demo_chest_xray.png")

cases = [
    {
        "id": "CASE-01",
        "folder": "patient_01_severe_head_injury",
        "patient_name": "Marcus Vance",
        "patient_id": "PAT-DEMO-01",
        "category": "Neurological / Severe Head Trauma",
        "expected_ktas": 1,
        "expected_urgency": "Level 1 - Critical Resuscitation",
        "target_time": "Immediate (0 min)",
        "clinical_rationale": "Severe traumatic brain injury secondary to motor vehicle accident. Depressed mental status (Mental=3 Pain/Stupor) and Cushing's Triad physiological response (severe hypertension SBP 195 with reflex bradycardia HR 48). Mandatory critical resuscitation override.",
        "vitals": {
            "age": 28,
            "sex": "Male",
            "arrival_mode": 2, # Ambulance
            "injury": 2,       # Trauma
            "chief_complaint": "Severe Traumatic Brain Injury - Motor Vehicle Crash",
            "symptoms": "Blunt force head trauma, loss of consciousness at scene, projectile vomiting, anisocoria, responsive only to painful stimuli, irregular respirations",
            "mental": 3,       # Pain / Stupor
            "pain": 1,
            "nrs_pain": 8,
            "sbp": 195.0,
            "dbp": 110.0,
            "hr": 48.0,
            "rr": 10.0,
            "bt": 36.6,
            "saturation": 94.0
        },
        "ecg_source": normal_ecg_path,
        "xray_source": general_cxr_path,
        "notes": "Emergency neurosurgical consultation required immediately. Elevated ICP protocol initiated."
    },
    {
        "id": "CASE-02",
        "folder": "patient_02_acute_stemi_cardiac",
        "patient_name": "Arthur Pendelton",
        "patient_id": "PAT-DEMO-02",
        "category": "Cardiovascular / Acute Coronary Syndrome",
        "expected_ktas": 1,
        "expected_urgency": "Level 1 - Critical Resuscitation",
        "target_time": "Immediate (0 min)",
        "clinical_rationale": "Acute ST-elevation myocardial infarction complicated by early cardiogenic shock. Severe substernal crushing pain NRS 10, hypotension SBP 82, marked tachycardia HR 124, shock index 1.51 (>1.2 safety threshold), and ventricular ectopic arrhythmia on ECG.",
        "vitals": {
            "age": 62,
            "sex": "Male",
            "arrival_mode": 2, # Ambulance
            "injury": 1,       # Non-trauma
            "chief_complaint": "Acute STEMI / Crushing Chest Pain",
            "symptoms": "Substernal crushing chest pressure radiating to left arm and jaw, severe diaphoresis, dyspnea, nausea, sense of impending doom",
            "mental": 1,       # Alert
            "pain": 1,
            "nrs_pain": 10,
            "sbp": 82.0,
            "dbp": 54.0,
            "hr": 124.0,
            "rr": 26.0,
            "bt": 36.5,
            "saturation": 91.0
        },
        "ecg_source": arrhythmia_ecg_path,
        "xray_source": abnormal_cxr_path,
        "notes": "Code STEMI activated. Immediate transfer to cardiac catheterization laboratory."
    },
    {
        "id": "CASE-03",
        "folder": "patient_03_septic_shock",
        "patient_name": "Eleanor Rigby",
        "patient_id": "PAT-DEMO-03",
        "category": "Infectious / Septic Shock",
        "expected_ktas": 1,
        "expected_urgency": "Level 1 - Critical Resuscitation",
        "target_time": "Immediate (0 min)",
        "clinical_rationale": "Severe urosepsis presenting in refractory septic shock. Profound hypotension SBP 74, extreme tachycardia HR 136, high hyperpyrexia 39.8 C, altered sensorium (Mental=2 Verbal), and extreme Shock Index 1.84 (>1.2). Immediate resuscitation safety override.",
        "vitals": {
            "age": 78,
            "sex": "Female",
            "arrival_mode": 2, # Ambulance
            "injury": 1,       # Non-trauma
            "chief_complaint": "Septic Shock / Severe Urosepsis",
            "symptoms": "High fever, rigors, confusion, somnolence, warm vasodilation shock, costovertebral tenderness, oliguria",
            "mental": 2,       # Verbal / Somnolent
            "pain": 1,
            "nrs_pain": 7,
            "sbp": 74.0,
            "dbp": 42.0,
            "hr": 136.0,
            "rr": 28.0,
            "bt": 39.8,
            "saturation": 90.0
        },
        "ecg_source": normal_ecg_path,
        "xray_source": general_cxr_path,
        "notes": "Sepsis resuscitation protocol: Blood cultures drawn, 30 mL/kg IV crystalloid fluid bolus and broad-spectrum antibiotics."
    },
    {
        "id": "CASE-04",
        "folder": "patient_04_tension_pneumothorax",
        "patient_name": "Devon Hayes",
        "patient_id": "PAT-DEMO-04",
        "category": "Trauma / Acute Respiratory Failure",
        "expected_ktas": 1,
        "expected_urgency": "Level 1 - Critical Resuscitation",
        "target_time": "Immediate (0 min)",
        "clinical_rationale": "Tension pneumothorax following blunt thoracic impact. Critical hypoxia SpO2 81% (<=88% life-threatening safety override), severe tachypnea RR 34, hypotension SBP 88 with tachycardia HR 132, and radiological collapse of lung field.",
        "vitals": {
            "age": 34,
            "sex": "Male",
            "arrival_mode": 2, # Ambulance
            "injury": 2,       # Trauma
            "chief_complaint": "Tension Pneumothorax / Blunt Chest Trauma",
            "symptoms": "Agonizing right pleuritic pain, acute air hunger, tracheal deviation to left, jugular venous distention, absent right breath sounds",
            "mental": 1,       # Alert
            "pain": 1,
            "nrs_pain": 9,
            "sbp": 88.0,
            "dbp": 56.0,
            "hr": 132.0,
            "rr": 34.0,
            "bt": 36.9,
            "saturation": 81.0
        },
        "ecg_source": normal_ecg_path,
        "xray_source": abnormal_cxr_path,
        "notes": "Immediate needle thoracostomy decompressed right hemithorax, followed by rapid chest tube insertion."
    },
    {
        "id": "CASE-05",
        "folder": "patient_05_acute_ischemic_stroke",
        "patient_name": "Beatrice Holloway",
        "patient_id": "PAT-DEMO-05",
        "category": "Neurological / Cerebrovascular Emergency",
        "expected_ktas": 2,
        "expected_urgency": "Level 2 - High Emergent",
        "target_time": "< 15 minutes",
        "clinical_rationale": "Acute ischemic stroke within thrombolytic time window. Sudden right hemiplegia, dense facial droop, expressive dysphasia, altered sensorium (Mental=2 Verbal), severe hypertensive urgency SBP 208/114. Urgent neuroimaging and stroke team mobilization.",
        "vitals": {
            "age": 71,
            "sex": "Female",
            "arrival_mode": 2, # Ambulance
            "injury": 1,       # Non-trauma
            "chief_complaint": "Acute Stroke / Sudden Right Hemiparesis",
            "symptoms": "Sudden onset right facial droop, flaccid right arm and leg paralysis, expressive aphasia, onset 40 mins prior",
            "mental": 2,       # Verbal / Disoriented
            "pain": 0,
            "nrs_pain": 0,
            "sbp": 208.0,
            "dbp": 114.0,
            "hr": 88.0,
            "rr": 18.0,
            "bt": 37.0,
            "saturation": 97.0
        },
        "ecg_source": normal_ecg_path,
        "xray_source": normal_cxr_path,
        "notes": "Code Stroke activated. Non-contrast brain CT and neurology evaluation underway for IV tenecteplase."
    },
    {
        "id": "CASE-06",
        "folder": "patient_06_acute_appendicitis_peritonitis",
        "patient_name": "Liam Gallagher",
        "patient_id": "PAT-DEMO-06",
        "category": "Gastrointestinal / Acute Surgical Abdomen",
        "expected_ktas": 2,
        "expected_urgency": "Level 2 - High Emergent / Level 3 Urgent",
        "target_time": "< 15 to 30 minutes",
        "clinical_rationale": "Acute appendicitis with impending perforation and localized peritonitis. Severe right lower quadrant rebound tenderness, involuntary guarding, severe pain NRS 9, pyrexia BT 38.9 C, and febrile tachycardia HR 112.",
        "vitals": {
            "age": 24,
            "sex": "Male",
            "arrival_mode": 3, # Private car
            "injury": 1,       # Non-trauma
            "chief_complaint": "Acute Abdominal Pain / Peritonitis",
            "symptoms": "Severe migratory right lower quadrant abdominal pain, involuntary abdominal guarding, rebound tenderness, high fever, nausea, vomiting",
            "mental": 1,       # Alert
            "pain": 1,
            "nrs_pain": 9,
            "sbp": 128.0,
            "dbp": 82.0,
            "hr": 112.0,
            "rr": 22.0,
            "bt": 38.9,
            "saturation": 98.0
        },
        "ecg_source": normal_ecg_path,
        "xray_source": general_cxr_path,
        "notes": "Urgent general surgical evaluation. NPO, IV fluid resuscitation, and intravenous piperacillin-tazobactam ordered."
    },
    {
        "id": "CASE-07",
        "folder": "patient_07_pediatric_status_asthmaticus",
        "patient_name": "Toby Miller",
        "patient_id": "PAT-DEMO-07",
        "category": "Pediatric / Respiratory Distress",
        "expected_ktas": 2,
        "expected_urgency": "Level 2 - High Emergent",
        "target_time": "< 15 minutes",
        "clinical_rationale": "Pediatric severe status asthmaticus refractory to home bronchodilators. Severe tachypnea RR 36, hypoxia SpO2 89%, marked pediatric tachycardia HR 142, accessory muscle retractions and inability to speak in full sentences.",
        "vitals": {
            "age": 8,
            "sex": "Male",
            "arrival_mode": 3, # Private car
            "injury": 1,       # Non-trauma
            "chief_complaint": "Severe Pediatric Asthma Exacerbation",
            "symptoms": "Acute severe wheezing, suprasternal and subcostal retractions, speaking single words only, cyanosis around mouth, unresponsive to home albuterol",
            "mental": 1,       # Alert
            "pain": 1,
            "nrs_pain": 6,
            "sbp": 104.0,
            "dbp": 64.0,
            "hr": 142.0,
            "rr": 36.0,
            "bt": 37.2,
            "saturation": 89.0
        },
        "ecg_source": normal_ecg_path,
        "xray_source": general_cxr_path,
        "notes": "Continuous nebulized albuterol/ipratropium, systemic IV corticosteroids, and magnesium sulfate initiated."
    },
    {
        "id": "CASE-08",
        "folder": "patient_08_congestive_heart_failure_edema",
        "patient_name": "Donald Fletcher",
        "patient_id": "PAT-DEMO-08",
        "category": "Cardiovascular / Acute Heart Failure",
        "expected_ktas": 1,
        "expected_urgency": "Level 1 - Critical / Level 2 Emergent",
        "target_time": "Immediate to < 15 minutes",
        "clinical_rationale": "Acute decompensated congestive heart failure with flash pulmonary edema. Severe respiratory distress, orthopnea, bilateral coarse rales, severe hypoxemia SpO2 87% (triggers hypoxia safety override), hypertension SBP 178, and bilateral pulmonary alveolar infiltrates on CXR.",
        "vitals": {
            "age": 74,
            "sex": "Male",
            "arrival_mode": 2, # Ambulance
            "injury": 1,       # Non-trauma
            "chief_complaint": "Acute Pulmonary Edema / CHF Exacerbation",
            "symptoms": "Acute gasping breathlessness when recumbent, coughing pink frothy secretions, 3+ pitting pedal edema, bilateral diffuse lung crackles",
            "mental": 1,       # Alert
            "pain": 1,
            "nrs_pain": 5,
            "sbp": 178.0,
            "dbp": 98.0,
            "hr": 108.0,
            "rr": 30.0,
            "bt": 36.8,
            "saturation": 87.0
        },
        "ecg_source": arrhythmia_ecg_path,
        "xray_source": abnormal_cxr_path,
        "notes": "BiPAP non-invasive positive pressure ventilation started. High-dose IV furosemide and IV nitroglycerin infusion."
    },
    {
        "id": "CASE-09",
        "folder": "patient_09_moderate_gastroenteritis",
        "patient_name": "Chloe Chen",
        "patient_id": "PAT-DEMO-09",
        "category": "Gastrointestinal / Dehydration",
        "expected_ktas": 4,
        "expected_urgency": "Level 4 - Less Urgent / Low Risk",
        "target_time": "< 60 minutes",
        "clinical_rationale": "Acute viral gastroenteritis with mild-to-moderate dehydration. Hemodynamically stable with normal blood pressure SBP 114, mild compensatory tachycardia HR 98, normal SpO2 99%, alert mental status, moderate pain NRS 4. Safe for standard semi-urgent assessment.",
        "vitals": {
            "age": 31,
            "sex": "Female",
            "arrival_mode": 1, # Walking
            "injury": 1,       # Non-trauma
            "chief_complaint": "Acute Gastroenteritis / Moderate Dehydration",
            "symptoms": "48 hours of watery non-bloody diarrhea, recurrent nausea, dry mucous membranes, diffuse mild crampy abdominal pain, able to sip liquids",
            "mental": 1,       # Alert
            "pain": 1,
            "nrs_pain": 4,
            "sbp": 114.0,
            "dbp": 74.0,
            "hr": 98.0,
            "rr": 16.0,
            "bt": 37.4,
            "saturation": 99.0
        },
        "ecg_source": normal_ecg_path,
        "xray_source": normal_cxr_path,
        "notes": "Oral rehydration solution challenge, antiemetic ondansetron 4mg PO, basic metabolic panel pending."
    },
    {
        "id": "CASE-10",
        "folder": "patient_10_mild_ankle_strain",
        "patient_name": "Hannah Wright",
        "patient_id": "PAT-DEMO-10",
        "category": "Musculoskeletal / Minor Trauma",
        "expected_ktas": 5,
        "expected_urgency": "Level 5 - Non-Urgent / Routine",
        "target_time": "< 120 minutes",
        "clinical_rationale": "Minor inversion ankle sprain with isolated lateral malleolar soft tissue tenderness. Completely normal physiological vitals (BP 118/76, HR 68, RR 16, SpO2 99%), ambulatory with minimal limp, low pain NRS 3. Appropriate for routine triage queue.",
        "vitals": {
            "age": 22,
            "sex": "Female",
            "arrival_mode": 1, # Walking
            "injury": 2,       # Minor trauma
            "chief_complaint": "Right Ankle Inversion Injury / Sprain",
            "symptoms": "Stepped off sidewalk awkwardly 3 hours ago, mild lateral swelling, able to bear weight, no neurovascular compromise, intact skin",
            "mental": 1,       # Alert
            "pain": 1,
            "nrs_pain": 3,
            "sbp": 118.0,
            "dbp": 76.0,
            "hr": 68.0,
            "rr": 16.0,
            "bt": 36.6,
            "saturation": 99.0
        },
        "ecg_source": normal_ecg_path,
        "xray_source": normal_cxr_path,
        "notes": "RICE protocol (Rest, Ice, Compression, Elevation), elastic bandage wrap, and over-the-counter NSAIDs."
    }
]

catalog_summary = []

for case in cases:
    folder_path = os.path.join(DEMO_DIR, case["folder"])
    os.makedirs(folder_path, exist_ok=True)
    
    # 1. Save patient_data.json
    p_data = {
        "patient_id": case["patient_id"],
        "patient_name": case["patient_name"],
        "category": case["category"],
        "expected_ktas": case["expected_ktas"],
        "expected_urgency": case["expected_urgency"],
        "target_time": case["target_time"],
        "clinical_rationale": case["clinical_rationale"],
        "notes": case["notes"],
        "vitals": case["vitals"]
    }
    
    json_path = os.path.join(folder_path, "patient_data.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(p_data, f, indent=2)
        
    # 2. Copy ECG signal
    ecg_dest = os.path.join(folder_path, "ecg_signal.csv")
    if os.path.exists(case["ecg_source"]):
        shutil.copyfile(case["ecg_source"], ecg_dest)
        
    # 3. Copy scan / radiograph image
    xray_dest = os.path.join(folder_path, "scan_image.png")
    if os.path.exists(case["xray_source"]):
        shutil.copyfile(case["xray_source"], xray_dest)
        
    catalog_summary.append({
        "case_id": case["id"],
        "folder": case["folder"],
        "patient_id": case["patient_id"],
        "patient_name": case["patient_name"],
        "category": case["category"],
        "age": case["vitals"]["age"],
        "sex": case["vitals"]["sex"],
        "chief_complaint": case["vitals"]["chief_complaint"],
        "expected_ktas": case["expected_ktas"],
        "expected_urgency": case["expected_urgency"],
        "target_time": case["target_time"],
        "vital_summary": f"BP: {case['vitals']['sbp']:.0f}/{case['vitals']['dbp']:.0f}, HR: {case['vitals']['hr']:.0f}, RR: {case['vitals']['rr']:.0f}, SpO2: {case['vitals']['saturation']:.0f}%, BT: {case['vitals']['bt']:.1f}C, Mental: {case['vitals']['mental']}"
    })

# Save catalog
catalog_path = os.path.join(DEMO_DIR, "demo_patients_catalog.json")
with open(catalog_path, "w", encoding="utf-8") as f:
    json.dump(catalog_summary, f, indent=2)

# Write a comprehensive README.md in the folder
readme_content = f"""# TRIAGEAI Comprehensive Demo Patient Test Suite

This directory contains **10 distinct, clinically authentic test cases** representing diverse emergency medicine presentations, demographics (pediatric to geriatric), and disease categories (including acute traumatic brain injury, acute coronary STEMI, septic shock, tension pneumothorax, cerebrovascular stroke, surgical peritonitis, pediatric status asthmaticus, acute pulmonary edema, acute gastroenteritis, and minor trauma).

## Directory Structure
Each patient subfolder contains:
- `patient_data.json`: Standardized clinical payload conforming to the `/api/assessment` API schema.
- `ecg_signal.csv`: 187-sample cardiac signal (MIT-BIH lead waveform) for 1D CNN evaluation.
- `scan_image.png`: Chest radiograph / diagnostic imaging for DenseNet-121 and Gemini Multimodal Vision analysis.

## Test Cases Overview

| Case ID | Patient Name | Age/Sex | Category & Condition | Key Vitals | Expected KTAS | Target Time |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **CASE-01** | Marcus Vance | 28M | **Severe Head Injury / TBI** (Motor Vehicle Crash) | BP 195/110, HR 48 (Cushing's Triad), Mental=3 (Stupor) | **Level 1 (Critical)** | Immediate (0 min) |
| **CASE-02** | Arthur Pendelton | 62M | **Acute STEMI / Cardiogenic Shock** | BP 82/54, HR 124 (Shock Index 1.51), NRS 10, PVC Arrhythmia | **Level 1 (Critical)** | Immediate (0 min) |
| **CASE-03** | Eleanor Rigby | 78F | **Septic Shock / Urosepsis** | BP 74/42, HR 136 (Shock Index 1.84), BT 39.8°C, Mental=2 | **Level 1 (Critical)** | Immediate (0 min) |
| **CASE-04** | Devon Hayes | 34M | **Tension Pneumothorax / Thoracic Trauma** | BP 88/56, HR 132, RR 34, SpO2 81% (Severe Hypoxia), Trauma | **Level 1 (Critical)** | Immediate (0 min) |
| **CASE-05** | Beatrice Holloway | 71F | **Acute Ischemic Stroke / CVA** | BP 208/114, HR 88, Mental=2, Dense Right Hemiparesis | **Level 2 (Emergent)** | < 15 minutes |
| **CASE-06** | Liam Gallagher | 24M | **Acute Appendicitis / Peritonitis** | BP 128/82, HR 112, BT 38.9°C, NRS 9, Rebound Guarding | **Level 2 / 3 (Urgent)** | < 15–30 minutes |
| **CASE-07** | Toby Miller | 8M | **Pediatric Status Asthmaticus** | BP 104/64, HR 142, RR 36, SpO2 89%, Severe Wheezing | **Level 2 (Emergent)** | < 15 minutes |
| **CASE-08** | Donald Fletcher | 74M | **CHF Exacerbation / Pulmonary Edema** | BP 178/98, HR 108, RR 30, SpO2 87%, Alveolar Edema | **Level 1 / 2 (Critical)** | Immediate to < 15 min |
| **CASE-09** | Chloe Chen | 31F | **Acute Gastroenteritis / Dehydration** | BP 114/74, HR 98, RR 16, SpO2 99%, NRS 4, Walk-in | **Level 4 (Less Urgent)** | < 60 minutes |
| **CASE-10** | Hannah Wright | 22F | **Minor Ankle Sprain / Contusion** | BP 118/76, HR 68, RR 16, SpO2 99%, NRS 3, Ambulatory | **Level 5 (Non-Urgent)** | < 120 minutes |

## Execution
Run the automated test runner:
```powershell
python scripts/test_demo_patients.py
```
This script exercises:
1. Pure Clinical JSON inference (`/api/clinical/assess`)
2. Multimodal Assessment (`/api/assessment` with multipart Clinical + ECG + X-Ray)
3. Dynamic Longitudinal Observation (`/api/timeline/patient/{{patient_id}}/observation`)
4. Deterministic Clinical Safety Overrides (Shock Index >= 1.2, SpO2 <= 88%, Cushing's Triad, Altered Sensorium)
5. SHAP Factor Explainability & Evidence-Grounded Differential Diagnostics
"""

with open(os.path.join(DEMO_DIR, "README.md"), "w", encoding="utf-8") as f:
    f.write(readme_content)

print(f"[Success] Generated 10 demo patient test cases in: {DEMO_DIR}")
