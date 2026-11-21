import React, { useState, useEffect, useRef } from 'react';
import { 
  LineChart, Clock, TrendingUp, TrendingDown, Minus, 
  Plus, AlertCircle, CheckCircle2, ArrowRight, RefreshCw, Heart,
  FileSpreadsheet, Eye, X, Upload, Activity, ShieldAlert, FileText, Sparkles, Layers
} from 'lucide-react';
import { api } from '../services/api';

export const TimelinePage = ({ initialPatientId, onViewAssessment }) => {
  const [patientId, setPatientId] = useState(initialPatientId || 'PAT-01');
  const [timeline, setTimeline] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showAddModal, setShowAddModal] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  // New Observation Form State (Pre-fills with latest patient values when available)
  const [obsVitals, setObsVitals] = useState({
    sbp: 120,
    hr: 75,
    saturation: 98,
    rr: 16,
  });

  // Updated Diagnostic Inputs State
  const [ecgFile, setEcgFile] = useState(null);
  const [ecgFileName, setEcgFileName] = useState('');
  const [scanFile, setScanFile] = useState(null);
  const [scanFileName, setScanFileName] = useState('');
  const [scanPreview, setScanPreview] = useState(null);
  const [reassessmentReason, setReassessmentReason] = useState('');

  // Graph Tooltip & Selection State
  const [hoveredPoint, setHoveredPoint] = useState(null);
  const [activeTooltipPos, setActiveTooltipPos] = useState({ x: 0, y: 0 });
  const graphContainerRef = useRef(null);

  const fetchTimeline = async (id) => {
    setLoading(true);
    try {
      const data = await api.getTimeline(id);
      setTimeline(data);
      // Pre-fill vitals from latest observation
      if (data?.trajectory && data.trajectory.length > 0) {
        const lastPt = data.trajectory[data.trajectory.length - 1];
        const v = lastPt.vitals_summary;
        if (v) {
          setObsVitals({
            sbp: v.sbp ?? 120,
            hr: v.hr ?? 75,
            saturation: v.spo2 ?? 98,
            rr: v.rr ?? 16,
          });
        }
      }
    } catch {
      // If no timeline exists yet for this ID, provide clean demonstration baseline
      const dummyTraj = {
        patient_id: id,
        patient_name: 'Patient ' + id,
        total_observations: 3,
        overall_trend: 'Deteriorating',
        latest_risk: 84.5,
        latest_priority: 'CRITICAL',
        trajectory: [
          {
            observation_id: 'OBS-001',
            assessment_id: 'ASM-01',
            timestamp: '10:00:00',
            risk_score: 32.0,
            priority: 'LESS_URGENT',
            priority_label: 'Level 4 - Low Risk',
            priority_color: 'blue',
            delta_risk: 0.0,
            delta_direction: 'initial',
            vitals_summary: { hr: 78, sbp: 124, dbp: 80, spo2: 98, rr: 16, shock_index: 0.63 },
            updated_types: ['Initial Triage'],
            reassessment_reason: 'Initial emergency department triage baseline assessment.',
            modalities_count: 2,
          },
          {
            observation_id: 'OBS-002',
            assessment_id: 'ASM-02',
            timestamp: '10:45:00',
            risk_score: 58.5,
            priority: 'HIGH',
            priority_label: 'Level 2 - High Emergent',
            priority_color: 'orange',
            delta_risk: 26.5,
            delta_direction: 'increased',
            vitals_summary: { hr: 106, sbp: 102, dbp: 68, spo2: 93, rr: 22, shock_index: 1.04 },
            updated_types: ['Vitals', 'ECG'],
            reassessment_reason: 'Updated ECG signal detected arrhythmia and vital signs shifted toward instability.',
            ecg_summary: { available: true, is_new: true, predicted_class: 'Supraventricular Ectopic (S)', is_abnormal: true },
            modalities_count: 3,
          },
          {
            observation_id: 'OBS-003',
            assessment_id: 'ASM-03',
            timestamp: '11:30:00',
            risk_score: 84.5,
            priority: 'CRITICAL',
            priority_label: 'Level 1 - Critical Resuscitation',
            priority_color: 'red',
            delta_risk: 26.0,
            delta_direction: 'increased',
            vitals_summary: { hr: 128, sbp: 86, dbp: 54, spo2: 88, rr: 28, shock_index: 1.49 },
            updated_types: ['Vitals', 'Medical Scan'],
            reassessment_reason: 'Critical hemodynamics (Shock Index 1.49, SpO2 88%) and updated scan escalated urgency to Level 1.',
            scan_summary: { available: true, is_new: true, top_condition: 'Pneumothorax', is_abnormal: true },
            safety_overrides: ['Elevated Shock Index (1.49) indicates acute hypoperfusion', 'Severe hypoxia (SpO2 88%)'],
            modalities_count: 4,
          }
        ]
      };
      setTimeline(dummyTraj);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTimeline(patientId);
  }, [patientId]);

  // Handle ECG File Selection
  const handleEcgChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    if (!file.name.toLowerCase().endsWith('.csv') && !file.name.toLowerCase().endsWith('.txt')) {
      alert("Please upload an ECG lead CSV or TXT signal file.");
      return;
    }
    setEcgFile(file);
    setEcgFileName(file.name);
  };

  // Handle Medical Scan File Selection
  const handleScanChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setScanFile(file);
    setScanFileName(file.name);
    const reader = new FileReader();
    reader.onload = () => setScanPreview(reader.result);
    reader.readAsDataURL(file);
  };

  const handleAddObservation = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      const formData = new FormData();
      formData.append('patient_data', JSON.stringify({
        patient_id: patientId,
        vitals: obsVitals,
        reassessment_reason: reassessmentReason
      }));
      if (ecgFile) {
        formData.append('ecg_file', ecgFile);
      }
      if (scanFile) {
        formData.append('xray_file', scanFile);
      }
      const updated = await api.addObservation(patientId, formData);
      setShowAddModal(false);
      // Reset inputs
      setEcgFile(null);
      setEcgFileName('');
      setScanFile(null);
      setScanFileName('');
      setScanPreview(null);
      setReassessmentReason('');
      await fetchTimeline(patientId);
      if (onViewAssessment) {
        onViewAssessment(updated);
      }
    } catch (err) {
      alert("Failed to recalculate observation: " + err.message);
    } finally {
      setSubmitting(false);
    }
  };

  const traj = timeline?.trajectory || [];

  // Key Indicators Calculation
  const initialRisk = traj.length > 0 ? traj[0].risk_score : 0.0;
  const currentRisk = timeline?.latest_risk ?? (traj.length > 0 ? traj[traj.length - 1].risk_score : 0.0);
  const riskChange = traj.length >= 2 ? roundToOne(currentRisk - initialRisk) : 0.0;
  const latestPriority = timeline?.latest_priority ?? (traj.length > 0 ? traj[traj.length - 1].priority : 'UNKNOWN');
  const latestPriorityLabel = traj.length > 0 ? (traj[traj.length - 1].priority_label || latestPriority) : latestPriority;
  const overallTrend = timeline?.overall_trend || (riskChange > 0 ? 'Deteriorating' : (riskChange < 0 ? 'Improving' : 'Stabilizing'));

  function roundToOne(num) {
    return Math.round(num * 10) / 10;
  }

  // Graph SVG Dimensions
  const svgWidth = 850;
  const svgHeight = 280;
  const margin = { left: 90, right: 80, top: 35, bottom: 50 };
  const graphWidth = svgWidth - margin.left - margin.right;
  const graphHeight = svgHeight - margin.top - margin.bottom;

  // Coordinate Mapping
  const getPointCoords = (pt, idx) => {
    const x = traj.length === 1 
      ? margin.left + graphWidth / 2 
      : margin.left + (idx / (traj.length - 1)) * graphWidth;
    const y = margin.top + graphHeight - ((pt.risk_score || 0) / 100) * graphHeight;
    return { x, y };
  };

  // Generate Smooth Curve Path
  const buildSmoothPath = () => {
    if (traj.length === 0) return '';
    const points = traj.map((pt, idx) => getPointCoords(pt, idx));
    if (points.length === 1) {
      return `M ${points[0].x} ${points[0].y}`;
    }
    let d = `M ${points[0].x} ${points[0].y}`;
    for (let i = 0; i < points.length - 1; i++) {
      const p0 = points[i];
      const p1 = points[i + 1];
      const cx1 = p0.x + (p1.x - p0.x) * 0.45;
      const cy1 = p0.y;
      const cx2 = p0.x + (p1.x - p0.x) * 0.55;
      const cy2 = p1.y;
      d += ` C ${cx1} ${cy1}, ${cx2} ${cy2}, ${p1.x} ${p1.y}`;
    }
    return d;
  };

  const getAcuityColor = (risk) => {
    if (risk >= 78) return '#DC2626';
    if (risk >= 58) return '#EA580C';
    if (risk >= 38) return '#D97706';
    return '#059669';
  };

  return (
    <div style={{ maxWidth: '1240px', margin: '0 auto', padding: '36px 24px 80px' }}>
      {/* HEADER & ACTIONS */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '24px', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <h1 style={{ fontSize: '2rem', fontWeight: 800, letterSpacing: '-0.02em', marginBottom: '6px' }}>
            Adaptive Triage: Longitudinal Trajectory
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
            Continuous emergency surveillance • Real-time multimodal reassessment with vital signs, ECG, and medical scans
          </p>
        </div>

        <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', fontWeight: 600 }}>Patient ID:</span>
            <input 
              type="text" 
              value={patientId} 
              onChange={(e) => setPatientId(e.target.value.toUpperCase())} 
              className="form-input" 
              style={{ width: '130px', padding: '7px 12px', fontWeight: 700, fontFamily: 'var(--font-mono)' }} 
            />
          </div>
          <button onClick={() => setShowAddModal(true)} className="btn btn-primary" style={{ padding: '8px 16px', gap: '8px' }}>
            <Plus size={16} />
            Add Observation
          </button>
        </div>
      </div>

      {/* THREE KEY RISK INDICATORS (Strict Requirement 2) */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
        gap: '16px',
        marginBottom: '28px'
      }}>
        {/* 1. Initial Risk */}
        <div className="glass-panel" style={{ padding: '20px 22px' }}>
          <div style={{ fontSize: '0.785rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 700, letterSpacing: '0.04em', marginBottom: '4px' }}>
            Initial Baseline Risk
          </div>
          <div style={{ fontSize: '2.1rem', fontWeight: 800, color: 'var(--text-primary)' }}>
            {initialRisk}%
          </div>
          <div style={{ fontSize: '0.785rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
            Assessment T1 Baseline
          </div>
        </div>

        {/* 2. Current Risk */}
        <div className="glass-panel" style={{ padding: '20px 22px' }}>
          <div style={{ fontSize: '0.785rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 700, letterSpacing: '0.04em', marginBottom: '4px' }}>
            Current Assessed Risk
          </div>
          <div style={{ fontSize: '2.1rem', fontWeight: 800, color: getAcuityColor(currentRisk) }}>
            {currentRisk}%
          </div>
          <div style={{ fontSize: '0.785rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
            Observation T{traj.length} (Latest)
          </div>
        </div>

        {/* 3. Risk Change */}
        <div className="glass-panel" style={{ padding: '20px 22px' }}>
          <div style={{ fontSize: '0.785rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 700, letterSpacing: '0.04em', marginBottom: '4px' }}>
            Net Risk Change
          </div>
          <div style={{
            fontSize: '2.1rem',
            fontWeight: 800,
            color: riskChange > 0 ? '#DC2626' : (riskChange < 0 ? '#059669' : '#64748B'),
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            {riskChange > 0 ? `+${riskChange} pp` : (riskChange < 0 ? `${riskChange} pp` : `0.0 pp`)}
            {riskChange > 0 && <TrendingUp size={24} color="#DC2626" />}
            {riskChange < 0 && <TrendingDown size={24} color="#059669" />}
            {riskChange === 0 && <Minus size={24} color="#64748B" />}
          </div>
          <div style={{ fontSize: '0.785rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
            {riskChange > 0 ? 'Urgency escalated' : (riskChange < 0 ? 'Physiological stabilization' : 'Baseline steady')}
          </div>
        </div>

        {/* Current Urgency Category */}
        <div className="glass-panel" style={{ padding: '20px 22px' }}>
          <div style={{ fontSize: '0.785rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 700, letterSpacing: '0.04em', marginBottom: '6px' }}>
            Current Urgency Level
          </div>
          <div style={{ marginBottom: '6px' }}>
            <span className={`priority-badge priority-${(latestPriority || 'LESS_URGENT').toLowerCase().replace('_', '-')}`} style={{ fontSize: '0.85rem', padding: '5px 12px' }}>
              {latestPriorityLabel}
            </span>
          </div>
          <div style={{ fontSize: '0.785rem', color: 'var(--text-secondary)' }}>
            Clinical Velocity: <strong style={{ color: overallTrend === 'Deteriorating' ? '#DC2626' : (overallTrend === 'Improving' ? '#059669' : '#D97706') }}>{overallTrend}</strong>
          </div>
        </div>
      </div>

      {/* LONGITUDINAL ACUITY TRAJECTORY GRAPH (Interactive & Zero-Overlap) */}
      <div className="glass-panel" style={{ padding: '28px 24px', marginBottom: '32px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '18px', flexWrap: 'wrap', gap: '10px' }}>
          <div>
            <h2 style={{ fontSize: '1.25rem', fontWeight: 800, marginBottom: '4px' }}>Longitudinal Acuity Trajectory</h2>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
              Hover or click any observation point to inspect time, acuity, and multimodal diagnostic inputs.
            </p>
          </div>
          <div style={{ display: 'flex', gap: '12px', alignItems: 'center', fontSize: '0.75rem' }}>
            <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
              <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#DC2626' }}></span> Critical (&gt;78%)
            </span>
            <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
              <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#EA580C' }}></span> Emergent (58-78%)
            </span>
            <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
              <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#D97706' }}></span> Urgent (38-58%)
            </span>
            <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
              <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#059669' }}></span> Low Risk (&lt;38%)
            </span>
          </div>
        </div>
        
        {traj.length > 0 ? (
          <div 
            ref={graphContainerRef}
            style={{ 
              position: 'relative', 
              background: '#FFFFFF', 
              border: '1px solid var(--border-medium)', 
              borderRadius: '12px', 
              padding: '16px 12px 10px',
              overflow: 'visible'
            }}
          >
            <svg 
              viewBox={`0 0 ${svgWidth} ${svgHeight}`} 
              style={{ width: '100%', height: 'auto', display: 'block', overflow: 'visible' }}
            >
              <defs>
                <linearGradient id="curveGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#10B981" stopOpacity="0.25" />
                  <stop offset="100%" stopColor="#10B981" stopOpacity="0.01" />
                </linearGradient>
              </defs>

              {/* Four Standard KTAS Risk Severity Background Zones (Strictly Non-overlapping) */}
              {/* Critical: 78% to 100% -> y: 35 to 77.9 (height: 42.9) */}
              <rect x={margin.left} y={margin.top} width={graphWidth} height={graphHeight * 0.22} fill="rgba(220, 38, 38, 0.05)" />
              <text x={margin.left + 8} y={margin.top + 16} fill="#B91C1C" fontSize="10" fontWeight="700" letterSpacing="0.04em">
                CRITICAL RESUSCITATION ZONE (&gt; 78%)
              </text>

              {/* Emergent: 58% to 78% -> y: 77.9 to 116.9 (height: 39) */}
              <rect x={margin.left} y={margin.top + graphHeight * 0.22} width={graphWidth} height={graphHeight * 0.20} fill="rgba(234, 88, 12, 0.04)" />
              <text x={margin.left + 8} y={margin.top + graphHeight * 0.22 + 16} fill="#C2410C" fontSize="10" fontWeight="700" letterSpacing="0.04em">
                HIGH / EMERGENT (58% – 78%)
              </text>

              {/* Moderate: 38% to 58% -> y: 116.9 to 155.9 (height: 39) */}
              <rect x={margin.left} y={margin.top + graphHeight * 0.42} width={graphWidth} height={graphHeight * 0.20} fill="rgba(217, 119, 6, 0.04)" />
              <text x={margin.left + 8} y={margin.top + graphHeight * 0.42 + 16} fill="#B45309" fontSize="10" fontWeight="700" letterSpacing="0.04em">
                MODERATE URGENT (38% – 58%)
              </text>

              {/* Low Risk: 0% to 38% -> y: 155.9 to 230 (height: 74.1) */}
              <rect x={margin.left} y={margin.top + graphHeight * 0.62} width={graphWidth} height={graphHeight * 0.38} fill="rgba(5, 150, 105, 0.04)" />
              <text x={margin.left + 8} y={margin.top + graphHeight * 0.62 + 16} fill="#047857" fontSize="10" fontWeight="700" letterSpacing="0.04em">
                STABLE / LOW RISK (&lt; 38%)
              </text>

              {/* Horizontal Reference Grid Lines with Y-Axis Percentages */}
              {[100, 78, 58, 38, 0].map((val) => {
                const yPos = margin.top + graphHeight - (val / 100) * graphHeight;
                return (
                  <g key={val}>
                    <line x1={margin.left} y1={yPos} x2={margin.left + graphWidth} y2={yPos} stroke="#E2E8F0" strokeDasharray={val === 0 || val === 100 ? "0" : "3,3"} strokeWidth="1" />
                    <text x={margin.left - 10} y={yPos + 4} fill="#64748B" fontSize="11" fontWeight="600" textAnchor="end">
                      {val}%
                    </text>
                  </g>
                );
              })}

              {/* Smooth Spline Trajectory Curve */}
              {traj.length > 1 && (
                <path
                  d={buildSmoothPath()}
                  fill="none"
                  stroke="#10B981"
                  strokeWidth="3.5"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              )}

              {/* Interactive Data Points and Clean Risk Badges */}
              {traj.map((pt, idx) => {
                const { x, y } = getPointCoords(pt, idx);
                const ptColor = getAcuityColor(pt.risk_score);
                const isHovered = hoveredPoint?.index === idx;

                return (
                  <g 
                    key={idx}
                    style={{ cursor: 'pointer' }}
                    onMouseEnter={(e) => {
                      const rect = graphContainerRef.current?.getBoundingClientRect();
                      const xRel = rect ? e.clientX - rect.left : x;
                      const yRel = rect ? e.clientY - rect.top : y;
                      setHoveredPoint({ pt, index: idx });
                      setActiveTooltipPos({ x: xRel, y: yRel });
                    }}
                    onMouseLeave={() => setHoveredPoint(null)}
                    onClick={() => {
                      setHoveredPoint({ pt, index: idx });
                    }}
                  >
                    {/* Pulsing ring for latest point */}
                    {idx === traj.length - 1 && (
                      <circle cx={x} cy={y} r="14" fill="none" stroke={ptColor} strokeWidth="1.5" opacity="0.4" />
                    )}

                    {/* Outer hover highlight */}
                    <circle cx={x} cy={y} r={isHovered ? "11" : "8"} fill={ptColor} stroke="#FFFFFF" strokeWidth="2.5" />

                    {/* Risk Percentage Label Badge (Offset to prevent any overlap) */}
                    <g transform={`translate(${x}, ${y < margin.top + 28 ? y + 20 : y - 14})`}>
                      <rect 
                        x="-20" 
                        y="-10" 
                        width="40" 
                        height="18" 
                        rx="4" 
                        fill={isHovered ? "#1E293B" : "#FFFFFF"} 
                        stroke={isHovered ? "#1E293B" : "#E2E8F0"} 
                        strokeWidth="1"
                      />
                      <text 
                        x="0" 
                        y="3" 
                        fill={isHovered ? "#FFFFFF" : ptColor} 
                        fontSize="11" 
                        fontWeight="800" 
                        textAnchor="middle"
                      >
                        {pt.risk_score}%
                      </text>
                    </g>

                    {/* X-Axis Observation Timestamp */}
                    <text x={x} y={svgHeight - 12} fill="#64748B" fontSize="11" fontWeight="700" textAnchor="middle">
                      T{idx + 1}
                    </text>
                    <text x={x} y={svgHeight - 1} fill="#94A3B8" fontSize="10" textAnchor="middle">
                      {pt.timestamp ? pt.timestamp.slice(11, 16) || pt.timestamp.slice(0, 5) : `T${idx+1}`}
                    </text>
                  </g>
                );
              })}
            </svg>

            {/* FLOATING INTERACTIVE TOOLTIP (Strict Requirement 3) */}
            {hoveredPoint && (
              <div 
                style={{
                  position: 'absolute',
                  left: `${activeTooltipPos.x}px`,
                  top: `${Math.max(activeTooltipPos.y - 12, 10)}px`,
                  transform: 'translate(-50%, -100%)',
                  background: '#0F172A',
                  color: '#FFFFFF',
                  borderRadius: '10px',
                  padding: '12px 16px',
                  boxShadow: '0 10px 25px rgba(0,0,0,0.25)',
                  pointerEvents: 'none',
                  zIndex: 20,
                  minWidth: '220px',
                  maxWidth: '280px',
                  border: '1px solid #334155'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid #334155', paddingBottom: '6px', marginBottom: '8px' }}>
                  <span style={{ fontWeight: 800, fontSize: '0.85rem', color: '#38BDF8' }}>
                    Observation T{hoveredPoint.index + 1}
                  </span>
                  <span style={{ fontSize: '0.75rem', color: '#94A3B8' }}>
                    {hoveredPoint.pt.timestamp}
                  </span>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                  <span style={{ fontSize: '0.8rem', color: '#CBD5E1' }}>Risk Percentage:</span>
                  <strong style={{ fontSize: '0.9rem', color: getAcuityColor(hoveredPoint.pt.risk_score) }}>
                    {hoveredPoint.pt.risk_score}%
                  </strong>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                  <span style={{ fontSize: '0.8rem', color: '#CBD5E1' }}>Triage Urgency:</span>
                  <strong style={{ fontSize: '0.8rem', color: '#F8FAFC' }}>
                    {hoveredPoint.pt.priority_label || hoveredPoint.pt.priority}
                  </strong>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                  <span style={{ fontSize: '0.8rem', color: '#CBD5E1' }}>Updated Input:</span>
                  <span style={{
                    fontSize: '0.725rem',
                    fontWeight: 700,
                    padding: '2px 6px',
                    borderRadius: '4px',
                    background: '#1E293B',
                    color: '#38BDF8',
                    border: '1px solid #0EA5E9'
                  }}>
                    {hoveredPoint.pt.updated_types ? hoveredPoint.pt.updated_types.join(' • ') : 'Vitals'}
                  </span>
                </div>

                {hoveredPoint.pt.reassessment_reason && (
                  <div style={{ borderTop: '1px solid #334155', paddingTop: '6px', fontSize: '0.725rem', color: '#94A3B8', lineHeight: 1.35 }}>
                    {hoveredPoint.pt.reassessment_reason}
                  </div>
                )}
              </div>
            )}
          </div>
        ) : (
          <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>
            No observations recorded yet. Click "Add Observation" to initiate dynamic trajectory.
          </div>
        )}
      </div>

      {/* ENRICHED OBSERVATION EVENT LOG (Requirement 3 & 4) */}
      <div className="glass-panel" style={{ padding: '24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '18px', flexWrap: 'wrap', gap: '10px' }}>
          <div>
            <h2 style={{ fontSize: '1.25rem', fontWeight: 800 }}>Observation Reassessment History</h2>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
              Chronological log of clinical vitals, newly acquired ECG signals, and diagnostic medical scans.
            </p>
          </div>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>
            {traj.length} Observation Time Points
          </span>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          {traj.map((pt, idx) => {
            const isLatest = idx === traj.length - 1;
            const updatedTypes = pt.updated_types || ['Vitals'];

            return (
              <div 
                key={idx} 
                style={{
                  padding: '18px 20px',
                  borderRadius: '10px',
                  background: isLatest ? '#F0FDF4' : '#F8FAFC',
                  border: isLatest ? '1px solid #BBF7D0' : '1px solid var(--border-subtle)',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '12px'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '12px' }}>
                  {/* Left: Time and observation marker */}
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <div style={{
                      width: '38px',
                      height: '38px',
                      borderRadius: '50%',
                      background: isLatest ? '#DCFCE7' : '#E2E8F0',
                      color: isLatest ? '#059669' : '#475569',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontWeight: 800,
                      fontSize: '0.95rem'
                    }}>
                      T{idx + 1}
                    </div>
                    <div>
                      <div style={{ fontWeight: 800, fontSize: '0.95rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <span>{pt.observation_id}</span>
                        <span style={{ fontSize: '0.785rem', color: 'var(--text-muted)', fontWeight: 500 }}>
                          • {pt.timestamp}
                        </span>
                        {isLatest && (
                          <span style={{ fontSize: '0.68rem', fontWeight: 700, padding: '2px 6px', borderRadius: '4px', background: '#DCFCE7', color: '#15803D' }}>
                            Latest
                          </span>
                        )}
                      </div>
                      {/* Vitals summary */}
                      <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
                        HR: <strong>{pt.vitals_summary?.hr ?? '—'}</strong> bpm • BP: <strong>{pt.vitals_summary?.sbp ?? '—'}/{pt.vitals_summary?.dbp ?? '—'}</strong> mmHg • SpO2: <strong>{pt.vitals_summary?.spo2 ?? '—'}%</strong> • Shock Index: <strong>{pt.vitals_summary?.shock_index ?? '—'}</strong>
                      </div>
                    </div>
                  </div>

                  {/* Right: Score, Priority, and Delta */}
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    {pt.delta_risk !== undefined && pt.delta_direction !== 'initial' && (
                      <span style={{
                        fontSize: '0.85rem',
                        fontWeight: 800,
                        padding: '4px 8px',
                        borderRadius: '6px',
                        background: pt.delta_risk > 0 ? '#FEE2E2' : '#DCFCE7',
                        color: pt.delta_risk > 0 ? '#DC2626' : '#059669',
                        border: pt.delta_risk > 0 ? '1px solid #FCA5A5' : '1px solid #86EFAC'
                      }}>
                        {pt.delta_risk > 0 ? `+${pt.delta_risk}%` : `${pt.delta_risk}%`}
                      </span>
                    )}
                    <span className={`priority-badge priority-${pt.priority.toLowerCase().replace('_', '-')}`} style={{ padding: '4px 10px' }}>
                      {pt.priority_label || pt.priority}
                    </span>
                    <span style={{ fontWeight: 800, fontSize: '1.25rem', minWidth: '45px', textAlign: 'right' }}>
                      {pt.risk_score}%
                    </span>
                  </div>
                </div>

                {/* Modality Badges & Updated Inputs */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>Inputs:</span>
                  {updatedTypes.map((type, tIdx) => (
                    <span key={tIdx} style={{
                      fontSize: '0.725rem',
                      fontWeight: 700,
                      padding: '2px 7px',
                      borderRadius: '4px',
                      background: type === 'ECG' ? '#ECFDF5' : (type === 'Medical Scan' ? '#FEFCE8' : '#EFF6FF'),
                      color: type === 'ECG' ? '#059669' : (type === 'Medical Scan' ? '#D97706' : '#1D4ED8'),
                      border: '1px solid rgba(0,0,0,0.06)'
                    }}>
                      {type}
                    </span>
                  ))}

                  {/* ECG Finding Pill */}
                  {pt.ecg_summary && (
                    <span style={{
                      fontSize: '0.725rem',
                      padding: '2px 7px',
                      borderRadius: '4px',
                      background: pt.ecg_summary.is_abnormal ? '#FEF2F2' : '#ECFDF5',
                      color: pt.ecg_summary.is_abnormal ? '#DC2626' : '#059669',
                      fontWeight: 600
                    }}>
                      ECG: {pt.ecg_summary.predicted_class || 'Lead Analyzed'}
                    </span>
                  )}

                  {/* Medical Scan Finding Pill */}
                  {pt.scan_summary && (
                    <span style={{
                      fontSize: '0.725rem',
                      padding: '2px 7px',
                      borderRadius: '4px',
                      background: pt.scan_summary.is_abnormal ? '#FEF2F2' : '#F0FDF4',
                      color: pt.scan_summary.is_abnormal ? '#DC2626' : '#059669',
                      fontWeight: 600
                    }}>
                      Scan: {pt.scan_summary.top_condition || 'Scan Evaluated'}
                    </span>
                  )}
                </div>

                {/* Reassessment Reason (Section 3 Prompt Pattern) */}
                {pt.reassessment_reason && (
                  <div style={{
                    fontSize: '0.8rem',
                    color: 'var(--text-secondary)',
                    background: 'rgba(255,255,255,0.7)',
                    padding: '8px 12px',
                    borderRadius: '6px',
                    borderLeft: '3px solid #10B981',
                    lineHeight: 1.4
                  }}>
                    <strong>Clinical Rationale:</strong> {pt.reassessment_reason}
                  </div>
                )}

                {/* Critical Safety Overrides if Triggered */}
                {pt.safety_overrides && pt.safety_overrides.length > 0 && (
                  <div style={{
                    fontSize: '0.75rem',
                    color: '#B91C1C',
                    background: '#FEF2F2',
                    padding: '6px 10px',
                    borderRadius: '6px',
                    border: '1px solid #FECACA',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px'
                  }}>
                    <AlertCircle size={14} color="#DC2626" />
                    <span><strong>Safety Override Triggered:</strong> {pt.safety_overrides.join(' • ')}</span>
                  </div>
                )}

                {/* View Explainability & Full Assessment */}
                {onViewAssessment && pt.assessment_id && (
                  <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '2px' }}>
                    <button
                      type="button"
                      onClick={async () => {
                        try {
                          const fullAssessment = await api.getAssessment(pt.assessment_id);
                          onViewAssessment(fullAssessment);
                        } catch {
                          onViewAssessment(pt);
                        }
                      }}
                      style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '6px',
                        padding: '5px 12px',
                        borderRadius: '6px',
                        background: '#FFFFFF',
                        border: '1px solid var(--border-subtle)',
                        color: '#059669',
                        fontSize: '0.785rem',
                        fontWeight: 700,
                        cursor: 'pointer',
                        boxShadow: '0 1px 3px rgba(0,0,0,0.04)'
                      }}
                    >
                      <Layers size={13} color="#059669" />
                      Why This Priority? (View Explainability)
                    </button>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* ADD OBSERVATION MODAL (Updated with ECG and Medical Scan Inputs) */}
      {showAddModal && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          background: 'rgba(15, 23, 42, 0.45)',
          backdropFilter: 'blur(6px)',
          zIndex: 200,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '20px'
        }}>
          <div 
            className="glass-panel" 
            style={{ 
              background: '#FFFFFF', 
              maxWidth: '620px', 
              width: '100%', 
              padding: '28px', 
              maxHeight: '90vh', 
              overflowY: 'auto' 
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
              <h2 style={{ fontSize: '1.4rem', fontWeight: 800 }}>Add Observation: {patientId}</h2>
              <button 
                type="button" 
                onClick={() => setShowAddModal(false)}
                style={{ background: 'transparent', border: 'none', cursor: 'pointer', color: 'var(--text-muted)' }}
              >
                <X size={20} />
              </button>
            </div>
            
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', marginBottom: '20px' }}>
              Update vital signs, upload an updated ECG lead signal, or attach a new medical scan to recalculate dynamic risk progression.
            </p>

            <form onSubmit={handleAddObservation}>
              {/* SECTION A: UPDATED VITAL SIGNS */}
              <div style={{ marginBottom: '20px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '10px' }}>
                  <Heart size={16} color="#059669" />
                  <span style={{ fontSize: '0.85rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-primary)', letterSpacing: '0.04em' }}>
                    Section A: Updated Vital Signs (Optional)
                  </span>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                  <div className="input-group">
                    <label className="input-label">Systolic BP (mmHg)</label>
                    <input 
                      type="number" 
                      min="20"
                      max="300"
                      value={obsVitals.sbp} 
                      onChange={(e) => setObsVitals({ ...obsVitals, sbp: parseFloat(e.target.value) || '' })} 
                      className="form-input" 
                      placeholder="e.g. 120"
                    />
                  </div>
                  <div className="input-group">
                    <label className="input-label">Heart Rate (bpm)</label>
                    <input 
                      type="number" 
                      min="20"
                      max="350"
                      value={obsVitals.hr} 
                      onChange={(e) => setObsVitals({ ...obsVitals, hr: parseFloat(e.target.value) || '' })} 
                      className="form-input" 
                      placeholder="e.g. 75"
                    />
                  </div>
                  <div className="input-group">
                    <label className="input-label">SpO2 (%)</label>
                    <input 
                      type="number" 
                      min="10"
                      max="100"
                      value={obsVitals.saturation} 
                      onChange={(e) => setObsVitals({ ...obsVitals, saturation: parseFloat(e.target.value) || '' })} 
                      className="form-input" 
                      placeholder="e.g. 98"
                    />
                  </div>
                  <div className="input-group">
                    <label className="input-label">Respiratory Rate (/min)</label>
                    <input 
                      type="number" 
                      min="0"
                      max="150"
                      value={obsVitals.rr} 
                      onChange={(e) => setObsVitals({ ...obsVitals, rr: parseFloat(e.target.value) || '' })} 
                      className="form-input" 
                      placeholder="e.g. 16"
                    />
                  </div>
                </div>
              </div>

              {/* SECTION B: UPDATED DIAGNOSTIC INPUTS (ECG & MEDICAL SCANS) */}
              <div style={{ marginBottom: '20px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '10px' }}>
                  <Activity size={16} color="#059669" />
                  <span style={{ fontSize: '0.85rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-primary)', letterSpacing: '0.04em' }}>
                    Section B: Updated Diagnostic Inputs (Optional)
                  </span>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px' }}>
                  {/* Updated ECG Upload */}
                  <div style={{
                    border: '1px dashed var(--border-medium)',
                    borderRadius: '8px',
                    padding: '12px',
                    background: '#F8FAFC',
                    textAlign: 'center'
                  }}>
                    <div style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '4px' }}>
                      Updated ECG Lead (.csv)
                    </div>
                    {ecgFileName ? (
                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', background: '#FFFFFF', padding: '6px 10px', borderRadius: '6px', border: '1px solid #A7F3D0', marginTop: '6px' }}>
                        <div style={{ textAlign: 'left', overflow: 'hidden' }}>
                          <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#065F46', textOverflow: 'ellipsis', overflow: 'hidden', whiteSpace: 'nowrap' }}>
                            {ecgFileName}
                          </div>
                          <div style={{ fontSize: '0.68rem', color: '#059669' }}>Ready for 1D-CNN</div>
                        </div>
                        <button 
                          type="button" 
                          onClick={() => { setEcgFile(null); setEcgFileName(''); }}
                          style={{ background: 'transparent', border: 'none', cursor: 'pointer', color: '#DC2626' }}
                          title="Remove ECG file"
                        >
                          <X size={14} />
                        </button>
                      </div>
                    ) : (
                      <label style={{ cursor: 'pointer', display: 'block', padding: '8px 4px' }}>
                        <Upload size={18} color="#059669" style={{ margin: '0 auto 4px' }} />
                        <span style={{ fontSize: '0.75rem', color: '#059669', fontWeight: 600 }}>Choose ECG CSV</span>
                        <input 
                          type="file" 
                          accept=".csv,.txt" 
                          onChange={handleEcgChange} 
                          style={{ display: 'none' }} 
                        />
                      </label>
                    )}
                  </div>

                  {/* Updated Medical Scan Upload */}
                  <div style={{
                    border: '1px dashed var(--border-medium)',
                    borderRadius: '8px',
                    padding: '12px',
                    background: '#F8FAFC',
                    textAlign: 'center'
                  }}>
                    <div style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '4px' }}>
                      Updated Medical Scan
                    </div>
                    {scanFileName ? (
                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', background: '#FFFFFF', padding: '6px 10px', borderRadius: '6px', border: '1px solid #FDE68A', marginTop: '6px' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', overflow: 'hidden' }}>
                          {scanPreview && (
                            <img src={scanPreview} alt="scan preview" style={{ width: '28px', height: '28px', objectFit: 'cover', borderRadius: '4px' }} />
                          )}
                          <div style={{ textAlign: 'left', overflow: 'hidden' }}>
                            <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#92400E', textOverflow: 'ellipsis', overflow: 'hidden', whiteSpace: 'nowrap', maxWidth: '130px' }}>
                              {scanFileName}
                            </div>
                            <div style={{ fontSize: '0.68rem', color: '#D97706' }}>DenseNet + Vision AI</div>
                          </div>
                        </div>
                        <button 
                          type="button" 
                          onClick={() => { setScanFile(null); setScanFileName(''); setScanPreview(null); }}
                          style={{ background: 'transparent', border: 'none', cursor: 'pointer', color: '#DC2626' }}
                          title="Remove Scan file"
                        >
                          <X size={14} />
                        </button>
                      </div>
                    ) : (
                      <label style={{ cursor: 'pointer', display: 'block', padding: '8px 4px' }}>
                        <Upload size={18} color="#D97706" style={{ margin: '0 auto 4px' }} />
                        <span style={{ fontSize: '0.75rem', color: '#D97706', fontWeight: 600 }}>Choose Scan Image</span>
                        <input 
                          type="file" 
                          accept=".png,.jpg,.jpeg,.webp" 
                          onChange={handleScanChange} 
                          style={{ display: 'none' }} 
                        />
                      </label>
                    )}
                  </div>
                </div>
              </div>

              {/* SECTION C: REASON FOR REASSESSMENT */}
              <div style={{ marginBottom: '22px' }}>
                <label className="input-label">Reason for Reassessment / Clinical Note (Optional)</label>
                <input 
                  type="text" 
                  value={reassessmentReason}
                  onChange={(e) => setReassessmentReason(e.target.value)}
                  className="form-input"
                  placeholder="e.g. Follow-up after oxygen therapy / New sudden chest pain / Routine hourly vitals check"
                />
              </div>

              {/* ACTION BUTTONS */}
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px' }}>
                <button type="button" onClick={() => setShowAddModal(false)} className="btn btn-secondary">
                  Cancel
                </button>
                <button type="submit" disabled={submitting} className="btn btn-primary" style={{ padding: '9px 20px', gap: '8px' }}>
                  {submitting ? (
                    <>
                      <RefreshCw size={15} className="spin-animate" />
                      Recalculating with Multimodal AI...
                    </>
                  ) : (
                    'Recalculate Dynamic Risk'
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
