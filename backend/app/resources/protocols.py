"""Protocol endpoints."""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from marshmallow import Schema, fields, ValidationError

from app.extensions import db
from app.models.protocol import Protocol
from app.utils.decorators import role_required

protocols_bp = Blueprint("protocols", __name__, url_prefix="/api/protocols")


class ProtocolSchema(Schema):
    """Schema for sepsis protocols."""

    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    description = fields.Str(required=False)
    criteria = fields.Str(required=False)
    active = fields.Bool(required=False)


protocol_schema = ProtocolSchema()
protocols_schema = ProtocolSchema(many=True)


@protocols_bp.get("")
@jwt_required()
def get_protocols():
    """Return all active protocols."""
    protocols = Protocol.query.filter_by(active=True).all()
    return jsonify(protocols_schema.dump(protocols)), 200


@protocols_bp.post("")
@jwt_required()
@role_required(["admin"])
def create_protocol():
    """Create a new protocol."""
    try:
        data = protocol_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    protocol = Protocol(**data)
    db.session.add(protocol)
    db.session.commit()
    return jsonify(protocol_schema.dump(protocol)), 201
