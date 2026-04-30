from pydantic import BaseModel, EmailStr
from typing import Optional, List, Any
from datetime import datetime

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    status: str
    last_login: Optional[datetime]
    created_at: datetime
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None

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

class MarineReportResponse(MarineReportBase):
    id: int
    user_id: int
    status: str
    created_at: datetime
    updated_at: Optional[datetime]
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

class DashboardSummary(BaseModel):
    total_reports: int
    active_alerts: int
    critical_risks: int
    data_points_analyzed: int
    recent_reports: List[MarineReportResponse]
    risk_heatmap: List[RiskScoreResponse]
