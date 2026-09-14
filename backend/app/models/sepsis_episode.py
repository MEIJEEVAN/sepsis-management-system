"""Sepsis episode model."""

from datetime import datetime

from app.extensions import db


class SepsisEpisode(db.Model):
    """A detected sepsis episode."""

    __tablename__ = "sepsis_episodes"

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(
        db.Integer, db.ForeignKey("patients.id"), nullable=False, index=True
    )
    detected_at = db.Column(db.DateTime, default=datetime.utcnow)
    confidence_score = db.Column(db.Numeric(4, 2))
    stage = db.Column(db.String(50))  # sirs, sepsis, severe_sepsis, septic_shock
    outcome = db.Column(db.String(50))  # recovered, died, ongoing
    notes = db.Column(db.Text)

    patient = db.relationship("Patient", back_populates="episodes")
    alerts = db.relationship("Alert", back_populates="episode")
