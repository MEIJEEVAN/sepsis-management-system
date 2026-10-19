"""Patient model."""

from ..extensions import db
from .base import DictMixin


class Patient(DictMixin, db.Model):
    """ICU patient."""

    __tablename__ = "patients"
    id = db.Column(db.Integer, primary_key=True)
    mrn = db.Column(db.String(50), nullable=False, unique=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    dob = db.Column(db.Date)
    gender = db.Column(db.String(20))
    admission_date = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    bed_number = db.Column(db.String(20))
    status = db.Column(db.String(20), nullable=False, server_default="active")
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
