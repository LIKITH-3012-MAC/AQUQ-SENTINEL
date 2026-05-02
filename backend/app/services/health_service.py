from sqlalchemy.orm import Session
from .. import models
import random

def calculate_ocean_health(
    db: Session,
    latitude: float,
    longitude: float,
    debris_density: float = 0.0,
    chl_anomaly: float = 0.0,
    sst_anomaly: float = 0.0,
    wave_height: float = 0.0,
    report_severity: float = 0.0,
    region_name: str = "Target Zone"
) -> models.OceanHealthScore:
    """
    Calculates Ocean Health Score (0-100) based on multiple parameters.
    Score: 100 is Excellent, 0 is Critical.
    """
    # Inverse logic: Higher risk = Lower health
    risk_score = 0.0
    
    # Weights for Risk (Total 100%)
    # Debris: 40%, Anomaly (Temp/Chl): 30%, Dynamic (Wave): 20%, Reports: 10%
    
    risk_score += min(debris_density, 100.0) * 0.4
    risk_score += (min(abs(chl_anomaly), 5.0) / 5.0 * 50 + min(abs(sst_anomaly), 5.0) / 5.0 * 50) * 0.3
    risk_score += (min(wave_height, 10.0) / 10.0 * 100) * 0.2
    risk_score += min(report_severity, 100.0) * 0.1
    
    health_score = int(max(0, 100 - risk_score))
    
    # Categories
    if health_score >= 85:
        category = "Excellent"
        explanation = "Pristine marine conditions. Ecosystem parameters are optimal."
        action = "Maintain current conservation efforts. Periodic monitoring only."
    elif health_score >= 65:
        category = "Stable"
        explanation = "Healthy ecosystem with minor anomalies. Low debris density."
        action = "Routine monitoring and community awareness programs."
    elif health_score >= 45:
        category = "Watchlist"
        explanation = "Increasing levels of debris or thermal stress detected."
        action = "Increase satellite surveillance frequency and verify ground reports."
    elif health_score >= 25:
        category = "At Risk"
        explanation = "Significant environmental degradation. Immediate attention required."
        action = "Deploy rapid response teams for debris assessment and cleanup."
    else:
        category = "Critical"
        explanation = "Severe ecological stress. High debris concentration and severe anomalies."
        action = "Emergency cleanup operations and maritime restriction zones recommended."

    contributing_factors = {
        "debris_density": round(debris_density, 2),
        "thermal_stress": round(abs(sst_anomaly), 2),
        "chlorophyll_anomaly": round(chl_anomaly, 2),
        "wave_impact": round(wave_height, 2)
    }

    health_entry = models.OceanHealthScore(
        latitude=latitude,
        longitude=longitude,
        region_name=region_name,
        score=health_score,
        category=category,
        explanation=explanation,
        contributing_factors=contributing_factors,
        recommended_action=action
    )

    db.add(health_entry)
    db.commit()
    db.refresh(health_entry)
    
    return health_entry

def get_latest_health_score(db: Session, lat: float, lon: float):
    # For simulation, if no entry exists within 0.1 degree, create one
    existing = db.query(models.OceanHealthScore).filter(
        models.OceanHealthScore.latitude.between(lat - 0.1, lat + 0.1),
        models.OceanHealthScore.longitude.between(lon - 0.1, lon + 0.1)
    ).order_by(models.OceanHealthScore.created_at.desc()).first()
    
    if not existing:
        # Mocking some data for the initial score if not found
        return calculate_ocean_health(
            db, lat, lon, 
            debris_density=random.uniform(5, 60),
            chl_anomaly=random.uniform(-1, 1),
            sst_anomaly=random.uniform(-1, 2),
            wave_height=random.uniform(0.5, 4.0),
            region_name="Localized Marine Zone"
        )
    return existing
