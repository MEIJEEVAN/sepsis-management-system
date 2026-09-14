"""Lab result model."""

from datetime import datetime

from app.extensions import db


class LabResult(db.Model):
    """Laboratory test results relevant to sepsis."""

    __tablename__ = "lab_results"

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(
        db.Integer, db.ForeignKey("patients.id"), nullable=False, index=True
    )
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    wbc = db.Column(db.Numeric(6, 1))  # x10^9/L
    lactate = db.Column(db.Numeric(5, 2))  # mmol/L
    crp = db.Column(db.Numeric(8, 2))  # mg/L
    procalcitonin = db.Column(db.Numeric(8, 2))  # ng/mL
    creatinine = db.Column(db.Numeric(6, 2))  # mg/dL
    bilirubin = db.Column(db.Numeric(6, 2))  # mg/dL
    platelets = db.Column(db.Integer)  # x10^9/L
    inr = db.Column(db.Numeric(4, 2))
    notes = db.Column(db.Text)

    patient = db.relationship("Patient", back_populates="labs")
