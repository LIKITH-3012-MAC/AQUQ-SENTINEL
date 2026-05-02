from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from .. import database, models, auth, schemas
from ..services.mission_service import MissionService

router = APIRouter(prefix="/api/missions", tags=["missions"])

@router.get("/", response_model=List[schemas.MissionResponse])
def get_missions(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    if current_user.role == "admin":
        return db.query(models.Mission).all()
    return MissionService.get_user_missions(db, current_user.id)

@router.get("/nearby", response_model=List[schemas.MissionResponse])
def get_nearby_missions(
    lat: float,
    lon: float,
    radius: float = 50.0,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    return MissionService.get_nearby_pending_missions(db, lat, lon, radius)

@router.post("/{report_id}/create", response_model=schemas.MissionResponse)
def create_mission(
    report_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    if current_user.role not in ["admin", "authority"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    return MissionService.create_mission_from_report(db, report_id)

@router.post("/{mission_id}/accept", response_model=schemas.MissionResponse)
def accept_mission(
    mission_id: UUID,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    mission = MissionService.accept_mission(db, mission_id, current_user.id)
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    return mission

@router.post("/{mission_id}/complete", response_model=schemas.MissionResponse)
def complete_mission(
    mission_id: UUID,
    notes: str,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    mission = MissionService.complete_mission(db, mission_id, notes)
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    return mission
