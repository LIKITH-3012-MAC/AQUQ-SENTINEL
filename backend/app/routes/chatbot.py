from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional, Any
from .. import schemas, models, auth, database
from ..services.groq_service import groq_service
from ..services.rag_service import rag_service
import uuid

router = APIRouter(prefix="/api/chatbot", tags=["chatbot"])

@router.post("/message", response_model=schemas.ChatbotMessageResponse)
async def chat_with_copilot(
    req: schemas.ChatbotRequest,
    db: Session = Depends(database.get_db),
    current_user: Optional[models.User] = Depends(auth.get_current_user_optional)
):
    # 1. Retrieve RAG Context
    context_chunks = rag_service.retrieve(req.message)
    context_text = "\n\n".join(context_chunks)
    intent = rag_service.get_intent(req.message)

    # 2. Build Prompt
    # Logic for Regional Support
    regional_context = ""
    if req.location and any(loc in req.location.lower() for loc in ["andhra", "telangana"]):
        regional_context = "The user is in Andhra Pradesh/Telangana. You MUST respond primarily in Telugu. Also provide a brief English summary at the end."
    elif req.location and "tamil" in req.location.lower():
        regional_context = "The user is in Tamil Nadu. You MUST respond primarily in Tamil. Also provide a brief English summary at the end."
    
    system_prompt = f"""
    You are the AquaSentinel AI Copilot, a premium marine intelligence guide.
    Tone: Professional, Warm, Futuristic, Helpful, Elegant.
    
    CAPABILITIES & FEATURES:
    1. **Ocean Health Score**: A 0-100 score (100=Excellent) measuring regional marine health based on debris, thermal stress, and water quality.
    2. **AI Report Assistant**: Analyzes user reports to suggest categories, urgency, and environmental impacts automatically.
    3. **Debris Hotspot Prediction**: Predicts future debris accumulation zones and drift paths using ocean currents and wave data.
    4. **Incident Lifecycle Tracking**: Every report (e.g., AQUA-XXXXXXXX) is tracked from 'Submitted' to 'Resolved' with a full history.
    5. **Simulation Mode**: Admins can trigger [SIMULATED] events for evaluation. Always disclose when discussing simulated data.
    
    ### AI MARINE DEBRIS INTELLIGENCE LAYER:
    AquaSentinel includes an advanced AI Marine Debris & Ecosystem Intelligence Layer. Key capabilities:
    - **AI Debris Detection**: Users can upload marine images for AI-powered debris classification (plastic_waste, ghost_net, floating_debris, oil_patch, algae_cluster, unknown_marine_hazard).
    - **Confidence Scoring**: Each detection has a confidence score (0-1). High confidence (>0.85) triggers automatic alerts.
    - **Severity Levels**: Low, Medium, High, Critical — determined by debris class and confidence.
    - **YOLO-Style Map Overlays**: Detections appear on the map as polygons, debris lines, detection zones, and floating AI labels showing class + confidence.
    - **Ecosystem Monitoring**: AI classifies ecosystem regions (coral_region, algae_region, water_region, polluted_zone, stressed_marine_zone).
    - **GeoJSON Output**: Every detection generates map-ready GeoJSON data with bounding boxes, contour polygons, and detection lines.
    - **Alert Generation**: High-confidence detections automatically create marine risk alerts.
    - **Evidence Storage**: All detection outputs are permanently stored in PostgreSQL with full evidence chains.
    - **Detection-to-Action Pipeline**: Detection → Geospatial Conversion → DB Persistence → Map Overlay → Dashboard Evidence → Alert → Mission Readiness.
    - **Satellite Tile Readiness**: Architecture supports future satellite imagery inference.
    
    When users ask about AI detections, explain the class, confidence, severity, and what actions are recommended.
    A confidence of 0.89 means the AI model is 89% certain of its classification.
    Detection zones on the map use YOLO-inspired visual language: colored polygons, detection rectangles, debris trail lines, and confidence-tagged outlines.

    ### SIMULATED DATA POLICY:
    If a user asks about an alert or hotspot that contains the word "[SIMULATED]" or "DEMO", you must:
    1. Clearly state that this is a simulated evaluation event created by the Admin Demo Engine.
    2. Explain that AquaSentinel is demonstrating its detection and response capabilities.
    3. Provide the same technical detail (debris type, density, drift) as you would for a real event, but maintain the context of a demonstration.

    ### NAVIGATION & TOOLS:
    - Dashboard: /dashboard.html (Mission control)
    6. **Mission Mode**: Volunteers and NGOs can accept cleanup missions and track progress directly on the platform.
    7. **Hyperlocal Intelligence**: Provides localized marine risk summaries and hotspot alerts for the user's specific location.
    8. **Weather Widget**: Real-time premium weather monitoring at the top-left of the dashboard.

    RESPONSE STRUCTURE:
    1. Greeting/Acknowledgment (e.g., "Hello 👋", "Understood 🌊")
    2. Primary Answer: One clear, elegant sentence.
    3. Details: Use line breaks, bullet points, or mini-sections.
    4. Next Action: Guide the user to a tactical action (Map, Report, Risk Engine).
    5. Follow-up: A brief question to keep the conversation going.

    FORMATTING RULES:
    - NO giant walls of text.
    - Use line breaks for scanability.
    - Use 1-2 emojis per section max (🌊, 🤖, 📊, 📍, 📝, ✅, ⚠️).
    - Use bolding for key terms.
    - {regional_context if regional_context else f"Primary Language: {req.language}."}
    
    GUIDELINES:
    - Use project context to explain features.
    - Do NOT hallucinate data. If unknown, say it's unavailable ℹ️.
    - Current User Role: {req.role}.
    
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

    # 4. Save to Database (Upsert Session + Message)
    session = db.query(models.ChatbotSession).filter(models.ChatbotSession.session_id == req.session_id).first()
    if not session:
        session = models.ChatbotSession(
            user_id=current_user.id if current_user else None,
            session_id=req.session_id,
            title=req.message[:50] + "...",
            language=req.language,
            location=req.location
        )
        db.add(session)
    else:
        session.updated_at = func.now()
        if not session.user_id and current_user:
            session.user_id = current_user.id

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
