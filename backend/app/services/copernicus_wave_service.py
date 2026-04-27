import random
from typing import Dict, Any

def get_wave_conditions(lat: float, lon: float, date: str) -> Dict[str, Any]:
    """
    Copernicus Marine Service wave structure.
    Uses mock fallback initially.
    """
    return {
        "wave_height_m": round(random.uniform(0.5, 4.5), 1),
        "wave_direction_deg": random.randint(0, 360),
        "wave_period_sec": round(random.uniform(4.0, 12.0), 1),
        "current_speed": round(random.uniform(0.1, 1.5), 2),
        "source_status": "mock_fallback"
    }
