"""Sepsis detection logic based on SIRS and qSOFA."""

from datetime import datetime

from app.extensions import db
from app.models.vital_sign import VitalSign
from app.models.lab_result import LabResult
from app.models.sepsis_episode import SepsisEpisode
from app.models.alert import Alert


def calculate_sirs(vitals, labs) -> int:
    """Calculate SIRS criteria score (0-4)."""
    score = 0
    if vitals and (vitals.temperature > 38 or vitals.temperature < 36):
        score += 1
    if vitals and vitals.heart_rate and vitals.heart_rate > 90:
        score += 1
    if (
        vitals
        and vitals.respiratory_rate
        and (vitals.respiratory_rate > 20 or (vitals.spo2 and vitals.spo2 < 90))
    ):
        score += 1
    if labs and labs.wbc and (labs.wbc > 12 or labs.wbc < 4):
        score += 1
    return score


def calculate_qsofa(vitals) -> int:
    """Calculate quick SOFA score (0-3)."""
    score = 0
    if vitals and vitals.respiratory_rate and vitals.respiratory_rate >= 22:
        score += 1
    if vitals and vitals.systolic_bp and vitals.systolic_bp <= 100:
        score += 1
    if vitals and vitals.gcs is not None and vitals.gcs < 15:
        score += 1
    return score


def assess_patient(patient_id: int) -> dict:
    """Assess a patient for sepsis risk and create episode/alert if positive."""
    vitals = (
        VitalSign.query.filter_by(patient_id=patient_id)
        .order_by(VitalSign.recorded_at.desc())
        .first()
    )
    labs = (
        LabResult.query.filter_by(patient_id=patient_id)
        .order_by(LabResult.recorded_at.desc())
        .first()
    )

    sirs_score = calculate_sirs(vitals, labs)
    qsofa_score = calculate_qsofa(vitals)

    sepsis_detected = False
    stage = None

    if sirs_score >= 2:
        sepsis_detected = True
        stage = "sirs"
        if labs and labs.lactate and float(labs.lactate) > 2.0:
            stage = "sepsis"
        if vitals and vitals.systolic_bp and vitals.systolic_bp < 90:
            stage = "septic_shock"
        elif labs and labs.lactate and float(labs.lactate) >= 4.0:
            stage = "septic_shock"

    if sepsis_detected:
        episode = SepsisEpisode(
            patient_id=patient_id,
            detected_at=datetime.utcnow(),
            confidence_score=min(0.5 + (sirs_score * 0.1) + (qsofa_score * 0.1), 0.99),
            stage=stage,
            notes=f"SIRS={sirs_score}, qSOFA={qsofa_score}",
        )
        db.session.add(episode)
        db.session.flush()

        alert = Alert(
            patient_id=patient_id,
            episode_id=episode.id,
            message=f"Possible {stage.replace('_', ' ').title()} detected "
            f"(SIRS={sirs_score}, qSOFA={qsofa_score})",
            severity="high" if stage in ("severe_sepsis", "septic_shock") else "medium",
        )
        db.session.add(alert)
        db.session.commit()

    return {
        "patient_id": patient_id,
        "sirs_score": sirs_score,
        "qsofa_score": qsofa_score,
        "sepsis_detected": sepsis_detected,
        "stage": stage,
        "timestamp": datetime.utcnow().isoformat(),
    }
