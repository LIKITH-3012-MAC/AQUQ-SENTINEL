"""
AquaSentinel AI Detection Routes
Full pipeline: image upload → AI inference → DB persistence → map/dashboard/alert integration.
"""
import os
import shutil
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, timedelta
from .. import models, models_ai, schemas_ai, auth, database, config
from ..services import ai_debris_detection_service, ai_alert_engine

router = APIRouter(prefix="/api/ai/detect", tags=["ai-detection"])


@router.post("/image", response_model=schemas_ai.AIInferenceResult)
async def detect_from_image(
    file: UploadFile = File(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    location_label: Optional[str] = Form(None),
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Upload a marine image and run AI debris detection inference.
    Full pipeline: upload → preprocess → inference → DB → alerts → response.
    """
    # 1. Save image
    os.makedirs(config.settings.UPLOAD_DIR, exist_ok=True)
    safe_filename = f"ai_detect_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
    file_location = os.path.join(config.settings.UPLOAD_DIR, safe_filename)
    with open(file_location, "wb+") as f:
        shutil.copyfileobj(file.file, f)

    # 2. Create uploaded image record
    db_image = models.UploadedImage(
        user_id=current_user.id,
        filename=safe_filename,
        original_filename=file.filename,
        image_path=file_location,
        status="ai_processing"
    )
    db.add(db_image)
    db.commit()
    db.refresh(db_image)

    # 3. Run AI inference
    detections, eco_records = ai_debris_detection_service.run_inference(
        db=db,
        image_id=db_image.id,
        user_id=current_user.id,
        latitude=latitude,
        longitude=longitude,
        source_type="user_upload",
        is_simulated=False,
        location_label=location_label
    )

    # 4. Evaluate alert thresholds
    alerts_created = ai_alert_engine.evaluate_and_create_alerts(
        db=db,
        detections=detections,
        user_id=current_user.id,
        is_simulated=False
    )

    # 5. Check cluster alert
    alerts_created += ai_alert_engine.check_cluster_alert(
        db=db,
        latitude=latitude,
        longitude=longitude
    )

    # 6. Update image status
    db_image.status = "ai_complete"
    db.commit()

    # 7. Log activity
    activity = models.UserActivityTimeline(
        user_id=current_user.id,
        event_type="ai_detection",
        description=f"AI debris detection completed: {len(detections)} detections from uploaded image.",
        metadata_json={
            "image_id": db_image.id,
            "detections_count": len(detections),
            "alerts_created": alerts_created,
            "classes": [d.debris_class for d in detections]
        }
    )
    db.add(activity)
    db.commit()

    return schemas_ai.AIInferenceResult(
        success=True,
        detections=[schemas_ai.AIDetectionResponse.model_validate(d) for d in detections],
        ecosystem_records=[schemas_ai.EcosystemMonitoringResponse.model_validate(e) for e in eco_records],
        alerts_created=alerts_created,
        message=f"AI inference complete: {len(detections)} detections, {len(eco_records)} ecosystem records, {alerts_created} alerts generated."
    )


@router.post("/simulate", response_model=schemas_ai.AIInferenceResult)
async def create_simulated_detection(
    req: schemas_ai.AISimulationDetectionRequest,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Create simulated AI detection records (admin or demo mode).
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required for simulation detections.")

    detections, eco_records = ai_debris_detection_service.run_inference(
        db=db,
        image_id=None,
        user_id=current_user.id,
        latitude=req.latitude,
        longitude=req.longitude,
        source_type="admin_simulation",
        is_simulated=True,
        scenario_id=req.scenario_id,
        location_label=req.location_label,
        forced_class=req.debris_class,
        forced_severity=req.severity,
        count=req.count
    )

    alerts_created = ai_alert_engine.evaluate_and_create_alerts(
        db=db,
        detections=detections,
        user_id=current_user.id,
        is_simulated=True
    )

    return schemas_ai.AIInferenceResult(
        success=True,
        detections=[schemas_ai.AIDetectionResponse.model_validate(d) for d in detections],
        ecosystem_records=[schemas_ai.EcosystemMonitoringResponse.model_validate(e) for e in eco_records],
        alerts_created=alerts_created,
        message=f"Simulated AI inference: {len(detections)} detections, {alerts_created} alerts."
    )


@router.get("/results", response_model=List[schemas_ai.AIDetectionResponse])
def get_detections(
    limit: int = Query(50, le=200),
    source_type: Optional[str] = None,
    debris_class: Optional[str] = None,
    min_confidence: Optional[float] = None,
    severity: Optional[str] = None,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Retrieve AI detection results with filtering."""
    query = db.query(models_ai.AIDebrisDetection).order_by(
        models_ai.AIDebrisDetection.created_at.desc()
    )

    if source_type:
        query = query.filter(models_ai.AIDebrisDetection.source_type == source_type)
    if debris_class:
        query = query.filter(models_ai.AIDebrisDetection.debris_class == debris_class)
    if min_confidence:
        query = query.filter(models_ai.AIDebrisDetection.confidence_score >= min_confidence)
    if severity:
        query = query.filter(models_ai.AIDebrisDetection.severity == severity)

    return query.limit(limit).all()


@router.get("/results/{detection_id}", response_model=schemas_ai.AIDetectionResponse)
def get_detection_detail(
    detection_id: str,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Get full detail for a single detection."""
    detection = db.query(models_ai.AIDebrisDetection).filter(
        models_ai.AIDebrisDetection.id == detection_id
    ).first()
    if not detection:
        raise HTTPException(status_code=404, detail="Detection not found")
    return detection


@router.get("/evidence/{detection_id}", response_model=List[schemas_ai.DetectionEvidenceResponse])
def get_detection_evidence(
    detection_id: str,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Get evidence records for a detection."""
    return db.query(models_ai.DetectionEvidence).filter(
        models_ai.DetectionEvidence.detection_id == detection_id
    ).all()


# ========= Dashboard / Summary Routes =========

@router.get("/dashboard", response_model=schemas_ai.AIDashboardSummary)
def get_ai_dashboard_summary(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Get AI intelligence dashboard summary."""
    today = datetime.utcnow().replace(hour=0, minute=0, second=0)

    total = db.query(func.count(models_ai.AIDebrisDetection.id)).scalar() or 0
    today_count = db.query(func.count(models_ai.AIDebrisDetection.id)).filter(
        models_ai.AIDebrisDetection.created_at >= today
    ).scalar() or 0

    high_conf = db.query(func.count(models_ai.AIDebrisDetection.id)).filter(
        models_ai.AIDebrisDetection.confidence_score >= 0.85
    ).scalar() or 0

    avg_conf = db.query(func.avg(models_ai.AIDebrisDetection.confidence_score)).scalar() or 0.0

    eco_alerts = db.query(func.count(models_ai.EcosystemMonitoringRecord.id)).filter(
        models_ai.EcosystemMonitoringRecord.ecosystem_health_index < 50
    ).scalar() or 0

    alert_conversions = db.query(func.count(models_ai.DetectionAlertLink.id)).scalar() or 0

    # Class distribution
    class_counts = db.query(
        models_ai.AIDebrisDetection.debris_class,
        func.count(models_ai.AIDebrisDetection.id)
    ).group_by(models_ai.AIDebrisDetection.debris_class).all()
    class_dist = {c: n for c, n in class_counts}

    # Latest detections
    latest = db.query(models_ai.AIDebrisDetection).order_by(
        models_ai.AIDebrisDetection.created_at.desc()
    ).limit(10).all()

    # Ecosystem signals
    eco_signals = db.query(models_ai.EcosystemMonitoringRecord).order_by(
        models_ai.EcosystemMonitoringRecord.created_at.desc()
    ).limit(5).all()

    return schemas_ai.AIDashboardSummary(
        ai_detections_today=today_count,
        ai_detections_total=total,
        high_confidence_zones=high_conf,
        avg_detection_confidence=round(float(avg_conf), 4),
        ecosystem_alerts=eco_alerts,
        detection_to_alert_conversions=alert_conversions,
        debris_class_distribution=class_dist,
        latest_detections=[schemas_ai.AIDetectionSummary.model_validate(d) for d in latest],
        ecosystem_signals=[schemas_ai.EcosystemMonitoringResponse.model_validate(e) for e in eco_signals]
    )


# ========= Map Overlay Routes =========

@router.get("/map/overlays", response_model=schemas_ai.AIMapOverlayData)
def get_ai_map_overlays(
    limit: int = Query(100, le=500),
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Get all AI detection data formatted for map overlay rendering."""
    detections = db.query(models_ai.AIDebrisDetection).order_by(
        models_ai.AIDebrisDetection.created_at.desc()
    ).limit(limit).all()

    eco_regions = db.query(models_ai.EcosystemMonitoringRecord).order_by(
        models_ai.EcosystemMonitoringRecord.created_at.desc()
    ).limit(50).all()

    # Build heatmap points [lat, lon, intensity]
    heatmap_points = []
    for d in detections:
        intensity = d.confidence_score * (
            1.5 if d.severity == "Critical" else 1.2 if d.severity == "High" else 1.0
        )
        heatmap_points.append([d.latitude, d.longitude, round(intensity, 2)])

    # Build combined GeoJSON collection
    all_features = []
    for d in detections:
        if d.geojson_data and "features" in d.geojson_data:
            all_features.extend(d.geojson_data["features"])

    geojson_collection = {
        "type": "FeatureCollection",
        "features": all_features
    } if all_features else None

    return schemas_ai.AIMapOverlayData(
        detections=[schemas_ai.AIDetectionSummary.model_validate(d) for d in detections],
        ecosystem_regions=[schemas_ai.EcosystemMonitoringResponse.model_validate(e) for e in eco_regions],
        heatmap_points=heatmap_points,
        geojson_collection=geojson_collection
    )


# ========= Ecosystem Routes =========

@router.get("/ecosystem", response_model=List[schemas_ai.EcosystemMonitoringResponse])
def get_ecosystem_records(
    limit: int = Query(50, le=200),
    region_type: Optional[str] = None,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Get ecosystem monitoring records."""
    query = db.query(models_ai.EcosystemMonitoringRecord).order_by(
        models_ai.EcosystemMonitoringRecord.created_at.desc()
    )
    if region_type:
        query = query.filter(models_ai.EcosystemMonitoringRecord.region_type == region_type)
    return query.limit(limit).all()


# ========= Satellite Tile Inference Placeholder =========

@router.post("/tiles/ingest", response_model=schemas_ai.AITileIngestResponse)
def ingest_satellite_tile(
    req: schemas_ai.AITileIngestRequest,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Satellite tile ingestion endpoint (Phase 2 architecture placeholder).
    Accepts tile bounding box and queues for future inference.
    """
    if current_user.role not in ["admin", "researcher"]:
        raise HTTPException(status_code=403, detail="Researcher/Admin access required")

    return schemas_ai.AITileIngestResponse(
        success=True,
        tile_id=f"tile_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        status="architecture_ready",
        message=(
            f"Tile ingestion architecture ready. "
            f"Bounding box: [{req.min_lat:.4f}, {req.min_lon:.4f}] to [{req.max_lat:.4f}, {req.max_lon:.4f}]. "
            f"Real satellite inference available in Phase 2."
        )
    )
