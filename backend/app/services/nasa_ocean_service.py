import random
from typing import Dict, Any
from ..config import settings

def search_ocean_datasets(keyword: str, start_date: str, end_date: str, lat: float, lon: float) -> Dict[str, Any]:
    """
    NASA CMR dataset search structure.
    """
    return {
        "status": "mock_fallback",
        "datasets": [
            {"id": "MODIS_AQUA_L3_SMI_CHL", "title": "MODIS Aqua Chlorophyll-a"},
            {"id": "VIIRS_SNPP_L3_SMI_SST", "title": "VIIRS Sea Surface Temperature"}
        ]
    }

def get_gibs_layers() -> Dict[str, Any]:
    """
    Fetch NASA GIBS layer metadata.
    """
    return {
        "status": "mock_fallback",
        "layers": [
            "MODIS_Aqua_Chlorophyll_A",
            "MODIS_Terra_CorrectedReflectance_TrueColor"
        ]
    }

def build_gibs_tile_url(layer: str, date: str) -> str:
    """
    Build NASA GIBS tile URL.
    """
    # EPSG4326 base URL template
    return f"https://gibs.earthdata.nasa.gov/wmts/epsg4326/best/{layer}/default/{date}/250m/{{z}}/{{y}}/{{x}}.png"

def get_chlorophyll_indicator(lat: float, lon: float, date: str) -> Dict[str, Any]:
    """
    Extract chlorophyll indicator from OB.DAAC service structure.
    Uses NASA_OB_DAAC_JWT for authentication if available.
    """
    headers = {}
    if settings.NASA_OB_DAAC_JWT:
        headers["Authorization"] = f"Bearer {settings.NASA_OB_DAAC_JWT}"
    
    # In a real scenario, we would make a request here
    # response = requests.get(f"{settings.NASA_OCEAN_COLOR_BASE_URL}...", headers=headers)
    
    val = round(random.uniform(0.1, 5.0), 2)
    return {
        "status": "mock_fallback",
        "chlorophyll_value": val,
        "unit": "mg/m^3"
    }

def get_ocean_color_summary(lat: float, lon: float, date: str) -> Dict[str, Any]:
    """
    Combined OB.DAAC summary.
    """
    chl = get_chlorophyll_indicator(lat, lon, date)
    algae = round(random.uniform(0, 100), 2)
    return {
        "status": "mock_fallback",
        "chlorophyll_value": chl["chlorophyll_value"],
        "algae_indicator": algae,
        "sst_value": round(random.uniform(20.0, 30.0), 2),
        "ocean_color_index": round(random.uniform(1.0, 5.0), 2)
    }
