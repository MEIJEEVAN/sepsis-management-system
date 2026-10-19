-- Sepsis detection, alerting and housekeeping triggers.

CREATE OR REPLACE FUNCTION sepsis_stage_rank(p_stage TEXT) RETURNS INT
LANGUAGE sql IMMUTABLE AS $$
  SELECT CASE p_stage
           WHEN 'sirs' THEN 1 WHEN 'sepsis' THEN 2
           WHEN 'severe_sepsis' THEN 3 WHEN 'septic_shock' THEN 4 ELSE 0 END;
$$;

CREATE OR REPLACE FUNCTION assess_sepsis(p_patient_id INT)
RETURNS TABLE(
  sepsis_detected BOOLEAN, stage TEXT, sirs_score INT, qsofa_score INT,
  episode_id INT, message TEXT, severity TEXT, new_episode BOOLEAN, escalated BOOLEAN
)
LANGUAGE plpgsql AS $$
#variable_conflict use_column
DECLARE
  rv        vital_signs%ROWTYPE;
  rl        lab_results%ROWTYPE;
  v_sirs    INT := 0;
  v_qsofa   INT := 0;
  v_stage   TEXT;
  v_sev     TEXT;
  v_msg     TEXT;
  v_ep      INT;
  v_old     TEXT;
  v_new     BOOLEAN := FALSE;
  v_esc     BOOLEAN := FALSE;
  v_conf    NUMERIC(4,2);
BEGIN
  SELECT * INTO rv FROM vital_signs WHERE patient_id = p_patient_id
    ORDER BY recorded_at DESC, id DESC LIMIT 1;
  SELECT * INTO rl FROM lab_results WHERE patient_id = p_patient_id
    ORDER BY recorded_at DESC, id DESC LIMIT 1;

  -- SIRS (one point per criterion group)
  IF COALESCE(rv.temperature > 38 OR rv.temperature < 36, FALSE) THEN v_sirs := v_sirs + 1; END IF;
  IF COALESCE(rv.heart_rate > 90, FALSE) THEN v_sirs := v_sirs + 1; END IF;
  IF COALESCE(rv.respiratory_rate > 20 OR rv.spo2 < 90, FALSE) THEN v_sirs := v_sirs + 1; END IF;
  IF COALESCE(rl.wbc > 12 OR rl.wbc < 4, FALSE) THEN v_sirs := v_sirs + 1; END IF;

  -- qSOFA
  IF COALESCE(rv.respiratory_rate >= 22, FALSE) THEN v_qsofa := v_qsofa + 1; END IF;
  IF COALESCE(rv.systolic_bp <= 100, FALSE) THEN v_qsofa := v_qsofa + 1; END IF;
  IF COALESCE(rv.gcs < 15, FALSE) THEN v_qsofa := v_qsofa + 1; END IF;

  IF v_sirs < 2 THEN
    -- Criteria no longer met: close an episode that has been open for more than 5 minutes.
    UPDATE sepsis_episodes
       SET outcome = 'recovered',
           notes = COALESCE(notes || E'\n', '') || 'Auto-resolved: criteria no longer met'
     WHERE patient_id = p_patient_id AND outcome = 'ongoing'
       AND detected_at < now() - INTERVAL '5 minutes';
    RETURN QUERY SELECT FALSE, NULL::TEXT, v_sirs, v_qsofa, NULL::INT, NULL::TEXT,
                        NULL::TEXT, FALSE, FALSE;
    RETURN;
  END IF;

  IF COALESCE(rv.systolic_bp < 90, FALSE) OR COALESCE(rl.lactate >= 4, FALSE) THEN
    v_stage := 'septic_shock'; v_sev := 'critical';
  ELSIF COALESCE(rl.lactate > 2, FALSE) THEN
    v_stage := 'sepsis'; v_sev := 'high';
  ELSE
    v_stage := 'sirs'; v_sev := 'medium';
  END IF;

  v_conf := LEAST(1.0, ROUND(v_sirs / 4.0 * 0.6 + v_qsofa / 3.0 * 0.4, 2));
  v_msg := format('%s: SIRS %s/4, qSOFA %s/3%s',
                  upper(replace(v_stage, '_', ' ')), v_sirs, v_qsofa,
                  CASE WHEN rl.lactate IS NOT NULL THEN ', lactate ' || rl.lactate ELSE '' END);

  SELECT id, stage INTO v_ep, v_old FROM sepsis_episodes
   WHERE patient_id = p_patient_id AND outcome = 'ongoing'
   ORDER BY detected_at DESC LIMIT 1 FOR UPDATE;

  IF FOUND THEN
    UPDATE sepsis_episodes
       SET sirs_score = v_sirs, qsofa_score = v_qsofa, stage = v_stage, confidence_score = v_conf
     WHERE id = v_ep;
    v_esc := sepsis_stage_rank(v_stage) > sepsis_stage_rank(v_old);
  ELSE
    INSERT INTO sepsis_episodes (patient_id, sirs_score, qsofa_score, stage, confidence_score)
    VALUES (p_patient_id, v_sirs, v_qsofa, v_stage, v_conf)
    RETURNING id INTO v_ep;
    v_new := TRUE;
  END IF;

  RETURN QUERY SELECT TRUE, v_stage, v_sirs, v_qsofa, v_ep, v_msg, v_sev, v_new, v_esc;
