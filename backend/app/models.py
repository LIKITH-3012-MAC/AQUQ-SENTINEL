from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="user") # 'user' or 'admin'
    theme = Column(String, default="dark")
    language = Column(String, default="en")
    status = Column(String, default="active") # 'active' or 'suspended'
    preferred_language = Column(String, default="en") # 'en', 'te', 'hi', etc.
    last_login = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ChatLog(Base):
    __tablename__ = "chat_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    message = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    language = Column(String, nullable=False)
    context = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Simulation(Base):
    __tablename__ = "simulations"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    simulation_type = Column(String, nullable=False) # 'pollution_flow', 'intervention'
    parameters = Column(JSON, nullable=False)
    results = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class MarineReport(Base):
    __tablename__ = "marine_reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    report_type = Column(String, nullable=False) # 'debris', 'oil_spill', 'illegal_fishing', 'bleaching'
    severity = Column(String, nullable=False) # 'Low', 'Medium', 'High', 'Critical'
    status = Column(String, default="pending") # 'pending', 'verified', 'resolved', 'dismissed'
    image_url = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class DebrisDetection(Base):
    __tablename__ = "debris_detections"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("marine_reports.id"), nullable=True)
    filename = Column(String, nullable=False)
    object_type = Column(String, nullable=False) # 'plastic_bottle', 'net', etc.
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
    score = Column(Float, nullable=False) # 0-100
    level = Column(String, nullable=False) # 'Low', 'Medium', 'High', 'Critical'
    explanation = Column(Text, nullable=True)
    recommended_action = Column(Text, nullable=True)
    factors = Column(JSON, nullable=True) # {chl: x, sst: y, etc.}
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class SatelliteObservation(Base):
    __tablename__ = "satellite_observations"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String, nullable=False) # 'NASA_GIBS', 'OB_DAAC'
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    parameter = Column(String, nullable=False) # 'chlorophyll', 'sst', 'ocean_color'
    value = Column(Float, nullable=False)
    unit = Column(String, nullable=True)
    observation_time = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class WeatherObservation(Base):
    __tablename__ = "weather_observations"

    id = Column(Integer, primary_key=True, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    temp = Column(Float, nullable=True)
    wind_speed = Column(Float, nullable=True)
    humidity = Column(Integer, nullable=True)
    description = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class OceanCurrentObservation(Base):
    __tablename__ = "ocean_current_observations"

    id = Column(Integer, primary_key=True, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    wave_height = Column(Float, nullable=True)
    current_speed = Column(Float, nullable=True)
    wave_direction = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    severity = Column(String, nullable=False) # 'Low', 'Medium', 'High', 'Critical'
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    status = Column(String, default="active") # 'active', 'resolved'
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class AdminAction(Base):
    __tablename__ = "admin_actions"

    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, ForeignKey("users.id"))
    action_type = Column(String, nullable=False) # 'verify_report', 'suspend_user', etc.
    target_id = Column(Integer, nullable=True)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    event_type = Column(String, nullable=False) # 'login', 'signup', 'data_fetch', 'error'
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    details = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
