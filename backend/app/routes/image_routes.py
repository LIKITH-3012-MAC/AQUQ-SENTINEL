import os
import shutil
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from .. import schemas, models, auth, database, config

router = APIRouter(prefix="/api/images", tags=["images"])

@router.post("/upload")
def upload_image(
    file: UploadFile = File(...),
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    os.makedirs(config.settings.UPLOAD_DIR, exist_ok=True)
    file_location = os.path.join(config.settings.UPLOAD_DIR, file.filename)
    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)
        
    db_image = models.UploadedImage(
        user_id=current_user.id,
        filename=file.filename,
        original_filename=file.filename,
        image_path=file_location,
        status="processed"
    )
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return {"id": db_image.id, "filename": db_image.filename}

@router.get("/")
def get_images(db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    if current_user.role == "admin":
        return db.query(models.UploadedImage).all()
    return db.query(models.UploadedImage).filter(models.UploadedImage.user_id == current_user.id).all()
