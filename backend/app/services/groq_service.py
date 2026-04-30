import requests
import json
import os
from ..config import settings

class GroqService:
    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        
        if not self.api_key:
            print("[CRITICAL] GROQ_API_KEY is missing in environment.")

    async def chat_completion(self, system_prompt: str, user_message: str, temperature: float = 0.5):
        if not self.api_key:
            return {"error": "GROQ_API_KEY is not configured on the server."}

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "temperature": temperature,
            "max_tokens": 1024
        }

        try:
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=20)
            if response.status_code != 200:
                return {"error": f"Groq API Error: {response.status_code} - {response.text}"}
            
            data = response.json()
            return {
                "content": data["choices"][0]["message"]["content"],
                "model": self.model,
                "usage": data.get("usage", {})
            }
        except Exception as e:
            return {"error": f"Connection to Intelligence OS failed: {str(e)}"}

groq_service = GroqService()
