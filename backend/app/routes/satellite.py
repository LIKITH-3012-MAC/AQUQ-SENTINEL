from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import database, auth, models
from ..services import nasa_service

router = APIRouter(prefix="/api/satellite", tags=["satellite"])

@router.get("/nasa")
def get_nasa_data(
    lat: float, 
    lon: float, 
    parameter: str = "chlorophyll",
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Fetch live NASA satellite data for a location.
    """
    return nasa_service.fetch_nasa_data(db, lat, lon, parameter)

@router.get("/layers")
def get_nasa_layers():
    """
    Get available NASA GIBS layers.
    """
    return nasa_service.get_gibs_layers()

