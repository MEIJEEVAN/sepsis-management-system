# Live demo script (about 15 minutes)

**Before you start:** the database is loaded, the API and Vite are running, the browser is logged in
at http://localhost:5173, and the simulator is **not** running yet. Open DBeaver with a SQL editor,
a terminal for the simulator and a terminal for `psql`.

| Time | Action | What the professor sees |
|---|---|---|
| 0:00 | **Connect DBeaver.** Database -> New Database Connection -> PostgreSQL. Host `localhost`, Port `5432`, Database `sepsis_db`, Username `sepsis_user`, Password `sepsis_pass`. Click **Test Connection**, then **Finish**. | Live PostgreSQL connection |
| 0:30 | Expand `sepsis_db -> Schemas -> public`, right-click **public** -> **View Diagram**. | ER diagram with all foreign keys |
| 2:00 | Open `docs/DATABASE_SCHEMA.md`. Point at the CHECK constraints, UNIQUE keys, the partial unique index and the indexes. | Integrity and normalisation |
| 3:00 | `SELECT * FROM patients;` | 10 patients (created by the simulator on its first run, or insert a few by hand) |
| 3:30 | Run **Q1** from `docs/QUERIES.md`. | LATERAL join, one row per patient |
| 5:00 | `SELECT * FROM v_patient_current_status LIMIT 10;` | The view |
| 5:30 | `SELECT * FROM v_sepsis_stats;` | Aggregation |
| 6:00 | In a terminal: `cd backend && uv run python simulate.py --speed 1` (keep it on screen). | One line per insert with its HTTP status |
| 6:30 | Run `SELECT count(*) FROM vital_signs;` three times, 10 s apart. | Count climbing live |
| 7:30 | `SELECT * FROM v_active_alerts ORDER BY created_at DESC;` | Alerts nobody wrote in Python |
| 8:30 | Run **Q4** (`EXPLAIN (ANALYZE, BUFFERS)`). | `Index Scan using idx_vitals_patient_time` |
| 9:30 | Run the insert below, then the select below it. | The trigger created an alert from a plain INSERT |
| 10:30 | In a terminal: `PGPASSWORD=sepsis_pass psql -h localhost -U sepsis_user -d sepsis_db`, then `LISTEN alerts_channel;`. psql prints notifications after the next statement, so press Enter or run `SELECT 1;` periodically. | Raw JSON payloads |
| 11:30 | Switch to the browser dashboard. | AlertFeed updating from the same channel; DevTools -> Network shows one `stream/alerts` request |
| 12:30 | Run the update below, then the select below it. | Audit trigger with a JSONB diff |
| 13:30 | In psql: `\d+ vital_signs` (or DBeaver: open the table -> Properties/Constraints/Indexes). | Constraints and index list |
| 14:00 | Q&A | |

**9:30, manual insert** (patient 3 is stable in the simulator, so this creates a new episode):
```sql
INSERT INTO vital_signs (patient_id, temperature, heart_rate, respiratory_rate,
                         systolic_bp, diastolic_bp, spo2, gcs)
VALUES (3, 39.5, 130, 28, 82, 50, 88, 13);

SELECT * FROM alerts WHERE patient_id = 3 ORDER BY id DESC LIMIT 1;
```
Expected: a `critical` alert, "SEPTIC SHOCK: SIRS 3/4, qSOFA 3/3...". DBeaver is in auto-commit mode by default.
If you repeat this within the same session, the patient already has an ongoing episode. Either use
another patient, or first run:
`UPDATE sepsis_episodes SET outcome='recovered' WHERE patient_id=3 AND outcome='ongoing';`

**12:30, audit trigger:**
```sql
UPDATE patients SET bed_number = 'ICU-7' WHERE id = 1;
SELECT * FROM audit_logs ORDER BY id DESC LIMIT 5;
```
Expected: an `UPDATE` row whose `details` is `{"bed_number": {"old": "ICU-1", "new": "ICU-7"}}`.

**Constraint demo (optional extra):**
```sql
INSERT INTO vital_signs (patient_id, heart_rate) VALUES (1, 999);
```
Expected: `violates check constraint "vital_signs_heart_rate_check"`.

## What to expect from the simulator

| Patient | Behaviour | First alert |
|---|---|---|
| 1-4 | Stable | none |
| 5-6 | Mild deterioration from t=60 | medium (SIRS) at roughly t=70-80 |
| 7-8 | Developing sepsis from t=45-50 | medium around t=55, escalates to high (lactate > 2) around t=60 |
| 9 | Septic shock from t=30 | critical around t=33 |
| 10 | Starts septic | medium, then high, at t=0. The episode is auto-resolved after 5 minutes once it recovers |
