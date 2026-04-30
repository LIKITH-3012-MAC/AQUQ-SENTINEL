from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import database, auth, models
from ..services import chatbot_service

router = APIRouter(prefix="/api/chatbot", tags=["chatbot"])

@router.post("/query")
async def ask_copilot(
    message: str,
    language: str = "en",
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Ask the Ocean Intelligence Copilot a question.
    """
    response = await chatbot_service.copilot.chat(db, current_user.id, message, language)
    return {"response": response}

@router.get("/history")
def get_chat_history(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Get chat history for the current user.
    """
    return db.query(models.ChatLog).filter(models.ChatLog.user_id == current_user.id).order_by(models.ChatLog.created_at.desc()).limit(20).all()

