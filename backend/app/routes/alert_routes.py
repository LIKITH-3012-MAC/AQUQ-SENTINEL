from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import schemas, models, auth, database

router = APIRouter(prefix="/api/alerts", tags=["alerts"])

@router.get("/", response_model=List[schemas.AlertResponse])
def get_all_alerts(db: Session = Depends(database.get_db), admin_user: models.User = Depends(auth.get_current_active_admin)):
    return db.query(models.Alert).order_by(models.Alert.created_at.desc()).all()

@router.get("/user", response_model=List[schemas.AlertResponse])
def get_user_alerts(db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    # Simple global active alerts for dashboard
    return db.query(models.Alert).filter(models.Alert.status == "active").order_by(models.Alert.created_at.desc()).all()

@router.post("/manual")
def create_manual_alert(data: dict, db: Session = Depends(database.get_db), admin_user: models.User = Depends(auth.get_current_active_admin)):
    db_alert = models.Alert(
        title=data.get("title"),
        message=data.get("message"),
        severity=data.get("severity", data.get("risk_level", "Medium")),
        latitude=data.get("latitude"),
        longitude=data.get("longitude"),
        status="active"
    )
    db.add(db_alert)
    db.commit()
    return {"status": "success"}

@router.put("/{alert_id}/verify")
def verify_alert(alert_id: int, db: Session = Depends(database.get_db), admin_user: models.User = Depends(auth.get_current_active_admin)):
    alert = db.query(models.Alert).filter(models.Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.verified_by_admin = True
    db.commit()
    return {"status": "success"}

@router.delete("/{alert_id}")
def resolve_alert(alert_id: int, db: Session = Depends(database.get_db), admin_user: models.User = Depends(auth.get_current_active_admin)):
    alert = db.query(models.Alert).filter(models.Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.status = "resolved"
    db.commit()
    return {"status": "success"}
