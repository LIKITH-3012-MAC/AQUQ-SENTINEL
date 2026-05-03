from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from .. import models, models_ai, schemas
from ..services import ai_debris_detection_service, ai_alert_engine
import uuid
import random

def trigger_simulation_effects(db: Session, sim: models.SimulatedIncident, admin_id: uuid.UUID):
    """
    Trigger all side effects of a simulated incident: 
    Alerts, Health Score impact, Missions, etc.
    """
    
    # 1. Create a Simulated Marine Report (for lifecycle & missions)
    report = models.MarineReport(
        user_id=admin_id,
        title=f"SIMULATED: {sim.scenario_title}",
        description=f"[EVALUATION MODE] This is a simulated incident created by Admin. {sim.judge_note or ''}",
        latitude=sim.latitude,
        longitude=sim.longitude,
        report_type=sim.debris_type,
        severity=sim.severity,
        status="Submitted",
        is_simulated=True,
        simulation_id=sim.id,
        ai_analysis={
            "suggested_category": sim.debris_type.title(),
            "urgency": sim.severity,
            "possible_impact": "Simulated impact for evaluation purposes.",
            "recommended_action": "Demo cleanup workflow.",
            "confidence": 100.0,
            "is_demo": True
        }
    )
    db.add(report)
    db.flush() # Flush to get ID if needed, though commit handles it
    db.commit()
    db.refresh(report)

    # 2. Add lifecycle entry
    update = models.IncidentUpdate(
        report_id=report.id,
        status="Submitted",
        notes=f"SIMULATED incident initialized for judge evaluation. Severity: {sim.severity}.",
        updated_by=admin_id
    )
    db.add(update)

    # 3. Create Demo Alerts if enabled
    if sim.alert_broadcast_enabled:
        alert = models.Alert(
            title=sim.message_title or f"⚠️ [SIMULATED] Judge Evaluation: {sim.scenario_title}",
            message=sim.message_body or f"DEMO MODE: High density {sim.debris_type} activity simulated near your monitored zone. (Evaluation Purposes Only)",
            severity=sim.severity,
            latitude=sim.latitude,
            longitude=sim.longitude,
            verified_by_admin=True,
            status="active",
            target_scope="global", # Broadcast to all
            is_simulated=True,
            simulation_id=sim.id,
            related_scenario_id=sim.id
        )
        db.add(alert)

    # 4. Create Simulated Map Event (Persistent marker)
    map_event = models.SimulatedMapEvent(
        simulation_scenario_id=sim.id,
        latitude=sim.latitude,
        longitude=sim.longitude,
        marker_type="hotspot",
        severity=sim.severity,
        radius_km=sim.affected_radius,
        is_active=True
    )
    db.add(map_event)

    # 5. Impact Health Score if enabled
    if sim.health_impact_enabled:
        # Create a new local health score entry that is lower
        score_impact = random.randint(15, 30) if sim.severity == "High" else 10
        base_score = 75
        new_score = max(5, base_score - score_impact)
        
        health_score = models.OceanHealthScore(
            latitude=sim.latitude,
            longitude=sim.longitude,
            region_name=f"SIMULATED {sim.scenario_title} ZONE",
            score=new_score,
            category="At Risk" if new_score < 40 else "Watchlist",
            explanation=f"SIMULATED IMPACT: This score has been temporarily lowered for evaluation due to a simulated {sim.debris_type} event.",
            contributing_factors={
                "debris_density": sim.density_score,
                "is_simulated": True,
                "simulation_id": str(sim.id)
            },
            recommended_action="Resolve simulation to restore baseline health metrics."
        )
        db.add(health_score)

    # 5. Create Mission if enabled
    if sim.mission_flow_enabled:
        mission = models.Mission(
            report_id=report.id,
            title=f"MISSION [DEMO]: {sim.scenario_title} Cleanup",
            description=f"EVALUATION WORKFLOW: This mission is a simulation of the NGO/Volunteer response to a {sim.debris_type} threat.",
            urgency=sim.severity,
            status="Pending",
            recommended_equipment="Surface Skimmers, Containment Booms (SIMULATED)",
            checklist=[
                {"task": "Initialize tactical team (Simulated)", "completed": False},
                {"task": "Deploy containment (Simulated)", "completed": False},
                {"task": "Extract debris (Simulated)", "completed": False}
            ],
            is_simulated=True,
            simulation_id=sim.id
        )
        db.add(mission)

    # 6. Generate AI Debris Detection Records (NEW — AI Intelligence Layer)
    try:
        ai_detections, eco_records = ai_debris_detection_service.run_inference(
            db=db,
            image_id=None,
            user_id=admin_id,
            latitude=sim.latitude,
            longitude=sim.longitude,
            source_type="admin_simulation",
            is_simulated=True,
            scenario_id=sim.id,
            location_label=f"SIMULATED: {sim.scenario_title}",
            forced_class=_map_debris_type_to_class(sim.debris_type),
            forced_severity=sim.severity,
            count=random.randint(2, 5)
        )

        # 7. Create AI Alerts from detections
        ai_alert_engine.evaluate_and_create_alerts(
            db=db,
            detections=ai_detections,
            user_id=admin_id,
            is_simulated=True
        )
    except Exception as e:
        print(f"[WARN] AI Detection generation during simulation failed: {e}")

    db.commit()
    return report.id


