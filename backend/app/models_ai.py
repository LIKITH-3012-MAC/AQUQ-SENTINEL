"""
AquaSentinel AI Marine Debris & Ecosystem Intelligence Layer
Database Models — Production-Grade Schema
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid
from .database import Base


class AIDebrisDetection(Base):
    """
    Primary AI detection record. Every image inference, simulation detection,
    or future satellite tile detection creates a record here.
    """
    __tablename__ = "ai_debris_detections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_type = Column(String, nullable=False)  # 'user_upload', 'admin_simulation', 'satellite_tile'
    source_image_id = Column(Integer, ForeignKey("uploaded_images.id", ondelete="SET NULL"), nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    scenario_id = Column(UUID(as_uuid=True), ForeignKey("simulated_incidents.id", ondelete="SET NULL"), nullable=True)
    debris_class = Column(String, nullable=False)  # plastic_waste, ghost_net, floating_debris, oil_patch, algae_cluster, unknown_marine_hazard
    confidence_score = Column(Float, nullable=False)
    severity = Column(String, nullable=False)  # Low, Medium, High, Critical
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    location_label = Column(String, nullable=True)
    bbox_like_data = Column(JSONB, nullable=True)  # {"min_lat": .., "min_lon": .., "max_lat": .., "max_lon": ..}
    overlay_line_data = Column(JSONB, nullable=True)  # [{"lat": .., "lon": ..}, ...]  debris trail line
    polygon_data = Column(JSONB, nullable=True)  # [{"lat": .., "lon": ..}, ...]  contour polygon
    geojson_data = Column(JSONB, nullable=True)  # Full GeoJSON FeatureCollection
    ecosystem_tags = Column(JSONB, nullable=True)  # {"coral_region": 0.3, "algae_region": 0.5, ...}
    environmental_impact = Column(Text, nullable=True)
    is_simulated = Column(Boolean, default=False)
    model_version = Column(String, nullable=True) # e.g. "yolov8n-v1"
    inference_mode = Column(String, default="simulated") # "simulated" or "real"
    related_alert_id = Column(Integer, ForeignKey("alerts.id", ondelete="SET NULL"), nullable=True)
    related_mission_id = Column(UUID(as_uuid=True), ForeignKey("missions.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class DetectionEvidence(Base):
    """
    Supporting evidence for an AI detection — raw model output, metadata, notes.
    """
    __tablename__ = "detection_evidence"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    detection_id = Column(UUID(as_uuid=True), ForeignKey("ai_debris_detections.id", ondelete="CASCADE"), nullable=False)
    file_reference = Column(String, nullable=True)
    raw_output_metadata = Column(JSONB, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class DetectionAlertLink(Base):
    """
    Links an AI detection to an alert it triggered.
    """
    __tablename__ = "detection_alert_links"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    detection_id = Column(UUID(as_uuid=True), ForeignKey("ai_debris_detections.id", ondelete="CASCADE"), nullable=False)
    alert_id = Column(Integer, ForeignKey("alerts.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class DetectionMissionLink(Base):
    """
    Links an AI detection to a mission it contributed to.
    """
    __tablename__ = "detection_mission_links"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    detection_id = Column(UUID(as_uuid=True), ForeignKey("ai_debris_detections.id", ondelete="CASCADE"), nullable=False)
    mission_id = Column(UUID(as_uuid=True), ForeignKey("missions.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class EcosystemMonitoringRecord(Base):
    """
    Ecosystem classification records from AI analysis.
    """
    __tablename__ = "ecosystem_monitoring_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    detection_id = Column(UUID(as_uuid=True), ForeignKey("ai_debris_detections.id", ondelete="SET NULL"), nullable=True)
    region_type = Column(String, nullable=False)  # coral_region, algae_region, water_region, stressed_zone, sensitive_area, polluted_zone
    confidence_score = Column(Float, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    geo_output = Column(JSONB, nullable=True)  # Polygon/region data
    ecosystem_health_index = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    is_simulated = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
