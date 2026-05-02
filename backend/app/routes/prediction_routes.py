from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import database, models, auth, schemas
from ..services import prediction_service

router = APIRouter(prefix="/api/predictions", tags=["predictions"])

@router.get("/hotspots", response_model=schemas.HotspotPredictionResponse)
def get_hotspot_prediction(
    lat: float, 
    lon: float, 
    hours: int = 24,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Get debris drift prediction for a specific location.
    """
    return prediction_service.predict_debris_hotspots(db, lat, lon, hours)