def _map_debris_type_to_class(debris_type: str) -> str:
    """Map simulation debris_type to AI detection class."""
    mapping = {
        "plastic": "plastic_waste",
        "oil": "oil_patch",
        "net": "ghost_net",
        "ghost_net": "ghost_net",
        "algae": "algae_cluster",
        "debris": "floating_debris",
        "floating_debris": "floating_debris",
        "plastic_waste": "plastic_waste",
        "oil_patch": "oil_patch",
        "algae_cluster": "algae_cluster"
    }
    return mapping.get(debris_type.lower(), "unknown_marine_hazard")

def clear_all_simulations(db: Session):
    """
    Clear all demo data using strict simulation flags.
    """
    # 1. Purge AI intelligence layer simulation data
    db.query(models_ai.DetectionAlertLink).filter(
        models_ai.DetectionAlertLink.detection_id.in_(
            db.query(models_ai.AIDebrisDetection.id).filter(models_ai.AIDebrisDetection.is_simulated == True)
        )
    ).delete(synchronize_session=False)
    db.query(models_ai.DetectionMissionLink).filter(
        models_ai.DetectionMissionLink.detection_id.in_(
            db.query(models_ai.AIDebrisDetection.id).filter(models_ai.AIDebrisDetection.is_simulated == True)
        )
    ).delete(synchronize_session=False)
    db.query(models_ai.DetectionEvidence).filter(
        models_ai.DetectionEvidence.detection_id.in_(
            db.query(models_ai.AIDebrisDetection.id).filter(models_ai.AIDebrisDetection.is_simulated == True)
        )
    ).delete(synchronize_session=False)
    db.query(models_ai.EcosystemMonitoringRecord).filter(
        models_ai.EcosystemMonitoringRecord.is_simulated == True
    ).delete(synchronize_session=False)
    db.query(models_ai.AIDebrisDetection).filter(
        models_ai.AIDebrisDetection.is_simulated == True
    ).delete(synchronize_session=False)

    # 2. Purge simulation scenarios
    db.query(models.SimulatedIncident).delete(synchronize_session=False)
    db.query(models.SimulatedMapEvent).delete(synchronize_session=False)
    db.query(models.AlertBroadcastLog).delete(synchronize_session=False)
    
    # 3. Purge simulated entities
    db.query(models.Alert).filter(models.Alert.is_simulated == True).delete(synchronize_session=False)
    db.query(models.Mission).filter(models.Mission.is_simulated == True).delete(synchronize_session=False)
    db.query(models.MarineReport).filter(models.MarineReport.is_simulated == True).delete(synchronize_session=False)
    db.query(models.RiskScore).filter(models.RiskScore.is_simulated == True).delete(synchronize_session=False)
    
    # 4. Handle OceanHealthScore which uses JSON for simulation flag
    db.query(models.OceanHealthScore).filter(models.OceanHealthScore.region_name.like("SIMULATED%")).delete(synchronize_session=False)
    
    db.commit()
    return True
