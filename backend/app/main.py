from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from . import models, database, auth, schemas
# We'll import routers later as we build them

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="AquaSentinel AI", version="1.0.0")

# CORS setup for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for local dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Seed database on startup
@app.on_event("startup")
def startup_event():
    db = database.SessionLocal()
    # Check if admin exists
    admin = db.query(models.User).filter(models.User.email == "admin@aquasentinel.ai").first()
    if not admin:
        new_admin = models.User(
            name="System Admin",
            email="admin@aquasentinel.ai",
            password_hash=auth.get_password_hash("Admin@123"),
            role="admin"
        )
        db.add(new_admin)
    
    # Check if user exists
    user = db.query(models.User).filter(models.User.email == "user@aquasentinel.ai").first()
    if not user:
        new_user = models.User(
            name="Demo User",
            email="user@aquasentinel.ai",
            password_hash=auth.get_password_hash("User@123"),
            role="user"
        )
        db.add(new_user)
    
    db.commit()
    db.close()

from .routes import (
    health, auth_routes, user_routes, admin_routes, image_routes,
    detection_routes, ecosystem_routes, nasa_routes, wave_routes,
    risk_routes, alert_routes, report_routes, metrics_routes
)

app.include_router(health.router)
app.include_router(auth_routes.router)
app.include_router(user_routes.router)
app.include_router(admin_routes.router)
app.include_router(image_routes.router)
app.include_router(detection_routes.router)
app.include_router(ecosystem_routes.router)
app.include_router(nasa_routes.router)
app.include_router(wave_routes.router)
app.include_router(risk_routes.router)
app.include_router(alert_routes.router)
app.include_router(report_routes.router)
app.include_router(metrics_routes.router)
