"""Vital sign endpoints."""

from typing import Any

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from ..extensions import db
from ..models import Patient, VitalSign
from ..schemas import VitalSchema
from ..utils.decorators import role_required

bp = Blueprint("vitals", __name__, url_prefix="/api/vitals")


@bp.post("")
@role_required(["admin", "clinician", "nurse"])
def add_vitals() -> Any:
    """Record vitals; the database trigger assesses sepsis on INSERT."""
    data = VitalSchema().load(request.get_json(silent=True) or {})
    db.get_or_404(Patient, data["patient_id"])
    row = VitalSign(**data)
    db.session.add(row)
    db.session.commit()
    return jsonify(row.to_dict()), 201


@bp.get("/patient/<int:patient_id>")
@jwt_required()
def patient_vitals(patient_id: int) -> Any:
    """Return the newest vitals for a patient."""
    limit = min(request.args.get("limit", 50, type=int), 500)
    stmt = (
        db.select(VitalSign)
        .filter_by(patient_id=patient_id)
        .order_by(VitalSign.recorded_at.desc())
        .limit(limit)
    )
    return jsonify([r.to_dict() for r in db.session.scalars(stmt)])
