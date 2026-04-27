from typing import Dict, Any, List

def evaluate_risk(
    debris_density_score: float,
    chlorophyll_value: float,
    algae_indicator: float,
    wave_height_m: float,
    wave_direction_deg: float,
    sensitive_zone_distance_km: float,
    ecosystem_degradation_score: float
) -> Dict[str, Any]:
    """
    Evaluate marine risk based on combined factors.
    """
    reasons = []
    risk_score = 0.0
    
    # Debris contribution
    if debris_density_score > 70:
        risk_score += 40
        reasons.append("High debris density")
    elif debris_density_score > 30:
        risk_score += 20
        reasons.append("Moderate debris density")
        
    # Chlorophyll/Algae contribution
    if algae_indicator > 60 or chlorophyll_value > 3.0:
        risk_score += 25
        reasons.append("Abnormal algae/chlorophyll signal")
        
    # Wave contribution
    if wave_height_m > 3.0:
        risk_score += 20
        reasons.append("Wave height above safe threshold")
        
    # Sensitive Zone proximity
    if sensitive_zone_distance_km < 10.0:
        risk_score += 15
        reasons.append("Proximity to sensitive marine zone")
        
    # Ecosystem degradation
    if ecosystem_degradation_score > 50:
        risk_score += 20
        reasons.append("Ecosystem stress detected")
        
    # Normalize score
    risk_score = min(100.0, risk_score)
    
    # Determine Level
    if risk_score >= 80:
        risk_level = "CRITICAL"
        recommendation = "Critical alert. Immediate monitoring or cleanup action recommended."
    elif risk_score >= 60:
        risk_level = "HIGH"
        recommendation = "High risk of debris movement or ecosystem stress. Schedule cleanup and monitor satellite layer."
    elif risk_score >= 35:
        risk_level = "MEDIUM"
        recommendation = "Moderate ecosystem pressure. Continue monitoring."
    else:
        risk_level = "LOW"
        recommendation = "Normal marine condition detected."
        
    return {
        "risk_level": risk_level,
        "risk_score": risk_score,
        "recommendation": recommendation,
        "reasons": reasons
    }
