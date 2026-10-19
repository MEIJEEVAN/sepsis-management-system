# Prepared queries

Run these in DBeaver (`Ctrl+Enter`). Numbers vary with the simulator's progress.

## Q1: latest vitals per patient (LATERAL)
```sql
SELECT p.mrn, p.first_name, p.last_name, v.*
FROM patients p
LEFT JOIN LATERAL (
  SELECT recorded_at, temperature, heart_rate, respiratory_rate,
         systolic_bp, diastolic_bp, spo2, gcs
  FROM vital_signs vs WHERE vs.patient_id = p.id
  ORDER BY vs.recorded_at DESC LIMIT 1
) v ON TRUE
ORDER BY p.id;
```
Expected: 10 rows. Before the simulator runs the vitals are NULL. After t=40 s patient 9 shows
SBP about 83-85, RR 26 and GCS 14, while patients 1-4 stay near HR 76, SBP 122.

## Q2: episodes by stage
```sql
SELECT stage, count(*) AS episodes, max(detected_at) AS last_detected
FROM sepsis_episodes GROUP BY stage ORDER BY episodes DESC;
```
Expected: 1-3 rows (`septic_shock`, `sepsis`, `sirs`). The total never exceeds the number of patients
that have deteriorated, because one episode per patient is updated in place.

## Q3: patients with lactate above 2 (CTE)
```sql
WITH latest AS (
  SELECT DISTINCT ON (patient_id) patient_id, lactate, recorded_at
  FROM lab_results ORDER BY patient_id, recorded_at DESC
)
SELECT p.mrn, p.first_name, l.lactate, l.recorded_at
FROM latest l JOIN patients p ON p.id = l.patient_id
WHERE l.lactate > 2 ORDER BY l.lactate DESC;
```
Expected: patient 10 (about 3.4) at t=0, then patient 9 (about 4.5 by t=90), patients 7 and 8 (about 3.2-3.5 by t=120).

## Q4: index proof
```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM vital_signs WHERE patient_id = 9
ORDER BY recorded_at DESC LIMIT 1;
```
Expected: `Index Scan using idx_vitals_patient_time on vital_signs`, with a `patient_id = 9` index
condition and no Sort node. On a tiny table the planner may pick a Seq Scan; if so run
`SET enable_seqscan = off;` first, or run it after the simulator has produced a few thousand rows.

## Q5: active connections
```sql
SELECT application_name, client_addr, state, query
FROM pg_stat_activity WHERE datname = 'sepsis_db';
```
Expected: `sepsis_flask` (API pool) and `sepsis_sse` (one per open dashboard, in `idle` state while it
waits for NOTIFY). The simulator talks only to the API, so it appears indirectly through `sepsis_flask`.

## Q6: notification queue usage
```sql
SELECT * FROM pg_notification_queue_usage();
```
Expected: a value near 0, meaning listeners are consuming notifications.
