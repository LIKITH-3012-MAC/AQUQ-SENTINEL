import random
from typing import Dict, Any
from app.config import settings

def get_wave_conditions(lat: float, lon: float, date: str) -> Dict[str, Any]:
    """
    Copernicus Marine Service wave structure.
    Uses COPERNICUS_USERNAME and COPERNICUS_PASSWORD for authentication.
    """
    # Placeholder for Copernicus Marine Toolbox or API request
    # auth = (settings.COPERNICUS_USERNAME, settings.COPERNICUS_PASSWORD)
    return {
        "wave_height_m": round(random.uniform(0.5, 4.5), 1),
        "wave_direction_deg": random.randint(0, 360),
        "wave_period_sec": round(random.uniform(4.0, 12.0), 1),
        "current_speed": round(random.uniform(0.1, 1.5), 2),
        "source_status": "mock_fallback"
    }