END;
$$;

-- Inserts an alert and publishes it on alerts_channel (delivered to listeners on commit).
CREATE OR REPLACE FUNCTION raise_sepsis_alert(
  p_patient_id INT, p_episode_id INT, p_message TEXT, p_severity TEXT, p_stage TEXT
) RETURNS INT
LANGUAGE plpgsql AS $$
DECLARE
  v_alert alerts%ROWTYPE;
  v_name  TEXT;
BEGIN
  INSERT INTO alerts (patient_id, episode_id, message, severity)
  VALUES (p_patient_id, p_episode_id, p_message, p_severity)
  RETURNING * INTO v_alert;

  SELECT p.mrn || ' ' || p.first_name || ' ' || p.last_name INTO v_name
    FROM patients p WHERE p.id = p_patient_id;

  PERFORM pg_notify('alerts_channel', json_build_object(
    'alert_id', v_alert.id, 'patient_id', p_patient_id, 'patient_name', v_name,
    'episode_id', p_episode_id, 'stage', p_stage, 'message', p_message,
    'severity', p_severity, 'created_at', v_alert.created_at)::text);
  RETURN v_alert.id;
END;
$$;

CREATE OR REPLACE FUNCTION trg_fn_assess_sepsis() RETURNS trigger
LANGUAGE plpgsql AS $$
DECLARE
  r RECORD;
  v_alert_id INT;
BEGIN
  SELECT * INTO r FROM assess_sepsis(NEW.patient_id);
  IF r.sepsis_detected AND (r.new_episode OR r.escalated) THEN
    v_alert_id := raise_sepsis_alert(NEW.patient_id, r.episode_id, r.message, r.severity, r.stage);
  END IF;
  RETURN NULL;
END;
$$;

DROP TRIGGER IF EXISTS trg_vitals_sepsis ON vital_signs;
CREATE TRIGGER trg_vitals_sepsis AFTER INSERT ON vital_signs
  FOR EACH ROW EXECUTE FUNCTION trg_fn_assess_sepsis();

DROP TRIGGER IF EXISTS trg_labs_sepsis ON lab_results;
CREATE TRIGGER trg_labs_sepsis AFTER INSERT ON lab_results
  FOR EACH ROW EXECUTE FUNCTION trg_fn_assess_sepsis();

CREATE OR REPLACE FUNCTION trg_fn_patients_updated_at() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
  NEW.updated_at := now();
  RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_patients_updated_at ON patients;
CREATE TRIGGER trg_patients_updated_at BEFORE UPDATE ON patients
  FOR EACH ROW EXECUTE FUNCTION trg_fn_patients_updated_at();

CREATE OR REPLACE FUNCTION trg_fn_patients_audit() RETURNS trigger
LANGUAGE plpgsql AS $$
DECLARE
  v_diff JSONB;
  v_user INT := NULLIF(current_setting('app.user_id', TRUE), '')::INT;
BEGIN
  IF TG_OP = 'INSERT' THEN
    INSERT INTO audit_logs (user_id, action, entity, entity_id, details)
    VALUES (v_user, 'INSERT', 'patients', NEW.id, to_jsonb(NEW));
  ELSE
    SELECT COALESCE(jsonb_object_agg(n.key, jsonb_build_object('old', o.value, 'new', n.value)),
                    '{}'::jsonb)
      INTO v_diff
      FROM jsonb_each(to_jsonb(NEW)) n
      JOIN jsonb_each(to_jsonb(OLD)) o USING (key)
     WHERE n.value IS DISTINCT FROM o.value AND n.key <> 'updated_at';
    IF v_diff <> '{}'::jsonb THEN
      INSERT INTO audit_logs (user_id, action, entity, entity_id, details)
      VALUES (v_user, 'UPDATE', 'patients', NEW.id, v_diff);
    END IF;
  END IF;
  RETURN NULL;
END;
$$;

DROP TRIGGER IF EXISTS trg_patients_audit ON patients;
CREATE TRIGGER trg_patients_audit AFTER INSERT OR UPDATE ON patients
  FOR EACH ROW EXECUTE FUNCTION trg_fn_patients_audit();
