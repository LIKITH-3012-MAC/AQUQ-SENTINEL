import sys
import os
import uuid
import random
from datetime import datetime, timedelta

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.database import SessionLocal, engine
from app import models, auth

def seed_data():
    db = SessionLocal()
    try:
        print("--- AquaSentinel DB Seeding Sequence ---")
        
        # 1. Create Risk Scores (Heatmap)
        if db.query(models.RiskScore).count() == 0:
            print("[INFO] Seeding Risk Heatmap...")
            locations = [
                (17.3850, 78.4867, "Hyderabad Sector"),
                (13.0827, 80.2707, "Chennai Coast"),
                (19.0760, 72.8777, "Mumbai Harbor"),
                (22.5726, 88.3639, "Kolkata Delta"),
                (8.1775, 77.4304, "Kanyakumari Tip")
            ]
            for lat, lon, name in locations:
                score = round(random.uniform(30.0, 95.0), 1)
                level = "CRITICAL" if score > 80 else "HIGH" if score > 60 else "MEDIUM"
                risk = models.RiskScore(
                    latitude=lat,
                    longitude=lon,
                    score=score,
                    level=level,
                    explanation=f"Detected anomaly in {name}. High concentration of non-organic debris.",
                    recommended_action="Deploy regional drone survey.",
                    factors={"debris": score, "sst_anomaly": random.uniform(0.5, 2.0)}
                )
                db.add(risk)
            print("[SUCCESS] Risk Heatmap Seeded.")

        # 2. Create Alerts
        if db.query(models.Alert).count() == 0:
            print("[INFO] Seeding Tactical Alerts...")
            alert = models.Alert(
                title="Massive Plastic Patch Detected",
                message="Satellite MODIS-4 confirmed a 5km wide plastic patch moving towards Chennai Coast.",
                severity="Critical",
                latitude=13.0827,
                longitude=80.2707,
                status="active"
            )
            db.add(alert)
            print("[SUCCESS] Alerts Seeded.")

        # 3. Create initial reports
        if db.query(models.MarineReport).count() == 0:
            print("[INFO] Seeding Initial Incident Reports...")
            # Need a user ID for the report
            admin = db.query(models.User).filter(models.User.email == "admin@aquasentinel.ai").first()
            if admin:
                report = models.MarineReport(
                    user_id=admin.id,
                    title="Ghost Net Cluster",
                    description="Submerged fishing nets detected near reef system.",
                    latitude=13.1,
                    longitude=80.3,
                    report_type="plastic_waste",
                    severity="High",
                    status="verified"
                )
                db.add(report)
            print("[SUCCESS] Reports Seeded.")

        db.commit()
        print("--- Seeding Complete ---")
    except Exception as e:
        print(f"[ERROR] Seeding failed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
