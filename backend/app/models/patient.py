"""Patient model."""

from datetime import datetime

from app.extensions import db


class Patient(db.Model):
    """Patient demographic and admission data."""

    __tablename__ = "patients"

    id = db.Column(db.Integer, primary_key=True)
    mrn = db.Column(db.String(50), unique=True, nullable=False, index=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    dob = db.Column(db.Date)
    gender = db.Column(db.String(20))
    admission_date = db.Column(db.DateTime, default=datetime.utcnow)
    bed_number = db.Column(db.String(20))
    status = db.Column(
        db.String(20), default="active"
    )  # active, discharged, transferred
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    vitals = db.relationship("VitalSign", back_populates="patient", lazy="dynamic")
    labs = db.relationship("LabResult", back_populates="patient", lazy="dynamic")
    episodes = db.relationship(
        "SepsisEpisode", back_populates="patient", lazy="dynamic"
    )
    alerts = db.relationship("Alert", back_populates="patient", lazy="dynamic")
