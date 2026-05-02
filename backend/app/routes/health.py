from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import database, models, auth
from ..services import health_service

router = APIRouter(prefix="/api/health", tags=["health"])

@router.get("/score")
def get_ocean_health(
    lat: float, 
    lon: float, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Get the Ocean Health Score for a specific location.
    """
    score = health_service.get_latest_health_score(db, lat, lon)
    return score

@router.post("/calculate")
def calculate_health(
    lat: float,
    lon: float,
    debris: float = 0.0,
    sst: float = 0.0,
    chl: float = 0.0,
    wave: float = 0.0,
    region: str = "Target Zone",
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Manually trigger a health score calculation.
    """
    score = health_service.calculate_ocean_health(
        db, lat, lon, debris, chl, sst, wave, region_name=region
    )
    return score
