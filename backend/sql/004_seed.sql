INSERT INTO protocols (title, description, criteria) VALUES
 ('Surviving Sepsis Hour-1 Bundle',
  'Measure lactate, take blood cultures, give broad-spectrum antibiotics, 30 mL/kg crystalloid for hypotension or lactate >= 4, vasopressors if needed.',
  'Suspected sepsis: SIRS >= 2 with suspected infection, or qSOFA >= 2.'),
 ('Lactate Clearance Protocol',
  'Re-measure lactate within 2-4 hours when initial lactate > 2 mmol/L; target at least 10% clearance.',
  'Initial lactate > 2 mmol/L.'),
 ('Antibiotic Escalation',
  'Escalate to broader coverage if no clinical improvement at 48-72 hours or cultures indicate resistance.',
  'Persisting septic stage after 48 hours of antibiotics.');
-- The admin user is created by backend/seed_admin.py so the password hash is never hardcoded.
