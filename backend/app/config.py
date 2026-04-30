import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/aquasentinel")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "supersecretjwtkey_please_change_in_production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 days
    
    NASA_EARTHDATA_USERNAME: str = os.getenv("NASA_EARTHDATA_USERNAME", "")
    NASA_EARTHDATA_PASSWORD: str = os.getenv("NASA_EARTHDATA_PASSWORD", "")
    NASA_OB_DAAC_JWT: str = os.getenv("NASA_OB_DAAC_JWT", "")
    
    NASA_GIBS_BASE_URL: str = os.getenv("NASA_GIBS_BASE_URL", "https://gibs.earthdata.nasa.gov/wmts/epsg4326/best/")
    NASA_CMR_BASE_URL: str = os.getenv("NASA_CMR_BASE_URL", "https://cmr.earthdata.nasa.gov/search/")
    NASA_OCEAN_COLOR_BASE_URL: str = os.getenv("NASA_OCEAN_COLOR_BASE_URL", "https://oceandata.sci.gsfc.nasa.gov/api/")
    
    OPENWEATHER_API_KEY: str = os.getenv("OPENWEATHER_API_KEY", "")
    
    COPERNICUS_USERNAME: str = os.getenv("COPERNICUS_USERNAME", "")
    COPERNICUS_PASSWORD: str = os.getenv("COPERNICUS_PASSWORD", "")
    
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    
    class Config:
        env_file = ".env"

settings = Settings()
