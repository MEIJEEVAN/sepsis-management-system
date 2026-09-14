"""Alert schemas."""

from marshmallow import Schema, fields


class AlertSchema(Schema):
    """Schema for alerts."""

    id = fields.Int(dump_only=True)
    patient_id = fields.Int(required=True)
    episode_id = fields.Int(required=False, allow_none=True)
    message = fields.Str(required=True)
    severity = fields.Str(required=False, load_default="medium")
    acknowledged = fields.Bool(dump_only=True)
    acknowledged_by = fields.Int(dump_only=True)
    acknowledged_at = fields.DateTime(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
