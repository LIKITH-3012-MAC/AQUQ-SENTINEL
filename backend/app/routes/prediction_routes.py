from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import database, models, auth, schemas
from ..services.hotspot_prediction_service import HotspotPredictionService

router = APIRouter(prefix="/api/predictions", tags=["predictions"])

@router.get("/hotspots")
def get_all_predictions(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    return HotspotPredictionService.get_all_predictions(db)

@router.post("/trigger/{report_id}")
def trigger_prediction(
    report_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    prediction = HotspotPredictionService.predict_drift(db, report_id)
    if not prediction:
        raise HTTPException(status_code=404, detail="Report not found")
    return prediction
