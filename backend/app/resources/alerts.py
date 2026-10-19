"""Alert endpoints."""

from typing import Any

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity
from sqlalchemy import text

from ..extensions import db
from ..models import Alert, AuditLog
from ..utils.decorators import role_required

bp = Blueprint("alerts", __name__, url_prefix="/api/alerts")

_ALL_ROLES = ["admin", "clinician", "nurse"]
_BASE = (
    "SELECT a.id AS alert_id, a.patient_id, p.mrn, p.first_name, p.last_name, a.message,"
    " a.severity, a.acknowledged, a.created_at, a.episode_id, e.stage AS episode_stage"
    " FROM alerts a JOIN patients p ON p.id = a.patient_id"
    " LEFT JOIN sepsis_episodes e ON e.id = a.episode_id"
)


@bp.get("")
@role_required(_ALL_ROLES)
def list_alerts() -> Any:
    """List alerts; ``?acknowledged=false`` reads from ``v_active_alerts``."""
    flag = request.args.get("acknowledged")
    limit = min(request.args.get("limit", 50, type=int), 500)
    if flag == "false":
        sql = "SELECT * FROM v_active_alerts ORDER BY created_at DESC LIMIT :n"
    elif flag == "true":
        sql = _BASE + " WHERE a.acknowledged ORDER BY a.created_at DESC LIMIT :n"
    else:
        sql = _BASE + " ORDER BY a.created_at DESC LIMIT :n"
    rows = db.session.execute(text(sql), {"n": limit}).mappings()
    return jsonify([dict(r) for r in rows])


@bp.put("/<int:alert_id>/acknowledge")
@role_required(_ALL_ROLES)
def acknowledge(alert_id: int) -> Any:
    """Acknowledge an alert."""
    alert = db.get_or_404(Alert, alert_id)
    user_id = int(get_jwt_identity())
    alert.acknowledged = True
    alert.acknowledged_by = user_id
    alert.acknowledged_at = db.func.now()
    db.session.add(
        AuditLog(user_id=user_id, action="ACKNOWLEDGE", entity="alerts", entity_id=alert_id)
    )
    db.session.commit()
    return jsonify(alert.to_dict())
