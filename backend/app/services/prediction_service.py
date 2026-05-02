from typing import List, Dict, Any
from sqlalchemy.orm import Session
from .. import models
import math
import random

def predict_debris_hotspots(db: Session, lat: float, lon: float, hours: int = 24) -> models.HotspotPrediction:
    """
    Predicts debris movement based on wave and current data.
    """
    # 1. Fetch current conditions (or use defaults)
    current = db.query(models.OceanCurrentObservation).filter(
        models.OceanCurrentObservation.latitude.between(lat - 0.5, lat + 0.5),
        models.OceanCurrentObservation.longitude.between(lon - 0.5, lon + 0.5)
    ).order_by(models.OceanCurrentObservation.created_at.desc()).first()
    
    speed = current.speed if current and current.speed else 0.5 # m/s
    direction = current.direction if current and current.direction else 45 # degrees
    
    # 2. Calculate drift path
    # 1 m/s = 3.6 km/h
    # 1 degree lat = 111km
    
    drift_path = []
    curr_lat, curr_lon = lat, lon
    
    for i in range(1, hours + 1):
        # Add some randomness for turbulence
        angle = math.radians(direction + random.uniform(-10, 10))
        dist_km = (speed * 3.6) # km in 1 hour
        
        delta_lat = (dist_km * math.cos(angle)) / 111.0
        delta_lon = (dist_km * math.sin(angle)) / (111.0 * math.cos(math.radians(curr_lat)))
        
        curr_lat += delta_lat
        curr_lon += delta_lon
        
        drift_path.append({"lat": round(curr_lat, 6), "lon": round(curr_lon, 6), "hour": i})
    
    # 3. Determine risk level
    risk_level = "High" if speed > 1.0 else "Moderate"
    
    prediction = models.HotspotPrediction(
        latitude=lat,
        longitude=lon,
        drift_path=drift_path,
        risk_level=risk_level,
        time_window=f"Next {hours}h",
        action_recommendation=f"Deploy interceptors at coordinate {drift_path[-1]['lat']}, {drift_path[-1]['lon']} to prevent coastal impact."
    )
    
    db.add(prediction)
    db.commit()
    db.refresh(prediction)
    
    return prediction
