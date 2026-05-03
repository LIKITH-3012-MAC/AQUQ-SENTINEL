import requests
import json
from ..config import settings
from sqlalchemy.orm import Session
from .. import models

class OceanCopilot:
    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "llama-3.3-70b-versatile"

    def get_system_prompt(self, user_role="user", language="en"):
        import os
        import json
        
        knowledge_path = os.path.join(os.path.dirname(__file__), "..", "knowledge", "project_knowledge.json")
        project_context = ""
        if os.path.exists(knowledge_path):
            try:
                with open(knowledge_path, "r", encoding="utf-8") as f:
                    project_context = f"\n\n[SYSTEM PROJECT KNOWLEDGE BASE]\n{json.dumps(json.load(f))}\n\nIMPORTANT RULE: Use the above structured metadata to answer questions about what AquaSentinel is, pages, risk, and AI modules. Be highly accurate to this data."
            except Exception:
                pass

        # Role-based tone adjustment
        base_instructions = {
            "user": "Explain simply for citizens, focus on community impact and clear actions.",
            "researcher": "Use technical marine terminology, cite satellite datasets (MODIS/VIIRS), and provide detailed data points.",
            "admin": "Focus on operational logistics, cleanup protocols, and jurisdictional urgency."
        }
        
        tone = base_instructions.get(user_role, base_instructions["user"])
        
        prompts = {
            "en": f"You are the AquaSentinel AI Ocean Intelligence Copilot. Expert in marine biology and satellite oceanography. Tone: {tone}. Provide actionable advice.{project_context}",
            "te": f"మీరు ఆక్వాసెంటినెల్ AI ఓషన్ ఇంటెలిజెన్స్ కోపైలట్. టోన్: {tone}.{project_context}",
            "hi": f"आप एक्वासेंटिनल एआई ओशन इंटेलिजेंस कोपायलट हैं। टोन: {tone}.{project_context}",
            "ta": f"நீங்கள் அக்வாசென்டினல் ஏஐ கடல் நுண்ணறிவு கோபிலட்.{project_context}",
            "kn": f"ನೀವು ಅಕ್ವಾಸಂಟಿನೆಲ್ ಎಐ ಸಾಗರ ಇಂಟೆಲಿಜೆನ್ಸ್ ಸಹ-ಪೈಲಟ್.{project_context}",
            "ml": f"നിങ്ങൾ അക്വാസെന്റിനൽ AI ഓഷ്യൻ ഇന്റലിജൻസ് കോപൈലറ്റ് ആണ്.{project_context}"
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
            print(f"Chatbot Query: {message} | Role: {user_role} | Lang: {language}")
            print(f"Using API Key: {self.api_key[:10]}...")
            
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=20)
            
            if response.status_code != 200:
                print(f"Groq API Error: {response.status_code} - {response.text}")
                return f"Intelligence OS Error: {response.status_code}"
                
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
            print(f"Chatbot Exception: {str(e)}")
            return f"Error connecting to Ocean Intelligence OS: {str(e)}"

copilot = OceanCopilot()
