from typing import Dict, Any, List
from sqlalchemy.orm import Session
from .. import models

def calculate_marine_risk(
    db: Session,
    latitude: float,
    longitude: float,
    temperature: float = 25.0,
    wind_speed: float = 5.0,
    weather_desc: str = "clear",
    signals_used: List[str] = None,
    signals_missing: List[str] = None
) -> Dict[str, Any]:
    """
    Weather-Integrated Marine Risk Scoring System.
    Returns a dictionary structured as requested for the risk response.
    """
    if signals_used is None:
        signals_used = []
    if signals_missing is None:
        signals_missing = []

    score = 0.0
    
    # 1. Debris Impact (Local DB proxy - default low if not queried deeply)
    # Could query db for nearby reports, but defaulting to a baseline for this integration
    debris_density = 15.0 
    score += debris_density
    
    # 2. Thermal Stress (Weight: ~30%)
    # Base temp ~25C. Temps > 28C start adding stress, >32C high stress
    # Temps < 15C can also be stressful but let's assume tropical risk
    if temperature > 28.0:
        thermal_stress = min((temperature - 28.0) * 10, 45.0)
    else:
        thermal_stress = 5.0 # baseline
        
    score += thermal_stress
    
    # 3. Biological Stress (Proxy)
    bio_stress = 10.0
    score += bio_stress
    
    # 4. Dynamic Load (Wind) (Weight: ~30%)
    # Wind > 10m/s increases dynamic load heavily
    dynamic_load = min(wind_speed * 3.5, 50.0)
    score += dynamic_load

    # Normalize final score
    final_score = round(min(100.0, score))
    
    # Determine Level & Action dynamically based on weather
    if final_score >= 76:
        level = "CRITICAL"
        action = "Immediate action required. Suspend local maritime operations."
        explanation = f"Critical risk detected. Weather '{weather_desc}' with high wind ({wind_speed}m/s) driving extreme dynamic load."
    elif final_score >= 51:
        level = "HIGH"
        action = "Increase monitoring. Advise caution for small vessels."
        explanation = f"Elevated dynamic load detected due to local wind conditions ({wind_speed}m/s, {weather_desc})."
    elif final_score >= 26:
        level = "MODERATE"
        action = "Continue standard monitoring. Conditions are active."
        explanation = f"Moderate risk based on current weather ({temperature}°C, {weather_desc})."
    else:
        level = "LOW"
        action = "Routine monitoring. Ecosystem parameters stable."
        explanation = f"Calm conditions detected ({weather_desc}, low wind). No immediate threat."

    # Save to DB (optional, but good for history)
    risk_entry = models.RiskScore(
        latitude=latitude,
        longitude=longitude,
        score=final_score,
        level=level,
        explanation=explanation,
        recommended_action=action,
        factors={"thermal_stress": thermal_stress, "dynamic_load": dynamic_load, "weather": weather_desc}
    )
    db.add(risk_entry)
    db.commit()
    db.refresh(risk_entry)

    # Return structured JSON format
    return {
        "success": True,
        "coordinate": {
            "latitude": latitude,
            "longitude": longitude
        },
        "risk_score": final_score,
        "risk_level": level,
        "components": {
            "debris_density": round(debris_density),
            "thermal_stress": round(thermal_stress),
            "bio_stress": round(bio_stress),
            "dynamic_load": round(dynamic_load)
        },
        "assessment": explanation,
        "recommended_action": action,
        "signals_used": signals_used,
        "signals_missing": signals_missing,
        "id": risk_entry.id
    }
