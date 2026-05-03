"""
AquaSentinel AI Alert Engine
Generates alerts from AI detections based on configurable thresholds.
"""
import uuid
from sqlalchemy.orm import Session
from sqlalchemy import func
from .. import models, models_ai


# Alert threshold configuration
ALERT_THRESHOLDS = {
    "auto_critical": {
        "min_confidence": 0.85,
        "severity": ["Critical"],
        "alert_severity": "Critical"
    },
    "auto_high": {
        "min_confidence": 0.80,
        "severity": ["High"],
        "alert_severity": "High"
    },
    "cluster": {
        "min_detections": 3,
        "radius_km": 5,
        "alert_severity": "High"
    },
    "ecosystem_degradation": {
        "min_health_index_drop": 40,
        "alert_severity": "High"
    }
}


def evaluate_and_create_alerts(
    db: Session,
    detections: list,
    user_id: uuid.UUID = None,
    is_simulated: bool = False
) -> int:
    """
    Evaluate detections against alert thresholds and create alerts.
    Returns count of alerts created.
    """
    alerts_created = 0

    for detection in detections:
        alert = None

        # Rule 1: Critical severity + high confidence
        if (detection.confidence_score >= ALERT_THRESHOLDS["auto_critical"]["min_confidence"]
                and detection.severity in ALERT_THRESHOLDS["auto_critical"]["severity"]):
            alert = _create_detection_alert(
                db, detection,
                alert_severity="Critical",
                is_simulated=is_simulated,
                reason="High-confidence critical debris detection"
            )

        # Rule 2: High severity + good confidence
        elif (detection.confidence_score >= ALERT_THRESHOLDS["auto_high"]["min_confidence"]
              and detection.severity in ALERT_THRESHOLDS["auto_high"]["severity"]):
            alert = _create_detection_alert(
                db, detection,
                alert_severity="High",
                is_simulated=is_simulated,
                reason="High-confidence marine debris detection"
            )

        if alert:
            # Link detection to alert
            link = models_ai.DetectionAlertLink(
                detection_id=detection.id,
                alert_id=alert.id
            )
            db.add(link)

            # Update detection with alert reference
            detection.related_alert_id = alert.id
            alerts_created += 1

    db.commit()
    return alerts_created


def _create_detection_alert(
    db: Session,
    detection,
    alert_severity: str,
    is_simulated: bool,
    reason: str
) -> models.Alert:
    """Create a DB-backed alert from an AI detection."""
    class_label = detection.debris_class.upper().replace("_", " ")
    sim_prefix = "[SIMULATED] " if is_simulated else ""

    alert = models.Alert(
        title=f"⚠️ {sim_prefix}AI Detection: {class_label} Zone",
        message=(
            f"AI debris intelligence identified a {class_label} zone with "
            f"{detection.confidence_score:.0%} confidence near "
            f"[{detection.latitude:.4f}, {detection.longitude:.4f}]. "
            f"Severity: {detection.severity}. "
            f"Source: {detection.source_type.replace('_', ' ').title()}. "
            f"Reason: {reason}. Action recommended."
        ),
        severity=alert_severity,
        latitude=detection.latitude,
        longitude=detection.longitude,
        status="active",
        target_scope="global",
        verified_by_admin=is_simulated,
        is_simulated=is_simulated
    )
    db.add(alert)
    db.flush()
    return alert


def check_cluster_alert(
    db: Session,
    latitude: float,
    longitude: float,
    radius_km: float = 5.0,
    is_simulated: bool = False
) -> int:
    """Check if detection cluster threshold is met and create cluster alert."""
    # Approximate degree conversion: 1 degree ≈ 111 km
    radius_deg = radius_km / 111.0

    nearby_count = db.query(func.count(models_ai.AIDebrisDetection.id)).filter(
        models_ai.AIDebrisDetection.latitude.between(latitude - radius_deg, latitude + radius_deg),
        models_ai.AIDebrisDetection.longitude.between(longitude - radius_deg, longitude + radius_deg)
    ).scalar()

    if nearby_count >= ALERT_THRESHOLDS["cluster"]["min_detections"]:
        # Check if cluster alert already exists nearby
        existing = db.query(models.Alert).filter(
            models.Alert.latitude.between(latitude - radius_deg, latitude + radius_deg),
            models.Alert.longitude.between(longitude - radius_deg, longitude + radius_deg),
            models.Alert.title.like("%Debris Cluster%"),
            models.Alert.status == "active"
        ).first()

        if not existing:
            sim_prefix = "[SIMULATED] " if is_simulated else ""
            alert = models.Alert(
                title=f"🔴 {sim_prefix}Marine Debris Cluster Detected",
                message=(
                    f"AI intelligence identified a cluster of {nearby_count} debris detections "
                    f"within {radius_km}km radius near [{latitude:.4f}, {longitude:.4f}]. "
                    f"Multi-source debris accumulation zone. Elevated response priority recommended."
                ),
                severity="High",
                latitude=latitude,
                longitude=longitude,
                status="active",
                target_scope="global",
                is_simulated=is_simulated
            )
            db.add(alert)
            db.commit()
            return 1
    return 0
