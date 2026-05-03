"""
AquaSentinel AI — Legacy Detection Routes (Fixed)
Now properly wired to existing DebrisDetection model.
For AI Intelligence Layer detections, use /api/ai/detect routes.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, auth, database
from ..services import debris_detector

router = APIRouter(prefix="/api/detect", tags=["detection"])

@router.post("/debris/{report_id}")
def run_debris_detection(
    report_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Run legacy debris detection for a report (uses existing DebrisDetection model)."""
    report = db.query(models.MarineReport).filter(models.MarineReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    if not report.image_url:
        raise HTTPException(status_code=400, detail="Report has no attached image for detection")

    results, avg_density = debris_detector.process_debris_detection(db, report_id, report.image_url or "")

    return {
        "success": True,
        "report_id": report_id,
        "detections": len(results),
        "avg_density": avg_density,
        "message": f"Debris detection complete: {len(results)} objects identified."
    }
