from sqlalchemy.orm import Session
from .. import models
import math
from datetime import datetime, timedelta

class HotspotPredictionService:
    @staticmethod
    def predict_drift(db: Session, report_id: int):
        """
        Predict the drift path of debris based on currents and wind.
        Uses a simplified drift model: Drift = (Current_Velocity + 0.03 * Wind_Velocity)
        """
        report = db.query(models.MarineReport).filter(models.MarineReport.id == report_id).first()
        if not report:
            return None

        # Fetch latest environmental data near report
        current = db.query(models.OceanCurrentObservation).filter(
            models.OceanCurrentObservation.latitude.between(report.latitude - 1, report.latitude + 1),
            models.OceanCurrentObservation.longitude.between(report.longitude - 1, report.longitude + 1)
        ).order_by(models.OceanCurrentObservation.created_at.desc()).first()

        wind = db.query(models.WeatherObservation).filter(
            models.WeatherObservation.latitude.between(report.latitude - 1, report.latitude + 1),
            models.WeatherObservation.longitude.between(report.longitude - 1, report.longitude + 1)
        ).order_by(models.WeatherObservation.created_at.desc()).first()

        # Fallback vectors if no real-time data
        u_curr = current.u_velocity if current else 0.2
        v_curr = current.v_velocity if current else 0.1
        u_wind = (wind.wind_speed * math.cos(math.radians(45))) if wind else 5.0
        v_wind = (wind.wind_speed * math.sin(math.radians(45))) if wind else 2.0

        # Drift calculation (m/s)
        u_drift = u_curr + (0.03 * u_wind)
        v_drift = v_curr + (0.03 * v_wind)

        # Convert to degrees per hour (approx)
        # 1 degree lat approx 111,000 meters
        # 1 degree lon approx 111,000 * cos(lat) meters
        d_lat_per_h = (v_drift * 3600) / 111000
        d_lon_per_h = (u_drift * 3600) / (111000 * math.cos(math.radians(report.latitude)))

        # Generate 24h path
        path = []
        for h in range(1, 25):
            path.append({
                "hour": h,
                "lat": report.latitude + (d_lat_per_h * h),
                "lon": report.longitude + (d_lon_per_h * h),
                "timestamp": (datetime.utcnow() + timedelta(hours=h)).isoformat()
            })

        # Store prediction
        prediction = models.HotspotPrediction(
            latitude=path[-1]['lat'],
            longitude=path[-1]['lon'],
            drift_path=path,
            risk_level="High" if report.severity in ["High", "Critical"] else "Medium",
            time_window="Next 24h",
            action_recommendation=f"Intercept at coordinates {round(path[6]['lat'], 4)}, {round(path[6]['lon'], 4)} (T+6h) before drift enters sensitive coastal zone."
        )
        db.add(prediction)
        db.commit()
        db.refresh(prediction)
        
        return prediction

    @staticmethod
    def get_all_predictions(db: Session):
        return db.query(models.HotspotPrediction).order_by(models.HotspotPrediction.created_at.desc()).limit(10).all()
