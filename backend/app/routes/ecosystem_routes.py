from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, auth, database
from ..services import ecosystem_segmenter

router = APIRouter(prefix="/api/ecosystem", tags=["ecosystem"])

@router.post("/segment/{image_id}")
def run_ecosystem_segmentation(image_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    image = db.query(models.UploadedImage).filter(models.UploadedImage.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
        
    result = ecosystem_segmenter.segment_ecosystem(image.image_path)
    
    # Store in DB
    db_seg = models.EcosystemSegment(
        image_id=image.id,
        water_percentage=result["water"],
        coral_percentage=result["coral"],
        algae_percentage=result["algae"],
        debris_percentage=result["debris"],
        turbid_water_percentage=result["turbid_water"],
        ecosystem_degradation_score=result["ecosystem_degradation_score"]
    )
    db.add(db_seg)
    db.commit()
    return result
