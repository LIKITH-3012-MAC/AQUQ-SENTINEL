from sqlalchemy.orm import Session
from .. import models
from uuid import UUID
from typing import List, Optional

def create_mission_from_report(db: Session, report_id: int) -> models.Mission:
    """
    Converts a verified report into a mission for NGOs/Volunteers.
    """
    report = db.query(models.MarineReport).filter(models.MarineReport.id == report_id).first()
    if not report:
        raise ValueError("Report not found")
        
    mission = models.Mission(
        report_id=report.id,
        title=f"Cleanup: {report.title}",
        description=f"Action required for detected {report.report_type} at {report.latitude}, {report.longitude}. {report.description}",
        urgency=report.severity,
        status="Pending",
        checklist=[
            {"task": "Verify site conditions", "done": False},
            {"task": "Deploy containment equipment", "done": False},
            {"task": "Collect and document waste", "done": False},
            {"task": "Final site clearance", "done": False}
        ]
    )
    
    db.add(mission)
    
    # Update report status
    report.status = "Assigned"
    update = models.IncidentUpdate(
        report_id=report.id,
        status="Assigned",
        notes="Mission created and awaiting assignment to a response team."
    )
    db.add(update)
    
    db.commit()
    db.refresh(mission)
    return mission

def assign_mission(db: Session, mission_id: UUID, user_id: UUID) -> models.Mission:
    mission = db.query(models.Mission).filter(models.Mission.id == mission_id).first()
    if not mission:
        raise ValueError("Mission not found")
        
    mission.assigned_to = user_id
    mission.status = "Accepted"
    
    # Update report
    report = db.query(models.MarineReport).filter(models.MarineReport.id == mission.report_id).first()
    report.status = "Action in Progress"
    
    update = models.IncidentUpdate(
        report_id=report.id,
        status="Action in Progress",
        notes=f"Mission accepted by volunteer team.",
        updated_by=user_id
    )
    db.add(update)
    
    db.commit()
    db.refresh(mission)
    return mission
