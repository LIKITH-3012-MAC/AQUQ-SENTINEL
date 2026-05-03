import uuid
import random
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app import models_ai, models, config

# Database setup
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/aquasentinel"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def seed_intelligence():
    db = SessionLocal()
    try:
        print("[SEED] Starting AI Intelligence Seeding...")
        
        # 1. Create simulated detections
        classes = ["plastic_waste", "ghost_net", "floating_debris", "oil_patch", "algae_cluster"]
        severities = ["Low", "Medium", "High", "Critical"]
        
        detections = []
        for i in range(25):
            is_today = random.random() > 0.4
            created_at = datetime.utcnow() if is_today else datetime.utcnow() - timedelta(days=random.randint(1, 5))
            
            det = models_ai.AIDebrisDetection(
                id=uuid.uuid4(),
                source_type="satellite",
                debris_class=random.choice(classes),
                confidence_score=random.uniform(0.75, 0.98),
                severity=random.choice(severities),
                latitude=17.6868 + random.uniform(-0.1, 0.1),
                longitude=83.2185 + random.uniform(-0.1, 0.1),
                is_simulated=True,
                inference_mode="simulated",
                created_at=created_at
            )
            detections.append(det)
            db.add(det)
            
        print(f"[SEED] Added {len(detections)} simulated detections.")

        # 2. Create ecosystem signals
        ecosystems = ["coral_reef", "mangrove", "seagrass", "open_water"]
        signals = []
        for i in range(10):
            sig = models_ai.EcosystemMonitoringRecord(
                id=uuid.uuid4(),
                region_type=random.choice(ecosystems),
                confidence_score=random.uniform(0.8, 0.95),
                latitude=17.6868 + random.uniform(-0.2, 0.2),
                longitude=83.2185 + random.uniform(-0.2, 0.2),
                ecosystem_health_index=random.uniform(30, 95),
                is_simulated=True,
                created_at=datetime.utcnow() - timedelta(hours=random.randint(1, 24))
            )
            signals.append(sig)
            db.add(sig)

        print(f"[SEED] Added {len(signals)} ecosystem signals.")
        db.commit()
        print("[SEED] Intelligence seeding complete.")
        
    except Exception as e:
        print(f"[SEED] ERROR: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_intelligence()
