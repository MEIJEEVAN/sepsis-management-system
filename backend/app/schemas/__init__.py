"""Marshmallow schemas for request validation.

Range checks are intentionally left to the database CHECK constraints so that
invalid readings are rejected (and demonstrated) by PostgreSQL itself.
"""

from marshmallow import Schema, fields, validate


class RegisterSchema(Schema):
    """User registration payload."""

    username = fields.Str(required=True, validate=validate.Length(min=3, max=80))
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True, validate=validate.Length(min=6))
    full_name = fields.Str(load_default=None)
    role = fields.Str(load_default="clinician", validate=validate.OneOf(["clinician", "nurse"]))


class LoginSchema(Schema):
    """Login payload."""

    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True)


class PatientSchema(Schema):
    """Patient create/update payload."""

    mrn = fields.Str(required=True, validate=validate.Length(max=50))
    first_name = fields.Str(required=True)
    last_name = fields.Str(required=True)
    dob = fields.Date(allow_none=True)
    gender = fields.Str(
        allow_none=True, validate=validate.OneOf(["Male", "Female", "Other", "Unknown"])
    )
    bed_number = fields.Str(allow_none=True)
    admission_date = fields.DateTime()
    status = fields.Str(validate=validate.OneOf(["active", "discharged", "transferred"]))


class VitalSchema(Schema):
    """Vital signs payload."""

    patient_id = fields.Int(required=True)
    recorded_at = fields.DateTime()
    temperature = fields.Float(allow_none=True)
    heart_rate = fields.Int(allow_none=True)
    respiratory_rate = fields.Int(allow_none=True)
    systolic_bp = fields.Int(allow_none=True)
    diastolic_bp = fields.Int(allow_none=True)
    spo2 = fields.Float(allow_none=True)
    gcs = fields.Int(allow_none=True)


class LabSchema(Schema):
    """Lab results payload."""

    patient_id = fields.Int(required=True)
    recorded_at = fields.DateTime()
    wbc = fields.Float(allow_none=True)
    lactate = fields.Float(allow_none=True)
    crp = fields.Float(allow_none=True)
    procalcitonin = fields.Float(allow_none=True)
    creatinine = fields.Float(allow_none=True)
    bilirubin = fields.Float(allow_none=True)
    platelets = fields.Int(allow_none=True)
    inr = fields.Float(allow_none=True)


class ProtocolSchema(Schema):
    """Protocol payload."""

    title = fields.Str(required=True, validate=validate.Length(max=120))
    description = fields.Str(allow_none=True)
    criteria = fields.Str(allow_none=True)
    active = fields.Bool(load_default=True)
