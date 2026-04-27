from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="user") # 'user' or 'admin'
    status = Column(String, default="active") # 'active' or 'suspended'
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class UploadedImage(Base):
    __tablename__ = "uploaded_images"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    image_path = Column(String, nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String, default="pending") # 'pending', 'processed', 'failed'

class DebrisDetection(Base):
    __tablename__ = "debris_detections"

    id = Column(Integer, primary_key=True, index=True)
    image_id = Column(Integer, ForeignKey("uploaded_images.id"))
    debris_type = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)
    bounding_box_json = Column(String, nullable=False) # Store JSON string
    debris_density_score = Column(Float, nullable=False)
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class EcosystemSegment(Base):
    __tablename__ = "ecosystem_segments"

    id = Column(Integer, primary_key=True, index=True)
    image_id = Column(Integer, ForeignKey("uploaded_images.id"))
    water_percentage = Column(Float, nullable=False)
    coral_percentage = Column(Float, nullable=False)
    algae_percentage = Column(Float, nullable=False)
    debris_percentage = Column(Float, nullable=False)
    turbid_water_percentage = Column(Float, nullable=False)
    ecosystem_degradation_score = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class NasaOceanObservation(Base):
    __tablename__ = "nasa_ocean_observations"

    id = Column(Integer, primary_key=True, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    observation_date = Column(String, nullable=False) # e.g. YYYY-MM-DD
    source = Column(String, nullable=False) # 'gibs', 'ob.daac'
    chlorophyll_value = Column(Float, nullable=True)
    algae_indicator = Column(Float, nullable=True)
    sst_value = Column(Float, nullable=True)
    ocean_color_index = Column(Float, nullable=True)
    raw_metadata_json = Column(Text, nullable=True)
    source_status = Column(String, nullable=False) # 'live', 'mock_fallback', 'error'
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class WaveCondition(Base):
    __tablename__ = "wave_conditions"

    id = Column(Integer, primary_key=True, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    observation_date = Column(String, nullable=False)
    wave_height_m = Column(Float, nullable=True)
    wave_direction_deg = Column(Float, nullable=True)
    wave_period_sec = Column(Float, nullable=True)
    current_speed = Column(Float, nullable=True)
    source = Column(String, nullable=False)
    source_status = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class SensitiveZone(Base):
    __tablename__ = "sensitive_zones"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    zone_type = Column(String, nullable=False) # 'coral_reef', 'marine_reserve'
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    radius_km = Column(Float, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class RiskAssessment(Base):
    __tablename__ = "risk_assessments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    assessment_date = Column(DateTime(timezone=True), server_default=func.now())
    debris_density_score = Column(Float, nullable=True)
    chlorophyll_value = Column(Float, nullable=True)
    algae_indicator = Column(Float, nullable=True)
    wave_height_m = Column(Float, nullable=True)
    wave_direction_deg = Column(Float, nullable=True)
    sensitive_zone_distance_km = Column(Float, nullable=True)
    ecosystem_degradation_score = Column(Float, nullable=True)
    risk_score = Column(Float, nullable=False)
    risk_level = Column(String, nullable=False) # 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
    recommendation = Column(Text, nullable=True)
    reasons_json = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    risk_assessment_id = Column(Integer, ForeignKey("risk_assessments.id"), nullable=True)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    risk_level = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    status = Column(String, default="active") # 'active', 'resolved'
    verified_by_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ApiLog(Base):
    __tablename__ = "api_logs"

    id = Column(Integer, primary_key=True, index=True)
    provider = Column(String, nullable=False) # 'nasa', 'copernicus'
    endpoint = Column(String, nullable=False)
    status_code = Column(Integer, nullable=False)
    status = Column(String, nullable=False) # 'success', 'failure'
    latency_ms = Column(Float, nullable=False)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, nullable=False)
    report_type = Column(String, nullable=False) # 'pdf', 'csv', 'json'
    file_path = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
