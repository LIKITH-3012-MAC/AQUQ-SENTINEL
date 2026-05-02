import requests
from typing import Dict, Any
from ..config import settings
from sqlalchemy.orm import Session
from .. import models

def get_weather_emoji(description: str) -> str:
    desc = description.lower()
    if "clear" in desc or "sunny" in desc: return "☀️"
    if "partly" in desc or "broken" in desc or "scattered" in desc: return "⛅"
    if "cloud" in desc: return "☁️"
    if "rain" in desc or "drizzle" in desc: return "🌧️"
    if "thunder" in desc: return "⛈️"
    if "wind" in desc: return "🌬️"
    if "fog" in desc or "mist" in desc or "haze" in desc: return "🌫️"
    if "snow" in desc: return "❄️"
    return "🌡️"

def fetch_marine_weather(db: Session, lat: float, lon: float):
    """
    Fetch marine weather from OpenWeather.
    """
    city_name = "Selected Zone"
    if not settings.OPENWEATHER_API_KEY:
        # Fallback to simulated data if key missing
        desc = "Partly cloudy (Simulated)"
        obs = models.WeatherObservation(
            latitude=lat,
            longitude=lon,
            temp=24.5,
            wind_speed=6.2,
            humidity=70,
            description=desc
        )
    else:
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={settings.OPENWEATHER_API_KEY}&units=metric"
        try:
            r = requests.get(url, timeout=5)
            data = r.json()
            city_name = data.get("name", city_name)
            desc = data.get("weather", [{}])[0].get("description", "Unknown")
            obs = models.WeatherObservation(
                latitude=lat,
                longitude=lon,
                temp=data.get("main", {}).get("temp"),
                wind_speed=data.get("wind", {}).get("speed"),
                humidity=data.get("main", {}).get("humidity"),
                description=desc
            )
        except:
            desc = "Fetch error fallback"
            obs = models.WeatherObservation(latitude=lat, longitude=lon, description=desc)

    db.add(obs)
    db.commit()
    db.refresh(obs)
    
    # Return dict with emoji
    res = {
        "id": obs.id,
        "latitude": obs.latitude,
        "longitude": obs.longitude,
        "temp": obs.temp,
        "wind_speed": obs.wind_speed,
        "humidity": obs.humidity,
        "description": obs.description,
        "emoji": get_weather_emoji(obs.description),
        "city": city_name
    }
    return res

def fetch_weather_by_city(db: Session, city: str):
    """
    Fetch weather by city name.
    """
    if not settings.OPENWEATHER_API_KEY:
        return {"error": "API Key missing", "city": city, "temp": 25, "description": "Sunny (Simulated)", "emoji": "☀️"}
    
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={settings.OPENWEATHER_API_KEY}&units=metric"
    try:
        r = requests.get(url, timeout=5)
        data = r.json()
        if r.status_code != 200:
            return {"error": data.get("message", "Unknown error")}
            
        desc = data.get("weather", [{}])[0].get("description", "Unknown")
        return {
            "latitude": data.get("coord", {}).get("lat"),
            "longitude": data.get("coord", {}).get("lon"),
            "temp": data.get("main", {}).get("temp"),
            "wind_speed": data.get("wind", {}).get("speed"),
            "humidity": data.get("main", {}).get("humidity"),
            "description": desc,
            "emoji": get_weather_emoji(desc),
            "city": data.get("name")
        }
    except Exception as e:
        return {"error": str(e)}

