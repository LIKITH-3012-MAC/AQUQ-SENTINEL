from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, database, auth
from ..services import debris_detector, risk_engine

router = APIRouter(prefix="/api/reports", tags=["reports"])

@router.post("/create", response_model=schemas.MarineReportResponse)
def create_report(
    report: schemas.MarineReportCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Create a new marine report and trigger AI analysis if an image is provided.
    """
    db_report = models.MarineReport(
        user_id=current_user.id,
        **report.dict()
    )
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    
    # Log Audit
    audit = models.AuditLog(
        user_id=current_user.id,
        action="report_created",
        entity_type="marine_report",
        entity_id=str(db_report.id),
        action_metadata={"report_id": db_report.id, "type": db_report.report_type}
    )
    db.add(audit)
    db.commit()
    
    # If image exists, trigger simulated AI detection
    if db_report.image_url:
        debris_detector.process_debris_detection(db, db_report.id, db_report.image_url)
        
    return db_report

@router.get("/", response_model=List[schemas.MarineReportResponse])
def get_reports(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Get all reports. Admin sees all, users see their own.
    """
    if current_user.role == "admin":
        return db.query(models.MarineReport).all()
    return db.query(models.MarineReport).filter(models.MarineReport.user_id == current_user.id).all()

@router.patch("/{id}/status", response_model=schemas.MarineReportResponse)
def update_report_status(
    id: int,
    status_update: schemas.ReportStatusUpdate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Update report status (Admin only).
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can update status")
    
    db_report = db.query(models.MarineReport).filter(models.MarineReport.id == id).first()
    if not db_report:
        raise HTTPException(status_code=404, detail="Report not found")
        
    db_report.status = status_update.status
    db.commit()
    db.refresh(db_report)
    
    # Log Admin Action
    action = models.AdminAction(
        admin_id=current_user.id,
        action_type="update_report_status",
        target_id=id,
        details=f"Status changed to {status_update.status}"
    )
    db.add(action)
    db.commit()
    
    return db_report

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_report(
    id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Delete a report.
    """
    db_report = db.query(models.MarineReport).filter(models.MarineReport.id == id).first()
    if not db_report:
        raise HTTPException(status_code=404, detail="Report not found")
        
    if current_user.role != "admin" and db_report.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this report")
        
    db.delete(db_report)
    db.commit()
    return None
