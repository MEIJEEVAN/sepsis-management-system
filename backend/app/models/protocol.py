"""Clinical protocol model."""

from ..extensions import db
from .base import DictMixin


class Protocol(DictMixin, db.Model):
    """A sepsis management protocol."""

    __tablename__ = "protocols"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    criteria = db.Column(db.Text)
    active = db.Column(db.Boolean, nullable=False, server_default=db.true())
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
