from sqlalchemy.orm import Session
from sqlalchemy import func
from .. import models, schemas
from uuid import UUID
from datetime import datetime

class ProfileService:
    @staticmethod
    def get_or_create_profile(db: Session, user_id: UUID):
        profile = db.query(models.UserProfile).filter(models.UserProfile.user_id == user_id).first()
        user = db.query(models.User).filter(models.User.id == user_id).first()
        
        if not profile:
            profile = models.UserProfile(user_id=user_id)
            db.add(profile)
            db.commit()
            db.refresh(profile)
            
        # Recalculate completion on every fetch to ensure it's dynamic
        profile.profile_completion_percent = ProfileService.calculate_completion(profile, user)
        db.commit()
        
        return profile

    @staticmethod
    def calculate_completion(profile: models.UserProfile, user: models.User):
        score = 0
        total = 7
        
        if user.full_name: score += 1
        if profile.phone: score += 1
        if profile.state or profile.city: score += 1
        if profile.preferred_region: score += 1
        if profile.bio: score += 1
        if profile.profile_image_url: score += 1
        if profile.organization or profile.occupation: score += 1
        
        return int((score / total) * 100)

    @staticmethod
    def log_activity(db: Session, user_id: UUID, event_type: str, description: str, metadata: dict = None):
        activity = models.UserActivityTimeline(
            user_id=user_id,
            event_type=event_type,
            description=description,
            metadata_json=metadata
        )
        db.add(activity)
        db.commit()

    @staticmethod
    def get_user_stats(db: Session, user_id: UUID):
        total_reports = db.query(models.MarineReport).filter(models.MarineReport.user_id == user_id).count()
        active_reports = db.query(models.MarineReport).filter(models.MarineReport.user_id == user_id, models.MarineReport.status != "Resolved").count()
        resolved_reports = db.query(models.MarineReport).filter(models.MarineReport.user_id == user_id, models.MarineReport.status == "Resolved").count()
        total_chat_queries = db.query(models.ChatbotMessage).filter(models.ChatbotMessage.user_id == user_id).count()
        missions_joined = db.query(models.Mission).filter(models.Mission.assigned_to == user_id).count()
        missions_completed = db.query(models.Mission).filter(models.Mission.assigned_to == user_id, models.Mission.status == "Completed").count()
        alerts_received = db.query(models.Alert).count() # Simplified, or filter by region
        watched_regions_count = db.query(models.UserWatchlistRegion).filter(models.UserWatchlistRegion.user_id == user_id).count()

        return schemas.UserActivityStats(
            total_reports=total_reports,
            active_reports=active_reports,
            resolved_reports=resolved_reports,
            total_chat_queries=total_chat_queries,
            missions_joined=missions_joined,
            missions_completed=missions_completed,
            alerts_received=alerts_received,
            watched_regions_count=watched_regions_count
        )

    @staticmethod
    def update_profile(db: Session, user: models.User, update_data: schemas.UserProfileUpdate):
        profile = ProfileService.get_or_create_profile(db, user.id)
        
        if update_data.full_name:
            user.full_name = update_data.full_name
            
        update_dict = update_data.dict(exclude_unset=True)
        if 'full_name' in update_dict: del update_dict['full_name']
        
        for key, value in update_dict.items():
            setattr(profile, key, value)
            
        profile.profile_completion_percent = ProfileService.calculate_completion(profile, user)
        
        db.commit()
        db.refresh(profile)
        db.refresh(user)
        
        ProfileService.log_activity(db, user.id, "profile_update", "Updated personal profile details.")
        
        return profile, user
