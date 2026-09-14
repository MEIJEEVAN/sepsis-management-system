"""Vital sign schemas."""

from marshmallow import Schema, fields


class VitalSignSchema(Schema):
    """Schema for vital signs."""

    id = fields.Int(dump_only=True)
    patient_id = fields.Int(required=True)
    recorded_at = fields.DateTime(required=False)
    temperature = fields.Decimal(required=False, allow_none=True, places=1)
    heart_rate = fields.Int(required=False, allow_none=True)
    respiratory_rate = fields.Int(required=False, allow_none=True)
    systolic_bp = fields.Int(required=False, allow_none=True)
    diastolic_bp = fields.Int(required=False, allow_none=True)
    spo2 = fields.Decimal(required=False, allow_none=True, places=1)
    gcs = fields.Int(required=False, allow_none=True, validate=lambda n: 3 <= n <= 15)
    notes = fields.Str(required=False, allow_none=True)
