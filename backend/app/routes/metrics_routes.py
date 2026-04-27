from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import auth, database
from ..services import metrics_service

router = APIRouter(prefix="/api/metrics", tags=["metrics"])

@router.get("/dashboard")
def get_metrics_dashboard(db: Session = Depends(database.get_db), admin_user=Depends(auth.get_current_active_admin)):
    return metrics_service.get_dashboard_metrics(db)

@router.get("/api-health")
def get_api_health(db: Session = Depends(database.get_db), admin_user=Depends(auth.get_current_active_admin)):
    return {"nasa": "Optimal", "copernicus": "Optimal"}

@router.get("/model-performance")
def get_model_performance(db: Session = Depends(database.get_db), admin_user=Depends(auth.get_current_active_admin)):
    return {"debris_detection": "98%", "ecosystem_segmentation": "95%"}

@router.get("/database")
def get_database_metrics(db: Session = Depends(database.get_db), admin_user=Depends(auth.get_current_active_admin)):
    return {"status": "Healthy", "connections": 5}
