from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Any
from datetime import datetime
from uuid import UUID

class UserBase(BaseModel):
    full_name: str
    email: EmailStr
    role: Optional[str] = "user"

class UserRegister(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    security_question: str
    security_answer: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: UUID
    full_name: str
    email: EmailStr
    role: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    class Config:
        from_attributes = True

class Token(BaseModel):
    success: bool = True
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class ForgotQuestionRequest(BaseModel):
    email: EmailStr

class ForgotQuestionResponse(BaseModel):
    success: bool
    security_question: str

class VerifyAnswerRequest(BaseModel):
    email: EmailStr
    security_answer: str

class VerifyAnswerResponse(BaseModel):
    success: bool
    message: str
    reset_token: str

class ResetPasswordRequest(BaseModel):
    email: EmailStr
    reset_token: str
    new_password: str

class AuthStatusResponse(BaseModel):
    success: bool
    message: str

class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None
    user_id: Optional[UUID] = None

class MarineReportBase(BaseModel):
    title: str
    description: str
    latitude: float
    longitude: float
    report_type: str
    severity: str
    image_url: Optional[str] = None

class MarineReportCreate(MarineReportBase):
    pass

class ReportStatusUpdate(BaseModel):
    status: str

class MarineReportResponse(MarineReportBase):
    id: int
    user_id: UUID
    status: str
    tracking_id: str
    ai_analysis: Optional[Any]
    created_at: datetime
    updated_at: Optional[datetime]
    class Config:
        from_attributes = True

class MissionResponse(BaseModel):
    id: UUID
    report_id: int
    assigned_to: Optional[UUID]
    title: str
    description: str
    urgency: str
    status: str
    recommended_equipment: Optional[str]
    checklist: Optional[Any]
    before_image: Optional[str]
    after_image: Optional[str]
    progress_notes: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]
    class Config:
        from_attributes = True

class HotspotPredictionResponse(BaseModel):
    id: int
    latitude: float
    longitude: float
    drift_path: Optional[Any]
    risk_level: str
    time_window: str
    action_recommendation: Optional[str]
    created_at: datetime
    class Config:
        from_attributes = True

class DebrisDetectionResponse(BaseModel):
    id: int
    report_id: Optional[int]
    filename: str
    object_type: str
    confidence: float
    bbox: Optional[Any]
    density_score: float
    recommended_equipment: Optional[str]
    created_at: datetime
    class Config:
        from_attributes = True

class RiskScoreBase(BaseModel):
    latitude: float
    longitude: float

class RiskScoreResponse(RiskScoreBase):
    id: int
    score: float
    level: str
    explanation: Optional[str]
    recommended_action: Optional[str]
    factors: Optional[Any]
    created_at: datetime
    class Config:
        from_attributes = True

class AlertResponse(BaseModel):
    id: int
    title: str
    message: str
    severity: str
    latitude: float
    longitude: float
    status: str
    created_at: datetime
    class Config:
        from_attributes = True

class ChatbotRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default"
    language: Optional[str] = "English"
    location: Optional[str] = "Global"
    role: Optional[str] = "user"

class ChatbotMessageResponse(BaseModel):
    success: bool
    answer: str
    intent: str
    language: str
    sources: List[str]
    session_id: str
    model: str
    error: Optional[str] = None

class ChatbotSessionResponse(BaseModel):
    id: UUID
    session_id: str
    title: Optional[str]
    language: str
    location: Optional[str]
    created_at: datetime
    class Config:
        from_attributes = True

class ChatbotHistoryResponse(BaseModel):
    id: UUID
    user_message: str
    bot_response: str
    created_at: datetime
    class Config:
        from_attributes = True

class DashboardSummary(BaseModel):
    total_reports: int
    active_alerts: int
    critical_risks: int
    data_points_analyzed: int
    recent_reports: List[MarineReportResponse]
    risk_heatmap: List[RiskScoreResponse]

class PreferenceUpdate(BaseModel):
    theme: Optional[str] = None
    language: Optional[str] = None

class UserProfileBase(BaseModel):
    phone: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    preferred_language: Optional[str] = "English"
    preferred_theme: Optional[str] = "dark"
    preferred_region: Optional[str] = None
    bio: Optional[str] = None
    profile_image_url: Optional[str] = None

class UserProfileUpdate(UserProfileBase):
    full_name: Optional[str] = None

class UserActivityStats(BaseModel):
    total_reports: int
    active_reports: int
    resolved_reports: int
    total_chat_queries: int
    missions_joined: int

class FullProfileResponse(BaseModel):
    success: bool
    user: UserResponse
    profile: UserProfileBase
    stats: UserActivityStats
    recent_reports: List[MarineReportResponse]
    watchlist_regions: List[Any]

class SatelliteObservationResponse(BaseModel):
    id: int
    latitude: float
    longitude: float
    parameter: str
    value: float
    unit: Optional[str]
    source: str
    captured_at: datetime
    class Config:
        from_attributes = True

class WeatherObservationResponse(BaseModel):
    id: int
    latitude: float
    longitude: float
    temp: Optional[float]
    wind_speed: Optional[float]
    description: Optional[str]
    source: str
    created_at: datetime
    class Config:
        from_attributes = True

class OceanCurrentObservationResponse(BaseModel):
    id: int
    latitude: float
    longitude: float
    speed: Optional[float]
    direction: Optional[float]
    source: str
    created_at: datetime
    class Config:
        from_attributes = True
