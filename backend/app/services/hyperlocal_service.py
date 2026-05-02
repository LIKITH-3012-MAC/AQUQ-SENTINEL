from sqlalchemy.orm import Session
from sqlalchemy import func
from .. import models
from .ocean_health_service import OceanHealthService
import math

class HyperlocalService:
    @staticmethod
    def get_hyperlocal_intelligence(db: Session, lat: float, lon: float, radius: float = 50.0):
        """
        Aggregate localized intelligence for a specific coordinate.
        Combines Health Score, Nearby Alerts, Hotspots, and Regional Summary.
        """
        # 1. Get Health Score
        health = OceanHealthService.calculate_health_score(db, lat, lon, radius)

        # 2. Get Nearby Alerts (Specific to this region)
        alerts = db.query(models.Alert).filter(
            func.sqrt(
                func.pow(models.Alert.latitude - lat, 2) + 
                func.pow(models.Alert.longitude - lon, 2)
            ) * 111.0 <= radius,
            models.Alert.status == "active"
        ).order_by(models.Alert.created_at.desc()).limit(5).all()

        # 3. Get Recent Nearby Reports
        reports = db.query(models.MarineReport).filter(
            func.sqrt(
                func.pow(models.MarineReport.latitude - lat, 2) + 
                func.pow(models.MarineReport.longitude - lon, 2)
            ) * 111.0 <= radius
        ).order_by(models.MarineReport.created_at.desc()).limit(5).all()

        # 4. Get Total Counts for the region
        total_alerts_count = db.query(models.Alert).filter(
            func.sqrt(
                func.pow(models.Alert.latitude - lat, 2) + 
                func.pow(models.Alert.longitude - lon, 2)
            ) * 111.0 <= radius,
            models.Alert.status == "active"
        ).count()

        total_reports_count = db.query(models.MarineReport).filter(
            func.sqrt(
                func.pow(models.MarineReport.latitude - lat, 2) + 
                func.pow(models.MarineReport.longitude - lon, 2)
            ) * 111.0 <= radius
        ).count()

        # 5. Generate Regional Intelligence Summary
        summary = ""
        if health['score'] < 40:
            summary = f"CRITICAL: Multiple high-density debris zones detected near {lat}, {lon}. Risk is accelerating."
        elif health['score'] < 60:
            summary = f"Watchlist: Increasing marine activity detected. Monitor coastal drift paths for possible accumulation."
        else:
            summary = f"Stable: Marine conditions are within normal parameters for this coastal sector."

        return {
            "location": {"lat": lat, "lon": lon},
            "radius_km": radius,
            "health_score": health,
            "alerts": alerts,
            "total_alerts_count": total_alerts_count,
            "recent_reports": reports,
            "total_reports_count": total_reports_count,
            "intelligence_summary": summary,
            "hotspot_status": "HIGH" if health['score'] < 50 else "LOW"
        }
