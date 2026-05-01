from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, database, auth
from ..services import risk_engine

router = APIRouter(prefix="/api/risk", tags=["risk"])

@router.post("/calculate", response_model=schemas.RiskScoreResponse)
def calculate_risk(
    req: schemas.RiskScoreBase,
    debris_density: float = 0.0,
    chl_anomaly: float = 0.0,
    sst_anomaly: float = 0.0,
    wave_height: float = 0.0,
    wind_speed: float = 0.0,
    current_speed: float = 0.0,
    proximity_sensitive: float = 100.0,
    report_severity: float = 0.0,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Trigger a risk calculation for a specific location.
    """
    risk_entry = risk_engine.calculate_marine_risk(
        db=db,
        latitude=req.latitude,
        longitude=req.longitude,
        debris_density=debris_density,
        chl_anomaly=chl_anomaly,
        sst_anomaly=sst_anomaly,
        wave_height=wave_height,
        wind_speed=wind_speed,
        current_speed=current_speed,
        proximity_sensitive_km=proximity_sensitive,
        report_severity_score=report_severity
    )
    
    # Audit log
    audit = models.AuditLog(
        user_id=current_user.id,
        action="risk_calculation",
        entity_type="risk_score",
        entity_id=str(risk_entry.id),
        action_metadata={"lat": req.latitude, "lon": req.longitude, "score": risk_entry.score}
    )
    db.add(audit)
    db.commit()
    
    return risk_entry

@router.get("/history", response_model=List[schemas.RiskScoreResponse])
def get_risk_history(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Get recent risk calculations.
    """
    return db.query(models.RiskScore).order_by(models.RiskScore.created_at.desc()).limit(50).all()
