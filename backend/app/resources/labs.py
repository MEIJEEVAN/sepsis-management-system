"""Lab result endpoints."""

from typing import Any

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from ..extensions import db
from ..models import LabResult, Patient
from ..schemas import LabSchema
from ..utils.decorators import role_required

bp = Blueprint("labs", __name__, url_prefix="/api/labs")


@bp.post("")
@role_required(["admin", "clinician", "nurse"])
def add_labs() -> Any:
    """Record labs; the database trigger assesses sepsis on INSERT."""
    data = LabSchema().load(request.get_json(silent=True) or {})
    db.get_or_404(Patient, data["patient_id"])
    row = LabResult(**data)
    db.session.add(row)
    db.session.commit()
    return jsonify(row.to_dict()), 201


@bp.get("/patient/<int:patient_id>")
@jwt_required()
def patient_labs(patient_id: int) -> Any:
    """Return the newest labs for a patient."""
    limit = min(request.args.get("limit", 50, type=int), 500)
    stmt = (
        db.select(LabResult)
        .filter_by(patient_id=patient_id)
        .order_by(LabResult.recorded_at.desc())
        .limit(limit)
    )
    return jsonify([r.to_dict() for r in db.session.scalars(stmt)])
