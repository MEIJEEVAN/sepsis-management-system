"""Lab result endpoints."""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError

from app.extensions import db
from app.models.lab_result import LabResult
from app.schemas.lab import LabResultSchema
from app.utils.decorators import role_required

labs_bp = Blueprint("labs", __name__, url_prefix="/api/labs")
lab_schema = LabResultSchema()
labs_schema = LabResultSchema(many=True)


@labs_bp.post("")
@jwt_required()
@role_required(["admin", "clinician", "nurse"])
def create_lab():
    """Record a new lab result entry."""
    try:
        data = lab_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    lab = LabResult(**data)
    db.session.add(lab)
    db.session.commit()
    return jsonify(lab_schema.dump(lab)), 201


@labs_bp.get("/patient/<int:patient_id>")
@jwt_required()
def get_patient_labs(patient_id):
    """Get all lab results for a patient."""
    labs = (
        LabResult.query.filter_by(patient_id=patient_id)
        .order_by(LabResult.recorded_at.desc())
        .all()
    )
    return jsonify(labs_schema.dump(labs)), 200
