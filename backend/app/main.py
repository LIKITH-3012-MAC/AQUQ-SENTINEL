from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from . import models, database, auth
from .routes import (
    auth_routes, dashboard, reports, satellite, 
    weather, ocean, debris, risk, admin_routes,
    chatbot, simulation
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
    db = database.SessionLocal()
    # Ensure system admin exists
    admin = db.query(models.User).filter(models.User.email == "admin@aquasentinel.ai").first()
    if not admin:
        new_admin = models.User(
            name="Intelligence Commander",
            email="admin@aquasentinel.ai",
            password_hash=auth.get_password_hash("Admin@2026!"),
            role="admin"
        )
        db.add(new_admin)
        db.commit()
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

@app.get("/")
def read_root():
    return {"status": "AquaSentinel AI Command Center v2.0 Online"}
