import requests
import json
from ..config import settings
from sqlalchemy.orm import Session
from .. import models

class OceanCopilot:
    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "llama3-70b-8192"

    def get_system_prompt(self, language="en"):
        prompts = {
            "en": "You are the AquaSentinel AI Ocean Intelligence Copilot. You are an expert in marine biology, satellite oceanography, and environmental protection. Provide professional, data-driven, and actionable advice. If asked to create a report or analyze a region, guide the user on how to use the AquaSentinel tools.",
            "te": "మీరు ఆక్వాసెంటినెల్ AI ఓషన్ ఇంటెలిజెన్స్ కోపైలట్. మీరు మెరైన్ బయాలజీ, శాటిలైట్ ఓషనోగ్రఫీ మరియు పర్యావరణ పరిరక్షణలో నిపుణులు. వృత్తిపరమైన మరియు డేటా ఆధారిత సలహాలను అందించండి.",
            "hi": "आप एक्वासेंटिनल एआई ओशन इंटेलिजेंस कोपायलट हैं। आप समुद्री जीव विज्ञान, उपग्रह समुद्र विज्ञान और पर्यावरण संरक्षण के विशेषज्ञ हैं।"
        }
        return prompts.get(language, prompts["en"])

    async def chat(self, db: Session, user_id: int, message: str, language="en"):
        """
        Interacts with Groq LLM and stores logs.
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        system_prompt = self.get_system_prompt(language)
        
        # In a real RAG system, we would fetch relevant docs here
        # context = vector_db.search(message)
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            "temperature": 0.5,
            "max_tokens": 1024
        }

        try:
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=20)
            data = response.json()
            reply = data["choices"][0]["message"]["content"]
            
            # Log to DB
            log = models.ChatLog(
                user_id=user_id,
                message=message,
                response=reply,
                language=language
            )
            db.add(log)
            db.commit()
            
            return reply
        except Exception as e:
            return f"Error connecting to Ocean Intelligence OS: {str(e)}"

copilot = OceanCopilot()
