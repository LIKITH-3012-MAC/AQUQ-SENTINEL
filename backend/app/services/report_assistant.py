from typing import Dict, Any
import os
import json
from groq import Groq

# Initialize Groq client
client = None
if os.environ.get("GROQ_API_KEY"):
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def analyze_report_submission(report_type: str, severity: str, description: str) -> Dict[str, Any]:
    """
    World-Class AI Report Assistant Logic.
    Uses LLM to analyze submissions and provide deep insights.
    """
    if not client:
        # Fallback to smart rule-based logic if API key is missing
        return _fallback_analysis(report_type, severity, description)

    prompt = f"""
    Analyze this marine issue report for AquaSentinel AI Intelligence OS.
    Description: {description}
    User Reported Type: {report_type}
    User Reported Severity: {severity}

    Return a JSON object with:
    - suggested_category: Intelligent category (e.g., 'Microplastics', 'Industrial Oil Spill', 'Illegal Trawling')
    - urgency: 'Low', 'Medium', 'High', or 'Critical'
    - possible_impact: Brief scientific environmental impact estimation.
    - recommended_action: Immediate operational step for NGOs/Authorities.
    - confidence: 0-100 float.
    - admin_escalation_needed: boolean.
    """

    try:
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": "You are the AquaSentinel Marine Intelligence Assistant. Provide precise, scientific, and operational analysis of ocean reports."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        analysis = json.loads(completion.choices[0].message.content)
        analysis["admin_escalation_needed"] = analysis.get("urgency") in ["High", "Critical"] or severity in ["High", "Critical"]
        return analysis
    except Exception as e:
        print(f"AI Analysis Error: {e}")
        return _fallback_analysis(report_type, severity, description)

def _fallback_analysis(report_type: str, severity: str, description: str) -> Dict[str, Any]:
    # Rule-based fallback (enhanced from original)
    desc_lower = description.lower()
    suggested = report_type.replace("_", " ").title()
    impact = "Potential localized ecological stress."
    action = "Dispatch verification unit to coordinates."
    
    if "plastic" in desc_lower: 
        suggested = "Plastic Pollution"
        impact = "Risk of ingestion by marine megafauna and microplastic breakdown."
        action = "Deploy surface skimmers and current-tracking drift buoys."
    elif "oil" in desc_lower:
        suggested = "Hydrocarbon Spill"
        impact = "Surface tension disruption and acute toxicity to marine avian species."
        action = "Immediate boom deployment and regional authority notification."

    return {
        "suggested_category": suggested,
        "urgency": severity,
        "possible_impact": impact,
        "recommended_action": action,
        "confidence": 85.0,
        "admin_escalation_needed": severity in ["High", "Critical"]
    }
