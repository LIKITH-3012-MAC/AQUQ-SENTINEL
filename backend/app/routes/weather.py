from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import database, auth, models
from ..services import openweather_service

router = APIRouter(prefix="/api/weather", tags=["weather"])

@router.get("/marine")
def get_weather_data(
    lat: float, 
    lon: float, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Fetch live marine weather data.
    """
    return openweather_service.fetch_marine_weather(db, lat, lon)

