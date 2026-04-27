from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import schemas, models, auth, database
from ..services import metrics_service

router = APIRouter(prefix="/api/admin", tags=["admin"])

@router.get("/overview")
def get_overview(db: Session = Depends(database.get_db), admin_user: models.User = Depends(auth.get_current_active_admin)):
    return metrics_service.get_dashboard_metrics(db)

@router.get("/users", response_model=List[schemas.UserResponse])
def get_users(db: Session = Depends(database.get_db), admin_user: models.User = Depends(auth.get_current_active_admin)):
    return db.query(models.User).all()

@router.put("/users/{user_id}/role")
def update_user_role(user_id: int, role: str, db: Session = Depends(database.get_db), admin_user: models.User = Depends(auth.get_current_active_admin)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.role = role
    db.commit()
    return {"status": "success"}

@router.put("/users/{user_id}/status")
def update_user_status(user_id: int, status: str, db: Session = Depends(database.get_db), admin_user: models.User = Depends(auth.get_current_active_admin)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.status = status
    db.commit()
    return {"status": "success"}
