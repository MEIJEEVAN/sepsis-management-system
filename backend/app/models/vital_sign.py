"""Vital sign model."""

from datetime import datetime

from app.extensions import db


class VitalSign(db.Model):
    """Patient vital signs at a point in time."""

    __tablename__ = "vital_signs"

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(
        db.Integer, db.ForeignKey("patients.id"), nullable=False, index=True
    )
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    temperature = db.Column(db.Numeric(4, 1))  # °C
    heart_rate = db.Column(db.Integer)  # bpm
    respiratory_rate = db.Column(db.Integer)  # breaths/min
    systolic_bp = db.Column(db.Integer)  # mmHg
    diastolic_bp = db.Column(db.Integer)  # mmHg
    spo2 = db.Column(db.Numeric(4, 1))  # %
    gcs = db.Column(db.Integer)  # 3-15
    notes = db.Column(db.Text)

    patient = db.relationship("Patient", back_populates="vitals")
