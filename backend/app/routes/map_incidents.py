from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import models, models_ai, schemas, database, auth

router = APIRouter(prefix="/api/map", tags=["map"])

@router.get("/incidents", response_model=List[schemas.MapIncidentResponse])
def get_all_map_incidents(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Unified route to fetch both Admin Simulated Incidents and User Issue Reports.
    Uses MarineReport table as the primary source of truth for both.
    """
    incidents = []

    # Fetch all Marine Reports (includes both real and simulated)
    all_reports = db.query(models.MarineReport).all()
    
    for report in all_reports:
        # Determine source type based on simulation flag or title hint
        is_sim = report.is_simulated or "SIMULATED" in report.title.upper()
        source_type = "admin_simulation" if is_sim else "user_report"
        
        # Determine radius (if simulated, try to find the original incident for radius)
        radius = 0.0
        if report.is_simulated and report.simulation_id:
            sim_orig = db.query(models.SimulatedIncident).filter(models.SimulatedIncident.id == report.simulation_id).first()
            if sim_orig:
                radius = sim_orig.affected_radius

        incidents.append(schemas.MapIncidentResponse(
            id=f"report_{report.id}",
            source_type=source_type,
            latitude=report.latitude,
            longitude=report.longitude,
            title=report.title,
            severity=report.severity,
            status=report.status,
            is_simulated=report.is_simulated,
            created_at=report.created_at,
            popup_summary=report.description[:100] + ("..." if len(report.description) > 100 else ""),
            radius_km=radius
        ))

    return incidents
