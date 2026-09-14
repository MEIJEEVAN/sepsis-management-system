"""Patient schemas."""

from marshmallow import Schema, fields, validate


class PatientSchema(Schema):
    """Full patient schema."""

    id = fields.Int(dump_only=True)
    mrn = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    first_name = fields.Str(required=True, validate=validate.Length(max=80))
    last_name = fields.Str(required=True, validate=validate.Length(max=80))
    dob = fields.Date(required=False, allow_none=True)
    gender = fields.Str(
        required=False,
        validate=validate.OneOf(["Male", "Female", "Other", "Unknown"]),
        allow_none=True,
    )
    admission_date = fields.DateTime(required=False, allow_none=True)
    bed_number = fields.Str(required=False, allow_none=True)
    status = fields.Str(required=False, load_default="active")
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class PatientUpdateSchema(Schema):
    """Schema for partial patient updates."""

    mrn = fields.Str(required=False, validate=validate.Length(min=1, max=50))
    first_name = fields.Str(required=False, validate=validate.Length(max=80))
    last_name = fields.Str(required=False, validate=validate.Length(max=80))
    dob = fields.Date(required=False, allow_none=True)
    gender = fields.Str(
        required=False,
        validate=validate.OneOf(["Male", "Female", "Other", "Unknown"]),
    )
    admission_date = fields.DateTime(required=False)
    bed_number = fields.Str(required=False)
    status = fields.Str(required=False)
