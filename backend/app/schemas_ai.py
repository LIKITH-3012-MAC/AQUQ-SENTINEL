"""
AquaSentinel AI Marine Debris & Ecosystem Intelligence Layer
Pydantic Schemas for API Request/Response
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict
from datetime import datetime
from uuid import UUID


# ========= REQUEST SCHEMAS =========

class AIDetectionRequest(BaseModel):
    """Request to run AI detection on an uploaded image."""
    latitude: float = Field(..., description="Latitude of image capture location")
    longitude: float = Field(..., description="Longitude of image capture location")
    location_label: Optional[str] = None


class AISimulationDetectionRequest(BaseModel):
    """Request to create simulated AI detection records."""
    latitude: float
    longitude: float
    debris_class: Optional[str] = None
    severity: Optional[str] = None
    count: int = Field(default=3, ge=1, le=10)
    scenario_id: Optional[UUID] = None
    location_label: Optional[str] = None


class AITileIngestRequest(BaseModel):
    """Request to ingest a satellite tile for future inference."""
    tile_url: Optional[str] = None
    min_lat: float
    min_lon: float
    max_lat: float
    max_lon: float
    source: str = "satellite"


# ========= RESPONSE SCHEMAS =========

class AIDetectionResponse(BaseModel):
    id: UUID
    source_type: str
    source_image_id: Optional[int] = None
    user_id: Optional[UUID] = None
    scenario_id: Optional[UUID] = None
    debris_class: str
    confidence_score: float
    severity: str
    latitude: float
    longitude: float
    location_label: Optional[str] = None
    bbox_like_data: Optional[Dict] = None
    overlay_line_data: Optional[List] = None
    polygon_data: Optional[List] = None
    geojson_data: Optional[Dict] = None
    ecosystem_tags: Optional[Dict] = None
    environmental_impact: Optional[str] = None
    is_simulated: bool = False
    related_alert_id: Optional[int] = None
    related_mission_id: Optional[UUID] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AIDetectionSummary(BaseModel):
    """Compact detection for map overlay rendering."""
    id: UUID
    debris_class: str
    confidence_score: float
    severity: str
    latitude: float
    longitude: float
    bbox_like_data: Optional[Dict] = None
    overlay_line_data: Optional[List] = None
    polygon_data: Optional[List] = None
    geojson_data: Optional[Dict] = None
    is_simulated: bool = False
    source_type: str
    created_at: datetime

    class Config:
        from_attributes = True


class DetectionEvidenceResponse(BaseModel):
    id: UUID
    detection_id: UUID
    file_reference: Optional[str] = None
    raw_output_metadata: Optional[Dict] = None
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class EcosystemMonitoringResponse(BaseModel):
    id: UUID
    detection_id: Optional[UUID] = None
    region_type: str
    confidence_score: float
    latitude: float
    longitude: float
    geo_output: Optional[Dict] = None
    ecosystem_health_index: Optional[float] = None
    notes: Optional[str] = None
    is_simulated: bool = False
    created_at: datetime

    class Config:
        from_attributes = True


class AIDashboardSummary(BaseModel):
    """AI Intelligence dashboard summary."""
    ai_detections_today: int = 0
    ai_detections_total: int = 0
    high_confidence_zones: int = 0
    avg_detection_confidence: float = 0.0
    ecosystem_alerts: int = 0
    detection_to_alert_conversions: int = 0
    debris_class_distribution: Dict[str, int] = {}
    latest_detections: List[AIDetectionSummary] = []
    ecosystem_signals: List[EcosystemMonitoringResponse] = []


class AIMapOverlayData(BaseModel):
    """Complete map overlay data package."""
    detections: List[AIDetectionSummary] = []
    ecosystem_regions: List[EcosystemMonitoringResponse] = []
    heatmap_points: List[List[float]] = []  # [[lat, lon, intensity], ...]
    geojson_collection: Optional[Dict] = None


class AIInferenceResult(BaseModel):
    """Result from AI inference pipeline."""
    success: bool = True
    detections: List[AIDetectionResponse] = []
    ecosystem_records: List[EcosystemMonitoringResponse] = []
    alerts_created: int = 0
    message: str = ""


class AITileIngestResponse(BaseModel):
    """Response from tile ingestion."""
    success: bool = True
    tile_id: Optional[str] = None
    status: str = "queued"
    message: str = "Tile ingestion architecture ready. Real inference available in Phase 2."
