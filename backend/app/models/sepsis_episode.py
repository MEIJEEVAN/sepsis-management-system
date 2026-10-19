"""Sepsis episode model (written by the database, read by the API)."""

from ..extensions import db
from .base import DictMixin


class SepsisEpisode(DictMixin, db.Model):
    """A detected sepsis episode."""

    __tablename__ = "sepsis_episodes"
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)
    detected_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    sirs_score = db.Column(db.Integer)
    qsofa_score = db.Column(db.Integer)
    stage = db.Column(db.String(20))
    confidence_score = db.Column(db.Numeric(4, 2))
    outcome = db.Column(db.String(20), server_default="ongoing")
    notes = db.Column(db.Text)
