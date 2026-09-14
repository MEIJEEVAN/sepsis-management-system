"""Vital sign endpoints."""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError

from app.extensions import db
from app.models.vital_sign import VitalSign
from app.schemas.vital import VitalSignSchema
from app.utils.decorators import role_required

vitals_bp = Blueprint("vitals", __name__, url_prefix="/api/vitals")
vital_schema = VitalSignSchema()
vitals_schema = VitalSignSchema(many=True)


@vitals_bp.post("")
@jwt_required()
@role_required(["admin", "clinician", "nurse"])
def create_vital():
    """Record a new vital sign entry."""
    try:
        data = vital_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    vital = VitalSign(**data)
    db.session.add(vital)
    db.session.commit()
    return jsonify(vital_schema.dump(vital)), 201


@vitals_bp.get("/patient/<int:patient_id>")
@jwt_required()
def get_patient_vitals(patient_id):
    """Get all vitals for a patient."""
    vitals = (
        VitalSign.query.filter_by(patient_id=patient_id)
        .order_by(VitalSign.recorded_at.desc())
        .all()
    )
    return jsonify(vitals_schema.dump(vitals)), 200
