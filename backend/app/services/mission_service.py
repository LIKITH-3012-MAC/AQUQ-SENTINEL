from sqlalchemy.orm import Session
from .. import models, schemas
import uuid
from datetime import datetime

class MissionService:
    @staticmethod
    def create_mission_from_report(db: Session, report_id: int):
        """
        Create a mission task for an NGO/Volunteer based on a verified report.
        """
        report = db.query(models.MarineReport).filter(models.MarineReport.id == report_id).first()
        if not report:
            return None

        mission = models.Mission(
            report_id=report.id,
            title=f"Cleanup Operation: {report.title}",
            description=f"Automated mission triggered by {report.severity} severity report. Location: {report.latitude}, {report.longitude}.",
            urgency=report.severity,
            status="Pending",
            recommended_equipment="Standard surface skimmers, heavy-duty collection bags, and GPS tracking buoy."
        )
        db.add(mission)
        
        # Update report status to Assigned
        report.status = "Assigned"
        
        db.commit()
        db.refresh(mission)
        return mission

    @staticmethod
    def accept_mission(db: Session, mission_id: uuid.UUID, user_id: uuid.UUID):
        mission = db.query(models.Mission).filter(models.Mission.id == mission_id).first()
        if not mission:
            return None
        
        mission.assigned_to = user_id
        mission.status = "Accepted"
        
        # Update report lifecycle
        report = db.query(models.MarineReport).filter(models.MarineReport.id == mission.report_id).first()
        report.status = "Action in Progress"
        
        update = models.IncidentUpdate(
            report_id=report.id,
            status="Action in Progress",
            notes=f"Mission accepted by responder unit {str(user_id)[:8]}.",
            updated_by=user_id
        )
        db.add(update)
        db.commit()
        return mission

    @staticmethod
    def complete_mission(db: Session, mission_id: uuid.UUID, notes: str, after_image_url: str = None):
        mission = db.query(models.Mission).filter(models.Mission.id == mission_id).first()
        if not mission:
            return None
        
        mission.status = "Completed"
        mission.progress_notes = notes
        mission.after_image = after_image_url
        mission.completed_at = datetime.utcnow()
        
        # Update report lifecycle to Resolved
        report = db.query(models.MarineReport).filter(models.MarineReport.id == mission.report_id).first()
        report.status = "Resolved"
        
        update = models.IncidentUpdate(
            report_id=report.id,
            status="Resolved",
            notes=f"Mission completed successfully. Cleanup verified. Note: {notes}",
            updated_by=mission.assigned_to
        )
        db.add(update)
        db.commit()
        return mission

    @staticmethod
    def get_user_missions(db: Session, user_id: uuid.UUID):
        return db.query(models.Mission).filter(models.Mission.assigned_to == user_id).all()

    @staticmethod
    def get_nearby_pending_missions(db: Session, lat: float, lon: float, radius: float = 50.0):
        return db.query(models.Mission).join(models.MarineReport).filter(
            models.Mission.status == "Pending",
            func.sqrt(
                func.pow(models.MarineReport.latitude - lat, 2) + 
                func.pow(models.MarineReport.longitude - lon, 2)
            ) * 111.0 <= radius
        ).all()
