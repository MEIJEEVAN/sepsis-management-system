"""Vital signs model."""

from ..extensions import db
from .base import DictMixin


class VitalSign(DictMixin, db.Model):
    """One set of vital signs for a patient."""

    __tablename__ = "vital_signs"
    id = db.Column(db.BigInteger, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)
    recorded_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    temperature = db.Column(db.Numeric(4, 1))
    heart_rate = db.Column(db.Integer)
    respiratory_rate = db.Column(db.Integer)
    systolic_bp = db.Column(db.Integer)
    diastolic_bp = db.Column(db.Integer)
    spo2 = db.Column(db.Numeric(4, 1))
    gcs = db.Column(db.Integer)
