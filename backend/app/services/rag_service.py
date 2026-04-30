import os
import re
from typing import List, Dict

class RAGService:
    def __init__(self, knowledge_path: str):
        self.knowledge_path = knowledge_path
        self.chunks = []
        self.load_knowledge()

    def load_knowledge(self):
        if not os.path.exists(self.knowledge_path):
            print(f"[ERROR] Knowledge base not found at {self.knowledge_path}")
            return

        with open(self.knowledge_path, "r") as f:
            content = f.read()
            
        # Chunking by headers (Markdown sections)
        sections = re.split(r'(?m)^## ', content)
        for section in sections:
            if section.strip():
                self.chunks.append("## " + section.strip() if not section.startswith("#") else section.strip())

    def retrieve(self, query: str, top_k: int = 3) -> List[str]:
        if not self.chunks:
            return []

        # Simple keyword scoring (Lightweight RAG)
        scored_chunks = []
        query_words = set(re.findall(r'\w+', query.lower()))
        
        for chunk in self.chunks:
            chunk_words = set(re.findall(r'\w+', chunk.lower()))
            score = len(query_words.intersection(chunk_words))
            if score > 0:
                scored_chunks.append((score, chunk))
        
        # Sort by score and take top K
        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        return [chunk for score, chunk in scored_chunks[:top_k]]

    def get_intent(self, query: str) -> str:
        query = query.lower()
        if "report" in query or "submit" in query: return "report_help"
        if "risk" in query or "score" in query: return "risk_explanation"
        if "map" in query or "layer" in query: return "map_help"
        if "debris" in query or "plastic" in query: return "debris_detection_help"
        if "alert" in query: return "alert_help"
        if "login" in query or "error" in query: return "technical_help"
        if "who" in query or "what is" in query: return "project_explanation"
        return "general_query"

# Path to the knowledge file
knowledge_file = os.path.join(os.path.dirname(__file__), "../../knowledge/aquasentinel_knowledge.md")
rag_service = RAGService(knowledge_file)
