from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import auth, database
from ..services import copernicus_wave_service

router = APIRouter(prefix="/api/waves", tags=["waves"])

@router.get("/conditions")
def get_wave_conditions(lat: float, lon: float, date: str, current_user=Depends(auth.get_current_user)):
    return copernicus_wave_service.get_wave_conditions(lat, lon, date)
