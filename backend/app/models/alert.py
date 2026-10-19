"""Alert model."""

from ..extensions import db
from .base import DictMixin


class Alert(DictMixin, db.Model):
    """Clinical alert raised by the database triggers."""

    __tablename__ = "alerts"
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)
    episode_id = db.Column(db.Integer, db.ForeignKey("sepsis_episodes.id"))
    message = db.Column(db.String(255), nullable=False)
    severity = db.Column(db.String(20), nullable=False, server_default="medium")
    acknowledged = db.Column(db.Boolean, nullable=False, server_default=db.false())
    acknowledged_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    acknowledged_at = db.Column(db.DateTime(timezone=True))
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
