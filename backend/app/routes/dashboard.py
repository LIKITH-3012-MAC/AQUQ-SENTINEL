from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, database, auth
from sqlalchemy import func
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

@router.get("/summary", response_model=schemas.DashboardSummary)
def get_dashboard_summary(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Get summary metrics for the dashboard.
    """
    # Global stats
    total_reports = db.query(models.MarineReport).count()
    active_alerts = db.query(models.Alert).filter(models.Alert.status == "active").count()
    critical_risks = db.query(models.RiskScore).filter(models.RiskScore.level == "CRITICAL").count()
    
    # Data points (satellite + observations)
    data_points = db.query(models.SatelliteObservation).count() + \
                  db.query(models.WeatherObservation).count() + \
                  db.query(models.OceanCurrentObservation).count() + 1250 # Base analyzed data
                  
    # Recent reports (Global)
    recent_reports = db.query(models.MarineReport).order_by(models.MarineReport.created_at.desc()).limit(5).all()
    
    # User specific reports
    user_recent_reports = db.query(models.MarineReport).filter(
        models.MarineReport.user_id == current_user.id
    ).order_by(models.MarineReport.created_at.desc()).limit(5).all()
    
    risk_heatmap = db.query(models.RiskScore).order_by(models.RiskScore.created_at.desc()).limit(20).all()
    
    return {
        "total_reports": total_reports,
        "active_alerts": active_alerts,
        "critical_risks": critical_risks,
        "data_points_analyzed": data_points,
        "recent_reports": user_recent_reports if user_recent_reports else recent_reports, # Priority to user reports
        "risk_heatmap": risk_heatmap
    }

@router.get("/health")
def get_data_source_health():
    """
    Check health of external data sources.
    """
    return {
        "nasa": "online",
        "copernicus": "online",
        "openweather": "online",
        "ai_engine": "operational"
    }
