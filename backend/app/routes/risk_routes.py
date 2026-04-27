from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import schemas, models, auth, database
from ..services import risk_engine
from datetime import datetime
import json

router = APIRouter(prefix="/api/risk", tags=["risk"])

@router.post("/evaluate", response_model=schemas.RiskAssessmentResponse)
def evaluate_risk(data: dict, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    result = risk_engine.evaluate_risk(
        debris_density_score=data.get("debris_density_score", 0.0),
        chlorophyll_value=data.get("chlorophyll_value", 0.0),
        algae_indicator=data.get("algae_indicator", 0.0),
        wave_height_m=data.get("wave_height_m", 0.0),
        wave_direction_deg=data.get("wave_direction_deg", 0.0),
        sensitive_zone_distance_km=data.get("sensitive_zone_distance_km", 50.0),
        ecosystem_degradation_score=data.get("ecosystem_degradation_score", 0.0)
    )
    
    db_risk = models.RiskAssessment(
        user_id=current_user.id,
        latitude=data.get("latitude", 0.0),
        longitude=data.get("longitude", 0.0),
        debris_density_score=data.get("debris_density_score", 0.0),
        chlorophyll_value=data.get("chlorophyll_value", 0.0),
        algae_indicator=data.get("algae_indicator", 0.0),
        wave_height_m=data.get("wave_height_m", 0.0),
        wave_direction_deg=data.get("wave_direction_deg", 0.0),
        sensitive_zone_distance_km=data.get("sensitive_zone_distance_km", 50.0),
        ecosystem_degradation_score=data.get("ecosystem_degradation_score", 0.0),
        risk_score=result["risk_score"],
        risk_level=result["risk_level"],
        recommendation=result["recommendation"],
        reasons_json=json.dumps(result["reasons"])
    )
    db.add(db_risk)
    db.commit()
    db.refresh(db_risk)
    
    # Generate Alert if Risk is HIGH or CRITICAL
    if result["risk_level"] in ["HIGH", "CRITICAL"]:
        db_alert = models.Alert(
            risk_assessment_id=db_risk.id,
            title=f"Marine Risk: {result['risk_level']}",
            message=result["recommendation"],
            risk_level=result["risk_level"],
            latitude=db_risk.latitude,
            longitude=db_risk.longitude,
            status="active"
        )
        db.add(db_alert)
        db.commit()
        
    return db_risk

@router.get("/location")
def get_risk_location(lat: float, lon: float, date: str, db: Session = Depends(database.get_db), current_user=Depends(auth.get_current_user)):
    # Find latest risk assessment for this location within a small radius
    # For demo, just get the most recent for this user
    return db.query(models.RiskAssessment).filter(models.RiskAssessment.user_id == current_user.id).order_by(models.RiskAssessment.assessment_date.desc()).first()
