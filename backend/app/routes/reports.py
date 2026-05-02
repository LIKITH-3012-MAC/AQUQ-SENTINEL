from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import models, schemas, database, auth
from ..services import debris_detector, risk_engine, report_assistant

router = APIRouter(prefix="/api/reports", tags=["reports"])

@router.post("/create", response_model=schemas.MarineReportResponse)
def create_report(
    report: schemas.MarineReportCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Create a new marine report and trigger AI analysis.
    """
    # Trigger AI Assistant Analysis
    ai_results = report_assistant.analyze_report_submission(
        report.report_type, report.severity, report.description
    )

    db_report = models.MarineReport(
        user_id=current_user.id,
        ai_analysis=ai_results,
        **report.dict()
    )
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    
    # Initial status update in lifecycle
    update = models.IncidentUpdate(
        report_id=db_report.id,
        status="Submitted",
        notes="Initial report received by AquaSentinel Intelligence OS.",
        updated_by=current_user.id
    )
    db.add(update)
    db.commit()
    
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

@router.post("/analyze")
def preview_analysis(
    report: schemas.MarineReportCreate,
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Get AI analysis preview before submission.
    """
    return report_assistant.analyze_report_submission(
        report.report_type, report.severity, report.description
    )

@router.get("/{id}/history")
def get_report_history(
    id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Get the lifecycle history of a report.
    """
    return db.query(models.IncidentUpdate).filter(models.IncidentUpdate.report_id == id).order_by(models.IncidentUpdate.created_at.desc()).all()

@router.patch("/{id}/status", response_model=schemas.MarineReportResponse)
def update_report_status(
    id: int,
    status_update: schemas.ReportStatusUpdate,
    notes: Optional[str] = "Status updated by authority.",
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Update report status and record in lifecycle history.
    """
    if current_user.role not in ["admin", "authority"]:
        raise HTTPException(status_code=403, detail="Not authorized to update status")
    
    db_report = db.query(models.MarineReport).filter(models.MarineReport.id == id).first()
    if not db_report:
        raise HTTPException(status_code=404, detail="Report not found")
        
    db_report.status = status_update.status
    
    # Record update in history
    update = models.IncidentUpdate(
        report_id=db_report.id,
        status=status_update.status,
        notes=notes,
        updated_by=current_user.id
    )
    db.add(update)
    db.commit()
    db.refresh(db_report)

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
