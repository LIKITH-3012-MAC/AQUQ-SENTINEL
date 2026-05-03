from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from .. import schemas, models, auth, database, db_fixer
from ..services import metrics_service

router = APIRouter(prefix="/api/admin", tags=["admin"])

@router.post("/repair-db")
async def repair_database(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    """Force run database schema fixes."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    try:
        db_fixer.fix_database_schema()
        return {"status": "success", "message": "Schema repairs completed. Check logs for details."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/overview")
def get_overview(db: Session = Depends(database.get_db), admin_user: models.User = Depends(auth.get_current_active_admin)):
    return metrics_service.get_dashboard_metrics(db)

@router.get("/users", response_model=List[schemas.UserResponse])
def get_users(db: Session = Depends(database.get_db), admin_user: models.User = Depends(auth.get_current_active_admin)):
    return db.query(models.User).all()

@router.put("/users/{user_id}/role")
def update_user_role(user_id: UUID, role: str, db: Session = Depends(database.get_db), admin_user: models.User = Depends(auth.get_current_active_admin)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.role = role
    db.commit()
    return {"status": "success"}

@router.put("/users/{user_id}/status")
def update_user_status(user_id: UUID, active: bool, db: Session = Depends(database.get_db), admin_user: models.User = Depends(auth.get_current_active_admin)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = active
    db.commit()
    return {"status": "success", "is_active": active}
@router.get("/audit-logs", response_model=List[schemas.AuditLogResponse])
def get_audit_logs(db: Session = Depends(database.get_db), admin_user: models.User = Depends(auth.get_current_active_admin)):
    return db.query(models.AuditLog).order_by(models.AuditLog.created_at.desc()).limit(100).all()
