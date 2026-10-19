"""User model."""

from typing import Any

from ..extensions import db
from .base import DictMixin


class User(DictMixin, db.Model):
    """Application user."""

    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(120))
    role = db.Column(db.String(20), nullable=False, server_default="clinician")
    is_active = db.Column(db.Boolean, nullable=False, server_default=db.true())
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())

    def to_dict(self) -> dict[str, Any]:
        """Return the user without the password hash."""
        data = super().to_dict()
        data.pop("password_hash", None)
        return data
