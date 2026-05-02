from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import database, models, auth
from ..services import hyperlocal_service

router = APIRouter(prefix="/api/hyperlocal", tags=["hyperlocal"])

@router.get("/intelligence")
def get_hyperlocal_data(
    lat: float, 
    lon: float, 
    radius: float = 50.0,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Get hyperlocal marine intelligence for a specific coordinate.
    """
    return hyperlocal_service.get_hyperlocal_intelligence(db, lat, lon, radius)
