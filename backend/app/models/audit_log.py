"""Audit log model."""

from sqlalchemy.dialects.postgresql import JSONB

from ..extensions import db
from .base import DictMixin


class AuditLog(DictMixin, db.Model):
    """An audit trail entry."""

    __tablename__ = "audit_logs"
    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    action = db.Column(db.String(50), nullable=False)
    entity = db.Column(db.String(50), nullable=False)
    entity_id = db.Column(db.Integer)
    details = db.Column(JSONB)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
