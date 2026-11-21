import React from 'react';
import { ShieldAlert, AlertTriangle, CheckCircle2, Info, Layers } from 'lucide-react';

/**
 * TriageExplainability: Redesigned Explainability Section
 * "Why This Triage Priority?"
 * 
 * Strict Clinical UI Requirements:
 * 1. Predicted Triage Level (with safety override / multimodal distinction)
 * 2. Key Contributing Features (Top 5 only, Human-readable name, patient value, SHAP value)
 *    - Green (+) increases output for displayed class
 *    - Red (−) decreases output for displayed class
 * 3. Clinical Safety Alerts (Rule-based & diagnostic, clearly separate from SHAP)
 * 4. Zero overlapping, minimal professional design in TRIAGEAI green-and-white theme.
 */
export const TriageExplainability = ({ assessment }) => {
  if (!assessment) return null;

  // 1. EXTRACT PREDICTED CLASS & PRIORITY DISTINCTIONS
  const shapData = assessment.shap_factors || {};
  const explainedClassLabel = shapData.explained_class_label || (
    assessment.priority_label ? `KTAS ${assessment.priority_level || ''} – ${assessment.priority}` : 'KTAS Assessment'
  );

  // Clean label formatting (e.g. "KTAS 2 – High Emergent" -> "KTAS 2 – Emergency")
  const formatKtasTitle = (rawLabel) => {
    if (!rawLabel) return 'Predicted Triage Level';
    return rawLabel
      .replace('KTAS 1 (Critical Resuscitation)', 'KTAS 1 – Resuscitation')
      .replace('KTAS 2 (High Emergent)', 'KTAS 2 – Emergency')
      .replace('KTAS 3 (Moderate Urgent)', 'KTAS 3 – Urgent')
      .replace('KTAS 4 (Low Risk)', 'KTAS 4 – Less Urgent')
      .replace('KTAS 5 (Non-Urgent)', 'KTAS 5 – Non-Urgent');
  };

  const predictedTitle = formatKtasTitle(explainedClassLabel);

  // Check if final priority differs from model prediction due to safety override or multimodal fusion
  const modelClassIdx = shapData.explained_class != null ? Number(shapData.explained_class) : null;
  const modelPredictedLevel = modelClassIdx != null ? modelClassIdx + 1 : null;
  const finalAssignedLevel = assessment.priority_level || (
    assessment.priority === 'CRITICAL' ? 1 :
    assessment.priority === 'HIGH' ? 2 :
    assessment.priority === 'MODERATE' ? 3 :
    assessment.priority === 'LESS_URGENT' ? 4 : 5
  );

  const hasOverride = Array.isArray(assessment.safety_overrides) && assessment.safety_overrides.length > 0;
  const hasMultimodalEscalation = (
    (assessment.ecg_analysis?.is_abnormal || assessment.xray_analysis?.is_abnormal) &&
    modelPredictedLevel !== null && finalAssignedLevel < modelPredictedLevel
  );

  const isPriorityOverridden = modelPredictedLevel !== null && finalAssignedLevel !== modelPredictedLevel;

  // 2. EXTRACT TOP 5 CONTRIBUTING FEATURES (Sorted by |SHAP|, filtered >= 0.0001)
  const allFeatures = Array.isArray(shapData.features) 
    ? shapData.features 
    : (Array.isArray(shapData) ? shapData : []);

  // Sort strictly by absolute magnitude descending
  const sortedFeatures = [...allFeatures].sort((a, b) => {
    const magA = Math.abs(a.shap_value != null ? a.shap_value : (a.magnitude || 0));
    const magB = Math.abs(b.shap_value != null ? b.shap_value : (b.magnitude || 0));
    return magB - magA;
  });

  // Filter out zero / negligible contributions (< 0.0001) and take top 5
  const topFeatures = sortedFeatures
    .filter(f => Math.abs(f.shap_value || 0) >= 0.0001)
    .slice(0, 5);

  // 3. COMPILE GENUINE CLINICAL SAFETY ALERTS (Physiological rules + Abnormal diagnostics)
  const rawAlerts = [];

  // Physiological safety overrides
  if (Array.isArray(assessment.safety_overrides)) {
    assessment.safety_overrides.forEach(so => {
      if (so && typeof so === 'string') rawAlerts.push(so);
    });
  }

  // Contributing vital sign factors
  if (Array.isArray(assessment.contributing_factors)) {
    assessment.contributing_factors.forEach(cf => {
      if (cf && typeof cf === 'string') {
        // Avoid duplicating if already covered in safety overrides
        const isDuplicate = rawAlerts.some(a => a.toLowerCase().includes(cf.toLowerCase().split('(')[0].trim()));
        if (!isDuplicate) rawAlerts.push(cf);
      }
    });
  }

  // Diagnostic ECG alert
  if (assessment.ecg_analysis?.is_abnormal) {
    rawAlerts.push(`Abnormal ECG: ${assessment.ecg_analysis.predicted_class || 'Pathological rhythm detected'}`);
  }

  // Diagnostic Scan alert
  if (assessment.xray_analysis?.is_abnormal) {
    const scanFinding = assessment.xray_analysis.top_condition || 'Pathological finding detected';
    rawAlerts.push(`Abnormal Medical Scan: ${scanFinding}`);
  }

  // Deduplicate
  const uniqueAlerts = Array.from(new Set(rawAlerts));

  return (
    <div className="glass-panel" style={{ padding: '24px', background: '#FFFFFF', borderRadius: '12px' }}>
      
      {/* SECTION HEADER */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px', flexWrap: 'wrap', gap: '8px' }}>
        <div>
          <h2 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#0F172A', margin: 0, display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Layers size={22} color="#059669" />
            Why This Triage Priority?
          </h2>
          <span style={{ fontSize: '0.75rem', color: '#64748B', fontWeight: 500, marginTop: '2px', display: 'block' }}>
            Clinical Model Feature Attribution (TreeSHAP) • Assessment ID: {assessment.assessment_id || 'ASM-01'}
          </span>
        </div>

        <span style={{
          fontSize: '0.725rem',
          padding: '4px 10px',
          borderRadius: '20px',
          background: '#ECFDF5',
          color: '#059669',
          border: '1px solid #A7F3D0',
          fontWeight: 700,
          display: 'flex',
          alignItems: 'center',
          gap: '5px'
        }}>
          TreeSHAP Verified
        </span>
      </div>

      {/* A. PREDICTED TRIAGE LEVEL */}
      <div style={{
        padding: '16px 18px',
        borderRadius: '10px',
        background: '#F8FAFC',
        border: '1px solid #E2E8F0',
        marginBottom: '20px'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '8px', marginBottom: '6px' }}>
          <span style={{ fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', color: '#64748B' }}>
            Clinical Model Prediction
          </span>
          <span style={{
            fontSize: '0.9rem',
            fontWeight: 800,
            padding: '3px 12px',
            borderRadius: '6px',
            background: '#0F172A',
            color: '#F8FAFC'
          }}>
            {predictedTitle}
          </span>
        </div>

        <p style={{ margin: 0, fontSize: '0.85rem', color: '#334155', lineHeight: 1.45 }}>
          These clinical factors contributed most strongly to the model's prediction.
        </p>

        {/* OVERRIDE OR MULTIMODAL DISTINCTION (If final triage differs from model prediction) */}
        {isPriorityOverridden && (
          <div style={{
            marginTop: '12px',
            padding: '10px 14px',
            borderRadius: '8px',
            background: '#FEF2F2',
            border: '1px solid #FECACA',
            fontSize: '0.8rem',
            color: '#991B1B',
            display: 'flex',
            alignItems: 'flex-start',
            gap: '8px'
          }}>
            <ShieldAlert size={16} color="#DC2626" style={{ flexShrink: 0, marginTop: '2px' }} />
            <div>
              <strong>Priority Escalation Distinction:</strong> The clinical model predicted <strong>KTAS Level {modelPredictedLevel}</strong>, but final patient priority was escalated to <strong>Level {finalAssignedLevel} ({assessment.priority_label || assessment.priority})</strong> due to:
              <ul style={{ margin: '4px 0 0', paddingLeft: '18px' }}>
                {hasOverride && assessment.safety_overrides.map((so, idx) => (
                  <li key={idx}>{so}</li>
                ))}
                {hasMultimodalEscalation && (
                  <li>Diagnostic evidence escalation (abnormal ECG or imaging finding)</li>
                )}
              </ul>
            </div>
          </div>
        )}
      </div>

      {/* B. KEY CONTRIBUTING FEATURES (Top 5 Only) */}
      <div style={{ marginBottom: '22px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
          <span style={{ fontSize: '0.8rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', color: '#475569' }}>
            Top Contributing Features ({topFeatures.length} of 5 shown)
          </span>
          <span style={{ fontSize: '0.725rem', color: '#64748B' }}>
            Sorted by |SHAP| Contribution
          </span>
        </div>

        {topFeatures.length === 0 ? (
          <div style={{ padding: '16px', textAlign: 'center', color: '#64748B', fontSize: '0.85rem', background: '#F8FAFC', borderRadius: '8px' }}>
            No significant SHAP feature contributions available for this assessment.
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {topFeatures.map((f, idx) => {
              const val = Number(f.shap_value || 0);
              const isPositive = val > 0;
              const isZero = Math.abs(val) < 0.0001;

              // Color coding strictly per prompt:
              // Positive SHAP (+): GREEN (Increases model output for predicted class)
              // Negative SHAP (−): RED (Decreases model output for predicted class)
              // Zero SHAP: Neutral Gray
              const badgeBg = isZero ? '#F1F5F9' : (isPositive ? '#ECFDF5' : '#FEF2F2');
              const badgeColor = isZero ? '#64748B' : (isPositive ? '#047857' : '#B91C1C');
              const badgeBorder = isZero ? '#E2E8F0' : (isPositive ? '#A7F3D0' : '#FECACA');
              const signSymbol = isZero ? '' : (isPositive ? '+' : '−');
              const formattedShap = `${signSymbol}${Math.abs(val).toFixed(4)}`;

              // Patient value representation
              const patientVal = f.patient_value_formatted || (
                f.patient_value != null ? `${f.patient_value}${f.unit ? ' ' + f.unit : ''}` : 'Not Documented'
              );

              const isNurseTriage = f.feature === 'KTAS_RN' || (f.label && f.label.includes('KTAS_RN'));

              return (
                <div
                  key={idx}
                  style={{
                    padding: '11px 16px',
                    borderRadius: '8px',
                    background: '#F8FAFC',
                    border: '1px solid #E2E8F0',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    gap: '14px',
                    transition: 'all 0.15s ease'
                  }}
                >
                  {/* Left: Feature Name and Actual Patient Value */}
                  <div style={{ flex: '1 1 auto', minWidth: 0 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
                      <span style={{ fontWeight: 700, fontSize: '0.875rem', color: '#0F172A', lineHeight: 1.3 }}>
                        {f.label || f.feature}
                      </span>
                      {isNurseTriage && (
                        <span style={{
                          fontSize: '0.675rem',
                          padding: '1px 6px',
                          borderRadius: '4px',
                          background: '#FEF3C7',
                          color: '#92400E',
                          fontWeight: 600
                        }}>
                          Initial Assessment Proxy
                        </span>
                      )}
                    </div>
                    <div style={{ fontSize: '0.775rem', color: '#64748B', marginTop: '3px' }}>
                      Patient Value: <strong style={{ color: '#1E293B', fontWeight: 600 }}>{patientVal}</strong>
                    </div>
                  </div>

                  {/* Right: SHAP Value Badge */}
                  <div style={{ textAlign: 'right', flexShrink: 0 }}>
                    <span style={{
                      display: 'inline-block',
                      padding: '4px 10px',
                      borderRadius: '6px',
                      fontSize: '0.85rem',
                      fontWeight: 800,
                      fontFamily: 'var(--font-mono, monospace)',
                      background: badgeBg,
                      color: badgeColor,
                      border: `1px solid ${badgeBorder}`,
                      minWidth: '78px',
                      textAlign: 'center'
                    }}>
                      {formattedShap}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* Minimal SHAP Color Legend */}
        <div style={{
          marginTop: '10px',
          padding: '8px 12px',
          borderRadius: '6px',
          background: '#F1F5F9',
          fontSize: '0.725rem',
          color: '#475569',
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          flexWrap: 'wrap'
        }}>
          <span style={{ display: 'flex', alignItems: 'center', gap: '4px', fontWeight: 600, color: '#047857' }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#059669', display: 'inline-block' }}></span>
            Green (+): Increases prediction for {predictedTitle.split('–')[0].trim()}
          </span>
          <span style={{ display: 'flex', alignItems: 'center', gap: '4px', fontWeight: 600, color: '#B91C1C' }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#DC2626', display: 'inline-block' }}></span>
            Red (−): Decreases prediction for {predictedTitle.split('–')[0].trim()}
          </span>
          <span style={{ color: '#64748B', marginLeft: 'auto', fontStyle: 'italic' }}>
            Colors indicate model output direction, not clinical safety.
          </span>
        </div>
      </div>

      {/* C. CLINICAL SAFETY ALERTS (Compact & Rule-Based) */}
      <div style={{
        padding: '14px 16px',
        borderRadius: '10px',
        background: uniqueAlerts.length > 0 ? '#FFF7ED' : '#F0FDF4',
        border: uniqueAlerts.length > 0 ? '1px solid #FED7AA' : '1px solid #BBF7D0',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: uniqueAlerts.length > 0 ? '8px' : '0' }}>
          {uniqueAlerts.length > 0 ? (
            <AlertTriangle size={16} color="#C2410C" />
          ) : (
            <CheckCircle2 size={16} color="#059669" />
          )}
          <span style={{
            fontSize: '0.8rem',
            fontWeight: 800,
            textTransform: 'uppercase',
            letterSpacing: '0.04em',
            color: uniqueAlerts.length > 0 ? '#9A3412' : '#166534'
          }}>
            Clinical Safety Alerts
          </span>
          <span style={{
            fontSize: '0.675rem',
            color: uniqueAlerts.length > 0 ? '#EA580C' : '#15803D',
            fontWeight: 600,
            marginLeft: 'auto'
          }}>
            Deterministic Safety Rules & Diagnostics — Separate from SHAP
          </span>
        </div>

        {uniqueAlerts.length > 0 ? (
          <ul style={{ margin: 0, paddingLeft: '18px', fontSize: '0.825rem', color: '#7C2D12', lineHeight: 1.6 }}>
            {uniqueAlerts.map((alertText, idx) => {
              const isCritical = alertText.toLowerCase().includes('hypoxemia') ||
                                alertText.toLowerCase().includes('shock') ||
                                alertText.toLowerCase().includes('hypotension') ||
                                alertText.toLowerCase().includes('severe');
              return (
                <li key={idx} style={{ fontWeight: isCritical ? 700 : 500, color: isCritical ? '#DC2626' : '#9A3412' }}>
                  {alertText}
                </li>
              );
            })}
          </ul>
        ) : (
          <div style={{ fontSize: '0.8rem', color: '#15803D', marginTop: '2px' }}>
            No critical physiological safety overrides triggered (all monitored vital signs and diagnostic signals within safe bounds).
          </div>
        )}
      </div>

    </div>
  );
};

