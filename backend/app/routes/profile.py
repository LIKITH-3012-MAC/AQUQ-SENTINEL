from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Response
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import models, schemas, database, auth
from ..services.profile_service import ProfileService
import uuid

router = APIRouter(prefix="/api/profile", tags=["profile"])

@router.get("/me", response_model=schemas.FullProfileResponse)
def get_my_profile(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    profile = ProfileService.get_or_create_profile(db, current_user.id)
    stats = ProfileService.get_user_stats(db, current_user.id)
    
    recent_reports = db.query(models.MarineReport).filter(
        models.MarineReport.user_id == current_user.id
    ).order_by(models.MarineReport.created_at.desc()).limit(5).all()
    
    recent_activity = db.query(models.UserActivityTimeline).filter(
        models.UserActivityTimeline.user_id == current_user.id
    ).order_by(models.UserActivityTimeline.created_at.desc()).limit(10).all()
    
    watchlist = db.query(models.UserWatchlistRegion).filter(
        models.UserWatchlistRegion.user_id == current_user.id
    ).all()

    # Ensure profile_image_url points to our retrieval route if binary exists
    binary_img = db.query(models.UserProfileImage).filter(models.UserProfileImage.user_id == current_user.id).first()
    if binary_img and binary_img.binary_data:
        profile.profile_image_url = f"/api/profile/image/{current_user.id}"

    return {
        "success": True,
        "user": current_user,
        "profile": profile,
        "stats": stats,
        "recent_reports": recent_reports,
        "recent_activity": recent_activity,
        "watchlist_regions": watchlist
    }

@router.patch("/me", response_model=schemas.FullProfileResponse)
def update_my_profile(
    update_data: schemas.UserProfileUpdate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    ProfileService.update_profile(db, current_user, update_data)
    return get_my_profile(db, current_user)

@router.post("/me/photo")
async def upload_profile_photo(
    file: UploadFile = File(...),
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    content = await file.read()
    if len(content) > 2 * 1024 * 1024: # 2MB limit
        raise HTTPException(status_code=400, detail="Image size must be less than 2MB")
    
    img_record = db.query(models.UserProfileImage).filter(models.UserProfileImage.user_id == current_user.id).first()
    if not img_record:
        img_record = models.UserProfileImage(user_id=current_user.id)
        db.add(img_record)
    
    img_record.binary_data = content
    img_record.mime_type = file.content_type
    img_record.file_size = len(content)
    
    # Also update the URL in profile
    profile = ProfileService.get_or_create_profile(db, current_user.id)
    profile.profile_image_url = f"/api/profile/image/{current_user.id}"
    
    db.commit()
    
    ProfileService.log_activity(db, current_user.id, "photo_upload", "Updated profile identification image.")
    
    return {"success": True, "message": "Profile photo updated", "url": profile.profile_image_url}

@router.get("/image/{user_id}")
def get_profile_image(
    user_id: uuid.UUID,
    db: Session = Depends(database.get_db)
):
    img_record = db.query(models.UserProfileImage).filter(models.UserProfileImage.user_id == user_id).first()
    if not img_record or not img_record.binary_data:
        raise HTTPException(status_code=404, detail="Image not found")
    
    return Response(content=img_record.binary_data, media_type=img_record.mime_type)
