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

    def get_system_prompt(self, user_role="user", language="en"):
        # Role-based tone adjustment
        base_instructions = {
            "user": "Explain simply for citizens, focus on community impact and clear actions.",
            "researcher": "Use technical marine terminology, cite satellite datasets (MODIS/VIIRS), and provide detailed data points.",
            "admin": "Focus on operational logistics, cleanup protocols, and jurisdictional urgency."
        }
        
        tone = base_instructions.get(user_role, base_instructions["user"])
        
        prompts = {
            "en": f"You are the AquaSentinel AI Ocean Intelligence Copilot. Expert in marine biology and satellite oceanography. Tone: {tone}. Provide actionable advice.",
            "te": f"మీరు ఆక్వాసెంటినెల్ AI ఓషన్ ఇంటెలిజెన్స్ కోపైలట్. టోన్: {tone}.",
            "hi": f"आप एक्वासेंटिनल एआई ओशन इंटेलिजेंस कोपायलट हैं। टोन: {tone}.",
            "ta": "நீங்கள் அக்வாசென்டினல் ஏஐ கடல் நுண்ணறிவு கோபிலட்.",
            "kn": "ನೀವು ಅಕ್ವಾಸಂಟಿನೆಲ್ ಎಐ ಸಾಗರ ಇಂಟೆಲಿಜೆನ್ಸ್ ಸಹ-ಪೈಲಟ್.",
            "ml": "നിങ്ങൾ അക്വാസെന്റിനൽ AI ഓഷ്യൻ ഇന്റലിജൻസ് കോപൈലറ്റ് ആണ്."
        }
        return prompts.get(language, prompts["en"])

    async def chat(self, db: Session, user_id: int, message: str, language="en"):
        user = db.query(models.User).filter(models.User.id == user_id).first()
        user_role = user.role if user else "user"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        system_prompt = self.get_system_prompt(user_role, language)
        
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
