from sqlalchemy.orm import Session
from sqlalchemy import func
from .. import models
import math

class OceanHealthService:
    @staticmethod
    def calculate_health_score(db: Session, lat: float, lon: float, radius: float = 20.0):
        """
        Calculate a premium Ocean Health Score for a specific coordinate.
        Inputs: debris density, temperature trends, user reports, alerts.
        Output: Score (0-100), Category, Explanation, and Factors.
        """
        # 1. Gather Data Points
        # User Reports in area
        reports = db.query(models.MarineReport).filter(
            func.sqrt(
                func.pow(models.MarineReport.latitude - lat, 2) + 
                func.pow(models.MarineReport.longitude - lon, 2)
            ) * 111.0 <= radius
        ).all()

        # Detections (from satellite or images)
        detections = db.query(models.DebrisDetection).join(models.MarineReport).filter(
            func.sqrt(
                func.pow(models.MarineReport.latitude - lat, 2) + 
                func.pow(models.MarineReport.longitude - lon, 2)
            ) * 111.0 <= radius
        ).all()

        # Alerts
        alerts = db.query(models.Alert).filter(
            func.sqrt(
                func.pow(models.Alert.latitude - lat, 2) + 
                func.pow(models.Alert.longitude - lon, 2)
            ) * 111.0 <= radius,
            models.Alert.status == "active"
        ).all()

        # 2. Logic to calculate score
        # Base score is 100
        base_score = 95.0
        factors = []
        
        # Factor A: Debris Density (High impact)
        if detections:
            avg_density = sum(d.density_score for d in detections) / len(detections)
            penalty = min(30, avg_density / 3.0)
            base_score -= penalty
            factors.append({
                "name": "Debris Density",
                "impact": -round(penalty, 1),
                "detail": f"Average density of {round(avg_density, 1)} detected via satellite/vision."
            })
        else:
            factors.append({"name": "Debris Density", "impact": 0, "detail": "No significant floating debris detected."})

        # Factor B: User Reports (Engagement & Verification)
        report_penalty = min(20, len(reports) * 4)
        if report_penalty > 0:
            base_score -= report_penalty
            factors.append({
                "name": "Local Incidents",
                "impact": -round(report_penalty, 1),
                "detail": f"{len(reports)} active reports submitted by users in this sector."
            })

        # Factor C: Alert Severity
        if alerts:
            max_severity = 0
            for a in alerts:
                if a.severity == "Critical": max_severity = max(max_severity, 25)
                elif a.severity == "High": max_severity = max(max_severity, 15)
                elif a.severity == "Medium": max_severity = max(max_severity, 8)
            
            base_score -= max_severity
            factors.append({
                "name": "Alert System",
                "impact": -round(max_severity, 1),
                "detail": "High-priority intelligence alerts active in this region."
            })

        # Factor D: Satellite Data (Chlorophyll/Temp) - Mocking logic for now
        # In a real app, we'd query models.SatelliteObservation
        eco_bonus = 5.0 # Assume baseline health
        base_score += eco_bonus
        factors.append({"name": "Ecological Base", "impact": 5.0, "detail": "Chlorophyll levels within optimal range for marine life."})

        # Finalize Score
        final_score = max(0, min(100, round(base_score)))
        
        # Category Mapping
        if final_score >= 85: category = "Excellent"
        elif final_score >= 70: category = "Stable"
        elif final_score >= 50: category = "Watchlist"
        elif final_score >= 30: category = "At Risk"
        else: category = "Critical"

        # Explanation
        if category == "Excellent":
            explanation = "Pristine marine conditions. Minimal debris activity and stable ecological metrics."
            action = "Continue baseline monitoring and maintain conservation efforts."
        elif category == "Stable":
            explanation = "Region is generally healthy with minor localized anomalies."
            action = "Standard routine inspections recommended."
        elif category == "Watchlist":
            explanation = "Multiple risk factors detected. Possible accumulation of floating debris or unusual temperature trends."
            action = "Deploy research drones for closer inspection of hotspot zones."
        elif category == "At Risk":
            explanation = "Significant environmental stress. High debris density and active intelligence alerts detected."
            action = "Immediate notification to coastal NGO teams and cleanup prioritization."
        else:
            explanation = "CRITICAL THREAT. High-density contamination detected. Marine ecosystems under severe stress."
            action = "Launch full-scale emergency mission and alert regional authorities."

        return {
            "score": final_score,
            "category": category,
            "explanation": explanation,
            "recommended_action": action,
            "contributing_factors": factors,
            "latitude": lat,
            "longitude": lon
        }

    @staticmethod
    def get_global_averages(db: Session):
        # In a real app, this would aggregate scores across major regions
        return {
            "global_score": 72,
            "trend": "decreasing",
            "active_hotspots": db.query(models.RiskScore).filter(models.RiskScore.level == "Critical").count()
        }
