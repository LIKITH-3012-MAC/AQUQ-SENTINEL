from sqlalchemy.orm import Session
from .. import models
from . import health_service
from typing import List, Dict, Any

def get_hyperlocal_intelligence(db: Session, lat: float, lon: float, radius_km: float = 50.0) -> Dict[str, Any]:
    """
    Aggregates intelligence for a specific location.
    """
    # 1. Get local health score
    health_score = health_service.get_latest_health_score(db, lat, lon)
    
    # 2. Find nearby alerts (simplistic box search for now)
    # 1 degree is roughly 111km
    delta = radius_km / 111.0
    alerts = db.query(models.Alert).filter(
        models.Alert.latitude.between(lat - delta, lat + delta),
        models.Alert.longitude.between(lon - delta, lon + delta),
        models.Alert.status == "active"
    ).all()
    
    # 3. Find nearby debris reports
    reports = db.query(models.MarineReport).filter(
        models.MarineReport.latitude.between(lat - delta, lat + delta),
        models.MarineReport.longitude.between(lon - delta, lon + delta),
        models.MarineReport.status != "Closed"
    ).all()
    
    # 4. Identify Hotspots (Zones with high report density or critical alerts)
    hotspots = []
    if len(reports) > 5 or health_score.score < 40:
        hotspots.append({
            "name": f"High Activity Zone near {health_score.region_name}",
            "risk_level": "High" if health_score.score < 40 else "Moderate",
            "reason": f"Detected {len(reports)} reports and {len(alerts)} active alerts."
        })
    
    return {
        "location": {"lat": lat, "lon": lon, "region": health_score.region_name},
        "health_score": health_score,
        "alerts_count": len(alerts),
        "nearby_alerts": alerts,
        "reports_count": len(reports),
        "hotspots": hotspots,
        "summary": f"The region is currently {health_score.category.lower()}. {len(alerts)} alerts active within {radius_km}km."
    }
