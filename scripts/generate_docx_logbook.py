import os
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, fill_hex):
    tcPr = cell._element.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._element.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def create_logbook_docx(output_path):
    doc = Document()
    
    # Page setup - Margins
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(0.75)
        section.bottom_margin = Inches(0.75)
        section.left_margin = Inches(0.75)
        section.right_margin = Inches(0.75)

    # Header styling
    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_inst = p_inst.add_run("SVKM's NMIMS\n")
    run_inst.bold = True
    run_inst.font.size = Pt(15)
    run_inst.font.color.rgb = RGBColor(163, 0, 0) # NMIMS Maroon

    run_school = p_inst.add_run("Mukesh Patel School of Technology Management & Engineering, Shirpur Campus\n")
    run_school.bold = True
    run_school.font.size = Pt(12)
    run_school.font.color.rgb = RGBColor(30, 41, 59)

    run_dept = p_inst.add_run("Department of Computer Engineering | Academic Session: 2025–26 / 2026–27\n")
    run_dept.italic = True
    run_dept.font.size = Pt(10.5)
    run_dept.font.color.rgb = RGBColor(71, 85, 105)

    # Document Title Box
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_title = p_title.add_run("B.TECH CAPSTONE PROJECT 15-WEEK LOG BOOK")
    run_title.bold = True
    run_title.font.size = Pt(14)
    run_title.font.color.rgb = RGBColor(15, 23, 42)

    # Metadata Info
    meta_p = doc.add_paragraph()
    meta_p.paragraph_format.space_after = Pt(8)
    meta_p.paragraph_format.line_spacing = 1.15
    
    r = meta_p.add_run("Project Title: ")
    r.bold = True
    r.font.size = Pt(10)
    meta_p.add_run("TRIAGEAI: AI-Based Multimodal Diagnostic Triage System for Intelligent Patient Prioritization\n").font.size = Pt(10)

    r = meta_p.add_run("Group Identifier: ")
    r.bold = True
    r.font.size = Pt(10)
    meta_p.add_run("Group G22   |   ").font.size = Pt(10)

    r = meta_p.add_run("Project Supervisor: ")
    r.bold = True
    r.font.size = Pt(10)
    meta_p.add_run("Dr. Suresh Kurumbanshi (Asst. Prof. & HOD, CE Dept.)\n").font.size = Pt(10)

    r = meta_p.add_run("Students: ")
    r.bold = True
    r.font.size = Pt(10)
    meta_p.add_run("1. Kunj Desai (70022300209 / B203)   2. Pragati Bhandari (70033300268 / B222)   3. Rishabh Mehta (70022300320 / B240)").font.size = Pt(10)

    doc.add_paragraph().paragraph_format.space_after = Pt(2)

    # Weeks Data
    weeks_data = [
        (
            "Week 1",
            "05/01/2026 to 10/01/2026",
            "10/01/2026",
            "Problem Formulation & Clinical Needs Analysis: Literature survey on emergency triage protocols (KTAS, ESI, Manchester Triage). Identified critical under-triage rates (18–30% of severe patients delayed) and resuscitation over-crowding. Established clinical objectives for multimodal decision support (clinical presentation, vital signs, ECG leads, chest radiography). Prepared initial project charter.",
            "Completed"
        ),
        (
            "Week 2",
            "12/01/2026 to 17/01/2026",
            "17/01/2026",
            "System Requirements Specification (SRS) & Architecture Planning: Formulated technical requirements (sub-2-second bedside response targets) and clinical data privacy safeguards (HIPAA de-identification). Designed 4-stage pipeline architecture: Modality Feature Extraction, Availability-Aware Gated Fusion, Clinical Safety Overrides, and Explainable AI (XAI).",
            "Completed"
        ),
        (
            "Week 3",
            "19/01/2026 to 24/01/2026",
            "24/01/2026",
            "Dataset Acquisition, Ingestion & Clinical Auditing: Procured and verified 4 core clinical datasets: Korean Emergency Service Triage tabular data (1,267 rows, 24 cols), MIT-BIH & PTB-DB ECG databases (123,998 beats), NIH ChestX-ray14 (112,120 radiographs), and 41-entity disease-symptom ontology. Sanitized Latin1 encoding and semicolon delimiters.",
            "Completed"
        ),
        (
            "Week 4",
            "26/01/2026 to 31/01/2026",
            "31/01/2026",
            "Tabular Data Preprocessing & Hemodynamic Feature Engineering: Enforced strict anti-leakage filtering by dropping post-hoc features (KTAS_RN, Disposition, Length of stay_min, mistriage). Sanitized corrupted strings (??, #BO!). Computed physiological indices: Shock Index (HR/SBP), Mean Arterial Pressure (MAP), and Pulse Pressure (PP).",
            "Completed"
        ),
        (
            "Week 5",
            "02/02/2026 to 07/02/2026",
            "07/02/2026",
            "ECG Signal Preprocessing & Morphological Analytics: Standardized 187-sample cardiac lead waveforms with Min-Max scaling into [0, 1]. Mapped signals into AAMI EC57 classes (Normal, Supraventricular, Ventricular, Fusion, Unknown). Developed Pan-Tompkins R-peak detector, calculating instantaneous heart rate, R-R intervals, and QRS complex duration (ms).",
            "Completed"
        ),
        (
            "Week 6",
            "09/02/2026 to 14/02/2026",
            "14/02/2026",
            "Radiographic Image Pipeline & Patient-Level Group Partitioning: Standardized chest radiographs to 224x224x3 resolution with ImageNet channel-wise normalization. Enforced strict patient-level GroupShuffleSplit on Patient ID to guarantee zero patient overlap between train, val, and test splits, eliminating longitudinal visual leakage across identical subjects.",
            "Completed"
        ),
        (
            "Week 7",
            "16/02/2026 to 21/02/2026",
            "21/02/2026",
            "Clinical Acuity XGBoost Classifier & Mid-Term Review Defense: Trained 5-tier KTAS gradient-boosted decision trees. Achieved 96.06% within-1 tier clinical tolerance accuracy, 94.09% acute high-acuity prioritization accuracy, and 0.9605 macro ROC-AUC. Prepared, presented, and successfully defended Interim Project Progress Report before the department review committee.",
            "Completed"
        ),
        (
            "Week 8",
            "23/02/2026 to 28/02/2026",
            "28/02/2026",
            "Deep 1D CNN Architecture for Cardiac Arrhythmia Discrimination: Architected 4-stage Conv1D network with BatchNorm, Adaptive Max Pooling, and 32-dim latent embedding projection. Trained with smoothed class weights against severe arrhythmia imbalance. Validated across 21,892 test heartbeats: achieved 97.87% accuracy and 97.82% weighted F1-score.",
            "Completed"
        ),
        (
            "Week 9",
            "02/03/2026 to 07/03/2026",
            "07/03/2026",
            "Thoracic Vision Engine & Universal Emergency Fallback: Configured transfer learning on DenseNet-121 for thoracic pathology classification (64-dim visual embedding). Engineered Universal Medical Vision Engine with multimodal Gemini integration for zero-shot triage of Head CTs, Bone X-rays, Ultrasounds, and burn photos with robust local offline fallback.",
            "Completed"
        ),
        (
            "Week 10",
            "09/03/2026 to 14/03/2026",
            "14/03/2026",
            "Availability-Aware Gated Multimodal Fusion & Deterministic Safety Overrides: Engineered weighted gated fusion layer handling binary modality mask M = [C, V, E, X] across all 5 operational permutations without data hallucination. Implemented deterministic clinical safety overrides: hard-coded tripwires (Shock Index >= 1.2, SpO2 < 85%) forcing critical resuscitation escalation.",
            "Completed"
        ),
        (
            "Week 11",
            "16/03/2026 to 21/03/2026",
            "21/03/2026",
            "Explainable AI (XAI) Implementation (TreeSHAP & Grad-CAM): Integrated TreeSHAP on tabular XGBoost trees for directional risk factor attributions (SpO2 down -> +28%, SI up -> +19%). Implemented Grad-CAM on DenseNet-121 penultimate layers to generate OpenCV JET heatmap overlays on radiographs. Added automated ECG QRS interval duration alerts.",
            "Completed"
        ),
        (
            "Week 12",
            "23/03/2026 to 28/03/2026",
            "28/03/2026",
            "Longitudinal Dynamic Triage Engine & Resilient Persistence: Developed multi-timestamp dynamic tracking (T1 -> T2 -> T3), computing net risk velocity (Delta Risk) and trajectory classification (Deteriorating, Stabilizing, Improving). Built resilient persistence layer: primary MongoDB driver with automated atomic fallback to local multi-tenant JSON storage.",
            "Completed"
        ),
        (
            "Week 13",
            "30/03/2026 to 04/04/2026",
            "04/04/2026",
            "Full-Stack API & Modern Clinical Frontend Dashboard: Built modular FastAPI REST endpoints (/api/triage/assess, /api/triage/timeline, /api/health, /api/metrics). Implemented React 19 + Vite dashboard featuring 4-node multimodal convergence canvas, bedside clinical presets, interactive SVG trajectory charts, and real-time XAI factor visualizations.",
            "Completed"
        ),
        (
            "Week 14",
            "06/04/2026 to 11/04/2026",
            "11/04/2026",
            "Comprehensive Testing, Benchmarking & Edge-Case Hardening: Built automated Pytest suite (26 unit/integration tests). Verified end-to-end response times (< 1.2s for full multimodal evaluation, < 180ms for bedside triage). Hardened API error handlers against network timeouts, synthetic vitals artifacts, and malformed medical file uploads.",
            "Completed"
        ),
        (
            "Week 15",
            "13/04/2026 to 18/04/2026",
            "18/04/2026",
            "Final Documentation, Black Book Compilation & Project Defense: Authored comprehensive Final Capstone Black Book report, technical user guide, and executive presentation deck. Prepared live examiner demonstration script showcasing missing-modality handling, Grad-CAM overlays, and dynamic re-triage. Successfully defended capstone project.",
            "Completed"
        )
    ]

    # Create Table
    table = doc.add_table(rows=1, cols=6)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False

    # Widths in inches
    col_widths = [Inches(0.7), Inches(1.3), Inches(0.9), Inches(3.1), Inches(0.7), Inches(0.8)]

    # Header Row
    headers = ["Week No.", "Date Range\n(From to To)", "Date of\nReporting", "Work Carried Out in That Week", "Status", "Guide's\nSign"]
    hdr_cells = table.rows[0].cells
    for i, h in enumerate(headers):
        hdr_cells[i].text = h
        hdr_cells[i].width = col_widths[i]
        set_cell_background(hdr_cells[i], "1E293B") # Dark slate
        set_cell_margins(hdr_cells[i], top=120, bottom=120, left=100, right=100)
        p = hdr_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for run in p.runs:
            run.bold = True
            run.font.size = Pt(8.5)
            run.font.color.rgb = RGBColor(255, 255, 255)

    # Data Rows
    for row_idx, item in enumerate(weeks_data):
        row_cells = table.add_row().cells
        bg_color = "F8FAFC" if row_idx % 2 == 1 else "FFFFFF"
        
        for c_idx in range(6):
            set_cell_background(row_cells[c_idx], bg_color)
            set_cell_margins(row_cells[c_idx], top=80, bottom=80, left=90, right=90)
            row_cells[c_idx].width = col_widths[c_idx]
            row_cells[c_idx].vertical_alignment = WD_ALIGN_VERTICAL.CENTER

        # Week No
        row_cells[0].paragraphs[0].text = item[0]
        row_cells[0].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        row_cells[0].paragraphs[0].runs[0].bold = True
        row_cells[0].paragraphs[0].runs[0].font.size = Pt(8)

        # Date Range
        row_cells[1].paragraphs[0].text = item[1].replace(" to ", "\nto\n")
        row_cells[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        row_cells[1].paragraphs[0].runs[0].font.size = Pt(7.5)

        # Date of reporting
        row_cells[2].paragraphs[0].text = item[2]
        row_cells[2].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        row_cells[2].paragraphs[0].runs[0].font.size = Pt(8)

        # Work Carried Out
        row_cells[3].paragraphs[0].text = item[3]
        row_cells[3].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.LEFT
        row_cells[3].paragraphs[0].runs[0].font.size = Pt(7.5)

        # Status
        row_cells[4].paragraphs[0].text = item[4]
        row_cells[4].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        row_cells[4].paragraphs[0].runs[0].font.size = Pt(8)
        row_cells[4].paragraphs[0].runs[0].font.color.rgb = RGBColor(22, 101, 52) # Dark green
        row_cells[4].paragraphs[0].runs[0].bold = True

        # Sign
        row_cells[5].paragraphs[0].text = ""

    # Signatures Table
    doc.add_paragraph().paragraph_format.space_after = Pt(12)
    sig_p = doc.add_paragraph()
    sig_run = sig_p.add_run("Verification & Supervisory Endorsement")
    sig_run.bold = True
    sig_run.font.size = Pt(11)

    sig_table = doc.add_table(rows=1, cols=3)
    sig_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    sig_cells = sig_table.rows[0].cells
    
    sig_cells[0].paragraphs[0].text = "_______________________\nKunj Desai (B203)\nPragati Bhandari (B222)\nRishabh Mehta (B240)\n(Student Signatures)"
    sig_cells[1].paragraphs[0].text = "_______________________\nDr. Suresh Kurumbanshi\nAssistant Professor & HOD\n(Project Supervisor)"
    sig_cells[2].paragraphs[0].text = "_______________________\nDr. Suresh Kurumbanshi\nHead of Department\n(Department Seal)"

    for c in sig_cells:
        c.paragraphs[0].runs[0].font.size = Pt(8.5)
        c.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Save
    doc.save(output_path)
    print(f"Successfully generated logbook docx at: {output_path}")

if __name__ == "__main__":
    out_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "PROJECT_LOGBOOK_15_WEEKS.docx"))
    create_logbook_docx(out_file)
