"""Laboratory results model."""

from ..extensions import db
from .base import DictMixin


class LabResult(DictMixin, db.Model):
    """One panel of lab results for a patient."""

    __tablename__ = "lab_results"
    id = db.Column(db.BigInteger, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)
    recorded_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    wbc = db.Column(db.Numeric(6, 1))
    lactate = db.Column(db.Numeric(5, 2))
    crp = db.Column(db.Numeric(8, 2))
    procalcitonin = db.Column(db.Numeric(8, 2))
    creatinine = db.Column(db.Numeric(6, 2))
    bilirubin = db.Column(db.Numeric(6, 2))
    platelets = db.Column(db.Integer)
    inr = db.Column(db.Numeric(4, 2))
