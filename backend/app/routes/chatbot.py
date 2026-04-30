from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import List
from .. import schemas, models, auth, database
from ..services.groq_service import groq_service
from ..services.rag_service import rag_service
import uuid

router = APIRouter(prefix="/api/chatbot", tags=["chatbot"])

@router.post("/message", response_model=schemas.ChatbotMessageResponse)
async def chat_with_copilot(
    req: schemas.ChatbotRequest,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # 1. Retrieve RAG Context
    context_chunks = rag_service.retrieve(req.message)
    context_text = "\n\n".join(context_chunks)
    intent = rag_service.get_intent(req.message)

    # 2. Build Prompt
    system_prompt = f"""
    You are the AquaSentinel AI Copilot. A specialized marine intelligence assistant.
    Tone: Professional, Action-oriented, Futuristic.
    
    GUIDELINES:
    - Use provided project context to explain AquaSentinel features.
    - Do NOT hallucinate live satellite data. If not in context, say it's currently unavailable.
    - Respond in {req.language} as the primary language.
    - If language is not English, provide a short English summary at the end.
    - Guide users to tactical actions (Map, Reports, etc.) based on context.
    - Role: {req.role}. Adjust technicality accordingly.
    
    PROJECT CONTEXT:
    {context_text}
    """

    # 3. Call Groq
    ai_resp = await groq_service.chat_completion(system_prompt, req.message)
    
    if "error" in ai_resp:
        return {
            "success": False,
            "answer": "AI service failure.",
            "intent": intent,
            "language": req.language,
            "sources": [],
            "session_id": req.session_id,
            "model": "unknown",
            "error": ai_resp["error"]
        }

    # 4. Save to Database
    msg_log = models.ChatbotMessage(
        user_id=current_user.id if current_user else None,
        session_id=req.session_id,
        user_message=req.message,
        bot_response=ai_resp["content"],
        detected_intent=intent,
        language=req.language,
        location=req.location,
        role=req.role,
        model=ai_resp["model"],
        retrieved_context=context_text,
        sources=["aquasentinel_knowledge.md"]
    )
    db.add(msg_log)
    db.commit()

    return {
        "success": True,
        "answer": ai_resp["content"],
        "intent": intent,
        "language": req.language,
        "sources": ["aquasentinel_knowledge.md"],
        "session_id": req.session_id,
        "model": ai_resp["model"]
    }

@router.get("/history", response_model=List[schemas.ChatbotHistoryResponse])
def get_chat_history(
    session_id: str,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    return db.query(models.ChatbotMessage)\
             .filter(models.ChatbotMessage.session_id == session_id)\
             .order_by(models.ChatbotMessage.created_at.asc()).all()

@router.get("/sessions", response_model=List[schemas.ChatbotSessionResponse])
def get_chat_sessions(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    return db.query(models.ChatbotSession)\
             .filter(models.ChatbotSession.user_id == current_user.id)\
             .order_by(models.ChatbotSession.updated_at.desc()).all()
