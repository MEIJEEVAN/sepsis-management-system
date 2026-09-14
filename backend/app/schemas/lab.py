"""Lab result schemas."""

from marshmallow import Schema, fields


class LabResultSchema(Schema):
    """Schema for lab results."""

    id = fields.Int(dump_only=True)
    patient_id = fields.Int(required=True)
    recorded_at = fields.DateTime(required=False)
    wbc = fields.Decimal(required=False, allow_none=True, places=1)
    lactate = fields.Decimal(required=False, allow_none=True, places=2)
    crp = fields.Decimal(required=False, allow_none=True, places=2)
    procalcitonin = fields.Decimal(required=False, allow_none=True, places=2)
    creatinine = fields.Decimal(required=False, allow_none=True, places=2)
    bilirubin = fields.Decimal(required=False, allow_none=True, places=2)
    platelets = fields.Int(required=False, allow_none=True)
    inr = fields.Decimal(required=False, allow_none=True, places=2)
    notes = fields.Str(required=False, allow_none=True)
