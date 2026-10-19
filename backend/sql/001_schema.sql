-- Authoritative DDL for the Sepsis Management System.
CREATE TABLE users (
  id            SERIAL PRIMARY KEY,
  username      VARCHAR(80)  NOT NULL UNIQUE,
  email         VARCHAR(120) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  full_name     VARCHAR(120),
  role          VARCHAR(20)  NOT NULL DEFAULT 'clinician'
                CHECK (role IN ('admin','clinician','nurse')),
  is_active     BOOLEAN      NOT NULL DEFAULT TRUE,
  created_at    TIMESTAMPTZ  NOT NULL DEFAULT now()
);

CREATE TABLE patients (
  id             SERIAL PRIMARY KEY,
  mrn            VARCHAR(50)  NOT NULL UNIQUE,
  first_name     VARCHAR(80)  NOT NULL,
  last_name      VARCHAR(80)  NOT NULL,
  dob            DATE,
  gender         VARCHAR(20)  CHECK (gender IN ('Male','Female','Other','Unknown')),
  admission_date TIMESTAMPTZ  NOT NULL DEFAULT now(),
  bed_number     VARCHAR(20),
  status         VARCHAR(20)  NOT NULL DEFAULT 'active'
                 CHECK (status IN ('active','discharged','transferred')),
  created_at     TIMESTAMPTZ  NOT NULL DEFAULT now(),
  updated_at     TIMESTAMPTZ  NOT NULL DEFAULT now()
);

CREATE TABLE vital_signs (
  id               BIGSERIAL PRIMARY KEY,
  patient_id       INT NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
  recorded_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  temperature      NUMERIC(4,1) CHECK (temperature BETWEEN 30 AND 45),
  heart_rate       INT          CHECK (heart_rate BETWEEN 20 AND 250),
  respiratory_rate INT          CHECK (respiratory_rate BETWEEN 4 AND 60),
  systolic_bp      INT          CHECK (systolic_bp BETWEEN 40 AND 300),
  diastolic_bp     INT          CHECK (diastolic_bp BETWEEN 20 AND 200),
  spo2             NUMERIC(4,1) CHECK (spo2 BETWEEN 50 AND 100),
  gcs              INT          CHECK (gcs BETWEEN 3 AND 15)
);
CREATE INDEX idx_vitals_patient_time ON vital_signs (patient_id, recorded_at DESC);

CREATE TABLE lab_results (
  id             BIGSERIAL PRIMARY KEY,
  patient_id     INT NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
  recorded_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  wbc            NUMERIC(6,1) CHECK (wbc BETWEEN 0 AND 100),
  lactate        NUMERIC(5,2) CHECK (lactate BETWEEN 0 AND 30),
  crp            NUMERIC(8,2) CHECK (crp BETWEEN 0 AND 500),
  procalcitonin  NUMERIC(8,2) CHECK (procalcitonin BETWEEN 0 AND 100),
  creatinine     NUMERIC(6,2) CHECK (creatinine BETWEEN 0 AND 20),
  bilirubin      NUMERIC(6,2) CHECK (bilirubin BETWEEN 0 AND 30),
  platelets      INT          CHECK (platelets BETWEEN 0 AND 1000),
  inr            NUMERIC(4,2) CHECK (inr BETWEEN 0.5 AND 10)
);
CREATE INDEX idx_labs_patient_time ON lab_results (patient_id, recorded_at DESC);

CREATE TABLE sepsis_episodes (
  id               SERIAL PRIMARY KEY,
  patient_id       INT NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
  detected_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  sirs_score       INT,
  qsofa_score      INT,
  stage            VARCHAR(20) CHECK (stage IN ('sirs','sepsis','severe_sepsis','septic_shock')),
  confidence_score NUMERIC(4,2) CHECK (confidence_score BETWEEN 0 AND 1),
  outcome          VARCHAR(20) DEFAULT 'ongoing'
                   CHECK (outcome IN ('ongoing','recovered','died')),
  notes            TEXT
);
CREATE INDEX idx_episodes_patient ON sepsis_episodes (patient_id, detected_at DESC);
-- At most one ongoing episode per patient (deduplication guarantee).
CREATE UNIQUE INDEX ux_one_ongoing_episode ON sepsis_episodes (patient_id)
  WHERE outcome = 'ongoing';

CREATE TABLE alerts (
  id              SERIAL PRIMARY KEY,
  patient_id      INT NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
  episode_id      INT REFERENCES sepsis_episodes(id) ON DELETE SET NULL,
  message         VARCHAR(255) NOT NULL,
  severity        VARCHAR(20) NOT NULL DEFAULT 'medium'
                  CHECK (severity IN ('low','medium','high','critical')),
  acknowledged    BOOLEAN NOT NULL DEFAULT FALSE,
  acknowledged_by INT REFERENCES users(id),
  acknowledged_at TIMESTAMPTZ,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_alerts_unacked ON alerts (acknowledged, created_at DESC);

CREATE TABLE protocols (
  id          SERIAL PRIMARY KEY,
  title       VARCHAR(120) NOT NULL,
  description TEXT,
  criteria    TEXT,
  active      BOOLEAN NOT NULL DEFAULT TRUE,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE audit_logs (
  id         BIGSERIAL PRIMARY KEY,
  user_id    INT REFERENCES users(id),
  action     VARCHAR(50) NOT NULL,
  entity     VARCHAR(50) NOT NULL,
  entity_id  INT,
  details    JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_audit_entity ON audit_logs (entity, entity_id, created_at DESC);
