"""
AquaSentinel AI — Legacy Ecosystem Routes (Fixed)
Ecosystem segmentation results are now returned directly without DB storage
since EcosystemSegment model doesn't exist.
For AI Intelligence Layer ecosystem monitoring, use /api/ai/detect/ecosystem routes.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, auth, database
from ..services import ecosystem_segmenter

router = APIRouter(prefix="/api/ecosystem", tags=["ecosystem"])

@router.post("/segment/{image_id}")
def run_ecosystem_segmentation(
    image_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Run ecosystem segmentation on an uploaded image."""
    image = db.query(models.UploadedImage).filter(models.UploadedImage.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    result = ecosystem_segmenter.segment_ecosystem(image.image_path)
    return {
        "success": True,
        "image_id": image_id,
        "segmentation": result,
        "message": "Ecosystem segmentation complete."
    }
