from sqlalchemy.orm import Session
from .. import models, schemas
import os
import json
from groq import Groq

# Initialize Groq client
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

class AIAssistantService:
    @staticmethod
    async def analyze_report(description: str, report_type: str = None):
        """
        Use AI to analyze a marine report and suggest metadata.
        """
        prompt = f"""
        Analyze the following marine issue report and provide a structured JSON analysis.
        Report Description: {description}
        Initial Type: {report_type or 'Unknown'}

        Return JSON with the following fields:
        - suggested_category: One of ['Plastic Waste', 'Chemical Spill', 'Ghost Net', 'Illegal Activity', 'Biological Anomaly']
        - urgency: One of ['Low', 'Medium', 'High', 'Critical']
        - environmental_impact: Brief description of likely impact.
        - recommended_response: Immediate action recommended.
        - confidence: 0-100 score.
        """

        try:
            completion = client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[
                    {"role": "system", "content": "You are the AquaSentinel Marine AI Assistant. You specialize in analyzing ocean debris and pollution reports."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            analysis = json.loads(completion.choices[0].message.content)
            return analysis
        except Exception as e:
            print(f"AI Analysis Error: {e}")
            return {
                "suggested_category": report_type or "Unknown",
                "urgency": "Medium",
                "environmental_impact": "Analysis unavailable. Human review required.",
                "recommended_action": "Proceed with standard verification protocol.",
                "confidence": 0
            }

    @staticmethod
    def update_report_status(db: Session, report_id: int, new_status: str, notes: str, user_id: str):
        """
        Update the lifecycle status of a report and log the update.
        """
        report = db.query(models.MarineReport).filter(models.MarineReport.id == report_id).first()
        if not report:
            return None
        
        report.status = new_status
        
        # Add entry to incident_updates (Lifecycle Timeline)
        update = models.IncidentUpdate(
            report_id=report.id,
            status=new_status,
            notes=notes,
            updated_by=user_id
        )
        db.add(update)
        db.commit()
        db.refresh(report)
        return report
