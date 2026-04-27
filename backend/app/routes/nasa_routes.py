from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import auth, database
from ..services import nasa_ocean_service

router = APIRouter(prefix="/api/nasa", tags=["nasa"])

@router.get("/layers")
def get_nasa_layers(current_user=Depends(auth.get_current_user)):
    return nasa_ocean_service.get_gibs_layers()

@router.get("/datasets")
def get_nasa_datasets(keyword: str = "", start_date: str = "", end_date: str = "", lat: float = 0.0, lon: float = 0.0, current_user=Depends(auth.get_current_user)):
    return nasa_ocean_service.search_ocean_datasets(keyword, start_date, end_date, lat, lon)

@router.get("/gibs-tile-url")
def get_gibs_url(layer: str, date: str, current_user=Depends(auth.get_current_user)):
    return {"url": nasa_ocean_service.build_gibs_tile_url(layer, date)}

@router.get("/chlorophyll")
def get_chlorophyll(lat: float, lon: float, date: str, current_user=Depends(auth.get_current_user)):
    return nasa_ocean_service.get_chlorophyll_indicator(lat, lon, date)

@router.get("/ocean-summary")
def get_ocean_summary(lat: float, lon: float, date: str, current_user=Depends(auth.get_current_user)):
    return nasa_ocean_service.get_ocean_color_summary(lat, lon, date)
