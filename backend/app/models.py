from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    security_question = Column(Text, nullable=False)
    security_answer_hash = Column(Text, nullable=False)
    role = Column(String, default="user") # 'user', 'admin', 'researcher', 'ngo', 'authority'
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=True)
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime(timezone=True), nullable=True)
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    password_changed_at = Column(DateTime(timezone=True), nullable=True)
    theme = Column(String, default="dark")
    language = Column(String, default="en")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class LoginSession(Base):
    __tablename__ = "login_sessions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    jwt_token_id = Column(Text, nullable=True)
    refresh_token_id = Column(Text, nullable=True)
    login_time = Column(DateTime(timezone=True), server_default=func.now())
    logout_time = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(Text, nullable=True)
    device_info = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class PasswordResetAudit(Base):
    __tablename__ = "password_reset_audit"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    email = Column(String, nullable=False)
    security_question = Column(Text, nullable=True)
    answer_verified = Column(Boolean, default=False)
    reset_success = Column(Boolean, default=False)
    ip_address = Column(String, nullable=True)
    user_agent = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class AuthResetToken(Base):
    __tablename__ = "auth_reset_tokens"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token_hash = Column(Text, nullable=False)
    purpose = Column(String, default="password_reset")
    is_used = Column(Boolean, default=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class OceanHealthScore(Base):
    __tablename__ = "ocean_health_scores"

    id = Column(Integer, primary_key=True, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    region_name = Column(String, nullable=True)
    score = Column(Integer, nullable=False) # 0 to 100
    category = Column(String, nullable=False) # Excellent, Stable, Watchlist, At Risk, Critical
    explanation = Column(Text, nullable=True)
    contributing_factors = Column(JSON, nullable=True)
    recommended_action = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class MarineReport(Base):
    __tablename__ = "marine_reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    report_type = Column(String, nullable=False) # 'debris', 'oil_spill', 'illegal_fishing', 'bleaching'
    severity = Column(String, nullable=False) # 'Low', 'Medium', 'High', 'Critical'
    status = Column(String, default="Submitted") # 'Submitted', 'Under Review', 'Verified', 'Assigned', 'Action in Progress', 'Resolved', 'Closed'
    image_url = Column(String, nullable=True)
    ai_analysis = Column(JSON, nullable=True) # AI Report Assistant results
    tracking_id = Column(String, unique=True, index=True, default=lambda: f"AQUA-{uuid.uuid4().hex[:8].upper()}")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class IncidentUpdate(Base):
    __tablename__ = "incident_updates"
    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("marine_reports.id"), nullable=False)
    status = Column(String, nullable=False)
    notes = Column(Text, nullable=True)
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Mission(Base):
    __tablename__ = "missions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_id = Column(Integer, ForeignKey("marine_reports.id"), nullable=False)
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True) # NGO/Volunteer User ID
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    urgency = Column(String, nullable=False)
    status = Column(String, default="Pending") # Pending, Accepted, In Progress, Completed
    recommended_equipment = Column(Text, nullable=True)
    checklist = Column(JSON, nullable=True)
    before_image = Column(String, nullable=True)
    after_image = Column(String, nullable=True)
    progress_notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

class HotspotPrediction(Base):
    __tablename__ = "hotspot_predictions"
    id = Column(Integer, primary_key=True, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    drift_path = Column(JSON, nullable=True) # List of lat/lon points
    risk_level = Column(String, nullable=False)
    time_window = Column(String, nullable=False) # e.g., "Next 24h"
    action_recommendation = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class DebrisDetection(Base):
    __tablename__ = "debris_detections"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("marine_reports.id"), nullable=True)
    filename = Column(String, nullable=False)
    object_type = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)
    bbox = Column(JSON, nullable=True)
    density_score = Column(Float, nullable=False)
    recommended_equipment = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class RiskScore(Base):
    __tablename__ = "risk_scores"

    id = Column(Integer, primary_key=True, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    score = Column(Float, nullable=False)
    level = Column(String, nullable=False)
    explanation = Column(Text, nullable=True)
    recommended_action = Column(Text, nullable=True)
    factors = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    severity = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    status = Column(String, default="active")
    verified_by_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class AdminAction(Base):
    __tablename__ = "admin_actions"

    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    action_type = Column(String, nullable=False)
    target_id = Column(String, nullable=True) # Could be UUID or Int depending on target
    details = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=True)
    action = Column(Text, nullable=False)
    entity_type = Column(String, nullable=True)
    entity_id = Column(String, nullable=True)
    action_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ChatbotSession(Base):
    __tablename__ = "chatbot_sessions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    session_id = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, nullable=True)
    language = Column(String, default="English")
    location = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class ChatbotMessage(Base):
    __tablename__ = "chatbot_messages"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    session_id = Column(String, nullable=False)
    user_message = Column(Text, nullable=False)
    bot_response = Column(Text, nullable=False)
    detected_intent = Column(String, nullable=True)
    language = Column(String, default="English")
    location = Column(String, nullable=True)
    role = Column(String, nullable=True)
    model = Column(String, nullable=True)
    retrieved_context = Column(Text, nullable=True)
    sources = Column(JSON, nullable=True)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class UploadedImage(Base):
    __tablename__ = "uploaded_images"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    image_path = Column(String, nullable=False)
    status = Column(String, default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class SatelliteObservation(Base):
    __tablename__ = "satellite_observations"
    id = Column(Integer, primary_key=True, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    parameter = Column(String, nullable=False) # e.g., 'chlorophyll', 'sst'
    value = Column(Float, nullable=False)
    unit = Column(String, nullable=True)
    source = Column(String, default="NASA")
    captured_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class WeatherObservation(Base):
    __tablename__ = "weather_observations"
    id = Column(Integer, primary_key=True, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    temp = Column(Float, nullable=True)
    wind_speed = Column(Float, nullable=True)
    humidity = Column(Float, nullable=True)
    pressure = Column(Float, nullable=True)
    description = Column(String, nullable=True)
    source = Column(String, default="OpenWeather")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class OceanCurrentObservation(Base):
    __tablename__ = "ocean_current_observations"
    id = Column(Integer, primary_key=True, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    u_velocity = Column(Float, nullable=True)
    v_velocity = Column(Float, nullable=True)
    speed = Column(Float, nullable=True)
    direction = Column(Float, nullable=True)
    source = Column(String, default="Copernicus")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ChatLog(Base): # Legacy, keeping for compatibility if needed, but we use ChatbotMessage now
    __tablename__ = "chat_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    message = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    language = Column(String, nullable=False)
    context = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Simulation(Base):
    __tablename__ = "simulations"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    simulation_type = Column(String, nullable=False)
    parameters = Column(JSON, nullable=True)
    results = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
