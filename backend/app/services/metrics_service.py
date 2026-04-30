from sqlalchemy.orm import Session
from .. import models
import random

def get_dashboard_metrics(db: Session):
    """
    Get metrics for Admin Control Tower.
    """
    total_users = db.query(models.User).count()
    total_assessments = db.query(models.RiskScore).count()
    total_images = db.query(models.UploadedImage).count()
    critical_alerts = db.query(models.Alert).filter(models.Alert.severity == "CRITICAL", models.Alert.status == "active").count()
    
    # Mocking some external API metrics for the dashboard
    nasa_requests_today = random.randint(10, 150)
    wave_requests_today = random.randint(5, 100)
    
    return {
        "total_users": total_users,
        "total_assessments": total_assessments,
        "total_images": total_images,
        "critical_alerts": critical_alerts,
        "nasa_requests_today": nasa_requests_today,
        "wave_requests_today": wave_requests_today,
        "api_health": "Optimal",
        "model_status": "Online"
    }
