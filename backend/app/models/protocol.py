"""Protocol model."""

from datetime import datetime

from app.extensions import db


class Protocol(db.Model):
    """Sepsis treatment protocol."""

    __tablename__ = "protocols"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    criteria = db.Column(db.Text)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
