from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, database, auth
from fastapi.responses import JSONResponse
from ..services import risk_engine, weather_service

router = APIRouter(prefix="/api/risk", tags=["risk"])

@router.post("/calculate")
def calculate_risk(
    req: schemas.RiskScoreBase,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Trigger a risk calculation for a specific location using Weather API integration.
    """
    # Fetch real weather data via backend service
    weather_data = weather_service.get_marine_weather(req.latitude, req.longitude)
    
    signals_used = ["local_db"]
    signals_missing = []
    
    temp = 25.0
    wind = 5.0
    weather_desc = "clear"
    
    if weather_data.get("status") == "success":
        signals_used.append("weather_api")
        temp = weather_data.get("temperature", 25.0)
        wind = weather_data.get("wind_speed", 5.0)
        weather_desc = weather_data.get("description", "clear")
    else:
        signals_missing.append("weather_api")

    risk_data = risk_engine.calculate_marine_risk(
        db=db,
        latitude=req.latitude,
        longitude=req.longitude,
        temperature=temp,
        wind_speed=wind,
        weather_desc=weather_desc,
        signals_used=signals_used,
        signals_missing=signals_missing
    )
    
    # Audit log
    audit = models.AuditLog(
        user_id=current_user.id,
        action="risk_calculation",
        entity_type="risk_score",
        entity_id=str(risk_data.get("id")),
        action_metadata={"lat": req.latitude, "lon": req.longitude, "score": risk_data.get("risk_score")}
    )
    db.add(audit)
    db.commit()
    
    # Remove DB 'id' before returning JSON structure
    if "id" in risk_data:
        del risk_data["id"]

    return JSONResponse(content=risk_data)

@router.get("/history", response_model=List[schemas.RiskScoreResponse])
def get_risk_history(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Get recent risk calculations.
    """
    return db.query(models.RiskScore).order_by(models.RiskScore.created_at.desc()).limit(50).all()
