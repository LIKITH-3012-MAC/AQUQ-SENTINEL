import requests
from typing import Dict, Any
from ..config import settings

def get_marine_weather(lat: float, lon: float) -> Dict[str, Any]:
    """
    Fetch marine weather data from OpenWeather API.
    """
    if not settings.OPENWEATHER_API_KEY:
        return {
            "status": "missing_api_key",
            "temperature": 25.0,
            "humidity": 60,
            "wind_speed": 5.0
        }
    
    # Example URL for OpenWeather Marine/Weather API
    # Note: Using standard weather as a placeholder if Marine API specific endpoint differs
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={settings.OPENWEATHER_API_KEY}&units=metric"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return {
                "status": "success",
                "temperature": data.get("main", {}).get("temp"),
                "humidity": data.get("main", {}).get("humidity"),
                "wind_speed": data.get("wind", {}).get("speed"),
                "description": data.get("weather", [{}])[0].get("description")
            }
        else:
            return {
                "status": "error",
                "error_code": response.status_code,
                "temperature": 25.0,
                "humidity": 60,
                "wind_speed": 5.0
            }
    except Exception as e:
        return {
            "status": "exception",
            "error": str(e),
            "temperature": 25.0,
            "humidity": 60,
            "wind_speed": 5.0
        }
