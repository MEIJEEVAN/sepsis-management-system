"""Sepsis assessment endpoints."""

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

from app.utils.decorators import role_required
from app.utils.sepsis_criteria import assess_patient

sepsis_bp = Blueprint("sepsis", __name__, url_prefix="/api/sepsis")


@sepsis_bp.post("/assess/<int:patient_id>")
@jwt_required()
@role_required(["admin", "clinician"])
def assess(patient_id):
    """Assess a patient for sepsis."""
    result = assess_patient(patient_id)
    return jsonify(result), 200
