"""Patient management endpoints."""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError

from app.extensions import db
from app.models.patient import Patient
from app.schemas.patient import PatientSchema, PatientUpdateSchema
from app.utils.decorators import role_required

patients_bp = Blueprint("patients", __name__, url_prefix="/api/patients")
patient_schema = PatientSchema()
patients_schema = PatientSchema(many=True)


@patients_bp.get("")
@jwt_required()
def get_patients():
    """Return list of all patients."""
    patients = Patient.query.order_by(Patient.admission_date.desc()).all()
    return jsonify(patients_schema.dump(patients)), 200


@patients_bp.post("")
@jwt_required()
@role_required(["admin", "clinician"])
def create_patient():
    """Create a new patient."""
    try:
        data = patient_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    patient = Patient(**data)
    db.session.add(patient)
    db.session.commit()
    return jsonify(patient_schema.dump(patient)), 201


@patients_bp.get("/<int:patient_id>")
@jwt_required()
def get_patient(patient_id):
    """Return a single patient by ID."""
    patient = db.session.get(Patient, patient_id)
    if patient is None:
        return jsonify({"message": "Patient not found"}), 404
    return jsonify(patient_schema.dump(patient)), 200


@patients_bp.put("/<int:patient_id>")
@jwt_required()
@role_required(["admin", "clinician"])
def update_patient(patient_id):
    """Update patient details."""
    patient = db.session.get(Patient, patient_id)
    if patient is None:
        return jsonify({"message": "Patient not found"}), 404

    try:
        data = PatientUpdateSchema().load(request.get_json(), partial=True)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    for key, value in data.items():
        setattr(patient, key, value)
    db.session.commit()
    return jsonify(patient_schema.dump(patient)), 200
