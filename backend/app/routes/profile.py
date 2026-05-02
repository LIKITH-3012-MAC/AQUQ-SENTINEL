from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Any
from .. import models, schemas, database, auth
from uuid import UUID

router = APIRouter(prefix="/api/profile", tags=["profile"])

@router.get("/me", response_model=schemas.FullProfileResponse)
def get_my_profile(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Fetch full profile and activity for the logged-in user.
    """
    # 1. Ensure profile exists (lazy create)
    profile = db.query(models.UserProfile).filter(models.UserProfile.user_id == current_user.id).first()
    if not profile:
        profile = models.UserProfile(user_id=current_user.id)
        db.add(profile)
        db.commit()
        db.refresh(profile)

    # 2. Fetch stats
    total_reports = db.query(func.count(models.MarineReport.id)).filter(models.MarineReport.user_id == current_user.id).scalar()
    active_reports = db.query(func.count(models.MarineReport.id)).filter(
        models.MarineReport.user_id == current_user.id,
        models.MarineReport.status.in_(["Submitted", "Under Review", "Verified", "Assigned", "Action in Progress"])
    ).scalar()
    resolved_reports = db.query(func.count(models.MarineReport.id)).filter(
        models.MarineReport.user_id == current_user.id,
        models.MarineReport.status == "Resolved"
    ).scalar()
    total_chats = db.query(func.count(models.ChatbotMessage.id)).filter(models.ChatbotMessage.user_id == current_user.id).scalar()
    missions_joined = db.query(func.count(models.Mission.id)).filter(models.Mission.assigned_to == current_user.id).scalar()

    # 3. Fetch recent reports
    recent_reports = db.query(models.MarineReport).filter(
        models.MarineReport.user_id == current_user.id
    ).order_by(models.MarineReport.created_at.desc()).limit(5).all()

    # 4. Watchlist
    watchlist = db.query(models.UserWatchlistRegion).filter(models.UserWatchlistRegion.user_id == current_user.id).all()

    return {
        "success": True,
        "user": current_user,
        "profile": profile,
        "stats": {
            "total_reports": total_reports or 0,
            "active_reports": active_reports or 0,
            "resolved_reports": resolved_reports or 0,
            "total_chat_queries": total_chats or 0,
            "missions_joined": missions_joined or 0
        },
        "recent_reports": recent_reports,
        "watchlist_regions": watchlist
    }

@router.patch("/me", response_model=schemas.FullProfileResponse)
def update_my_profile(
    profile_update: schemas.UserProfileUpdate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Update profile and basic user info.
    """
    profile = db.query(models.UserProfile).filter(models.UserProfile.user_id == current_user.id).first()
    if not profile:
        profile = models.UserProfile(user_id=current_user.id)
        db.add(profile)

    # Update User model if full_name is provided
    if profile_update.full_name is not None:
        current_user.full_name = profile_update.full_name

    # Update Profile fields
    update_data = profile_update.dict(exclude_unset=True)
    if "full_name" in update_data:
        del update_data["full_name"]
        
    for key, value in update_data.items():
        setattr(profile, key, value)

    db.commit()
    db.refresh(profile)
    db.refresh(current_user)

    return get_my_profile(db, current_user)

@router.post("/watchlist", status_code=status.HTTP_201_CREATED)
def add_to_watchlist(
    region: Any = None, # Simplified for now
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # Logic to add a region to watchlist
    pass
