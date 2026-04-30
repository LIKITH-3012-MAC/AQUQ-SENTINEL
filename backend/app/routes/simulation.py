from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import database, auth, models
from ..services import simulation_service

router = APIRouter(prefix="/api/simulation", tags=["simulation"])

@router.post("/pollution")
def simulate_pollution(
    lat: float,
    lon: float,
    spill_type: str,
    volume: float,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Run a digital twin pollution spread simulation.
    """
    sim = simulation_service.run_pollution_simulation(db, current_user.id, lat, lon, spill_type, volume)
    prescription = simulation_service.prescribe_action(sim.results)
    
    return {
        "simulation": sim,
        "prescription": prescription
    }

