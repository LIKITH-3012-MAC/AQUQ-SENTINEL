import random
from sqlalchemy.orm import Session
from .. import models

def run_pollution_simulation(db: Session, user_id: int, lat: float, lon: float, spill_type: str, volume: float):
    """
    Digital Twin Simulation: Predicts pollution spread based on currents and wind.
    """
    # Simplified simulation logic
    # In production, this would use numerical models like GNOME or OpenDrift
    
    spread_radius = volume * random.uniform(0.5, 2.0)
    direction = random.randint(0, 360)
    
    # Generate predicted path points
    path = []
    for i in range(1, 6):
        path.append({
            "hour": i * 6,
            "lat": lat + (i * 0.05 * random.uniform(0.8, 1.2)),
            "lon": lon + (i * 0.05 * random.uniform(0.8, 1.2)),
            "concentration": round(100 / i, 2)
        })
        
    simulation = models.Simulation(
        user_id=user_id,
        simulation_type="pollution_flow",
        parameters={"lat": lat, "lon": lon, "spill_type": spill_type, "volume": volume},
        results={"spread_radius_km": spread_radius, "predicted_path": path}
    )
    
    db.add(simulation)
    db.commit()
    db.refresh(simulation)
    
    return simulation

def prescribe_action(simulation_data: dict):
    """
    Prescriptive AI: Suggests actions based on simulation results.
    """
    radius = simulation_data.get("spread_radius_km", 0)
    if radius > 10:
        return {
            "priority": "CRITICAL",
            "actions": [
                "Deploy large-scale containment booms",
                "Alert National Coast Guard",
                "Evacuate nearby marine farms"
            ]
        }
    return {
        "priority": "MEDIUM",
        "actions": [
            "Monitor spread via satellite",
            "Deploy surface skimmers"
        ]
    }
