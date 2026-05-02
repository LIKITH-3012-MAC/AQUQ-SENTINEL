from typing import Dict, Any
import random

def analyze_report_submission(report_type: str, severity: str, description: str) -> Dict[str, Any]:
    """
    AI Report Assistant Logic.
    Simulates intelligent analysis of a report submission.
    """
    
    # Logic for suggested category based on keywords in description
    desc_lower = description.lower()
    suggested_category = report_type.replace("_", " ").title()
    
    if "plastic" in desc_lower or "bottle" in desc_lower or "net" in desc_lower:
        suggested_category = "Plastic Waste"
    elif "oil" in desc_lower or "slick" in desc_lower or "fuel" in desc_lower:
        suggested_category = "Petroleum/Oil Leak"
    elif "green" in desc_lower or "algae" in desc_lower or "bloom" in desc_lower:
        suggested_category = "Algae Bloom"
    elif "fish" in desc_lower or "mammal" in desc_lower or "whale" in desc_lower:
        suggested_category = "Marine Life Incident"

    # Urgency mapping
    urgency_map = {
        "Low": "Moderate",
        "Medium": "Elevated",
        "High": "High",
        "Critical": "Extreme"
    }
    urgency = urgency_map.get(severity, "High")

    # Impact estimation
    impacts = [
        "Coastal habitat contamination risk.",
        "Local biodiversity stress detected.",
        "Potential threat to regional fishing zones.",
        "Risk of spread to nearby marine protected areas.",
        "Possible toxicity to surface-dwelling organisms."
    ]
    possible_impact = random.choice(impacts)

    # Response recommendation
    responses = {
        "Plastic Waste": "Deploy cleanup vessel with surface skimmers. Inspect nearby current flow for drift estimation.",
        "Petroleum/Oil Leak": "Immediate deployment of containment booms. Notify environmental response unit.",
        "Algae Bloom": "Monitor oxygen levels. Advise local marine traffic to avoid the bloom core.",
        "Marine Life Incident": "Dispatch veterinary response team and notify local researchers.",
        "Default": "Verify via satellite imagery and dispatch regional patrol unit."
    }
    recommended_response = responses.get(suggested_category, responses["Default"])

    return {
        "suggested_category": suggested_category,
        "urgency": urgency,
        "possible_impact": possible_impact,
        "recommended_action": recommended_response,
        "confidence": round(random.uniform(85.0, 98.5), 1),
        "admin_escalation_needed": severity in ["High", "Critical"]
    }
