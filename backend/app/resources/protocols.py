"""Protocol endpoints."""

from typing import Any

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from ..extensions import db
from ..models import Protocol
from ..schemas import ProtocolSchema
from ..utils.decorators import role_required

bp = Blueprint("protocols", __name__, url_prefix="/api/protocols")


@bp.get("")
@jwt_required()
def list_protocols() -> Any:
    """List protocols."""
    rows = db.session.scalars(db.select(Protocol).order_by(Protocol.id))
    return jsonify([p.to_dict() for p in rows])


@bp.post("")
@role_required(["admin"])
def create_protocol() -> Any:
    """Create a protocol (admin only)."""
    protocol = Protocol(**ProtocolSchema().load(request.get_json(silent=True) or {}))
    db.session.add(protocol)
    db.session.commit()
    return jsonify(protocol.to_dict()), 201
