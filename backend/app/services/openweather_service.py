import requests
from typing import Dict, Any
from ..config import settings
from sqlalchemy.orm import Session
from .. import models

def fetch_marine_weather(db: Session, lat: float, lon: float):
    """
    Fetch marine weather from OpenWeather.
    """
    if not settings.OPENWEATHER_API_KEY:
        # Fallback to simulated data if key missing
        obs = models.WeatherObservation(
            latitude=lat,
            longitude=lon,
            temp=24.5,
            wind_speed=6.2,
            humidity=70,
            description="Partly cloudy (Simulated)"
        )
    else:
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={settings.OPENWEATHER_API_KEY}&units=metric"
        try:
            r = requests.get(url, timeout=5)
            data = r.json()
            obs = models.WeatherObservation(
                latitude=lat,
                longitude=lon,
                temp=data.get("main", {}).get("temp"),
                wind_speed=data.get("wind", {}).get("speed"),
                humidity=data.get("main", {}).get("humidity"),
                description=data.get("weather", [{}])[0].get("description")
            )
        except:
            obs = models.WeatherObservation(latitude=lat, longitude=lon, description="Fetch error fallback")

    db.add(obs)
    db.commit()
    db.refresh(obs)
    return obs

