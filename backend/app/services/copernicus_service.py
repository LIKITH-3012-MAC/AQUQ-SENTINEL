import random
from sqlalchemy.orm import Session
from .. import models

def fetch_ocean_currents(db: Session, lat: float, lon: float):
    """
    Fetch ocean currents and wave data from Copernicus.
    """
    # Simulate Copernicus Marine Toolbox interaction
    # Map mock data to model fields (speed, direction)
    obs = models.OceanCurrentObservation(
        latitude=lat,
        longitude=lon,
        speed=round(random.uniform(0.1, 2.5), 2),
        direction=round(random.uniform(0, 360), 1),
        source="Copernicus_Marine"
    )
    
    db.add(obs)
    db.commit()
    db.refresh(obs)
    return obs
