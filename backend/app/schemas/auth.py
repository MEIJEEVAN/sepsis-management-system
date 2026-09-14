"""Authentication schemas."""

from marshmallow import Schema, fields, validate


class RegisterSchema(Schema):
    """Schema for user registration."""

    username = fields.Str(required=True, validate=validate.Length(min=3, max=80))
    email = fields.Email(required=True)
    password = fields.Str(
        required=True, load_only=True, validate=validate.Length(min=6)
    )
    full_name = fields.Str(required=False, allow_none=True)
    role = fields.Str(
        required=False,
        validate=validate.OneOf(["admin", "clinician", "nurse"]),
        load_default="clinician",
    )


class LoginSchema(Schema):
    """Schema for user login."""

    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True)
