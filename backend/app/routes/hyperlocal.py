from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import database, models, auth
from ..services.hyperlocal_service import HyperlocalService

router = APIRouter(prefix="/api/hyperlocal", tags=["hyperlocal"])

@router.get("/intelligence")
def get_hyperlocal_data(
    lat: float, 
    lon: float, 
    radius: float = 20.0,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Get localized marine intelligence for a specific coordinate.
    Includes health score, alerts, and hotspot summaries.
    """
    return HyperlocalService.get_hyperlocal_intelligence(db, lat, lon, radius)
