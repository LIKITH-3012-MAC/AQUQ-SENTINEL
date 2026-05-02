from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from .. import database, models, auth, schemas
from ..services import mission_service

router = APIRouter(prefix="/api/missions", tags=["missions"])

@router.get("/", response_model=List[schemas.MissionResponse])
def get_missions(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Get all missions. NGOs/Volunteers see missions nearby or assigned to them.
    """
    if current_user.role == "admin":
        return db.query(models.Mission).all()
    return db.query(models.Mission).filter(
        (models.Mission.assigned_to == current_user.id) | (models.Mission.status == "Pending")
    ).all()

@router.post("/{report_id}/create", response_model=schemas.MissionResponse)
def create_mission(
    report_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    if current_user.role not in ["admin", "authority"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    return mission_service.create_mission_from_report(db, report_id)

@router.post("/{mission_id}/accept", response_model=schemas.MissionResponse)
def accept_mission(
    mission_id: UUID,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    return mission_service.assign_mission(db, mission_id, current_user.id)

@router.patch("/{mission_id}/progress")
def update_progress(
    mission_id: UUID,
    status: str,
    notes: str,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    mission = db.query(models.Mission).filter(models.Mission.id == mission_id).first()
    if not mission or mission.assigned_to != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized or mission not found")
    
    mission.status = status
    mission.progress_notes = notes
    
    if status == "Completed":
        from datetime import datetime
        mission.completed_at = datetime.utcnow()
        # Update report status
        report = db.query(models.MarineReport).filter(models.MarineReport.id == mission.report_id).first()
        report.status = "Resolved"
    
    db.commit()
    return {"message": "Mission updated"}
