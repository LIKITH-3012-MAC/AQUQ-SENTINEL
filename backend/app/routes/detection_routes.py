from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, auth, database
from ..services import debris_detector
import json

router = APIRouter(prefix="/api/detect", tags=["detection"])

@router.post("/debris/{image_id}")
def run_debris_detection(image_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    image = db.query(models.UploadedImage).filter(models.UploadedImage.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
        
    result = debris_detector.detect_debris(image.image_path)
    
    # Store results in DB
    for det in result["detections"]:
        db_det = models.DebrisDetection(
            image_id=image.id,
            debris_type=det["class"],
            confidence=det["confidence"],
            bounding_box_json=json.dumps(det["bbox"]),
            debris_density_score=result["debris_density_score"],
            summary=result["summary"]
        )
        db.add(db_det)
    db.commit()
    return result
