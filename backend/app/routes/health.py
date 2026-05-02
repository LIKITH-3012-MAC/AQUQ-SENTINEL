from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import database, models, auth
from ..services.ocean_health_service import OceanHealthService

router = APIRouter(prefix="/api/health", tags=["health"])

@router.get("/score")
def get_ocean_health(
    lat: float, 
    lon: float, 
    radius: float = 20.0,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Get the Ocean Health Score for a specific location using advanced intelligence logic.
    """
    score = OceanHealthService.calculate_health_score(db, lat, lon, radius)
    return score

@router.get("/global")
def get_global_health(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    return OceanHealthService.get_global_averages(db)
