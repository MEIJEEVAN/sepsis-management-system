CREATE OR REPLACE VIEW v_patient_current_status AS
SELECT p.id AS patient_id, p.mrn, p.first_name, p.last_name, p.bed_number,
       v.recorded_at AS vitals_at, v.temperature, v.heart_rate, v.respiratory_rate,
       v.systolic_bp, v.diastolic_bp, v.spo2, v.gcs,
       l.recorded_at AS labs_at, l.wbc, l.lactate, l.crp, l.procalcitonin,
       l.creatinine, l.bilirubin, l.platelets, l.inr,
       e.id AS episode_id, e.stage AS episode_stage, e.outcome AS episode_outcome,
       e.detected_at AS episode_detected_at
FROM patients p
LEFT JOIN LATERAL (
  SELECT * FROM vital_signs vs WHERE vs.patient_id = p.id
  ORDER BY vs.recorded_at DESC, vs.id DESC LIMIT 1
) v ON TRUE
LEFT JOIN LATERAL (
  SELECT * FROM lab_results lr WHERE lr.patient_id = p.id
  ORDER BY lr.recorded_at DESC, lr.id DESC LIMIT 1
) l ON TRUE
LEFT JOIN LATERAL (
  SELECT se.id, se.stage, se.outcome, se.detected_at FROM sepsis_episodes se
  WHERE se.patient_id = p.id ORDER BY se.detected_at DESC LIMIT 1
) e ON TRUE
WHERE p.status = 'active';

CREATE OR REPLACE VIEW v_active_alerts AS
SELECT a.id AS alert_id, a.patient_id, p.mrn, p.first_name, p.last_name,
       a.message, a.severity, a.created_at, a.episode_id, e.stage AS episode_stage
FROM alerts a
JOIN patients p ON p.id = a.patient_id
LEFT JOIN sepsis_episodes e ON e.id = a.episode_id
WHERE NOT a.acknowledged;

CREATE OR REPLACE VIEW v_sepsis_stats AS
SELECT e.stage,
       count(*) AS episodes,
       count(*) FILTER (WHERE e.outcome = 'ongoing') AS ongoing_episodes,
       avg(now() - e.detected_at) AS avg_time_since_detection,
       (SELECT count(*) FROM alerts WHERE severity = 'critical') AS critical_alerts_total
FROM sepsis_episodes e
GROUP BY e.stage;
