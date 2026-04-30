from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import database, auth, models
from ..services import copernicus_service

router = APIRouter(prefix="/api/ocean", tags=["ocean"])

@router.get("/copernicus")
def get_ocean_data(
    lat: float, 
    lon: float, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Fetch live Copernicus ocean current and wave data.
    """
    return copernicus_service.fetch_ocean_currents(db, lat, lon)

