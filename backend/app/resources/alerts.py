"""Alert endpoints."""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

from app.extensions import db
from app.models.alert import Alert
from app.schemas.alert import AlertSchema
from app.utils.decorators import role_required

alerts_bp = Blueprint("alerts", __name__, url_prefix="/api/alerts")
alert_schema = AlertSchema()
alerts_schema = AlertSchema(many=True)


@alerts_bp.get("")
@jwt_required()
def get_alerts():
    """Return all alerts, optionally filtered by acknowledged status."""
    acknowledged = request.args.get("acknowledged")
    query = Alert.query.order_by(Alert.created_at.desc())
    if acknowledged is not None:
        query = query.filter_by(acknowledged=acknowledged.lower() == "true")
    return jsonify(alerts_schema.dump(query.all())), 200


@alerts_bp.put("/<int:alert_id>/acknowledge")
@jwt_required()
@role_required(["admin", "clinician", "nurse"])
def acknowledge_alert(alert_id):
    """Mark an alert as acknowledged."""
    alert = db.session.get(Alert, alert_id)
    if alert is None:
        return jsonify({"message": "Alert not found"}), 404

    alert.acknowledged = True
    alert.acknowledged_by = int(get_jwt_identity())
    alert.acknowledged_at = datetime.utcnow()
    db.session.commit()
    return jsonify(alert_schema.dump(alert)), 200
