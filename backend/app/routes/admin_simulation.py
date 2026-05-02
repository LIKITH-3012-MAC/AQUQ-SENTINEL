from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, database, auth
from ..services import simulation_engine
from datetime import datetime, timedelta
import uuid

router = APIRouter(prefix="/api/admin/simulations", tags=["admin-simulation"])

def check_admin_role(current_user: models.User = Depends(auth.get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access restricted to administrative intelligence officers only."
        )
    return current_user

@router.post("/", response_model=schemas.SimulatedIncidentResponse)
def create_simulation(
    sim_data: schemas.SimulatedIncidentCreate,
    db: Session = Depends(database.get_db),
    admin: models.User = Depends(check_admin_role)
):
    """
    Create a world-class simulated debris event for demonstrations.
    """
    expires_at = datetime.utcnow() + timedelta(minutes=sim_data.duration_minutes)
    
    new_sim = models.SimulatedIncident(
        admin_id=admin.id,
        scenario_title=sim_data.scenario_title,
        debris_type=sim_data.debris_type,
        latitude=sim_data.latitude,
        longitude=sim_data.longitude,
        severity=sim_data.severity,
        density_score=sim_data.density_score,
        affected_radius=sim_data.affected_radius,
        drift_direction=sim_data.drift_direction,
        message_title=sim_data.message_title,
        message_body=sim_data.message_body,
        health_impact_enabled=sim_data.health_impact_enabled,
        alert_broadcast_enabled=sim_data.alert_broadcast_enabled,
        mission_flow_enabled=sim_data.mission_flow_enabled,
        judge_note=sim_data.judge_note,
        expires_at=expires_at,
        is_active=True
    )
    db.add(new_sim)
    db.commit()
    db.refresh(new_sim)

    # Trigger intelligence side-effects
    simulation_engine.trigger_simulation_effects(db, new_sim, admin.id)

    # Log Audit
    audit = models.AuditLog(
        user_id=admin.id,
        action="simulation_created",
        entity_type="simulation",
        entity_id=str(new_sim.id),
        action_metadata={"title": new_sim.scenario_title, "severity": new_sim.severity}
    )
    db.add(audit)
    db.commit()

    return new_sim

@router.get("/", response_model=List[schemas.SimulatedIncidentResponse])
def list_simulations(
    db: Session = Depends(database.get_db),
    admin: models.User = Depends(check_admin_role)
):
    return db.query(models.SimulatedIncident).filter(models.SimulatedIncident.is_active == True).all()

@router.post("/reset", status_code=status.HTTP_200_OK)
def reset_all_simulations(
    db: Session = Depends(database.get_db),
    admin: models.User = Depends(check_admin_role)
):
    """
    Clear all simulated data from the system.
    """
    simulation_engine.clear_all_simulations(db)
    
    # Log Audit
    audit = models.AuditLog(
        user_id=admin.id,
        action="simulation_reset",
        entity_type="system",
        action_metadata={"purged_by": admin.full_name}
    )
    db.add(audit)
    db.commit()
    
    return {"success": True, "message": "All simulation data purged from the system."}

@router.delete("/{sim_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_simulation(
    sim_id: uuid.UUID,
    db: Session = Depends(database.get_db),
    admin: models.User = Depends(check_admin_role)
):
    sim = db.query(models.SimulatedIncident).filter(models.SimulatedIncident.id == sim_id).first()
    if not sim:
        raise HTTPException(status_code=404, detail="Simulation not found.")
    
    sim.is_active = False
    db.commit()
    return None
