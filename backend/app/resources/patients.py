"""Patient endpoints."""

from typing import Any

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy import text

from ..extensions import db
from ..models import Alert, LabResult, Patient, SepsisEpisode, VitalSign
from ..schemas import PatientSchema
from ..utils.decorators import role_required

bp = Blueprint("patients", __name__, url_prefix="/api/patients")

_LIST_SQL = text(
    """
    SELECT p.*, s.temperature, s.heart_rate, s.systolic_bp, s.diastolic_bp, s.spo2,
           s.lactate, s.episode_stage, s.episode_outcome
    FROM patients p
    LEFT JOIN v_patient_current_status s ON s.patient_id = p.id
    ORDER BY p.id
    """
)


def _set_audit_user() -> None:
    """Expose the acting user to the audit trigger for this transaction."""
    db.session.execute(
        text("SELECT set_config('app.user_id', :uid, true)"), {"uid": str(get_jwt_identity())}
    )


@bp.get("")
@jwt_required()
def list_patients() -> Any:
    """List all patients with their current status."""
    return jsonify([dict(r) for r in db.session.execute(_LIST_SQL).mappings()])


@bp.post("")
@role_required(["admin", "clinician"])
def create_patient() -> Any:
    """Admit a patient."""
    data = PatientSchema().load(request.get_json(silent=True) or {})
    _set_audit_user()
    patient = Patient(**data)
    db.session.add(patient)
    db.session.commit()
    return jsonify(patient.to_dict()), 201


@bp.get("/<int:patient_id>")
@jwt_required()
def get_patient(patient_id: int) -> Any:
    """Return one patient."""
    return jsonify(db.get_or_404(Patient, patient_id).to_dict())


@bp.put("/<int:patient_id>")
@role_required(["admin", "clinician"])
def update_patient(patient_id: int) -> Any:
    """Update a patient (partial updates allowed)."""
    patient = db.get_or_404(Patient, patient_id)
    data = PatientSchema(partial=True).load(request.get_json(silent=True) or {})
    _set_audit_user()
    for key, value in data.items():
        setattr(patient, key, value)
    db.session.commit()
    return jsonify(patient.to_dict())


@bp.get("/<int:patient_id>/summary")
@jwt_required()
def patient_summary(patient_id: int) -> Any:
    """Return current status, recent vitals/labs, episodes and alerts."""
    patient = db.get_or_404(Patient, patient_id)
    current = (
        db.session.execute(
            text("SELECT * FROM v_patient_current_status WHERE patient_id = :id"),
            {"id": patient_id},
        )
        .mappings()
        .first()
    )

    def recent(model: Any, order_col: Any, limit: int) -> list[dict[str, Any]]:
        stmt = db.select(model).filter_by(patient_id=patient_id).order_by(order_col.desc())
        return [r.to_dict() for r in db.session.scalars(stmt.limit(limit))]

    return jsonify(
        patient=patient.to_dict(),
        current=dict(current) if current else None,
        vitals=recent(VitalSign, VitalSign.recorded_at, 20),
        labs=recent(LabResult, LabResult.recorded_at, 10),
        episodes=recent(SepsisEpisode, SepsisEpisode.detected_at, 20),
        alerts=recent(Alert, Alert.created_at, 5),
    )
