from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from . import models, database, auth, db_fixer
from .routes import (
    auth_routes, dashboard, reports, satellite, 
    weather, ocean, debris, risk, admin_routes,
    chatbot, simulation, alert_routes, image_routes,
    health, hyperlocal, prediction_routes, mission_routes, profile,
    admin_simulation, map_incidents
)

# Auto-create tables (use migrations in real production)
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="AquaSentinel AI Command Center", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    print("--- AquaSentinel AI Boot Sequence Initiated ---")
    db = database.SessionLocal()
    try:
        # Verify DB Connection
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        print("[SUCCESS] Quantum Core: Database Connection Established.")
        
        # Verify/Create Tables
        models.Base.metadata.create_all(bind=database.engine)
        print("[SUCCESS] Systems: PostgreSQL Schema Verified and Synced.")

        # Run schema fixes for missing columns
        db_fixer.fix_database_schema()
        print("[SUCCESS] Systems: Applied schema hot-fixes for simulated intelligence fields.")

        # Ensure system admin exists
        admin = db.query(models.User).filter(models.User.email == "admin@aquasentinel.ai").first()
        if not admin:
            new_admin = models.User(
                full_name="Intelligence Commander",
                email="admin@aquasentinel.ai",
                password_hash=auth.get_password_hash("Admin@2026!"),
                security_question="What is the mission code?",
                security_answer_hash=auth.get_password_hash("ocean-sentinel"),
                role="admin",
                is_active=True,
                is_verified=True
            )
            db.add(new_admin)
            db.commit()
            print("[INFO] Security: Initial Administrator Credentialed.")
        
        print("[READY] AquaSentinel AI Command Center Online.")
    except Exception as e:
        print(f"[CRITICAL ERROR] Core Initialization Failure: {str(e)}")
    finally:
        db.close()

# Include futuristic API routers
app.include_router(auth_routes.router)
app.include_router(dashboard.router)
app.include_router(reports.router)
app.include_router(satellite.router)
app.include_router(weather.router)
app.include_router(ocean.router)
app.include_router(debris.router)
app.include_router(risk.router)
app.include_router(admin_routes.router)
app.include_router(chatbot.router)
app.include_router(simulation.router)
app.include_router(alert_routes.router)
app.include_router(image_routes.router)
app.include_router(health.router)
app.include_router(hyperlocal.router)
app.include_router(prediction_routes.router)
app.include_router(mission_routes.router)
app.include_router(profile.router)
app.include_router(admin_simulation.router)
app.include_router(map_incidents.router)

@app.get("/")
def read_root():
    return {"status": "AquaSentinel AI Command Center v2.0 Online"}
