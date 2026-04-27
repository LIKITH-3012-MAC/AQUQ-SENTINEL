from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, auth, database
from ..services import report_generator
import os

router = APIRouter(prefix="/api/reports", tags=["reports"])

@router.post("/generate")
def generate_report(data: dict, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    file_path = report_generator.generate_simple_report(data)
    
    db_report = models.Report(
        user_id=current_user.id,
        title=f"Report - {data.get('location', 'Unknown')}",
        report_type="json",
        file_path=file_path
    )
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return {"status": "success", "report_id": db_report.id, "file_path": file_path}

@router.get("/")
def get_reports(db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    if current_user.role == "admin":
        return db.query(models.Report).all()
    return db.query(models.Report).filter(models.Report.user_id == current_user.id).all()
