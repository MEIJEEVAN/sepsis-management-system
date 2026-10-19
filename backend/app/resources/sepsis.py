"""Manual sepsis assessment endpoint."""

from typing import Any

from flask import Blueprint, jsonify
from sqlalchemy import text

from ..extensions import db
from ..models import Patient
from ..utils.decorators import role_required

bp = Blueprint("sepsis", __name__, url_prefix="/api/sepsis")


@bp.post("/assess/<int:patient_id>")
@role_required(["admin", "clinician"])
def assess(patient_id: int) -> Any:
    """Call ``assess_sepsis()`` directly and return its row (works without triggers)."""
    db.get_or_404(Patient, patient_id)
    row = (
        db.session.execute(text("SELECT * FROM assess_sepsis(:id)"), {"id": patient_id})
        .mappings()
        .one()
    )
    result = dict(row)
    result["alert_id"] = None
    if result["sepsis_detected"] and (result["new_episode"] or result["escalated"]):
        result["alert_id"] = db.session.execute(
            text("SELECT raise_sepsis_alert(:p, :e, :m, :s, :st)"),
            {
                "p": patient_id,
                "e": result["episode_id"],
                "m": result["message"],
                "s": result["severity"],
                "st": result["stage"],
            },
        ).scalar_one()
    db.session.commit()
    return jsonify(result)
