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
    created_at: datetime
    class Config:
        orm_mode = True
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None

class RiskAssessmentBase(BaseModel):
    latitude: float
    longitude: float

class RiskAssessmentResponse(BaseModel):
    id: int
    latitude: float
    longitude: float
    risk_score: float
    risk_level: str
    recommendation: Optional[str]
    reasons: Optional[List[str]]
    debris_density_score: Optional[float]
    chlorophyll_value: Optional[float]
    wave_height_m: Optional[float]
    class Config:
        orm_mode = True
        from_attributes = True

class AlertResponse(BaseModel):
    id: int
    title: str
    message: str
    risk_level: str
    latitude: float
    longitude: float
    status: str
    verified_by_admin: bool
    created_at: datetime
    class Config:
        orm_mode = True
        from_attributes = True
