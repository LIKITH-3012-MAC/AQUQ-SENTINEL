from typing import Dict, Any, List
from sqlalchemy.orm import Session
from .. import models

def calculate_marine_risk(
    db: Session,
    latitude: float,
    longitude: float,
    debris_density: float = 0.0,
    chl_anomaly: float = 0.0,
    sst_anomaly: float = 0.0,
    wave_height: float = 0.0,
    wind_speed: float = 0.0,
    current_speed: float = 0.0,
    proximity_sensitive_km: float = 100.0,
    report_severity_score: float = 0.0
) -> models.RiskScore:
    """
    Advanced Rule-Based Marine Risk Scoring System.
    Returns a RiskScore model instance.
    """
    score = 0.0
    factors = {}

    # 1. Debris Impact (Weight: 30%)
    debris_contribution = min(debris_density, 100.0) * 0.3
    score += debris_contribution
    factors["debris"] = round(debris_contribution, 2)

    # 2. Biological/Thermal Stress (Weight: 20%)
    # Anomalies > 2.0 are considered high stress
    bio_stress = (min(abs(chl_anomaly), 5.0) / 5.0 * 50) + (min(abs(sst_anomaly), 5.0) / 5.0 * 50)
    bio_contribution = (bio_stress / 100.0) * 20
    score += bio_contribution
    factors["bio_thermal"] = round(bio_contribution, 2)

    # 3. Dynamic Conditions (Wave/Wind/Current) (Weight: 20%)
    # Safe thresholds: Wave < 3m, Wind < 15m/s, Current < 1.0m/s
    dynamic_stress = (min(wave_height, 10.0) / 10.0 * 33) + \
                     (min(wind_speed, 30.0) / 30.0 * 33) + \
                     (min(current_speed, 3.0) / 3.0 * 34)
    dynamic_contribution = (dynamic_stress / 100.0) * 20
    score += dynamic_contribution
    factors["dynamic_conditions"] = round(dynamic_contribution, 2)

    # 4. Proximity & Sensitive Zone Stress (Weight: 20%)
    # High risk if < 5km
    proximity_stress = max(0, (20.0 - proximity_sensitive_km) / 20.0 * 100) if proximity_sensitive_km < 20.0 else 0
    proximity_contribution = (proximity_stress / 100.0) * 20
    score += proximity_contribution
    factors["proximity"] = round(proximity_contribution, 2)

    # 5. Community Reports (Weight: 10%)
    report_contribution = min(report_severity_score, 100.0) * 0.1
    score += report_contribution
    factors["community_reports"] = round(report_contribution, 2)

    # Normalize final score
    final_score = round(min(100.0, score), 2)

    # Determine Level & Action
    if final_score >= 76:
        level = "CRITICAL"
        action = "Immediate deployment of cleanup vessels and containment booms. Notify local maritime authorities."
        explanation = "Extremely high concentrations of debris coupled with biological stress and adverse weather detected."
    elif final_score >= 51:
        level = "HIGH"
        action = "Schedule cleanup operation within 48 hours. Increase satellite monitoring frequency."
        explanation = "Significant environmental stress detected. Conditions favorable for rapid debris accumulation."
    elif final_score >= 26:
        level = "MEDIUM"
        action = "Continue monitoring. Advise local marine traffic to report sightings."
        explanation = "Moderate ecosystem pressure detected. No immediate intervention required."
    else:
        level = "LOW"
        action = "Routine monitoring. Ecosystem parameters within nominal range."
        explanation = "Ocean health indicators show stable conditions."

    risk_entry = models.RiskScore(
        latitude=latitude,
        longitude=longitude,
        score=final_score,
        level=level,
        explanation=explanation,
        recommended_action=action,
        factors=factors
    )

    db.add(risk_entry)
    db.commit()
    db.refresh(risk_entry)

    # Generate Alert if High/Critical
    if final_score > 50:
        alert = models.Alert(
            title=f"Marine Risk Alert: {level}",
            message=explanation,
            severity=level,
            latitude=latitude,
            longitude=longitude
        )
        db.add(alert)
        db.commit()

    return risk_entry
