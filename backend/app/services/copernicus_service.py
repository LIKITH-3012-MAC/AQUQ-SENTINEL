import random
from sqlalchemy.orm import Session
from .. import models

def fetch_ocean_currents(db: Session, lat: float, lon: float):
    """
    Fetch ocean currents and wave data from Copernicus.
    """
    # Simulate Copernicus Marine Toolbox interaction
    obs = models.OceanCurrentObservation(
        latitude=lat,
        longitude=lon,
        wave_height=round(random.uniform(0.5, 5.0), 2),
        current_speed=round(random.uniform(0.1, 2.5), 2),
        wave_direction=round(random.uniform(0, 360), 1)
    )
    
    db.add(obs)
    db.commit()
    db.refresh(obs)
    return obs
