from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import database, auth, models
from ..services import debris_detector

router = APIRouter(prefix="/api/debris", tags=["debris"])

@router.post("/detect")
def detect_debris(
    report_id: int,
    image_path: str,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Trigger AI debris detection for a report.
    """
    results, avg_density = debris_detector.process_debris_detection(db, report_id, image_path)
    return {
        "detections": results,
        "average_density": avg_density,
        "summary": f"Detected {len(results)} items with average density of {avg_density}%"
    }

