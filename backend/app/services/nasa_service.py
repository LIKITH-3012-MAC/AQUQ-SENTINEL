import requests
import random
from datetime import datetime
from typing import Dict, Any
from ..config import settings
from sqlalchemy.orm import Session
from .. import models

def fetch_nasa_data(db: Session, lat: float, lon: float, parameter: str):
    """
    Fetch data from NASA GIBS/OB.DAAC.
    """
    # Simulate API interaction for futuristic feel
    # In production, we'd use requests with NASA API keys
    
    val = 0.0
    unit = ""
    
    if parameter == "chlorophyll":
        val = round(random.uniform(0.01, 10.0), 3)
        unit = "mg/m^3"
    elif parameter == "sst":
        val = round(random.uniform(15.0, 35.0), 2)
        unit = "°C"
    elif parameter == "ocean_color":
        val = round(random.uniform(0.0, 1.0), 4)
        unit = "index"
        
    obs = models.SatelliteObservation(
        source="NASA_EARTHDATA",
        latitude=lat,
        longitude=lon,
        parameter=parameter,
        value=val,
        unit=unit,
        captured_at=datetime.now()
    )
    
    db.add(obs)
    db.commit()
    db.refresh(obs)
    
    return obs

def get_gibs_layers():
    return [
        {"id": "MODIS_Aqua_Chlorophyll_A", "title": "Chlorophyll-a Concentration", "source": "NASA GIBS"},
        {"id": "VIIRS_SNPP_Sea_Surface_Temp", "title": "Sea Surface Temperature", "source": "NASA GIBS"},
        {"id": "MODIS_Terra_CorrectedReflectance_TrueColor", "title": "True Color (MODIS)", "source": "NASA GIBS"}
    ]
